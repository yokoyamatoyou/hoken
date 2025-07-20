from src.agent import ToTAgent


def test_tot_agent_selects_best_path():
    prompts = []

    def fake_llm(prompt: str) -> str:
        prompts.append(prompt)
        if "箇条書き" in prompt:
            return "- A\n- B"
        return "最終的な答え: done"

    def evaluate(history: str) -> float:
        return 1.0 if "B" in history else 0.0

    agent = ToTAgent(fake_llm, evaluate, max_depth=1, breadth=2)
    answer = agent.run("test")

    assert answer == "done"
    assert "B" in prompts[-1]


def test_tot_run_iter_yields_steps():
    calls = []

    def llm(prompt: str) -> str:
        calls.append(prompt)
        if "箇条書き" in prompt:
            return "- A\n- B"
        return "最終的な答え: ok"

    def evaluate(history: str) -> float:
        return 1.0 if "B" in history else 0.0

    agent = ToTAgent(llm, evaluate, max_depth=1, breadth=2)
    steps = list(agent.run_iter("q"))
    assert any(s.startswith("思考候補:") for s in steps)
    assert steps[-1] == "最終的な答え: ok"
