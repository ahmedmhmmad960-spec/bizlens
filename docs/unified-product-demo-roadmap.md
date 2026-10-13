# BizLens Unified Product Blueprint — Demo, Funder Roadmap & Code

**Status:** proposed build specification; only explicitly verified existing capabilities should be called "implemented".  
**Date:** 2026-10-13  
**Narrative:** Evidence-to-Outcome Decision Intelligence  
**Core principle:** compute business facts deterministically; let AI interpret verified evidence but never silently invent numbers or causality.

## 1. One product, not six grant-driven forks

BizLens is an open-source business diagnosis and decision intelligence platform that helps operators go from business data to defensible diagnoses, transparent options and observed outcomes.

**Unified user journey:** Understand → Diagnose → Prove → Investigate → Decide → Measure → Learn.

**Domains** share one core:
- **Commerce:** revenue, costs, products, discounts, margin, profit and business diagnostics.
- **Digital Business:** invoices, cash collection, subscriptions and revenue-to-cash discrepancies.
- **Web3/Base:** transparent USDC onchain evidence and reconciliation — optional, independent module.

**Delivery modes**
- **Community:** genuinely useful MIT/open-source and self-hostable with metrics, evidence, diagnosis, basic decision comparison and export; no accuracy/evidence paywall.
- **Cloud:** later managed deployment, connectors, automated sync, monitoring, teamwork, permissions, support and operations, subject to compatible license and legal eligibility.

**Not in the first demo:** ERP/general ledger, card acquiring, bank custody, autonomous changes to business/payment accounts, complete accounting, marketplace, benchmarking, broad third-party intelligence.

## 2. Repository facts versus roadmap

Read-only review of `main` as of 2026-10-13 shows:
- Python FastAPI API, Next.js web app, deterministic metrics, 5 registered diagnosis detectors, evidence, confidence, ranking, diagnosis chains, period comparisons, reports and demo replay, rule-based explanation fallback and Ask BizLens UI/API hooks.
- Current UI flow in `apps/web/app/page.tsx`: entry → diagnosis workflow → overview → diagnosis feed → what changed → Ask BizLens → report.
- Existing demo CSV files and backend/frontend CI; MIT LICENSE.

**Not verified as production-ready:** active deployed public demo, fully passing current CI, statistically calibrated confidence, evidence row-level lineage, live Base/USDC onchain ingest, Decision Twin, durable Business Memory, measured Outcome Learning, real users/traction. Do not imply these are already shipped.

## 3. Flagship 6–8 minute demo (synthetic dataset, clearly labeled)

**Demo name:** "Why did sales grow while profit and collected cash deteriorated?"

The scenario uses a **synthetic** digital storefront/SaaS business with illustrative figures only; create golden CSV fixtures and expected answers before recording.

1. **Ask**: choose Full Diagnosis or type "Why are sales up while profit and cash are down?" Show supported vs unsupported query scope.
2. **Load data**: orders/revenue/cost/discount CSV; invoice ledger CSV; crypto payout/transaction evidence CSV or documented Base testnet fixtures. No live customer or bank data.
3. **Understand & trust**: detect data schema, row grain, currency, missing and malformed cells, duplicates, incomplete periods; demonstrate explicit warnings and abstention, never zero-fill malformed money.
4. **Diagnose**: compare valid periods and identify (when supported) gross margin decline, cost/discount pressure, top product loss, invoiced-vs-collected gap and unmatched USDC invoice payments.
5. **Show Me Why**: show precise calculations, source rows, transaction references, version/time window, confidence, limitations and possible *noncausal* explanations. Show a false-positive avoided.
6. **Diagnosis Chains**: group related symptoms and rank alternative hypotheses with labels: observed / associated / hypothesized / insufficient evidence. Avoid falsely claiming causation.
7. **Ask BizLens**: ask a natural-language follow-up; answer only from verified context with evidence references and an "I can't determine that" example.
8. **Decision Twin v1**: compare two transparent, bounded scenarios (e.g., reduce discount rate versus prioritize recovering overdue invoices) with explicit assumptions, sensitivity and no promises of future returns.
9. **Business Memory and Outcome Replay**: record chosen action/assumptions; compare against a **separate synthetic future period** to demonstrate measurement and explicitly describe that as simulated history, not real model learning.
10. **Final report**: export/share digest of findings, evidence, proposed action, uncertainties, grant/public-good relevance and reproducibility link.

