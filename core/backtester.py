"""
Backtesting utilities: fixed holding period backtest.
"""

from typing import Tuple, Dict

import pandas as pd

from utils.logger import logger


def backtest_strategy(df: pd.DataFrame, holding_days: int = 5,
                      initial_capital: float = 100000.0) -> Tuple[
    pd.DataFrame, Dict]:
    """
    Backtest a simple fixed-holding strategy after buy signals.

    Args:
        df (pd.DataFrame): Dataframe with 'Signal' and 'Close' and 'Date'
        holding_days (int): Days to hold after entry
        initial_capital (float): Starting capital

    Returns:
        Tuple[pd.DataFrame, dict]: trades dataframe and summary dict
    """
    df = df.copy()
    df.dropna(inplace=True)
    capital = float(initial_capital)
    trade_log = []

    for i in range(len(df)):
        if int(df.iloc[i].get('Signal', 0)) == 1:
            entry_price = float(df.iloc[i]['Close'])
            entry_date = df.iloc[i]['Date']
            exit_index = i + holding_days
            if exit_index >= len(df):
                logger.debug(
                    "Skipping trade: exit index out of range for entry at %s",
                    entry_date)
                continue
            exit_price = float(df.iloc[exit_index]['Close'])
            exit_date = df.iloc[exit_index]['Date']
            ret_pct = (exit_price - entry_price) / entry_price * 100.0
            capital = capital * (1 + ret_pct / 100.0)

            trade_log.append({
                'Entry Date': entry_date,
                'Exit Date': exit_date,
                'Entry Price': round(entry_price, 2),
                'Exit Price': round(exit_price, 2),
                'Return (%)': round(ret_pct, 2)
            })

    trades_df = pd.DataFrame(trade_log)
    if trades_df.empty:
        summary = {
            'Total Trades': 0,
            'Winning Trades': 0,
            'Win Ratio (%)': 0.0,
            'Final Capital': round(initial_capital, 2),
            'Total Return (%)': 0.0
        }
        logger.info("Backtest produced no trades")
        return trades_df, summary

    wins = int((trades_df['Return (%)'] > 0).sum())
    win_ratio = (wins / len(trades_df)) * 100.0
    total_return = ((capital - initial_capital) / initial_capital) * 100.0

    summary = {
        'Total Trades': len(trades_df),
        'Winning Trades': wins,
        'Win Ratio (%)': round(win_ratio, 2),
        'Final Capital': round(capital, 2),
        'Total Return (%)': round(total_return, 2)
    }
    logger.info("Backtest complete: %s", summary)
    return trades_df, summary
