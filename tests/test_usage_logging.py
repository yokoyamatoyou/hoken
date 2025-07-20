import logging
from types import SimpleNamespace

from src import main as src_main

class DummyResp:
    def __init__(self):
        msg = SimpleNamespace(content="ok")
        self.choices = [SimpleNamespace(message=msg)]
        self.usage = SimpleNamespace(total_tokens=42)

class DummyClient:
    def __init__(self):
        self.chat = self
        self.completions = self
    def create(self, model, messages, **kwargs):
        self.last_kwargs = kwargs
        return DummyResp()


def test_create_llm_logs_usage(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(src_main, "OpenAI", lambda api_key: DummyClient())
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OPENAI_TOKEN_PRICE", "0.001")
    llm = src_main.create_llm(log_usage=True)
    llm("hi")
    assert "Tokens used: 42" in caplog.text
    assert "Cost: $0.0420" in caplog.text


def test_create_llm_timeout(monkeypatch):
    dummy = DummyClient()
    monkeypatch.setattr(src_main, "OpenAI", lambda api_key: dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OPENAI_TIMEOUT", "5")
    llm = src_main.create_llm()
    llm("hi")
    assert dummy.last_kwargs.get("timeout") == 5.0


def test_create_llm_bad_timeout(monkeypatch):
    dummy = DummyClient()
    monkeypatch.setattr(src_main, "OpenAI", lambda api_key: dummy)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OPENAI_TIMEOUT", "oops")
    llm = src_main.create_llm()
    llm("hi")
    assert "timeout" not in dummy.last_kwargs


def test_create_llm_base_url(monkeypatch):
    captured = {}

    class DummyClient:
        def __init__(self):
            self.chat = self
            self.completions = self

        def create(self, model, messages, **kwargs):
            return DummyResp()

    def fake_openai(api_key, base_url=None):
        captured["base_url"] = base_url
        return DummyClient()

    monkeypatch.setattr(src_main, "OpenAI", fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com")
    llm = src_main.create_llm()
    llm("hi")
    assert captured["base_url"] == "https://example.com"
