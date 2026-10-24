"""Developer Toolkit public API and CLI contract, requiring no network or model key."""

import json
from pathlib import Path

import pytest

from bizlens_toolkit import base_usdc_demo, diagnose_csv, verify_golden
from bizlens_toolkit.__main__ import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "golden"


@pytest.mark.parametrize("scenario", ["order_lines", "profit_reversal"])
def test_published_financial_truth_is_reproducible(scenario):
    case = FIXTURES / f"{scenario}.csv"
    expected = FIXTURES / f"{scenario}.expected.json"
    verification = verify_golden(case, expected)
    assert verification.passed, verification.discrepancies
    assert not verification.discrepancies
    assert verification.scenario == scenario


def test_standalone_api_keeps_financial_evidence_not_random_session_ids():
    csv_file = FIXTURES / "profit_reversal.csv"
    one = diagnose_csv(csv_file)
    two = diagnose_csv(csv_file)
    assert one == two
    assert one["schema_version"] == "bizlens.toolkit.v1"
    assert one["source_type"] == "local_csv"
    assert one["explanation_provider"] == "rule_based_offline"
    assert "analysis_id" not in one
    assert one["metrics"]["revenue"] == 500
    assert one["metrics"]["gross_profit"] == 150
    assert one["period_comparison"]["current"]["gross_margin"] == 3.33
    assert set(d["diagnosis"] for d in one["diagnoses"]) == {
        "Margin Decline", "Revenue Up / Profit Down",
        "Cost Pressure", "Discount Pressure",
        "High Revenue / Low Profit Product",
    }
    assert one["recommended_actions"]
    assert one["limitations"]


def test_python_cli_outputs_structured_json_without_running_services(capsys):
    csv_file = FIXTURES / "profit_reversal.csv"
    assert main(["diagnose", "--csv", str(csv_file)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["metrics"]["revenue"] == 500
    assert "analysis_id" not in data
    assert data["what_changed"]


def test_golden_verifier_cli_exits_success_on_hand_audited_facts(capsys):
    csv_file = FIXTURES / "order_lines.csv"
    expected = FIXTURES / "order_lines.expected.json"
    assert main([
        "verify-golden", "--csv", str(csv_file), "--expected", str(expected),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["passed"] is True
    assert result["expected_values_unchanged"] is True


def test_changed_golden_expectation_fails_closed_and_is_never_rewritten(capsys, tmp_path):
    original = (FIXTURES / "profit_reversal.expected.json").read_text()
    expected = json.loads(original)
    expected["metrics"]["gross_profit"] = 9999
    changed = tmp_path / "wrong.expected.json"
    changed.write_text(json.dumps(expected))
    report = verify_golden(FIXTURES / "profit_reversal.csv", changed)
    assert not report.passed
    assert any("gross_profit" in issue for issue in report.discrepancies)
    assert main([
        "verify-golden",
        "--csv", str(FIXTURES / "profit_reversal.csv"),
        "--expected", str(changed),
    ]) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False
    assert json.loads(changed.read_text()) == expected
    assert (FIXTURES / "profit_reversal.expected.json").read_text() == original


def test_invalid_money_and_wrong_file_type_fail_safely(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("order_id,revenue,cost\n0007,1.005,1.00\n")
    with pytest.raises(ValueError, match="more than two decimal places"):
        diagnose_csv(bad_csv)
    with pytest.raises(ValueError, match="only CSV"):
        diagnose_csv(tmp_path / "test.txt")


def test_identifiers_are_not_normalized_into_numbers(tmp_path):
    csv_file = tmp_path / "leading_zeroes.csv"
    csv_file.write_text(
        "order_id,date,product_id,revenue,cost\n"
        "0001,2026-02-01,0009,12.00,6.00\n"
        "0001,2026-02-01,0010,8.00,5.00\n"
        "0002,2026-02-02,0009,10.00,4.00\n"
    )
    snapshot = diagnose_csv(csv_file)
    assert snapshot["metrics"]["orders"] == 2
    assert snapshot["metrics"]["revenue"] == 30.0
    assert snapshot["metrics"]["cost"] == 15.0


def test_usdc_sample_has_no_actual_transaction_or_onchain_claim(capsys):
    assert main(["usdc-demo"]) == 0
    cli_output = json.loads(capsys.readouterr().out)
    assert cli_output == base_usdc_demo()
    assert not cli_output["real_transaction"]
    assert not cli_output["onchain_verified"]
    assert [r["status"] for r in cli_output["results"]] == [
        "candidate_match", "partial", "missing",
    ]


def test_cli_invalid_csv_exits_nonzero_without_traceback(tmp_path, capsys):
    p = tmp_path / "invalid.csv"
    p.write_text("revenue\n1.00000001\n")
    with pytest.raises(SystemExit) as exc:
        main(["diagnose", "--csv", str(p)])
    assert exc.value.code == 2
    assert "BizLens Toolkit" in capsys.readouterr().err
