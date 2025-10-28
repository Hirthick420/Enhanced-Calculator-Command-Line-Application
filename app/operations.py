# app/operations.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Callable, Dict
from math import isfinite
from app.exceptions import OperationError

class Operation(Protocol):
    def execute(self, a: float, b: float) -> float: ...

@dataclass(frozen=True)
class Add:
    def execute(self, a: float, b: float) -> float:
        return a + b

@dataclass(frozen=True)
class Subtract:
    def execute(self, a: float, b: float) -> float:
        return a - b

@dataclass(frozen=True)
class Multiply:
    def execute(self, a: float, b: float) -> float:
        return a * b

@dataclass(frozen=True)
class Divide:
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Division by zero")
        return a / b

@dataclass(frozen=True)
class Power:
    def execute(self, a: float, b: float) -> float:
        try:
            result = a ** b
        except Exception as exc:
            raise OperationError(f"Invalid power operation: {exc}") from exc
        if not isfinite(result):
            raise OperationError("Result not finite in power operation")
        return result

@dataclass(frozen=True)
class Root:
    """
    Computes the nth root of a: root(a, n) = a ** (1/n).
    We restrict n to a nonzero integer. If a < 0 then n must be odd.
    """
    def execute(self, a: float, b: float) -> float:
        # b is n (the degree)
        if int(b) != b or b == 0:
            raise OperationError("Root degree must be a nonzero integer")
        n = int(b)
        if a < 0 and n % 2 == 0:
            raise OperationError("Even root of a negative number is not real")
        try:
            result = a ** (1.0 / n)
        except Exception as exc:
            raise OperationError(f"Invalid root operation: {exc}") from exc
        if not isfinite(result):
            raise OperationError("Result not finite in root operation")
        return result

@dataclass(frozen=True)
class Modulus:
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Modulus by zero")
        return a % b

@dataclass(frozen=True)
class IntDivide:
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Integer division by zero")
        # Truncate toward zero to match typical integer division semantics
        return int(a) // int(b)

@dataclass(frozen=True)
class Percent:
    """
    Percentage(a, b) computes (a / b) * 100
    """
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Percentage denominator cannot be zero")
        return (a / b) * 100.0

@dataclass(frozen=True)
class AbsDiff:
    def execute(self, a: float, b: float) -> float:
        return abs(a - b)

# Factory

_FACTORY: Dict[str, Callable[[], Operation]] = {
    "add": Add,
    "subtract": Subtract,
    "multiply": Multiply,
    "divide": Divide,
    "power": Power,
    "root": Root,
    "modulus": Modulus,
    "int_divide": IntDivide,
    "percent": Percent,
    "abs_diff": AbsDiff,
}

def create_operation(name: str) -> Operation:
    """
    Factory function that returns a new operation instance.
    """
    op_name = name.strip().lower()
    cls = _FACTORY.get(op_name)
    if cls is None:
        raise OperationError(f"Unknown operation: {name}")
    return cls()
