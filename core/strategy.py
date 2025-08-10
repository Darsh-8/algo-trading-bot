"""
Trading strategy implementation: RSI < 30 + 20DMA crossing above 50DMA.
Returns DataFrame with signals.
"""

import pandas as pd
import ta

from utils.logger import logger


def apply_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply indicators and generate buy signals.

    Args:
        df (pd.DataFrame): Data with at least 'Open' and 'Close'.

    Returns:
        pd.DataFrame: input df with 'RSI','SMA_20','SMA_50','Signal' columns
    """
    df = df.copy()
    try:
        df['RSI'] = ta.momentum.RSIIndicator(df['Open'], window=14).rsi()
        df['SMA_20'] = ta.trend.SMAIndicator(df['Open'],
                                             window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(df['Open'],
                                             window=50).sma_indicator()

        df['Signal'] = 0
        buy_mask = (
                (df['RSI'] < 50) 
                # & (df['SMA_20'] > df['SMA_50']) &
                # (df['SMA_20'].shift(1) <= df['SMA_50'].shift(1))
        )
        df.loc[buy_mask, 'Signal'] = 1
        logger.info("Applied strategy; found %d buy signals",
                    int(df['Signal'].sum()))
        return df
    except Exception:
        logger.exception("Error applying strategy")
        raise

