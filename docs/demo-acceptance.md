# BizLens demo acceptance: release gate V1

This document separates **proven automated coverage** from the **human
browser walkthrough** required before announcing a public demo. Never
treat passing unit tests or successful Next.js builds as proof the entire
visual interaction works.

## Deterministic offline HTTP journey

The `Live demo HTTP journey` CI job starts the *built Next.js app* and
the FastAPI server with an explicitly disabled external AI provider.
`scripts/demo_http_smoke.py` then verifies the actual HTTP chain:

1. Open the Next.js landing page and fetch the exact committed demo CSV.
2. POST that CSV to `/api/analyze` via Next.js, forwarding to FastAPI.
3. Verify independently audited figures: **revenue 1560.00**,
   **cost 990.00**, **gross profit 570.00**, **10 distinct orders**.
4. Confirm the observed quarter is `2026-Q3`, with no fictitious
   empty-quarter data or currency.
5. Check diagnoses, evidence, report, recommended actions and replay
   reuse exactly the same calculated figures and what-changed observations.
6. POST a question to `/api/ask` using the analysis id returned in step 2.
   Confirm the rule-based answer uses the actual stored figures, includes
   evidence and explicitly reports that fallback reasoning is limited.
7. Reject unknown analysis ids, blank questions, sub-cent CSV amounts
   and wrong file extensions without inventing an analysis session.

In-process `tests/e2e/test_demo_journey.py` covers the same API lifecycle
under pytest and isolates stored sessions and providers per test.

This test makes **real local HTTP requests**, but it does **not** control
a graphical browser or perform a visual comparison against Figma.

## Human browser acceptance checklist (required before public launch)

Start a fresh preview of the tested branch in a separate Codespace or
worktree, leaving dirty main files untouched. Use the local rule-based
provider; **do not configure paid-model environment variables**.

- [ ] Desktop: landing → select Full Diagnosis → Try demo dataset →
  Understand my data → Data quality → 10 Replay steps → Overview.
- [ ] Overview: revenue **1560**, gross profit **570**, ten orders and
  gross margin correctly displayed. Quarterly Revenue-vs-Profit and Margin
  charts must reflect the **single observed 2026-Q3** quarter.
- [ ] Feed and What Changed: diagnoses and evidence correspond to the
  imported dataset; Observed Signals labels midpoint periods honestly.
- [ ] Ask BizLens: ask about margin change, confirm a grounded explanation,
  limitations and a route to the report. Do not claim this fallback is
  a fully reasoning AI model.
- [ ] Report: show the **executive headline**, *never* `[object Object]`;
  preserve diagnosed findings, action recommendations and limitations.
- [ ] Invalid CSV: show a readable error on the upload screen without
  losing the ability to try another file.
- [ ] Mobile viewport (~375px): no accidental page overflow, unreadable
  chart labels, overlapping buttons or unusable upload controls.
- [ ] Keyboard: navigate file picker, next/back, Ask and report;
  focus indicators are visible, chart values available as text.
- [ ] Print/Save PDF uses the browser print dialog and outputs a usable
  document; visual quality and page breaks require manual inspection.

## Known constraints, not silent pass criteria

- The current default `store.csv` is **August 2026 only**. It legitimately
  produces **one quarter** of chart data; it cannot show a multi-quarter
  trend. A separate realistic multi-quarter demo fixture should be
  prepared before showcasing time trends.
- The legacy What Changed engine compares chronological halves, **not
  calendar quarters**.
- The deterministic no-key Ask fallback summarizes verified facts but
  is not a substitute for open-ended LLM reasoning.
- Browser render, PDF print layout, animation and Figma fidelity are
  **not covered** by the HTTP CI job.
- The in-memory analysis store is suitable for local demo only; production
  deployment needs explicit state retention, size limits and privacy controls.

## Local reproducible smoke

With the project checked out and Python/Node dependencies installed,
run the servers in separate terminal sessions:

```bash
OPENAI_API_KEY= BIZLENS_AI_MODEL= python -m uvicorn apps.api.app.main:app --reload --port 8000
```

```bash
cd apps/web
BIZLENS_API_URL=http://127.0.0.1:8000 npm run dev
```

Then `python scripts/demo_http_smoke.py` from the repository root;
open the forwarded port 3000 for the human browser checklist.
