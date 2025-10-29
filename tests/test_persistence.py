# tests/test_persistence.py
from pathlib import Path
import pandas as pd
import pytest
from app.history import History
from app.calculation import Calculation

def test_history_save_and_load_roundtrip(tmp_path, monkeypatch):
    # route history file to a temp folder
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    h = History()
    h.add(Calculation("add", 1, 2, 3))
    h.add(Calculation("multiply", 2, 3, 6))

    out = h.save()
    assert out.exists()

    # Load into a fresh History instance
    h2 = History()
    loaded = h2.load()
    assert loaded == 2
    assert h2.size() == 2
    items = h2.items()
    assert items[0].operation == "add" and items[0].result == 3
    assert items[1].operation == "multiply" and items[1].result == 6

def test_history_load_missing_file_returns_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "missing.csv")

    h = History()
    loaded = h.load()  # file does not exist
    assert loaded == 0
    assert h.size() == 0

def test_history_load_malformed_is_graceful(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "bad.csv")

    # write malformed CSV (missing required columns)
    bad = tmp_path / "bad.csv"
    bad.write_text("not,valid,columns\n1,2,3\n", encoding="utf-8")

    h = History()
    loaded = h.load()
    assert loaded == 0
    assert h.size() == 0

def test_history_save_raises_operationerror_on_io_failure(tmp_path, monkeypatch):
    # Route file to a writable directory but force to_csv to fail
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "cannot.csv")

    h = History()
    h.add(Calculation("add", 1, 2, 3))

    def boom(*args, **kwargs):
        raise OSError("disk error")

    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)

    from app.exceptions import OperationError
    with pytest.raises(OperationError):
        h.save()  # must hit the except path in save()

def test_history_load_handles_read_exception_gracefully(tmp_path, monkeypatch):
    # Create a file so we pass the "exists" check, then make read_csv blow up
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "bad.csv")

    bad = tmp_path / "bad.csv"
    bad.write_text("id,operation,a,b,result,timestamp\n", encoding="utf-8")

    def blow(*args, **kwargs):
        raise ValueError("parse error")

    monkeypatch.setattr(pd, "read_csv", blow)

    h = History()
    loaded = h.load()  # must hit the except path in load()
    assert loaded == 0
    assert h.size() == 0