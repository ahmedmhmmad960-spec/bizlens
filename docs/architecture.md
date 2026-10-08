# BizLens Architecture

## System boundary

BizLens separates business computation from language generation.

```text
                    ┌─────────────────────┐
                    │   Next.js Web App   │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Analysis Service   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Metrics Engine   Diagnosis Engine   Evidence
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                     Confidence + Ranking
                               │
                               ▼
                     Structured Diagnosis
                               │
                               ▼
                         AI Provider
                               │
                               ▼
                      Human Explanation
```

## Layer responsibilities

### API

The API layer owns HTTP concerns: request validation, file handling, status responses and transport-level errors. It should not contain diagnosis calculations.

### Analysis Service

The analysis service orchestrates a complete analysis. It connects deterministic engines and AI interpretation without exposing HTTP concerns to the core domain.

### Deterministic core

The core owns business facts:

- normalization
- metrics
- period comparisons
- diagnosis triggers
- evidence
- confidence
- ranking
- diagnosis chains
- reports

A diagnosis rule should be reproducible from the same input data.

### AI layer

The AI layer receives verified diagnosis context. It can explain a supported finding and formulate a recommendation within the supplied evidence boundary. It must not become the calculator for business metrics.

## Evidence contract

A useful diagnosis should expose:

```text
Signal
  ↓
Calculation
  ↓
Evidence
  ↓
Interpretation
  ↓
Impact
  ↓
Confidence
  ↓
Recommended action
```

If evidence is incomplete, BizLens should lower confidence or explicitly report that the available data is insufficient.

## Current persistence boundary

The v0.1 API uses an in-memory analysis store. This is intentional for the prototype and local demo. It is not the production persistence strategy.

The future persistence boundary should allow the analysis service to use a durable store without moving storage logic into diagnosis rules or UI components.

## Design goals

1. Keep business calculations deterministic.
2. Keep diagnosis rules testable without an LLM.
3. Keep the API thin.
4. Keep AI providers replaceable.
5. Keep evidence inspectable by users and developers.
6. Prefer explicit domain types over generic dictionaries at public boundaries.
