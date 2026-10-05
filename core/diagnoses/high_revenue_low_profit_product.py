def detect_high_revenue_low_profit_product(
    df,
    revenue_threshold=0.20,
    margin_threshold=0.15,
):
    required_columns = {
        "product_id",
        "revenue",
        "cost",
    }

    if not required_columns.issubset(df.columns):
        return []

    product_data = (
        df.groupby("product_id")
        .agg(
            revenue=("revenue", "sum"),
            cost=("cost", "sum"),
        )
        .reset_index()
    )

    product_data["gross_profit"] = (
        product_data["revenue"]
        - product_data["cost"]
    )

    product_data["gross_margin"] = (
        product_data["gross_profit"]
        / product_data["revenue"]
    )

    total_revenue = product_data["revenue"].sum()

    if total_revenue <= 0:
        return []

    product_data["revenue_share"] = (
        product_data["revenue"]
        / total_revenue
    )

    candidates = product_data[
        (product_data["revenue_share"] >= revenue_threshold)
        & (product_data["gross_margin"] <= margin_threshold)
    ].copy()

    diagnoses = []

    for _, product in candidates.iterrows():

        diagnoses.append({
            "diagnosis": "High Revenue / Low Profit Product",
            "product_id": product["product_id"],
            "revenue": round(product["revenue"], 2),
            "cost": round(product["cost"], 2),
            "gross_profit": round(product["gross_profit"], 2),
            "gross_margin": round(
                product["gross_margin"] * 100, 2
            ),
            "revenue_share": round(
                product["revenue_share"] * 100, 2
            ),
            "severity": "high",
            "evidence": {
                "revenue": round(product["revenue"], 2),
                "gross_profit": round(
                    product["gross_profit"], 2
                ),
                "gross_margin": round(
                    product["gross_margin"] * 100, 2
                ),
                "revenue_share": round(
                    product["revenue_share"] * 100, 2
                ),
            },
            "explanation": (
                f"Product {product['product_id']} "
                f"generates {product['revenue']:.2f} in revenue "
                f"but has only "
                f"{product['gross_margin'] * 100:.2f}% gross margin."
            ),
            "recommended_action": (
                "Review this product's pricing, cost structure, "
                "and discounting before increasing its sales volume."
            ),
            "confidence": "medium",
        })

    return diagnoses