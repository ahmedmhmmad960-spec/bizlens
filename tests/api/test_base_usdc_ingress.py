"""Direct FastAPI ingress must uphold Next's limits without trusting Next."""

import json

import pytest
from fastapi.testclient import TestClient

from apps.api.app import base_usdc_routes as routes
from apps.api.app.base_usdc_ingress import MAX_INSPECTION_BODY_BYTES
from apps.api.app.main import app

client = TestClient(app)

VALID = {
    "invoice_id": "SYNTH-SECURITY-001",
    "chain_id": 84532,
    "recipient": "0x" + "a" * 40,
    "amount_usdc": "1.000001",
    "tx_hash": "0x" + "b" * 64,
    "log_index": 0,
}


@pytest.fixture
def no_rpc_network(monkeypatch):
    # Even valid operator credentials cannot bypass the ingress limit.
    monkeypatch.setenv("BIZLENS_BASE_RPC_ENABLED", "1")
    monkeypatch.setenv("BIZLENS_BASE_RPC_TOKEN", "f" * 64)
    monkeypatch.setattr(
        routes,
        "BasePublicRpc",
        lambda chain: pytest.fail("Body cap failed; unexpected RPC constructor"),
    )


def assert_rejected(response):
    assert response.status_code == 413, response.text[:250]
    assert response.headers["cache-control"] == "no-store"
    assert "too large" in response.text.lower()


def test_direct_api_rejects_large_content_length_before_parsing(no_rpc_network):
    oversized = json.dumps(VALID).encode() + b" " * MAX_INSPECTION_BODY_BYTES
    assert_rejected(client.post(
        "/base-usdc/inspect", content=oversized,
        headers={
            "content-type": "application/json",
            "X-BizLens-Rpc-Key": "f" * 64,
        },
    ))


def test_direct_api_enforces_actual_chunked_bytes_without_content_length(no_rpc_network):
    # A streamed caller can omit or forge the length header.
    oversized = json.dumps(VALID).encode() + b" " * MAX_INSPECTION_BODY_BYTES

    def body_chunks():
        for pos in range(0, len(oversized), 337):
            yield oversized[pos:pos + 337]

    assert_rejected(client.post(
        "/base-usdc/inspect", content=body_chunks(),
        headers={
            "content-type": "application/json",
            "X-BizLens-Rpc-Key": "f" * 64,
        },
    ))


def test_forged_short_declared_length_does_not_bypass_stream_cap(no_rpc_network):
    oversized = json.dumps(VALID).encode() + b" " * MAX_INSPECTION_BODY_BYTES
    response = client.post(
        "/base-usdc/inspect", content=iter([oversized]),
        headers={
            "content-length": "3",
            "content-type": "application/json",
            "X-BizLens-Rpc-Key": "f" * 64,
        },
    )
    assert_rejected(response)


def test_legitimate_small_inspection_still_reaches_default_disabled_gate(monkeypatch):
    monkeypatch.delenv("BIZLENS_BASE_RPC_ENABLED", raising=False)
    response = client.post("/base-usdc/inspect", json=VALID)
    assert response.status_code == 503
    assert response.json()["mode"] == "disabled"
    assert response.headers["cache-control"] == "no-store"


def test_limit_does_not_affect_other_healthy_api_routes():
    assert client.get("/health").json()["status"] == "healthy"
