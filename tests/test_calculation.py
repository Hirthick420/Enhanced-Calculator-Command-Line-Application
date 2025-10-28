# tests/test_calculation.py
from app.calculation import Calculation

def test_with_timestamp_preserves_existing():
    c = Calculation("add", 1, 2, 3, timestamp="2025-01-01T00:00:00+00:00")
    c2 = c.with_timestamp()
    # same object values, not None, unchanged timestamp
    assert c2.timestamp == "2025-01-01T00:00:00+00:00"

def test_to_dict_forces_timestamp_and_roundtrip_without_timestamp():
    c = Calculation("sub", 5, 2, 3, timestamp=None)
    d = c.to_dict()  # must inject a timestamp
    assert isinstance(d["timestamp"], str) and len(d["timestamp"]) >= 19

    # from_dict without timestamp should yield None timestamp in object
    c2 = Calculation.from_dict(
        {"operation": "mul", "a": 2, "b": 3, "result": 6}
    )
    assert c2.timestamp is None
    assert c2.operation == "mul" and c2.a == 2 and c2.b == 3 and c2.result == 6
