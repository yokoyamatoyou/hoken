import json
from types import SimpleNamespace

from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    return ChatGPTClient.__new__(ChatGPTClient)


def test_save_conversation(tmp_path, monkeypatch):
    client = _client()
    client.current_title = "TestChat"
    client.model_var = SimpleNamespace(get=lambda: "model-x")
    client.messages = [{"role": "user", "content": "hi"}]
    client.uploaded_files = [{"name": "file.docx", "type": ".docx"}]

    monkeypatch.chdir(tmp_path)
    client.save_conversation()

    conv_dir = tmp_path / "conversations"
    files = list(conv_dir.glob("*.json"))
    assert len(files) == 1

    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["title"] == "TestChat"
    assert data["model"] == "model-x"
    assert data["messages"] == client.messages
    assert data["uploaded_files_metadata"] == [{"name": "file.docx", "type": ".docx"}]
    assert "timestamp" in data


def test_save_conversation_with_tool(tmp_path, monkeypatch):
    client = _client()
    client.current_title = "ToolChat"
    client.model_var = SimpleNamespace(get=lambda: "model-x")
    client.messages = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "1",
                    "type": "function",
                    "function": {"name": "f", "arguments": "{}"},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "1", "content": "path"},
    ]
    client.uploaded_files = []
    monkeypatch.setattr(GPT.messagebox, 'showinfo', lambda *a, **k: None)
    monkeypatch.setattr(GPT.messagebox, 'showerror', lambda *a, **k: None)
    monkeypatch.chdir(tmp_path)
    client.save_conversation()

    conv_dir = tmp_path / "conversations"
    files = list(conv_dir.glob("*.json"))
    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["messages"] == client.messages


def test_save_conversation_custom_dir(tmp_path, monkeypatch):
    client = _client()
    client.current_title = "CustomDir"
    client.model_var = SimpleNamespace(get=lambda: "model-x")
    client.messages = [{"role": "user", "content": "hi"}]
    client.uploaded_files = []

    custom = tmp_path / "mydir"
    monkeypatch.setattr(GPT, "CONV_DIR", str(custom))
    monkeypatch.chdir(tmp_path)

    client.save_conversation(show_popup=False)

    files = list(custom.glob("*.json"))
    assert len(files) == 1
