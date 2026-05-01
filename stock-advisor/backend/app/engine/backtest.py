"""Backtest engine: runs strategy against historical data and computes metrics."""

import datetime
from dataclasses import dataclass, field

import pandas as pd
import numpy as np

from app.database import SessionLocal
from app.models import DailyKline, Indicator, BacktestResult, Strategy as StrategyModel
from app.engine.rules_engine import parse_strategy_from_config, evaluate_strategy


@dataclass
class BacktestMetrics:
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    equity_curve: list[float] = field(default_factory=list)


def run_backtest(strategy_id: int, start_date: str, end_date: str,
                 stock_codes: list[str] | None = None) -> BacktestMetrics:
    """
    Run a backtest for a strategy over a date range.
    
    Simple strategy: when score >= buy_threshold, buy at next day open.
    When score <= sell_threshold or hold_days >= max_hold, sell.
    """
    db = SessionLocal()

    # Load strategy
    strategy_row = db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
    if not strategy_row:
        db.close()
        raise ValueError(f"Strategy {strategy_id} not found")
    strategy = parse_strategy_from_config(strategy_row.config_json)

    # Load indicators for all stocks in range
    if stock_codes is None:
        # Get all stocks that have indicators
        stock_codes = [r[0] for r in db.query(Indicator.code).distinct().all()]

    equity_curve = [100_000]  # Start with 100k
    cash = 100_000
    holdings: dict[str, dict] = {}  # {code: {shares, cost}}
    trades = []

    for code in stock_codes:
        indicators_df = pd.read_sql(
            db.query(Indicator).filter(
                Indicator.code == code,
                Indicator.trade_date >= datetime.datetime.strptime(start_date, "%Y%m%d"),
                Indicator.trade_date <= datetime.datetime.strptime(end_date, "%Y%m%d"),
            ).order_by(Indicator.trade_date).statement,
            db.bind,
        )
        if indicators_df.empty:
            continue

        klines_df = pd.read_sql(
            db.query(DailyKline).filter(
                DailyKline.code == code,
                DailyKline.trade_date >= datetime.datetime.strptime(start_date, "%Y%m%d"),
                DailyKline.trade_date <= datetime.datetime.strptime(end_date, "%Y%m%d"),
            ).order_by(DailyKline.trade_date).statement,
            db.bind,
        )
        if klines_df.empty:
            continue

        # Evaluate strategy
        scores = evaluate_strategy(strategy, indicators_df)

        for i in range(1, len(scores)):
            score = scores.iloc[i]
            prev_score = scores.iloc[i - 1]
            close = klines_df.iloc[i]["close"]

            if code in holdings:
                # Check sell signal
                if score <= strategy.sell_threshold:
                    shares = holdings[code]["shares"]
                    cash += shares * close
                    trades.append({"code": code, "type": "sell", "price": close, "shares": shares, "date": klines_df.iloc[i]["trade_date"]})
                    del holdings[code]
            else:
                # Check buy signal
                if score >= strategy.buy_threshold and prev_score < strategy.buy_threshold:
                    # Buy with 20% of cash per position
                    allocation = cash * 0.2
                    shares = int(allocation / close)
                    if shares >= 100:  # A-share min 100 shares
                        cash -= shares * close
                        holdings[code] = {"shares": shares, "cost": close}
                        trades.append({"code": code, "type": "buy", "price": close, "shares": shares, "date": klines_df.iloc[i]["trade_date"]})

        # Close remaining positions at end of period
        for code, pos in list(holdings.items()):
            last_close = klines_df.iloc[-1]["close"]
            cash += pos["shares"] * last_close
            trades.append({"code": code, "type": "sell", "price": last_close, "shares": pos["shares"], "date": end_date})
            del holdings[code]

        equity_curve.append(cash)

    db.close()

    # Compute metrics
    total_return = (cash - 100_000) / 100_000 * 100
    days = (datetime.datetime.strptime(end_date, "%Y%m%d") - datetime.datetime.strptime(start_date, "%Y%m%d")).days
    annual_return = ((1 + total_return / 100) ** (365 / max(days, 1)) - 1) * 100

    # Drawdown
    peak = 100_000
    max_dd = 0
    for eq in equity_curve:
        peak = max(peak, eq)
        dd = (eq - peak) / peak * 100
        max_dd = min(max_dd, dd)

    # Sharpe (simplified, assuming 0 risk-free rate)
    returns = pd.Series(equity_curve).pct_change().dropna()
    sharpe = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(252)

    # Win rate
    wins = 0
    for i in range(0, len(trades) - 1, 2):
        if i + 1 < len(trades) and trades[i]["type"] == "buy" and trades[i + 1]["type"] == "sell":
            if trades[i + 1]["price"] > trades[i]["price"]:
                wins += 1
    win_rate = wins / max(len(trades) // 2, 1) * 100

    return BacktestMetrics(
        total_return=total_return,
        annual_return=annual_return,
        max_drawdown=max_dd,
        sharpe_ratio=sharpe,
        win_rate=win_rate,
        total_trades=len(trades),
        equity_curve=equity_curve,
    )
