# tests/test_config_and_logger.py
import logging
from pathlib import Path

import pytest

def _reset_global_logger(name: str = "calculator"):
    import app.logger as logger_mod
    logger_mod._loggers.clear()
    lg = logging.getLogger(name)
    for h in list(lg.handlers):
        lg.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass
    lg.handlers.clear()

def test_config_as_int_exception_fallback(tmp_path, monkeypatch):
    # Force _as_int to hit the except branch and return default
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "not-an-int")  # triggers except
    from app.calculator_config import load_config
    cfg = load_config()
    assert cfg.max_history_size == 1000  # default returned by _as_int

def test_get_logger_cache_miss_creates_handler(tmp_path, monkeypatch):
    # Exercise the cache-miss path (line where load_config() is called)
    _reset_global_logger("calculator-unique")
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "l"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "u.log")

    from app.logger import get_logger
    lg = get_logger("calculator-unique")  # cache miss -> calls load_config()
    lg.info("hello")
    out = tmp_path / "l" / "u.log"
    assert out.exists()
    assert "hello" in out.read_text(encoding="utf-8")

    # Call again to also hit the cache-hit branch (no new handler added)
    lg2 = get_logger("calculator-unique")
    assert lg is lg2
