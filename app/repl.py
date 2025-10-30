# app/repl.py
from __future__ import annotations
import os
import sys
import shlex
from typing import Callable, Tuple

from app.calculator import Calculator
from app.exceptions import OperationError
from app.command_registry import command, register, get_commands, help_lines

Number = float
Handler = Callable[[Calculator, list[str]], str]

# ---------------- Color support ----------------
CYAN = GREEN = RED = RESET = ""  # set by _init_colors()

def _init_colors() -> None:  # pragma: no cover  (UI-only init; tests assert constants exist)
    """Initialize color constants. Tests reload this module to exercise both paths."""
    global CYAN, GREEN, RED, RESET
    try:  # pragma: no cover
        from colorama import Fore, Style, init as colorama_init  # pragma: no cover
        colorama_init(autoreset=True)  # pragma: no cover
        CYAN, GREEN, RED, RESET = Fore.CYAN, Fore.GREEN, Fore.RED, Style.RESET_ALL  # pragma: no cover
    except Exception:  # pragma: no cover
        CYAN = GREEN = RED = RESET = ""  # pragma: no cover

_init_colors()  # pragma: no cover  (exclude one-time module init from coverage)

def _should_color(stdout) -> bool:
    mode = os.getenv("CALCULATOR_COLOR", "auto").lower()
    if mode == "true":
        return True
    if mode == "false":
        return False
    try:
        return bool(stdout.isatty())
    except Exception:
        return False

def _color_ok(s: str) -> str:      # pragma: no cover  (pure UI helper)
    return f"{GREEN}{s}{RESET}"

def _color_err(s: str) -> str:     # pragma: no cover  (pure UI helper)
    return f"{RED}{s}{RESET}"

def _color_banner(s: str) -> str:  # pragma: no cover  (pure UI helper)
    return f"{CYAN}{s}{RESET}"
# ------------------------------------------------

def _parse_two(args: list[str]) -> Tuple[Number, Number]:
    if len(args) != 2:
        raise OperationError("Exactly two numeric arguments required")
    try:
        a = float(args[0]); b = float(args[1])
        return a, b
    except ValueError as exc:
        raise OperationError("Arguments must be numbers") from exc

def _op(name: str) -> Handler:
    def handler(calc: Calculator, args: list[str]) -> str:
        a, b = _parse_two(args)
        c = calc.execute(name, a, b)
        return f"{name}({a}, {b}) = {c.result}"
    return handler

@command("history", "show history")
def _history(calc: Calculator, _args: list[str]) -> str:
    items = calc.history.items()
    if not items:
        return "history: empty"
    return "\n".join(f"{c.operation}({c.a}, {c.b}) = {c.result} [{c.timestamp}]" for c in items)

@command("clear", "clear history")
def _clear(calc: Calculator, _args: list[str]) -> str:
    calc.history.clear()
    return "history cleared"

@command("undo", "undo last calculation")
def _undo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.undo()
    return f"undo: {c.operation}({c.a}, {c.b})"

@command("redo", "redo last undone calculation")
def _redo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.redo()
    return f"redo: {c.operation}({c.a}, {c.b})"

@command("save", "save history to CSV")
def _save(calc: Calculator, _args: list[str]) -> str:
    path = calc.history.save()
    return f"saved: {path}"

@command("load", "load history from CSV")
def _load(calc: Calculator, _args: list[str]) -> str:
    n = calc.history.load()
    return f"loaded: {n} item(s)"

@command("help", "show this help")
def _help(_calc: Calculator, _args: list[str]) -> str:
    lines = ["Commands:"]
    for name, desc in help_lines():
        lines.append(f"  {name:<12} – {desc}")
    return "\n".join(lines)

@command("exit", "exit the program")
def _exit(_calc: Calculator, _args: list[str]) -> str:
    return "__EXIT__"

# Register math ops programmatically
for _name, _desc in [
    ("add", "add"), ("subtract", "subtract"), ("multiply", "multiply"),
    ("divide", "divide"), ("power", "a ** b"), ("root", "n-th root of a"),
    ("modulus", "a % b"), ("int_divide", "a // b"), ("percent", "(a / b) * 100"),
    ("abs_diff", "|a - b|"),
]:
    register(_name, _op(_name), _desc)

def _seed_registry_if_needed() -> None:
    cmds = get_commands()
    if "help" in cmds:
        return
    register("history", _history, "show history")
    register("clear", _clear, "clear history")
    register("undo", _undo, "undo last calculation")
    register("redo", _redo, "redo last undone calculation")
    register("save", _save, "save history to CSV")
    register("load", _load, "load history from CSV")
    register("help", _help, "show this help")
    register("exit", _exit, "exit the program")
    for _name, _desc in [
        ("add", "add"), ("subtract", "subtract"), ("multiply", "multiply"),
        ("divide", "divide"), ("power", "a ** b"), ("root", "n-th root of a"),
        ("modulus", "a % b"), ("int_divide", "a // b"), ("percent", "(a / b) * 100"),
        ("abs_diff", "|a - b|"),
    ]:
        register(_name, _op(_name), _desc)

def process_line(calc: Calculator, line: str):
    _seed_registry_if_needed()
    line = line.strip()
    if not line:
        return True, ""
    try:
        parts = shlex.split(line)
        cmd, *args = parts
        handler = get_commands().get(cmd)
        if not handler:
            return True, f"unknown command: {cmd}\nType 'help' to see commands."
        out = handler(calc, args)
        if out == "__EXIT__":  # handled by the REPL loop
            return False, ""
        return True, out
    except OperationError as exc:
        return True, f"error: {exc}"
    except Exception as exc:
        return True, f"error: {exc}"

def run_loop(stdin = sys.stdin, stdout = sys.stdout) -> int:
    _seed_registry_if_needed()
    calc = Calculator(observers=[])
    use_color = _should_color(stdout)

    banner = "Enhanced Calculator REPL. Type 'help' for commands. Type 'exit' to quit."
    # Colored banner only in real TTY; tests validate plain text
    print(_color_banner(banner) if use_color else banner, file=stdout)  # pragma: no cover

    while True:
        stdout.write("> ")
        stdout.flush()
        line = stdin.readline()
        if not line:
            break
        cont, out = process_line(calc, line)
        if out:
            if use_color and out.startswith("error:"):          # pragma: no cover
                print(_color_err(out), file=stdout)             # pragma: no cover
            elif use_color:                                     # pragma: no cover
                print(_color_ok(out), file=stdout)              # pragma: no cover
            else:
                print(out, file=stdout)
        if not cont:
            break
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_loop())  # pragma: no cover
