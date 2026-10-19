# Confidence is evidence support, not business severity

BizLens exposes **two different judgments**. Neither is a calibrated probability.

1. **Severity / urgency** reflects the magnitude or immediacy of a business problem.
   The ranking engine consumes `severity` when calculating urgency.
2. **Confidence** reflects the *support available in the imported data* for a
   diagnosis. It must be deterministic and independent of severity.

This distinction prevents a dramatic signal with weak supporting data from
presenting itself as highly verified.

## Confidence V1 heuristic

The rule in `core/confidence/engine.py` starts at **0.50** and adds:

| Condition | Added score |
| --- | ---: |
| Verified zero missing values | +0.10 |
| A cost column is available | +0.10 |
| A discount column is available | +0.05 |
| At least 20 distinct orders verified by `order_id` | +0.10 |
| At least 100 distinct orders verified by `order_id` | +0.15 **instead of** +0.10 |

No severity bonus is permitted. Row counts are *not* substituted for distinct
orders when `order_id` is missing, because several lines may belong to one
customer order. Such datasets receive an explicit limitation.

A diagnosis must also supply at least one **finite numeric fact** in its
structured `evidence` dictionary. If it does not, its score is capped at
0.59 (low) and the result explicitly explains the limitation.

Final scores are rounded to two decimals, with categories:

- **High**: score >= 0.80
- **Medium**: 0.60 <= score < 0.80
- **Low**: score < 0.60

All scoring conditions are visible in source code and regression tests.
`limitations` is part of the existing structured response contract, passed
through to the diagnosis and evidence payloads.

## Scope and honesty

- This is a deterministic **data-coverage heuristic**, **not** statistical
  certainty, a calibrated probability, or proof that a causal explanation is
  correct. A larger order count does not guarantee independent observations.
- For now the rubric considers dataset-wide column availability, not yet
  diagnosis-specific reliability weighting. Calibrating diagnostic performance
  against labelled ground truth remains a separate future task.
- Confidence must not increase because `severity` changes from low to high;
  ranking can still prioritize a severe problem based on urgency.
- Synthetic/demo fixtures should remain clearly identified.
- Keep tests in `tests/confidence/test_engine.py` synchronized with any
  weight or interpretation change.

## Verification

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m ruff check --no-cache .
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider
```
