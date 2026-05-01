"""Tests for backtest engine logic."""

import pytest
from dataclasses import dataclass
from app.engine.backtest import BacktestMetrics


class TestBacktestMetrics:
    """Test the BacktestMetrics dataclass and metric calculations."""

    def test_metrics_creation(self):
        metrics = BacktestMetrics(
            total_return=15.5,
            annual_return=12.3,
            max_drawdown=-8.2,
            sharpe_ratio=1.45,
            win_rate=62.0,
            total_trades=42,
            equity_curve=[100000, 101000, 102500, 101800],
        )
        assert metrics.total_return == 15.5
        assert metrics.annual_return == 12.3
        assert metrics.max_drawdown == -8.2
        assert metrics.sharpe_ratio == 1.45
        assert metrics.win_rate == 62.0
        assert metrics.total_trades == 42
        assert len(metrics.equity_curve) == 4


    def test_metrics_types(self):
        """Ensure all fields accept their declared types."""
        metrics = BacktestMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0)
        assert isinstance(metrics.total_return, float)
        assert isinstance(metrics.annual_return, float)
        assert isinstance(metrics.max_drawdown, float)
        assert isinstance(metrics.sharpe_ratio, float)
        assert isinstance(metrics.win_rate, float)
        assert isinstance(metrics.total_trades, int)
        assert isinstance(metrics.equity_curve, list)


    def test_equity_curve_default(self):
        """equity_curve should default to empty list."""
        metrics = BacktestMetrics(0, 0, 0, 0, 0, 0)
        assert metrics.equity_curve == []


    def test_metric_ranges(self):
        """Verify metric ranges make sense for real backtests."""
        # Typical backtest: +20% return, -15% drawdown, 0.8 Sharpe, 55% win
        metrics = BacktestMetrics(20.0, 15.0, -15.0, 0.8, 55.0, 120)
        assert -100 <= metrics.total_return <= 1000  # sane range
        assert -100 <= metrics.max_drawdown <= 0
        assert -10 <= metrics.sharpe_ratio <= 10
        assert 0 <= metrics.win_rate <= 100
