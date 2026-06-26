# Publishing Checklist

Use this checklist when turning the private research repo into a public-safe mirror.

## Safe to publish

- generic system architecture
- feature-engineering approach at a high level
- validation philosophy
- lifecycle simulation design
- public-safe dashboards and screenshots
- recruiter-facing case study and portfolio copy
- tests that do not reveal private benchmark settings

## Keep private

- exact benchmark JSONs used for deployment decisions
- deployable selector thresholds and score tables
- venue-specific execution intents
- private journals and live testing notes
- any data artifacts that make the strategy easy to reverse engineer

## Review before publishing

- remove or abstract private output artifacts
- check screenshots for revealing parameters
- scrub proprietary command examples if they reveal exact live settings
- replace private benchmark paths with sanitized placeholders where needed
- make sure the README frames the project as research infrastructure, not a public signal release

## Better public framing

Lead with:

- research question
- validation workflow
- stress testing
- uncertainty and limitations
- engineering decisions

Avoid leading with:

- eye-catching return numbers
- overfit Sharpe ratios
- claims that imply deployable alpha is being published

## Good final public package

The public version should make a recruiter think:

- this person can design experiments
- this person understands fragility
- this person can build systems around messy real constraints

It should not make them think:

- this is another hype-heavy trading repo
- the candidate does not understand limitations

That difference is the whole point.
