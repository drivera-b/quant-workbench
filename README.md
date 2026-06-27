# Quant Research Workbench

Quant Research Workbench is a lightweight quantitative research toolkit for empirical trade analysis. It packages a few genuinely useful pieces of a larger intraday futures research stack while intentionally leaving private deployable settings out of the public mirror.

The repository centers on one question:

**Can a modest intraday edge remain meaningful after transaction costs, account-rule friction, and execution uncertainty are made explicit?**

## Repository scope

This public mirror includes:

- quantitative research framing and documentation
- architecture and workflow notes
- a GitHub Pages-ready overview
- a lightweight Python package for trade-level summaries, regime diagnostics, uncertainty estimation, lifecycle simulation, and static HTML reporting
- tests and example data for the public workbench layer

This public mirror does **not** include:

- private benchmark JSON artifacts
- deployable selector thresholds
- venue-specific execution bridges
- live-account parameters

## Repository map

- [ARCHITECTURE.md](ARCHITECTURE.md)  
  Public architecture of the research platform.

- [WORKFLOW.md](WORKFLOW.md)  
  End-to-end research workflow: event extraction, validation, lifecycle modeling, and forward evaluation.

- [USER_GUIDE.md](USER_GUIDE.md)  
  How to run the public package on a trade CSV and what the commands return.

- [CASE_STUDY.md](CASE_STUDY.md)  
  Narrative case study of the problem, methodology, and main lessons.

- [RELATED_PAPERS.md](RELATED_PAPERS.md)  
  Research influences behind the modeling choices.

- [docs/index.html](docs/index.html)  
  GitHub Pages-ready project overview with validation and stress-test framing.

- `quant_workbench/`  
  Lightweight public code package for empirical trade analysis and lifecycle simulations.

- `tests/`  
  Basic test coverage for the public workbench layer.

- `examples/`  
  Small sample trade data for local runs and quick demonstrations.

## Public package

The included package is intentionally generic. It demonstrates the research workflow without exposing private alpha configuration.

Available utilities:

- empirical trade summary
- regime-by-regime summary when labels are available
- bootstrap confidence intervals for expectancy
- simple lifecycle Monte Carlo using empirical trade resampling
- static HTML report generation from an empirical trade CSV

## Quick start

Create a virtual environment if desired, then from the repository root:

```bash
python3 -m pip install -e .
python3 -m quant_workbench.cli summarize-trades --trades examples/sample_trades.csv
python3 -m quant_workbench.cli summarize-regimes --trades examples/sample_trades.csv
python3 -m quant_workbench.cli bootstrap-ev --trades examples/sample_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli simulate-lifecycle --trades examples/sample_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli write-report --trades examples/sample_trades.csv --out examples/sample_report.html --iterations 2000 --seed 7
```

## Example output questions

The public workbench is designed around questions such as:

- What is the trade-level expectancy?
- Which regime labels are actually carrying the stream?
- How wide is the uncertainty band around that expectancy?
- What happens if the same empirical trade distribution is wrapped in a constrained account lifecycle?
- Which assumptions matter most once friction is included?

## Why this repository exists

Many public quant repositories optimize for aesthetics, in-sample performance, or grand claims. This repository is more useful when read as a compact workbench:

- it separates signal quality from payout geometry
- it treats execution as a first-order risk
- it emphasizes benchmark freezing and recent-window comparisons
- it makes room for uncertainty and failure modes
- it turns a plain trade CSV into a shareable report without a notebook stack

That makes it a better fit for readers who care about research process, systems design, and quantitative validation than for readers looking for turnkey live deployment code.

## GitHub Pages

The `docs/` folder is already structured for GitHub Pages.
