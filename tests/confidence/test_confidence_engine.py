"""Golden invariants for evidential confidence and business severity separation."""

import pandas as pd
import pytest

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService
from core.confidence.engine import calculate_confidence
from core.ranking.priority import calculate_urgency


def analysis(orders: int = 30, *, rows: int = 90, basis: str = "order_id") -> dict:
    return {
        "rows": rows,
        "metrics": {"orders": orders},
        "data_quality": {
            "missing_values": 0,
            "has_cost": True,
            "has_discount": True,
            "order_count_basis": basis,
        },
    }


def diagnosis(severity: str = "medium", *, evidence: dict | None = None) -> dict:
    return {
        "diagnosis": "Margin Decline",
        "severity": severity,
        "evidence": {"margin_change_points": -11.3} if evidence is None else evidence,
    }


@pytest.mark.parametrize("severity", ["low", "medium", "high", "critical"])
def test_severity_cannot_boost_or_reduce_evidential_confidence(severity: str) -> None:
    expected = calculate_confidence(diagnosis("medium"), analysis())

    observed = calculate_confidence(diagnosis(severity), analysis())

    assert observed == expected
    assert observed["score"] == 0.85
    assert observed["confidence"] == "high"


def test_severity_still_controls_business_urgency_separately() -> None:
    assert calculate_urgency(diagnosis("high")) > calculate_urgency(diagnosis("low"))


def test_repeated_line_items_cannot_fake_a_large_order_sample() -> None:
    few_orders = analysis(1, rows=1000)
    one_row = analysis(1, rows=1)

    observed = calculate_confidence(diagnosis(), few_orders)

    assert observed == calculate_confidence(diagnosis(), one_row)
    assert observed["score"] == 0.75
    assert "Small dataset" in " ".join(observed["limitations"])


def test_100_distinct_orders_merit_the_defined_sample_bonus() -> None:
    assert calculate_confidence(diagnosis(), analysis(100))["score"] == 0.90
    assert calculate_confidence(diagnosis(), analysis(20))["score"] == 0.85
    assert calculate_confidence(diagnosis(), analysis(19))["score"] == 0.75


@pytest.mark.parametrize("evidence", [{}, {"context": "vague"}, {"ratio": float("nan")}])
def test_missing_quantitative_evidence_caps_confidence_to_low(evidence: dict) -> None:
    result = calculate_confidence(diagnosis("high", evidence=evidence), analysis(500))
    assert result["score"] == 0.59
    assert result["confidence"] == "low"
    assert any("quantitative" in item for item in result["limitations"])


def test_zero_is_a_valid_numeric_evidence_value() -> None:
    result = calculate_confidence(diagnosis(evidence={"change": 0}), analysis())
    assert result["score"] == 0.85


def test_row_count_fallback_does_not_claim_independent_order_sample() -> None:
    result = calculate_confidence(diagnosis(), analysis(500, rows=500, basis="row"))
    assert result["score"] == 0.75
    assert any("unverified" in item for item in result["limitations"])


def test_unverified_completeness_does_not_earn_a_bonus() -> None:
    case = analysis()
    del case["data_quality"]["missing_values"]
    result = calculate_confidence(diagnosis(), case)
    assert result["score"] == 0.75
    assert any("completeness" in item for item in result["limitations"])


def test_missing_cost_and_incomplete_data_are_explained() -> None:
    case = analysis(40)
    case["data_quality"].update({"missing_values": 3, "has_cost": False})
    result = calculate_confidence(diagnosis(), case)
    assert result["score"] == 0.65
    assert "Cost data is missing." in result["limitations"]
    assert "Dataset contains missing values." in result["limitations"]


def test_analysis_service_propagates_confidence_to_evidence() -> None:
    frame = pd.DataFrame(
        {
            "order_id": ["A", "B"],
            "product_id": ["P1", "P2"],
            "revenue": [300, 30],
            "cost": [290, 10],
        }
    )

    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(frame)

    assert result["diagnoses"]
    for item in result["diagnoses"]:
        independent = calculate_confidence(item, result["analysis"])
        assert independent["score"] == item["confidence_score"]
        assert independent["confidence"] == item["confidence"]
        assert item["evidence"]["confidence_score"] == independent["score"]
