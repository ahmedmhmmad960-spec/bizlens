"""Offline USDC matching regression: these are synthetic, unverified events."""

from dataclasses import replace

import pytest

from integrations.base_usdc.matcher import (
    Invoice,
    TransferRecord,
    USDC_CONTRACTS,
    match_invoice,
    match_invoices,
)

RECIPIENT = "0x" + "a" * 40
OTHER = "0x" + "b" * 40
TX = "0x" + "1" * 64
TX2 = "0x" + "2" * 64


def invoice(**changes):
    base = Invoice("INV-0001", 84532, RECIPIENT, "12.345678", TX, 0)
    return replace(base, **changes)


def transfer(**changes):
    base = TransferRecord(TX, 0, 84532, USDC_CONTRACTS[84532], RECIPIENT, 12_345_678)
    return replace(base, **changes)


def test_supplied_matching_fields_never_imply_onchain_verification():
    result = match_invoice(invoice(), [transfer()])
    assert result.status == "candidate_match"
    assert not result.onchain_verified
    assert "NOT verified" in result.reason
    assert result.record == transfer()


def test_missing_transaction_reference_or_record_is_not_claimed_missing_on_chain():
    assert match_invoice(invoice(tx_hash=None, log_index=None), []).status == "missing"
    result = match_invoice(invoice(), [transfer(tx_hash=TX2)])
    assert result.status == "missing"
    assert "supplied records" in result.reason


@pytest.mark.parametrize(
    ("changes", "status"),
    [
        ({"chain_id": 8453}, "wrong_chain"),
        ({"token_contract": OTHER}, "wrong_token"),
        ({"recipient": OTHER}, "wrong_address"),
        ({"amount_raw": 12_345_677}, "partial"),
        ({"amount_raw": 12_345_679}, "amount_mismatch"),
    ],
)
def test_mismatch_cases_do_not_produce_matches(changes, status):
    result = match_invoice(invoice(), [transfer(**changes)])
    assert result.status == status
    assert not result.onchain_verified
    assert result.record is not None


def test_wrong_network_token_is_never_treated_as_native_usdc():
    result = match_invoice(invoice(chain_id=8453), [
        transfer(chain_id=8453, token_contract=USDC_CONTRACTS[84532]),
    ])
    assert result.status == "wrong_token"


def test_case_insensitive_evm_references():
    result = match_invoice(
        invoice(recipient=RECIPIENT.upper().replace("0X", "0x"),
                tx_hash=TX.upper().replace("0X", "0x")),
        [transfer()],
    )
    assert result.status == "candidate_match"


def test_multiple_logs_need_explicit_index_to_avoid_guessing():
    extra = transfer(log_index=1, amount_raw=12_345_678)
    assert match_invoice(invoice(log_index=None), [transfer(), extra]).status == "duplicate"
    assert match_invoice(invoice(log_index=1), [transfer(), extra]).status == "candidate_match"


def test_duplicate_identical_supplied_log_fails_closed():
    assert match_invoice(invoice(), [transfer(), transfer()]).status == "duplicate"


def test_one_log_cannot_satisfy_two_invoices():
    other_invoice = invoice(invoice_id="INV-0002")
    result = match_invoices([invoice(), other_invoice], [transfer()])
    assert [row.status for row in result] == ["duplicate", "duplicate"]


def test_distinct_references_can_satisfy_distinct_invoices():
    other_invoice = invoice(invoice_id="INV-0002", tx_hash=TX2)
    second_transfer = transfer(tx_hash=TX2)
    result = match_invoices([invoice(), other_invoice], [transfer(), second_transfer])
    assert [row.status for row in result] == ["candidate_match", "candidate_match"]


@pytest.mark.parametrize("bad", [
    "0", "-1", "nan", "inf", "1.1234567", "", "not-an-amount",
])
def test_invalid_invoice_amounts_fail_closed(bad):
    with pytest.raises(ValueError):
        invoice(amount_usdc=bad)


def test_decimal_precision_avoids_floating_point_rounding():
    exact = match_invoice(invoice(amount_usdc="0.000001"), [transfer(amount_raw=1)])
    assert exact.status == "candidate_match"
    with pytest.raises(ValueError):
        invoice(amount_usdc=0.1)


@pytest.mark.parametrize("bad", [True, -1, 1.5])
def test_invalid_transfer_amounts_are_rejected(bad):
    with pytest.raises(ValueError):
        transfer(amount_raw=bad)


def test_invalid_address_chain_hash_and_log_index_are_rejected():
    with pytest.raises(ValueError):
        invoice(recipient="not-a-wallet")
    with pytest.raises(ValueError):
        invoice(chain_id=1)
    with pytest.raises(ValueError):
        invoice(tx_hash="0xdead")
    with pytest.raises(ValueError):
        invoice(log_index=-1)
    with pytest.raises(ValueError):
        transfer(token_contract="not-a-token")
    with pytest.raises(ValueError):
        transfer(log_index=-1)
    with pytest.raises(ValueError):
        transfer(chain_id=True)
