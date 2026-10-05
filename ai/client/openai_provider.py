import json
import os
from typing import Any

from openai import OpenAI

from ai.client.provider import AIProvider
from ai.prompts.explain_diagnosis import (
    SYSTEM_PROMPT,
    build_diagnosis_prompt,
    ASK_SYSTEM_PROMPT,
    build_ask_prompt,
)


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the BizLens AI provider.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("BIZLENS_AI_MODEL")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        if not model:
            raise RuntimeError(
                "BIZLENS_AI_MODEL is not configured."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def explain(
        self,
        diagnosis: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = build_diagnosis_prompt(diagnosis)

        schema = {
            "type": "object",
            "properties": {
                "headline": {
                    "type": "string"
                },
                "what_happened": {
                    "type": "string"
                },
                "why_it_matters": {
                    "type": "string"
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "recommended_action": {
                    "type": "string"
                },
                "limitations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
            },
            "required": [
                "headline",
                "what_happened",
                "why_it_matters",
                "evidence",
                "recommended_action",
                "limitations",
            ],
            "additionalProperties": False,
        }

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "bizlens_explanation",
                    "strict": True,
                    "schema": schema,
                }
            },
        )

        return json.loads(response.output_text)

    def ask(
        self,
        question: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = build_ask_prompt(
            question,
            context,
        )

        schema = {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string"
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "limitations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
            },
            "required": [
                "answer",
                "evidence",
                "limitations",
            ],
            "additionalProperties": False,
        }

        response = self.client.responses.create(
            model=self.model,
            instructions=ASK_SYSTEM_PROMPT,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "bizlens_ask",
                    "strict": True,
                    "schema": schema,
                }
            },
        )

        return json.loads(
            response.output_text
        )
