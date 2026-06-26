# User Guide

## What the public package does

The public package is intentionally small and focused. It is useful for evaluating an empirical trade CSV when the goal is to answer questions like:

- what is the trade-level expectancy?
- how noisy is that expectancy?
- what happens if the same trade stream is wrapped in a constrained account lifecycle?

It is not a broker adapter or live trading engine.

## Input format

The package expects a CSV with at least one column:

```csv
pnl
161.26
-89.98
322.52
```

An optional `regime` column can be included:

```csv
pnl,regime
161.26,volatile
-89.98,normal
322.52,volatile
```

## Installation

From the repository root:

```bash
python3 -m pip install -e .
```

## Commands

### 1. Summarize trades

```bash
python3 -m quant_workbench.cli summarize-trades --trades path/to/trades.csv
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
  --trades path/to/trades.csv \
  --iterations 2000 \
  --seed 7
```

Returns:

- estimated EV
- lower and upper confidence bounds
- zero-cross flag
- lower-bound-positive flag

### 3. Simulate lifecycle

```bash
python3 -m quant_workbench.cli simulate-lifecycle \
  --trades path/to/trades.csv \
  --iterations 2000 \
  --seed 7
```

Returns:

- pass rate
- payout rate
- probability of positive net
- net expected value
- median / tail net outcomes

## Interpreting the results

The public package is most useful when the outputs are treated as decision-support tools, not as promises.

Good uses:

- compare two trade streams
- see how sensitive a strategy is to friction
- show research process in a project or interview
- sanity-check a backtest export before deeper work

Bad uses:

- assuming the lifecycle output is a deployable forecast
- treating a positive sample as proof of live viability
- skipping venue-specific execution validation
