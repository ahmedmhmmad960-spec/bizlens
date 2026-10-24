"""Read-only Base USDC invoice comparison against *supplied* transfer records.

This module never connects to an RPC, verifies receipts, moves funds, or marks
an invoice paid. A candidate match is NOT proof of on-chain settlement.
"""

import re
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Literal

# Circle-issued native USDC contracts, not bridged USDbC.
# Source: https://developers.circle.com/stablecoins/usdc-contract-addresses
USDC_CONTRACTS = {
    8453: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    84532: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
}
USDC_DECIMALS = 6
_AMOUNT_SCALE = 10**USDC_DECIMALS
_MAX_AMOUNT_RAW = 10**24 - 1  # V1 cap: < 10**18 whole USDC units.
_AMOUNT_FORMAT = re.compile(r"(?:0|[1-9][0-9]{0,17})(?:\.[0-9]{1,6})?\Z")
_ADDRESS = re.compile(r"0x[0-9a-fA-F]{40}\Z")
_HASH = re.compile(r"0x[0-9a-fA-F]{64}\Z")

MatchStatus = Literal[
    "candidate_match", "missing", "duplicate", "wrong_chain",
    "wrong_token", "wrong_address", "partial", "amount_mismatch",
]


def _address(value: str, name: str) -> str:
    if not isinstance(value, str) or not _ADDRESS.fullmatch(value):
        raise ValueError(f"{name} must be a 20-byte hexadecimal EVM address.")
    return value.lower()


def _hash(value: str) -> str:
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise ValueError("tx_hash must be a 32-byte hexadecimal hash.")
    return value.lower()


def _raw_amount(value: str) -> int:
    """Reject rounding, floats and unsupported USDC precision."""
    if not isinstance(value, str):
        raise ValueError("Invoice USDC amount must be a decimal string.")
    if not _AMOUNT_FORMAT.fullmatch(value):
        raise ValueError(
            "Invoice USDC amount must use plain decimal notation with "
            "at most 18 whole digits and six decimal places."
        )
    try:
        scaled = Decimal(value) * _AMOUNT_SCALE
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invoice USDC amount is not decimal.") from exc
    raw = int(scaled)
    if raw <= 0 or raw > _MAX_AMOUNT_RAW:
        raise ValueError("Invoice USDC amount must be positive and within the V1 limit.")
    return raw


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    chain_id: int
    recipient: str
    amount_usdc: str
    tx_hash: str | None = None
    log_index: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.invoice_id, str) or not self.invoice_id.strip():
            raise ValueError("invoice_id is required.")
        if len(self.invoice_id) > 80:
            raise ValueError("invoice_id must be at most 80 characters.")
        if type(self.chain_id) is not int or self.chain_id not in USDC_CONTRACTS:
            raise ValueError("Only Base mainnet and Base Sepolia are supported.")
        _address(self.recipient, "recipient")
        _raw_amount(self.amount_usdc)
        if self.tx_hash is not None:
            _hash(self.tx_hash)
        if self.log_index is not None and (
            self.tx_hash is None or type(self.log_index) is not int or self.log_index < 0
        ):
            raise ValueError("log_index must be nonnegative and requires tx_hash.")


@dataclass(frozen=True)
class TransferRecord:
    tx_hash: str
    log_index: int
    chain_id: int
    token_contract: str
    recipient: str
    amount_raw: int

    def __post_init__(self) -> None:
        _hash(self.tx_hash)
        if type(self.log_index) is not int or self.log_index < 0:
            raise ValueError("log_index must be a nonnegative integer.")
        if type(self.chain_id) is not int or self.chain_id <= 0:
            raise ValueError("chain_id must be a positive integer.")
        _address(self.token_contract, "token_contract")
        _address(self.recipient, "recipient")
        if type(self.amount_raw) is not int or not 0 <= self.amount_raw <= _MAX_AMOUNT_RAW:
            raise ValueError("amount_raw must be a bounded nonnegative integer.")


@dataclass(frozen=True)
class MatchResult:
    invoice_id: str
    status: MatchStatus
    reason: str
    record: TransferRecord | None = None
    # No RPC access or receipt/chain verification occurs in this module.
    onchain_verified: bool = False


def _result(invoice: Invoice, status: MatchStatus, reason: str,
            record: TransferRecord | None = None) -> MatchResult:
    return MatchResult(invoice.invoice_id, status, reason, record)


def match_invoice(invoice: Invoice, records: list[TransferRecord]) -> MatchResult:
    """Compare an explicit transaction reference, never guess from amounts alone.

    A tx can have several ERC-20 logs. Without an explicit log index a multi-log
    reference is ambiguous and cannot be reported as matched.
    """
    if invoice.tx_hash is None:
        return _result(
            invoice, "missing",
            "No transaction reference supplied; no chain lookup was made.",
        )

    matching_tx = [r for r in records if _hash(r.tx_hash) == _hash(invoice.tx_hash)]
    if invoice.log_index is not None:
        matching_tx = [r for r in matching_tx if r.log_index == invoice.log_index]
    if not matching_tx:
        return _result(
            invoice, "missing",
            "Referenced transfer was not present in the supplied records.",
        )
    if len(matching_tx) > 1:
        return _result(
            invoice, "duplicate",
            "Multiple supplied records use the same invoice reference.",
        )

    record = matching_tx[0]
    if record.chain_id != invoice.chain_id:
        return _result(
            invoice, "wrong_chain",
            "Supplied transfer belongs to a different chain.",
            record,
        )
    if _address(record.token_contract, "token_contract") != _address(
        USDC_CONTRACTS[invoice.chain_id], "expected_token"
    ):
        return _result(
            invoice, "wrong_token",
            "Token is not Circle-issued native USDC on this chain.",
            record,
        )
    if _address(record.recipient, "recipient") != _address(invoice.recipient, "recipient"):
        return _result(
            invoice, "wrong_address",
            "Transfer recipient differs from the invoice.",
            record,
        )

    expected_raw = _raw_amount(invoice.amount_usdc)
    if record.amount_raw < expected_raw:
        return _result(invoice, "partial", "Transfer is less than the invoice amount.", record)
    if record.amount_raw > expected_raw:
        return _result(invoice, "amount_mismatch", "Transfer exceeds the invoice amount.", record)
    return _result(
        invoice, "candidate_match",
        "Supplied transfer fields match the invoice; on-chain settlement is NOT verified.",
        record,
    )


def match_invoices(invoices: list[Invoice], records: list[TransferRecord]) -> list[MatchResult]:
    """Detect reuse of one transfer log across multiple invoices."""
    results = [match_invoice(invoice, records) for invoice in invoices]
    claimed: dict[tuple[int, str, int], list[int]] = {}
    for index, result in enumerate(results):
        if result.status != "candidate_match" or result.record is None:
            continue
        record = result.record
        key = (record.chain_id, record.tx_hash.lower(), record.log_index)
        claimed.setdefault(key, []).append(index)
    for indices in claimed.values():
        if len(indices) > 1:
            for index in indices:
                results[index] = replace(
                    results[index], status="duplicate",
                    reason="The same transfer log was claimed by multiple invoices.",
                )
    return results
