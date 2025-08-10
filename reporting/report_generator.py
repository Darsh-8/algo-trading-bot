"""
Report generator: produce CSV/PDF/Excel summaries.
(Keep simple for this assignment; can be extended.)
"""

from pathlib import Path

import pandas as pd

from config import settings
from utils.logger import logger


def save_trade_report(trades_df: pd.DataFrame, symbol: str) -> Path:
    """
    Save trades to CSV and return path.
    """
    out_dir = Path(settings.DATA_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{symbol}_trades.csv"
    trades_df.to_csv(path, index=False)
    logger.info("Saved trade report to %s", path)
    return path