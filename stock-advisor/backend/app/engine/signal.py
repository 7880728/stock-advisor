"""Signal generator: produces signals from analysis results."""

import datetime
from dataclasses import dataclass


@dataclass
class SignalResult:
    code: str
    signal_type: str        # ranking / entry_exit / anomaly
    direction: str | None   # buy / sell
    score: float | None
    reason: str
    ref_price: float | None
    stop_loss: float | None
    take_profit: float | None


def generate_ranking_signals(scores: list[tuple[str, str, float]], top_n: int = 10) -> list[SignalResult]:
    """
    Generate ranking signals from scored stocks.
    scores: list of (code, name, score) sorted desc by score.
    """
    results = []
    for i, (code, name, score) in enumerate(scores[:top_n]):
        results.append(SignalResult(
            code=code,
            signal_type="ranking",
            direction=None,
            score=score,
            reason=f"综合评分排名 #{i+1}: {name} ({score:.1f}分)",
            ref_price=None,
            stop_loss=None,
            take_profit=None,
        ))
    return results


def generate_anomaly_alert(code: str, alert_type: str, detail: str, ref_price: float | None = None) -> SignalResult:
    """Generate an anomaly alert signal."""
    return SignalResult(
        code=code,
        signal_type="anomaly",
        direction=None,
        score=None,
        reason=f"[{alert_type}] {detail}",
        ref_price=ref_price,
        stop_loss=None,
        take_profit=None,
    )
