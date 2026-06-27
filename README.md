# Quant Research Workbench

Quant Research Workbench is a public-safe quantitative research repo for
empirical trade analysis. It packages a few useful pieces of a larger intraday
futures research stack while keeping private deployable thresholds, venue
bridges, and live execution details out of the public mirror.

The core question is simple:

**Can a modest intraday edge remain meaningful after transaction costs,
account-rule friction, and execution uncertainty are made explicit?**

## Why this repo is worth reading

Most public quant repos optimize for one of three things:

- aesthetic dashboards
- impressive in-sample numbers
- vague strategy language with very little audit trail

This repo is stronger when read as a compact research workbench:

- it freezes a broad out-of-sample benchmark first
- it checks recent windows against that benchmark instead of retuning on recency
- it promotes policy branches only after ablation and stress checks
- it separates trade-level edge from payout geometry
- it turns checked-in artifacts into a reproducible docs surface and HTML report

## Repository scope

This public mirror includes:

- a lightweight Python package for trade summaries, regime diagnostics, EV
  uncertainty, lifecycle simulation, and static HTML reporting
- checked-in reference artifacts exported from a private ranked-event research
  run
- generated public artifacts rebuilt from an anonymized trade export
- docs that surface methodology, limitations, ablations, and package usage

This public mirror does **not** include:

- raw minute data or venue adapters
- private ranked-event thresholds
- deployable live trading credentials or execution bridges
- turnkey live trading code

## Audit trail

The best place to start is the artifact trail:

- [docs/index.html](docs/index.html)
- [results/reference/benchmark_summary.json](results/reference/benchmark_summary.json)
- [results/reference/window_checks.csv](results/reference/window_checks.csv)
- [results/reference/policy_ablations.csv](results/reference/policy_ablations.csv)
- [results/reference/stress_scenarios.csv](results/reference/stress_scenarios.csv)
- [results/reference/firm_comparison.csv](results/reference/firm_comparison.csv)
- [examples/anonymized_oos_report.html](examples/anonymized_oos_report.html)
- [docs/data/site_data.json](docs/data/site_data.json)

## Repository map

- [ARCHITECTURE.md](ARCHITECTURE.md)
  Public architecture of the research platform and the public-safe boundary.

- [WORKFLOW.md](WORKFLOW.md)
  End-to-end workflow: benchmark freezing, validation, lifecycle modeling, and
  stress thinking.

- [USER_GUIDE.md](USER_GUIDE.md)
  How to run the package and regenerate the public demo artifacts.

- [CASE_STUDY.md](CASE_STUDY.md)
  A data-backed narrative of the benchmark, ablations, stress ladder, and
  limitations.

- [RELATED_PAPERS.md](RELATED_PAPERS.md)
  Research influences behind the modeling choices.

- [results/README.md](results/README.md)
  What lives in `results/reference` versus `results/generated`.

- `quant_workbench/`  
  Public package for empirical trade analysis and lifecycle simulation.

- `examples/`  
  An anonymized trade export plus a generated HTML report.

- `tests/`
  Test coverage for the public workbench layer.

## Quick start

From the repository root:

```bash
python3 -m pip install -e .
python3 -m quant_workbench.cli build-public-demo --repo-root . --iterations 2000 --seed 7
python3 -m quant_workbench.cli summarize-trades --trades examples/anonymized_oos_trades.csv
python3 -m quant_workbench.cli summarize-regimes --trades examples/anonymized_oos_trades.csv
python3 -m quant_workbench.cli bootstrap-ev --trades examples/anonymized_oos_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli simulate-lifecycle --trades examples/anonymized_oos_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli write-report --trades examples/anonymized_oos_trades.csv --out examples/anonymized_oos_report.html --iterations 2000 --seed 7
```

The `build-public-demo` command rebuilds:

- `examples/anonymized_oos_report.html`
- `results/generated/package_summary.json`
- `results/generated/package_regimes.json`
- `results/generated/package_bootstrap_ev.json`
- `results/generated/package_lifecycle.json`
- `results/generated/artifact_manifest.json`
- `docs/data/site_data.json`

## Results layers

The public repo has two artifact layers:

- `results/reference/`
  Frozen benchmark, recent-window checks, ablations, stress scenarios, and
  cross-firm comparisons exported from the private research environment.

- `results/generated/`
  Outputs rebuilt locally from the anonymized checked-in trade export using the
  public package only.

That split matters. Reference artifacts carry the public research claims.
Generated artifacts prove the public package can reproduce a realistic surface
without exposing private deployment logic.

## What the package is good for

- reviewing an empirical trade export without opening a notebook stack
- comparing regime buckets and EV uncertainty quickly
- teaching the difference between trade-level edge and lifecycle economics
- showing research discipline and limitations in a recruiter-safe repo

## What it is not

- a broker adapter
- a live execution engine
- a public release of a private ranked-event strategy
- a substitute for venue-specific execution validation

## GitHub Pages

The `docs/` folder is already structured for GitHub Pages. The page reads from
`docs/data/site_data.json`, which is regenerated by the public demo build
command.
