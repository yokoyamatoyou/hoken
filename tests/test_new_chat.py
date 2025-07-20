from types import SimpleNamespace

from src.ui import main as GPT
from src.memory import ConversationMemory

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.memory = ConversationMemory()
    c.memory.add("user", "hi")
    c.chat_display = SimpleNamespace(
        configure=lambda *a, **k: None,
        delete=lambda *a, **k: None,
        insert=lambda *a, **k: None,
    )
    c.file_list_text = SimpleNamespace(
        configure=lambda *a, **k: None,
        delete=lambda *a, **k: None,
    )
    c.window = SimpleNamespace(title=lambda *a, **k: None)
    c.calls = {}
    c.diagram_label = SimpleNamespace(
        configure=lambda **k: c.calls.setdefault("label", []).append(k),
        image="img",
    )
    c.save_button = SimpleNamespace(
        configure=lambda **k: c.calls.setdefault("save", []).append(k)
    )
    c.clear_button = SimpleNamespace(
        configure=lambda **k: c.calls.setdefault("clear", []).append(k)
    )
    c.copy_button = SimpleNamespace(
        configure=lambda **k: c.calls.setdefault("copy", []).append(k)
    )
    c.fix_button = SimpleNamespace(
        configure=lambda **k: c.calls.setdefault("fix", []).append(k)
    )
    return c


def test_new_chat_clears_memory():
    client = _client()
    assert client.memory.messages
    client.new_chat()
    assert client.memory.messages == []


def test_new_chat_resets_diagram_preview():
    client = _client()
    client._diagram_path = "dummy.png"
    client.new_chat()
    assert client._diagram_path is None
    assert client.diagram_label.image is None
    assert any(k.get("state") == "disabled" for k in client.calls.get("save", []))
    assert any(k.get("state") == "disabled" for k in client.calls.get("clear", []))
    assert any(k.get("state") == "disabled" for k in client.calls.get("copy", []))
    assert any(k.get("state") == "disabled" for k in client.calls.get("fix", []))
