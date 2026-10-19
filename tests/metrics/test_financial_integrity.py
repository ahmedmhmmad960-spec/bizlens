"""Regression tests for the financial-facts contract and order grain."""

import pandas as pd
import pytest

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService
from core.metrics.engine import analyze_dataframe


def test_line_items_keep_revenue_but_count_distinct_orders() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["A", "A", "B", "C"],
            "date": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-03"],
            "revenue": [100, 50, 200, 90],
            "cost": [60, 20, 100, 40],
        }
    )

    result = analyze_dataframe(df)
    metrics = result["metrics"]
    comparison = result["period_comparison"]

    assert result["rows"] == 4
    assert metrics["revenue"] == 440
    assert metrics["orders"] == 3
    assert metrics["aov"] == pytest.approx(146.67, abs=0.01)
    assert result["data_quality"]["order_count_basis"] == "order_id"
    assert comparison["previous"]["revenue"] == 150
    assert comparison["current"]["revenue"] == 290
    assert comparison["previous"]["orders"] == 1
    assert comparison["current"]["orders"] == 2


def test_legacy_csv_without_order_id_declares_row_count_basis() -> None:
    result = analyze_dataframe(pd.DataFrame({"revenue": [100, 50, 20]}))

    assert result["metrics"]["revenue"] == 170
    assert result["metrics"]["orders"] == 3
    assert result["data_quality"]["order_count_basis"] == "row"


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("revenue", "not-a-number"),
        ("revenue", None),
        ("revenue", float("inf")),
        ("cost", "missing"),
        ("cost", None),
        ("discount", "-"),
        ("quantity", "invalid"),
    ],
)
def test_invalid_financial_facts_are_rejected(column: str, value: object) -> None:
    frame = pd.DataFrame({"revenue": [100.0], column: [value]})
    with pytest.raises(ValueError, match=f"Column '{column}'"):
        analyze_dataframe(frame)


@pytest.mark.parametrize("order_id", [None, " ", ""])
def test_missing_order_identifier_is_rejected(order_id: object) -> None:
    with pytest.raises(ValueError, match="order_id"):
        analyze_dataframe(pd.DataFrame({"order_id": [order_id], "revenue": [20]}))


def test_same_order_spanning_multiple_transaction_dates_is_rejected() -> None:
    frame = pd.DataFrame(
        {
            "order_id": ["A", "A"],
            "date": ["2026-01-01", "2026-01-02"],
            "revenue": [100, 50],
        }
    )
    with pytest.raises(ValueError, match="different transaction dates"):
        analyze_dataframe(frame)


def test_invalid_date_is_rejected_instead_of_dropping_sales() -> None:
    with pytest.raises(ValueError, match="Column 'date'"):
        analyze_dataframe(pd.DataFrame({"date": ["bad"], "revenue": [200]}))


def test_empty_input_and_colliding_normalized_columns_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        analyze_dataframe(pd.DataFrame({"revenue": []}))
    with pytest.raises(ValueError, match="unique after normalization"):
        analyze_dataframe(pd.DataFrame({"Revenue": [30], " revenue ": [40]}))


def test_missing_cost_column_does_not_invent_gross_profit() -> None:
    result = analyze_dataframe(pd.DataFrame({"order_id": ["A"], "revenue": [120]}))

    assert result["metrics"]["cost"] is None
    assert result["metrics"]["gross_profit"] is None
    assert result["metrics"]["gross_margin"] is None
    assert result["data_quality"]["has_cost"] is False


def test_exact_duplicate_line_items_are_reported_not_silently_dropped() -> None:
    result = analyze_dataframe(
        pd.DataFrame({"order_id": ["A", "A"], "revenue": [50, 50]})
    )

    assert result["metrics"]["revenue"] == 100
    assert result["metrics"]["orders"] == 1
    assert result["data_quality"]["duplicate_rows"] == 1


def test_validation_does_not_modify_input_dataframe() -> None:
    frame = pd.DataFrame({"Order ID": [" A ", " A "], "Revenue": ["10", "20"]})
    original = frame.copy(deep=True)

    result = analyze_dataframe(frame)

    pd.testing.assert_frame_equal(frame, original)
    assert result["metrics"]["orders"] == 1
    assert result["metrics"]["revenue"] == 30


def test_service_uses_numeric_facts_for_product_diagnoses() -> None:
    frame = pd.DataFrame(
        {
            "order_id": ["A", "B"],
            "product_id": ["P1", "P2"],
            "revenue": ["300", "30"],
            "cost": ["290", "10"],
        }
    )

    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(frame)

    assert result["analysis"]["metrics"]["revenue"] == 330
    assert result["analysis"]["metrics"]["orders"] == 2
    assert any(
        item.get("product_id") == "P1"
        for item in result["diagnoses"]
    )
