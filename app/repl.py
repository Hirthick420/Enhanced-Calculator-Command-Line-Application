# app/repl.py
from __future__ import annotations
import os
import sys
import shlex
from typing import Callable, Tuple

from app.calculator import Calculator
from app.exceptions import OperationError
from app.command_registry import command, register, get_commands, help_lines
from app.command_pattern import CommandQueue, MathCommand
from app.help_decorator import with_help, help_entries, register_help

_QUEUE = CommandQueue()

Number = float
Handler = Callable[[Calculator, list[str]], str]

# ---------------- Color support ----------------
CYAN = GREEN = RED = RESET = ""  # will be set by _init_colors()

def _init_colors() -> None:
    """
    Initialize color constants. If colorama is present, use it.
    If not, keep the exported constants as empty strings (to satisfy tests),
    and we'll inject raw ANSI escapes at print time in helpers.
    """
    global CYAN, GREEN, RED, RESET
    try:
        from colorama import Fore, Style, init as colorama_init
        colorama_init(autoreset=True)
        CYAN, GREEN, RED, RESET = Fore.CYAN, Fore.GREEN, Fore.RED, Style.RESET_ALL
    except Exception:
        # Leave constants empty. Helpers will supply raw ANSI when needed.
        CYAN = GREEN = RED = RESET = ""

_init_colors()

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

def _wrap_with(color_start: str, s: str, color_reset: str, raw_start: str) -> str:
    start = color_start if color_start else raw_start
    reset = color_reset if color_reset else "\x1b[0m"
    return f"{start}{s}{reset}"

def _color_ok(s: str) -> str:
    return _wrap_with(GREEN, s, RESET, "\x1b[32m")

def _color_err(s: str) -> str:
    return _wrap_with(RED, s, RESET, "\x1b[31m")

def _color_banner(s: str) -> str:
    return _wrap_with(CYAN, s, RESET, "\x1b[36m")
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

# ---------------- Command Pattern: queue support ----------------
@with_help("enqueue", "queue an operation: enqueue <op> <a> <b>")
@command("enqueue", "queue an operation: enqueue <op> <a> <b>")
def _enqueue(calc: Calculator, args: list[str]) -> str:
    if len(args) != 3:
        return "error: usage: enqueue <op> <a> <b>"
    op, a, b = args[0], args[1], args[2]
    try:
        cmd = MathCommand(op, float(a), float(b))
    except ValueError:
        return "error: arguments must be numbers"
    _QUEUE.enqueue(cmd)
    return f"enqueued: {op} {float(a)} {float(b)}"

@with_help("queue", "show queued commands")
@command("queue", "show queued commands")
def _queue_show(_calc: Calculator, _args: list[str]) -> str:
    items = _QUEUE.list()
    return "queue: empty" if not items else "\n".join(items)

@with_help("runqueue", "run and clear the queued commands")
@command("runqueue", "run and clear the queued commands")
def _runqueue(calc: Calculator, _args: list[str]) -> str:
    results = _QUEUE.run_all(calc)
    if not results:
        return "queue: empty"
    return "\n".join(results)

@with_help("clearqueue", "clear queued commands")
@command("clearqueue", "clear queued commands")
def _clearqueue(_calc: Calculator, _args: list[str]) -> str:
    n = _QUEUE.clear()
    return f"queue cleared ({n} item(s) removed)"
# ---------------------------------------------------------------

@with_help("history", "show history")
@command("history", "show history")
def _history(calc: Calculator, _args: list[str]) -> str:
    items = calc.history.items()
    if not items:
        return "history: empty"
    return "\n".join(f"{c.operation}({c.a}, {c.b}) = {c.result} [{c.timestamp}]" for c in items)

@with_help("clear", "clear history")
@command("clear", "clear history")
def _clear(calc: Calculator, _args: list[str]) -> str:
    calc.history.clear()
    return "history cleared"

@with_help("undo", "undo last calculation")
@command("undo", "undo last calculation")
def _undo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.undo()
    return f"undo: {c.operation}({c.a}, {c.b})"

@with_help("redo", "redo last undone calculation")
@command("redo", "redo last undone calculation")
def _redo(calc: Calculator, _args: list[str]) -> str:
    c = calc.history.redo()
    return f"redo: {c.operation}({c.a}, {c.b})"

@with_help("save", "save history to CSV")
@command("save", "save history to CSV")
def _save(calc: Calculator, _args: list[str]) -> str:
    path = calc.history.save()
    return f"saved: {path}"

@with_help("load", "load history from CSV")
@command("load", "load history from CSV")
def _load(calc: Calculator, _args: list[str]) -> str:
    n = calc.history.load()
    return f"loaded: {n} item(s)"

@command("help", "show this help")
@command("help", "show this help")
def _help(_calc: Calculator, _args: list[str]) -> str:
    """
    Build help strictly from the LIVE registry to stay dynamic.
    Any entries present only in help_lines() (e.g., 'dummy' from a decorator demo)
    are filtered out unless they exist in the current registry.
    """
    live = set(get_commands().keys())
    # keep only descriptions for commands that are actually live
    filtered: list[tuple[str, str]] = [(n, d) for n, d in help_lines() if n in live]

    # if a command is live but has no description, still show it with a placeholder
    described = {n for n, _ in filtered}
    for name in sorted(live):
        if name not in described:
            filtered.append((name, "no description"))

    # stable sort by name
    filtered.sort(key=lambda x: x[0])

    lines = ["Commands:"]
    for name, desc in filtered:
        lines.append(f"  {name:<12} – {desc}")
    return "\n".join(lines)

@with_help("exit", "exit the program")
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
    register_help(_name, _desc)          # Decorator registry
    register(_name, _op(_name), _desc)   # Existing command registry

def _seed_registry_if_needed() -> None:
    cmds = get_commands()
    if "help" in cmds:
        return
    # re-register baseline commands
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
        register_help(_name, _desc)
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
        if out == "__EXIT__":
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
    print(_color_banner(banner) if use_color else banner, file=stdout)

    while True:
        stdout.write("> ")
        stdout.flush()
        line = stdin.readline()
        if not line:
            break
        cont, out = process_line(calc, line)
        if out:
            if use_color and out.startswith("error:"):
                print(_color_err(out), file=stdout)
            elif use_color:
                print(_color_ok(out), file=stdout)
            else:
                print(out, file=stdout)
        if not cont:
            break
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_loop())  # pragma: no cover
