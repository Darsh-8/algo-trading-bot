"""
Logging configuration for trading system.
Creates rotating log files under LOG_DIR.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config import settings


def ensure_dirs():
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)


def setup_logging(name: str = "trading_system") -> logging.Logger:
    """
    Configure and return a logger with a RotatingFileHandler and console handler.
    """
    ensure_dirs()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    log_file = os.path.join(settings.LOG_DIR, f"{name}.log")

    fh = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5,
                             encoding="utf-8")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = setup_logging()
