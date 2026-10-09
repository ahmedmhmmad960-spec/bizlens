import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from ai.client.openai_provider import OpenAIProvider
from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService

load_dotenv()

app = FastAPI(
    title="BizLens API",
    description="Open-source AI business diagnosis engine",
    version="0.1.0",
)

api_key = os.getenv("OPENAI_API_KEY")
ai_model = os.getenv("BIZLENS_AI_MODEL")
ai_provider = OpenAIProvider() if api_key and ai_model else RuleBasedProvider()
analysis_service = AnalysisService(ai_provider)
analysis_store: dict[str, dict[str, Any]] = {}


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "BizLens", "version": "0.1.0", "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


class AskRequest(BaseModel):
    question: str
    analysis_id: str


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        return {"success": False, "error": "Only CSV files are supported."}

    try:
        df = pd.read_csv(file.file)
        payload = analysis_service.analyze_dataframe(df)
        analysis_store[payload["analysis_id"]] = payload
        return payload
    except (ValueError, pd.errors.ParserError) as error:
        return {"success": False, "error": str(error)}


@app.post("/ask")
async def ask(request: AskRequest) -> dict[str, Any]:
    question = request.question.strip()
    if not question:
        return {"success": False, "error": "Question cannot be empty."}

    analysis_context = analysis_store.get(request.analysis_id)
    if analysis_context is None:
        return {"success": False, "error": "Analysis not found or expired."}

    analysis = analysis_context.get("analysis", {})
    context = {
        "metrics": analysis.get("metrics", {}),
        "data_quality": analysis.get("data_quality", {}),
        "period_comparison": analysis.get("period_comparison", {}),
        "analysis": analysis,
        "diagnoses": analysis_context.get("diagnoses", []),
        "top_diagnoses": analysis_context.get("top_diagnoses", []),
        "diagnosis_chains": analysis_context.get("diagnosis_chains", []),
        "evidence": analysis_context.get("evidence", []),
        "what_changed": analysis_context.get("what_changed", []),
    }

    try:
        result = ai_provider.ask(question, context)
        return {"success": True, "analysis_id": request.analysis_id, "question": question, "answer": result}
    except Exception as error:
        return {"success": False, "error": str(error)}
