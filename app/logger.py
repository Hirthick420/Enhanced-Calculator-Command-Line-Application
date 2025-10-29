# app/logger.py
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .calculator_config import load_config

_loggers: dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]

    cfg = load_config()
    log_path = cfg.log_dir / cfg.log_file

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(log_path, maxBytes=512_000, backupCount=2, encoding=cfg.default_encoding)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    _loggers[name] = logger
    return logger
