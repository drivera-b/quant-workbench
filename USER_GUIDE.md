# User Guide

## What the public package does

The public package is intentionally small and focused. It is useful for
evaluating an empirical trade CSV when the goal is to answer questions like:

- what is the trade-level expectancy?
- which regime labels help or hurt the stream?
- how noisy is that expectancy?
- what happens when the same trade stream is wrapped in a constrained account
  lifecycle?

It is not a broker adapter or live trading engine.

## Installation

From the repository root:

```bash
python3 -m pip install -e .
```

## Public demo rebuild

If you want the full checked-in public surface rebuilt from the anonymized
example input, start here:

```bash
python3 -m quant_workbench.cli build-public-demo --repo-root . --iterations 2000 --seed 7
```

That command regenerates:

- `examples/anonymized_oos_report.html`
- `results/generated/package_summary.json`
- `results/generated/package_regimes.json`
- `results/generated/package_bootstrap_ev.json`
- `results/generated/package_lifecycle.json`
- `results/generated/artifact_manifest.json`
- `docs/data/site_data.json`

## Input format

The core package reads a CSV with at least one required column:

```csv
pnl
161.26
-251.24
161.26
```

An optional `regime` column can be included:

```csv
pnl,regime
161.26,volatile
-251.24,normal
161.26,volatile
```

The checked-in public example is intentionally richer:

```csv
trade_id,session_id,event_family,regime,score_bucket,bars_held,outcome,pnl
T0001,S001,gap,volatile,0.4-0.5,1,win,161.26
T0002,S001,impulse,normal,0.2-0.3,2,loss,-251.24
```

The extra fields help the public artifacts feel like a real research export,
even though the core metrics package only requires `pnl` and optionally
`regime`.

## Commands

### 1. Summarize trades

```bash
python3 -m quant_workbench.cli summarize-trades --trades examples/anonymized_oos_trades.csv
```

Returns:

- trade count
- win rate
- expectancy
- total pnl
- average win / loss
- profit factor
- max drawdown

### 2. Bootstrap expectancy

```bash
python3 -m quant_workbench.cli bootstrap-ev \
  --trades examples/anonymized_oos_trades.csv \
  --iterations 2000 \
  --seed 7
```

Returns:

- estimated EV
- lower and upper confidence bounds
- zero-cross flag
- lower-bound-positive flag

### 3. Summarize by regime

```bash
python3 -m quant_workbench.cli summarize-regimes --trades examples/anonymized_oos_trades.csv
```

Returns:

- one trade summary per regime label
- per-regime win rate, expectancy, total pnl, and drawdown
- an `unlabeled` bucket when rows do not carry a regime value

### 4. Simulate lifecycle

```bash
python3 -m quant_workbench.cli simulate-lifecycle \
  --trades examples/anonymized_oos_trades.csv \
  --iterations 2000 \
  --seed 7
```

Returns:

- pass rate
- payout rate
- probability of positive net
- net expected value
- median and tail net outcomes

### 5. Write a static HTML report

```bash
python3 -m quant_workbench.cli write-report \
  --trades examples/anonymized_oos_trades.csv \
  --out examples/anonymized_oos_report.html \
  --iterations 2000 \
  --seed 7
```

Returns a self-contained HTML report with:

- trade summary
- regime breakdown when labels are present
- bootstrap EV bounds
- lifecycle Monte Carlo outputs

## Interpreting the results

The public package is most useful when the outputs are treated as
decision-support tools, not promises.

Good uses:

- compare two trade streams
- inspect which regime buckets are actually carrying expectancy
- generate a quick shareable report for discussion
- separate trade-level edge from account-wrapper effects

Bad uses:

- assuming the lifecycle output is a deployable forecast
- treating a positive sample as proof of live viability
- skipping venue-specific execution validation
