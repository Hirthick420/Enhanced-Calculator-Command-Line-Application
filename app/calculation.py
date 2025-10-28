# app/calculation.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
from datetime import datetime, UTC

@dataclass(frozen=True)
class Calculation:
    operation: str
    a: float
    b: float
    result: float
    timestamp: str | None = None  # ISO string

    def with_timestamp(self) -> "Calculation":
        if self.timestamp is not None:
            return self
        return Calculation(
        operation=self.operation,
        a=self.a,
        b=self.b,
        result=self.result,
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self.with_timestamp())

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Calculation":
        return Calculation(
            operation=str(d["operation"]),
            a=float(d["a"]),
            b=float(d["b"]),
            result=float(d["result"]),
            timestamp=str(d.get("timestamp")) if d.get("timestamp") is not None else None,
        )

