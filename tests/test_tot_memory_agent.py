from src.agent import ToTAgent
from src.memory import ConversationMemory


def test_tot_agent_uses_memory(monkeypatch):
    mem = ConversationMemory()
    mem.add("user", "Pythonについて話そう")
    mem.add("assistant", "はい、Pythonは人気があります")

    prompts = []

    def fake_llm(prompt: str) -> str:
        prompts.append(prompt)
        if "箇条書き" in prompt:
            return "- A"
        return "最終的な答え: ok"

    agent = ToTAgent(fake_llm, lambda h: 1.0, max_depth=1, breadth=1, memory=mem)
    answer = agent.run("Pythonの利用例は？")
    assert answer == "ok"
    assert "Pythonについて話そう" in prompts[0]
