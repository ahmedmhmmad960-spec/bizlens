"""A public, attributed Base Sepolia USDC transfer as a reproducible reference.

Default is OFFLINE: read a public explorer annotation, never make an RPC call.
--inspect is opt-in, performs only allowlisted Base JSON-RPC read methods, and
does not infer that a hypothetical invoice actually existed or was paid.
"""

import argparse
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from integrations.base_usdc.matcher import USDC_CONTRACTS, Invoice
from integrations.base_usdc.rpc_evidence import BasePublicRpc, inspect_invoice

REFERENCE = Path(__file__).with_suffix(".json")


def reference_case() -> dict:
    """Validate the versioned public reference without querying any service."""
    source = json.loads(REFERENCE.read_text(encoding="utf-8"))
    if source.get("schema_version") != "bizlens.public_reference.v1":
        raise ValueError("Unknown public reference schema.")
    if source.get("chain_id") != 84532:
        raise ValueError("The supplied example must use Base Sepolia.")
    if source.get("token_contract", "").lower() != USDC_CONTRACTS[84532].lower():
        raise ValueError("Reference must identify native Base Sepolia USDC.")
    sample_invoice = Invoice(
        invoice_id=source["reference_id"], chain_id=source["chain_id"],
        recipient=source["recipient"], amount_usdc=source["expected_amount_usdc"],
        tx_hash=source["transaction_hash"], log_index=None,
    )
    expected_raw = int(Decimal(sample_invoice.amount_usdc) * 1_000_000)
    if expected_raw != source.get("expected_amount_raw"):
        raise ValueError("Explorer amount does not match exact six-decimal USDC units.")
    if source.get("invoice_paid") is not False or source.get(
        "sample_invoice_is_hypothetical"
    ) is not True:
        raise ValueError("Do not assert a real invoice or paid status from an explorer.")
    return source


def run(*, inspect: bool = False) -> tuple[dict, int]:
    """Return a report and a process exit code without making payments."""
    source = reference_case()
    report = {
        "reference_id": source["reference_id"],
        "network": source["network"],
        "source": "public_explorer_annotation",
        "source_url": source["explorer_url"],
        "transaction_hash": source["transaction_hash"],
        "recipient": source["recipient"],
        "amount_usdc": source["expected_amount_usdc"],
        "explorer_reported_status": source["explorer_reported_status"],
        "explorer_block_number": source["explorer_block_number"],
        "hypothetical_invoice": True,
        "settlement_finality_established": False,
        "invoice_paid": False,
        "limitations": (
            "Third-party testnet transfer, not a BizLens or merchant payment. "
            "Public explorer information is not independently verified by this tool "
            "unless --inspect is requested. Even an RPC observation is not L1 finality."
        ),
    }
    if not inspect:
        report["inspection"] = "not_requested"
        report["rpc_observed"] = False
        return report, 0

    invoice = Invoice(
        source["reference_id"], source["chain_id"], source["recipient"],
        source["expected_amount_usdc"], source["transaction_hash"],
    )
    observation = inspect_invoice(invoice, BasePublicRpc(invoice.chain_id))
    block_matches_explorer = (
        observation.block_number == source["explorer_block_number"]
    )
    receipt_consistent = (
        observation.status == "rpc_observed_match" and block_matches_explorer
    )
    report["inspection"] = "rpc_observed" if receipt_consistent else "unconfirmed"
    report["receipt_consistent_with_explorer"] = receipt_consistent
    report["rpc_observed"] = receipt_consistent
    report["rpc_observation"] = asdict(observation)
    return report, 0 if receipt_consistent else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Explore a real public testnet USDC transfer (offline by default)."
    )
    parser.add_argument(
        "--inspect", action="store_true",
        help="Explicitly query free public Base Sepolia JSON-RPC, read-only.",
    )
    args = parser.parse_args(argv)
    try:
        report, status = run(inspect=args.inspect)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Base public reference: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
