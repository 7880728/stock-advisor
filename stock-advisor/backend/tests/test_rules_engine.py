"""Tests for rules engine."""

import pandas as pd
import numpy as np
import pytest

from app.engine.rules_engine import (
    Rule, Strategy, evaluate_rule, evaluate_strategy,
    generate_signal, parse_strategy_from_config,
)


@pytest.fixture
def simple_df():
    """DataFrame with 20 rows of simulated indicators."""
    dates = pd.date_range("2025-01-02", periods=20, freq="B")
    np.random.seed(42)
    close = pd.Series(100 + np.cumsum(np.random.randn(20) * 2))
    return pd.DataFrame({
        "trade_date": dates,
        "close": close,
        "ma5": close.rolling(5).mean(),  # first 4 rows will be NaN
        "ma20": close.rolling(20, min_periods=1).mean(),
        "rsi14": np.clip(50 + np.cumsum(np.random.randn(20) * 3), 0, 100),
        "macd_dif": np.cumsum(np.random.randn(20) * 0.1),
        "macd_dea": np.cumsum(np.random.randn(20) * 0.05),
    })


# ===== evaluate_rule =====

def test_evaluate_rule_gt(simple_df):
    rule = Rule(name="test", indicator="close", op=">", value=100)
    result = evaluate_rule(rule, simple_df)
    assert result.dtype == bool
    assert result.iloc[-1] == (simple_df["close"].iloc[-1] > 100)


def test_evaluate_rule_lt(simple_df):
    rule = Rule(name="test", indicator="close", op="<", value=200)
    result = evaluate_rule(rule, simple_df)
    assert result.all()  # all close < 200 (small random walk)


def test_evaluate_rule_ge(simple_df):
    rule = Rule(name="test", indicator="close", op=">=", value=simple_df["close"].min())
    result = evaluate_rule(rule, simple_df)
    assert result.all()


def test_evaluate_rule_le(simple_df):
    rule = Rule(name="test", indicator="close", op="<=", value=simple_df["close"].max())
    result = evaluate_rule(rule, simple_df)
    assert result.all()


def test_evaluate_rule_eq(simple_df):
    df = simple_df.copy()
    df["close"] = 50.0
    rule = Rule(name="test", indicator="close", op="==", value=50)
    result = evaluate_rule(rule, df)
    assert result.all()


def test_evaluate_rule_missing_indicator(simple_df):
    rule = Rule(name="test", indicator="nonexistent", op=">", value=10)
    result = evaluate_rule(rule, simple_df)
    assert not result.any()  # all False


def test_cross_above(simple_df):
    df = simple_df.copy()
    df["indicator"] = [1, 2, 3, 9, 11, 13, 15] + [10] * 13  # crosses above 10 at index 4
    rule = Rule(name="cross", indicator="indicator", op="cross_above", value=10)
    result = evaluate_rule(rule, df)
    assert result.iloc[4]  # 9→11 crosses 10
    assert not result.iloc[3]  # 3→9, both below


def test_cross_below(simple_df):
    df = simple_df.copy()
    df["indicator"] = [20, 18, 15, 12, 9, 7, 5] + [8] * 13  # crosses below 10 at index 4
    rule = Rule(name="cross", indicator="indicator", op="cross_below", value=10)
    result = evaluate_rule(rule, df)
    assert result.iloc[4]  # 12→9 crosses below 10
    assert not result.iloc[3]  # 15→12, both above


# ===== evaluate_strategy =====

def test_evaluate_strategy_empty_rules(simple_df):
    strategy = Strategy(name="empty", rules=[])
    score = evaluate_strategy(strategy, simple_df)
    assert (score == 50).all()  # default neutral


def test_evaluate_strategy_single_rule_always_true(simple_df):
    rule = Rule(name="always", indicator="close", op=">", value=0, weight=2)
    strategy = Strategy(name="single", rules=[rule])
    score = evaluate_strategy(strategy, simple_df)
    assert (score == 100).all()


def test_evaluate_strategy_weighted(simple_df):
    df = simple_df.copy()
    df["a"] = 10.0   # always >= 5 → True
    df["b"] = 1.0    # always >= 5 → False

    r1 = Rule(name="a_hit", indicator="a", op=">=", value=5, weight=3)
    r2 = Rule(name="b_miss", indicator="b", op=">=", value=5, weight=1)
    strategy = Strategy(name="weighted", rules=[r1, r2])

    score = evaluate_strategy(strategy, df)
    # Total weight 4, r1 contributes 3*100/4=75, r2 0
    assert (score == 75).all()


def test_evaluate_strategy_mixed(simple_df):
    """Half rules hit, half miss."""
    df = simple_df.copy()
    df["hit"] = 100.0
    df["miss"] = 0.0

    r_hit = Rule(name="h", indicator="hit", op=">", value=50, weight=1)
    r_miss = Rule(name="m", indicator="miss", op=">", value=50, weight=1)
    strategy = Strategy(name="mixed", rules=[r_hit, r_miss])

    score = evaluate_strategy(strategy, df)
    # 1*100/2 + 0*100/2 = 50
    assert (score == 50).all()


# ===== generate_signal =====

def test_generate_buy_signal(simple_df):
    df = simple_df.copy()
    df["indicator"] = 100.0  # always hits buy rule
    rule = Rule(name="buy_me", indicator="indicator", op=">", value=50, weight=3)
    strategy = Strategy(name="bull", rules=[rule], buy_threshold=70)

    signal = generate_signal(strategy, df, latest_close=105.0)
    assert signal is not None
    assert signal["direction"] == "buy"
    assert signal["score"] == 100
    assert signal["ref_price"] == 105.0


def test_generate_sell_signal(simple_df):
    df = simple_df.copy()
    df["indicator"] = 0.0  # always misses
    rule = Rule(name="sell_me", indicator="indicator", op=">", value=50, weight=3)
    strategy = Strategy(name="bear", rules=[rule], sell_threshold=30)

    signal = generate_signal(strategy, df, latest_close=95.0)
    assert signal is not None
    assert signal["direction"] == "sell"
    assert signal["score"] == 0


def test_generate_no_signal(simple_df):
    df = simple_df.copy()
    df["indicator"] = 100.0
    rule = Rule(name="hit", indicator="indicator", op=">", value=50, weight=1)
    strategy = Strategy(name="neutral", rules=[rule], buy_threshold=101, sell_threshold=-1)

    signal = generate_signal(strategy, df, latest_close=100.0)
    assert signal is None  # score 100, but buy_threshold is 101


# ===== parse_strategy_from_config =====

def test_parse_strategy_from_config():
    config = """{
        "name": "test_strat",
        "buy_threshold": 80,
        "sell_threshold": 20,
        "rules": [
            {"name": "r1", "indicator": "rsi14", "op": "<", "value": 30, "weight": 2},
            {"name": "r2", "indicator": "macd_dif", "op": ">", "value": 0, "weight": 1}
        ]
    }"""
    strategy = parse_strategy_from_config(config)
    assert strategy.name == "test_strat"
    assert strategy.buy_threshold == 80
    assert strategy.sell_threshold == 20
    assert len(strategy.rules) == 2
    assert strategy.rules[0].indicator == "rsi14"
    assert strategy.rules[0].op == "<"
    assert strategy.rules[0].value == 30
    assert strategy.rules[0].weight == 2


def test_parse_strategy_default_thresholds():
    config = '{"name": "defaults", "rules": []}'
    strategy = parse_strategy_from_config(config)
    assert strategy.buy_threshold == 70
    assert strategy.sell_threshold == 30
