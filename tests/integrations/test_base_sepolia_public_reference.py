"""Public testnet explorer reference: attributed, offline by default, no forged proofs."""

import json

import pytest

from examples.developer_toolkit import base_sepolia_reference as sample
from integrations.base_usdc.rpc_evidence import ReceiptObservation

PUBLIC_TX = "0x32def9a45ee1ba8dadc6fd557719b89ea9b43c87792de9c496ed9b08728a57d0"
SOURCE_BLOCK = 42173271
RECIPIENT = "0xBB7Bc0b596d471b34F2770E95f93f0AB9596A649"


def test_real_explorer_reference_has_specific_attribution_and_usdc_contract():
    case = sample.reference_case()
    assert case["transaction_hash"] == PUBLIC_TX
    assert case["recipient"] == RECIPIENT
    assert case["chain_id"] == 84532
    assert case["explorer_block_number"] == SOURCE_BLOCK
    assert case["expected_amount_usdc"] == "0.001"
    assert case["expected_amount_raw"] == 1000
    assert case["explorer_reported_status"] == "Success"
    assert "sepolia.basescan.org/tx/" in case["explorer_url"]
    assert case["sample_invoice_is_hypothetical"] is True
    assert case["invoice_paid"] is False
    assert case["onchain_rpc_verified_by_bizlens"] is False
    assert case["settlement_finality_established"] is False


def test_default_cli_is_offline_and_does_not_claim_rpc_success(capsys, monkeypatch):
    monkeypatch.setattr(
        sample, "BasePublicRpc",
        lambda chain_id: pytest.fail("Offline reference must not create RPC transport"),
    )
    monkeypatch.setattr(
        sample, "inspect_invoice",
        lambda *args, **kwargs: pytest.fail("Offline reference must not inspect receipt"),
    )
    assert sample.main([]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["inspection"] == "not_requested"
    assert data["rpc_observed"] is False
    assert data["invoice_paid"] is False
    assert data["hypothetical_invoice"] is True
    assert data["settlement_finality_established"] is False


def test_explicit_inspection_only_marks_observed_when_receipt_matches_reference(monkeypatch):
    accessed = []

    def mocked_transport(chain):
        accessed.append(chain)
        return object()

    def observed(invoice, transport):
        assert invoice.tx_hash == PUBLIC_TX
        assert invoice.log_index is None
        assert invoice.recipient == RECIPIENT
        return ReceiptObservation(
            invoice_id=invoice.invoice_id, status="rpc_observed_match",
            explanation="Mocked public RPC observation, NOT real chain evidence.",
            chain_id=84532, tx_hash=PUBLIC_TX,
            block_number=SOURCE_BLOCK, confirmations=6, rpc_observed=True,
        )

    monkeypatch.setattr(sample, "BasePublicRpc", mocked_transport)
    monkeypatch.setattr(sample, "inspect_invoice", observed)
    output, exit_code = sample.run(inspect=True)
    assert exit_code == 0
    assert accessed == [84532]
    assert output["inspection"] == "rpc_observed"
    assert output["receipt_consistent_with_explorer"] is True
    assert output["rpc_observed"] is True
    assert output["invoice_paid"] is False
    assert output["settlement_finality_established"] is False


@pytest.mark.parametrize(
    ("status", "block_number"),
    [
        ("rpc_observed_match", SOURCE_BLOCK + 1),
        ("pending_or_missing", None),
        ("wrong_token", SOURCE_BLOCK),
        ("rpc_unavailable", None),
    ],
)
def test_nonmatching_or_unavailable_rpc_fails_closed(monkeypatch, status, block_number):
    monkeypatch.setattr(sample, "BasePublicRpc", lambda _: object())
    monkeypatch.setattr(
        sample, "inspect_invoice",
        lambda invoice, rpc: ReceiptObservation(
            invoice_id=invoice.invoice_id, status=status,
            explanation="Mocked only.", chain_id=84532,
            block_number=block_number, rpc_observed=status == "rpc_observed_match",
        ),
    )
    output, exit_code = sample.run(inspect=True)
    assert exit_code == 2
    assert output["rpc_observed"] is False
    assert output["inspection"] == "unconfirmed"
    assert output["invoice_paid"] is False


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("chain_id", 8453),
        ("token_contract", "0x" + "f" * 40),
        ("expected_amount_raw", 999),
        ("invoice_paid", True),
        ("sample_invoice_is_hypothetical", False),
    ],
)
def test_tampered_explorer_reference_is_rejected(tmp_path, monkeypatch, field, bad):
    data = sample.reference_case()
    data[field] = bad
    fixture = tmp_path / "altered-reference.json"
    fixture.write_text(json.dumps(data))
    monkeypatch.setattr(sample, "REFERENCE", fixture)
    with pytest.raises(ValueError):
        sample.reference_case()
