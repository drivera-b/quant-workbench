# Workflow

## Research workflow

The research process is organized around explicit checkpoints rather than a single backtest result.

### 1. Define the research question

The starting point is not "find the best chart pattern." It is:

- which intraday event families are worth representing explicitly?
- what context might change their behavior?
- what failure modes should be visible before trusting the result?

### 2. Normalize market data

Minute-level futures data is converted into a consistent schema suitable for repeatable research.

Typical outputs:

- session-aligned OHLCV bars
- derived event rows
- empirical trade CSVs for resampling

### 3. Engineer event and context features

Potential catalysts are converted into explicit event families. Context features are then layered on top:

- volatility state
- time-of-day
- overnight or opening context
- optional cross-asset information

### 4. Backtest and summarize

The next step is not just to run a strategy but to summarize the resulting trade stream honestly:

- trade count
- win rate
- expectancy
- profit factor
- drawdown

### 5. Bootstrap uncertainty

Backtest outputs are not treated as certain. The empirical trade distribution is resampled to estimate a confidence interval around expectancy.

### 6. Wrap the trade stream in account rules

The same trade distribution is then evaluated under challenge-style and funded-style account constraints:

- profit target
- loss barrier
- activation fees
- payout trigger
- payout split

This is where modest trade-level edges can become either more interesting or much less interesting.

### 7. Stress friction assumptions

The workflow becomes more useful when it asks:

- what happens if costs are slightly worse?
- what happens if fills degrade?
- what happens if recent performance weakens?

### 8. Compare recent windows against the benchmark

Recent samples should be evaluated against a frozen benchmark instead of being used for constant retuning. This is the main protection against overreacting to noise.

### 9. Keep execution separate from research

Execution and venue-specific bridging are important, but they should not be allowed to quietly rewrite the research logic. The public mirror documents that separation even where the deployable bridge remains private.

## Public code workflow

The public repository exposes a smaller runnable loop:

1. load empirical trades from CSV
2. compute trade-level summaries
3. bootstrap confidence intervals
4. run lifecycle Monte Carlo with configurable rules

Example commands:

```bash
python3 -m quant_workbench.cli summarize-trades --trades examples/sample_trades.csv
python3 -m quant_workbench.cli bootstrap-ev --trades examples/sample_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli simulate-lifecycle --trades examples/sample_trades.csv --iterations 2000 --seed 7
```

## What the public workflow is for

This workflow is meant to demonstrate:

- quantitative process design
- empirical trade evaluation
- uncertainty estimation
- lifecycle modeling under constraints

It is not meant to publish a private live strategy.
