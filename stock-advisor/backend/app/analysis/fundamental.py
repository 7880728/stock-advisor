"""Fundamental analysis: PE, PB, ROE, growth rates, scoring."""

import pandas as pd


def score_fundamental(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score stocks based on fundamental data.
    
    Criteria:
    - PE: lower is better, but > 0 (profitable)
    - PB: lower is better (value), but adjust by industry
    - ROE: higher is better
    - Revenue growth: higher is better
    - Profit growth: higher is better
    
    Returns DataFrame with 'fund_score' column (0-100).
    """
    df = df.copy()
    scores = pd.DataFrame(index=df.index)
    scores["score"] = 50.0  # neutral baseline

    # PE score: rank within profitable stocks, lower is better
    profitable = df["pe"] > 0
    if profitable.any():
        scores.loc[profitable, "score"] += _rank_score(-df.loc[profitable, "pe"]) * 0.25

    # PB score: lower is better
    if (df["pb"] > 0).any():
        scores["score"] += _rank_score(-df["pb"]) * 0.15

    # ROE score: higher is better
    scores["score"] += _rank_score(df["roe"]) * 0.30

    # Revenue growth: higher is better
    scores["score"] += _rank_score(df["revenue_yoy"]) * 0.15

    # Profit growth: higher is better
    scores["score"] += _rank_score(df["profit_yoy"]) * 0.15

    scores["score"] = scores["score"].clip(0, 100)
    df["fund_score"] = scores["score"]
    return df


def _rank_score(series: pd.Series) -> pd.Series:
    """Convert a series to 0-100 percentile rank."""
    return series.rank(pct=True, na_option="bottom") * 100
