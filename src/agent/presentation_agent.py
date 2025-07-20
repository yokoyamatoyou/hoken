import json
import re
import tempfile
from typing import Callable, Iterator

class PresentationAgent:
    """Generate simple HTML presentations using an LLM."""

    DEFAULT_SLIDES = 5
    SLIDE_RE = re.compile(r"(\d+)\s*枚")

    PROMPT_TEMPLATE = (
        "あなたはプロフェッショナルなプレゼンテーションデザイナーです。"
        "トピックに沿って {n} 枚のスライド原稿を日本語で作成してください。"
        "出力はJSON配列で、各要素は {\"title\": \"..\", \"body\": \"..\"} の形式で。"
    )

    def __init__(self, llm: Callable[[str], str]):
        self.llm = llm

    def _parse_count(self, question: str) -> int:
        match = self.SLIDE_RE.search(question)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return self.DEFAULT_SLIDES

    def _build_html(self, slides: list[dict]) -> str:
        style = (
            "<style>\n"
            "body{margin:0;font-family:sans-serif;color:#202124;background:#FFFFFF;}\n"
            ".slide{width:21cm;height:29.7cm;padding:1cm;box-sizing:border-box;page-break-after:always;}\n"
            ".slide h1{margin-top:0;font-size:28px;color:#1A73E8;}\n"
            ".slide p{font-size:18px;}\n"
            "</style>"
        )
        parts = ["<html><head>", style, "</head><body>"]
        for s in slides:
            title = s.get("title", "")
            body = s.get("body", "").replace("\n", "<br>")
            parts.append(f'<div class="slide"><h1>{title}</h1><p>{body}</p></div>')
        parts.append("</body></html>")
        return "".join(parts)

    def run_iter(self, question: str) -> Iterator[str]:
        count = self._parse_count(question)
        prompt = self.PROMPT_TEMPLATE.format(n=count) + "\n" + question
        resp = self.llm(prompt)
        try:
            slides = json.loads(resp)
        except Exception:
            yield "エラー: スライドの生成に失敗しました"
            return
        html = self._build_html(slides)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        with open(tmp.name, "w", encoding="utf-8") as f:
            f.write(html)
        yield f"プレゼン資料を生成しました: {tmp.name}"

    def run(self, question: str) -> str:
        result = ""
        for step in self.run_iter(question):
            result = step
        return result
