from src.agent import ReActAgent
from src.tools.web_scraper import get_tool


def test_agent_returns_final_answer(monkeypatch):
    responses = [
        "思考: ウェブを検索します\n行動: web_scraper: http://example.com",
        "最終的な答え: テスト完了",
    ]

    def fake_llm(prompt):
        return responses.pop(0)

    agent = ReActAgent(fake_llm, [get_tool()])

    def mock_scrape(url, max_chars=1000):
        return "dummy"

    monkeypatch.setattr("src.tools.web_scraper.scrape_website_content", mock_scrape)

    answer = agent.run("質問")
    assert answer == "テスト完了"


def test_run_iter_yields_steps(monkeypatch):
    responses = [
        "思考: 検索します\n行動: web_scraper: http://example.com",
        "最終的な答え: ok",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    monkeypatch.setattr(
        "src.tools.web_scraper.scrape_website_content", lambda url, max_chars=1000: "dummy"
    )
    agent = ReActAgent(fake_llm, [get_tool()])

    steps = list(agent.run_iter("質問"))
    assert steps[0].startswith("思考")
    assert steps[1] == "観察: dummy"
    assert steps[2].startswith("最終的な答え")
    assert steps[3] == "ok"
