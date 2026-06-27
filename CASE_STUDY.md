# Case Study

## Project

**Quant Research Workbench**

A public-safe research platform for studying whether a small intraday futures
edge can remain viable after realistic friction, account rules, and execution
stress are made explicit.

## Why this project is interesting

Many public quant projects stop at a backtest and a headline metric. This
project is more useful when framed as a broader research question:

**What happens to a promising trade stream once benchmark discipline, account
geometry, and execution degradation are all made first-order?**

That framing pushes the work past raw trade statistics and toward a more honest
research loop.

## Public artifact trail

The public claims in this repo are backed by checked-in artifacts:

- [results/reference/benchmark_summary.json](results/reference/benchmark_summary.json)
- [results/reference/window_checks.csv](results/reference/window_checks.csv)
- [results/reference/policy_ablations.csv](results/reference/policy_ablations.csv)
- [results/reference/stress_scenarios.csv](results/reference/stress_scenarios.csv)
- [results/reference/firm_comparison.csv](results/reference/firm_comparison.csv)
- [results/reference/firm_comparison_plus2usd.csv](results/reference/firm_comparison_plus2usd.csv)
- [examples/anonymized_oos_report.html](examples/anonymized_oos_report.html)

## System design

The system has five layers:

### 1. Data and feature layer

- normalized futures inputs
- event extraction
- contextual features around the open
- volatility and regime labels
- optional cross-asset context

### 2. Research layer

- event studies
- deterministic backtests
- ranked-event selection
- bootstrap confidence intervals

### 3. Benchmark-control layer

- frozen broad out-of-sample anchor
- recent-window comparisons
- explicit policy ablations

### 4. Lifecycle simulation layer

- Monte Carlo resampling
- prop-style challenge and funded modeling
- fees, payout splits, resets, and drawdown rules
- cross-firm comparison under different rule sets

### 5. Forward-validation and execution layer

- recent-window tracking
- fill and cost stress
- execution-quality thinking

## The key architectural choice

The most important design decision was separating:

- **signal quality**
- **payout geometry**

A trade stream can have acceptable trade-level statistics and still be a poor
lifecycle bet. Conversely, a modest edge can look materially better or worse
depending on the account structure wrapped around it.

That led to a cleaner research process:

1. test whether the signal has any defensible trade-level edge
2. freeze a benchmark before looking too hard at recency
3. compare policy branches through ablation instead of storytelling
4. wrap the trade stream in realistic account rules
5. stress the result under worse execution

## Public benchmark snapshot

The frozen benchmark artifact reports:

| Metric | Value |
| --- | ---: |
| Broad OOS trades | 1123 |
| Win rate | 66.6% |
| Expectancy | $23.52 |
| Lifecycle EV | $2,396.66 |
| Probability of positive net | 73.4% |

The recent 90-session reference check reports:

| Metric | Value |
| --- | ---: |
| Trades | 164 |
| Win rate | 67.7% |
| Expectancy | $27.95 |
| EV lower bound | $0.28 |
| Status | on_track |

That matters because the recent window is being judged against a frozen anchor,
not promoted simply for being recent.

## What the ablations actually found

The public ablation table is one of the strongest parts of the repo because it
shows that not every plausible branch was allowed to survive.

| Policy | Trades | Win rate | Expectancy | EV lower | Status | Lifecycle EV |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| baseline | 164 | 67.7% | $27.95 | -$2.23 | inconclusive | $2,498.32 |
| volatile_only | 162 | 67.3% | $26.31 | -$4.25 | inconclusive | $3,631.01 |
| exclude_prior_sweep | 164 | 67.7% | $27.95 | $0.28 | on_track | $2,491.84 |

The useful result is not that the promoted branch has the highest lifecycle EV.
It is that `exclude_prior_sweep` is the only checked branch that preserved a
positive EV lower bound at the 90-session anchor.

That is a much more credible reason to promote a branch than "it looked best in
the last sample."

## Execution stress is the real warning label

The stress ladder is where the project becomes more honest:

| Scenario | Net EV | Funded payout rate | Median net |
| --- | ---: | ---: | ---: |
| base | $2,509.22 | 73.3% | $1,878.56 |
| plus_1usd | $2,324.31 | 71.3% | $1,850.22 |
| plus_2usd | $2,120.10 | 68.0% | $1,814.55 |
| fill_haircut_5pct | $888.29 | 47.3% | -$319.50 |

This is the most important caution in the whole project.

Small extra cost hurts but does not destroy the profile. Broad fill degradation
does. That tells a reviewer exactly what breaks first in production.

## Cross-firm payout geometry

The same trade stream behaves differently under different account wrappers:

| Program | Net EV | Funded payout rate |
| --- | ---: | ---: |
| MyFundedFutures Rapid 50K | $3,740.59 | 84.4% |
| LucidPro 50K | $3,706.86 | 84.8% |
| Topstep 50K Standard | $2,509.22 | 73.3% |
| LucidFlex 50K | $1,936.85 | 92.9% |
| MyFundedFutures Flex 50K | -$165.65 | 0.0% |

Under the `+$2 per trade` stress case, the same ranking remains broadly
similar:

| Program | Net EV |
| --- | ---: |
| MyFundedFutures Rapid 50K | $3,351.78 |
| LucidPro 50K | $3,340.81 |
| Topstep 50K Standard | $2,120.10 |
| LucidFlex 50K | $1,855.89 |
| MyFundedFutures Flex 50K | -$175.13 |

The key point is not that payout geometry creates alpha. The point is that
account structure changes the realized economics of a small edge enough that it
belongs inside the research loop.

## Public package layer

The repo also includes a runnable package that rebuilds the public surface from
the anonymized checked-in trade export:

```bash
python3 -m pip install -e .
python3 -m quant_workbench.cli build-public-demo --repo-root . --iterations 2000 --seed 7
```

That command regenerates:

- [results/generated/package_summary.json](results/generated/package_summary.json)
- [results/generated/package_regimes.json](results/generated/package_regimes.json)
- [results/generated/package_bootstrap_ev.json](results/generated/package_bootstrap_ev.json)
- [results/generated/package_lifecycle.json](results/generated/package_lifecycle.json)
- [docs/data/site_data.json](docs/data/site_data.json)

This is important because it proves the repo is not only a writeup. It is a
small, runnable research workbench.

## Main lessons

The most useful lesson from this project is that serious research often looks
less impressive at first glance.

What improved the project most was not cosmetic complexity. It was:

- freezing the benchmark
- promoting branches by ablation instead of vibe
- stressing execution quality directly
- showing what assumptions fail first
- keeping the public and private boundaries explicit

That is the part of the project most likely to survive a deeper technical
conversation.
