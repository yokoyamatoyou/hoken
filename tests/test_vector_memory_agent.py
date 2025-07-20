from src.agent import ReActAgent
from src.vector_memory import VectorMemory


def test_agent_uses_vector_memory_search():
    mem = VectorMemory()
    mem.add("user", "Pythonについて話そう")
    mem.add("assistant", "はい、Pythonは人気があります")

    captured = {}

    def fake_llm(prompt: str) -> str:
        captured['prompt'] = prompt
        return "最終的な答え: ok"

    agent = ReActAgent(fake_llm, [], mem)
    answer = agent.run("Pythonの利用例は？")
    assert answer == "ok"
    assert "Pythonについて話そう" in captured['prompt']
