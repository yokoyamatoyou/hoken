import os
import tempfile
from graphviz import Source
from mermaid import Mermaid

from src.tools.graphviz_tool import create_graphviz_diagram
from src.tools.mermaid_tool import create_mermaid_diagram, sanitize_mermaid_code


def test_create_graphviz_diagram_success(monkeypatch, tmp_path):
    def fake_render(self, *, outfile=None, cleanup=True):
        open(outfile, "wb").close()
        return outfile

    monkeypatch.setattr(Source, "render", fake_render)
    path = create_graphviz_diagram("digraph {a->b}")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_graphviz_diagram_failure(monkeypatch, tmp_path):
    def fake_render(self, *, outfile=None, cleanup=True):
        raise RuntimeError("boom")

    monkeypatch.setattr(Source, "render", fake_render)

    temp_path = tmp_path / "gv.png"

    def fake_tempfile(*args, **kwargs):
        class Temp:
            def __init__(self, name):
                self.name = str(name)

            def close(self):
                open(self.name, "wb").close()

        return Temp(temp_path)

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", fake_tempfile)

    result = create_graphviz_diagram("digraph {}")
    assert result.startswith("Failed to generate diagram")
    assert not temp_path.exists()


def test_create_mermaid_diagram_success(monkeypatch):
    def fake_png(self, filename):
        open(filename, "wb").close()

    monkeypatch.setattr(Mermaid, "to_png", fake_png)
    path = create_mermaid_diagram("graph TD; A-->B;")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_mermaid_diagram_failure(monkeypatch, tmp_path):
    def fake_png(self, filename):
        raise RuntimeError("fail")

    monkeypatch.setattr(Mermaid, "to_png", fake_png)

    temp_path = tmp_path / "md.png"

    def fake_tempfile(*args, **kwargs):
        class Temp:
            def __init__(self, name):
                self.name = str(name)

            def close(self):
                open(self.name, "wb").close()

        return Temp(temp_path)

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", fake_tempfile)

    result = create_mermaid_diagram("graph TD;")
    assert result.startswith("Failed to generate diagram")
    assert not temp_path.exists()


def test_sanitize_mermaid_code():
    raw = "```mermaid\n<div>graph TD; A-->B;</div>\n```"
    assert sanitize_mermaid_code(raw) == "graph TD; A-->B;"


def test_create_mermaid_diagram_sanitizes(monkeypatch, tmp_path):
    captured = {}

    class Dummy:
        def __init__(self, code):
            captured["code"] = code

        def to_png(self, filename):
            open(filename, "wb").close()

    monkeypatch.setattr("src.tools.mermaid_tool.Mermaid", Dummy)
    path = create_mermaid_diagram("```mermaid\n<b>graph TD;A-->B;</b>\n```")
    assert captured["code"] == "graph TD;A-->B;"
    os.unlink(path)
