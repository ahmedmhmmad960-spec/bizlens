from typing import Any

from ai.client.provider import AIProvider


class RuleBasedProvider(AIProvider):
    """
    Fallback explanation provider for BizLens.
    Works without an external AI API.
    """

    def explain(
        self,
        diagnosis: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "explanation": diagnosis.get(
                "explanation",
                "No explanation available."
            ),
            "recommended_action": diagnosis.get(
                "recommended_action",
                "Review the available business evidence."
            ),
        }

    def ask(
        self,
        question: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:

        metrics = context.get(
            "metrics",
            {}
        )

        top_diagnoses = context.get(
            "top_diagnoses",
            []
        )

        evidence = []

        for diagnosis in top_diagnoses:
            evidence.append(
                diagnosis.get(
                    "explanation",
                    diagnosis.get(
                        "diagnosis",
                        "Business diagnosis detected."
                    )
                )
            )

        if not evidence:
            evidence.append(
                "No specific diagnosis was available from the analyzed data."
            )

        return {
            "answer": (
                "BizLens analyzed the available business data. "
                f"Revenue is {metrics.get('revenue')}, "
                f"gross profit is {metrics.get('gross_profit')}, "
                f"and gross margin is {metrics.get('gross_margin')}%. "
                "Review the evidence below for the main detected issues."
            ),
            "evidence": evidence,
            "limitations": [
                "Rule-based fallback is active, so natural-language reasoning is limited."
            ],
        }
