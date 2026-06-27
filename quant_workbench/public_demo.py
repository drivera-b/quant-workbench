from __future__ import annotations

import csv
import html
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


def _format_usd(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def _svg_shell(*, title: str, subtitle: str, width: int, height: int, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title>{html.escape(title)}</title>
  <desc>{html.escape(subtitle)}</desc>
  <style>
    .bg {{ fill: #fbfcfb; stroke: #d4ddd7; stroke-width: 1; }}
    .title {{ fill: #171c19; font: 700 24px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .subtitle {{ fill: #58625c; font: 400 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .label {{ fill: #58625c; font: 600 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .small {{ fill: #58625c; font: 400 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .value {{ fill: #171c19; font: 700 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .axis {{ stroke: #d4ddd7; stroke-width: 1; }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" />
  <text class="title" x="28" y="38">{html.escape(title)}</text>
  <text class="subtitle" x="28" y="60">{html.escape(subtitle)}</text>
{body}
</svg>
"""


def _render_window_checks_svg(rows: list[dict[str, Any]]) -> str:
    width = 920
    height = 330
    chart_left = 64
    chart_top = 96
    chart_height = 170
    baseline_y = chart_top + chart_height
    bar_width = 108
    gap = 48
    max_value = max(float(row["expectancy"]) for row in rows) or 1.0

    parts = [f'  <line class="axis" x1="{chart_left}" y1="{baseline_y}" x2="{width - 40}" y2="{baseline_y}" />']
    for index, row in enumerate(rows):
        expectancy = float(row["expectancy"])
        height_px = max(18.0, (expectancy / max_value) * chart_height)
        x = chart_left + 32 + index * (bar_width + gap)
        y = baseline_y - height_px
        color = "#0f766e" if row["benchmark_status"] == "on_track" else "#a16207"
        label = f'{int(row["recent_sessions"])} sessions'
        parts.extend(
            [
                f'  <rect x="{x}" y="{y:.2f}" width="{bar_width}" height="{height_px:.2f}" rx="8" fill="{color}" fill-opacity="0.82" />',
                f'  <text class="value" x="{x + bar_width / 2:.1f}" y="{y - 10:.1f}" text-anchor="middle">{html.escape(_format_usd(expectancy))}</text>',
                f'  <text class="label" x="{x + bar_width / 2:.1f}" y="{baseline_y + 22}" text-anchor="middle">{html.escape(label)}</text>',
                f'  <text class="small" x="{x + bar_width / 2:.1f}" y="{baseline_y + 40}" text-anchor="middle">{html.escape(str(row["benchmark_status"]).replace("_", " "))}</text>',
            ]
        )
    return _svg_shell(
        title="Recent Window Checks",
        subtitle="Expectancy per trade across 20-90 session slices versus the frozen benchmark.",
        width=width,
        height=height,
        body="\n".join(parts),
    )


def _render_stress_scenarios_svg(rows: list[dict[str, Any]]) -> str:
    width = 920
    height = 330
    chart_left = 64
    chart_top = 96
    chart_height = 170
    baseline_y = chart_top + chart_height
    bar_width = 138
    gap = 42
    max_value = max(float(row["net_ev"]) for row in rows) or 1.0
    color_map = {
        "base": "#0f766e",
        "plus_1usd": "#3b7f77",
        "plus_2usd": "#8f6c1e",
        "fill_haircut_5pct": "#b91c1c",
    }

    parts = [f'  <line class="axis" x1="{chart_left}" y1="{baseline_y}" x2="{width - 40}" y2="{baseline_y}" />']
    for index, row in enumerate(rows):
        value = float(row["net_ev"])
        height_px = max(18.0, (value / max_value) * chart_height)
        x = chart_left + 20 + index * (bar_width + gap)
        y = baseline_y - height_px
        label = str(row["scenario"]).replace("_", " ")
        payout_label = f"payout {float(row['funded_payout_rate']) * 100:.1f}%"
        parts.extend(
            [
                f'  <rect x="{x}" y="{y:.2f}" width="{bar_width}" height="{height_px:.2f}" rx="8" fill="{color_map.get(str(row["scenario"]), "#0f766e")}" fill-opacity="0.86" />',
                f'  <text class="value" x="{x + bar_width / 2:.1f}" y="{y - 10:.1f}" text-anchor="middle">{html.escape(_format_usd(value))}</text>',
                f'  <text class="label" x="{x + bar_width / 2:.1f}" y="{baseline_y + 22}" text-anchor="middle">{html.escape(label)}</text>',
                f'  <text class="small" x="{x + bar_width / 2:.1f}" y="{baseline_y + 40}" text-anchor="middle">{html.escape(payout_label)}</text>',
            ]
        )
    return _svg_shell(
        title="Execution Stress Ladder",
        subtitle="Topstep-style lifecycle EV under added cost and fill-degradation assumptions.",
        width=width,
        height=height,
        body="\n".join(parts),
    )


def _render_firm_comparison_svg(rows: list[dict[str, Any]]) -> str:
    width = 980
    height = 360
    zero_x = 300
    chart_right = width - 56
    top = 92
    row_gap = 44
    max_abs = max(abs(float(row["net_ev"])) for row in rows) or 1.0
    scale = (chart_right - zero_x - 24) / max_abs

    parts = [
        f'  <line class="axis" x1="{zero_x}" y1="{top - 18}" x2="{zero_x}" y2="{height - 34}" />',
        f'  <text class="small" x="{zero_x}" y="{top - 26}" text-anchor="middle">0</text>',
    ]
    for index, row in enumerate(rows):
        value = float(row["net_ev"])
        y = top + index * row_gap
        label = f'{row["prop_firm"]} {row["program"]}'
        color = "#0f766e"
        if value < 0:
            color = "#b91c1c"
        elif index >= 2:
            color = "#8f6c1e"

        bar_width = abs(value) * scale
        x = zero_x if value >= 0 else zero_x - bar_width
        text_anchor = "start" if value >= 0 else "end"
        text_x = (x + bar_width + 10) if value >= 0 else (x - 10)
        parts.extend(
            [
                f'  <text class="label" x="28" y="{y + 6}" text-anchor="start">{html.escape(label)}</text>',
                f'  <rect x="{x:.2f}" y="{y - 11}" width="{bar_width:.2f}" height="22" rx="7" fill="{color}" fill-opacity="0.86" />',
                f'  <text class="value" x="{text_x:.2f}" y="{y + 5}" text-anchor="{text_anchor}">{html.escape(_format_usd(value))}</text>',
            ]
        )
    return _svg_shell(
        title="Cross-Firm Lifecycle Comparison",
        subtitle="Same trade stream, different account wrappers and payout geometry.",
        width=width,
        height=height,
        body="\n".join(parts),
    )


def _write_readme_assets(root: Path, reference_payloads: dict[str, Any]) -> dict[str, str]:
    asset_dir = root / "assets" / "readme"
    asset_dir.mkdir(parents=True, exist_ok=True)

    assets = {
        "window_checks_svg": asset_dir / "window_checks.svg",
        "stress_scenarios_svg": asset_dir / "stress_scenarios.svg",
        "firm_comparison_svg": asset_dir / "firm_comparison.svg",
    }
    assets["window_checks_svg"].write_text(
        _render_window_checks_svg(reference_payloads["window_checks"]),
        encoding="utf-8",
    )
    assets["stress_scenarios_svg"].write_text(
        _render_stress_scenarios_svg(reference_payloads["stress_scenarios"]),
        encoding="utf-8",
    )
    assets["firm_comparison_svg"].write_text(
        _render_firm_comparison_svg(reference_payloads["firm_comparison"]),
        encoding="utf-8",
    )
    return {name: _relative_path(root, path) for name, path in assets.items()}


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
    readme_assets = _write_readme_assets(root, reference_payloads)

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
        "readme_assets": readme_assets,
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
            "label": "README window chart",
            "path": readme_assets["window_checks_svg"],
            "kind": "svg",
            "group": "generated",
            "description": "Rendered README chart for recent-window validation checks.",
        },
        {
            "label": "README stress chart",
            "path": readme_assets["stress_scenarios_svg"],
            "kind": "svg",
            "group": "generated",
            "description": "Rendered README chart for the execution stress ladder.",
        },
        {
            "label": "README firm chart",
            "path": readme_assets["firm_comparison_svg"],
            "kind": "svg",
            "group": "generated",
            "description": "Rendered README chart for cross-firm lifecycle comparison.",
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
