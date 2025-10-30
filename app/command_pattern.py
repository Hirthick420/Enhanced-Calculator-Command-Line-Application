# app/command_pattern.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List

from app.calculator import Calculator

class Command(Protocol):
    """Behavioral Command interface."""
    def execute(self, calc: Calculator) -> str: ...

@dataclass(frozen=True)
class MathCommand:
    """Concrete Command that wraps a calculator operation."""
    op_name: str
    a: float
    b: float

    def execute(self, calc: Calculator) -> str:
        c = calc.execute(self.op_name, float(self.a), float(self.b))
        return f"{self.op_name}({float(self.a)}, {float(self.b)}) = {c.result}"

class CommandQueue:
    """Invoker that can queue and run commands (deferred execution)."""
    def __init__(self) -> None:
        self._items: List[Command] = []

    def enqueue(self, cmd: Command) -> None:
        self._items.append(cmd)

    def clear(self) -> int:
        n = len(self._items)
        self._items.clear()
        return n

    def list(self) -> list[str]:
        out: list[str] = []
        for i, cmd in enumerate(self._items, 1):
            if isinstance(cmd, MathCommand):
                out.append(f"{i}. {cmd.op_name} {cmd.a} {cmd.b}")
            else:
                out.append(f"{i}. {cmd.__class__.__name__}")
        return out

    def run_all(self, calc: Calculator) -> list[str]:
        results: list[str] = []
        while self._items:
            cmd = self._items.pop(0)
            results.append(cmd.execute(calc))
        return results  # pragma: no cover