**Success criteria for demo:** a viewer can reproduce every reported metric; demo runs without paid AI; all synthetic data labeled; show at least one justified abstention; at least two decision options; report and tests link to relevant fixtures.

## 4. Visual mock-up / navigation target

Navigation:
- **Home / Diagnose:** entry and dataset wizard
- **Overview:** key metrics, confidence and data quality
- **Findings:** ranked diagnosis cards + impact
- **Show Me Why:** expandable evidence trail and source references
- **Causes / Hypotheses:** alternatives, required tests and limitation state
- **Decision Twin:** scenario sliders/inputs and side-by-side result ranges
- **Business Memory:** decisions, targets, status and outcomes
- **Ask BizLens:** evidence-constrained chat
- **Reports:** reproducible exports, notes and limitations
- **Base / Payments Evidence:** optional USDC matching and chain provenance

Target UX is a walkthrough of one actual question end-to-end, not 10 unrelated dashboards.

## 5. Roadmap with objective acceptance gates, for funders

| Phase | Deliverable | Public evidence / acceptance |
|---|---|---|
| **0. Foundation trust** | Reconcile current repo/branch/local workspace; run CI/tests; fix missing-value, period, row-grain, evidence-confidence semantics without regressions | tests, benchmark fixtures, CI logs, meaningful changelog |
| **1. Diagnostic Brain vNext** | Typed evidence/diagnosis contracts; traceability, hypothesis & driver analysis, stable priority rankings | versioned schema, reproducible golden examples, negative-case tests and labeled limitations |
| **2. Premium Community Demo** | Polished, self-hostable full decision narrative, Show Me Why/Ask BizLens/Replay/report | reproducible end-to-end demo, screenshots, short walkthrough, accessible docs |
| **3. Decisions & outcomes** | Honest Decision Twin with sensitivity, durable Business Memory and observable Outcome Learning | two alternatives per supported case, versioned assumptions, replayed synthetic before/after and uncertainty |
| **4. Base public-good adapter** | Open-source USDC matching and provenance, invoice/ledger matching, missing/duplicate/partial payments | standalone MIT module, documented network verification, chain-mismatch/duplicate tests, example integration |
| **5. Community & grant proof** | Onboard real pilot testers, gather consented feedback, publish uses/contributions, budgets and milestone updates | verifiable testimonials only with permission, issue/release activity, transparent budget and source links |
| **6. Hosted business** | Optional Cloud hosting/secure connectors/team UX; explore merchant-of-record processor only after residency/KYC/payout eligibility is confirmed | privacy/security review, operational SLO evidence, provider contract; revenue is NOT a grant requirement |

**Order can be adapted to real round deadlines without sacrificing core accuracy.** Public grant milestones should claim only deliverables that can genuinely be achieved and demonstrated.

## 6. Six-grant packaging matrix

- **Base Builder Grants:** ship and demonstrate a real Base/USDC utility, onchain provenance, working demo and ecosystem benefit; follow current published tax/KYC and program-specific eligibility rules.
- **Gitcoin:** MIT repo, meaningful GitHub history, Ethereum public-good value, honest contributors/users and authentic donor support; check the actual open round.
- **Giveth:** a directly useful and transparent public-good Community offering, trustworthy beneficiary wallet, public updates and clear use of donations; verification tier is not automatic.
- **Ethereum Foundation ESP:** proposal for standalone free/open Ethereum builder infrastructure, concrete technical methods/tests/milestones/budget; distinguish this from financing the commercial Cloud.
- **Octant:** invite/verification, credible public-good impact, owned project wallet, milestones, community evidence and clear cost categories.
- **Drips:** prove repo ownership/maintenance, real public code and community value, and appropriately configure `FUNDING.json` only after verifying wallet metadata.

