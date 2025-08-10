"""
Telegram service: send detailed trade alerts.
No ML model accuracy messages, only executed trades.
"""

import os

import requests

from config import settings
from utils.logger import logger

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN or os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID or os.environ.get(
    "TELEGRAM_CHAT_ID")
BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"

_sent_messages = set()  # Track sent messages in current run


def send_telegram_message(message: str, parse_mode: str = "HTML") -> bool:
    """
    Send a Telegram message unless it was already sent in this run.
    """
    global _sent_messages
    if message in _sent_messages:
        logger.info("Skipped duplicate Telegram message: %s", message)
        return False

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not provided; skipping send.")
        return False

    url = BASE_URL.format(token=TELEGRAM_TOKEN)
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message,
               "parse_mode": parse_mode}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        _sent_messages.add(message)
        logger.info("Telegram message sent: %s", message)
        return True
    except Exception:
        logger.exception("Failed to send Telegram message.")
        return False


def format_trade_alert(
        ticker: str,
        trade_type: str,
        entry_date: str,
        exit_date: str,
        entry_price: float,
        exit_price: float,
        qty: int = None,
        ml_pred: str = None
) -> str:
    """
    Format a detailed trade alert.
    """
    pnl_value = (exit_price - entry_price) * (qty if qty else 1)
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100.0
    qty_str = f" | Qty: {qty}" if qty else ""
    ml_str = f"\nML Prediction: {ml_pred}" if ml_pred else ""

    return (f"📊 Trade Executed: {ticker}\n"
            f"Type: {trade_type}\n"
            f"Entry: {entry_date} @ ₹{entry_price}\n"
            f"Exit: {exit_date} @ ₹{exit_price}\n"
            f"PnL: ₹{pnl_value:.2f} | {pnl_pct:.2f}%{qty_str}"
            f"{ml_str}")
