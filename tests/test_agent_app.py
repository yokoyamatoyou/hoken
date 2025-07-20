import queue

from pydantic import BaseModel, Field

from src.agent import ReActAgent
from src.tools.base import Tool
from src.ui.agent_app import agent_worker


class DummyInput(BaseModel):
    url: str = Field(description="dummy")

def test_agent_worker_puts_steps():
    responses = [
        "思考: test\n行動: dummy_tool: arg",
        "最終的な答え: done",
    ]

    def fake_llm(prompt: str) -> str:
        return responses.pop(0)

    def dummy_func(url: str):
        return "obs"

    tool = Tool(name="dummy_tool", description="d", func=dummy_func, args_schema=DummyInput)
    agent = ReActAgent(fake_llm, [tool])

    q: queue.Queue[str] = queue.Queue()
    agent_worker("q", agent, q)
    outputs = []
    while not q.empty():
        outputs.append(q.get())

    assert outputs[0].startswith("思考")
    assert outputs[1] == "観察: obs"
    # The agent yields the LLM output and then the final answer separately
    assert outputs[-2].startswith("最終的な答え:")
