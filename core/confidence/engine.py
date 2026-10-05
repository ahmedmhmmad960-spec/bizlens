def calculate_confidence(diagnosis, analysis):
    score = 0.5
    limitations = []

    data_quality = analysis.get(
        "data_quality", {}
    )

    metrics = analysis.get(
        "metrics", {}
    )

    # Data completeness
    if data_quality.get(
        "missing_values", 0
    ) == 0:
        score += 0.1
    else:
        limitations.append(
            "Dataset contains missing values."
        )

    # Cost data
    if data_quality.get("has_cost"):
        score += 0.1
    else:
        limitations.append(
            "Cost data is missing."
        )

    # Discount data
    if data_quality.get(
        "has_discount"
    ):
        score += 0.05

    # Dataset size
    rows = analysis.get("rows", 0)

    if rows >= 100:
        score += 0.15
    elif rows >= 20:
        score += 0.1
    elif rows < 10:
        limitations.append(
            "Small dataset."
        )

    # Strong signals
    severity = diagnosis.get(
        "severity"
    )

    if severity == "high":
        score += 0.1

    score = min(score, 1.0)

    if score >= 0.8:
        confidence = "high"
    elif score >= 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score": round(score, 2),
        "confidence": confidence,
        "limitations": limitations,
    }
