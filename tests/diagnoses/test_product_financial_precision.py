"""Golden product-finance invariants independent of rounded display values."""

import pandas as pd
import pytest

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService
from core.diagnoses.high_revenue_low_profit_product import (
    detect_high_revenue_low_profit_product,
)
from core.metrics.engine import analyze_dataframe

PRODUCT_DIAGNOSIS = "High Revenue / Low Profit Product"


def detect(frame: pd.DataFrame) -> list[dict]:
    return detect_high_revenue_low_profit_product(frame)


def test_multiline_product_cents_and_evidence_match_global_totals() -> None:
    frame = pd.DataFrame(
        {
            "order_id": ["A", "A", "B"],
            "product_id": [" P1 ", "P1", "P2"],
            "revenue": ["0.10", "0.20", "0.30"],
            "cost": ["0.10", "0.19", "0.15"],
        }
    )
    original = frame.copy(deep=True)

    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(frame)
    diagnoses = [item for item in result["diagnoses"] if item["diagnosis"] == PRODUCT_DIAGNOSIS]

    assert len(diagnoses) == 1
    product = diagnoses[0]
    assert product["product_id"] == "P1"
    assert product["revenue"] == 0.30
    assert product["cost"] == 0.29
    assert product["gross_profit"] == 0.01
    assert product["gross_margin"] == 3.33
    assert product["revenue_share"] == 50.0
    for key in ("revenue", "gross_profit", "gross_margin", "revenue_share"):
        assert product["evidence"][key] == product[key]

    assert result["analysis"]["metrics"]["revenue"] == 0.60
    assert result["analysis"]["metrics"]["cost"] == 0.44
    assert result["analysis"]["metrics"]["gross_profit"] == 0.16
    assert result["analysis"]["metrics"]["orders"] == 2
    assert result["business_report"]["diagnoses"][0] == product
    pd.testing.assert_frame_equal(frame, original)


def test_rounded_margin_display_cannot_trigger_false_threshold_positive() -> None:
    # Both ratios display as 15.00%, but only B is *below* 15% unrounded.
    frame = pd.DataFrame(
        {
            "product_id": ["A", "B"],
            "revenue": ["20000.00", "20000.00"],
            "cost": ["16999.99", "17000.01"],
        }
    )

    results = detect(frame)

    assert len(results) == 1
    assert results[0]["product_id"] == "B"
    assert results[0]["gross_margin"] == 15.0


def test_rounded_revenue_share_cannot_trigger_false_threshold_positive() -> None:
    # Both A and B display as 20.00%; only B has at least 20% in exact cents.
    frame = pd.DataFrame(
        {
            "product_id": ["A", "B", "C"],
            "revenue": ["3999.99", "4000.01", "12000.00"],
            "cost": ["3999.99", "4000.01", "10000.00"],
        }
    )

    results = detect(frame)

    assert len(results) == 1
    assert results[0]["product_id"] == "B"
    assert results[0]["revenue_share"] == 20.0


def test_exact_threshold_equality_is_inclusive() -> None:
    frame = pd.DataFrame(
        {
            "product_id": ["A", "B"],
            "revenue": ["200.00", "800.00"],
            "cost": ["170.00", "600.00"],
        }
    )

    result = detect(frame)
    assert [item["product_id"] for item in result] == ["A"]
    assert result[0]["gross_margin"] == 15.0
    assert result[0]["revenue_share"] == 20.0


def test_many_cent_sized_lines_do_not_accumulate_float_drift() -> None:
    frame = pd.DataFrame(
        {
            "product_id": ["A"] * 1_000,
            "revenue": ["0.01"] * 1_000,
            "cost": ["0.01"] * 999 + ["0.00"],
        }
    )

    result = detect(frame)

    assert len(result) == 1
    assert result[0]["revenue"] == 10.0
    assert result[0]["cost"] == 9.99
    assert result[0]["gross_profit"] == 0.01
    assert result[0]["gross_margin"] == 0.1
    assert result[0]["revenue_share"] == 100.0


@pytest.mark.parametrize("invalid_id", [None, "", "   "])
def test_product_identity_fails_closed_even_without_cost(invalid_id: object) -> None:
    frame = pd.DataFrame(
        {"product_id": ["A", invalid_id], "revenue": ["10.00", "30.00"]}
    )

    with pytest.raises(ValueError, match="product_id"):
        analyze_dataframe(frame)


def test_direct_detector_rejects_missing_product_key() -> None:
    frame = pd.DataFrame(
        {"product_id": ["A", None], "revenue": [50, 50], "cost": [50, 50]}
    )
    with pytest.raises(ValueError, match="product_id"):
        detect(frame)


def test_invalid_subcent_money_rejected_even_for_direct_detector() -> None:
    frame = pd.DataFrame(
        {"product_id": ["A"], "revenue": ["0.001"], "cost": ["0.00"]}
    )
    with pytest.raises(ValueError, match="Column 'revenue'"):
        detect(frame)


@pytest.mark.parametrize("threshold", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_detection_thresholds_are_rejected(threshold: float) -> None:
    frame = pd.DataFrame(
        {"product_id": ["A"], "revenue": [100], "cost": [90]}
    )
    with pytest.raises(ValueError, match="finite ratio"):
        detect_high_revenue_low_profit_product(frame, revenue_threshold=threshold)


def test_missing_product_or_cost_columns_do_not_fabricate_diagnoses() -> None:
    assert detect(pd.DataFrame({"revenue": [100], "cost": [90]})) == []
    assert detect(pd.DataFrame({"product_id": ["A"], "revenue": [100]})) == []


def test_zero_or_negative_net_revenue_products_are_not_flagged() -> None:
    frame = pd.DataFrame(
        {
            "product_id": ["A", "B", "C"],
            "revenue": ["0.00", "-5.00", "10.00"],
            "cost": ["4.00", "0.00", "10.00"],
        }
    )
    result = detect(frame)
    assert [item["product_id"] for item in result] == ["C"]


def test_product_order_and_evidence_are_independent_of_row_order() -> None:
    frame = pd.DataFrame(
        {
            "product_id": ["C", "B", "A", "B", "C"],
            "revenue": ["15.00", "20.00", "25.00", "10.00", "30.00"],
            "cost": ["14.00", "20.00", "25.00", "10.00", "30.00"],
        }
    )
    shuffled = frame.sample(frac=1, random_state=4).reset_index(drop=True)
    assert detect(frame) == detect(shuffled)
