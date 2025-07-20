import queue
import threading
import tkinter
import customtkinter as ctk
from typing import Callable

from src.agent import ReActAgent
from src.tools import get_web_scraper, get_sqlite_tool
from src.main import create_llm


def agent_worker(question: str, agent: ReActAgent, result_queue: queue.Queue) -> None:
    """Run the agent and push steps to the queue."""
    try:
        for step in agent.run_iter(question):
            result_queue.put(step)
    except Exception as e:
        result_queue.put(f"エラー: {e}")


class AgentApp(ctk.CTk):
    """Simple interface for interacting with :class:`ReActAgent`."""

    def __init__(self, llm: Callable[[str], str] | None = None, *, log_usage: bool = False) -> None:
        super().__init__()

        self.title("ReAct Agent")
        self.geometry("800x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(3, weight=1)

        self.entry = ctk.CTkEntry(self.left_frame, placeholder_text="質問を入力してください")
        self.entry.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.run_button = ctk.CTkButton(self.left_frame, text="実行", command=self.start_agent)
        self.run_button.grid(row=1, column=0, padx=20, pady=10)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.right_frame, width=400)
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.configure(state="disabled")

        self.result_queue: queue.Queue[str] = queue.Queue()

        if llm is None:
            llm = create_llm(log_usage=log_usage)
        tools = [get_web_scraper(), get_sqlite_tool()]
        self.agent = ReActAgent(llm, tools)

    def start_agent(self) -> None:
        question = self.entry.get().strip()
        if not question:
            return

        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", tkinter.END)
        self.textbox.insert("1.0", f"質問: {question}\n\n")
        self.textbox.configure(state="disabled")

        self.run_button.configure(state="disabled")
        thread = threading.Thread(target=agent_worker, args=(question, self.agent, self.result_queue))
        thread.start()
        self.after(100, self.check_queue)

    def check_queue(self) -> None:
        try:
            message = self.result_queue.get_nowait()
            self.textbox.configure(state="normal")
            self.textbox.insert(tkinter.END, message + "\n")
            self.textbox.configure(state="disabled")

            if message.startswith("最終的な答え:") or message.startswith("エラー:"):
                self.run_button.configure(state="normal")
            else:
                self.after(100, self.check_queue)
        except queue.Empty:
            self.after(100, self.check_queue)


if __name__ == "__main__":
    app = AgentApp(log_usage=True)
    app.mainloop()
