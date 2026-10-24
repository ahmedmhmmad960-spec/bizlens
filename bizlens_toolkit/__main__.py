"""Minimal repeatable CLI for developer review and open-source integration."""

import argparse
import json
from pathlib import Path

from bizlens_toolkit.diagnosis import diagnose_csv, verify_golden
from integrations.base_usdc.__main__ import offline_demo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bizlens-toolkit",
        description="Evidence-first BizLens developer tools. No accounts or paid AI calls.",
    )
    actions = parser.add_subparsers(dest="command", required=True)
    diagnostic = actions.add_parser("diagnose", help="Analyze a local CSV with the offline core")
    diagnostic.add_argument("--csv", required=True, type=Path)
    verify = actions.add_parser(
        "verify-golden", help="Compare engine output to hand-audited JSON expectations"
    )
    verify.add_argument("--csv", required=True, type=Path)
    verify.add_argument("--expected", required=True, type=Path)
    actions.add_parser("usdc-demo", help="Run only synthetic USDC matching; no RPC")
    args = parser.parse_args(argv)

    try:
        if args.command == "diagnose":
            print(json.dumps(diagnose_csv(args.csv), indent=2, sort_keys=True))
            return 0
        if args.command == "verify-golden":
            result = verify_golden(args.csv, args.expected)
            print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
            return 0 if result.passed else 1
        print(json.dumps(offline_demo(), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"BizLens Toolkit: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
