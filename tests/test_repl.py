# tests/test_repl.py
from io import StringIO
import runpy
import sys
from app.repl import process_line, run_loop
from app.calculator import Calculator
import pytest

def test_process_line_math_and_history(monkeypatch, tmp_path):
    # configure history path so save/load won't hit the real fs root
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    calc = Calculator(observers=[])
    cont, out = process_line(calc, "add 2 3")
    assert cont and "add(2.0, 3.0) = 5.0" in out

    cont, out = process_line(calc, "history")
    assert cont and "add(2.0, 3.0) = 5.0" in out

    # undo/redo
    cont, out = process_line(calc, "undo")
    assert cont and "undo: add(2.0, 3.0)" in out
    cont, out = process_line(calc, "redo")
    assert cont and "redo: add(2.0, 3.0)" in out

    # save/load
    cont, out = process_line(calc, "save")
    assert cont and "saved:" in out
    cont, out = process_line(calc, "load")
    assert cont and "loaded:" in out

def test_process_line_errors_and_exit():
    calc = Calculator(observers=[])
    # bad command
    cont, out = process_line(calc, "nonesuch 1 2")
    assert cont and "unknown command" in out
    # not enough args
    cont, out = process_line(calc, "add 1")
    assert cont and "error:" in out
    # exit
    cont, out = process_line(calc, "exit")
    assert cont is False

def test_run_loop_end_to_end(monkeypatch):
    # small end-to-end: add, history, exit
    user_input = "add 1 4\nhistory\nexit\n"
    stdin = StringIO(user_input)
    stdout = StringIO()
    code = run_loop(stdin=stdin, stdout=stdout)
    text = stdout.getvalue()
    assert code == 0
    assert "Enhanced Calculator REPL" in text
    assert "> " in text
    assert "add(1.0, 4.0) = 5.0" in text

def test_process_line_empty_whitespace_is_noop():
    calc = Calculator(observers=[])
    cont, out = process_line(calc, "   ")
    assert cont is True and out == ""

def test_process_line_help_and_clear(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    calc = Calculator(observers=[])
    # fill history, then clear
    process_line(calc, "add 5 7")
    cont, out = process_line(calc, "help")
    assert cont is True and "Commands:" in out and "exit" in out

    cont, out = process_line(calc, "clear")
    assert cont is True and out == "history cleared"
    cont, out = process_line(calc, "history")
    assert cont is True and out == "history: empty"

def test_process_line_more_math_ops(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    calc = Calculator(observers=[])
    # hit multiple _op closures to cover mapping entries
    assert process_line(calc, "power 2 3")[1].endswith("= 8.0")
    assert process_line(calc, "percent 50 200")[1].endswith("= 25.0")
    assert process_line(calc, "abs_diff 10 3")[1].endswith("= 7.0")
    out = process_line(calc, "int_divide 7 2")[1]
    # parse the numeric suffix and compare numerically
    val_str = out.split("=")[-1].strip()
    assert float(val_str) == 3.0
    assert process_line(calc, "modulus 7 5")[1].endswith("= 2.0")
    # root(27, 3) = 3
    assert process_line(calc, "root 27 3")[1].endswith("= 3.0")

def test_run_loop_immediate_eof():
    # stdin is empty string -> readline() returns "", loop breaks via EOF branch
    stdin = StringIO("")               # immediate EOF
    stdout = StringIO()
    code = run_loop(stdin=stdin, stdout=stdout)
    assert code == 0
    text = stdout.getvalue()
    assert "Enhanced Calculator REPL" in text
    # prompt was written at least once
    assert "> " in text

def test_repl_module_main_entrypoint(monkeypatch):
    # Execute app.repl as __main__ so the __name__==\"__main__\" block runs
    # Provide input so REPL exits cleanly
    fake_stdin = StringIO("exit\n")
    fake_stdout = StringIO()
    monkeypatch.setattr(sys, "stdin", fake_stdin, raising=False)
    monkeypatch.setattr(sys, "stdout", fake_stdout, raising=False)
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("app.repl", run_name="__main__")
    assert excinfo.value.code == 0  # clean exit
    output = fake_stdout.getvalue()
    assert "Enhanced Calculator REPL" in output

def test_process_line_non_numeric_args():
    calc = Calculator(observers=[])
    cont, out = process_line(calc, "add foo 2")
    assert cont is True
    assert "error:" in out
    assert "Arguments must be numbers" in out