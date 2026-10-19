"""Exact minor-unit financial contract and no-silent-rounding regressions."""

import pandas as pd
import pytest

from core.metrics.engine import analyze_dataframe
from core.metrics.money import as_amount, average, minor_units, percent, sum_minor_units


def test_decimal_tenths_add_as_exact_cents() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["A", "B"],
            "date": ["2026-01-01", "2026-01-02"],
            "revenue": ["0.10", "0.20"],
            "cost": ["0.01", "0.02"],
            "discount": ["0.00", "0.01"],
        }
    )

    analysis = analyze_dataframe(df)
    assert analysis["metrics"]["revenue"] == 0.30
    assert analysis["metrics"]["cost"] == 0.03
    assert analysis["metrics"]["gross_profit"] == 0.27
    assert analysis["metrics"]["gross_margin"] == 90.0
    assert analysis["metrics"]["discount"] == 0.01
    assert analysis["quarterly_trend"][0]["revenue"] == 0.30
    assert analysis["data_quality"]["monetary_precision"] == "two_decimal_minor_units"
    assert analysis["data_quality"]["currency"] == "unspecified"


def test_many_small_lines_preserve_exact_cent_totals() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-15"] * 10_000,
            "revenue": ["0.01"] * 10_000,
            "cost": ["0.01"] * 10_000,
        }
    )
    result = analyze_dataframe(df)
    assert result["metrics"]["revenue"] == 100.0
    assert result["metrics"]["cost"] == 100.0
    assert result["metrics"]["gross_profit"] == 0.0
    assert result["quarterly_trend"][0]["revenue"] == 100.0


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("revenue", "1.005"),
        ("revenue", 0.001),
        ("revenue", "not-money"),
        ("revenue", None),
        ("revenue", float("inf")),
        ("cost", "2.0009"),
        ("cost", float("-inf")),
        ("discount", "0.0001"),
    ],
)
def test_sub_cent_missing_and_invalid_money_fails_closed(
    column: str, value: object
) -> None:
    frame = pd.DataFrame({"revenue": [100.0]})
    frame[column] = [value]

    with pytest.raises(ValueError, match=f"Column '{column}'"):
        analyze_dataframe(frame)


def test_negative_adjustments_are_kept_not_discarded() -> None:
    result = analyze_dataframe(
        pd.DataFrame({"revenue": ["12.00", "-2.25"], "cost": ["4.00", "0.75"]})
    )
    assert result["metrics"]["revenue"] == 9.75
    assert result["metrics"]["cost"] == 4.75
    assert result["metrics"]["gross_profit"] == 5.0


def test_half_up_rounding_is_explicit_at_final_ratio_boundary() -> None:
    assert average(101, 2) == 0.51
    assert percent(201, 20_000) == 1.01
    assert as_amount(sum_minor_units(["0.10", "0.20"], "revenue")) == 0.30


def test_amount_range_is_bounded_before_float_json_conversion() -> None:
    with pytest.raises(ValueError, match="supported amount range"):
        minor_units("1000000000000.00", "revenue", 1)
    with pytest.raises(ValueError, match="supported amount range"):
        sum_minor_units(["60000000000.00", "60000000000.00"], "revenue")


def test_quarterly_amounts_reconcile_exactly_in_minor_units() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-03-31", "2026-04-01", "2026-07-01"],
            "revenue": ["0.10", "0.20", "0.30"],
            "cost": ["0.01", "0.02", "0.03"],
        }
    )
    analysis = analyze_dataframe(df)
    trends = analysis["quarterly_trend"]

    assert [quarter["period"] for quarter in trends] == [
        "2026-Q1", "2026-Q2", "2026-Q3"
    ]
    assert sum_minor_units(
        [item["revenue"] for item in trends], "revenue"
    ) == 60
    assert sum_minor_units(
        [item["gross_profit"] for item in trends], "gross_profit"
    ) == 54
    assert analysis["metrics"]["gross_profit"] == 0.54
