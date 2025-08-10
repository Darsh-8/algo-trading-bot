"""
Central orchestrator:
Runs ingestion, strategy, backtest, ML training, logging, sheet updates, and alerts.
Telegram rules:
 - Send alerts only for executed trades and allowed ML accuracy (per PDF).
 - ML predictions are logged and saved, only shown in trade alerts.
 - Avoid duplicate messages within the same run.
"""
import os
from pathlib import Path

import pandas as pd
from core.ml_model import train_model, predict_signals

from config import settings
from core.backtester import backtest_strategy
from core.strategy import apply_strategy
from reporting.report_generator import save_trade_report
from services.sheet_logger import append_to_single_sheet
from services.telegram_service import send_telegram_message, format_trade_alert
from utils.data_loader import fetch_and_save_stock_data
from utils.logger import logger


def run_pipeline(tickers=None):
    tickers = tickers or settings.DEFAULT_TICKERS
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    for ticker in tickers:
        try:
            file_path = fetch_and_save_stock_data(ticker)
            symbol = Path(file_path).stem.upper()

            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True).dt.strftime(
                '%d-%m-%Y')

            df = apply_strategy(df)
            df.to_csv(os.path.join(settings.DATA_DIR, f"{symbol}_signals.csv"),
                      index=False)

            trades, summary = backtest_strategy(df)
            logger.info("Summary for %s: %s", symbol, summary)

            df_with_preds = pd.DataFrame()
            try:
                model_path = os.path.join(settings.MODELS_DIR,
                                          f"{symbol}_model.pkl")
                _, acc = train_model(df, model_path)

                model_acc_df = pd.DataFrame([{
                    "Ticker": symbol,
                    "Type": "ModelAccuracy",
                    "Model Accuracy (%)": acc
                }])
                append_to_single_sheet(model_acc_df, sheet_tab=symbol)

                df_with_preds = predict_signals(df, model_path)
                pred_csv = os.path.join(settings.DATA_DIR,
                                        f"{symbol}_ml_predictions.csv")
                df_with_preds.to_csv(pred_csv, index=False)
                logger.info("ML predictions for %s saved to %s", symbol,
                            pred_csv)

            except Exception as ml_exc:
                logger.exception("ML step failed for %s", symbol)

            summary_df = pd.DataFrame(
                [{"Ticker": symbol, "Type": "Summary", **summary}])
            append_to_single_sheet(summary_df, sheet_tab=symbol)

            if not trades.empty:
                trades["Ticker"] = symbol
                trades["Type"] = "Trade"
                append_to_single_sheet(trades, sheet_tab=symbol)
                save_trade_report(trades, symbol)

                for _, row in trades.iterrows():
                    trade_type = "BUY" if row['Return (%)'] >= 0 else "SELL"

                    # Attach ML prediction for entry date if available
                    ml_pred = None
                    try:
                        if not df_with_preds.empty:
                            pred_val = df_with_preds.loc[
                                df_with_preds['Date'] == row[
                                    'Entry Date'], 'ML_Pred'
                            ].iloc[0]
                            ml_pred = 'BUY' if pred_val == 1 else 'SELL'
                    except Exception:
                        pass

                    msg = format_trade_alert(
                        ticker=symbol,
                        trade_type=trade_type,
                        entry_date=row['Entry Date'],
                        exit_date=row['Exit Date'],
                        entry_price=row['Entry Price'],
                        exit_price=row['Exit Price'],
                        qty=None,  # Add real quantity if available
                        ml_pred=ml_pred
                    )
                    send_telegram_message(msg)

        except Exception:
            logger.exception("Pipeline error for %s", ticker)
            continue


if __name__ == "__main__":
    run_pipeline()
