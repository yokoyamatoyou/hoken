import queue
from types import SimpleNamespace
from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.input_field = SimpleNamespace(get=lambda: "hello", delete=lambda *a, **k: None)
    c.chat_display = SimpleNamespace(configure=lambda *a, **k: None,
                                     insert=lambda *a, **k: None,
                                     see=lambda *a, **k: None)
    c.uploaded_files = []
    c.messages = []
    c.generate_title = lambda m: None
    c.get_response = lambda: None
    c.response_queue = queue.Queue()
    c.agent_var = SimpleNamespace(get=lambda: "chatgpt")
    return c


def test_first_message_adds_system_prompt():
    client = _client()
    client.send_message()
    assert client.messages[0]["role"] == "system"
    assert "プロンプトアドバイス" in client.messages[0]["content"]
    assert client.messages[1]["role"] == "user"
