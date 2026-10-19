# Quarterly trend contract — BizLens V1

The V1 dashboard displays **two charts backed by a single deterministic
quarterly data series**: (1) Revenue vs. Gross Profit and (2) Gross Margin
Trend. The existing "Observed Signals / What Changed" view remains a
*separate* midpoint-period comparison until its own visualization contract is
reviewed. Do not advertise it as quarter-on-quarter movement.

## Source and grain

- Core implementation: `core/metrics/quarterly.py`.
- Output: `analysis.quarterly_trend`, repeated verbatim under
  `business_report.quarterly_trend`. The replay's business-report step
  therefore contains the same data, **not a second calculation**.
- This is **UTC calendar-quarter** aggregation (Jan–Mar, Apr–Jun, Jul–Sep,
  Oct–Dec), not fiscal quarters. `period` includes the year, e.g.
  `2025-Q4`, so cross-year analysis cannot collapse two Q1 values together.
- Only quarters with observed sales lines appear. A quarter without imported
  transactions is **missing, not zero**; the UI never invents its values.
- Without valid dates, the series is the empty list. Invalid supplied dates
  fail closed at import rather than dropping transactions.
- Sales rows represent **line items**. Revenue, cost and discount are additive.
  `orders` count unique order IDs when supplied; otherwise they are a
  row-count estimate as declared by `data_quality.order_count_basis`.
- A single order is required to have one transaction date, so it cannot be
  counted in two quarters.

## Shape of an observed quarter

```json
{
  "period": "2026-Q1",
  "year": 2026,
  "quarter": 1,
  "revenue": 100.0,
  "cost": 40.0,
  "gross_profit": 60.0,
  "gross_margin": 60.0,
  "discount": 5.0,
  "orders": 2,
  "aov": 50.0
}
```

`gross_margin` is **(sum(revenue) − sum(cost)) / sum(revenue) × 100**,
*not* the average of line or product margins. It is `null` when no cost is
supplied or quarterly revenue is nonpositive. `gross_profit` is also `null`
when no cost is supplied.

The V1 user interface renders these figures using responsive SVG and also
publishes an accessible text table with exact output values. Units are
identified as the **source dataset units**: BizLens does not yet infer a
currency, perform FX conversion, or attach a dollar sign to unknown data.

## Compatibility and verification

The existing `analysis.period_comparison` and
`what_changed` remain unchanged: they compare two chronological halves
of the observed date span, not calendar quarters. Existing diagnostic rules
continue to use this V1 midpoint split.

`tests/metrics/test_quarterly_trends.py` covers cross-year ordering,
distinct multiline orders, accounting reconciliation, weighted margins,
missing cost/date behavior, no invented zero margins, invalid date/order
rejection, shuffle invariance, and report/replay agreement.

This milestone does **not** claim exact-cent accounting across very large
datasets, calendar-quarter diagnoses, or fiscal-quarter support. Monetary
precision and currency labeling are separate quality gates.
