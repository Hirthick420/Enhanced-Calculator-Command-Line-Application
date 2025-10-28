# app/calculator_memento.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from .calculation import Calculation  # package-relative import

__all__ = ["CalculatorMemento"]

@dataclass(frozen=True)
class CalculatorMemento:
    """Immutable snapshot of the 'done' list."""
    done: Tuple[Calculation, ...]
