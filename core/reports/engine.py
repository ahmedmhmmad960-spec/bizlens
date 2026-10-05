from typing import Any


def build_business_report(
    analysis: dict[str, Any],
    diagnoses: list[dict[str, Any]],
    top_diagnoses: list[dict[str, Any]],
    diagnosis_chains: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    what_changed: list[dict[str, Any]],
    ai_explanations: list[dict[str, Any]],
) -> dict[str, Any]:
    metrics = analysis.get("metrics", {})
    data_quality = analysis.get("data_quality", {})

    return {
        "title": "BizLens Business Report",
        "summary": build_executive_summary(metrics, top_diagnoses),
        "metrics": metrics,
        "data_quality": data_quality,
        "top_diagnoses": top_diagnoses,
        "diagnoses": diagnoses,
        "evidence": evidence,
        "diagnosis_chains": diagnosis_chains,
        "what_changed": what_changed,
        "ai_explanations": ai_explanations,
        "recommended_actions": build_recommended_actions(top_diagnoses),
        "limitations": build_limitations(top_diagnoses),
    }


def build_executive_summary(
    metrics: dict[str, Any],
    top_diagnoses: list[dict[str, Any]],
) -> dict[str, Any]:
    revenue = metrics.get("revenue")
    gross_profit = metrics.get("gross_profit")
    gross_margin = metrics.get("gross_margin")
    orders = metrics.get("orders")
    aov = metrics.get("aov")

    return {
        "headline": build_headline(top_diagnoses),
        "revenue": revenue,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
        "orders": orders,
        "aov": aov,
        "main_findings": [
            diagnosis.get("diagnosis")
            for diagnosis in top_diagnoses
            if diagnosis.get("diagnosis")
        ],
    }


def build_headline(top_diagnoses: list[dict[str, Any]]) -> str:
    if not top_diagnoses:
        return "No major business diagnosis was detected from the available data."

    first = top_diagnoses[0].get("diagnosis", "Business issue detected")
    return f"BizLens detected a primary business signal: {first}."


def build_recommended_actions(
    top_diagnoses: list[dict[str, Any]],
) -> list[str]:
    actions = []

    for diagnosis in top_diagnoses:
        action = diagnosis.get("recommended_action")
        if action and action not in actions:
            actions.append(action)

    return actions


def build_limitations(
    top_diagnoses: list[dict[str, Any]],
) -> list[str]:
    limitations = []

    for diagnosis in top_diagnoses:
        diagnosis_limitations = diagnosis.get("limitations", [])

        if isinstance(diagnosis_limitations, list):
            for limitation in diagnosis_limitations:
                if limitation not in limitations:
                    limitations.append(limitation)

    if not limitations:
        limitations.append(
            "BizLens reports observed patterns from the available dataset "
            "and does not establish causation unless supported by evidence."
        )

    return limitations
