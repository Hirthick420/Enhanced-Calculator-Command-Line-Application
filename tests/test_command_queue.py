# tests/test_command_queue.py
from io import StringIO
import importlib
import sys
import pytest

from app.calculator import Calculator
from app.repl import process_line

def test_queue_end_to_end(monkeypatch, tmp_path):
    # isolate persistence so tests don't touch real FS
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    calc = Calculator(observers=[])

    # enqueue a couple commands
    ok, out = process_line(calc, "enqueue add 2 3")
    assert ok and "enqueued:" in out
    ok, out = process_line(calc, "enqueue percent 50 200")
    assert ok and "enqueued:" in out

    # list queue
    ok, out = process_line(calc, "queue")
    assert ok
    # tolerate formatting differences, just check key substrings
    assert "add 2.0 3.0" in out
    assert "percent 50.0 200.0" in out

    # run queued commands
    ok, out = process_line(calc, "runqueue")
    assert ok
    assert "add(2.0, 3.0) = 5.0" in out
    assert "percent(50.0, 200.0) = 25.0" in out

    # queue is now empty
    ok, out = process_line(calc, "queue")
    assert ok and "empty" in out

def test_clearqueue_and_bad_args(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    calc = Calculator(observers=[])

    # clear after enqueue
    process_line(calc, "enqueue power 2 3")
    ok, out = process_line(calc, "clearqueue")
    assert ok and "queue cleared" in out
    ok, out = process_line(calc, "queue")
    assert ok and "empty" in out

    # bad args (coverage for argument validation)
    ok, out = process_line(calc, "enqueue add 2")
    assert ok and "error:" in out

def test_color_init_success_path():
    # reload to hit the color success path
    import app.repl as repl
    importlib.reload(repl)
    # attributes must exist even if colors are empty strings
    assert hasattr(repl, "CYAN")
    assert hasattr(repl, "GREEN")
    assert hasattr(repl, "RED")
    assert hasattr(repl, "RESET")

def test_color_init_fallback_path(monkeypatch):
    # force Colorama "missing" and reload to exercise except-branch
    monkeypatch.setitem(sys.modules, "colorama", None)
    import app.repl as repl
    importlib.reload(repl)
    assert (repl.CYAN, repl.GREEN, repl.RED, repl.RESET) == ("", "", "", "")
