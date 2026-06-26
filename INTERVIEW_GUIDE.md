# Interview Guide

This guide is meant to support deeper conversations about the project. It leads with the questions I would expect a serious interviewer to ask.

## Why does the strategy exist?

The motivating idea is that some intraday futures behavior around the open can be represented as explicit event families rather than vague chart intuition. The project tests whether those event families have any measurable trade-level usefulness once context is added.

The point is not "markets are predictable in a magical way." The point is that some structured event/context combinations may produce a modest edge worth evaluating honestly.

## What happens under stress?

Stress testing matters because small edges are fragile.

The project explicitly checks:

- wider effective costs
- worse fills
- regime instability
- recent-window degradation
- account-rule friction

One of the most important takeaways is that a strategy can remain viable under small extra cost stress and still weaken badly under broad execution degradation. That is a more useful conclusion than a single optimistic backtest number.

## How stable is the signal across regimes?

Not perfectly stable, and that matters.

The project treats regime behavior as something to measure, not assume. It uses volatility and context labels to compare how event families behave in different environments. The goal is not to claim regime invariance, but to know where the signal is stronger, weaker, or too noisy to trust.

## What changes once transaction costs become real?

Two things:

1. some attractive branches disappear
2. execution quality becomes part of the model, not a footnote

That is why the project does not stop at raw expectancy. It includes stress scenarios for fees and fill quality, plus lifecycle modeling where cost drag compounds through repeated attempts and payouts.

## What breaks first in production?

The most likely failure points are:

- execution drift from the research fill model
- venue-specific order-routing constraints
- automation issues around session timing and state tracking
- degraded fills in exactly the short holding-period trades that look best on paper

In other words, production risk is not just "the signal stops working." It is often that the implementation cannot reproduce the benchmark closely enough.

## How does execution affect returns?

Execution affects the project in two ways:

- directly, through worse entry and exit quality
- indirectly, by interacting with tight holding periods and fixed account rules

This is why the project separates the Python-side truth engine from any venue-side execution bridge. That keeps the research question clean: did the execution layer reproduce the intended actions closely enough?

## What assumptions silently fail?

The main silent assumptions are:

- that historical fills are representative of live fills
- that signal cadence remains similar in newer samples
- that regime mix does not shift too far
- that account-rule wrappers do not dominate the economics
- that a platform adapter can reproduce the research logic faithfully enough

The project is strongest when it names these assumptions instead of hiding them.

## Related papers and institutional intuition

The project was influenced by a mix of intraday microstructure, regime, and risk-modeling ideas. A few examples:

- **Intraday Price Formation in U.S. Equity Index Markets**  
  Helpful for thinking about futures-led price discovery and ES/NQ context.

- **Clustering Market Regimes Using the Wasserstein Distance**  
  Helpful as a regime-thinking reference even where the implementation stayed simpler.

- **The Random Matrix-Based Informative Content of Correlation Matrices in Stock Markets**  
  Useful for thinking about when correlation structure may be informative versus mostly noise.

- **Time-Varying Factor-Augmented Models**  
  A reminder that market structure is not static and context should be treated as dynamic.

- **Deep Learning Enhanced Multivariable GARCH**  
  More of an extension reference than a core implementation choice, but relevant for future volatility modeling ideas.

- **The Augmented Black-Litterman Model** and **Robust Online Portfolio Optimization with Cash Flows**  
  Not direct strategy engines here, but useful for broader portfolio and capital-allocation thinking.

The institutional intuition underneath the project is simple:

- small edges can be real
- small edges are easy to destroy
- the wrapper around the edge can matter almost as much as the edge itself

## Extension pathways

If I kept pushing the project forward, the most sensible next steps would be:

- richer execution-quality modeling using trade/quote data
- cleaner regime segmentation
- better causal forward-validation workflows
- venue-specific execution adapters with replay testing
- broader research dashboards for comparing branches and failure modes

## Resume positioning

The right way to position this project is not:

- "I built a trading bot with amazing returns"

The better framing is:

- "I built a validation-first quantitative research platform for intraday futures, focused on whether small edges survive realistic frictions, account rules, and execution uncertainty."

That signals the right instincts:

- quantitative honesty
- experimental discipline
- engineering depth
- understanding of fragility

## Questions I would be ready for

- Why did you choose these event families?
- How did you keep the benchmark honest?
- What did you reject and why?
- How sensitive are the results to execution?
- What evidence would make you stop trusting the candidate?
- What part of the system are you least confident in?
- What would you do next if given more data or more time?

Those are good questions. A project like this should be able to survive them.
