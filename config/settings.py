"""
App configuration and constants.
Prefer overriding via environment variables in production.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # ✅ loads .env file

LOG_DIR = os.environ.get("LOG_DIR", str(BASE_DIR / "logs"))
DATA_DIR = os.environ.get("DATA_DIR", str(BASE_DIR / "data"))
MODELS_DIR = os.environ.get("MODELS_DIR", str(BASE_DIR / "models"))

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

GS_CREDS_FILE = os.environ.get("GS_CREDS_FILE",
                               str(BASE_DIR / "service_account.json"))
SHEET_NAME = os.environ.get("SHEET_NAME", "AlgoTrading_Logs")

DEFAULT_TICKERS = os.environ.get("DEFAULT_TICKERS", "").split(
    ",") if os.environ.get("DEFAULT_TICKERS") else []
