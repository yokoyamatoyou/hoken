import queue
import threading
from types import SimpleNamespace

from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.response_queue = queue.Queue()
    c.chat_display = SimpleNamespace(
        configure=lambda *a, **k: None,
        insert=lambda *a, **k: None,
        see=lambda *a, **k: None,
        tag_add=lambda *a, **k: None,
        index=lambda *a, **k: "1.0",
    )
    c.window = SimpleNamespace(after=lambda *a, **k: None)
    return c


def test_process_queue_starts_thread(monkeypatch):
    client = _client()
    client.response_queue.put("__SAVE__")
    client.save_conversation = lambda show_popup=False: None

    calls = []

    class DummyThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=None):
            calls.append((target, kwargs, daemon))
        def start(self):
            calls.append("started")

    monkeypatch.setattr(threading, "Thread", DummyThread)

    client.process_queue()

    assert calls[0][0] == client.save_conversation
    assert calls[0][1] == {"show_popup": False}
    assert calls[0][2] is True
    assert "started" in calls
