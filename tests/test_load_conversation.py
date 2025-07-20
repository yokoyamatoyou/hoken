import json
from types import SimpleNamespace
from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient

def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.window = SimpleNamespace(title=lambda *a, **k: None)
    c.chat_display = SimpleNamespace(configure=lambda *a, **k: None,
                                     delete=lambda *a, **k: None,
                                     insert=lambda *a, **k: None)
    c.file_list_text = SimpleNamespace(configure=lambda *a, **k: None,
                                       delete=lambda *a, **k: None,
                                       insert=lambda *a, **k: None)
    c.update_file_list = lambda: None
    return c


def test_load_conversation(tmp_path):
    data = {
        "title": "Chat",
        "messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "ok"}],
        "uploaded_files_metadata": [{"name": "f.pdf", "type": ".pdf"}],
    }
    file = tmp_path / "conv.json"
    file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    client = _client()
    client.load_conversation(str(file))
    assert client.current_title == "Chat"
    assert client.messages == data["messages"]
    assert client.uploaded_files == [{"name": "f.pdf", "type": ".pdf"}]
