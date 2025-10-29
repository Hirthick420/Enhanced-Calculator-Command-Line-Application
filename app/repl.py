# app/repl.py
from __future__ import annotations
import sys
import shlex
from typing import Callable, Dict, Tuple

from app.calculator import Calculator
from app.exceptions import OperationError

Number = float
Handler = Callable[[Calculator, list[str]], str]

HELP_TEXT = """\
Commands:
  add a b           – add
  subtract a b      – subtract
  multiply a b      – multiply
  divide a b        – divide
  power a b         – a ** b
  root a n          – n-th root of a
  modulus a b       – a % b
  int_divide a b    – a // b
  percent a b       – (a / b) * 100
  abs_diff a b      – |a - b|

  history           – show history
  clear             – clear history
  undo              – undo last calculation
  redo              – redo last undone calculation
  save              – save history to CSV
  load              – load history from CSV

  help              – show this help
  exit              – exit the program
"""

def _parse_two(args: list[str]) -> Tuple[Number, Number]:
    if len(args) != 2:
        raise OperationError("Exactly two numeric arguments required")
    try:
        a = float(args[0])
        b = float(args[1])
        return a, b
    except ValueError as exc:
        raise OperationError("Arguments must be numbers") from exc

def _op(name: str) -> Handler:
    def handler(calc: Calculator, args: list[str]) -> str:
        a, b = _parse_two(args)
        c = calc.execute(name, a, b)
        return f"{name}({a}, {b}) = {c.result}"
    return handler

def _history(calc: Calculator, _args: list[str]) -> str:
    items = calc.history.items()
    if not items:
        return "history: empty"
    lines = []
    for c in items:
        lines.append(f"{c.operation}({c.a}, {c.b}) = {c.result} [{c.timestamp}]")
    return "\n".join(lines)

def _clear(calc: Calculator, _args: list[str]) -> str:
    calc.history.clear()
    return "history cleared"

def _undo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.undo()
    return f"undo: {c.operation}({c.a}, {c.b})"

def _redo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.redo()
    return f"redo: {c.operation}({c.a}, {c.b})"

def _save(calc: Calculator, _args: list[str]) -> str:
    path = calc.history.save()
    return f"saved: {path}"

def _load(calc: Calculator, _args: list[str]) -> str:
    n = calc.history.load()
    return f"loaded: {n} item(s)"

def _help(_calc: Calculator, _args: list[str]) -> str:
    return HELP_TEXT.rstrip()

def _exit(_calc: Calculator, _args: list[str]) -> str:
    # Special marker read by run_loop to stop the REPL
    return "__EXIT__"

COMMANDS: Dict[str, Handler] = {
    # math
    "add": _op("add"),
    "subtract": _op("subtract"),
    "multiply": _op("multiply"),
    "divide": _op("divide"),
    "power": _op("power"),
    "root": _op("root"),
    "modulus": _op("modulus"),
    "int_divide": _op("int_divide"),
    "percent": _op("percent"),
    "abs_diff": _op("abs_diff"),
    # history / io
    "history": _history,
    "clear": _clear,
    "undo": _undo,
    "redo": _redo,
    "save": _save,
    "load": _load,
    # meta
    "help": _help,
    "exit": _exit,
}

def process_line(calc: Calculator, line: str) -> Tuple[bool, str]:
    """
    Process a single input line and return (continue_loop, output_string).
    Useful for tests and for the interactive loop.
    """
    line = line.strip()
    if not line:
        return True, ""
    try:
        parts = shlex.split(line)
        cmd, *args = parts
        handler = COMMANDS.get(cmd)
        if not handler:
            return True, f"unknown command: {cmd}\nType 'help' to see commands."
        out = handler(calc, args)
        if out == "__EXIT__":
            return False, ""
        return True, out
    except OperationError as exc:
        return True, f"error: {exc}"
    except Exception as exc:  # pragma: no cover (paranoia)
        return True, f"error: {exc}"

def run_loop(stdin = sys.stdin, stdout = sys.stdout) -> int:
    """
    Interactive REPL. Reads from stdin, writes to stdout.
    Returns 0 on clean exit.
    """
    calc = Calculator(observers=[])  # observers not needed for REPL correctness tests
    print("Enhanced Calculator REPL. Type 'help' for commands. Type 'exit' to quit.", file=stdout)
    while True:
        stdout.write("> ")
        stdout.flush()
        line = stdin.readline()
        if not line:
            break
        cont, out = process_line(calc, line)
        if out:
            print(out, file=stdout)
        if not cont:
            break
    return 0

if __name__ == "__main__":  # manual run: python -m app.repl
    raise SystemExit(run_loop())
