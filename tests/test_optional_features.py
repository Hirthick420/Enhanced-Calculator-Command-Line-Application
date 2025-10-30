# tests/test_optional_features.py
from io import StringIO
import os
from app.command_registry import clear, register, help_lines
from app.repl import process_line, run_loop
from app.calculator import Calculator

def test_dynamic_help_updates_when_registering_new_command(monkeypatch):
    # Isolate registry for this test
    clear()
    # Re-register one tiny command and verify help sees it
    def hello(_calc, _args): return "hello"
    register("hello", hello, "say hello")

    calc = Calculator(observers=[])
    cont, out = process_line(calc, "help")
    assert cont is True
    assert "Commands:" in out
    assert "hello" in out and "say hello" in out

def test_color_outputs_enabled_when_forced_true(monkeypatch):
    # Turn on color explicitly and provide a stdout with isatty=True
    monkeypatch.setenv("CALCULATOR_COLOR", "true")

    class TtyStringIO(StringIO):
        def isatty(self): return True

    stdin = StringIO("add 1 1\nexit\n")
    stdout = TtyStringIO()
    code = run_loop(stdin=stdin, stdout=stdout)
    s = stdout.getvalue()
    assert code == 0
    # Presence of ANSI escape sequence
    assert "\x1b[" in s
