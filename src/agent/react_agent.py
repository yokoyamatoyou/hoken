import re
import logging
import json
from typing import Callable, Dict, List, Optional, Iterator

from src.tools.base import Tool, execute_tool
from src.memory import BaseMemory


logger = logging.getLogger(__name__)


class ReActAgent:
    """Minimal implementation of the ReAct loop."""

    ACTION_RE = re.compile(r"^行動:\s*(\w+):\s*(.*)$", re.MULTILINE)
    FINAL_RE = re.compile(r"^最終的な答え:\s*(.*)$", re.MULTILINE)

    PROMPT_TEMPLATE = (
        "あなたは質問に答えるアシスタントです。\n"
        "利用可能な行動:\n{tools}\n\n"
        "質問: {input}\n"
        "{agent_scratchpad}"
    )

    def __init__(
        self,
        llm: Callable[[str], str],
        tools: List[Tool],
        memory: Optional[BaseMemory] = None,
        verbose: bool = False,
    ):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.memory = memory
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

    def tool_descriptions(self) -> str:
        descs = []
        for t in self.tools.values():
            descs.append(f"- {t.name}: {t.description}")
        return "\n".join(descs)

    def run_iter(self, question: str, max_turns: int = 5) -> Iterator[str]:
        """Yield intermediate steps of the ReAct loop."""
        scratchpad = ""
        if self.memory is not None:
            self.memory.add("user", question)
            try:
                history_lines = self.memory.search(question, top_k=3)
            except Exception:
                history_lines = [
                    f"{m['role']}: {m['content']}" for m in self.memory.messages[:-1]
                ]
            history = "\n".join(history_lines)
        else:
            history = ""

        for _ in range(max_turns):
            prompt = self.PROMPT_TEMPLATE.format(
                input=question,
                tools=self.tool_descriptions(),
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
                answer = final_match.group(1)
                if self.memory is not None:
                    self.memory.add("assistant", answer)
                if self.verbose:
                    logger.info("Final answer: %s", answer)
                yield answer
                return
            action_match = self.ACTION_RE.search(output)
            if not action_match:
                yield "エラー: 行動を特定できませんでした"
                return
            tool_name, tool_input = action_match.groups()
            if self.verbose:
                logger.info("Executing tool %s with %s", tool_name, tool_input)
            try:
                args: Dict[str, str] = json.loads(tool_input)
                if not isinstance(args, dict):
                    raise ValueError
            except Exception:
                args = {"url": tool_input}

            observation = execute_tool(tool_name, args, self.tools)
            if self.verbose:
                logger.debug("Observation: %s", observation)
            yield f"観察: {observation}"
            scratchpad += f"{output}\n観察: {observation}\n"
            if self.memory is not None:
                self.memory.add("assistant", output)
                self.memory.add("system", f"観察: {observation}")
        if self.verbose:
            logger.warning("Max turns reached with no final answer")
        yield "エラー: 最大試行回数に達しました"

    def run(self, question: str, max_turns: int = 5) -> str:
        answer = None
        last = ""
        for message in self.run_iter(question, max_turns=max_turns):
            last = message
            if message.startswith("最終的な答え:"):
                answer = message[len("最終的な答え:"):].strip()
        return answer or last
