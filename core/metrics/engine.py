import pandas as pd


def analyze_dataframe(df: pd.DataFrame) -> dict:
    df = df.copy()

    # Normalize column names
    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    # Required field
    if "revenue" not in df.columns:
        raise ValueError("The CSV must contain a revenue column.")

    # Convert numeric fields
    numeric_columns = [
        "revenue",
        "cost",
        "discount",
        "quantity",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    # Convert date when available
    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    revenue = float(df["revenue"].sum())
    orders = len(df)

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
                    "orders": len(period_df),
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
