import base64
import datetime
import json
import logging
import os
import queue
import re
import shutil
import threading
import functools

import customtkinter as ctk
import tkinter
from tkinter import filedialog, messagebox
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

from src.document_loader import load_document
from src.vector_store_manager import VectorStoreManager


def get_font_family(preferred: str = "Meiryo") -> str:
    env_font = os.getenv("PREFERRED_FONT")
    candidates = []
    if env_font:
        candidates.extend([f.strip() for f in env_font.split(",") if f.strip()])
    candidates.append(preferred)
    try:
        root = tkinter.Tk()
        root.withdraw()
        families = set(root.tk.call("font", "families"))
        root.destroy()
        for font in candidates:
            if font in families:
                return font
    except tkinter.TclError:
        pass
    return "Helvetica"

# --- Constants ---
load_dotenv()
CONV_DIR = os.getenv("CONVERSATION_DIR", "conversations")
FONT_FAMILY = get_font_family()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- CustomTkinter Setup ---
ctk.set_appearance_mode("light")
try:
    GOOGLE_THEME = os.path.join(os.path.dirname(__file__), "resources", "google.json")
    if os.path.exists(GOOGLE_THEME):
        ctk.set_default_color_theme(GOOGLE_THEME)
except Exception:
    logging.warning("Google theme not found or failed to load, using default.")

