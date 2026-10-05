def detect_margin_decline(period_comparison: dict) -> dict | None:
    previous = period_comparison.get("previous", {})
    current = period_comparison.get("current", {})

    previous_margin = previous.get("gross_margin")
    current_margin = current.get("gross_margin")

    if previous_margin is None or current_margin is None:
        return None

    margin_change = current_margin - previous_margin

    # No meaningful decline
    if margin_change >= -3:
        return None

    return {
        "diagnosis": "Margin Decline",
        "severity": "high" if margin_change <= -10 else "medium",
        "previous_margin": previous_margin,
        "current_margin": current_margin,
        "change_points": round(margin_change, 2),
        "evidence": {
            "previous_gross_margin": previous_margin,
            "current_gross_margin": current_margin,
            "margin_change_points": round(margin_change, 2),
        },
        "explanation": (
            f"Gross margin fell from "
            f"{previous_margin:.2f}% to "
            f"{current_margin:.2f}%."
        ),
        "recommended_action": (
            "Review product costs, pricing, and discounting "
            "to identify the main drivers of the margin decline."
        ),
        "confidence": "medium",
    }
