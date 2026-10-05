def detect_revenue_up_profit_down(period_comparison: dict) -> dict | None:
    previous = period_comparison.get("previous", {})
    current = period_comparison.get("current", {})

    previous_revenue = previous.get("revenue")
    current_revenue = current.get("revenue")
    previous_profit = previous.get("gross_profit")
    current_profit = current.get("gross_profit")

    if (
        previous_revenue is None
        or current_revenue is None
        or previous_profit is None
        or current_profit is None
    ):
        return None

    if current_revenue <= previous_revenue:
        return None

    if current_profit >= previous_profit:
        return None

    revenue_change = current_revenue - previous_revenue
    profit_change = current_profit - previous_profit

    revenue_change_percent = (
        revenue_change / previous_revenue * 100
        if previous_revenue > 0
        else None
    )

    profit_change_percent = (
        profit_change / previous_profit * 100
        if previous_profit > 0
        else None
    )

    return {
        "diagnosis": "Revenue Up / Profit Down",
        "severity": "high",
        "previous_revenue": previous_revenue,
        "current_revenue": current_revenue,
        "revenue_change": round(revenue_change, 2),
        "revenue_change_percent": round(revenue_change_percent, 2)
        if revenue_change_percent is not None
        else None,
        "previous_profit": previous_profit,
        "current_profit": current_profit,
        "profit_change": round(profit_change, 2),
        "profit_change_percent": round(profit_change_percent, 2)
        if profit_change_percent is not None
        else None,
        "evidence": {
            "previous_revenue": previous_revenue,
            "current_revenue": current_revenue,
            "previous_profit": previous_profit,
            "current_profit": current_profit,
        },
        "explanation": (
            f"Revenue increased from {previous_revenue:.2f} "
            f"to {current_revenue:.2f}, while gross profit "
            f"fell from {previous_profit:.2f} "
            f"to {current_profit:.2f}."
        ),
        "recommended_action": (
            "Investigate rising product costs, discounting, "
            "and changes in product mix to identify why higher "
            "sales are producing lower profit."
        ),
        "confidence": "medium",
    }
