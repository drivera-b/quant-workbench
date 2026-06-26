# Quant Research Workbench

Quant Research Workbench is a public-safe quantitative research repository for intraday futures workflows. It exposes the research infrastructure, validation approach, and lifecycle modeling ideas behind the project while intentionally omitting private deployable strategy settings.

The repository centers on one question:

**Can a modest intraday edge remain meaningful after transaction costs, account-rule friction, and execution uncertainty are made explicit?**

## Repository scope

This public mirror includes:

- quantitative research framing and documentation
- architecture and workflow notes
- a GitHub Pages-ready showcase
- a lightweight Python package for trade-level summaries and lifecycle simulation
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

- [CASE_STUDY.md](CASE_STUDY.md)  
  Narrative case study of the problem, methodology, and main lessons.

- [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)  
  Questions, limitations, and discussion prompts for deeper interviews.

- [PORTFOLIO_COPY.md](PORTFOLIO_COPY.md)  
  Resume bullets, recruiter blurbs, and GitHub-ready positioning.

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
- bootstrap confidence intervals for expectancy
- simple lifecycle Monte Carlo using empirical trade resampling

## Quick start

Create a virtual environment if desired, then from the repository root:

```bash
python3 -m pip install -e .
python3 -m quant_workbench.cli summarize-trades --trades examples/sample_trades.csv
python3 -m quant_workbench.cli bootstrap-ev --trades examples/sample_trades.csv --iterations 2000 --seed 7
python3 -m quant_workbench.cli simulate-lifecycle --trades examples/sample_trades.csv --iterations 2000 --seed 7
```

## Example output questions

The public workbench is designed around questions such as:

- What is the trade-level expectancy?
- How wide is the uncertainty band around that expectancy?
- What happens if the same empirical trade distribution is wrapped in a constrained account lifecycle?
- Which assumptions matter most once friction is included?

## Why this repository exists

Many public quant repositories optimize for aesthetics, in-sample performance, or grand claims. This repository is more useful when read as a research artifact:

- it separates signal quality from payout geometry
- it treats execution as a first-order risk
- it emphasizes benchmark freezing and recent-window comparisons
- it makes room for uncertainty and failure modes

That makes it a better fit for readers interested in research process, systems design, and quantitative validation than for readers looking for a copy-trading recipe.

## GitHub Pages

The `docs/` folder is already structured for GitHub Pages. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for the publish steps.
