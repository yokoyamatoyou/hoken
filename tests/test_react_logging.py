import logging
from src.agent import ReActAgent
from src.tools.web_scraper import get_tool


def test_verbose_logging(monkeypatch, caplog):
    responses = [
        "思考: something\n行動: web_scraper: http://example.com",
        "最終的な答え: done",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    caplog.set_level(logging.DEBUG)
    agent = ReActAgent(fake_llm, [get_tool()], verbose=True)

    monkeypatch.setattr(
        "src.tools.web_scraper.scrape_website_content",
        lambda url, max_chars=1000: "dummy",
    )

    agent.run("質問")

    assert "Executing tool web_scraper" in caplog.text
    assert "Final answer: done" in caplog.text
