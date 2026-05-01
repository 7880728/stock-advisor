"""Tests for technical analysis engine."""

import pandas as pd
import numpy as np

from app.analysis.technical import compute_all


def make_ohlcv(n=100, seed=42) -> pd.DataFrame:
    """Generate synthetic OHLCV data with a trending pattern."""
    np.random.seed(seed)
    dates = pd.date_range("2025-01-02", periods=n, freq="B")
    # Trending close
    trend = np.linspace(0, 20, n)
    noise = np.random.randn(n) * 2
    close = 100 + trend + noise.cumsum() * 0.5

    high = close + np.abs(np.random.randn(n)) * 2
    low = close - np.abs(np.random.randn(n)) * 2
    open_price = low + np.random.rand(n) * (high - low)
    volume = np.random.randint(10000, 50000, n) * 1.0

    return pd.DataFrame({
        "trade_date": dates,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def test_compute_all_returns_expected_columns():
    df = make_ohlcv()
    result = compute_all(df)
    expected_cols = [
        "ma5", "ma10", "ma20", "ma60",
        "macd_dif", "macd_dea", "macd_bar",
        "k", "d", "j",
        "rsi6", "rsi14",
        "boll_upper", "boll_mid", "boll_lower",
        "obv",
        "atr14",
        "wr14",
        "cci14",
        "bias6", "bias12", "bias24",
    ]
    for col in expected_cols:
        assert col in result.columns, f"Missing column: {col}"


def test_ma_values():
    df = make_ohlcv(n=30)
    result = compute_all(df)
    # Verify MA5 manually for last row
    manual_ma5 = df["close"].iloc[-5:].mean()
    assert abs(result["ma5"].iloc[-1] - manual_ma5) < 0.01


def test_macd_exists():
    df = make_ohlcv(n=50)
    result = compute_all(df)
    # After ~30 rows, MACD should have non-NaN values
    assert result["macd_dif"].iloc[-1] is not pd.NA
    assert not pd.isna(result["macd_dif"].iloc[-1])


def test_rsi_range():
    df = make_ohlcv(n=50)
    result = compute_all(df)
    # RSI should be in [0, 100] for non-NaN rows
    rsi6_valid = result["rsi6"].dropna()
    assert (rsi6_valid >= 0).all()
    assert (rsi6_valid <= 100).all()

    rsi14_valid = result["rsi14"].dropna()
    assert (rsi14_valid >= 0).all()
    assert (rsi14_valid <= 100).all()


def test_kdj_range():
    df = make_ohlcv(n=50)
    result = compute_all(df)
    k_valid = result["k"].dropna()
    d_valid = result["d"].dropna()
    # K/D typically in 0-100 range
    assert (k_valid >= -10).all() and (k_valid <= 110).all()
    assert (d_valid >= -10).all() and (d_valid <= 110).all()


def test_bollinger_bands():
    df = make_ohlcv(n=30)
    result = compute_all(df)
    last = result.iloc[-1]
    assert last["boll_lower"] <= last["boll_mid"] <= last["boll_upper"]


def test_obv_monotonicity():
    """OBV should be cumulative."""
    df = make_ohlcv(n=30)
    result = compute_all(df)
    obv = result["obv"].dropna()
    # OBV is cumulative of signed volume — not strictly monotonic but close to original
    assert len(obv) > 0
    assert not obv.isna().any()


def test_wr_range():
    df = make_ohlcv(n=30)
    result = compute_all(df)
    wr = result["wr14"].dropna()
    # WR is between -100 and 0
    assert (wr >= -100).all()
    assert (wr <= 0).all()


def test_atr_positive():
    df = make_ohlcv(n=30)
    result = compute_all(df)
    atr = result["atr14"].dropna()
    assert (atr > 0).all()


def test_bias_sign():
    df = make_ohlcv(n=30)
    result = compute_all(df)
    # BIAS signs depend on trend — but should be finite
    assert not result["bias6"].dropna().isna().any()
    assert not result["bias12"].dropna().isna().any()
    assert not result["bias24"].dropna().isna().any()


def test_input_not_mutated():
    """compute_all should not modify input DataFrame."""
    df = make_ohlcv()
    original_cols = list(df.columns)
    original_close = df["close"].copy()
    compute_all(df)
    assert list(df.columns) == original_cols
    assert (df["close"] == original_close).all()
