import os
import tempfile
import re
from mermaid import Mermaid
from pydantic import BaseModel, Field
from .base import Tool

class MermaidInput(BaseModel):
    code: str = Field(description="Mermaid記法のコード")


def sanitize_mermaid_code(code: str) -> str:
    """Strip Markdown fences and HTML tags from Mermaid code."""
    code = code.strip()
    code = re.sub(r"^```(?:mermaid)?\n?", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```$", "", code.strip())
    code = re.sub(r"<[^>]+>", "", code)
    return code.strip()


def create_mermaid_diagram(mermaid_code: str) -> str:
    """Generate a diagram PNG from Mermaid code using mermaid-py."""
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    out_file.close()
    try:
        code = sanitize_mermaid_code(mermaid_code)
        diagram = Mermaid(code)
        diagram.to_png(out_file.name)
    except Exception as exc:
        os.unlink(out_file.name)
        return f"Failed to generate diagram: {exc}"
    return out_file.name


def get_tool() -> Tool:
    """Return a Tool for generating diagrams from Mermaid code."""
    return Tool(
        name="create_mermaid_diagram",
        description="Mermaid markdown-like codeから図を生成する。シーケンス図、ガントチャート等に適している。",
        func=create_mermaid_diagram,
        args_schema=MermaidInput,
    )
