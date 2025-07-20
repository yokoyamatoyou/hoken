import queue
from types import SimpleNamespace

from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.response_queue = queue.Queue()
    c.agent_tools = []
    c.memory = None
    c.messages = []
    c.window = SimpleNamespace(after=lambda *a, **k: None)

    class DummyVar:
        def __init__(self, value="LOW"):
            self._val = value
        def get(self):
            return self._val
        def set(self, value):
            self._val = value
    c.tot_level_var = DummyVar("LOW")

    class DummyText:
        def __init__(self):
            self.text = ""
        def configure(self, *a, **k):
            pass
        def insert(self, index, txt):
            self.text += txt
        def delete(self, start, end):
            try:
                pos = int(float(start))
            except Exception:
                pos = 0
            self.text = self.text[:pos]
        def tag_add(self, *a, **k):
            pass
        def index(self, *_):
            return str(len(self.text))
        def see(self, *_):
            pass

    c.chat_display = DummyText()
    return c


def test_tot_end_without_newline():
    client = _client()
    client.response_queue.put("Assistant: ")
    client.response_queue.put("__TOT_START__")
    client.response_queue.put("__TOT__thinking")
    client.response_queue.put("__TOT_END__final answer")

    while not client.response_queue.empty():
        client.process_queue()

    assert "final answer" in client.chat_display.text
