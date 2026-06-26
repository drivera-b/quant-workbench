from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TradeRow:
    pnl: float
    regime: str | None = None


def load_trade_rows(path: str | Path) -> list[TradeRow]:
    source = Path(path)
    rows: list[TradeRow] = []
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if "pnl" not in (reader.fieldnames or []):
            raise ValueError("trade CSV must include a 'pnl' column")
        for record in reader:
            pnl_raw = (record.get("pnl") or "").strip()
            if not pnl_raw:
                continue
            regime_raw = (record.get("regime") or "").strip()
            rows.append(TradeRow(pnl=float(pnl_raw), regime=regime_raw or None))
    if not rows:
        raise ValueError(f"no trade rows found in {source}")
    return rows
