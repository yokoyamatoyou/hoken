import logging
import re
from typing import Callable, Iterator, Optional

from src.memory import BaseMemory

logger = logging.getLogger(__name__)

class CoTAgent:
    """Minimal Chain-of-Thought agent.

    The agent repeatedly asks the LLM for the next thought until a final
    answer is produced. Each LLM call should return either a ``思考:`` line
    or ``最終的な答え:``.
    """

    THOUGHT_RE = re.compile(r"^思考:\s*(.*)$", re.MULTILINE)
    FINAL_RE = re.compile(r"^最終的な答え:\s*(.*)$", re.MULTILINE)

    PROMPT_TEMPLATE = (
        "質問: {input}\n" "{agent_scratchpad}"
        "次の思考を '思考:'、最終的な答えを '最終的な答え:' として出力してください。"
    )

    def __init__(
        self,
        llm: Callable[[str], str],
        memory: Optional[BaseMemory] = None,
        *,
        max_turns: int = 5,
        verbose: bool = False,
    ) -> None:
        self.llm = llm
        self.memory = memory
        self.max_turns = max_turns
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

    def run_iter(self, question: str) -> Iterator[str]:
        scratchpad = ""
        if self.memory is not None:
            self.memory.add("user", question)
            try:
                history_lines = self.memory.search(question, top_k=3)
            except Exception:
                history_lines = [m["content"] for m in self.memory.messages[:-1]]
            history = "\n".join(history_lines)
        else:
            history = ""

        for _ in range(self.max_turns):
            prompt = self.PROMPT_TEMPLATE.format(
                input=question,
                agent_scratchpad=(history + "\n" + scratchpad if history else scratchpad),
            )
            if self.verbose:
                logger.debug("Prompt:\n%s", prompt)
            output = self.llm(prompt)
            if self.verbose:
                logger.debug("LLM output:\n%s", output)
            yield output
            final_match = self.FINAL_RE.search(output)
            if final_match:
                answer = final_match.group(1).strip()
                if self.memory is not None:
                    self.memory.add("assistant", answer)
                if self.verbose:
                    logger.info("Final answer: %s", answer)
                yield answer
                return
            thought_match = self.THOUGHT_RE.search(output)
            if not thought_match:
                yield "エラー: 思考を特定できませんでした"
                return
            scratchpad += f"{output}\n"
            if self.memory is not None:
                self.memory.add("assistant", output)
        if self.verbose:
            logger.warning("Max turns reached with no final answer")
        yield "エラー: 最大試行回数に達しました"

    def run(self, question: str) -> str:
        answer = None
        last = ""
        for message in self.run_iter(question):
            last = message
            if message.startswith("最終的な答え:"):
                answer = message[len("最終的な答え:"):].strip()
        return answer or last
