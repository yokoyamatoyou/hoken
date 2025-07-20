import os
import tempfile
from graphviz import Source
import subprocess
from pydantic import BaseModel, Field
from .base import Tool

class GraphvizInput(BaseModel):
    code: str = Field(description="DOT言語のコード")


def create_graphviz_diagram(dot_code: str) -> str:
    """Generate a diagram PNG from Graphviz DOT code using the graphviz package."""
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    out_file.close()
    try:
        src = Source(dot_code)
        src.format = "png"
        # Render directly to the temporary file path
        src.render(outfile=out_file.name, cleanup=True)
    except FileNotFoundError:
        os.unlink(out_file.name)
        return "Failed to generate diagram: Graphviz 'dot' executable not found"
    except subprocess.CalledProcessError as exc:
        os.unlink(out_file.name)
        return f"Failed to generate diagram: {exc}"
    except Exception as exc:
        os.unlink(out_file.name)
        return f"Failed to generate diagram: {exc}"
    return out_file.name


def get_tool() -> Tool:
    return Tool(
        name="create_graphviz_diagram",
        description="DOT言語から図を生成する。フローチャート等に適している。",
        func=create_graphviz_diagram,
        args_schema=GraphvizInput,
    )
