"""Base invoice evidence endpoints: synthetic by default, live RPC opt-in only."""

from fastapi.testclient import TestClient

from apps.api.app import base_usdc_routes as routes
from apps.api.app.main import app
from integrations.base_usdc.rpc_evidence import ReceiptObservation

client = TestClient(app)

PAYLOAD = {
    "invoice_id": "INV-123",
    "chain_id": 84532,
    "recipient": "0x" + "a" * 40,
    "amount_usdc": "12.345678",
    "tx_hash": "0x" + "1" * 64,
    "log_index": 0,
}


def test_synthetic_demo_is_disclosed_and_never_calls_network(monkeypatch):
    monkeypatch.delenv("BIZLENS_BASE_RPC_ENABLED", raising=False)

    def unexpected(*args, **kwargs):
        raise AssertionError("Demo should not call RPC")

    monkeypatch.setattr(routes, "BasePublicRpc", unexpected)
    response = client.get("/base-usdc/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "synthetic_fixture"
    assert data["success"] is True
    assert data["onchain_verified"] is False
    assert data["real_transaction"] is False
    assert [row["status"] for row in data["results"]] == [
        "candidate_match", "partial", "missing",
    ]


def test_rpc_endpoint_disabled_by_default(monkeypatch):
    monkeypatch.delenv("BIZLENS_BASE_RPC_ENABLED", raising=False)
    monkeypatch.setattr(
        routes, "BasePublicRpc",
        lambda chain: (_ for _ in ()).throw(AssertionError("unexpected call")),
    )
    response = client.post("/base-usdc/inspect", json=PAYLOAD)
    assert response.status_code == 503
    assert response.json()["success"] is False
    assert response.headers["cache-control"] == "no-store"


def test_explicit_opt_in_still_remains_evidence_only(monkeypatch):
    monkeypatch.setenv("BIZLENS_BASE_RPC_ENABLED", "1")
    monkeypatch.setattr(routes, "BasePublicRpc", lambda chain: object())
    monkeypatch.setattr(
        routes, "inspect_invoice",
        lambda invoice, rpc: ReceiptObservation(
            invoice_id=invoice.invoice_id,
            status="rpc_observed_match",
            explanation="Observed matching Base L2 receipt, not final.",
            chain_id=invoice.chain_id,
            tx_hash=invoice.tx_hash,
            block_number=123,
            confirmations=6,
            rpc_observed=True,
        ),
    )
    response = client.post("/base-usdc/inspect", json=PAYLOAD)
    data = response.json()
    assert response.status_code == 200
    assert data["mode"] == "read_only_rpc"
    assert data["result"]["rpc_observed"] is True
    assert "NOT proof of final settlement" in data["warning"]
    assert "paid" not in data["result"]["status"]


def test_wrong_invoice_is_rejected_before_rpc_lookup(monkeypatch):
    monkeypatch.setenv("BIZLENS_BASE_RPC_ENABLED", "1")
    monkeypatch.setattr(
        routes, "BasePublicRpc",
        lambda chain: (_ for _ in ()).throw(AssertionError("unexpected network")),
    )
    response = client.post("/base-usdc/inspect", json={**PAYLOAD, "recipient": "wrong"})
    assert response.status_code == 422
    response = client.post("/base-usdc/inspect", json={**PAYLOAD, "amount_usdc": "1.1234567"})
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_unexpected_or_oversized_fields_fail_closed(monkeypatch):
    monkeypatch.setenv("BIZLENS_BASE_RPC_ENABLED", "1")
    assert client.post(
        "/base-usdc/inspect", json={**PAYLOAD, "private_key": "must_not_be_accepted"},
    ).status_code == 422
    assert client.post(
        "/base-usdc/inspect", json={**PAYLOAD, "invoice_id": "x" * 81},
    ).status_code == 422
    assert client.post(
        "/base-usdc/inspect", json={**PAYLOAD, "chain_id": 1},
    ).status_code == 422
