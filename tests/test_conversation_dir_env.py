import importlib
import sys
import types
import tkinter


def test_conversation_dir_from_env(monkeypatch, tmp_path):
    dummy_ctk = types.SimpleNamespace(
        set_appearance_mode=lambda *a, **k: None,
        set_default_color_theme=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, 'customtkinter', dummy_ctk)
    monkeypatch.setattr(tkinter, 'Tk', lambda: (_ for _ in ()).throw(tkinter.TclError()))
    monkeypatch.setenv('CONVERSATION_DIR', str(tmp_path / 'custom'))
    if 'src.ui.main' in sys.modules:
        del sys.modules['src.ui.main']
    module = importlib.import_module('src.ui.main')
    assert module.CONV_DIR == str(tmp_path / 'custom')
