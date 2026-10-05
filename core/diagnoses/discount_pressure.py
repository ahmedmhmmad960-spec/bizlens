def detect_discount_pressure(period_comparison: dict) -> dict | None:
    previous = period_comparison.get("previous", {})
    current = period_comparison.get("current", {})

    previous_revenue = previous.get("revenue")
    current_revenue = current.get("revenue")

    previous_discount = previous.get("discount")
    current_discount = current.get("discount")

    previous_profit = previous.get("gross_profit")
    current_profit = current.get("gross_profit")

    if (
        previous_revenue is None
        or current_revenue is None
        or previous_discount is None
        or current_discount is None
        or previous_profit is None
        or current_profit is None
    ):
        return None

    if previous_revenue <= 0 or previous_discount < 0:
        return None

    discount_change = current_discount - previous_discount

    discount_change_percent = (
        discount_change / previous_discount * 100
        if previous_discount > 0
        else None
    )

    revenue_change = current_revenue - previous_revenue

    revenue_change_percent = (
        revenue_change / previous_revenue * 100
    )

    # Need a meaningful increase in discounting
    if discount_change <= 0:
        return None

    # If there was no previous discount, avoid treating
    # the first appearance of a discount as a growth rate.
    if previous_discount == 0:
        return None

    # Discount pressure exists when discounting grows
    # faster than revenue.
    if discount_change_percent <= revenue_change_percent:
        return None

    profit_change = current_profit - previous_profit

    return {
        "diagnosis": "Discount Pressure",
        "severity": (
            "high"
            if discount_change_percent >= 25
            else "medium"
        ),
        "previous_discount": previous_discount,
        "current_discount": current_discount,
        "discount_change": round(discount_change, 2),
        "discount_change_percent": round(
            discount_change_percent, 2
        ),
        "revenue_change_percent": round(
            revenue_change_percent, 2
        ),
        "profit_change": round(
            profit_change, 2
        ),
        "evidence": {
            "previous_discount": previous_discount,
            "current_discount": current_discount,
            "discount_growth_percent": round(
                discount_change_percent, 2
            ),
            "revenue_growth_percent": round(
                revenue_change_percent, 2
            ),
        },
        "explanation": (
            f"Discounting increased from "
            f"{previous_discount:.2f} to "
            f"{current_discount:.2f}, growing "
            f"{discount_change_percent:.2f}% compared with "
            f"{revenue_change_percent:.2f}% revenue growth."
        ),
        "recommended_action": (
            "Review discount levels, promotional campaigns, "
            "and product pricing to determine whether discounts "
            "are reducing profitability without generating "
            "proportional revenue growth."
        ),
        "confidence": "medium",
    }
