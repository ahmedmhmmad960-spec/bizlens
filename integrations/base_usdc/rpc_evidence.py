"""Bounded read-only Base JSON-RPC receipt inspection for native USDC.

Observations depend on the configured public RPC node. This is *not* a
cryptographic light-client proof, Ethereum L1 finality, or payment settlement.
The only outgoing calls are allowlisted Ethereum read methods over HTTPS.
"""

import json
import re
from dataclasses import dataclass, replace
from typing import Literal, Protocol
from urllib import error, request

from integrations.base_usdc.matcher import (
    USDC_CONTRACTS,
    Invoice,
    _address,
    _hash,
    _raw_amount,
)

BASE_RPC_URLS = {
    8453: "https://mainnet.base.org",
    84532: "https://sepolia.base.org",
}
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
_HEX_QUANTITY = re.compile(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)\Z")
_HEX_WORD = re.compile(r"0x[0-9a-fA-F]{64}\Z")
_MAX_RESPONSE = 1024 * 1024
_ALLOWED_METHODS = frozenset({
    "eth_chainId",
    "eth_getTransactionReceipt",
    "eth_blockNumber",
    "eth_getBlockByNumber",
})

ObservationStatus = Literal[
    "rpc_observed_match",
    "duplicate_claim",
    "missing_reference",
    "pending_or_missing",
    "failed_transaction",
    "wrong_chain",
    "noncanonical_block",
    "insufficient_confirmations",
    "missing_transfer",
    "ambiguous_transfer",
    "wrong_token",
    "wrong_address",
    "partial",
    "amount_mismatch",
    "invalid_evidence",
    "rpc_unavailable",
]


class RpcUnavailableError(Exception):
    """The public RPC could not provide usable read-only data."""


