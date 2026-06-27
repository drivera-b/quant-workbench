from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io import load_trade_rows
from .lifecycle import LifecycleConfig, simulate_lifecycle
from .metrics import bootstrap_ev_ci, summarize_by_regime, summarize_trades
from .reporting import write_report_html


def command_summarize_trades(args: argparse.Namespace) -> None:
    rows = load_trade_rows(args.trades)
    print(json.dumps(summarize_trades(rows), indent=2))


def command_bootstrap_ev(args: argparse.Namespace) -> None:
    rows = load_trade_rows(args.trades)
    result = bootstrap_ev_ci(
        rows,
        iterations=args.iterations,
        confidence=args.confidence,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2))


def command_summarize_regimes(args: argparse.Namespace) -> None:
    rows = load_trade_rows(args.trades)
    print(json.dumps(summarize_by_regime(rows), indent=2))


def command_simulate_lifecycle(args: argparse.Namespace) -> None:
    rows = load_trade_rows(args.trades)
    config = LifecycleConfig(
        challenge_target=args.challenge_target,
        challenge_loss_limit=args.challenge_loss_limit,
        funded_loss_limit=args.funded_loss_limit,
        payout_trigger=args.payout_trigger,
        activation_fee=args.activation_fee,
        evaluation_fee=args.evaluation_fee,
        payout_split=args.payout_split,
        combine_trade_limit=args.combine_trade_limit,
        funded_trade_limit=args.funded_trade_limit,
    )
    result = simulate_lifecycle(rows, config=config, iterations=args.iterations, seed=args.seed)
    print(json.dumps(result, indent=2))


def command_write_report(args: argparse.Namespace) -> None:
    rows = load_trade_rows(args.trades)
    summary = summarize_trades(rows)
    ev_ci = bootstrap_ev_ci(rows, iterations=args.iterations, confidence=args.confidence, seed=args.seed)
    config = LifecycleConfig(
        challenge_target=args.challenge_target,
        challenge_loss_limit=args.challenge_loss_limit,
        funded_loss_limit=args.funded_loss_limit,
        payout_trigger=args.payout_trigger,
        activation_fee=args.activation_fee,
        evaluation_fee=args.evaluation_fee,
        payout_split=args.payout_split,
        combine_trade_limit=args.combine_trade_limit,
        funded_trade_limit=args.funded_trade_limit,
    )
    lifecycle = simulate_lifecycle(rows, config=config, iterations=args.iterations, seed=args.seed)
    target = write_report_html(
        rows,
        summary,
        ev_ci,
        lifecycle,
        source_name=Path(args.trades).name,
        out_path=args.out,
    )
    print(json.dumps({"report": str(target)}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Public-safe quant research workbench tools")
    sub = parser.add_subparsers(dest="command", required=True)

    summarize = sub.add_parser("summarize-trades", help="Summarize an empirical trade CSV")
    summarize.add_argument("--trades", required=True)
    summarize.set_defaults(func=command_summarize_trades)

    summarize_regimes = sub.add_parser(
        "summarize-regimes",
        help="Summarize an empirical trade CSV by regime label",
    )
    summarize_regimes.add_argument("--trades", required=True)
    summarize_regimes.set_defaults(func=command_summarize_regimes)

    bootstrap = sub.add_parser("bootstrap-ev", help="Bootstrap expectancy confidence intervals")
    bootstrap.add_argument("--trades", required=True)
    bootstrap.add_argument("--iterations", type=int, default=2000)
    bootstrap.add_argument("--confidence", type=float, default=0.95)
    bootstrap.add_argument("--seed", type=int)
    bootstrap.set_defaults(func=command_bootstrap_ev)

    lifecycle = sub.add_parser("simulate-lifecycle", help="Run a simple lifecycle simulation from empirical trades")
    lifecycle.add_argument("--trades", required=True)
    lifecycle.add_argument("--iterations", type=int, default=2000)
    lifecycle.add_argument("--seed", type=int)
    lifecycle.add_argument("--challenge-target", type=float, default=3000.0)
    lifecycle.add_argument("--challenge-loss-limit", type=float, default=2000.0)
    lifecycle.add_argument("--funded-loss-limit", type=float, default=2000.0)
    lifecycle.add_argument("--payout-trigger", type=float, default=3000.0)
    lifecycle.add_argument("--activation-fee", type=float, default=149.0)
    lifecycle.add_argument("--evaluation-fee", type=float, default=49.0)
    lifecycle.add_argument("--payout-split", type=float, default=0.9)
    lifecycle.add_argument("--combine-trade-limit", type=int, default=80)
    lifecycle.add_argument("--funded-trade-limit", type=int, default=80)
    lifecycle.set_defaults(func=command_simulate_lifecycle)

    report = sub.add_parser("write-report", help="Write a static HTML report from an empirical trade CSV")
    report.add_argument("--trades", required=True)
    report.add_argument("--out", required=True)
    report.add_argument("--iterations", type=int, default=2000)
    report.add_argument("--confidence", type=float, default=0.95)
    report.add_argument("--seed", type=int)
    report.add_argument("--challenge-target", type=float, default=3000.0)
    report.add_argument("--challenge-loss-limit", type=float, default=2000.0)
    report.add_argument("--funded-loss-limit", type=float, default=2000.0)
    report.add_argument("--payout-trigger", type=float, default=3000.0)
    report.add_argument("--activation-fee", type=float, default=149.0)
    report.add_argument("--evaluation-fee", type=float, default=49.0)
    report.add_argument("--payout-split", type=float, default=0.9)
    report.add_argument("--combine-trade-limit", type=int, default=80)
    report.add_argument("--funded-trade-limit", type=int, default=80)
    report.set_defaults(func=command_write_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
