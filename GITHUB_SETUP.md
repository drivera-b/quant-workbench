# GitHub Setup

This folder is meant to become its own public repo.

## Recommended repo name

- `quant-research-workbench`
- `intraday-futures-validation-lab`
- `event-driven-futures-research`

## What to publish

Publish the contents of this folder:

- `README.md`
- `ARCHITECTURE.md`
- `WORKFLOW.md`
- `USER_GUIDE.md`
- `CASE_STUDY.md`
- `INTERVIEW_GUIDE.md`
- `PORTFOLIO_COPY.md`
- `RELATED_PAPERS.md`
- `PUBLISHING_CHECKLIST.md`
- `quant_workbench/`
- `tests/`
- `examples/`
- `docs/`

## Suggested GitHub repo description

Python quant research platform for intraday futures strategy validation with event studies, backtesting, bootstrap confidence intervals, Monte Carlo lifecycle simulation, and forward-validation tooling.

## Suggested GitHub topics

- `python`
- `quantitative-finance`
- `backtesting`
- `monte-carlo`
- `time-series`
- `simulation`
- `research-tools`
- `data-engineering`

## Local steps

From inside `public_mirror/`:

```bash
git init
git add .
git commit -m "Initial public mirror"
```

Then create an empty GitHub repo and connect it:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## GitHub Pages

The showcase in `docs/index.html` is already set up for GitHub Pages.

After pushing:

1. Open the repo on GitHub.
2. Go to `Settings`.
3. Open `Pages`.
4. Set source to `Deploy from a branch`.
5. Choose branch `main`.
6. Choose folder `/docs`.
7. Save.

GitHub will then host the showcase from `docs/`.

## Keep private

Do not mix this public mirror with:

- exact deployable benchmark JSON files
- private journals
- execution-intent exports
- venue-specific live settings
- artifacts that make the private strategy easy to reverse engineer

The point of this repo is to showcase the research process and engineering quality, not to publish the private edge.
