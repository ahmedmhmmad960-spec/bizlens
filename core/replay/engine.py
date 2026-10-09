from typing import Any


def build_demo_replay(
    analysis: dict[str, Any],
    diagnoses: list[dict[str, Any]],
    top_diagnoses: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    diagnosis_chains: list[dict[str, Any]],
    what_changed: list[dict[str, Any]],
    ai_explanations: list[dict[str, Any]],
    business_report: dict[str, Any],
) -> dict[str, Any]:
    metrics = analysis.get("metrics", {})
    data_quality = analysis.get("data_quality", {})

    steps = [
        {
            "step": 1,
            "key": "data_understanding",
            "title": "Understanding your data",
            "description": "BizLens inspected the uploaded business dataset.",
            "data": {
                "rows": analysis.get("rows"),
                "columns": analysis.get("columns", []),
            },
        },
        {
            "step": 2,
            "key": "data_quality",
            "title": "Checking data quality",
            "description": "BizLens checked whether the available data is suitable for analysis.",
            "data": data_quality,
        },
        {
            "step": 3,
            "key": "business_metrics",
            "title": "Building the business picture",
            "description": "BizLens calculated the core business metrics.",
            "data": metrics,
        },
        {
            "step": 4,
            "key": "diagnosis",
            "title": "Finding business signals",
            "description": "BizLens searched the data for meaningful problems and opportunities.",
            "data": {
                "total_diagnoses": len(diagnoses),
                "top_diagnoses": top_diagnoses,
            },
        },
        {
            "step": 5,
            "key": "evidence",
            "title": "Checking the evidence",
            "description": "BizLens connected each diagnosis to measurable evidence.",
            "data": evidence,
        },
        {
            "step": 6,
            "key": "diagnosis_chains",
            "title": "Connecting the signals",
            "description": "BizLens looked for relationships between detected business signals.",
            "data": diagnosis_chains,
        },
        {
            "step": 7,
            "key": "what_changed",
            "title": "Understanding what changed",
            "description": "BizLens compared the available periods to identify meaningful changes.",
            "data": what_changed,
        },
        {
            "step": 8,
            "key": "ai_explanation",
            "title": "Explaining what it means",
            "description": (
                "The AI explanation layer translated the evidence into clear business language."
            ),
            "data": ai_explanations,
        },
        {
            "step": 9,
            "key": "recommended_actions",
            "title": "Deciding what to do next",
            "description": "BizLens generated actions based on the detected evidence.",
            "data": business_report.get("recommended_actions", []),
        },
        {
            "step": 10,
            "key": "business_report",
            "title": "Creating your business report",
            "description": "BizLens assembled the findings into a structured business report.",
            "data": business_report,
        },
    ]

    return {
        "title": "BizLens Analysis Replay",
        "description": "A step-by-step view of how BizLens analyzed the business data.",
        "total_steps": len(steps),
        "steps": steps,
    }
