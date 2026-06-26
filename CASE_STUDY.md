# Case Study

## Project

**Quant Research Workbench**

A Python research platform for studying whether small intraday futures edges can remain viable after realistic frictions, account rules, and execution constraints.

## Problem framing

Many public trading projects stop at a backtest. This project is organized around a broader research question:

**What happens to a promising signal once transaction costs, constrained account rules, and execution drift are made explicit?**

That framing pushes the work beyond raw trade statistics and toward a more complete research workflow.

## System design

The system has four layers:

### 1. Data and feature layer

- normalized futures OHLCV inputs
- event extraction
- contextual features around the open
- volatility and regime labels
- optional cross-asset context

### 2. Research layer

- event studies
- deterministic strategy backtests
- ranked-event selection
- bootstrap confidence intervals

### 3. Lifecycle simulation layer

- Monte Carlo resampling
- prop-style challenge and funded modeling
- fees, payout splits, resets, and drawdown rules
- cross-firm comparison under different rule sets

### 4. Forward-validation layer

- benchmark freezing
- recent-window comparison
- paper-trade style evaluation
- execution-drift and stress thinking

## The key design decision

The most important architectural choice was separating:

- **signal quality**
- **payout geometry**

A strategy can have non-awful trade statistics and still be a bad lifecycle bet. Conversely, a modest edge can look much better or much worse depending on the account structure wrapped around it.

That led to a cleaner research process:

1. test whether the signal has any defensible trade-level edge
2. test whether the account geometry helps or hurts that edge
3. stress the result under more realistic execution assumptions

## Research arc

The project moved through several stages:

1. simple opening and gap-style tests
2. translation of discretionary ideas into explicit rules
3. event-study promotion of stronger catalyst families
4. ranked-event selection with contextual features
5. recent-window robustness and cross-firm lifecycle comparison

The useful lesson was not that every branch worked. It was that several branches **did not** survive once the evaluation became more honest.

## What made the project stronger

Three things improved the project most:

### 1. Freezing the benchmark

Instead of retuning every time a new sample arrived, the project keeps a frozen benchmark and compares newer windows against it. That makes drift visible.

### 2. Stressing execution

It is easy to hide behind backtest fills. This project explicitly asked what happens when:

- fees increase
- fills degrade
- regime mix changes
- recent performance becomes noisier

That made the conclusions much more credible.

### 3. Treating limitations as first-order outputs

The output is not just performance. It is also:

- what assumptions carry the result
- what breaks first
- how sensitive the edge is to execution quality
- whether the recent sample is broadly consistent with the frozen benchmark

## What I learned

The biggest lesson was that strong research often looks less impressive at first glance.

The branches that were easiest to sell were not always the branches that held up best. The more useful work was:

- tightening definitions
- measuring fragility
- separating signal from wrapper effects
- accepting when a result was only conditionally good

That is the part of the project I would want a recruiter or interviewer to notice.

## Public research value

This repository is useful as a public artifact because it shows:

- experimental discipline
- systems thinking
- quantitative modeling
- technical writing
- the ability to communicate uncertainty without hiding behind hype

It is much closer to a real research workflow than a one-off notebook with a high Sharpe ratio.
