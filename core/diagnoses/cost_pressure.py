def detect_cost_pressure(period_comparison: dict) -> dict | None:
    previous = period_comparison.get("previous", {})
    current = period_comparison.get("current", {})

    previous_revenue = previous.get("revenue")
    current_revenue = current.get("revenue")
    previous_cost = previous.get("cost")
    current_cost = current.get("cost")
    previous_profit = previous.get("gross_profit")
    current_profit = current.get("gross_profit")

    if (
        previous_revenue is None
        or current_revenue is None
        or previous_cost is None
        or current_cost is None
        or previous_profit is None
        or current_profit is None
    ):
        return None

    if previous_cost <= 0 or previous_revenue <= 0:
        return None

    cost_change = current_cost - previous_cost
    cost_change_percent = cost_change / previous_cost * 100

    revenue_change = current_revenue - previous_revenue
    revenue_change_percent = revenue_change / previous_revenue * 100

    if cost_change_percent < 10:
        return None

    if cost_change_percent <= revenue_change_percent:
        return None

    profit_change = current_profit - previous_profit

    return {
        "diagnosis": "Cost Pressure",
        "severity": (
            "high"
            if cost_change_percent >= 25
            else "medium"
        ),
        "previous_cost": previous_cost,
        "current_cost": current_cost,
        "cost_change": round(cost_change, 2),
        "cost_change_percent": round(cost_change_percent, 2),
        "revenue_change_percent": round(
            revenue_change_percent, 2
        ),
        "profit_change": round(profit_change, 2),
        "evidence": {
            "previous_cost": previous_cost,
            "current_cost": current_cost,
            "cost_growth_percent": round(
                cost_change_percent, 2
            ),
            "revenue_growth_percent": round(
                revenue_change_percent, 2
            ),
        },
        "explanation": (
            f"Costs increased from {previous_cost:.2f} "
            f"to {current_cost:.2f}, growing "
            f"{cost_change_percent:.2f}% compared with "
            f"{revenue_change_percent:.2f}% revenue growth."
        ),
        "recommended_action": (
            "Review supplier costs, product margins, "
            "pricing, and the product mix to identify "
            "the main sources of cost pressure."
        ),
        "confidence": "medium",
    }