Not every funder will fund the whole platform: propose the eligible public-good component, with shared evidence package and individualized budget.

## 7. Target code structure — additions are planned, not existing

```text
bizlens/
├─ apps/
│  ├─ web/                          # existing Next.js UX; gradually extend
│  └─ api/                          # existing FastAPI; version contracts
├─ core/
│  ├─ ingestion/                    # existing; strengthen parsing / row grain
│  ├─ metrics/                      # existing deterministic mathematics
│  ├─ diagnoses/                    # existing detectors; expand carefully
│  ├─ evidence/                     # existing; add provenance and trace IDs
│  ├─ confidence/                   # existing; decouple severity
│  ├─ ranking/, chains/, changes/   # existing; guard causal claims
│  ├─ reports/, replay/             # existing; preserve
│  ├─ data_quality/                 # proposed
│  ├─ hypotheses/                   # proposed
│  ├─ decisions/                    # proposed Decision Twin
│  ├─ business_memory/              # proposed outcomes/decision log
│  └─ evaluation/                   # proposed benchmark + quality metrics
├─ integrations/
│  └─ base_usdc/                    # proposed optional standalone adapter
├─ ai/
│  ├─ client/                       # existing replaceable provider boundary
│  └─ prompts/                      # grounded explanation instructions
├─ demo/                            # existing CSV + proposed synthetic cases
├─ tests/                           # existing + new diagnostic/evidence/decision/base tests
└─ docs/                            # architecture, grant plan, demos & budgets
```

### Contracts to implement and test

```text
AnalysisRequest:
  source_id, dataset_schema, row_grain, currency, timezone, requested_period

DiagnosticFinding:
  finding_id, detector_version, observed_metric, time_range, scope,
  confidence_evidence, severity_business, financial_impact,
  exact_calculation, evidence_refs, hypotheses, limitations, epistemic_state

DecisionScenario:
  decision_id, candidate_action, assumptions, scenario_range,
  forecast_type, comparison_baseline, confidence_limitations

OutcomeRecord:
  decision_id, action_date, target_metric, observed_period,
  observed_result, confounders, evaluation_notes
```

The AI provider is **not allowed** to mutate deterministic facts, rewrite input data, fabricate causal certainty, execute a business decision or submit payments. Human approval and verifiable evidence remain authoritative.

## 8. Dedicated payments path: not a prerequisite for grants

- Direct ETH/USDC grants and onchain donations need program permission, a wallet and compliance, **not card acceptance**.
- Customer subscriptions/cards require a separately licensed and eligible merchant processor or authorized Merchant of Record; currently **no provider is confirmed** for an individual Sudan resident without company registration receiving USDC/Base proceeds.
- Keep any checkout integration disabled until seller-country, KYC, chargeback, treasury, payout asset/network and fees are verified.
- Never route payments through an unapproved third party account, use fabricated residency, or claim approved support from a homepage only.

## 9. Definition of 'funding ready'

A grant page or deck should link to:
1. Public MIT repository with stable release and tests.
2. Public usable demo and a 60–120-second concise walkthrough.
3. Specific evidence trace including a case where the system refuses to overclaim.
4. Base/USDC open component **only when implemented**, with reproducible fixtures.
5. Honest adoption data, community activity, maintenance cadence.
6. Clear grant request by milestone, expense categories, wallet compliance, and risks.
7. Realistic continued sustainability via Community + optional managed Cloud.

## Immediate next engineering step

Using the **existing ten-agent OpenCode team**, first verify active local workspace/branch/remotes and current green CI, then create regression tests for numeric coercion/quality, row grain, period comparison, confidence–severity decoupling and causality claims. Protect existing Morph integration and avoid additional AI subscriptions. Make small reviewable PRs with measurable acceptance results. The draft planning PR is documentation only, not proof code was implemented.
