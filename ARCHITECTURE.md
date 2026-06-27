# Architecture

## Overview

The full private project is structured as a research platform rather than a single backtest script. This public mirror exposes that architecture at a safe level.

The architecture is best understood as four connected layers:

1. **Data and normalization**
2. **Research and feature generation**
3. **Lifecycle simulation**
4. **Forward-validation and execution analysis**

## 1. Data and normalization

The private project consumes minute-level futures data and standardizes it into a common format for research.

Typical responsibilities:

- OHLCV normalization
- session alignment
- export adapters for external platforms
- basic schema consistency

The public mirror does not ship private raw data, but it does preserve the shape of the workflow.

## 2. Research and feature generation

The research layer turns market structure into explicit, testable objects rather than chart narratives.

Typical responsibilities:

- event-family generation
- contextual feature engineering
- volatility and regime labeling
- ranked-event or rule-based backtests
- trade-level statistical summaries

The public code package in this mirror includes the generic evaluation side of this layer, especially empirical trade summaries, regime diagnostics, and bootstrap confidence intervals.

## 3. Lifecycle simulation

The key modeling decision is to separate:

- **trade-level edge**
- **account wrapper economics**

That means the same trade distribution can be evaluated under different friction and payout structures.

The public mirror includes a lightweight lifecycle simulator that demonstrates:

- passing a challenge-style phase
- failing on a loss barrier
- entering a funded-style phase
- extracting payouts after fees and splits

This is intentionally simpler than the full private simulator, but it preserves the core idea.

## 4. Forward-validation and execution analysis

The private project treats execution as a source of model error, not just an operational detail.

Typical responsibilities:

- frozen benchmark comparison
- recent-window consistency checks
- slippage and fill-degradation thinking
- venue-side execution bridging

The public mirror documents this layer and keeps the design visible, while leaving deployable venue logic private.

## Public repository layout

```text
public_mirror/
  README.md
  ARCHITECTURE.md
  WORKFLOW.md
  USER_GUIDE.md
  CASE_STUDY.md
  RELATED_PAPERS.md
  docs/
  examples/
  quant_workbench/
  tests/
  pyproject.toml
```

## Public code package layout

```text
quant_workbench/
  __init__.py
  cli.py
  io.py
  metrics.py
  lifecycle.py
  reporting.py
```

## Design goals for the public mirror

- expose the workflow and reasoning
- keep the repository runnable
- avoid publishing private deployable edge details
- provide enough code to demonstrate that the project is a workbench, not just a writeup

That balance is the main architectural constraint of the public version.
