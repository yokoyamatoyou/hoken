from types import SimpleNamespace
import queue
from src.ui import main as GPT
from src.constants import TOT_LEVELS

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.response_queue = queue.Queue()
    c.simple_llm = lambda prompt: ""
    c.agent_tools = []
    c.memory = None
    c.messages = []
    class DummyVar:
        def __init__(self, value="LOW"):
            self._val = value
        def get(self):
            return self._val
        def set(self, value):
            self._val = value

    c.tot_level_var = DummyVar("LOW")
    return c


def test_run_agent_uses_tot_env(monkeypatch):
    client = _client()
    created = {}

    def dummy_tot(llm, evaluate, *, max_depth, breadth, memory=None):
        created["depth"] = max_depth
        created["breadth"] = breadth
        return SimpleNamespace(run_iter=lambda q: [])

    monkeypatch.setattr(GPT, "ToTAgent", dummy_tot)
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_DEPTH", "3")
    monkeypatch.setenv("TOT_BREADTH", "4")

    client.run_agent("tot", "q")

    assert created["depth"] == 3
    assert created["breadth"] == 4


def test_run_agent_invalid_tot_env(monkeypatch):
    client = _client()

    monkeypatch.setattr(GPT, "ToTAgent", lambda *a, **k: SimpleNamespace(run_iter=lambda q: []))
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_DEPTH", "0")

    client.run_agent("tot", "q")
    outputs = []
    while not client.response_queue.empty():
        outputs.append(client.response_queue.get())
    assert any("エラー" in o for o in outputs)


def test_run_agent_uses_tot_level(monkeypatch):
    client = _client()
    created = {}

    def dummy_tot(llm, evaluate, *, max_depth, breadth, memory=None):
        created["depth"] = max_depth
        created["breadth"] = breadth
        return SimpleNamespace(run_iter=lambda q: [])

    monkeypatch.setattr(GPT, "ToTAgent", dummy_tot)
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)

    client.tot_level_var.set("MIDDLE")
    client.run_agent("tot", "q")

    depth, breadth = TOT_LEVELS["MIDDLE"]
    assert created["depth"] == depth
    assert created["breadth"] == breadth


def test_run_agent_tot_level_env(monkeypatch):
    client = _client()
    created = {}

    def dummy_tot(llm, evaluate, *, max_depth, breadth, memory=None):
        created["depth"] = max_depth
        created["breadth"] = breadth
        return SimpleNamespace(run_iter=lambda q: [])

    monkeypatch.setattr(GPT, "ToTAgent", dummy_tot)
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_LEVEL", "HIGH")

    client.run_agent("tot", "q")

    depth, breadth = TOT_LEVELS["HIGH"]
    assert created["depth"] == depth
    assert created["breadth"] == breadth


def test_run_agent_tot_level_extreme(monkeypatch):
    client = _client()
    created = {}

    def dummy_tot(llm, evaluate, *, max_depth, breadth, memory=None):
        created["depth"] = max_depth
        created["breadth"] = breadth
        return SimpleNamespace(run_iter=lambda q: [])

    monkeypatch.setattr(GPT, "ToTAgent", dummy_tot)
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_LEVEL", "EXTREME")

    client.run_agent("tot", "q")

    depth, breadth = TOT_LEVELS["EXTREME"]
    assert created["depth"] == depth
    assert created["breadth"] == breadth


def test_run_agent_tot_level_env_invalid(monkeypatch):
    client = _client()

    monkeypatch.setattr(GPT, "ToTAgent", lambda *a, **k: SimpleNamespace(run_iter=lambda q: []))
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_LEVEL", "WRONG")

    client.run_agent("tot", "q")
    outputs = []
    while not client.response_queue.empty():
        outputs.append(client.response_queue.get())
    assert any("エラー" in o for o in outputs)
