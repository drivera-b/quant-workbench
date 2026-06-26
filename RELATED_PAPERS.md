# Related Papers

This public project was informed by real research ideas, even when the final implementation stayed simpler than the papers themselves.

## Regime and structure

- **Clustering Market Regimes Using the Wasserstein Distance**  
  Useful for thinking about regime segmentation as a modeling problem rather than a loose label.

- **Time-Varying Factor-Augmented Models**  
  Reinforces the idea that explanatory structure changes over time, so context should not be treated as fixed.

- **The Random Matrix-Based Informative Content of Correlation Matrices in Stock Markets**  
  Helpful for thinking about when cross-asset correlation structure might contain signal versus mostly noise.

## Intraday microstructure and open behavior

- **Intraday Price Formation in U.S. Equity Index Markets**  
  Directly relevant to futures-led price discovery and the intuition behind ES/NQ context features.

- gap-fill / opening-drive literature and intraday reversal studies  
  Helpful for understanding why the opening session is worth isolating and why continuation versus reversal should be treated as empirical rather than narrative questions.

## Volatility and execution realism

- **Deep Learning Enhanced Multivariable GARCH**  
  More relevant as an extension path than a core implementation choice, but useful for thinking about richer volatility modeling.

- execution-sensitive intraday studies  
  Important because short holding periods are especially vulnerable to fill assumptions and transaction-cost drift.

## Portfolio and allocation context

- **Robust Online Portfolio Optimization with Cash Flows**
- **The Augmented Black-Litterman Model**

These were not used as direct strategy engines, but they were helpful for capital-allocation thinking and for keeping the project grounded in broader portfolio logic rather than isolated signal enthusiasm.

## Quantamental perspective

- **Quantamentals: Combining Technical and Fundamental Analysis**

This was more of a framing reference than a literal implementation recipe. It helped reinforce the idea that context features and broader market structure can matter as much as raw price patterns.

## Honest framing

The public point is not "this project reproduces every paper."

The stronger and more honest claim is:

- the project was informed by real market microstructure, regime, and risk-modeling ideas
- those ideas were translated into a practical research workflow
- the implementation stayed focused on falsifiable, testable components

That is a better research story than pretending the repo is a direct paper clone.
