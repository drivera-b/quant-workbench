# Workflow

## Research workflow

The research process is organized around explicit checkpoints rather than a
single backtest result.

### 1. Define the research question

The starting point is not "find the best chart pattern." It is:

- which intraday event families are worth representing explicitly?
- what context might change their behavior?
- what failure modes should be visible before trusting the result?

### 2. Normalize market data

Minute-level futures data is converted into a consistent schema suitable for
repeatable research.

Typical outputs:

- session-aligned OHLCV bars
- derived event rows
- empirical trade CSVs for resampling

### 3. Engineer event and context features

Potential catalysts are converted into explicit event families. Context
features are layered on top:

- volatility state
- opening-session structure
- overnight or prior-session context
- optional cross-asset information

### 4. Backtest and summarize

The next step is not just to run a strategy but to summarize the resulting
trade stream honestly:

- trade count
- win rate
- expectancy
- profit factor
- drawdown
- regime-level splits when labels are available

### 5. Freeze the benchmark

The strongest anti-overfitting move in the workflow is to lock a broad
out-of-sample benchmark first, then compare newer windows to it.

That makes recent drift visible instead of letting each new sample quietly
become a retuning target.

### 6. Bootstrap uncertainty

Backtest outputs are not treated as certain. The empirical trade distribution
is resampled to estimate a confidence interval around expectancy.

### 7. Wrap the trade stream in account rules

The same trade distribution is evaluated under challenge-style and funded-style
account constraints:

- profit target
- loss barrier
- activation fees
- payout trigger
- payout split

This is where modest trade-level edges can become either more interesting or
much less interesting.

### 8. Run ablations and friction stress

The workflow becomes more useful when it asks:

- what happens if a weak event family is excluded?
- what happens if costs are slightly worse?
- what happens if fills degrade?
- what happens if recent performance weakens?

### 9. Keep execution separate from research logic

Execution and venue-specific bridging matter, but they should not be allowed to
quietly rewrite the research logic. The public mirror documents that separation
even where deployable bridge code remains private.

## Public artifact workflow

The public repo preserves a smaller, runnable loop:

1. load an anonymized empirical trade export
2. compute trade-level summaries
3. inspect regime splits
4. bootstrap EV confidence intervals
5. simulate lifecycle economics
6. write a static HTML report
7. regenerate the docs payload used by GitHub Pages

Example commands:

```bash
python3 -m pip install -e .
python3 -m quant_workbench.cli build-public-demo --repo-root . --iterations 2000 --seed 7
python3 -m quant_workbench.cli summarize-trades --trades examples/anonymized_oos_trades.csv
python3 -m quant_workbench.cli summarize-regimes --trades examples/anonymized_oos_trades.csv
python3 -m quant_workbench.cli bootstrap-ev --trades examples/anonymized_oos_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli simulate-lifecycle --trades examples/anonymized_oos_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli write-report --trades examples/anonymized_oos_trades.csv --out examples/anonymized_oos_report.html --iterations 2000 --seed 7
```

## What the public workflow is for

This workflow is meant to demonstrate:

- quantitative process design
- empirical trade evaluation
- uncertainty estimation
- lifecycle modeling under constraints
- artifact-backed research communication

It is not meant to publish a private live strategy.
