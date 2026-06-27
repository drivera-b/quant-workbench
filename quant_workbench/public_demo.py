from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .io import load_trade_rows
from .lifecycle import LifecycleConfig, simulate_lifecycle
from .metrics import bootstrap_ev_ci, summarize_by_regime, summarize_trades
from .reporting import write_report_html


REFERENCE_JSON_FILES = {
    "benchmark_summary": "benchmark_summary.json",
    "methodology": "methodology.json",
    "dataset_metadata": "sample_dataset_metadata.json",
}

REFERENCE_CSV_FILES = {
    "window_checks": "window_checks.csv",
    "monthly_stability": "monthly_stability.csv",
    "policy_ablations": "policy_ablations.csv",
    "stress_scenarios": "stress_scenarios.csv",
    "firm_comparison": "firm_comparison.csv",
    "firm_comparison_plus2usd": "firm_comparison_plus2usd.csv",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _coerce_csv_value(value: str) -> Any:
    if value == "":
        return None
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: _coerce_csv_value(value) for key, value in row.items()} for row in reader]


def _relative_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _profile_trade_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_rows = len(rows)

    def summarize_field(field: str) -> list[dict[str, Any]]:
        counts: Counter[str] = Counter()
        for row in rows:
            value = row.get(field)
            if value in (None, ""):
                continue
            counts[str(value)] += 1
        return [
            {"label": label, "count": count, "share": count / total_rows}
            for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    sessions = {str(row["session_id"]) for row in rows if row.get("session_id") not in (None, "")}
    return {
        "rows": total_rows,
        "sessions": len(sessions),
        "event_families": summarize_field("event_family"),
        "regimes": summarize_field("regime"),
        "outcomes": summarize_field("outcome"),
        "score_buckets": summarize_field("score_bucket"),
        "bars_held": summarize_field("bars_held"),
    }


def build_public_demo(
    repo_root: str | Path,
    *,
    trades_path: str | Path | None = None,
    iterations: int = 2000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    reference_dir = root / "results" / "reference"
    generated_dir = root / "results" / "generated"
    docs_data_dir = root / "docs" / "data"
    example_dir = root / "examples"

    generated_dir.mkdir(parents=True, exist_ok=True)
    docs_data_dir.mkdir(parents=True, exist_ok=True)
    example_dir.mkdir(parents=True, exist_ok=True)

    source_trades = Path(trades_path).resolve() if trades_path is not None else example_dir / "anonymized_oos_trades.csv"
    if not source_trades.exists():
        raise FileNotFoundError(f"public demo trade CSV not found: {source_trades}")

    raw_rows = _read_csv_rows(source_trades)
    rows = load_trade_rows(source_trades)
    summary = summarize_trades(rows)
    regime_summary = summarize_by_regime(rows)
    ev_ci = bootstrap_ev_ci(rows, iterations=iterations, confidence=confidence, seed=seed)
    lifecycle = simulate_lifecycle(rows, config=LifecycleConfig(), iterations=iterations, seed=seed)
    data_profile = _profile_trade_rows(raw_rows)

    report_path = example_dir / "anonymized_oos_report.html"
    write_report_html(
        rows,
        summary,
        ev_ci,
        lifecycle,
        source_name=source_trades.name,
        out_path=report_path,
    )

    generated_payloads = {
        "package_summary": summary,
        "package_regimes": regime_summary,
        "package_bootstrap_ev": ev_ci,
        "package_lifecycle": lifecycle,
    }
    for name, payload in generated_payloads.items():
        _write_json(generated_dir / f"{name}.json", payload)

    reference_payloads: dict[str, Any] = {}
    for key, filename in REFERENCE_JSON_FILES.items():
        reference_payloads[key] = _read_json(reference_dir / filename)
    for key, filename in REFERENCE_CSV_FILES.items():
        reference_payloads[key] = _read_csv_rows(reference_dir / filename)

    manifest = {
        "trades": _relative_path(root, source_trades),
        "report": _relative_path(root, report_path),
        "docs_data": "docs/data/site_data.json",
        "generated": {
            key: f"results/generated/{key}.json" for key in generated_payloads
        },
        "reference": {
            key: f"results/reference/{filename}" for key, filename in {**REFERENCE_JSON_FILES, **REFERENCE_CSV_FILES}.items()
        },
    }
    _write_json(generated_dir / "artifact_manifest.json", manifest)

    artifact_links = [
        {
            "label": "Anonymized trade export",
            "path": _relative_path(root, source_trades),
            "kind": "csv",
            "group": "example",
            "description": "Public example trade stream with session ids, broad family labels, regimes, and pnl.",
        },
        {
            "label": "Generated HTML report",
            "path": _relative_path(root, report_path),
            "kind": "html",
            "group": "generated",
            "description": "Self-contained report generated from the anonymized trade export.",
        },
        {
            "label": "Frozen benchmark summary",
            "path": "results/reference/benchmark_summary.json",
            "kind": "json",
            "group": "reference",
            "description": "Broad out-of-sample anchor exported from the private ranked-event research run.",
        },
        {
            "label": "Recent window checks",
            "path": "results/reference/window_checks.csv",
            "kind": "csv",
            "group": "reference",
            "description": "20/30/45/60/90-session comparisons against the frozen benchmark.",
        },
        {
            "label": "Policy ablations",
            "path": "results/reference/policy_ablations.csv",
            "kind": "csv",
            "group": "reference",
            "description": "90-session policy comparison showing which branch kept a positive EV lower bound.",
        },
        {
            "label": "Execution stress ladder",
            "path": "results/reference/stress_scenarios.csv",
            "kind": "csv",
            "group": "reference",
            "description": "Topstep lifecycle outcomes under added cost and fill haircut assumptions.",
        },
        {
            "label": "Cross-firm comparison",
            "path": "results/reference/firm_comparison.csv",
            "kind": "csv",
            "group": "reference",
            "description": "Same trade stream, different account wrappers and payout geometry.",
        },
        {
            "label": "Generated package summary",
            "path": "results/generated/package_summary.json",
            "kind": "json",
            "group": "generated",
            "description": "Trade-level summary computed from the checked-in anonymized trade stream.",
        },
        {
            "label": "Generated lifecycle simulation",
            "path": "results/generated/package_lifecycle.json",
            "kind": "json",
            "group": "generated",
            "description": "Monte Carlo lifecycle output from the public workbench defaults.",
        },
        {
            "label": "Docs site data",
            "path": "docs/data/site_data.json",
            "kind": "json",
            "group": "generated",
            "description": "Single JSON payload used by the static docs surface.",
        },
        {
            "label": "Artifact manifest",
            "path": "results/generated/artifact_manifest.json",
            "kind": "json",
            "group": "generated",
            "description": "Machine-readable map of reference, generated, and example artifacts.",
        },
    ]

    command_examples = [
        "python3 -m pip install -e .",
        f"python3 -m quant_workbench.cli build-public-demo --repo-root . --iterations {iterations} --seed {seed or 7}",
        f"python3 -m quant_workbench.cli summarize-trades --trades {_relative_path(root, source_trades)}",
        f"python3 -m quant_workbench.cli summarize-regimes --trades {_relative_path(root, source_trades)}",
        f"python3 -m quant_workbench.cli bootstrap-ev --trades {_relative_path(root, source_trades)} --iterations {iterations} --seed {seed or 7}",
        f"python3 -m quant_workbench.cli simulate-lifecycle --trades {_relative_path(root, source_trades)} --iterations {iterations} --seed {seed or 7}",
        f"python3 -m quant_workbench.cli write-report --trades {_relative_path(root, source_trades)} --out {_relative_path(root, report_path)} --iterations {iterations} --seed {seed or 7}",
    ]

    site_data = {
        "reference": reference_payloads,
        "package": {
            "summary": summary,
            "regimes": regime_summary,
            "bootstrap_ev": ev_ci,
            "lifecycle": lifecycle,
            "data_profile": data_profile,
            "source_csv": _relative_path(root, source_trades),
            "report_path": _relative_path(root, report_path),
            "commands": command_examples,
        },
        "artifacts": artifact_links,
        "manifest": manifest,
    }
    _write_json(docs_data_dir / "site_data.json", site_data)
    return manifest
