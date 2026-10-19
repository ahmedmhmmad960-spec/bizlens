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
- The current engine sums using floating-point arithmetic and rounds the
  presented metrics to two decimals. Currency-specific minor-unit precision
  and an explicit currency column should be addressed before financial-grade
  production accounting claims.
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
