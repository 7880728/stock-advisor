"""Stock detail API: K-line data, indicators, signals for a single stock."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DailyKline, Indicator, Signal, Financial, News, Stock

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("/{code}")
def stock_detail(code: str, db: Session = Depends(get_db)):
    """Get stock basic info."""
    stock = db.get(Stock, code)
    if not stock:
        return {"error": "Stock not found"}
    return {
        "code": stock.code,
        "name": stock.name,
        "market": stock.market,
        "industry": stock.industry,
    }


@router.get("/{code}/kline")
def stock_kline(
    code: str,
    limit: int = Query(default=250, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get recent K-line data for a stock."""
    rows = (
        db.query(DailyKline)
        .filter(DailyKline.code == code)
        .order_by(DailyKline.trade_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "date": r.trade_date.isoformat() if hasattr(r.trade_date, "isoformat") else str(r.trade_date),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
            "turnover": r.turnover,
        }
        for r in reversed(rows)
    ]


@router.get("/{code}/indicators")
def stock_indicators(
    code: str,
    limit: int = Query(default=250, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get technical indicators for a stock."""
    rows = (
        db.query(Indicator)
        .filter(Indicator.code == code)
        .order_by(Indicator.trade_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "date": r.trade_date.isoformat() if hasattr(r.trade_date, "isoformat") else str(r.trade_date),
            "ma5": r.ma5, "ma10": r.ma10, "ma20": r.ma20, "ma60": r.ma60,
            "macd_dif": r.macd_dif, "macd_dea": r.macd_dea, "macd_bar": r.macd_bar,
            "k": r.k, "d": r.d, "j": r.j,
            "rsi6": r.rsi6, "rsi14": r.rsi14,
            "boll_upper": r.boll_upper, "boll_mid": r.boll_mid, "boll_lower": r.boll_lower,
            "obv": r.obv, "atr14": r.atr14, "wr14": r.wr14, "cci14": r.cci14,
            "bias6": r.bias6, "bias12": r.bias12, "bias24": r.bias24,
        }
        for r in reversed(rows)
    ]


@router.get("/{code}/signals")
def stock_signals(code: str, limit: int = Query(default=50), db: Session = Depends(get_db)):
    """Get historical signals for a stock."""
    rows = (
        db.query(Signal)
        .filter(Signal.code == code)
        .order_by(Signal.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "type": r.signal_type,
            "direction": r.direction,
            "score": r.score,
            "reason": r.reason,
            "ref_price": r.ref_price,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/{code}/financials")
def stock_financials(code: str, db: Session = Depends(get_db)):
    """Get fundamental financial data."""
    rows = (
        db.query(Financial)
        .filter(Financial.code == code)
        .order_by(Financial.report_date.desc())
        .limit(12)
        .all()
    )
    return [
        {
            "report_date": r.report_date.isoformat() if hasattr(r.report_date, "isoformat") else str(r.report_date),
            "pe": r.pe, "pb": r.pb, "roe": r.roe,
            "revenue_yoy": r.revenue_yoy, "profit_yoy": r.profit_yoy,
            "total_market_cap": r.total_market_cap,
        }
        for r in rows
    ]
