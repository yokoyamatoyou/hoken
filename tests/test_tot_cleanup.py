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


def test_tot_steps_removed(monkeypatch):
    client = _client()

    class DummyTot:
        def run_iter(self, q):
            yield "思考候補: A"
            yield "選択: A"
            yield "最終的な答え: done"

    monkeypatch.setattr(GPT, "ToTAgent", lambda *a, **k: DummyTot())
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setattr(ChatGPTClient, "save_conversation", lambda *a, **k: None)

    client.run_agent("tot", "q")

    while not client.response_queue.empty():
        client.process_queue()

    assert "done" in client.chat_display.text
    assert "思考候補" not in client.chat_display.text
    assert "選択" not in client.chat_display.text
