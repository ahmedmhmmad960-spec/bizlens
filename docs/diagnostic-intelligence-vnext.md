# BizLens — Diagnostic Intelligence Engine vNext

> Architecture / delivery specification. Nothing below should be presented as shipped until tests and demonstrations prove it.  
> Scope: evolve the **existing** explainable deterministic diagnosis engine. Do not replace it with unconstrained LLM decisions.  
> Project priority: **correctness and trust before diagnosis count**.

## Goal

Evolve BizLens from detecting isolated metrics to a dependable **evidence → hypotheses → impact → decision options → measured outcomes** loop.

A useful user interaction is:
1. **What changed?** Report a reproducible metric or signal and its time window.
2. **What supports that?** Show calculations, source rows and data quality.
3. **Why might it have changed?** Rank competing hypotheses, distinguish correlation from proven causation, ask for missing evidence.
4. **What can we do?** Show plausible actions, cost/risk/trade-offs and forecast uncertainty.
5. **What happened after action?** Record the action and observed outcome without claiming unjustified model learning.

## Read-only source review (main, 2026-10-13)

- `core/metrics/engine.py`: numeric conversion uses `errors="coerce"` followed by `fillna(0)` **before** reporting `missing_values`, obscuring invalid vs legitimate zero numeric cells; date midpoint split may produce unequal/incomparable periods; `orders = len(df)` is only a valid count for an explicitly *one-row-per-order* schema, not line-item CSVs.
- `core/confidence/engine.py`: confidence increases when `severity == "high"`, making urgency/magnitude appear to increase evidence quality; the score is heuristic, not statistically calibrated.
- `core/chains/engine.py`: when diagnoses co-occur, the textual explanation sometimes claims one factor **caused/contributed** to another without a standalone causal identification step.
- `core/evidence/engine.py`: evidence is grouped from diagnosis dictionaries but generally lacks first-class source-row provenance and calculation-version references.
- `core/analysis/service.py`: only five detectors currently wired; a foundation already exists for confidence, ranking, chains, replay, report and explanatory AI.
- `core/ranking/priority.py`: heuristic impact × confidence × urgency priority is useful but must be explainable and validated against business magnitude and data completeness.

These are code inspection findings, not claims of completed test runs or known user-facing failures. Confirm behavior with regression tests before fixes.

## Workstream A — Data semantics and input integrity (blocker for all other work)

- [ ] Introduce explicit input schema and unit semantics: row grain (orders vs line items), currency, timezone, date column, cost/discount conventions (gross vs net revenue), refunds, cancellations.
- [ ] Keep distinct states: absent, malformed, unknown, legitimate zero. Never silently convert malformed finance numbers to zero. Report per-column completeness, coercion counts and duplicated IDs.
- [ ] Validate duplicate orders/transactions; detect date gaps/outliers without ungrounded imputation.
- [ ] Define period comparisons with comparable durations and coverage; report partial periods and missing dates.
- [ ] Prevent invalid denominator use, misleading percentage changes from zero baselines, and accidental double-counting.
- [ ] Build golden fixtures: missing and malformed values, no dates, duplicates, negative entries/refunds, identical periods, uneven period coverage, row-grain ambiguity.

**Exit criteria:** every computed metric has a verified unit, calculation and source provenance; ambiguous inputs produce warnings or abstention, never false precision.

## Workstream B — First-class diagnosis and evidence contracts

- [ ] Define typed `DiagnosisFinding` with stable IDs/version, scope/segment, time range, observed signal, exact computation, evidence refs, data limitations, plausible hypotheses, severity, impact and confidence **as distinct fields**.
- [ ] Create verifiable evidence trails: original row identifier, relevant aggregated subset, calculation version, compared periods and clear human explanation.
- [ ] Treat severity as potential business impact, confidence as quality of support, probability as a separate calibrated quantity only when justified.
- [ ] Use explicit epistemic states: `observed`, `associated`, `hypothesized`, `causally_identified`, `insufficient_evidence`. Never silently promote states.
- [ ] Require null/abstain rather than invent confidence or missing attributes; add reproducibility/version tests.

**Exit criteria:** each displayed diagnosis can be reproduced from a data fixture, with a limitation shown when evidence is weak.

