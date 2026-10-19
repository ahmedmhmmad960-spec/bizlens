"""CSV HTTP ingress must preserve identifiers and exact financial text."""

import pytest
from fastapi.testclient import TestClient

from ai.client.rule_based_provider import RuleBasedProvider
from apps.api.app import main as api
from core.analysis.service import AnalysisService

client = TestClient(api.app)


@pytest.fixture(autouse=True)
def offline_analysis(monkeypatch: pytest.MonkeyPatch) -> None:
    # Always force a local deterministic provider, independent of CI secrets.
    monkeypatch.setattr(api, "analysis_service", AnalysisService(RuleBasedProvider()))


def submit(csv_text: str) -> dict:
    response = client.post(
        "/analyze",
        files={"file": ("sales.csv", csv_text.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    return response.json()


def test_csv_ids_keep_leading_zeroes_and_numeric_cents() -> None:
    result = submit(
        "order_id,product_id,date,revenue,cost\n"
        "0001,0007,2026-01-01,0.10,0.10\n"
        "0001,0007,2026-01-01,0.20,0.19\n"
        "0002,0008,2026-01-02,0.30,0.15\n"
    )

    assert result["success"] is True
    assert result["analysis"]["metrics"]["revenue"] == 0.60
    assert result["analysis"]["metrics"]["gross_profit"] == 0.16
    assert result["analysis"]["metrics"]["orders"] == 2

    diagnoses = [
        item for item in result["diagnoses"]
        if item["diagnosis"] == "High Revenue / Low Profit Product"
    ]
    assert len(diagnoses) == 1
    assert diagnoses[0]["product_id"] == "0007"
    assert diagnoses[0]["revenue"] == 0.30
    assert diagnoses[0]["gross_profit"] == 0.01


def test_csv_rejects_subcent_amount_that_float_inference_could_round_away() -> None:
    result = submit(
        "order_id,product_id,revenue,cost\n"
        "0001,0007,1.00000000000000000001,1.00\n"
    )
    assert result["success"] is False
    assert "more than two decimal places" in result["error"]


def test_csv_rejects_blank_product_id_instead_of_dropping_revenue() -> None:
    result = submit(
        "order_id,product_id,revenue,cost\n"
        "0001,P1,10.00,5.00\n"
        "0002, ,20.00,10.00\n"
    )
    assert result["success"] is False
    assert "product_id" in result["error"]
