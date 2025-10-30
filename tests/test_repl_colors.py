import importlib
import sys
import types

def test_color_init_success(monkeypatch):
    """Simulate successful Colorama import path."""
    fake_colorama = types.SimpleNamespace(
        Fore=types.SimpleNamespace(CYAN="C", GREEN="G", RED="R"),
        Style=types.SimpleNamespace(RESET_ALL="S"),
        init=lambda autoreset: None,
    )
    monkeypatch.setitem(sys.modules, "colorama", fake_colorama)
    import app.repl as repl
    importlib.reload(repl)
    assert repl.CYAN == "C"
    assert repl.GREEN == "G"
    assert repl.RED == "R"
    assert repl.RESET == "S"

def test_color_init_fallback(monkeypatch):
    """Simulate missing Colorama import path."""
    monkeypatch.setitem(sys.modules, "colorama", None)
    import importlib, app.repl as repl
    importlib.reload(repl)
    assert (repl.CYAN, repl.GREEN, repl.RED, repl.RESET) == ("", "", "", "")
