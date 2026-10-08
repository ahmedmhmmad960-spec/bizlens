import pandas as pd
import pytest

from core.metrics.engine import analyze_dataframe


def test_analyze_dataframe_calculates_core_metrics() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "revenue": [100, 200],
            "cost": [40, 100],
            "discount": [10, 20],
            "quantity": [1, 2],
        }
    )

    result = analyze_dataframe(df)

    assert result["metrics"]["revenue"] == 300
    assert result["metrics"]["cost"] == 140
    assert result["metrics"]["gross_profit"] == 160
    assert result["metrics"]["gross_margin"] == pytest.approx(53.33, abs=0.01)
    assert result["metrics"]["aov"] == 150
    assert result["data_quality"]["has_cost"] is True


def test_missing_revenue_is_rejected() -> None:
    with pytest.raises(ValueError, match="revenue column"):
        analyze_dataframe(pd.DataFrame({"cost": [10]}))


def test_period_comparison_is_created_for_dated_data() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
            "revenue": [100, 100, 150, 150],
            "cost": [40, 40, 90, 90],
        }
    )

    result = analyze_dataframe(df)
    comparison = result["period_comparison"]

    assert comparison["previous"]["revenue"] == 200
    assert comparison["current"]["revenue"] == 300
    assert comparison["previous"]["gross_profit"] == 120
    assert comparison["current"]["gross_profit"] == 120
