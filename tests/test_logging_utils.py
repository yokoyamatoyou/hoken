import logging
from src.logging_utils import setup_logging


def test_setup_logging_writes_file(tmp_path):
    log_file = tmp_path / "out.log"
    setup_logging(level=logging.INFO, log_file=str(log_file))
    logging.info("hello")
    with open(log_file, "r", encoding="utf-8") as f:
        data = f.read()
    assert "hello" in data


def test_setup_logging_uses_env_var(tmp_path, monkeypatch):
    log_file = tmp_path / "env.log"
    monkeypatch.setenv("AGENT_LOG_FILE", str(log_file))
    setup_logging(level=logging.INFO)
    logging.info("world")
    with open(log_file, "r", encoding="utf-8") as f:
        data = f.read()
    assert "world" in data


def test_setup_logging_level_from_env(monkeypatch):
    monkeypatch.setenv("AGENT_LOG_LEVEL", "DEBUG")
    setup_logging()
    assert logging.getLogger().level == logging.DEBUG
