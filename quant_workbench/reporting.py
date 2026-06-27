from __future__ import annotations

from html import escape
from pathlib import Path

from .io import TradeRow
from .metrics import summarize_by_regime


def _fmt_money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _spark_bars(rows: list[TradeRow]) -> str:
    pnls = [row.pnl for row in rows]
    if not pnls:
        return ""
    max_abs = max(abs(value) for value in pnls) or 1.0
    bars: list[str] = []
    for value in pnls[:60]:
        height = max(12.0, abs(value) / max_abs * 88.0)
        tone = "positive" if value >= 0 else "negative"
        bars.append(f'<span class="spark-bar {tone}" style="height:{height:.1f}px"></span>')
    return "".join(bars)


def _regime_table(rows: list[TradeRow]) -> str:
    if not any(row.regime for row in rows):
        return ""
    summaries = summarize_by_regime(rows)
    body = "".join(
        (
            "<tr>"
            f"<td>{escape(label)}</td>"
            f"<td>{int(stats['trades'])}</td>"
            f"<td>{_fmt_pct(float(stats['win_rate']))}</td>"
            f"<td>{_fmt_money(float(stats['expectancy']))}</td>"
            f"<td>{_fmt_money(float(stats['max_drawdown']))}</td>"
            "</tr>"
        )
        for label, stats in summaries.items()
    )
    return f"""
      <section class="section">
        <article class="card">
          <h2>Regime breakdown</h2>
          <table class="regime-table">
            <thead>
              <tr>
                <th>Regime</th>
                <th>Trades</th>
                <th>Win rate</th>
                <th>Expectancy</th>
                <th>Max drawdown</th>
              </tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </article>
      </section>
    """


