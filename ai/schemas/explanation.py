from typing import TypedDict


class BizLensExplanation(TypedDict):
    headline: str
    what_happened: str
    why_it_matters: str
    evidence: list[str]
    recommended_action: str
    limitations: list[str]
