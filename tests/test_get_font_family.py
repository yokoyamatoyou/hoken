import tkinter
from types import SimpleNamespace
from src.ui import main as GPT


def test_get_font_family_tclerror(monkeypatch):
    def raise_tclerror(*args, **kwargs):
        raise tkinter.TclError('no display')
    monkeypatch.setattr(tkinter, 'Tk', raise_tclerror)
    assert GPT.get_font_family() == "Helvetica"


def test_get_font_family_env(monkeypatch):
    fonts = ["MyFont", "Helvetica"]

    class DummyTk:
        def __init__(self):
            self.tk = SimpleNamespace(call=lambda *a: fonts)

        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tkinter, "Tk", DummyTk)
    monkeypatch.setenv("PREFERRED_FONT", "Missing, MyFont")
    try:
        assert GPT.get_font_family() == "MyFont"
    finally:
        monkeypatch.delenv("PREFERRED_FONT", raising=False)


def test_get_font_family_env_missing(monkeypatch):
    fonts = ["Helvetica"]

    class DummyTk:
        def __init__(self):
            self.tk = SimpleNamespace(call=lambda *a: fonts)

        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tkinter, "Tk", DummyTk)
    monkeypatch.setenv("PREFERRED_FONT", "Missing1, Missing2")
    try:
        assert GPT.get_font_family() == "Helvetica"
    finally:
        monkeypatch.delenv("PREFERRED_FONT", raising=False)


def test_get_font_family_env_fallback(monkeypatch):
    fonts = ["Meiryo", "Helvetica"]

    class DummyTk:
        def __init__(self):
            self.tk = SimpleNamespace(call=lambda *a: fonts)

        def withdraw(self):
            pass

        def destroy(self):
            pass

    monkeypatch.setattr(tkinter, "Tk", DummyTk)
    monkeypatch.setenv("PREFERRED_FONT", "Missing1, Missing2")
    try:
        assert GPT.get_font_family() == "Meiryo"
    finally:
        monkeypatch.delenv("PREFERRED_FONT", raising=False)
