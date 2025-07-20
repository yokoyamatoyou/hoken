from src.agent import CoTAgent


def test_cot_agent_returns_final_answer():
    responses = [
        "思考: intermediate",
        "最終的な答え: done",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    agent = CoTAgent(fake_llm)
    answer = agent.run("質問")
    assert answer == "done"


def test_cot_run_iter_yields_steps():
    responses = [
        "思考: step",
        "最終的な答え: ok",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    agent = CoTAgent(fake_llm)
    steps = list(agent.run_iter("q"))
    assert steps[0].startswith("思考")
    assert steps[1].startswith("最終的な答え")
    assert steps[2] == "ok"
