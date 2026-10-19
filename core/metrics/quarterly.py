"""UTC calendar-quarter sales aggregation for deterministic V1 chart data."""

import pandas as pd

from core.metrics.money import as_amount, average, percent, sum_minor_units


def build_quarterly_trend(frame: pd.DataFrame, order_count_basis: str) -> list[dict]:
    """Return only observed calendar quarters in chronological order.

    Revenue, cost and discount belong to sales *lines*. Orders are distinct
    order IDs when available, and otherwise are labeled row-based estimates
    at the enclosing analysis boundary. Each order must have one transaction
    date (enforced by the shared ingestion boundary).
    """
    if "date" not in frame.columns:
        return []

    quarter_keys = [frame["date"].dt.year, frame["date"].dt.quarter]
    result = []
    for (year, quarter), records in frame.groupby(quarter_keys, sort=True):
        revenue_cents = sum_minor_units(records["revenue"], "revenue")
        cost_cents = (
            sum_minor_units(records["cost"], "cost")
            if "cost" in records.columns else None
        )
        discount_cents = (
            sum_minor_units(records["discount"], "discount")
            if "discount" in records.columns else 0
        )
        profit_cents = (
            revenue_cents - cost_cents if cost_cents is not None else None
        )
        orders = (
            int(records["order_id"].nunique())
            if order_count_basis == "order_id"
            else len(records)
        )

        result.append(
            {
                "period": f"{int(year)}-Q{int(quarter)}",
                "year": int(year),
                "quarter": int(quarter),
                "revenue": as_amount(revenue_cents),
                "cost": as_amount(cost_cents) if cost_cents is not None else None,
                "gross_profit": as_amount(profit_cents)
                if profit_cents is not None else None,
                "gross_margin": percent(profit_cents, revenue_cents)
                if profit_cents is not None else None,
                "discount": as_amount(discount_cents),
                "orders": orders,
                "aov": average(revenue_cents, orders),
            }
        )

    return result
