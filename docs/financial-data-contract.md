# Financial data contract (V1)

This contract is part of the deterministic, evidence-first BizLens core. It
defines what an input row means, how an order is counted, and which errors
must block a financial report. Keep it aligned with
`core/metrics/engine.py` and the executable regression tests.

## Grain and counting

- **Each CSV row is one sales line**, not necessarily one customer order.
  Line-level `revenue`, `cost`, and `discount` are summed across rows.
- When `order_id` exists, **orders = number of distinct nonblank order IDs**;
  AOV = sum of line revenues / distinct orders. Multiple products in one order
  are counted as one order. The `date` of every line in the same order must
  agree, so period-level order counts do not count one order in two periods.
- For legacy datasets with **no `order_id` column**, retain the row-count
  estimate, and expose `data_quality.order_count_basis = "row"`. This is an
  *estimate*, not evidence that each row is a separate customer order.
- With an order identifier, the basis is
  `data_quality.order_count_basis = "order_id"`. `rows` always describes
  the actual number of input records.
- Exact duplicate input rows are reported under `duplicate_rows`, but are
  **not silently removed**. Disambiguating duplicate exports from genuine
  repeated line items requires a separate line-item identity rule.

## Validation and explicit failure

- `revenue` is required. An empty dataset fails before producing a report.
- Any **present** numeric field (`revenue`, `cost`, `discount`,
  `quantity`) must be finite and numeric on every row. Missing, invalid,
  or infinite values are rejected with a named column and data-row position.
  Missing *columns* remain optional except for `revenue`; e.g. no `cost`
  means gross profit/margin are unknown rather than zero.
- A present `date` must be parseable for **every** row; we will not
  silently drop invalid dates from a period comparison.
- A present `order_id` must be nonblank on every row. IDs are normalized
  to trimmed strings to preserve identifiers as categorical keys.
- Column names are normalized consistently; two source columns that
  normalize to the same name cause a validation error.
- Negative revenue/cost values are **not silently changed**. Whether they
  represent returns, refunds, or adjustments must be established by a future
  source-specific contract; the engine currently sums them as supplied.
- Input frames are copied before normalization and remain unchanged.

## Calculation and diagnosis boundaries

- Metrics and product diagnoses consume the **same validated numeric rows**,
  so string-numeric CSV inputs cannot produce one figure in the metrics
  engine and a different figure in product diagnosis.
- Existing period grouping remains a chronological midpoint split between
  the earliest and latest dates, **not a calendar quarter**. Quarterly
  reporting requires its own explicit date-grain implementation.
- **V1 currency-agnostic two-decimal contract:** Every *present* monetary
  value in `revenue`, `cost` and `discount` must be an exact multiple of
  0.01. Missing, non-finite or sub-cent values (e.g. `1.005`) are rejected
  before numeric coercion. The engine does **not** silently round imported
  amounts or invent cents.
- Totals and period/quarter amounts accumulate in **integer minor units**.
  Conversion back to JSON numbers happens only at the output boundary for
  compatibility. Gross margins and AOV are computed from those integer
  totals using Decimal and explicit ROUND_HALF_UP at two decimals.
- `data_quality.monetary_precision` records `two_decimal_minor_units` and
  `data_quality.currency` records `unspecified`. **No currency conversion,
  exchange-rate lookup, symbol or ISO 4217 claim** is made without an
  explicit source currency. V1 does not support currencies with other
  minor-unit scales (such as 0-decimal currencies) as financial-grade output.
- The current numeric JSON API has a safety limit of 10^13 minor units per
  row and per aggregated input field, to avoid falsely implying cent-level
  precision after conversion to floats in client code. Values exceeding the
  limit are rejected with a clear import error rather than distorted.
- **Product diagnosis now uses exact minor-unit sums**, sharing the
  `core.metrics.money` primitives with global, midpoint and quarterly
  financial metrics. A present `product_id` must be nonblank on every sales
  line and is normalized to trimmed string identifiers. A missing
  `product_id` *column* remains optional, so product-specific diagnoses are
  simply unavailable if the dataset has no product identifiers.
- Product revenue share and gross margin are compared against the configured
  thresholds using **unrounded integer-cent ratios**. Displayed percentages
  are rounded only after the inclusion decision; two products both displaying
  15.00% may legitimately fall on different sides of the actual threshold.
  This prevents misleading false positive or false negative diagnoses.
- A product with nonpositive net revenue has no meaningful positive-revenue
  margin and is excluded from this particular diagnosis. When returns reduce
  other products' revenue, an individual product's share of **net** total
  revenue can exceed 100%: this is a mathematical consequence, not a
  conventional market-share claim.
- The FastAPI CSV boundary now reads columns as **source strings**
  before validation, preserving leading zeros in order/product identifiers
  and preventing binary-float parsing from erasing unsupported fractional
  cents. This protects HTTP CSV imports; direct pandas DataFrame callers
  must themselves preserve identifiers and decimal lexemes before calling
  the analysis service.
- This is **not** tax-grade accounting certification. Currency codes,
  returns/refunds, tax conventions, the treatment of ID-shaped CSV
  missing-value sentinels, and multi-currency imports remain explicit
  future contracts. Product share is *share of net sales in this import*,
  not externally verified market share.
- Fail-closed validation is deliberate: the API should communicate a useful
  import error instead of presenting misleading zeroes or partial totals.

## Verification

```bash
python3 -B -m ruff check --no-cache .
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider
```

Key regressions live in `tests/metrics/test_financial_integrity.py`. The
integration test specifically confirms that product diagnoses use numeric
facts prepared by the same validation boundary as global metrics.
