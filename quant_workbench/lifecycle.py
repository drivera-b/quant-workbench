from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from typing import Any

from .io import TradeRow


@dataclass(frozen=True)
class LifecycleConfig:
    challenge_target: float = 3000.0
    challenge_loss_limit: float = 2000.0
    funded_loss_limit: float = 2000.0
    payout_trigger: float = 3000.0
    activation_fee: float = 149.0
    evaluation_fee: float = 49.0
    payout_split: float = 0.9
    combine_trade_limit: int = 80
    funded_trade_limit: int = 80


def _resample_trade(rows: list[TradeRow], rng: random.Random) -> float:
    return rows[rng.randrange(len(rows))].pnl


def simulate_lifecycle(
    rows: list[TradeRow],
    config: LifecycleConfig | None = None,
    iterations: int = 2000,
    seed: int | None = None,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("lifecycle simulation requires at least one trade row")
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    cfg = config or LifecycleConfig()
    rng = random.Random(seed)

    passes = 0
    payouts = 0
    positive_nets = 0
    net_results: list[float] = []

    for _ in range(iterations):
        net = -cfg.evaluation_fee
        challenge_pnl = 0.0
        passed = False

        for _ in range(cfg.combine_trade_limit):
            challenge_pnl += _resample_trade(rows, rng)
            if challenge_pnl >= cfg.challenge_target:
                passed = True
                passes += 1
                break
            if challenge_pnl <= -cfg.challenge_loss_limit:
                break

        if passed:
            net -= cfg.activation_fee
            funded_pnl = 0.0
            for _ in range(cfg.funded_trade_limit):
                funded_pnl += _resample_trade(rows, rng)
                if funded_pnl >= cfg.payout_trigger:
                    payout = funded_pnl * cfg.payout_split
                    net += payout
                    payouts += 1
                    break
                if funded_pnl <= -cfg.funded_loss_limit:
                    break

        net_results.append(net)
        if net > 0:
            positive_nets += 1

    net_results.sort()
    mid = len(net_results) // 2
    median = net_results[mid] if len(net_results) % 2 == 1 else (net_results[mid - 1] + net_results[mid]) / 2.0
    return {
        "config": asdict(cfg),
        "iterations": iterations,
        "pass_rate": passes / iterations,
        "payout_rate": payouts / iterations,
        "prob_positive_net": positive_nets / iterations,
        "net_ev": sum(net_results) / iterations,
        "median_net": median,
        "p05_net": net_results[max(0, int(0.05 * iterations) - 1)],
        "p95_net": net_results[min(iterations - 1, int(0.95 * iterations))],
    }
