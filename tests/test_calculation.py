# tests/test_calculation.py
from app.calculation import Calculation

def test_with_timestamp_preserves_existing_uuid_and_timestamp():
    c = Calculation(
        "add", 1, 2, 3,
        uid="11111111-2222-3333-4444-555555555555",
        timestamp="2025-01-01T00:00:00+00:00"
    )
    c2 = c.with_timestamp()
    assert c2.uid == "11111111-2222-3333-4444-555555555555"
    assert c2.timestamp == "2025-01-01T00:00:00+00:00"

def test_with_timestamp_generates_uuid_and_timestamp_when_missing():
    c = Calculation("sub", 5, 2, 3, uid=None, timestamp=None)
    c2 = c.with_timestamp()
    assert isinstance(c2.uid, str) and len(c2.uid) >= 32
    assert isinstance(c2.timestamp, str) and "T" in c2.timestamp

def test_to_dict_forces_timestamp_and_uses_id_key():
    c = Calculation("mul", 2, 3, 6, uid=None, timestamp=None)
    d = c.to_dict()  # must inject uid/timestamp
    assert "id" in d and isinstance(d["id"], str)
    assert isinstance(d["timestamp"], str) and len(d["timestamp"]) >= 19
    assert d["operation"] == "mul" and d["a"] == 2 and d["b"] == 3 and d["result"] == 6

def test_from_dict_roundtrip_without_id_or_timestamp():
    # when id/timestamp absent, object fields remain None
    c2 = Calculation.from_dict({"operation": "percent", "a": 50, "b": 200, "result": 25})
    assert c2.uid is None and c2.timestamp is None
    assert c2.operation == "percent" and c2.a == 50 and c2.b == 200 and c2.result == 25
