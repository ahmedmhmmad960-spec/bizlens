"""Regression contract for observable signals used by the dashboard bars."""

import pandas as pd
import pytest

from core.changes.engine import build_what_changed, calculate_change
from core.metrics.engine import analyze_dataframe


def test_finite_growth_percent_uses_previous_period_baseline() -> None:
    change = calculate_change(200, 300)

    assert change == {
        "previous": 200,
        "current": 300,
        "change": 100,
        "change_percent": 50.0,
    }


def test_zero_baseline_keeps_percentage_unknown_not_infinite_or_zero() -> None:
    change = calculate_change(0, 150)

    assert change["change"] == 150
    assert change["change_percent"] is None


def test_gross_margin_absolute_change_is_in_percentage_points() -> None:
    changes = build_what_changed(
        {
            "previous": {"gross_margin": 70.0},
            "current": {"gross_margin": 3.33},
        }
    )
    assert len(changes) == 1
    assert changes[0]["key"] == "gross_margin"
    assert changes[0]["change"] == -66.67
    assert changes[0]["direction"] == "down"
    # Relative change exists, but UI must use 'change' as percentage points,
    # never graph that relative percentage beside sales growth bars.


def test_unknown_cost_or_profit_cannot_emit_a_comparable_signal() -> None:
    changes = build_what_changed(
        {
            "previous": {"revenue": 100, "cost": None, "gross_profit": None},
            "current": {"revenue": 110, "cost": None, "gross_profit": None},
        }
    )

    assert [item["key"] for item in changes] == ["revenue"]
    assert changes[0]["change_percent"] == pytest.approx(10.0)


def test_full_analysis_signal_is_derived_from_verified_amounts() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["A", "B", "C", "D"],
            "date": [
                "2026-02-01", "2026-02-02",
                "2026-02-03", "2026-02-04",
            ],
            "revenue": ["100.00", "100.00", "150.00", "150.00"],
            "cost": ["30.00", "30.00", "145.00", "145.00"],
        }
    )
    analyzed = analyze_dataframe(df)
    changes = {item["key"]: item for item in build_what_changed(
        analyzed["period_comparison"]
    )}

    assert changes["revenue"]["previous"] == 200.0
    assert changes["revenue"]["current"] == 300.0
    assert changes["revenue"]["change_percent"] == 50.0
    assert changes["gross_profit"]["change_percent"] == -92.86
    assert changes["gross_margin"]["change"] == -66.67
    assert changes["orders"]["change"] == 0
    assert changes["orders"]["direction"] == "unchanged"
