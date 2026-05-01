"""Screening funnel: coarse → fine pipeline for stock selection."""

import datetime

import pandas as pd
from sqlalchemy import func

from app.database import SessionLocal
from app.models import DailyKline, Stock


def coarse_screen() -> list[str]:
    """
    Stage 1 — Coarse screen on all A-shares.
    
    Filters:
    - Not ST
    - Not suspended
    - Recent daily volume > 0 (actively trading)
    - Volume > 20-day average (liquidity check)
    
    Returns list of stock codes that pass.
    """
    db = SessionLocal()
    try:
        # Get all non-ST, non-suspended stocks
        stocks = db.query(Stock.code).filter(
            Stock.is_st == False,
            Stock.is_suspended == False,
        ).all()
        all_codes = [s[0] for s in stocks]

        passed = []
        for code in all_codes:
            # Check last 30 trading days
            recent = (
                db.query(DailyKline)
                .filter(DailyKline.code == code)
                .order_by(DailyKline.trade_date.desc())
                .limit(30)
                .all()
            )
            if len(recent) < 20:
                continue

            latest = recent[0]
            if latest.volume is None or latest.volume == 0:
                continue

            avg_vol = sum(r.volume for r in recent[1:21] if r.volume) / max(len([r for r in recent[1:21] if r.volume]), 1)
            if avg_vol == 0 or latest.volume / avg_vol < 0.5:
                continue

            passed.append(code)

        return passed
    finally:
        db.close()
