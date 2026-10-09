from io import StringIO

import pandas as pd
from ai.client.rule_based_provider import RuleBasedProvider
from core.analysis.service import AnalysisService


DEMO_CSV = """order_id,date,customer_id,product_id,quantity,revenue,discount,cost
1,2026-08-01,C001,P001,1,120,10,60
2,2026-08-02,C002,P002,2,200,20,130
3,2026-08-03,C001,P001,1,120,0,60
4,2026-08-04,C003,P003,1,80,15,50
5,2026-08-05,C004,P002,1,100,10,65
6,2026-08-06,C005,P004,1,150,30,100
7,2026-08-07,C002,P002,1,100,0,65
8,2026-08-08,C006,P005,1,300,50,240
9,2026-08-09,C007,P001,2,240,20,120
10,2026-08-10,C008,P004,1,150,0,100
"""


def test_analysis_service_returns_complete_contract() -> None:
    df = pd.read_csv(StringIO(DEMO_CSV))
    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(df)

    assert result["success"] is True
    assert result["analysis_id"]
    assert result["analysis"]["metrics"]["revenue"] == 1460
    assert isinstance(result["diagnoses"], list)
    assert len(result["top_diagnoses"]) <= 3
    assert result["demo_replay"]["total_steps"] == 10
    assert result["business_report"]


def test_analysis_service_never_requires_an_external_ai_provider() -> None:
    df = pd.read_csv(StringIO(DEMO_CSV))
    result = AnalysisService(RuleBasedProvider()).analyze_dataframe(df)

    assert result["ai_explanations"]
    assert all("ai" in item for item in result["ai_explanations"])
