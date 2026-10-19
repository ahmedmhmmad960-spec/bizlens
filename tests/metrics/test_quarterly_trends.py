"""Calendar-quarter regression tests: stable, evidence-backed chart contract."""

import pandas as pd
import pytest

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService
from core.metrics.engine import analyze_dataframe


def dated_rows() -> pd.DataFrame:
    """One multiline order in 2025 Q4 and four more orders in 2026 Q1/Q2."""
    return pd.DataFrame(
        {
            "order_id": ["A", "A", "B", "C", "D", "E"],
            "date": [
                "2025-12-31", "2025-12-31",
                "2026-01-01", "2026-03-31",
                "2026-04-01", "2026-04-02",
            ],
            "revenue": [20.10, 9.90, 50, 50, 100, 200],
            "cost": [10, 5, 30, 10, 80, 100],
            "discount": [1, 0, 0, 5, 0, 0],
        }
    )


def test_calendar_quarters_are_chronological_and_auditable() -> None:
    analysis = analyze_dataframe(dated_rows())
    assert analysis["quarterly_trend"] == [
        {
            "period": "2025-Q4", "year": 2025, "quarter": 4,
            "revenue": 30.0, "cost": 15.0, "gross_profit": 15.0,
            "gross_margin": 50.0, "discount": 1.0, "orders": 1, "aov": 30.0,
        },
        {
            "period": "2026-Q1", "year": 2026, "quarter": 1,
            "revenue": 100.0, "cost": 40.0, "gross_profit": 60.0,
            "gross_margin": 60.0, "discount": 5.0, "orders": 2, "aov": 50.0,
        },
        {
            "period": "2026-Q2", "year": 2026, "quarter": 2,
            "revenue": 300.0, "cost": 180.0, "gross_profit": 120.0,
            "gross_margin": 40.0, "discount": 0.0, "orders": 2, "aov": 150.0,
        },
    ]
    assert analysis["metrics"]["orders"] == 5
    assert analysis["metrics"]["revenue"] == 430.0


def test_quarterly_balances_reconcile_with_global_financial_facts() -> None:
    result = analyze_dataframe(dated_rows())
    trend = result["quarterly_trend"]

    for key in ("revenue", "cost", "discount", "gross_profit", "orders"):
        assert round(sum(item[key] for item in trend), 2) == result["metrics"][key]


def test_quarterly_gross_margin_is_weighted_not_average_of_line_margins() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-02-01", "2026-02-02"],
            "revenue": [100, 200],
            "cost": [70, 100],
        }
    )
    trend = analyze_dataframe(df)["quarterly_trend"]

    assert trend[0]["gross_margin"] == pytest.approx(43.33, abs=0.01)
    assert trend[0]["aov"] == 150.0


def test_no_date_yields_no_quarterly_observations() -> None:
    result = analyze_dataframe(pd.DataFrame({"revenue": [20, 30]}))
    assert result["quarterly_trend"] == []


def test_missing_cost_keeps_quarterly_profit_unknown() -> None:
    result = analyze_dataframe(
        pd.DataFrame({"date": ["2026-01-01"], "revenue": [42]})
    )["quarterly_trend"][0]
    assert result["revenue"] == 42.0
    assert result["cost"] is None
    assert result["gross_profit"] is None
    assert result["gross_margin"] is None


def test_zero_revenue_quarter_never_invents_margin() -> None:
    result = analyze_dataframe(
        pd.DataFrame({"date": ["2026-01-01"], "revenue": [0], "cost": [5]})
    )["quarterly_trend"][0]
    assert result["gross_profit"] == -5.0
    assert result["gross_margin"] is None
    assert result["aov"] == 0


def test_invalid_date_blocks_quarterly_and_midpoint_reports() -> None:
    with pytest.raises(ValueError, match="Column 'date'"):
        analyze_dataframe(pd.DataFrame({"date": ["unparseable"], "revenue": [10]}))


def test_multiline_order_cannot_cross_quarter_boundaries() -> None:
    with pytest.raises(ValueError, match="different transaction dates"):
        analyze_dataframe(
            pd.DataFrame(
                {
                    "order_id": ["A", "A"],
                    "date": ["2026-03-31", "2026-04-01"],
                    "revenue": [10, 20],
                }
            )
        )


def test_quarterly_series_is_stable_under_row_reordering() -> None:
    frame = dated_rows()
    expected = analyze_dataframe(frame)["quarterly_trend"]
    shuffled = frame.sample(frac=1, random_state=31).reset_index(drop=True)
    assert analyze_dataframe(shuffled)["quarterly_trend"] == expected


def test_report_and_replay_preserve_identical_quarterly_data() -> None:
    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(dated_rows())
    series = result["analysis"]["quarterly_trend"]
    report = result["business_report"]
    replay_report = next(
        step["data"]
        for step in result["demo_replay"]["steps"]
        if step["key"] == "business_report"
    )

    assert report["quarterly_trend"] == series
    assert replay_report["quarterly_trend"] == series
    assert len(result["demo_replay"]["steps"]) == 10
