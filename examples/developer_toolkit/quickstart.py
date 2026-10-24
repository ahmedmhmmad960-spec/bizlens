"""BizLens Community reproducible quickstart: NO RPC and NO AI API keys.

Run from the repository root:
    python -m examples.developer_toolkit.quickstart
"""

import json
from pathlib import Path

from bizlens_toolkit import base_usdc_demo, diagnose_csv, verify_golden

ROOT = Path(__file__).resolve().parents[2]


def run() -> dict:
    csv_file = ROOT / "tests/fixtures/golden/profit_reversal.csv"
    expected = ROOT / "tests/fixtures/golden/profit_reversal.expected.json"
    diagnosis = diagnose_csv(csv_file)
    verified = verify_golden(csv_file, expected)
    base_evidence = base_usdc_demo()

    # Explicitly separate business data from synthetic blockchain evidence.
    return {
        "toolkit_schema": diagnosis["schema_version"],
        "commerce": {
            "metrics": diagnosis["metrics"],
            "detected_diagnoses": [d["diagnosis"] for d in diagnosis["diagnoses"]],
            "recommended_actions": diagnosis["recommended_actions"],
            "golden_financial_reproduction": verified.as_dict(),
            "confidence_note": diagnosis["confidence_note"],
        },
        "base_usdc": {
            "sample_only": True,
            "source": base_evidence["source"],
            "onchain_verified": False,
            "outcomes": [
                {
                    "invoice_id": finding["invoice_id"],
                    "status": finding["status"],
                    "onchain_verified": finding["onchain_verified"],
                }
                for finding in base_evidence["results"]
            ],
        },
        "limitations": [
            "Synthetic financial and USDC evidence only; not real merchant transactions.",
            "This example performs no RPC access and no external AI requests.",
            "A supplied-record match does not verify settlement or paid status.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
