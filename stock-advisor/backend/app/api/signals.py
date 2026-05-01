"""Signals API: list and query signals."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Signal

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("/")
def list_signals(
    signal_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List recent signals, optionally filtered by type."""
    q = db.query(Signal).order_by(Signal.created_at.desc())
    if signal_type:
        q = q.filter(Signal.signal_type == signal_type)
    rows = q.limit(limit).all()
    return [
        {
            "id": r.id,
            "code": r.code,
            "signal_type": r.signal_type,
            "direction": r.direction,
            "score": r.score,
            "reason": r.reason,
            "ref_price": r.ref_price,
            "stop_loss": r.stop_loss,
            "take_profit": r.take_profit,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
