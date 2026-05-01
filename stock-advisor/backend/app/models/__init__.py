"""SQLAlchemy ORM models for the stock advisor system."""

import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, Index
from sqlalchemy.orm import Mapped

from app.database import Base


class Stock(Base):
    """A-share stock basic info."""
    __tablename__ = "stocks"

    code: Mapped[str] = Column(String(10), primary_key=True, comment="股票代码, e.g. sh600519")
    name: Mapped[str] = Column(String(20), nullable=False)
    market: Mapped[str] = Column(String(2), nullable=False, comment="sh / sz / bj")
    industry: Mapped[str] = Column(String(50), default="")
    is_st: Mapped[bool] = Column(Integer, default=False)
    is_suspended: Mapped[bool] = Column(Integer, default=False)
    listed_date: Mapped[datetime.date | None] = Column(DateTime, nullable=True)
    updated_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)


class DailyKline(Base):
    """Daily K-line (OHLCV) data."""
    __tablename__ = "daily_klines"
    __table_args__ = (
        Index("idx_kl_code_date", "code", "trade_date"),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    trade_date: Mapped[datetime.date] = Column(DateTime, nullable=False)
    open: Mapped[float] = Column(Float, nullable=False)
    high: Mapped[float] = Column(Float, nullable=False)
    low: Mapped[float] = Column(Float, nullable=False)
    close: Mapped[float] = Column(Float, nullable=False)
    volume: Mapped[float] = Column(Float, nullable=False)
    amount: Mapped[float] = Column(Float, nullable=False)
    turnover: Mapped[float | None] = Column(Float, nullable=True)  # 换手率


class Indicator(Base):
    """Computed technical indicators for each stock per day."""
    __tablename__ = "indicators"
    __table_args__ = (
        Index("idx_ind_code_date", "code", "trade_date"),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    trade_date: Mapped[datetime.date] = Column(DateTime, nullable=False)
    # MA
    ma5: Mapped[float | None] = Column(Float, nullable=True)
    ma10: Mapped[float | None] = Column(Float, nullable=True)
    ma20: Mapped[float | None] = Column(Float, nullable=True)
    ma60: Mapped[float | None] = Column(Float, nullable=True)
    # MACD
    macd_dif: Mapped[float | None] = Column(Float, nullable=True)
    macd_dea: Mapped[float | None] = Column(Float, nullable=True)
    macd_bar: Mapped[float | None] = Column(Float, nullable=True)
    # KDJ
    k: Mapped[float | None] = Column(Float, nullable=True)
    d: Mapped[float | None] = Column(Float, nullable=True)
    j: Mapped[float | None] = Column(Float, nullable=True)
    # RSI
    rsi6: Mapped[float | None] = Column(Float, nullable=True)
    rsi14: Mapped[float | None] = Column(Float, nullable=True)
    # BOLL
    boll_upper: Mapped[float | None] = Column(Float, nullable=True)
    boll_mid: Mapped[float | None] = Column(Float, nullable=True)
    boll_lower: Mapped[float | None] = Column(Float, nullable=True)
    # OBV
    obv: Mapped[float | None] = Column(Float, nullable=True)
    # ATR
    atr14: Mapped[float | None] = Column(Float, nullable=True)
    # WR
    wr14: Mapped[float | None] = Column(Float, nullable=True)
    # CCI
    cci14: Mapped[float | None] = Column(Float, nullable=True)
    # BIAS
    bias6: Mapped[float | None] = Column(Float, nullable=True)
    bias12: Mapped[float | None] = Column(Float, nullable=True)
    bias24: Mapped[float | None] = Column(Float, nullable=True)


class Financial(Base):
    """Fundamental financial data per stock per quarter."""
    __tablename__ = "financials"
    __table_args__ = (
        Index("idx_fin_code_date", "code", "report_date"),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    report_date: Mapped[datetime.date] = Column(DateTime, nullable=False)
    pe: Mapped[float | None] = Column(Float, nullable=True)
    pb: Mapped[float | None] = Column(Float, nullable=True)
    roe: Mapped[float | None] = Column(Float, nullable=True)
    revenue_yoy: Mapped[float | None] = Column(Float, nullable=True)  # 营收同比增速%
    profit_yoy: Mapped[float | None] = Column(Float, nullable=True)   # 利润同比增速%
    total_market_cap: Mapped[float | None] = Column(Float, nullable=True)  # 总市值


class News(Base):
    """News / announcements related to a stock."""
    __tablename__ = "news"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    title: Mapped[str] = Column(String(300), nullable=False)
    content: Mapped[str | None] = Column(Text, nullable=True)
    source: Mapped[str] = Column(String(50), default="")
    pub_date: Mapped[datetime.datetime] = Column(DateTime, nullable=False)
    sentiment: Mapped[float | None] = Column(Float, nullable=True)  # -1 负, 0 中, 1 正
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)


class Signal(Base):
    """Generated trading signals."""
    __tablename__ = "signals"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    signal_type: Mapped[str] = Column(String(20), nullable=False)  # ranking / entry_exit / anomaly
    direction: Mapped[str | None] = Column(String(10), nullable=True)  # buy / sell
    score: Mapped[float | None] = Column(Float, nullable=True)          # 综合评分
    reason: Mapped[str] = Column(Text, default="")
    ref_price: Mapped[float | None] = Column(Float, nullable=True)
    stop_loss: Mapped[float | None] = Column(Float, nullable=True)
    take_profit: Mapped[float | None] = Column(Float, nullable=True)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)


class Strategy(Base):
    """User-defined strategy — a collection of rules with weights."""
    __tablename__ = "strategies"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    config_json: Mapped[str] = Column(Text, nullable=False)  # JSON string of rules + weights
    is_active: Mapped[bool] = Column(Integer, default=False)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)


class PaperOrder(Base):
    """Virtual trading order in the paper account."""
    __tablename__ = "paper_orders"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String(10), nullable=False)
    direction: Mapped[str] = Column(String(4), nullable=False)  # buy / sell
    price: Mapped[float] = Column(Float, nullable=False)
    volume: Mapped[int] = Column(Integer, nullable=False)  # shares (股)
    amount: Mapped[float] = Column(Float, nullable=False)
    signal_id: Mapped[int | None] = Column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)


class BacktestResult(Base):
    """Backtest run results."""
    __tablename__ = "backtest_results"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = Column(Integer, nullable=False)
    start_date: Mapped[datetime.date] = Column(DateTime, nullable=False)
    end_date: Mapped[datetime.date] = Column(DateTime, nullable=False)
    total_return: Mapped[float] = Column(Float, nullable=False)
    annual_return: Mapped[float | None] = Column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = Column(Float, nullable=True)
    sharpe_ratio: Mapped[float | None] = Column(Float, nullable=True)
    win_rate: Mapped[float | None] = Column(Float, nullable=True)
    total_trades: Mapped[int | None] = Column(Integer, nullable=True)
    result_json: Mapped[str | None] = Column(Text, nullable=True)  # full result data
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.utcnow)
