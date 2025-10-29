# tests/test_observers_config.py
import logging
from pathlib import Path
import pandas as pd
import pytest

def _reset_loggers_for_test():
    """Make logger initialization deterministic between tests."""
    # reset our module-level cache
    import app.logger as logger_mod
    logger_mod._loggers.clear()

    # also clear global logger handlers for the 'calculator' logger
    lg = logging.getLogger("calculator")
    for h in list(lg.handlers):
        lg.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass
    lg.handlers.clear()


def test_logging_and_autosave_observers(tmp_path, monkeypatch):
    _reset_loggers_for_test()

    # point config to temp dirs and enable autosave
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "calc.log")
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "history.csv")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "10")

    from app.calculator import Calculator, LoggingObserver, AutoSaveObserver

    calc = Calculator(observers=[LoggingObserver(), AutoSaveObserver()])
    out_csv = tmp_path / "hist" / "history.csv"
    out_log = tmp_path / "logs" / "calc.log"

    # run a couple of operations
    c1 = calc.execute("add", 2, 3)
    c2 = calc.execute("multiply", 2, 4)
    assert c1.uid and c2.uid

    # CSV exists and has both rows
    assert out_csv.exists()
    df = pd.read_csv(out_csv)
    assert list(df.columns) == ["id", "operation", "a", "b", "result", "timestamp"]
    assert len(df) == 2
    assert df.loc[0, "operation"] == "add"
    assert df.loc[1, "operation"] == "multiply"
    assert isinstance(df.loc[0, "id"], str) and isinstance(df.loc[0, "timestamp"], str)

    # log file exists and contains at least one line
    assert out_log.exists()
    content = out_log.read_text(encoding="utf-8")
    assert "op=add" in content and "result=" in content


def test_autosave_respects_toggle_off(tmp_path, monkeypatch):
    _reset_loggers_for_test()

    # point env vars to fresh temp paths, and disable autosave
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "h"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "l"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "c.log")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")

    from app.calculator import Calculator, AutoSaveObserver, LoggingObserver

    calc = Calculator(observers=[AutoSaveObserver(), LoggingObserver()])
    calc.execute("add", 1, 1)

    # CSV should not exist if autosave is off
    assert not (tmp_path / "h" / "h.csv").exists()
    # Log should exist even when autosave is off
    assert (tmp_path / "l" / "c.log").exists()


def test_input_limit_raises(monkeypatch):
    _reset_loggers_for_test()

    # very small limit to force a failure
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "10")

    from app.calculator import Calculator
    with pytest.raises(Exception):
        Calculator([]).execute("add", 11, 0)
