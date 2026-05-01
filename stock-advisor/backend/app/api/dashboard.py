"""Dashboard API: overview stats, top signals, portfolio summary."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Stock, Signal, DailyKline, PaperOrder

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard overview statistics."""
    total_stocks = db.query(func.count(Stock.code)).scalar()

    # Recent signals
    recent_signals = (
        db.query(Signal)
        .order_by(Signal.created_at.desc())
        .limit(20)
        .all()
    )

    # Paper account summary
    orders = db.query(PaperOrder).order_by(PaperOrder.created_at).all()
    cash = 100_000
    holdings = {}
    for o in orders:
        if o.direction == "buy":
            cash -= o.amount
            holdings[o.code] = holdings.get(o.code, 0) + o.volume
        else:
            cash += o.amount
            holdings[o.code] = holdings.get(o.code, 0) - o.volume

    total_value = cash  # + current market value (simplified)
    pnl = total_value - 100_000

    return {
        "total_stocks": total_stocks,
        "recent_signals": [
            {
                "code": s.code,
                "type": s.signal_type,
                "direction": s.direction,
                "score": s.score,
                "reason": s.reason,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent_signals
        ],
        "paper_account": {
            "cash": cash,
            "total_value": total_value,
            "pnl": pnl,
            "pnl_pct": pnl / 100_000 * 100,
            "positions": len(holdings),
        },
    }