class ChatGPTClient:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("保険文書分析AI")
        self.window.geometry("1200x800")
        self.window.minsize(800, 600)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showerror("エラー", "環境変数 OPENAI_API_KEY が設定されていません")
            self.window.destroy()
            return
        self.client = OpenAI(api_key=api_key)

        self.vector_store_manager = VectorStoreManager(openai_api_key=api_key)

        self.model_var = ctk.StringVar(value="gpt-4.1-mini")
        self.messages = []
        self.uploaded_sources = []
        self.response_queue = queue.Queue()

        self.setup_ui()
        self.window.after(100, self.process_queue)

    def setup_ui(self):
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        # --- Left Panel ---
        left_panel = ctk.CTkFrame(self.window, width=300, fg_color="#F1F3F4")
        left_panel.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
        left_panel.grid_rowconfigure(8, weight=1)

        row = 0
        ctk.CTkLabel(left_panel, text="設定", font=(FONT_FAMILY, 20, "bold")).grid(
            row=row, column=0, padx=20, pady=10, sticky="w"); row += 1

        ctk.CTkLabel(left_panel, text="モデル:", font=(FONT_FAMILY, 14)).grid(
            row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        ctk.CTkOptionMenu(left_panel, variable=self.model_var,
                          values=["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-3.5-turbo"]).grid(
            row=row, column=0, padx=20, pady=5, sticky="ew"); row += 1

        ctk.CTkButton(left_panel, text="ファイルをアップロード", command=self.upload_file).grid(
            row=row, column=0, padx=20, pady=(20, 5), sticky="ew"); row += 1

        ctk.CTkLabel(left_panel, text="またはURL:", font=(FONT_FAMILY, 14)).grid(
            row=row, column=0, padx=20, pady=(10, 0), sticky="w"); row += 1
        self.url_entry = ctk.CTkEntry(left_panel, placeholder_text="https://...")
        self.url_entry.grid(row=row, column=0, padx=20, pady=5, sticky="ew"); row += 1
        ctk.CTkButton(left_panel, text="URLを読み込む", command=self.load_from_url).grid(
            row=row, column=0, padx=20, pady=5, sticky="ew"); row += 1

        ctk.CTkLabel(left_panel, text="読み込み済ソース:", font=(FONT_FAMILY, 14)).grid(
            row=row, column=0, padx=20, pady=(20, 0), sticky="w"); row += 1
        self.file_list_text = ctk.CTkTextbox(left_panel, height=150)
        self.file_list_text.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
        self.file_list_text.configure(state="disabled")
        row += 1

        left_panel.grid_rowconfigure(row, weight=1); row+=1

        ctk.CTkButton(left_panel, text="会話をクリア", command=self.new_chat).grid(
            row=row, column=0, padx=20, pady=10, sticky="ew"); row += 1

        # --- Right Panel ---
        right_panel = ctk.CTkFrame(self.window, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_rowconfigure(0, weight=3)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_rowconfigure(2, weight=0)
        right_panel.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(right_panel, font=(FONT_FAMILY, 16), wrap="word")
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.configure(state="disabled")
        self.chat_display.tag_config("user_msg", background="#e3f2fd")
        self.chat_display.tag_config("assistant_msg", background="#f1f3f4")

        self.citation_display = ctk.CTkTextbox(right_panel, font=(FONT_FAMILY, 12), wrap="word", height=150, fg_color="#fafafa")
        self.citation_display.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.citation_display.configure(state="disabled")

        input_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="sew", pady=(10,0))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_field = ctk.CTkEntry(input_frame, placeholder_text="質問を入力してください...", height=40)
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(input_frame, text="送信", width=80, command=self.send_message)
        self.send_button.grid(row=0, column=1)

        self.status_label = ctk.CTkLabel(input_frame, text="準備完了", font=(FONT_FAMILY, 12), text_color="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5,0))

    def _load_and_index_documents(self, source_path):
        try:
            self.response_queue.put(("status", "ドキュメントを読み込み中..."))
            docs = load_document(source_path)
            if not docs:
                self.response_queue.put(("error", f"{os.path.basename(source_path)}からテキストを抽出できませんでした。"))
                return

            self.response_queue.put(("status", "ベクトル化中..."))
            self.vector_store_manager.build_from_documents(docs)

            source_name = os.path.basename(source_path) if not source_path.startswith('http') else source_path
            self.uploaded_sources.append(source_name)
            self.response_queue.put(("update_source_list", None))
            self.response_queue.put(("status", "準備完了"))
        except Exception as e:
            self.response_queue.put(("error", f"処理中にエラーが発生しました: {e}"))

    def upload_file(self):
        file_paths = filedialog.askopenfilenames(
            title="ファイルを選択",
            filetypes=[("Document Files", "*.pdf *.docx"), ("All files", "*.*")]
        )
        if file_paths:
            for file_path in file_paths:
                threading.Thread(target=self._load_and_index_documents, args=(file_path,), daemon=True).start()

    def load_from_url(self):
        url = self.url_entry.get().strip()
        if url and url.startswith(('http://', 'https://')):
            threading.Thread(target=self._load_and_index_documents, args=(url,), daemon=True).start()
            self.url_entry.delete(0, "end")
        else:
            messagebox.showwarning("警告", "有効なURLを入力してください。")

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.response_queue.get_nowait()
                if msg_type == "status":
                    self.status_label.configure(text=data)
                elif msg_type == "assistant_chunk":
                    self.display_message(data, "assistant_msg")
                elif msg_type == "citation":
                    self.citation_display.configure(state="normal")
                    self.citation_display.delete("1.0", "end")
                    self.citation_display.insert("1.0", data)
                    self.citation_display.configure(state="disabled")
                elif msg_type == "update_source_list":
                    self.update_file_list()
                elif msg_type == "error":
                    messagebox.showerror("エラー", data)
                    self.status_label.configure(text="エラー")
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.process_queue)

    def update_file_list(self):
        self.file_list_text.configure(state="normal")
        self.file_list_text.delete("1.0", "end")
        self.file_list_text.insert("1.0", "\n".join(self.uploaded_sources))
        self.file_list_text.configure(state="disabled")

    def send_message(self):
        user_message = self.input_field.get().strip()
        if not user_message:
            return

        self.input_field.delete(0, "end")
        self.display_message(f"You: {user_message}\n\n", "user_msg")

        threading.Thread(target=self._get_response_worker, args=(user_message,), daemon=True).start()

    def _get_response_worker(self, user_message: str):
        if not self.vector_store_manager.is_ready():
            self.response_queue.put(("error", "情報ソースが読み込まれていません。"))
            return

        self.response_queue.put(("status", "関連情報を検索中..."))
        retrieved_docs = self.vector_store_manager.search(user_message, top_k=3)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        if retrieved_docs:
            citation_text = "\n\n---\n\n".join([f"Source: {doc.metadata.get('source', 'N/A')}, Page: {doc.metadata.get('page', 'N/A')}\n\n{doc.page_content}" for doc in retrieved_docs])
            self.response_queue.put(("citation", citation_text))
        else:
            self.response_queue.put(("citation", "関連する引用元は見つかりませんでした。"))

        system_prompt = (
            "あなたは保険業界のベテラン専門家です。提供されたコンテキスト情報に基づいて、ユーザーの質問に正確かつ丁寧に回答してください。"
            "回答はコンテキスト内の情報に厳密に基づき、憶測で補完しないでください。"
            "コンテキスト情報で回答できない場合は、「提供された情報だけでは判断できません」と答えてください。"
        )
        prompt_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"コンテキスト:\n{context}\n\n質問: {user_message}"}
        ]

        try:
            self.response_queue.put(("status", "応答を生成中..."))
            self.response_queue.put(("assistant_chunk", "Assistant: "))
            stream = self.client.chat.completions.create(
                model=self.model_var.get(), messages=prompt_messages, stream=True
            )
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                self.response_queue.put(("assistant_chunk", content))

            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": full_response})
            self.response_queue.put(("status", "準備完了"))

        except Exception as e:
            self.response_queue.put(("error", f"API呼び出しエラー: {e}"))

    def display_message(self, text, tag):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text, (tag,))
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def new_chat(self):
        self.messages = []
        self.uploaded_sources = []
        self.vector_store_manager = VectorStoreManager(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.citation_display.configure(state="normal")
        self.citation_display.delete("1.0", "end")
        self.citation_display.configure(state="disabled")
        self.update_file_list()
        self.status_label.configure(text="準備完了")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ChatGPTClient()
    app.run()