def build_report_html(
    rows: list[TradeRow],
    summary: dict[str, float],
    ev_ci: dict[str, float | bool],
    lifecycle: dict[str, float | int | dict[str, float | int]],
    *,
    source_name: str,
) -> str:
    spark = _spark_bars(rows)
    regime_table = _regime_table(rows)
    zero_cross = "yes" if bool(ev_ci["zero_cross"]) else "no"
    lower_positive = "yes" if bool(ev_ci["lower_bound_positive"]) else "no"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Quant Workbench Report</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #eef2f0;
        --surface: #fbfcfb;
        --ink: #171c19;
        --muted: #58625c;
        --line: #d4ddd7;
        --teal: #0f766e;
        --teal-soft: #d7f1ee;
        --rust: #c2410c;
        --rust-soft: #fde7dc;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #edf1ee 0%, #f7faf8 38%, #eef2f0 100%);
        color: var(--ink);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .wrap {{
        width: min(1120px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 28px 0 42px;
      }}
      .hero, .card {{
        background: rgba(251, 252, 251, 0.95);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 18px 38px rgba(34, 42, 36, 0.08);
      }}
      .hero {{
        padding: 24px;
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 20px;
      }}
      .eyebrow {{
        margin: 0 0 10px;
        color: var(--teal);
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
      }}
      h1, h2, h3, p {{ margin-top: 0; }}
      h1 {{
        font-size: clamp(2rem, 4vw, 3.6rem);
        line-height: 0.96;
        margin-bottom: 14px;
      }}
      h2 {{
        font-size: 1.5rem;
        margin-bottom: 10px;
      }}
      p {{
        color: var(--muted);
        line-height: 1.55;
      }}
      .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin-top: 18px;
      }}
      .metric {{
        padding: 18px;
      }}
      .label {{
        color: var(--muted);
        font-size: 0.88rem;
      }}
      .value {{
        margin-top: 10px;
        font-size: 1.9rem;
        font-weight: 700;
      }}
      .section {{
        margin-top: 18px;
      }}
      .grid-two {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }}
      .card {{
        padding: 20px;
      }}
      .stat-list {{
        display: grid;
        gap: 10px;
      }}
      .stat-row {{
        display: flex;
        justify-content: space-between;
        gap: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--line);
      }}
      .stat-row:last-child {{
        border-bottom: 0;
        padding-bottom: 0;
      }}
      .spark {{
        display: grid;
        grid-template-columns: repeat(20, minmax(0, 1fr));
        gap: 6px;
        align-items: end;
        min-height: 112px;
      }}
      .spark-bar {{
        min-height: 12px;
        border-radius: 6px 6px 0 0;
      }}
      .spark-bar.positive {{
        background: linear-gradient(180deg, rgba(15,118,110,0.9), rgba(15,118,110,0.35));
      }}
      .spark-bar.negative {{
        background: linear-gradient(180deg, rgba(194,65,12,0.9), rgba(194,65,12,0.35));
      }}
      .regime-table {{
        width: 100%;
        border-collapse: collapse;
      }}
      .regime-table th,
      .regime-table td {{
        text-align: left;
        padding: 12px 10px;
        border-bottom: 1px solid var(--line);
      }}
      .regime-table th {{
        color: var(--muted);
        font-size: 0.84rem;
        text-transform: uppercase;
      }}
      code {{
        background: rgba(15, 118, 110, 0.09);
        padding: 2px 6px;
        border-radius: 6px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      }}
      @media (max-width: 920px) {{
        .hero, .metric-grid, .grid-two {{
          grid-template-columns: 1fr;
        }}
        .wrap {{
          width: min(100vw - 20px, 1120px);
        }}
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <section class="hero">
        <div>
          <p class="eyebrow">Quant workbench report</p>
          <h1>Empirical Trade Summary</h1>
          <p>
            Static report generated from <code>{escape(source_name)}</code>.
            This report summarizes trade-level behavior, bootstrap uncertainty,
            and a simple lifecycle simulation from the same empirical trade stream.
          </p>
        </div>
        <div class="card">
          <h3>Trade path snapshot</h3>
          <div class="spark">{spark}</div>
        </div>
      </section>

      <section class="metric-grid">
        <article class="card metric">
          <div class="label">Trades</div>
          <div class="value">{int(summary["trades"])}</div>
        </article>
        <article class="card metric">
          <div class="label">Win rate</div>
          <div class="value">{_fmt_pct(float(summary["win_rate"]))}</div>
        </article>
        <article class="card metric">
          <div class="label">Expectancy</div>
          <div class="value">{_fmt_money(float(summary["expectancy"]))}</div>
        </article>
        <article class="card metric">
          <div class="label">Max drawdown</div>
          <div class="value">{_fmt_money(float(summary["max_drawdown"]))}</div>
        </article>
      </section>

      <section class="section grid-two">
        <article class="card">
          <h2>Trade-level statistics</h2>
          <div class="stat-list">
            <div class="stat-row"><span>Total pnl</span><strong>{_fmt_money(float(summary["total_pnl"]))}</strong></div>
            <div class="stat-row"><span>Average win</span><strong>{_fmt_money(float(summary["avg_win"]))}</strong></div>
            <div class="stat-row"><span>Average loss</span><strong>{_fmt_money(float(summary["avg_loss"]))}</strong></div>
            <div class="stat-row"><span>Profit factor</span><strong>{float(summary["profit_factor"]):.2f}</strong></div>
          </div>
        </article>
        <article class="card">
          <h2>Bootstrap EV band</h2>
          <div class="stat-list">
            <div class="stat-row"><span>EV estimate</span><strong>{_fmt_money(float(ev_ci["ev"]))}</strong></div>
            <div class="stat-row"><span>Lower bound</span><strong>{_fmt_money(float(ev_ci["lower"]))}</strong></div>
            <div class="stat-row"><span>Upper bound</span><strong>{_fmt_money(float(ev_ci["upper"]))}</strong></div>
            <div class="stat-row"><span>Zero cross</span><strong>{zero_cross}</strong></div>
            <div class="stat-row"><span>Lower bound positive</span><strong>{lower_positive}</strong></div>
          </div>
        </article>
      </section>

      {regime_table}

      <section class="section">
        <article class="card">
          <h2>Lifecycle simulation</h2>
          <div class="metric-grid">
            <div class="metric">
              <div class="label">Pass rate</div>
              <div class="value">{_fmt_pct(float(lifecycle["pass_rate"]))}</div>
            </div>
            <div class="metric">
              <div class="label">Payout rate</div>
              <div class="value">{_fmt_pct(float(lifecycle["payout_rate"]))}</div>
            </div>
            <div class="metric">
              <div class="label">Net EV</div>
              <div class="value">{_fmt_money(float(lifecycle["net_ev"]))}</div>
            </div>
            <div class="metric">
              <div class="label">Positive net probability</div>
              <div class="value">{_fmt_pct(float(lifecycle["prob_positive_net"]))}</div>
            </div>
          </div>
        </article>
      </section>
    </div>
  </body>
</html>
"""


def write_report_html(
    rows: list[TradeRow],
    summary: dict[str, float],
    ev_ci: dict[str, float | bool],
    lifecycle: dict[str, float | int | dict[str, float | int]],
    *,
    source_name: str,
    out_path: str | Path,
) -> Path:
    target = Path(out_path)
    target.write_text(
        build_report_html(rows, summary, ev_ci, lifecycle, source_name=source_name),
        encoding="utf-8",
    )
    return target
