from __future__ import annotations

import math
import random
from typing import Any

from .io import TradeRow


def _max_drawdown(pnls: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return max_dd


def summarize_trades(rows: list[TradeRow]) -> dict[str, Any]:
    pnls = [row.pnl for row in rows]
    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    trades = len(pnls)
    win_rate = len(wins) / trades if trades else 0.0
    expectancy = sum(pnls) / trades if trades else 0.0
    avg_win = gross_profit / len(wins) if wins else 0.0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else math.inf if gross_profit > 0 else 0.0
    return {
        "trades": trades,
        "win_rate": win_rate,
        "expectancy": expectancy,
        "total_pnl": sum(pnls),
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "max_drawdown": _max_drawdown(pnls),
    }


def summarize_by_regime(rows: list[TradeRow]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[TradeRow]] = {}
    for row in rows:
        label = row.regime or "unlabeled"
        grouped.setdefault(label, []).append(row)
    return {label: summarize_trades(group_rows) for label, group_rows in sorted(grouped.items())}


def bootstrap_ev_ci(
    rows: list[TradeRow],
    iterations: int = 2000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> dict[str, float | bool]:
    if not rows:
        raise ValueError("bootstrap requires at least one trade row")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    rng = random.Random(seed)
    pnls = [row.pnl for row in rows]
    sample_size = len(pnls)
    samples: list[float] = []
    for _ in range(iterations):
        draw = [pnls[rng.randrange(sample_size)] for _ in range(sample_size)]
        samples.append(sum(draw) / sample_size)
    samples.sort()
    alpha = (1.0 - confidence) / 2.0
    lo_index = max(0, min(iterations - 1, int(alpha * iterations)))
    hi_index = max(0, min(iterations - 1, int((1.0 - alpha) * iterations) - 1))
    ev = sum(pnls) / sample_size
    lower = samples[lo_index]
    upper = samples[hi_index]
    return {
        "ev": ev,
        "lower": lower,
        "upper": upper,
        "confidence": confidence,
        "zero_cross": lower <= 0 <= upper,
        "lower_bound_positive": lower > 0,
    }
