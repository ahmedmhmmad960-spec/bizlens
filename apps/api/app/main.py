import os
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pandas as pd

from core.metrics.engine import analyze_dataframe

from core.diagnoses.margin_decline import (
    detect_margin_decline,
)
from core.diagnoses.revenue_up_profit_down import (
    detect_revenue_up_profit_down,
)
from core.diagnoses.cost_pressure import (
    detect_cost_pressure,
)
from core.diagnoses.discount_pressure import (
    detect_discount_pressure,
)
from core.diagnoses.high_revenue_low_profit_product import (
    detect_high_revenue_low_profit_product,
)

from core.ranking.priority import rank_diagnoses
from core.chains.engine import build_diagnosis_chains
from core.changes.engine import build_what_changed
from core.evidence.engine import build_evidence
from core.confidence.engine import calculate_confidence
from core.reports.engine import build_business_report
from core.replay.engine import build_demo_replay

from ai.client.rule_based_provider import (
    RuleBasedProvider,
)
from ai.client.openai_provider import (
    OpenAIProvider,
)


load_dotenv()


app = FastAPI(
    title="BizLens API",
    description="Open-source AI business diagnosis engine",
    version="0.1.0",
)


api_key = os.getenv("OPENAI_API_KEY")
ai_model = os.getenv("BIZLENS_AI_MODEL")

if api_key and ai_model:
    ai_provider = OpenAIProvider()
else:
    ai_provider = RuleBasedProvider()


analysis_store: dict[str, dict[str, Any]] = {}


@app.get("/")
def root():
    return {
        "name": "BizLens",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


class AskRequest(BaseModel):
    question: str
    analysis_id: str


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        return {
            "success": False,
            "error": "Only CSV files are supported.",
        }

    try:
        df = pd.read_csv(file.file)

        result = analyze_dataframe(df)

        diagnoses = []

        period_comparison = result.get(
            "period_comparison"
        )

        if period_comparison:

            margin_diagnosis = detect_margin_decline(
                period_comparison
            )

            if margin_diagnosis:
                diagnoses.append(
                    margin_diagnosis
                )

            revenue_profit_diagnosis = (
                detect_revenue_up_profit_down(
                    period_comparison
                )
            )

            if revenue_profit_diagnosis:
                diagnoses.append(
                    revenue_profit_diagnosis
                )

            cost_pressure_diagnosis = (
                detect_cost_pressure(
                    period_comparison
                )
            )

            if cost_pressure_diagnosis:
                diagnoses.append(
                    cost_pressure_diagnosis
                )

            discount_diagnosis = (
                detect_discount_pressure(
                    period_comparison
                )
            )

            if discount_diagnosis:
                diagnoses.append(
                    discount_diagnosis
                )

        product_diagnoses = (
            detect_high_revenue_low_profit_product(
                df
            )
        )

        if product_diagnoses:
            diagnoses.extend(product_diagnoses)

        for diagnosis in diagnoses:
            confidence_result = calculate_confidence(
                diagnosis,
                result,
            )

            diagnosis["confidence"] = confidence_result["confidence"]
            diagnosis["confidence_score"] = confidence_result["score"]
            diagnosis["limitations"] = confidence_result["limitations"]

            diagnosis["evidence"] = {
                **diagnosis.get("evidence", {}),
                "confidence": confidence_result["confidence"],
                "confidence_score": confidence_result["score"],
                "limitations": confidence_result["limitations"],
            }

        top_diagnoses = rank_diagnoses(
            diagnoses,
            limit=3,
        )

        diagnosis_chains = build_diagnosis_chains(
            diagnoses
        )

        evidence = [
            {
                "diagnosis": diagnosis.get("diagnosis"),
                "evidence": build_evidence(diagnosis),
            }
            for diagnosis in diagnoses
        ]

        what_changed = build_what_changed(
            result.get("period_comparison", {})
        )

        ai_explanations = []

        for diagnosis in top_diagnoses:
            explanation = ai_provider.explain(
                diagnosis
            )

            ai_explanations.append({
                "diagnosis": diagnosis.get(
                    "diagnosis"
                ),
                "ai": explanation,
            })

        analysis_id = str(uuid4())

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

        analysis_store[analysis_id] = {
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

    except ValueError as error:
        return {
            "success": False,
            "error": str(error),
        }

@app.post("/ask")
async def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        return {
            "success": False,
            "error": "Question cannot be empty.",
        }

    analysis_context = analysis_store.get(
        request.analysis_id
    )

    if analysis_context is None:
        return {
            "success": False,
            "error": "Analysis not found or expired.",
        }

    try:
        context = {
            "analysis": analysis_context.get(
                "analysis",
                {}
            ),
            "diagnoses": analysis_context.get(
                "diagnoses",
                []
            ),
            "top_diagnoses": analysis_context.get(
                "top_diagnoses",
                []
            ),
            "diagnosis_chains": analysis_context.get(
                "diagnosis_chains",
                []
            ),
            "evidence": analysis_context.get(
                "evidence",
                []
            ),
            "what_changed": analysis_context.get(
                "what_changed",
                []
            ),
        }

        result = ai_provider.ask(
            question,
            context,
        )

        return {
            "success": True,
            "analysis_id": request.analysis_id,
            "question": question,
            "answer": result,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }
