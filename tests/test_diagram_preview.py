from types import SimpleNamespace
from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.diagram_label = SimpleNamespace(configure=lambda **k: c.calls.setdefault('label', []).append(k), image=None)
    c.save_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('save', []).append(k))
    c.clear_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('clear', []).append(k))
    c.copy_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('copy', []).append(k))
    c.fix_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('fix', []).append(k))
    c.calls = {}
    return c


def test_display_and_clear_diagram(monkeypatch, tmp_path):
    client = _client()
    img = tmp_path / "d.png"
    img.write_bytes(b'x')
    monkeypatch.setattr(GPT.Image, 'open', lambda path: object())
    monkeypatch.setattr(GPT.ctk, 'CTkImage', lambda light_image, size: object())

    client.display_diagram(str(img))
    assert client._diagram_path == str(img)
    assert any(k.get('state') == 'normal' for k in client.calls.get('save', []))
    assert any(k.get('state') == 'normal' for k in client.calls.get('clear', []))

    client.calls = {'label': [], 'save': [], 'clear': []}
    client.clear_diagram()
    assert client._diagram_path is None
    assert any(k.get('state') == 'disabled' for k in client.calls.get('save', []))
    assert any(k.get('state') == 'disabled' for k in client.calls.get('clear', []))


def test_save_diagram(monkeypatch, tmp_path):
    client = _client()
    src = tmp_path / "src.png"
    src.write_bytes(b'x')
    client._diagram_path = str(src)

    dest = tmp_path / "out.png"
    monkeypatch.setattr(GPT.filedialog, 'asksaveasfilename', lambda **k: str(dest))
    monkeypatch.setattr(GPT.shutil, 'copy', lambda s, d: dest.write_bytes(b'y'))
    info_calls = []
    monkeypatch.setattr(GPT.messagebox, 'showinfo', lambda *a, **k: info_calls.append(a))
    monkeypatch.setattr(GPT.messagebox, 'showerror', lambda *a, **k: None)

    client.save_diagram()

    assert dest.exists()
    assert info_calls


def test_copy_diagram(monkeypatch):
    client = _client()
    client._diagram_path = "foo.png"
    clipboard = {}
    client.window = SimpleNamespace(
        clipboard_clear=lambda: clipboard.update(clear=True),
        clipboard_append=lambda v: clipboard.update(value=v),
    )
    info_calls = []
    monkeypatch.setattr(GPT.messagebox, "showinfo", lambda *a, **k: info_calls.append(a))
    monkeypatch.setattr(GPT.messagebox, "showerror", lambda *a, **k: None)

    client.copy_diagram()

    assert clipboard.get("value") == "foo.png"
    assert info_calls
