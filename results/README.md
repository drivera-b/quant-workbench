# Results

The public repo keeps research artifacts in two layers.

## `reference/`

Frozen artifacts exported from the private ranked-event research environment:

- `benchmark_summary.json`
- `window_checks.csv`
- `monthly_stability.csv`
- `policy_ablations.csv`
- `stress_scenarios.csv`
- `firm_comparison.csv`
- `firm_comparison_plus2usd.csv`
- `methodology.json`
- `sample_dataset_metadata.json`

These files carry the public research claims.

## `generated/`

Artifacts rebuilt locally from the checked-in anonymized trade export using the
public package only:

- `package_summary.json`
- `package_regimes.json`
- `package_bootstrap_ev.json`
- `package_lifecycle.json`
- `artifact_manifest.json`

These files prove the public workbench can regenerate a realistic docs and
reporting surface without exposing private deployment details.

The public rebuild flow also generates lightweight README charts in
`assets/readme/` from the checked-in reference data so the repository front
page shows actual evidence, not only links.
