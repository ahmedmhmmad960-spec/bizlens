"""Local, versioned, deterministic public output contract for BizLens V1.

No HTTP server, model credentials, RPC service or session store is required.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService

SCHEMA_VERSION = "bizlens.toolkit.v1"


def diagnose_csv(csv_path: str | Path) -> dict[str, Any]:
    """Analyze a local sales-line CSV using the deterministic BizLens engine.

    String ingestion preserves zero-prefixed identifiers and financial lexemes.
    Returns a stable business-facts contract with no random analysis/session ID.
    The explanation provider is rule-based and cannot establish causality.
    """
    path = Path(csv_path)
    if path.suffix.lower() != ".csv":
        raise ValueError("Developer Toolkit accepts only CSV source files.")
    frame = pd.read_csv(path, dtype="string")
    payload = AnalysisService(RuleBasedProvider()).analyze_dataframe(frame)
    analysis = payload["analysis"]
    report = payload["business_report"]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_type": "local_csv",
        "explanation_provider": "rule_based_offline",
        "rows": analysis["rows"],
        "metrics": analysis["metrics"],
        "data_quality": analysis["data_quality"],
        "period_comparison": analysis.get("period_comparison"),
        "quarterly_trend": analysis.get("quarterly_trend", []),
        "diagnoses": payload["diagnoses"],
        "top_diagnoses": payload["top_diagnoses"],
        "what_changed": payload["what_changed"],
        "recommended_actions": report["recommended_actions"],
        "limitations": report["limitations"],
        "confidence_note": (
            "Evidence support heuristic; not a calibrated probability or proof of causality."
        ),
    }


@dataclass(frozen=True)
class GoldenVerification:
    """Independent expectation comparison; never rewrites golden baselines."""

    passed: bool
    scenario: str
    discrepancies: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "scenario": self.scenario,
            "discrepancies": list(self.discrepancies),
            "expected_values_unchanged": True,
        }


def verify_golden(csv_path: str | Path, expected_json: str | Path) -> GoldenVerification:
    """Compare real engine output to externally hand-audited expectations.

    This deliberately reads a separate expected JSON file. It never generates
    or mutates a baseline using the implementation under test.
    """
    expected = json.loads(Path(expected_json).read_text(encoding="utf-8"))
    if not isinstance(expected, dict):
        raise ValueError("Golden expectations must be a JSON object.")
    result = diagnose_csv(csv_path)
    problems: list[str] = []

    def compare(label: str, actual: object, desired: object) -> None:
        if actual != desired:
            problems.append(f"{label}: actual={actual!r}; expected={desired!r}")

    compare("rows", result["rows"], expected["rows"])
    compare("metrics", result["metrics"], expected["metrics"])
    compare("period_comparison", result["period_comparison"], expected["period_comparison"])
    quality = result["data_quality"]
    for key, value in expected["quality"].items():
        compare(f"quality.{key}", quality.get(key), value)
    diagnoses = {d["diagnosis"]: d for d in result["diagnoses"]}
    compare("diagnosis names", sorted(diagnoses), sorted(expected["diagnoses"]))
    for name, facts in expected["diagnoses"].items():
        item = diagnoses.get(name)
        if item is None:
            continue
        for key, value in facts.items():
            compare(f"diagnosis.{name}.{key}", item.get(key), value)
    movements = {row["key"]: row for row in result["what_changed"]}
    for key, facts in expected["changes"].items():
        row = movements.get(key)
        if row is None:
            problems.append(f"what_changed.{key}: missing")
            continue
        for field, value in facts.items():
            compare(f"what_changed.{key}.{field}", row.get(field), value)
    return GoldenVerification(
        passed=not problems,
        scenario=Path(csv_path).stem,
        discrepancies=tuple(problems),
    )
