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
API_URL = os.getenv("BIZLENS_API_URL", "http://127.0.0.1:8000").rstrip("/")
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
    """Both services must be live; the web landing can boot before FastAPI."""
    for _ in range(120):
        try:
            status, html = request("/")
            with urlopen(f"{API_URL}/health", timeout=3) as api_response:
                healthy = (
                    api_response.status == 200
                    and json.load(api_response).get("status") == "healthy"
                )
            if status == 200 and b"BizLens" in html and healthy:
                return
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for both Next.js {WEB_URL} and API {API_URL}")


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
    _, landing = request("/")
    check(b"See your business" in landing, "Brand headline is missing from the SSR landing")
    check(b"Try Interactive Demo" in landing, "Approved one-click demo CTA is missing")
    check(b"Explore a diagnosis" in landing, "Secondary landing action is missing")
    print("PASS: Next.js landing and approved visual-entry contract respond")

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

    # Optional Base evidence adapter must stay synthetic / disabled in default CI.
    base_status, base_raw = request("/api/base-usdc/demo")
    check(base_status == 200, "Base synthetic fixture API did not respond")
    base_fixture = json.loads(base_raw)
    check(base_fixture.get("success") is True, "Base synthetic adapter did not succeed")
    check(base_fixture.get("source") == "synthetic_fixture", "Base fixture lacks provenance")
    check(base_fixture.get("real_transaction") is False, "Synthetic transaction mislabelled")
    check(base_fixture.get("onchain_verified") is False, "Fabricated onchain proof")
    check(
        [item["status"] for item in base_fixture["results"]]
        == ["candidate_match", "partial", "missing"],
        "Base example status did not use deterministic matching",
    )
    print("PASS: independent Base USDC synthetic evidence behind real Next API")

    inspect_payload = {
        "invoice_id": "SYNTH-001", "chain_id": 84532,
        "recipient": "0x" + "a" * 40,
        "amount_usdc": "12.345678",
        "tx_hash": "0x" + "1" * 64,
        "log_index": 0,
    }
    base_status, base_raw = request(
        "/api/base-usdc/inspect",
        json.dumps(inspect_payload).encode(), "application/json",
    )
    check(base_status == 503, "Public Base RPC must be opt-in, not active in CI")
    check(json.loads(base_raw).get("mode") == "disabled", "RPC disable reason missing")
    print("PASS: disabled live Base RPC cannot fabricate settlement in default CI")

    # The Next.js proxy must reject oversized or mislabeled input BEFORE FastAPI/RPC.
    oversized = json.dumps({**inspect_payload, "invoice_id": "X" * 2500}).encode()
    big_status, big_raw = request("/api/base-usdc/inspect", oversized, "application/json")
    check(big_status == 413, "Inspector must reject oversized input at Next.js boundary")
    check(json.loads(big_raw)["success"] is False, "Oversized request accepted")
    content_status, content_raw = request(
        "/api/base-usdc/inspect", b"not-json", "text/plain",
    )
    check(content_status == 415, "Inspector must reject non-JSON requests at web boundary")
    check(json.loads(content_raw)["success"] is False, "Non-JSON request accepted")
    print("PASS: Next.js Base inspector rejects large/non-JSON payloads before RPC")

    print("DEMO_HTTP_JOURNEY: PASS")


if __name__ == "__main__":
    main()
