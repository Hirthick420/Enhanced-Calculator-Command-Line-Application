# app/history.py
from __future__ import annotations
from typing import List, Iterable
from .calculation import Calculation
from .calculator_memento import CalculatorMemento
from .exceptions import OperationError

__all__ = ["History"]

class History:
    """
    Manages calculation history with undo/redo using a Memento snapshot.
    - done:   list[Calculation] (chronological)
    - undone: stack[list[Calculation]] (LIFO for redo)
    """
    def __init__(self, max_size: int = 1000):
        if max_size <= 0:
            raise OperationError("max_size must be positive")
        self._done: List[Calculation] = []
        self._undone: List[Calculation] = []
        self._max_size = int(max_size)

    # ---------- basic info ----------
    def size(self) -> int:
        return len(self._done)

    def is_empty(self) -> bool:
        return not self._done

    def items(self) -> List[Calculation]:
        # return a defensive copy
        return list(self._done)

    # ---------- mutation ----------
    def add(self, calc: Calculation) -> None:
        if not isinstance(calc, Calculation):
            raise OperationError("Only Calculation can be added")
        # new action invalidates redo stack
        self._undone.clear()
        self._done.append(calc.with_timestamp())
        # enforce max size by trimming from the oldest
        overflow = len(self._done) - self._max_size
        if overflow > 0:
            del self._done[0:overflow]

    def clear(self) -> None:
        self._done.clear()
        self._undone.clear()

    # ---------- undo/redo ----------
    def undo(self) -> Calculation:
        if not self._done:
            raise OperationError("Nothing to undo")
        c = self._done.pop()
        self._undone.append(c)
        return c

    def redo(self) -> Calculation:
        if not self._undone:
            raise OperationError("Nothing to redo")
        c = self._undone.pop()
        self._done.append(c)
        return c

    # ---------- memento ----------
    def create_memento(self) -> CalculatorMemento:
        return CalculatorMemento(done=tuple(self._done))

    def restore(self, m: CalculatorMemento) -> None:
        # restoring invalidates redo
        self._undone.clear()
        self._done = list(m.done)

    # ---------- convenience ----------
    def extend(self, calcs: Iterable[Calculation]) -> None:
        for c in calcs:
            self.add(c)
