from typing import Any
from uuid import uuid4

import pandas as pd

from ai.client.openai_provider import OpenAIProvider
from ai.client.rule_based_provider import RuleBasedProvider
from core.chains.engine import build_diagnosis_chains
from core.changes.engine import build_what_changed
from core.confidence.engine import calculate_confidence
from core.diagnoses.cost_pressure import detect_cost_pressure
from core.diagnoses.discount_pressure import detect_discount_pressure
from core.diagnoses.high_revenue_low_profit_product import detect_high_revenue_low_profit_product
from core.diagnoses.margin_decline import detect_margin_decline
from core.diagnoses.revenue_up_profit_down import detect_revenue_up_profit_down
from core.evidence.engine import build_evidence
from core.metrics.engine import analyze_dataframe
from core.ranking.priority import rank_diagnoses
from core.replay.engine import build_demo_replay
from core.reports.engine import build_business_report


class AnalysisService:
    """Orchestrates a complete BizLens analysis without owning HTTP concerns."""

    def __init__(self, ai_provider: OpenAIProvider | RuleBasedProvider) -> None:
        self.ai_provider = ai_provider

    def analyze_dataframe(self, df: pd.DataFrame) -> dict[str, Any]:
        result = analyze_dataframe(df)
        diagnoses = self._detect_diagnoses(df, result)
        self._attach_confidence(diagnoses, result)

        top_diagnoses = rank_diagnoses(diagnoses, limit=3)
        diagnosis_chains = build_diagnosis_chains(diagnoses)
        evidence = [
            {"diagnosis": diagnosis.get("diagnosis"), "evidence": build_evidence(diagnosis)}
            for diagnosis in diagnoses
        ]
        what_changed = build_what_changed(result.get("period_comparison", {}))
        ai_explanations = self._build_ai_explanations(top_diagnoses)
        business_report = build_business_report(
            analysis=result,
            diagnoses=diagnoses,
            top_diagnoses=top_diagnoses,
            diagnosis_chains=diagnosis_chains,
            evidence=evidence,
            what_changed=what_changed,
            ai_explanations=ai_explanations,
        )
        demo_replay = build_demo_replay(
            analysis=result,
            diagnoses=diagnoses,
            top_diagnoses=top_diagnoses,
            evidence=evidence,
            diagnosis_chains=diagnosis_chains,
            what_changed=what_changed,
            ai_explanations=ai_explanations,
            business_report=business_report,
        )

        analysis_id = str(uuid4())
        return {
            "success": True,
            "analysis_id": analysis_id,
            "analysis": result,
            "diagnoses": diagnoses,
            "top_diagnoses": top_diagnoses,
            "diagnosis_chains": diagnosis_chains,
            "evidence": evidence,
            "what_changed": what_changed,
            "ai_explanations": ai_explanations,
            "business_report": business_report,
            "demo_replay": demo_replay,
        }

    @staticmethod
    def _detect_diagnoses(df: pd.DataFrame, result: dict[str, Any]) -> list[dict[str, Any]]:
        diagnoses: list[dict[str, Any]] = []
        period_comparison = result.get("period_comparison")

        if period_comparison:
            for detector in (
                detect_margin_decline,
                detect_revenue_up_profit_down,
                detect_cost_pressure,
                detect_discount_pressure,
            ):
                diagnosis = detector(period_comparison)
                if diagnosis:
                    diagnoses.append(diagnosis)

        diagnoses.extend(detect_high_revenue_low_profit_product(df) or [])
        return diagnoses

    @staticmethod
    def _attach_confidence(diagnoses: list[dict[str, Any]], analysis: dict[str, Any]) -> None:
        for diagnosis in diagnoses:
            confidence_result = calculate_confidence(diagnosis, analysis)
            diagnosis["confidence"] = confidence_result["confidence"]
            diagnosis["confidence_score"] = confidence_result["score"]
            diagnosis["limitations"] = confidence_result["limitations"]
            diagnosis["evidence"] = {
                **diagnosis.get("evidence", {}),
                "confidence": confidence_result["confidence"],
                "confidence_score": confidence_result["score"],
                "limitations": confidence_result["limitations"],
            }

    def _build_ai_explanations(self, diagnoses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"diagnosis": diagnosis.get("diagnosis"), "ai": self.ai_provider.explain(diagnosis)}
            for diagnosis in diagnoses
        ]
