"""Developer-facing example must be runnable without network, secrets or wallets."""

import json

import pytest

from integrations.base_usdc import __main__ as cli
from integrations.base_usdc.rpc_evidence import ReceiptObservation


def test_offline_demo_exposes_verifiable_failure_states(capsys, monkeypatch):
    def no_network(_chain):
        pytest.fail("Synthetic demo must never create an RPC client")

    monkeypatch.setattr(cli, "BasePublicRpc", no_network)
    assert cli.main(["--demo"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["source"] == "synthetic_fixture"
    assert output["real_transaction"] is False
    assert output["onchain_verified"] is False
    assert [r["status"] for r in output["results"]] == [
        "candidate_match", "partial", "missing",
    ]
    assert all(not r["onchain_verified"] for r in output["results"])


def test_verify_is_opt_in_and_discloses_confirmation_limits(capsys, monkeypatch):
    def fake_client(chain):
        assert chain == 84532
        return object()

    def fake_inspection(inv, rpc, *, min_confirmations):
        assert min_confirmations == 6
        assert inv.invoice_id == "INV-1"
        return ReceiptObservation(
            "INV-1", "rpc_observed_match", "Observed on Base L2, not final.",
            84532, tx_hash=cli.DEMO_TX, block_number=100,
            confirmations=6, rpc_observed=True,
        )

    monkeypatch.setattr(cli, "BasePublicRpc", fake_client)
    monkeypatch.setattr(cli, "inspect_invoice", fake_inspection)
    result = cli.main([
        "--verify", "--chain", "84532",
        "--invoice-id", "INV-1",
        "--recipient", cli.DEMO_RECIPIENT,
        "--amount-usdc", "12.345678",
        "--tx-hash", cli.DEMO_TX, "--log-index", "0",
    ])
    assert result == 0
    obj = json.loads(capsys.readouterr().out)
    assert obj["result"]["rpc_observed"]
    assert "not cryptographic proof" in obj["warning"]
    assert obj["source"] == "official_public_base_rpc"


def test_unsuccessful_rpc_inspection_returns_nonzero(capsys, monkeypatch):
    monkeypatch.setattr(cli, "BasePublicRpc", lambda chain: object())
    monkeypatch.setattr(
        cli, "inspect_invoice",
        lambda *args, **kwargs: ReceiptObservation(
            "INV-1", "pending_or_missing", "No receipt.", 84532,
        ),
    )
    status = cli.main([
        "--verify", "--invoice-id", "INV-1",
        "--recipient", cli.DEMO_RECIPIENT,
        "--amount-usdc", "1.00", "--tx-hash", cli.DEMO_TX,
    ])
    assert status == 2
    obj = json.loads(capsys.readouterr().out)
    assert not obj["result"]["rpc_observed"]


def test_verify_must_not_accept_missing_transaction_parameters():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--verify"])
    assert exc.value.code == 2
