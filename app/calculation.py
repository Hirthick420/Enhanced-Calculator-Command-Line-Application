# app/calculation.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from typing import Dict, Any
import uuid

@dataclass(frozen=True)
class Calculation:
    operation: str
    a: float
    b: float
    result: float
    uid: str | None = None
    timestamp: str | None = None  # ISO 8601 with +00:00

    def with_timestamp(self) -> "Calculation":
        """Ensure uid and timestamp exist; return an updated immutable instance."""
        if self.uid is not None and self.timestamp is not None:
            return self
        return Calculation(
            operation=self.operation,
            a=self.a,
            b=self.b,
            result=self.result,
            uid=self.uid or str(uuid.uuid4()),
            timestamp=self.timestamp or datetime.now(UTC).isoformat(timespec="seconds"),
        )

    def to_dict(self) -> Dict[str, Any]:
        c = self.with_timestamp()
        d = asdict(c)
        return {
            "id": d["uid"],
            "operation": d["operation"],
            "a": d["a"],
            "b": d["b"],
            "result": d["result"],
            "timestamp": d["timestamp"],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Calculation":
        cid = d.get("id", d.get("uid", None))
        ts = d.get("timestamp", None)
        return Calculation(
            operation=str(d["operation"]),
            a=float(d["a"]),
            b=float(d["b"]),
            result=float(d["result"]),
            uid=str(cid) if cid is not None else None,
            timestamp=str(ts) if ts is not None else None,
        )
