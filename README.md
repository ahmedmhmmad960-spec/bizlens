# BizLens

> **See your business clearly.**
>
> Open-source AI business diagnosis engine for turning business data into evidence-backed explanations and actionable decisions.

BizLens is built around a simple principle: **deterministic systems calculate and validate business facts; AI interprets those verified facts.**

It is not a dashboard that leaves the owner to interpret charts. BizLens analyzes business data, detects meaningful signals, connects them into diagnoses, shows the evidence, communicates confidence and impact, and recommends the next action.

## Why BizLens

Small businesses often have the data but not a dedicated data team. BizLens aims to make business diagnosis accessible through an open, inspectable engine.

The core loop is:

```text
Observe → Diagnose → Explain → Act → Measure → Learn
```

The v0.1 product flow is intentionally narrow:

```text
CSV → Analysis → Diagnosis → Evidence → Explanation → Action
```

## How it works

```text
Business Data
     ↓
Ingestion & Validation
     ↓
Deterministic Metrics
     ↓
Signals & Diagnosis Rules
     ↓
Evidence + Confidence + Impact
     ↓
Structured Diagnosis
     ↓
AI Interpretation
     ↓
Human-readable Explanation
     ↓
BizLens UX
```

### AI boundary

AI is **not** the source of truth for business calculations.

BizLens keeps calculations such as revenue, cost, gross profit, gross margin, comparisons, evidence and confidence inside deterministic application code. The AI layer receives verified diagnosis context and turns it into human-readable explanations and recommendations.

This boundary is deliberate: a language model should not silently change a business metric or invent a diagnosis that the data does not support.

## Current capabilities

- CSV business-data ingestion
- Data validation and normalization
- Deterministic business metrics
- Business diagnosis rules
- Evidence generation
- Confidence scoring and limitations
- Diagnosis ranking
- Diagnosis chains
- Period-change analysis
- AI explanations with a rule-based fallback
- Grounded Ask BizLens context
- Business report generation
- Analysis replay
- Next.js web experience
- FastAPI backend

## v0.1 diagnosis focus

The first diagnosis engine focuses on high-value ecommerce signals such as:

- Gross margin decline
- Revenue growth without profit growth
- Cost pressure
- Discount pressure
- Product-level revenue/profit signals when the data supports them

BizLens follows a strict rule: **never invent a business problem.** If the available data is insufficient, the system should say so.

## Repository structure

```text
bizlens/
├── apps/
│   ├── api/                 # FastAPI application
│   └── web/                 # Next.js application
├── core/
│   ├── ingestion/           # Input validation and normalization
│   ├── metrics/              # Deterministic business calculations
│   ├── diagnoses/            # Diagnosis rules
│   ├── evidence/             # Evidence construction
│   ├── confidence/           # Confidence scoring
│   ├── ranking/              # Diagnosis prioritization
│   ├── chains/               # Connected diagnosis signals
│   ├── changes/              # Period comparisons
│   ├── reports/              # Business report generation
│   └── replay/               # Analysis replay
├── ai/
│   ├── client/               # AI providers
│   └── prompts/              # AI instructions
├── demo/                     # Demo datasets
├── tests/                    # Automated tests
├── docs/                     # Architecture and engineering docs
└── .github/                  # CI and repository automation
```

## Run locally

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn apps.api.app.main:app --reload --port 8000
```

The API exposes:

- `GET /health`
- `POST /analyze`
- `POST /ask`

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

Then open the local Next.js URL shown by the terminal.

## Testing

Python tests:

```bash
pytest
```

Frontend checks:

```bash
cd apps/web
npm run lint
npm run build
```

CI runs the same core checks on every pull request and push to `main`.

## Engineering principles

1. **Deterministic before generative.** Business facts are calculated by code, not by an LLM.
2. **Evidence before explanation.** Every diagnosis should be traceable to data.
3. **Confidence is explicit.** Weak or incomplete evidence should reduce confidence.
4. **No unsupported causality.** A possible driver is not presented as a proven cause without evidence.
5. **Typed contracts.** Business-domain structures should be explicit and testable.
6. **Small surface area.** Build the foundation for the long-term product without prematurely building every feature.
7. **Open and inspectable.** The core diagnosis engine is intended to be understandable, reusable and extensible.

## Roadmap

### v0.1 — Open diagnosis core

CSV analysis, diagnosis, evidence, confidence, explanation, actions and reporting.

### Later

- Business Memory
- What-If analysis
- Direct platform integrations
- Benchmarking
- Outcome/evaluation learning
- Hosted and commercial capabilities

These are roadmap directions, not requirements for the current open-source core.

## Contributing

Contributions are welcome. Before proposing a new diagnosis rule, document:

- the business problem it detects
- the exact trigger
- the calculation
- the evidence required
- limitations and confidence conditions
- the recommended action
- tests covering positive and negative cases

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

Please do not publish credentials, API keys, customer data or sensitive business datasets in issues or pull requests. See [`SECURITY.md`](SECURITY.md).

## License

BizLens is released under the MIT License. See [`LICENSE`](LICENSE).
