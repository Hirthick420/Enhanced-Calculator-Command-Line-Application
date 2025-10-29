# app/calculator_config.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

def _as_bool(s: str | None, default: bool) -> bool:
    if s is None:
        return default
    return s.strip().lower() in {"1", "true", "yes", "y", "on"}

def _as_int(s: str | None, default: int) -> int:
    try:
        return int(s) if s is not None else default
    except Exception:
        return default

@dataclass(frozen=True)
class Config:
    log_dir: Path
    history_dir: Path
    log_file: str
    history_file: str
    max_history_size: int
    auto_save: bool
    precision: int
    max_input_value: float
    default_encoding: str

def load_config() -> Config:
    load_dotenv()  # load .env if present

    log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", "var/logs"))
    history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", "var/history"))
    log_file = os.getenv("CALCULATOR_LOG_FILE", "calculator.log")
    history_file = os.getenv("CALCULATOR_HISTORY_FILE", "history.csv")

    max_history_size = _as_int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE"), 1000)
    auto_save = _as_bool(os.getenv("CALCULATOR_AUTO_SAVE"), True)

    precision = _as_int(os.getenv("CALCULATOR_PRECISION"), 6)
    max_input_value = float(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e12"))
    default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    # ensure dirs exist
    log_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)

    return Config(
        log_dir=log_dir,
        history_dir=history_dir,
        log_file=log_file,
        history_file=history_file,
        max_history_size=max_history_size,
        auto_save=auto_save,
        precision=precision,
        max_input_value=max_input_value,
        default_encoding=default_encoding,
    )
