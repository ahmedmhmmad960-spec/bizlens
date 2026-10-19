# Observed Signals — V1 bar chart contract

The third V1 dashboard chart is **Observed Signals**. It appears on the
existing "What changed" screen and draws from the structured
`what_changed` response. It does **not** independently recalculate
financial metrics or ask AI to supply numbers.

## Source and temporal scope

- Source engine: `core/changes/engine.py` `build_what_changed`.
- Every emitted signal contains `previous`, `current`, absolute
  `change`, optional `change_percent` and `direction`.
- V1 comparison is between **chronological halves of the observed date
  range**. These are *not* calendar quarters. The two quarterly financial
  charts use a separate calendar-quarter contract.
- Bars cover **Revenue, Orders, Cost, Discounts and Gross Profit** where
  data permits comparison. Gross Margin is deliberately shown in a separate
  text strip as **percentage-point change**, not as a relative percent bar.

## Exact bar semantics

For each comparable metric with a non-zero previous baseline:

```text
change_percent = (current - previous) / abs(previous) × 100
```

Labels display the engine's rounded percentage change and the previous,
current and absolute change amounts. Bar lengths are proportional to the
largest absolute percentage change present **within the uploaded dataset**.
They do **not** represent currency amounts, universal risk, urgency, or the
confidence of a diagnosis. Up/down direction is *descriptive*, not a
judgment of business benefit: increasing cost may be negative even when
revenue increases.

If the previous value is zero, the percentage is **unknown** and no
percentage-change bar is shown. Its absolute change and both observed
period values remain visible. Missing required financial fields are omitted
from the signal rather than filled with invented zeros.

The frontend rejects structurally invalid or non-finite observations and
provides explicit no-comparison messaging. A readable data list accompanies
all bars; color is not the only carrier of meaning.

## Test and review gates

The tests in `tests/changes/test_observed_signals_contract.py` protect
the baseline formula, zero-baseline unknowns, gross margin percentage-point
change, suppression of absent costs and full-analysis consistency.
Financial golden fixtures continue to verify business invariants.

V1 improvement tasks include a quarter-on-quarter comparison
mode, explicit transaction currency handling and diagnosis-specific
signal weighting. Until then, the chart must continue to label
midpoint comparisons honestly.
