from dataclasses import dataclass

import pandas as pd


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
        if column in frame.columns:
            frame[column] = _reject_invalid(frame[column], column)

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

    revenue = float(df["revenue"].sum())
    orders = _count_orders(df, basis)

    cost = (
        float(df["cost"].sum())
        if "cost" in df.columns
        else None
    )

    discount = (
        float(df["discount"].sum())
        if "discount" in df.columns
        else 0.0
    )

    gross_profit = (
        revenue - cost
        if cost is not None
        else None
    )

    gross_margin = (
        gross_profit / revenue
        if cost is not None and revenue > 0
        else None
    )

    aov = (
        revenue / orders
        if orders > 0
        else 0
    )

    result = {
        "rows": len(df),
        "columns": list(df.columns),
        "metrics": {
            "revenue": round(revenue, 2),
            "orders": orders,
            "cost": round(cost, 2)
            if cost is not None else None,
            "gross_profit": round(gross_profit, 2)
            if gross_profit is not None else None,
            "gross_margin": round(gross_margin * 100, 2)
            if gross_margin is not None else None,
            "discount": round(discount, 2),
            "aov": round(aov, 2),
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
        },
    }

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
                period_revenue = float(
                    period_df["revenue"].sum()
                )

                period_discount = (
                    float(period_df["discount"].sum())
                    if "discount" in period_df.columns
                    else None
                )

                period_cost = (
                    float(period_df["cost"].sum())
                    if "cost" in period_df.columns
                    else None
                )

                period_profit = (
                    period_revenue - period_cost
                    if period_cost is not None
                    else None
                )

                period_margin = (
                    period_profit / period_revenue * 100
                    if period_profit is not None
                    and period_revenue > 0
                    else None
                )

                return {
                    "revenue": round(period_revenue, 2),
                    "discount": (
                        round(period_discount, 2)
                        if period_discount is not None
                        else None
                    ),
                    "orders": _count_orders(period_df, basis),
                    "cost": (
                        round(period_cost, 2)
                        if period_cost is not None
                        else None
                    ),
                    "gross_profit": (
                        round(period_profit, 2)
                        if period_profit is not None
                        else None
                    ),
                    "gross_margin": (
                        round(period_margin, 2)
                        if period_margin is not None
                        else None
                    ),
                }

            previous_metrics = period_metrics(previous)
            current_metrics = period_metrics(current)

            result["period_comparison"] = {
                "previous": previous_metrics,
                "current": current_metrics,
            }

    return result
