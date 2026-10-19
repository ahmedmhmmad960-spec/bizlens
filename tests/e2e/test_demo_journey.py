"""App-level deterministic demo journey, without any external AI provider."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai.client.rule_based_provider import RuleBasedProvider
from apps.api.app import main as api
from core.analysis.service import AnalysisService

DEMO = Path(__file__).resolve().parents[2] / "apps/web/public/demo/store.csv"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Avoid accidental external calls when CI has model configuration.
    provider = RuleBasedProvider()
    monkeypatch.setattr(api, "analysis_service", AnalysisService(provider))
    monkeypatch.setattr(api, "ai_provider", provider)
    monkeypatch.setattr(api, "analysis_store", {})
    return TestClient(api.app)


def analyze_demo(client: TestClient) -> dict:
    response = client.post(
        "/analyze",
        files={"file": ("store.csv", DEMO.read_bytes(), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    return data


def test_complete_demo_analyze_ask_report_and_replay(client: TestClient) -> None:
    payload = analyze_demo(client)
    metrics = payload["analysis"]["metrics"]

    assert metrics["revenue"] == 1560.0
    assert metrics["cost"] == 990.0
    assert metrics["gross_profit"] == 570.0
    assert metrics["orders"] == 10
    assert payload["analysis"]["quarterly_trend"][0]["period"] == "2026-Q3"
    assert len(payload["analysis"]["quarterly_trend"]) == 1

    diagnoses = payload["diagnoses"]
    assert diagnoses
    assert all(item["evidence"] for item in diagnoses)
    assert payload["business_report"]["metrics"] == metrics
    assert payload["business_report"]["summary"]["headline"]
    assert payload["business_report"]["recommended_actions"]
    assert payload["business_report"]["quarterly_trend"] == payload["analysis"][
        "quarterly_trend"
    ]

    replay = payload["demo_replay"]
    assert replay["total_steps"] == len(replay["steps"]) == 10
    steps = {step["key"]: step["data"] for step in replay["steps"]}
    assert steps["business_metrics"] == metrics
    assert steps["what_changed"] == payload["what_changed"]
    assert steps["business_report"] == payload["business_report"]

    reply = client.post(
        "/ask",
        json={
            "analysis_id": payload["analysis_id"],
            "question": "Why did the margin change?",
        },
    )
    assert reply.status_code == 200
    answer = reply.json()
    assert answer["success"] is True
    assert "1560" in answer["answer"]["answer"]
    assert "570" in answer["answer"]["answer"]
    assert answer["answer"]["evidence"]
    assert answer["answer"]["limitations"]


def test_invalid_upload_never_creates_an_analysis_session(client: TestClient) -> None:
    before = len(api.analysis_store)
    response = client.post(
        "/analyze",
        files={"file": ("sales.csv", b"order_id,revenue\nA,1.005\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert "more than two decimal places" in response.json()["error"]
    assert len(api.analysis_store) == before


def test_bad_ask_and_unknown_analysis_fail_closed(client: TestClient) -> None:
    payload = analyze_demo(client)
    session_id = payload["analysis_id"]

    for question, analysis_id, expected in (
        (" ", session_id, "Question cannot be empty"),
        ("What happened?", "unknown-analysis-id", "not found or expired"),
    ):
        response = client.post(
            "/ask",
            json={"analysis_id": analysis_id, "question": question},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert expected in data["error"]
