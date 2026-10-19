"""Product-level diagnosis using the same exact-cent facts as global metrics."""

from decimal import Decimal, InvalidOperation

import pandas as pd

from core.metrics.money import as_amount, percent, sum_minor_units


def _validated_threshold(value: float, name: str) -> Decimal:
    """Require a finite ratio between zero and one, with exact comparisons."""
    try:
        ratio = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{name} must be a finite ratio between 0 and 1.") from error
    if not ratio.is_finite() or not Decimal(0) <= ratio <= Decimal(1):
        raise ValueError(f"{name} must be a finite ratio between 0 and 1.")
    return ratio


def detect_high_revenue_low_profit_product(
    df: pd.DataFrame,
    revenue_threshold: float = 0.20,
    margin_threshold: float = 0.15,
) -> list[dict]:
    """Flag material products with weak margins, without floating-point sums.

    Each row is a sales line; net product amounts are exact integer minor
    units. The revenue-share and margin thresholds are compared *before*
    rounding any percentages for human-readable output.
    """
    required_columns = {"product_id", "revenue", "cost"}
    if not required_columns.issubset(df.columns):
        return []

    minimum_share = _validated_threshold(revenue_threshold, "revenue_threshold")
    maximum_margin = _validated_threshold(margin_threshold, "margin_threshold")

    # The detector also supports direct calls outside AnalysisService.
    # Never silently lose the revenue of a row with a blank product key.
    product_ids = df["product_id"].astype("string").str.strip()
    if product_ids.isna().any() or product_ids.eq("").any():
        raise ValueError("Column 'product_id' contains a missing or blank identifier.")

    total_revenue_cents = sum_minor_units(df["revenue"], "revenue")
    if total_revenue_cents <= 0:
        return []

    diagnoses = []
    for product_id, lines in df.groupby(product_ids, sort=True):
        revenue_cents = sum_minor_units(lines["revenue"], "revenue")
        cost_cents = sum_minor_units(lines["cost"], "cost")
        if revenue_cents <= 0:
            # A zero/negative net revenue does not define a meaningful
            # positive-revenue product margin or share.
            continue

        profit_cents = revenue_cents - cost_cents
        if Decimal(revenue_cents) < minimum_share * total_revenue_cents:
            continue
        if Decimal(profit_cents) > maximum_margin * revenue_cents:
            continue

        revenue = as_amount(revenue_cents)
        cost = as_amount(cost_cents)
        gross_profit = as_amount(profit_cents)
        gross_margin = percent(profit_cents, revenue_cents)
        revenue_share = percent(revenue_cents, total_revenue_cents)

        diagnoses.append(
            {
                "diagnosis": "High Revenue / Low Profit Product",
                "product_id": str(product_id),
                "revenue": revenue,
                "cost": cost,
                "gross_profit": gross_profit,
                "gross_margin": gross_margin,
                "revenue_share": revenue_share,
                "severity": "high",
                "evidence": {
                    "revenue": revenue,
                    "gross_profit": gross_profit,
                    "gross_margin": gross_margin,
                    "revenue_share": revenue_share,
                },
                "explanation": (
                    f"Product {product_id} generates {revenue:.2f} in revenue "
                    f"but has only {gross_margin:.2f}% gross margin."
                ),
                "recommended_action": (
                    "Review this product's pricing, cost structure, "
                    "and discounting before increasing its sales volume."
                ),
                "confidence": "medium",
            }
        )
    return diagnoses
