# app/calculator.py
from __future__ import annotations
from typing import Protocol, List, Sequence
import pandas as pd
from pathlib import Path

from .operations import create_operation
from .calculation import Calculation
from .history import History
from .exceptions import OperationError
from .calculator_config import load_config
from .logger import get_logger

class Observer(Protocol):
    def on_new_calculation(self, calc: Calculation, history: History) -> None: ...

class LoggingObserver:
    def __init__(self) -> None:
        self._logger = get_logger("calculator")

    def on_new_calculation(self, calc: Calculation, history: History) -> None:
        c = calc.with_timestamp()
        self._logger.info(
            "op=%s a=%s b=%s result=%s id=%s ts=%s size=%d",
            c.operation, c.a, c.b, c.result, c.uid, c.timestamp, history.size(),
        )

class AutoSaveObserver:
    def __init__(self) -> None:
        self._cfg = load_config()

    def on_new_calculation(self, calc: Calculation, history: History) -> None:
        if not self._cfg.auto_save:
            return
        rows = [c.to_dict() for c in history.items()]
        df = pd.DataFrame(rows, columns=["id", "operation", "a", "b", "result", "timestamp"])
        out = self._cfg.history_dir / self._cfg.history_file
        df.to_csv(out, index=False, encoding=self._cfg.default_encoding)

class Calculator:
    def __init__(self, observers: Sequence[Observer] | None = None) -> None:
        cfg = load_config()
        self.history = History(max_size=cfg.max_history_size)
        self._observers: List[Observer] = list(observers or [])

    def add_observer(self, obs: Observer) -> None:
        self._observers.append(obs)

    def _notify(self, calc: Calculation) -> None:
        for obs in self._observers:
            obs.on_new_calculation(calc, self.history)

    def execute(self, op_name: str, a: float, b: float) -> Calculation:
        # Optional input bound check (keeps requirement ready for validators later)
        cfg = load_config()
        if abs(a) > cfg.max_input_value or abs(b) > cfg.max_input_value:
            raise OperationError("Input exceeds configured maximum")

        op = create_operation(op_name)
        result = op.execute(a, b)
        calc = Calculation(op_name, a, b, result).with_timestamp()
        self.history.add(calc)
        self._notify(calc)
        return calc
