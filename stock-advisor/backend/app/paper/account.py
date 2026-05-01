"""Paper trading account management."""

import datetime

import pandas as pd
from sqlalchemy import func

from app.database import SessionLocal
from app.models import PaperOrder


class PaperAccount:
    """Virtual trading account for strategy validation."""

    def __init__(self, initial_cash: float = 100_000):
        self.initial_cash = initial_cash
        self.cash = initial_cash

    def buy(self, code: str, price: float, volume: int, signal_id: int | None = None) -> PaperOrder | None:
        """Execute a buy order if sufficient cash."""
        amount = price * volume
        if amount > self.cash:
            return None

        self.cash -= amount
        return self._record(code, "buy", price, volume, amount, signal_id)

    def sell(self, code: str, price: float, volume: int, signal_id: int | None = None) -> PaperOrder | None:
        """Execute a sell order."""
        # Check holdings (simplified — full version would track positions)
        amount = price * volume
        self.cash += amount
        return self._record(code, "sell", price, volume, amount, signal_id)

    def _record(self, code: str, direction: str, price: float, volume: int, amount: float, signal_id: int | None) -> PaperOrder:
        db = SessionLocal()
        order = PaperOrder(
            code=code,
            direction=direction,
            price=price,
            volume=volume,
            amount=amount,
            signal_id=signal_id,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        db.close()
        return order

    def current_positions(self) -> dict:
        """Get current holdings: {code: (total_volume, avg_cost)}."""
        db = SessionLocal()
        orders = db.query(PaperOrder).order_by(PaperOrder.created_at).all()
        db.close()

        holdings: dict[str, dict] = {}
        for o in orders:
            if o.code not in holdings:
                holdings[o.code] = {"volume": 0, "cost": 0.0}
            if o.direction == "buy":
                total_cost = holdings[o.code]["cost"] * holdings[o.code]["volume"] + o.amount
                holdings[o.code]["volume"] += o.volume
                if holdings[o.code]["volume"] > 0:
                    holdings[o.code]["cost"] = total_cost / holdings[o.code]["volume"]
            else:
                holdings[o.code]["volume"] -= o.volume

        return {k: v for k, v in holdings.items() if v["volume"] > 0}
