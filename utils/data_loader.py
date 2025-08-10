"""
Data loader utilities: fetch and persist historical data.
Uses yfinance for now; safe file operations and logging included.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

from config import settings
from utils.logger import logger


def fetch_and_save_stock_data(ticker: str, period: str = "6mo",
                              interval: str = "1d") -> Path:
    """
    Fetch historical stock data and save as CSV in DATA_DIR.

    Args:
        ticker (str): Ticker string (e.g., "TCS.NS")
        period (str): yfinance period (default "6mo")
        interval (str): yfinance interval (default "1d")

    Returns:
        Path: Path to saved CSV file
    """
    try:
        logger.info("Fetching data for %s (%s, %s)", ticker, period, interval)
        df = yf.download(ticker, period=period, interval=interval,
                         auto_adjust=False)
        if df.empty:
            logger.warning("No data returned for %s", ticker)
            raise ValueError(f"No data for {ticker}")

        df = df.reset_index()[
            ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
        symbol = ticker.replace('.NS', '').replace('.BO', '')
        file_path = Path(settings.DATA_DIR) / f"{symbol}.csv"
        df.to_csv(file_path, index=False)
        _clean_corrupt_rows(file_path)
        logger.info("Saved cleaned data to %s", file_path)
        return file_path
    except Exception as exc:
        logger.exception("Failed to fetch/save data for %s: %s", ticker, exc)
        raise


def _clean_corrupt_rows(file_path: Path) -> None:
    """
    Clean non-numeric rows and invalid entries from a saved CSV.
    """
    try:
        df = pd.read_csv(file_path)
        # remove rows where numeric columns are non-numeric
        for col in ['Close', 'High', 'Low', 'Open', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        df.to_csv(file_path, index=False)
    except Exception:
        logger.exception("Failed to clean %s", file_path)
        raise
