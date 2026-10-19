"""UTC calendar-quarter sales aggregation for deterministic V1 chart data."""

import pandas as pd


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
        revenue = float(records["revenue"].sum())
        cost = float(records["cost"].sum()) if "cost" in records.columns else None
        discount = (
            float(records["discount"].sum())
            if "discount" in records.columns
            else 0.0
        )
        profit = revenue - cost if cost is not None else None
        margin = (
            profit / revenue * 100
            if profit is not None and revenue > 0
            else None
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
                "revenue": round(revenue, 2),
                "cost": round(cost, 2) if cost is not None else None,
                "gross_profit": round(profit, 2) if profit is not None else None,
                "gross_margin": round(margin, 2) if margin is not None else None,
                "discount": round(discount, 2),
                "orders": orders,
                "aov": round(revenue / orders, 2) if orders else None,
            }
        )

    return result
