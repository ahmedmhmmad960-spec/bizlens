"""Base USDC read-only evidence demo and optional RPC inspection CLI.

Default demo uses synthetic records only; --verify explicitly enables read-only
calls to allowlisted Base public RPCs. Never signs or sends transactions.
"""

import argparse
import json
from dataclasses import asdict

from integrations.base_usdc.matcher import (
    USDC_CONTRACTS,
    Invoice,
    TransferRecord,
    match_invoices,
)
from integrations.base_usdc.rpc_evidence import BasePublicRpc, inspect_invoice

DEMO_RECIPIENT = "0x" + "a" * 40
DEMO_TX = "0x" + "1" * 64


def offline_demo() -> dict:
    """Reproducible, explicitly synthetic examples; no RPC calls are made."""
    first = Invoice("SYNTH-001", 84532, DEMO_RECIPIENT, "12.345678", DEMO_TX, 0)
    second = Invoice("SYNTH-002", 84532, DEMO_RECIPIENT, "12.345679", DEMO_TX, 1)
    third = Invoice("SYNTH-003", 84532, DEMO_RECIPIENT, "12.345678")
    events = [
        TransferRecord(
            DEMO_TX, 0, 84532, USDC_CONTRACTS[84532], DEMO_RECIPIENT, 12_345_678,
        ),
        TransferRecord(
            DEMO_TX, 1, 84532, USDC_CONTRACTS[84532], DEMO_RECIPIENT, 12_345_677,
        ),
    ]
    return {
        "source": "synthetic_fixture",
        "network": "base-sepolia",
        "real_transaction": False,
        "onchain_verified": False,
        "warning": "Demonstration only. These are NOT real transaction receipts or payments.",
        "results": [asdict(result) for result in match_invoices(
            [first, second, third], events,
        )],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BizLens Base native-USDC evidence demo or read-only RPC inspection."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Synthetic offline test; NO network")
    mode.add_argument(
        "--verify", action="store_true",
        help="Read a real Base RPC transaction receipt; NOT settlement finality",
    )
    parser.add_argument("--chain", type=int, choices=sorted(USDC_CONTRACTS), default=84532)
    parser.add_argument("--invoice-id")
    parser.add_argument("--recipient")
    parser.add_argument("--amount-usdc")
    parser.add_argument("--tx-hash")
    parser.add_argument("--log-index", type=int)
    parser.add_argument(
        "--min-confirmations", type=int, default=6,
        help="Minimum observed Base L2 blocks including tx (default: 6)",
    )
    args = parser.parse_args(argv)

    if args.demo:
        print(json.dumps(offline_demo(), indent=2))
        return 0

    if not all((args.invoice_id, args.recipient, args.amount_usdc, args.tx_hash)):
        parser.error("--verify requires --invoice-id, --recipient, --amount-usdc, --tx-hash")
    try:
        invoice = Invoice(
            args.invoice_id, args.chain, args.recipient, args.amount_usdc,
            args.tx_hash, args.log_index,
        )
        rpc = BasePublicRpc(args.chain)
        finding = inspect_invoice(
            invoice, rpc, min_confirmations=args.min_confirmations,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(json.dumps({
        "network": "base-mainnet" if args.chain == 8453 else "base-sepolia",
        "source": "official_public_base_rpc",
        "warning": "RPC observation is not cryptographic proof or final settlement.",
        "result": asdict(finding),
    }, indent=2))
    return 0 if finding.status == "rpc_observed_match" else 2


if __name__ == "__main__":
    raise SystemExit(main())
