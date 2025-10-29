# app/history.py
from __future__ import annotations
from typing import List, Iterable
from .calculation import Calculation
from .calculator_memento import CalculatorMemento
from .exceptions import OperationError

from pathlib import Path
import pandas as pd
from .calculator_config import load_config

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

    # ---------- persistence ----------
    def to_dataframe(self) -> pd.DataFrame:
        """Return the current 'done' list as a DataFrame suitable for CSV."""
        rows = [c.to_dict() for c in self._done]
        return pd.DataFrame(rows, columns=["id", "operation", "a", "b", "result", "timestamp"])

    def save(self, path: Path | None = None) -> Path:
        """
        Save the current history to CSV. Returns the file path.
        Raises OperationError if something goes wrong.
        """
        cfg = load_config()
        out = path or (cfg.history_dir / cfg.history_file)
        try:
            df = self.to_dataframe()
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False, encoding=cfg.default_encoding)
            return out
        except Exception as exc:
            raise OperationError(f"Failed to save history to {out}: {exc}") from exc

    def load(self, path: Path | None = None, clear_existing: bool = True) -> int:
        """
        Load history from CSV into this History instance.
        Returns number of records loaded. Missing/malformed files are handled gracefully (0).
        """
        cfg = load_config()
        file = path or (cfg.history_dir / cfg.history_file)
        if not file.exists():
            return 0
        try:
            df = pd.read_csv(file)
            required = {"id", "operation", "a", "b", "result", "timestamp"}
            if not required.issubset(set(df.columns)):
                # Malformed CSV; ignore but do not crash
                return 0

            items: list[Calculation] = []
            for _, row in df.iterrows():
                c = Calculation.from_dict(
                    {
                        "id": row.get("id"),
                        "operation": row["operation"],
                        "a": float(row["a"]),
                        "b": float(row["b"]),
                        "result": float(row["result"]),
                        "timestamp": row.get("timestamp"),
                    }
                ).with_timestamp()
                items.append(c)

            if clear_existing:
                self.clear()
            # Use existing add() so max-size logic stays consistent
            for c in items:
                self.add(c)
            return len(items)
        except Exception:
            # Any parse or IO problem should not crash the app during load
            return 0