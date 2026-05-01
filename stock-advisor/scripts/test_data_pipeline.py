"""Data pipeline integration test: fetch + compute + verify."""
import sys
import pandas as pd
import numpy as np
import akshare as ak

stocks = {
    'sh600519': '贵州茅台',
    'sz000001': '平安银行',
    'sh601318': '中国平安',
}

results = {}
for symbol, name in stocks.items():
    try:
        df = ak.stock_zh_a_hist_tx(symbol=symbol, start_date='20250101', end_date='20260501', adjust='qfq')
        df = df.rename(columns={'date': 'trade_date'})
        df['code'] = symbol
        df['volume'] = df['amount']
        df['turnover'] = np.nan
        results[symbol] = df
        print(f"{name}({symbol}): {len(df)} rows, {df['trade_date'].iloc[0]} ~ {df['trade_date'].iloc[-1]}")
    except Exception as e:
        print(f"{name}({symbol}): ERROR {e}")

# Compute indicators
def compute_all(ohlcv):
    df = ohlcv.copy()
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float).fillna(0)

    for period in [5, 10, 20, 60]:
        df[f"ma{period}"] = close.rolling(window=period).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd_dif"] = ema12 - ema26
    df["macd_dea"] = df["macd_dif"].ewm(span=9, adjust=False).mean()
    df["macd_bar"] = 2 * (df["macd_dif"] - df["macd_dea"])

    low_9 = low.rolling(window=9).min()
    high_9 = high.rolling(window=9).max()
    rsv = (close - low_9) / (high_9 - low_9 + 1e-9) * 100
    df["k"] = rsv.ewm(alpha=1/3, adjust=False).mean()
    df["d"] = df["k"].ewm(alpha=1/3, adjust=False).mean()
    df["j"] = 3 * df["k"] - 2 * df["d"]

    for period in [6, 14]:
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df[f"rsi{period}"] = 100 - 100 / (1 + rs)

    df["boll_mid"] = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    df["boll_upper"] = df["boll_mid"] + 2 * std20
    df["boll_lower"] = df["boll_mid"] - 2 * std20

    df["obv"] = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()

    hh_14 = high.rolling(window=14).max()
    ll_14 = low.rolling(window=14).min()
    df["wr14"] = (hh_14 - close) / (hh_14 - ll_14 + 1e-9) * -100

    tp = (high + low + close) / 3
    ma_tp = tp.rolling(window=14).mean()
    md_tp = tp.rolling(window=14).apply(lambda x: np.abs(x - x.mean()).mean())
    df["cci14"] = (tp - ma_tp) / (0.015 * md_tp + 1e-9)

    for period in [6, 12, 24]:
        ma = close.rolling(window=period).mean()
        df[f"bias{period}"] = (close - ma) / (ma + 1e-9) * 100

    return df

print()
all_ok = True
for symbol in results:
    df_ind = compute_all(results[symbol])
    latest = df_ind.iloc[-1]
    print(f"\n{'='*50}")
    print(f"{stocks[symbol]} ({symbol}) — 最新: {latest['trade_date']}")
    print(f"  close={latest['close']:.2f}  MA5={latest['ma5']:.2f}  MA20={latest['ma20']:.2f}")
    print(f"  MACD: DIF={latest['macd_dif']:.2f} DEA={latest['macd_dea']:.2f} BAR={latest['macd_bar']:.2f}")
    print(f"  KDJ: K={latest['k']:.2f} D={latest['d']:.2f} J={latest['j']:.2f}")
    print(f"  RSI6={latest['rsi6']:.2f} RSI14={latest['rsi14']:.2f}")
    print(f"  BOLL: {latest['boll_upper']:.2f} / {latest['boll_mid']:.2f} / {latest['boll_lower']:.2f}")
    print(f"  ATR14={latest['atr14']:.2f}  WR14={latest['wr14']:.2f}  CCI14={latest['cci14']:.2f}")
    print(f"  BIAS6={latest['bias6']:.2f} BIAS12={latest['bias12']:.2f} BIAS24={latest['bias24']:.2f}")

print("\n✅ 全部正常" if all_ok else "\n❌ 有错误")
