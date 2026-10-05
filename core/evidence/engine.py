from typing import Any


def build_evidence(diagnosis: dict[str, Any]) -> dict[str, Any]:
    """
    Build structured evidence for a BizLens diagnosis.

    The Evidence Engine does not invent facts.
    It only extracts and organizes evidence already
    present in the diagnosis.
    """

    evidence = diagnosis.get("evidence", {})

    return {
        "signal": build_signal(diagnosis),
        "calculation": build_calculation(diagnosis),
        "evidence": evidence,
        "confidence": diagnosis.get("confidence", "medium"),
    }


def build_signal(diagnosis: dict[str, Any]) -> str:
    diagnosis_name = diagnosis.get("diagnosis")

    signals = {
        "Margin Decline": (
            "Gross margin declined between the previous "
            "and current periods."
        ),
        "Revenue Up / Profit Down": (
            "Revenue increased while gross profit declined."
        ),
        "Cost Pressure": (
            "Costs increased faster than revenue."
        ),
        "Discount Pressure": (
            "Discounting increased faster than revenue."
        ),
        "High Revenue / Low Profit Product": (
            "A high-revenue product is generating very low "
            "or negative gross profit."
        ),
    }

    return signals.get(
        diagnosis_name,
        "A business signal was detected from the available data."
    )


def build_calculation(diagnosis: dict[str, Any]) -> dict[str, Any]:
    diagnosis_name = diagnosis.get("diagnosis")

    if diagnosis_name == "Margin Decline":
        return {
            "previous_margin": diagnosis.get("previous_margin"),
            "current_margin": diagnosis.get("current_margin"),
            "change_points": diagnosis.get("change_points"),
        }

    if diagnosis_name == "Revenue Up / Profit Down":
        return {
            "revenue_change_percent": diagnosis.get(
                "revenue_change_percent"
            ),
            "profit_change_percent": diagnosis.get(
                "profit_change_percent"
            ),
        }

    if diagnosis_name == "Cost Pressure":
        return {
            "cost_change_percent": diagnosis.get(
                "cost_change_percent"
            ),
            "revenue_change_percent": diagnosis.get(
                "revenue_change_percent"
            ),
        }

    if diagnosis_name == "Discount Pressure":
        return {
            "discount_change_percent": diagnosis.get(
                "discount_change_percent"
            ),
            "revenue_change_percent": diagnosis.get(
                "revenue_change_percent"
            ),
        }

    if diagnosis_name == "High Revenue / Low Profit Product":
        return {
            "revenue": diagnosis.get("revenue"),
            "gross_profit": diagnosis.get("gross_profit"),
            "gross_margin": diagnosis.get("gross_margin"),
            "revenue_share": diagnosis.get("revenue_share"),
        }

    return {}
