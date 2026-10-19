"""Live HTTP smoke of Next.js -> FastAPI -> deterministic analysis -> ask.

Run while the web app is listening on 127.0.0.1:3000 and the local API on
127.0.0.1:8000. Uses standard library only; NEVER invokes an AI service.
CI explicitly clears the optional paid-provider environment variables.
"""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
WEB_URL = os.getenv("BIZLENS_WEB_URL", "http://127.0.0.1:3000").rstrip("/")
BOUNDARY = "BizLensDemoJourneyBoundary"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def request(path: str, data: bytes | None = None, content_type: str | None = None):
    headers = {"Content-Type": content_type} if content_type else {}
    verb = "POST" if data is not None else "GET"
    req = Request(WEB_URL + path, data=data, headers=headers, method=verb)
    try:
        with urlopen(req, timeout=25) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def ready() -> None:
    for _ in range(100):
        try:
            status, html = request("/")
            if status == 200 and b"BizLens" in html:
                return
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Next.js app did not become ready at {WEB_URL}")


def upload_csv(contents: bytes, name: str = "store.csv") -> dict:
    prefix = (
        f"--{BOUNDARY}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode("ascii")
    body = prefix + contents + f"\r\n--{BOUNDARY}--\r\n".encode("ascii")
    status, response = request(
        "/api/analyze",
        body,
        f"multipart/form-data; boundary={BOUNDARY}",
    )
    check(status == 200, f"Unexpected analysis HTTP status: {status}: {response[:250]!r}")
    return json.loads(response)


def ask(analysis_id: str, question: str) -> dict:
    body = json.dumps({"analysis_id": analysis_id, "question": question}).encode()
    status, raw = request("/api/ask", body, "application/json")
    check(status == 200, f"Ask API returned HTTP {status}: {raw[:250]!r}")
    return json.loads(raw)


def main() -> None:
    ready()
    print("PASS: Next.js landing responds")

    csv = (ROOT / "apps/web/public/demo/store.csv").read_bytes()
    status, served = request("/demo/store.csv")
    check(status == 200 and served == csv, "Demo download must serve the exact committed CSV")
    print("PASS: demo fixture served unchanged")

    result = upload_csv(csv)
    check(result.get("success") is True, f"Demo upload failed: {result.get('error')}")
    analysis_id = result.get("analysis_id")
    check(isinstance(analysis_id, str) and analysis_id, "Missing analysis id")
    analysis = result["analysis"]
    metrics = analysis["metrics"]
    check(
        (metrics["revenue"], metrics["orders"], metrics["cost"], metrics["gross_profit"])
        == (1560.0, 10, 990.0, 570.0),
        f"Incorrect demo business totals: {metrics}",
    )
    check(analysis["data_quality"]["order_count_basis"] == "order_id", "Lost order grain")
    check(analysis["data_quality"]["currency"] == "unspecified", "Currency invented")
    check(
        len(analysis["quarterly_trend"]) == 1
        and analysis["quarterly_trend"][0]["period"] == "2026-Q3",
        "Demo CSV must yield one observed calendar quarter",
    )
    print("PASS: CSV upload through Next.js proxy and deterministic financial facts")

    expected = result["top_diagnoses"]
    check(expected and result["diagnoses"], "Demo did not produce evidence-backed signals")
    report = result["business_report"]
    check(report["metrics"] == metrics, "Report totals differ from analysis")
    check(report["quarterly_trend"] == analysis["quarterly_trend"], "Chart/report mismatch")
    check(
        isinstance(report["summary"], dict)
        and isinstance(report["summary"].get("headline"), str),
        "Report summary is not an explicit headline object",
    )
    check(report["recommended_actions"], "Demo report has no recommended actions")
    replay = result["demo_replay"]
    check(replay["total_steps"] == len(replay["steps"]) == 10, "Replay steps missing")
    by_step = {s["key"]: s["data"] for s in replay["steps"]}
    check(by_step["business_metrics"] == metrics, "Replay totals diverge")
    check(by_step["business_report"] == report, "Replay report diverges")
    check(by_step["what_changed"] == result["what_changed"], "Observed signals diverge")
    print("PASS: diagnoses, evidence, chart data, executive summary, report and replay")

    response = ask(analysis_id, "Why did the margin change?")
    check(response.get("success") is True, f"Ask failed: {response.get('error')}")
    answer = response.get("answer", {})
    check("1560" in answer.get("answer", ""), "Ask did not use actual revenue context")
    check("570" in answer.get("answer", ""), "Ask did not use actual profit context")
    check(answer.get("evidence"), "Ask did not provide diagnostic evidence")
    check(answer.get("limitations"), "Fallback mode not clearly disclosed")
    print("PASS: Ask BizLens round-trip uses the same stored analysis without AI keys")

    wrong = ask("not-an-analysis", "What happened?")
    check(wrong.get("success") is False, "Unknown analysis id should fail")
    blank = ask(analysis_id, "   ")
    check(blank.get("success") is False, "Blank question should fail")
    invalid = upload_csv(b"order_id,revenue,cost\n1,1.005,1.00\n")
    check(
        invalid.get("success") is False
        and "more than two decimal places" in invalid.get("error", ""),
        "Sub-cent upload was not rejected through web proxy",
    )
    wrong_format = upload_csv(b"hello", "report.txt")
    check(wrong_format.get("success") is False, "Non-CSV upload should fail")
    print("PASS: invalid questions, unknown sessions and misleading CSV data fail safely")

    print("DEMO_HTTP_JOURNEY: PASS")


if __name__ == "__main__":
    main()
