from dataclasses import dataclass

import pandas as pd

from core.metrics.money import as_amount, average, minor_units, percent, sum_minor_units
from core.metrics.quarterly import build_quarterly_trend


@dataclass(frozen=True)
class PreparedSalesData:
    """Validated input shared by metrics and downstream diagnosis engines."""

    frame: pd.DataFrame
    order_count_basis: str


def _reject_invalid(series: pd.Series, column: str) -> pd.Series:
    """Convert a supplied numeric column without concealing invalid values."""
    numeric = pd.to_numeric(series, errors="coerce").astype("float64")
    invalid = numeric.isna() | numeric.isin([float("inf"), float("-inf")])
    if invalid.any():
        first_row = int(invalid.to_numpy().nonzero()[0][0]) + 1
        raise ValueError(
            f"Column '{column}' has a missing, non-numeric, or non-finite "
            f"value at data row {first_row}."
        )
    return numeric


def prepare_sales_dataframe(df: pd.DataFrame) -> PreparedSalesData:
    """Normalize and validate row-level financial facts exactly once.

    A row represents a sales line; when order_id is supplied, unique order
    identifiers—not row counts—represent customer orders.
    """
    frame = df.copy()
    frame.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in frame.columns
    ]

    if not frame.columns.is_unique:
        raise ValueError("Column names must be unique after normalization.")
    if frame.empty:
        raise ValueError("The CSV must contain at least one data row.")
    if "revenue" not in frame.columns:
        raise ValueError("The CSV must contain a revenue column.")

    for column in ("revenue", "cost", "discount", "quantity"):
        if column not in frame.columns:
            continue
        if column == "quantity":
            frame[column] = _reject_invalid(frame[column], column)
        else:
            # Validate the original lexical values BEFORE pandas float coercion.
            # Diagnoses receive only canonical amounts; metrics sum integer cents.
            frame[column] = [
                as_amount(minor_units(value, column, row))
                for row, value in enumerate(frame[column], start=1)
            ]

    if "date" in frame.columns:
        dates = pd.to_datetime(frame["date"], errors="coerce", utc=True)
        if dates.isna().any():
            first_row = int(dates.isna().to_numpy().nonzero()[0][0]) + 1
            raise ValueError(f"Column 'date' has an invalid value at data row {first_row}.")
        frame["date"] = dates

    if "order_id" in frame.columns:
        order_ids = frame["order_id"].astype("string").str.strip()
        if order_ids.isna().any() or order_ids.eq("").any():
            raise ValueError("Column 'order_id' contains a missing or blank identifier.")
        frame["order_id"] = order_ids

        if "date" in frame.columns:
            conflicting_dates = frame.groupby("order_id")["date"].nunique()
            if (conflicting_dates > 1).any():
                raise ValueError("The same order_id cannot have different transaction dates.")
        basis = "order_id"
    else:
        # Older CSVs without an identifier retain explicit row-based estimates.
        basis = "row"

    return PreparedSalesData(frame=frame, order_count_basis=basis)


def _count_orders(frame: pd.DataFrame, basis: str) -> int:
    return int(frame["order_id"].nunique()) if basis == "order_id" else len(frame)


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Public compatibility entry point: validate, then calculate metrics."""
    return analyze_prepared_sales(prepare_sales_dataframe(df))


def analyze_prepared_sales(prepared: PreparedSalesData) -> dict:
    """Compute totals from already-validated, canonical sales rows."""
    df = prepared.frame
    basis = prepared.order_count_basis

    revenue_cents = sum_minor_units(df["revenue"], "revenue")
    orders = _count_orders(df, basis)
    cost_cents = (
        sum_minor_units(df["cost"], "cost")
        if "cost" in df.columns
        else None
    )
    discount_cents = (
        sum_minor_units(df["discount"], "discount")
        if "discount" in df.columns
        else 0
    )
    profit_cents = (
        revenue_cents - cost_cents if cost_cents is not None else None
    )

    result = {
        "rows": len(df),
        "columns": list(df.columns),
        "metrics": {
            "revenue": as_amount(revenue_cents),
            "orders": orders,
            "cost": as_amount(cost_cents)
            if cost_cents is not None else None,
            "gross_profit": as_amount(profit_cents)
            if profit_cents is not None else None,
            "gross_margin": percent(profit_cents, revenue_cents)
            if profit_cents is not None else None,
            "discount": as_amount(discount_cents),
            "aov": average(revenue_cents, orders),
        },
        "data_quality": {
            "missing_values": int(
                df.isna().sum().sum()
            ),
            "duplicate_rows": int(
                df.duplicated().sum()
            ),
            "has_cost": "cost" in df.columns,
            "has_discount": "discount" in df.columns,
            "has_date": "date" in df.columns,
            "order_count_basis": basis,
            "monetary_precision": "two_decimal_minor_units",
            "currency": "unspecified",
        },
    }

    # Calendar-quarter chart data is distinct from legacy midpoint comparison.
    result["quarterly_trend"] = build_quarterly_trend(df, basis)

    # Period comparison
    if "date" in df.columns and df["date"].notna().any():

        dated_df = df.dropna(subset=["date"]).copy()

        min_date = dated_df["date"].min()
        max_date = dated_df["date"].max()

        total_days = (max_date - min_date).days + 1

        if total_days >= 2:

            midpoint = min_date + (
                max_date - min_date
            ) / 2

            previous = dated_df[
                dated_df["date"] < midpoint
            ]

            current = dated_df[
                dated_df["date"] >= midpoint
            ]

            def period_metrics(period_df):
                period_revenue = sum_minor_units(period_df["revenue"], "revenue")
                period_cost = (
                    sum_minor_units(period_df["cost"], "cost")
                    if "cost" in period_df.columns else None
                )
                period_discount = (
                    sum_minor_units(period_df["discount"], "discount")
                    if "discount" in period_df.columns else None
                )
                period_profit = (
                    period_revenue - period_cost
                    if period_cost is not None else None
                )

                return {
                    "revenue": as_amount(period_revenue),
                    "discount": (
                        as_amount(period_discount)
                        if period_discount is not None else None
                    ),
                    "orders": _count_orders(period_df, basis),
                    "cost": (
                        as_amount(period_cost) if period_cost is not None else None
                    ),
                    "gross_profit": (
                        as_amount(period_profit) if period_profit is not None else None
                    ),
                    "gross_margin": (
                        percent(period_profit, period_revenue)
                        if period_profit is not None else None
                    ),
                }

            previous_metrics = period_metrics(previous)
            current_metrics = period_metrics(current)

            result["period_comparison"] = {
                "previous": previous_metrics,
                "current": current_metrics,
            }

    return result
