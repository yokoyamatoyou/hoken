from src.agent import ReActAgent
from src.tools.web_scraper import get_tool
from src.memory import ConversationMemory


def test_agent_updates_memory(monkeypatch):
    responses = [
        "思考: 検索\n行動: web_scraper: http://example.com",
        "最終的な答え: OK",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    memory = ConversationMemory()
    agent = ReActAgent(fake_llm, [get_tool()], memory)

    monkeypatch.setattr(
        "src.tools.web_scraper.scrape_website_content", lambda url, max_chars=1000: "dummy"
    )

    answer = agent.run("質問")
    assert answer == "OK"
    assert memory.messages[0]["role"] == "user"
    assert memory.messages[-1]["content"] == "OK"
