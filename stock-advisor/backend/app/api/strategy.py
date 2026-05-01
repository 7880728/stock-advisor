"""Strategy configuration API."""

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Strategy as StrategyModel
from app.engine.backtest import run_backtest

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


class StrategyCreate(BaseModel):
    name: str
    rules: list[dict]
    buy_threshold: float = 70
    sell_threshold: float = 30


class StrategyUpdate(BaseModel):
    name: str | None = None
    rules: list[dict] | None = None
    buy_threshold: float | None = None
    sell_threshold: float | None = None
    is_active: bool | None = None


@router.get("/")
def list_strategies(db: Session = Depends(get_db)):
    """List all strategies."""
    rows = db.query(StrategyModel).order_by(StrategyModel.updated_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "config": json.loads(r.config_json),
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/")
def create_strategy(data: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new strategy."""
    config = {
        "name": data.name,
        "rules": data.rules,
        "buy_threshold": data.buy_threshold,
        "sell_threshold": data.sell_threshold,
    }
    strat = StrategyModel(name=data.name, config_json=json.dumps(config), is_active=False)
    db.add(strat)
    db.commit()
    db.refresh(strat)
    return {"id": strat.id, "name": strat.name}


@router.put("/{strategy_id}")
def update_strategy(strategy_id: int, data: StrategyUpdate, db: Session = Depends(get_db)):
    """Update an existing strategy."""
    strat = db.get(StrategyModel, strategy_id)
    if not strat:
        return {"error": "Strategy not found"}

    current = json.loads(strat.config_json)
    if data.name:
        strat.name = data.name
        current["name"] = data.name
    if data.rules is not None:
        current["rules"] = data.rules
    if data.buy_threshold is not None:
        current["buy_threshold"] = data.buy_threshold
    if data.sell_threshold is not None:
        current["sell_threshold"] = data.sell_threshold
    if data.is_active is not None:
        # Deactivate other strategies
        if data.is_active:
            db.query(StrategyModel).filter(StrategyModel.id != strategy_id).update({"is_active": False})
        strat.is_active = data.is_active

    strat.config_json = json.dumps(current)
    db.commit()
    return {"id": strat.id, "name": strat.name, "updated": True}


@router.post("/{strategy_id}/backtest")
def backtest_strategy(
    strategy_id: int,
    start_date: str = "20230101",
    end_date: str = "20250101",
    db: Session = Depends(get_db),
):
    """Run backtest for a strategy."""
    try:
        metrics = run_backtest(strategy_id, start_date, end_date)
        return {
            "total_return": round(metrics.total_return, 2),
            "annual_return": round(metrics.annual_return, 2),
            "max_drawdown": round(metrics.max_drawdown, 2),
            "sharpe_ratio": round(metrics.sharpe_ratio, 2),
            "win_rate": round(metrics.win_rate, 2),
            "total_trades": metrics.total_trades,
        }
    except Exception as e:
        return {"error": str(e)}
