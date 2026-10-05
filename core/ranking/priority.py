def calculate_impact(diagnosis: dict) -> float:
    """
    Estimate business impact from the strength of the evidence.

    Impact increases continuously with the magnitude of the
    business signal instead of relying only on fixed categories.
    """

    impact = 1.0

    # Profit deterioration
    profit_change_percent = diagnosis.get(
        "profit_change_percent"
    )

    if profit_change_percent is not None:
        if profit_change_percent < -100:
            impact += 3.0
        elif profit_change_percent < -50:
            impact += 2.5
        elif profit_change_percent < -25:
            impact += 2.0
        elif profit_change_percent < -10:
            impact += 1.5
        elif profit_change_percent < 0:
            impact += 1.0

    # Margin deterioration
    change_points = diagnosis.get("change_points")

    if change_points is not None:
        if change_points <= -15:
            impact += 2.5
        elif change_points <= -10:
            impact += 2.0
        elif change_points <= -5:
            impact += 1.5
        elif change_points < 0:
            impact += 0.75

    # Negative or very low product margin
    gross_margin = diagnosis.get("gross_margin")

    if gross_margin is not None:
        if gross_margin < 0:
            impact += 2.0
        elif gross_margin < 10:
            impact += 1.5
        elif gross_margin < 15:
            impact += 1.0

    # Product concentration
    revenue_share = diagnosis.get("revenue_share")

    if revenue_share is not None:
        if revenue_share >= 40:
            impact += 1.5
        elif revenue_share >= 30:
            impact += 1.0
        elif revenue_share >= 20:
            impact += 0.5

    # Cost pressure relative to the previous period
    cost_change_percent = diagnosis.get(
        "cost_change_percent"
    )

    if cost_change_percent is not None:
        if cost_change_percent >= 100:
            impact += 2.5
        elif cost_change_percent >= 50:
            impact += 2.0
        elif cost_change_percent >= 25:
            impact += 1.0
        elif cost_change_percent >= 10:
            impact += 0.5

    # Discount pressure relative to the previous period
    discount_change_percent = diagnosis.get(
        "discount_change_percent"
    )

    if discount_change_percent is not None:
        if discount_change_percent >= 100:
            impact += 2.0
        elif discount_change_percent >= 50:
            impact += 1.5
        elif discount_change_percent >= 25:
            impact += 1.0
        elif discount_change_percent > 0:
            impact += 0.5

    return round(impact, 2)


def calculate_confidence(diagnosis: dict) -> float:
    """
    Use the confidence score produced by the Confidence Engine.
    Fall back to the legacy mapping only when a score is unavailable.
    """

    confidence_score = diagnosis.get(
        "confidence_score"
    )

    if isinstance(
        confidence_score,
        (int, float)
    ):
        return round(
            max(
                0.0,
                min(
                    1.0,
                    float(confidence_score)
                )
            ),
            2
        )

    confidence = diagnosis.get(
        "confidence",
        "medium"
    )

    return {
        "high": 0.85,
        "medium": 0.70,
        "low": 0.50,
    }.get(confidence, 0.70)


def calculate_urgency(diagnosis: dict) -> float:
    """
    Estimate urgency based on severity and active deterioration.
    """

    severity = diagnosis.get(
        "severity",
        "medium"
    )

    urgency = {
        "high": 1.3,
        "medium": 1.1,
        "low": 0.9,
    }.get(severity, 1.0)

    profit_change = diagnosis.get(
        "profit_change"
    )

    if profit_change is not None and profit_change < 0:
        urgency += 0.2

    gross_margin = diagnosis.get(
        "gross_margin"
    )

    if gross_margin is not None and gross_margin < 0:
        urgency += 0.2

    return round(urgency, 2)


def calculate_priority(diagnosis: dict) -> float:
    """
    Evidence-Based BizLens priority.

    Priority =
        Evidence Impact
        × Confidence
        × Urgency
    """

    impact = calculate_impact(diagnosis)
    confidence = calculate_confidence(diagnosis)
    urgency = calculate_urgency(diagnosis)

    return round(
        impact * confidence * urgency,
        2
    )


def rank_diagnoses(
    diagnoses: list,
    limit: int = 3
) -> list:
    """
    Rank diagnoses by evidence-based business priority.
    """

    ranked = []

    for diagnosis in diagnoses:
        item = diagnosis.copy()

        item["impact_score"] = (
            calculate_impact(diagnosis)
        )

        item["confidence_score"] = (
            calculate_confidence(diagnosis)
        )

        item["urgency_score"] = (
            calculate_urgency(diagnosis)
        )

        item["priority_score"] = (
            calculate_priority(diagnosis)
        )

        ranked.append(item)

    ranked.sort(
        key=lambda item: item["priority_score"],
        reverse=True
    )

    return ranked[:limit]
 
