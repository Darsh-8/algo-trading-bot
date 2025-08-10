"""
ML utilities: prepare features, train a Decision Tree, save/load model.
Only model accuracy is eligible for Telegram alerts per PDF policy.
"""

import os
from typing import Tuple

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from utils.logger import logger


def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df


def prepare_features(df: pd.DataFrame) -> Tuple[
    pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Prepare X, y for training. Raises if required cols missing.
    """
    df = compute_macd(df.copy())
    req_cols = ['RSI', 'SMA_20', 'SMA_50', 'MACD', 'MACD_Signal', 'Volume']
    if not all(c in df.columns for c in req_cols):
        raise ValueError(f"Missing required columns: {req_cols}")
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df.dropna(inplace=True)
    X = df[req_cols]
    y = df['Target']
    return X, y, df


def train_model(df: pd.DataFrame, model_path: str) -> Tuple[object, float]:
    """
    Train and persist a DecisionTreeClassifier. Returns (model, accuracy_percent).
    """
    X, y, _ = prepare_features(df)
    if len(X) < 10:
        raise ValueError("Insufficient data for training.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        shuffle=False)
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test)) * 100.0
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("Saved model to %s with accuracy %.2f%%", model_path, acc)
    return model, round(acc, 2)


def load_model(model_path: str):
    return joblib.load(model_path)


def predict_signals(df: pd.DataFrame, model_path: str) -> pd.DataFrame:
    model = load_model(model_path)
    X, _, data = prepare_features(df)
    data['ML_Pred'] = model.predict(X)
    return data
