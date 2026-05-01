"""Rules engine: evaluates user-defined rules against stock data."""

import json
import operator
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Rule:
    """A single trading rule."""
    name: str
    indicator: str          # e.g. "macd_dif", "rsi14", "ma5"
    op: str                 # ">", "<", ">=", "<=", "==", "cross_above", "cross_below"
    value: float
    weight: float = 1.0     # contribution to total score


@dataclass
class Strategy:
    """Collection of rules with weights."""
    name: str
    rules: list[Rule] = field(default_factory=list)
    # Signal generation thresholds
    buy_threshold: float = 70.0
    sell_threshold: float = 30.0


# Map string operators to functions
_OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
}


def evaluate_rule(rule: Rule, indicators: pd.DataFrame) -> pd.Series:
    """
    Evaluate a single rule against the indicator DataFrame.
    Returns a boolean Series (True where condition is met).
    """
    col = rule.indicator
    if col not in indicators.columns:
        return pd.Series(False, index=indicators.index)

    values = indicators[col]

    if rule.op in ("cross_above", "cross_below"):
        # Cross detection: today vs yesterday
        prev = values.shift(1)
        if rule.op == "cross_above":
            return (prev <= rule.value) & (values > rule.value)
        else:
            return (prev >= rule.value) & (values < rule.value)

    op_func = _OPS.get(rule.op)
    if op_func:
        return op_func(values, rule.value)

    return pd.Series(False, index=indicators.index)


def evaluate_strategy(strategy: Strategy, indicators: pd.DataFrame) -> pd.Series:
    """
    Evaluate all rules and compute a composite score (0-100).
    """
    total_weight = sum(r.weight for r in strategy.rules)
    if total_weight == 0:
        return pd.Series(50, index=indicators.index)

    score = pd.Series(0.0, index=indicators.index)
    for rule in strategy.rules:
        hits = evaluate_rule(rule, indicators)
        score += hits.astype(float) * rule.weight * (100 / total_weight)

    return score.clip(0, 100)


def generate_signal(strategy: Strategy, indicators: pd.DataFrame, latest_close: float) -> dict | None:
    """
    Generate a buy/sell signal based on strategy evaluation.
    Returns None if no signal triggered.
    """
    score = evaluate_strategy(strategy, indicators)
    latest_score = score.iloc[-1]

    if latest_score >= strategy.buy_threshold:
        return {
            "direction": "buy",
            "score": latest_score,
            "ref_price": latest_close,
            "reason": f"综合评分 {latest_score:.1f} >= 买入阈值 {strategy.buy_threshold}",
        }
    elif latest_score <= strategy.sell_threshold:
        return {
            "direction": "sell",
            "score": latest_score,
            "ref_price": latest_close,
            "reason": f"综合评分 {latest_score:.1f} <= 卖出阈值 {strategy.sell_threshold}",
        }

    return None


def parse_strategy_from_config(config_json: str) -> Strategy:
    """Parse a strategy from JSON config string."""
    data = json.loads(config_json)
    rules = [Rule(**r) for r in data.get("rules", [])]
    return Strategy(
        name=data.get("name", "Unnamed"),
        rules=rules,
        buy_threshold=data.get("buy_threshold", 70),
        sell_threshold=data.get("sell_threshold", 30),
    )