class _NoRedirect(request.HTTPRedirectHandler):
    """Never let a public RPC redirect an allowlisted request to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class RpcTransport(Protocol):
    def call(self, method: str, params: list[object]) -> object: ...


class BasePublicRpc:
    """Read-only allowlisted transport. Never accepts an arbitrary RPC URL."""

    def __init__(self, chain_id: int, timeout_seconds: float = 8.0):
        if type(chain_id) is not int or chain_id not in BASE_RPC_URLS:
            raise ValueError("Unsupported Base chain ID.")
        if not 0 < timeout_seconds <= 30:
            raise ValueError("RPC timeout must be between 0 and 30 seconds.")
        self.endpoint = BASE_RPC_URLS[chain_id]
        self.timeout = timeout_seconds

    def call(self, method: str, params: list[object]) -> object:
        if method not in _ALLOWED_METHODS:
            raise ValueError("Only approved read-only RPC methods are permitted.")
        body = json.dumps({
            "jsonrpc": "2.0", "method": method, "params": params, "id": 1,
        }).encode("utf-8")
        req = request.Request(
            self.endpoint, data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with request.build_opener(_NoRedirect()).open(
                req, timeout=self.timeout
            ) as response:
                data = response.read(_MAX_RESPONSE + 1)
                if len(data) > _MAX_RESPONSE:
                    raise RpcUnavailableError("RPC response exceeds safety limit.")
                payload = json.loads(data)
        except (error.HTTPError, error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise RpcUnavailableError("Read-only Base RPC request failed.") from exc
        if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
            raise RpcUnavailableError("Invalid RPC envelope.")
        if payload.get("id") != 1 or "error" in payload or "result" not in payload:
            raise RpcUnavailableError("RPC returned an invalid response or an error.")
        return payload["result"]


def _hex_number(value: object) -> int:
    if not isinstance(value, str) or not _HEX_QUANTITY.fullmatch(value):
        raise ValueError("Expected canonical hexadecimal RPC quantity.")
    return int(value, 16)


def _word(value: object) -> str:
    if not isinstance(value, str) or not _HEX_WORD.fullmatch(value):
        raise ValueError("Expected a full 32-byte hexadecimal word.")
    return value.lower()


def _topic_address(value: object) -> str:
    word = _word(value)
    if word[2:26] != "0" * 24:
        raise ValueError("ERC-20 indexed address has nonzero padding.")
    return "0x" + word[-40:]


@dataclass(frozen=True)
class ReceiptObservation:
    invoice_id: str
    status: ObservationStatus
    explanation: str
    chain_id: int
    tx_hash: str | None = None
    block_number: int | None = None
    block_hash: str | None = None
    confirmations: int | None = None
    log_index: int | None = None
    # A match is observed by an RPC node. It does not establish L1 finality.
    rpc_observed: bool = False
    source: str = "base_public_rpc"


def inspect_invoice(
    invoice: Invoice,
    rpc: RpcTransport,
    *,
    min_confirmations: int = 6,
) -> ReceiptObservation:
    """Match an invoice to a canonical successful receipt and ERC-20 log.

    The injected transport must be a trusted read-only Base RPC transport.
    Mock transports are for deterministic tests only. Malformed evidence
    fails closed; do not claim final payment settlement from an RPC response.
    """
    if type(min_confirmations) is not int or min_confirmations < 1:
        raise ValueError("min_confirmations must be a positive integer.")

    def result(
        status: ObservationStatus,
        message: str,
        *,
        block: int | None = None,
        block_hash: str | None = None,
        confirmations: int | None = None,
        log_index: int | None = None,
    ) -> ReceiptObservation:
        return ReceiptObservation(
            invoice_id=invoice.invoice_id, status=status, explanation=message,
            chain_id=invoice.chain_id, tx_hash=invoice.tx_hash,
            block_number=block, block_hash=block_hash,
            confirmations=confirmations, log_index=log_index,
            rpc_observed=status == "rpc_observed_match",
        )

    if invoice.tx_hash is None:
        return result("missing_reference", "Supply an explicit transaction hash first.")

    try:
        chain_id = _hex_number(rpc.call("eth_chainId", []))
        if chain_id != invoice.chain_id:
            return result("wrong_chain", "RPC chain differs from the invoice network.")

        receipt = rpc.call("eth_getTransactionReceipt", [invoice.tx_hash])
        if receipt is None:
            return result("pending_or_missing", "RPC has no receipt; status is not established.")
        if not isinstance(receipt, dict):
            raise ValueError("Malformed transaction receipt.")
        if _hash(receipt.get("transactionHash")) != _hash(invoice.tx_hash):
            raise ValueError("Receipt transaction hash does not match request.")
        status = _hex_number(receipt.get("status"))
        if status == 0:
            return result("failed_transaction", "Transaction receipt reports reverted execution.")
        if status != 1:
            raise ValueError("Unexpected transaction status.")
        block = _hex_number(receipt.get("blockNumber"))
        block_hash = _word(receipt.get("blockHash"))
        # Refuse stale/orphaned receipts: ask for the current canonical block.
        canonical = rpc.call("eth_getBlockByNumber", [hex(block), False])
        if not isinstance(canonical, dict):
            raise ValueError("Canonical block data unavailable.")
        if _hex_number(canonical.get("number")) != block:
            raise ValueError("Canonical block number mismatch.")
        if _word(canonical.get("hash")) != block_hash:
            return result(
                "noncanonical_block",
                "Receipt block no longer matches the RPC canonical chain.",
                block=block, block_hash=block_hash,
            )
        head = _hex_number(rpc.call("eth_blockNumber", []))
        if head < block:
            raise ValueError("RPC latest block predates transaction receipt.")
        confirmations = head - block + 1
        if confirmations < min_confirmations:
            return result(
                "insufficient_confirmations",
                "Too few observed L2 block confirmations for this demo policy.",
                block=block, block_hash=block_hash, confirmations=confirmations,
            )

        logs = receipt.get("logs")
        if not isinstance(logs, list):
            raise ValueError("Receipt logs must be an array.")
        transfers = []
        for item in logs:
            if not isinstance(item, dict):
                raise ValueError("Malformed receipt log.")
            topics = item.get("topics")
            if not isinstance(topics, list):
                raise ValueError("Malformed receipt log topics.")
            if not topics or not isinstance(topics[0], str):
                continue
            if topics[0].lower() != TRANSFER_TOPIC:
                continue
            if len(topics) != 3:
                raise ValueError("ERC-20 Transfer event must contain 3 topics.")
            if item.get("removed") is True:
                raise ValueError("Receipt contains a removed transfer log.")
            if _hash(item.get("transactionHash")) != _hash(invoice.tx_hash):
                raise ValueError("Transfer transaction hash does not match receipt.")
            if _word(item.get("blockHash")) != block_hash:
                raise ValueError("Transfer block hash does not match receipt.")
            if _hex_number(item.get("blockNumber")) != block:
                raise ValueError("Transfer block number does not match receipt.")
            transfers.append((
                _hex_number(item.get("logIndex")),
                _address(item.get("address"), "token_contract"),
                _topic_address(topics[2]),
                int(_word(item.get("data")), 16),
            ))

        if invoice.log_index is not None:
            transfers = [item for item in transfers if item[0] == invoice.log_index]
        if not transfers:
            return result(
                "missing_transfer",
                "No matching ERC-20 Transfer log in the supplied transaction receipt.",
                block=block, block_hash=block_hash, confirmations=confirmations,
            )
        if len(transfers) > 1:
            return result(
                "ambiguous_transfer", "Multiple Transfer logs; specify the log index.",
                block=block, block_hash=block_hash, confirmations=confirmations,
            )

        index, token, recipient, amount = transfers[0]
        details = {
            "block": block, "block_hash": block_hash,
            "confirmations": confirmations, "log_index": index,
        }
        if token != USDC_CONTRACTS[invoice.chain_id].lower():
            return result("wrong_token", "Transfer does not come from native USDC.", **details)
        if recipient != invoice.recipient.lower():
            return result("wrong_address", "Transfer recipient differs from invoice.", **details)
        expected = _raw_amount(invoice.amount_usdc)
        if amount < expected:
            return result("partial", "Transfer amount is below expected USDC amount.", **details)
        if amount > expected:
            return result(
                "amount_mismatch", "Transfer amount exceeds expected USDC amount.",
                **details,
            )
        return result(
            "rpc_observed_match",
            "Matching successful L2 receipt and canonical Transfer log observed "
            "via Base RPC; not a cryptographic proof or final settlement.",
            **details,
        )
    except (ValueError, TypeError, KeyError):
        return result("invalid_evidence", "Malformed or contradictory chain evidence; no match.")
    except Exception:
        # Hide transport errors and never display secrets or endpoint responses.
        return result("rpc_unavailable", "Read-only RPC unavailable; nothing was verified.")


def inspect_invoices(
    invoices: list[Invoice],
    rpc: RpcTransport,
    *,
    min_confirmations: int = 6,
) -> list[ReceiptObservation]:
    """Reject reuse of one observed event across multiple invoice claims."""
    if len(invoices) > 20:
        raise ValueError("At most 20 invoices can be inspected in one batch.")
    results = [
        inspect_invoice(invoice, rpc, min_confirmations=min_confirmations)
        for invoice in invoices
    ]
    claims: dict[tuple[int, str, int], list[int]] = {}
    for index, observation in enumerate(results):
        if (
            not observation.rpc_observed
            or observation.tx_hash is None
            or observation.log_index is None
        ):
            continue
        claim = (
            observation.chain_id, observation.tx_hash.lower(),
            observation.log_index,
        )
        claims.setdefault(claim, []).append(index)
    for indices in claims.values():
        if len(indices) > 1:
            for index in indices:
                results[index] = replace(
                    results[index],
                    status="duplicate_claim",
                    explanation="One observed transfer log is referenced by multiple invoices.",
                    rpc_observed=False,
                )
    return results
