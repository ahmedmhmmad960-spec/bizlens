"""Hand-audited, version-controlled financial golden tests.

Source fixtures and expected values live together in tests/fixtures/golden/.
Expected results are reviewed calculations, NOT regenerated from BizLens.
Do not auto-update them merely to make a failing test pass.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "golden"
SCENARIOS = ("order_lines", "profit_reversal")


@pytest.fixture(params=SCENARIOS, ids=SCENARIOS)
def golden_case(request: pytest.FixtureRequest) -> tuple[pd.DataFrame, dict]:
    name = request.param
    frame = pd.read_csv(FIXTURES / f"{name}.csv")
    expected = json.loads((FIXTURES / f"{name}.expected.json").read_text())
    return frame, expected


def analyze(frame: pd.DataFrame) -> dict:
    """Full deterministic path, with no remote model or API calls."""
    return AnalysisService(RuleBasedProvider()).analyze_dataframe(frame)


def test_golden_financial_totals(golden_case: tuple[pd.DataFrame, dict]) -> None:
    frame, expected = golden_case

    result = analyze(frame)
    analysis = result["analysis"]

    assert analysis["rows"] == expected["rows"]
    assert analysis["metrics"] == expected["metrics"]
    for field, value in expected["quality"].items():
        assert analysis["data_quality"][field] == value


def test_golden_periods_and_order_grain(golden_case: tuple[pd.DataFrame, dict]) -> None:
    frame, expected = golden_case

    periods = analyze(frame)["analysis"]["period_comparison"]

    # The V1 comparison is the chronological midpoint, NOT fiscal quarters.
    assert periods == expected["period_comparison"]


def test_golden_diagnoses_and_numeric_evidence(
    golden_case: tuple[pd.DataFrame, dict],
) -> None:
    frame, expected = golden_case

    result = analyze(frame)
    diagnoses = {item["diagnosis"]: item for item in result["diagnoses"]}

    assert len(diagnoses) == len(result["diagnoses"])
    assert set(diagnoses) == set(expected["diagnoses"])
    for name, facts in expected["diagnoses"].items():
        actual = diagnoses[name]
        for key, value in facts.items():
            assert actual[key] == value, (name, key, actual[key], value)
        assert actual["confidence_score"] <= 1.0
        assert actual["evidence"]["confidence_score"] == actual["confidence_score"]
        assert actual["evidence"]["confidence"] == actual["confidence"]


def test_golden_what_changed(golden_case: tuple[pd.DataFrame, dict]) -> None:
    frame, expected = golden_case
    changes = {change["key"]: change for change in analyze(frame)["what_changed"]}

    for metric, facts in expected["changes"].items():
        for key, value in facts.items():
            assert changes[metric][key] == value, (metric, key)


def test_golden_replay_uses_the_same_financial_facts(
    golden_case: tuple[pd.DataFrame, dict],
) -> None:
    frame, expected = golden_case

    result = analyze(frame)
    replay = result["demo_replay"]
    steps = {step["key"]: step for step in replay["steps"]}

    assert replay["total_steps"] == 10
    assert len(replay["steps"]) == replay["total_steps"]
    assert steps["business_metrics"]["data"] == expected["metrics"]
    assert steps["business_metrics"]["data"] == result["analysis"]["metrics"]
    assert steps["data_quality"]["data"] == result["analysis"]["data_quality"]
    assert steps["what_changed"]["data"] == result["what_changed"]
    assert steps["business_report"]["data"] == result["business_report"]


def test_golden_accounting_conservation(
    golden_case: tuple[pd.DataFrame, dict],
) -> None:
    frame, _ = golden_case
    analysis = analyze(frame)["analysis"]
    periods = analysis["period_comparison"]

    # No sales-line revenue or cost can disappear between midpoint periods.
    for metric in ("revenue", "cost", "gross_profit", "discount", "orders"):
        assert (
            periods["previous"][metric] + periods["current"][metric]
            == analysis["metrics"][metric]
        )


def test_shuffling_lines_cannot_change_business_facts(
    golden_case: tuple[pd.DataFrame, dict],
) -> None:
    frame, _ = golden_case

    original = analyze(frame)
    shuffled = analyze(frame.sample(frac=1, random_state=91).reset_index(drop=True))

    assert shuffled["analysis"] == original["analysis"]
    assert shuffled["what_changed"] == original["what_changed"]
    # Avoid comparing random analysis IDs; compare reproducible diagnoses.
    by_name = lambda result: {
        item["diagnosis"]: (item["severity"], item["confidence_score"])
        for item in result["diagnoses"]
    }
    assert by_name(shuffled) == by_name(original)