## Workstream C — Deep diagnosis / drivers, not just alarms

- [ ] Quantify segment-level drivers for gross profit and margin by product/category/channel/period **only when data is available**.
- [ ] Separate volume, price, unit-cost, discount and mix effects when decomposition assumptions are satisfied; residual must be reported if exact attribution is impossible.
- [ ] Group redundant symptoms into a hypothesis graph; competing explanations should be ranked by strength of observed evidence and marked *unverified* when appropriate.
- [ ] Add checks for seasonality, period imbalance, mix shifts and measurement errors before attributing blame.
- [ ] Prioritize estimated economic impact (explicit currency) + actionable urgency + evidence strength, not only a synthetic score.

**Exit criteria:** in benchmark cases, the engine flags known drivers without false causal claims and ranks the material problems correctly.

## Workstream D — Decision intelligence, with honest uncertainty

- [ ] Attach multiple decision options and trade-offs: likely benefit, implementation cost, operating risk and what evidence is missing.
- [ ] Decision Twin v1: deterministic what-if calculations with declared assumptions, sensitivity ranges and **no predictive guarantees**. Do not imply counterfactual outcomes are measured facts.
- [ ] Require human confirmation before any external action (pricing, operations or payments).
- [ ] Preserve Show Me Why / Diagnosis Chains / Replay / Ask BizLens. Ask BizLens must cite the analyzed evidence and say when an answer is outside it.

**Exit criteria:** a user can compare at least two actions with visible assumptions and limitations using the same reproducible example.

## Workstream E — Business Memory and Outcome Learning

- [ ] Record diagnosis version, evidence snapshot, decision taken, owner/time, expected KPI and measurement date.
- [ ] Compare outcomes on clearly comparable windows; separate observed association from demonstrated effect and note confounders.
- [ ] Build opt-in, privacy-preserving feedback/evaluation; do not train models on customers' data silently.
- [ ] Measure observed forecast error / usefulness over time before claiming that the system "learns" or has better causal reasoning.

**Exit criteria:** replay the original analysis, decision and observed follow-up from a reproducible trace.

## Workstream F — Optional Base-specific evidence

Use a separate adapter for USDC/Base transaction evidence. Preserve the general commercial diagnosis core; include chain/network verification and reconciliation provenance. A payment discrepancy is an observable mismatch, **not** proof of fraud or misconduct.

## Test and evaluation approach

- Golden cases with **known** expected findings and **negative cases** that must **not** trigger diagnoses.
- Track precision, recall, severity errors, abstention correctness, duplicate finding rate, attribution coverage, stability across equivalent row ordering, and evidence correctness on a representative fixture corpus.
- Separate unit, metamorphic/property-based, integration and user-explanation tests.
- Add regressions for every discovered bug. Run CI for frontend/backend, plus deterministic-output snapshots where appropriate.
- Have domain experts review a small labeled evaluation set; document sample size and limitations. Avoid promising accuracy percentages until measured.
- No live customer data or API secrets in demo or CI.

## Implementation order / acceptance gates

1. **P0 — Trust fixes**: tests documenting numeric missingness, row granularity, periods, confidence/severity coupling, causal-language overclaim, and evidence provenance.
2. **P1 — Structured brain**: typed diagnosis/evidence contracts; reproducibility; data quality and reliable explanations.
3. **P2 — Diagnostic depth**: independent driver decomposition, hypothesis ranking, uncertainty and duplicate suppression.
4. **P3 — Decision Twin**: transparent what-if analysis and action prioritization.
5. **P4 — Outcome feedback**: decision memory, evaluation and privacy boundaries.
6. **P5 — Base adapter**: onchain evidence and economic reconciliation; keep independently reusable/open source.

**No code edits in this document-only PR.** Implement in small, separately tested PRs after inspection of the active workspace and team assignment in OpenCode; protect the existing Morph setup and stay on no-extra-spend model routes.

## Grant narrative

A credible public-good contribution is a transparent, reusable **trustworthy diagnosis and evidence library** with reproducible tests, plus an independently useful Base/USDC reconciliation adapter. Describe real shipped code, tests, developers served and usage evidence; never claim "AI discovers root causes" or "learning works" absent evaluation.
