"""Technical analysis: classic 10 indicators computed from OHLCV data.

Indicators: MA(5/10/20/60), MACD, KDJ, RSI(6/14), BOLL, OBV, ATR(14), WR(14), CCI(14), BIAS(6/12/24)
"""

import pandas as pd
import numpy as np


def compute_all(ohlcv: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all 10 indicators from OHLCV DataFrame.
    Expects columns: trade_date, open, high, low, close, volume
    Returns DataFrame with all indicator columns appended.
    """
    df = ohlcv.copy()
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float)

    # 1. MA — Moving Averages
    for period in [5, 10, 20, 60]:
        df[f"ma{period}"] = close.rolling(window=period).mean()

    # 2. MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd_dif"] = ema12 - ema26
    df["macd_dea"] = df["macd_dif"].ewm(span=9, adjust=False).mean()
    df["macd_bar"] = 2 * (df["macd_dif"] - df["macd_dea"])

    # 3. KDJ
    low_9 = low.rolling(window=9).min()
    high_9 = high.rolling(window=9).max()
    rsv = (close - low_9) / (high_9 - low_9 + 1e-9) * 100
    df["k"] = rsv.ewm(alpha=1/3, adjust=False).mean()
    df["d"] = df["k"].ewm(alpha=1/3, adjust=False).mean()
    df["j"] = 3 * df["k"] - 2 * df["d"]

    # 4. RSI
    for period in [6, 14]:
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df[f"rsi{period}"] = 100 - 100 / (1 + rs)

    # 5. BOLL
    df["boll_mid"] = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    df["boll_upper"] = df["boll_mid"] + 2 * std20
    df["boll_lower"] = df["boll_mid"] - 2 * std20

    # 6. OBV
    df["obv"] = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    # 7. ATR(14)
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()

    # 8. WR(14)
    hh_14 = high.rolling(window=14).max()
    ll_14 = low.rolling(window=14).min()
    df["wr14"] = (hh_14 - close) / (hh_14 - ll_14 + 1e-9) * -100

    # 9. CCI(14)
    tp = (high + low + close) / 3
    ma_tp = tp.rolling(window=14).mean()
    md_tp = tp.rolling(window=14).apply(lambda x: np.abs(x - x.mean()).mean())
    df["cci14"] = (tp - ma_tp) / (0.015 * md_tp + 1e-9)

    # 10. BIAS
    for period in [6, 12, 24]:
        ma = close.rolling(window=period).mean()
        df[f"bias{period}"] = (close - ma) / (ma + 1e-9) * 100

    return df
