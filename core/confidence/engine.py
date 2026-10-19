"""Deterministic evidence-quality scoring, separate from business severity.

Scores are transparent heuristic categories, NOT calibrated probabilities.
Severity influences urgency elsewhere, never the credibility of evidence.
"""

from math import isfinite
from typing import Any


def _has_quantitative_evidence(diagnosis: dict[str, Any]) -> bool:
    """Require at least one finite numerical fact in structured evidence."""
    evidence = diagnosis.get("evidence")
    return isinstance(evidence, dict) and any(
        isinstance(value, (float, int))
        and not isinstance(value, bool)
        and isfinite(value)
        for value in evidence.values()
    )


def _verified_order_count(analysis: dict[str, Any], limitations: list[str]) -> int:
    """Use distinct verified orders rather than inflated line-item counts."""
    quality = analysis.get("data_quality", {})
    if quality.get("order_count_basis") != "order_id":
        limitations.append(
            "Distinct order sample size is unverified without an order_id column."
        )
        return 0

    orders = analysis.get("metrics", {}).get("orders")
    if isinstance(orders, int) and not isinstance(orders, bool) and orders >= 0:
        return orders

    limitations.append("Verified order count is unavailable.")
    return 0


def calculate_confidence(
    diagnosis: dict[str, Any], analysis: dict[str, Any]
) -> dict[str, Any]:
    """Score reproducible data support, never incident urgency or severity.

    This deliberately conservative V1 rubric awards credit for validated data
    completeness, relevant available columns and distinct order sample size.
    Diagnoses without quantitative evidence cannot exceed the low category.
    """
    score = 0.5
    limitations: list[str] = []

    quality = analysis.get("data_quality", {})

    if quality.get("missing_values") == 0:
        score += 0.1
    elif quality.get("missing_values") is None:
        limitations.append("Data completeness has not been verified.")
    else:
        limitations.append("Dataset contains missing values.")

    if quality.get("has_cost"):
        score += 0.1
    else:
        limitations.append("Cost data is missing.")

    if quality.get("has_discount"):
        score += 0.05

    orders = _verified_order_count(analysis, limitations)
    if orders >= 100:
        score += 0.15
    elif orders >= 20:
        score += 0.1
    elif orders > 0:
        limitations.append("Small dataset: fewer than 20 distinct orders.")

    if not _has_quantitative_evidence(diagnosis):
        limitations.append("Diagnosis lacks quantitative supporting evidence.")
        score = min(score, 0.59)

    score = round(min(score, 1.0), 2)
    if score >= 0.8:
        confidence = "high"
    elif score >= 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score": score,
        "confidence": confidence,
        "limitations": limitations,
    }
