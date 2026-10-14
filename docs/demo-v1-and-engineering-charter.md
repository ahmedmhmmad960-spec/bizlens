# BizLens — Approved Demo V1 & Engineering Excellence Charter

**Approval date:** 2026-10-14  
**Status:** Product owner approved strategy and explicit engineering ambition. This document is a binding target for planning and review, **not** proof that any feature has already shipped.
**Implementation:** No code changes made in adopting this charter. Preserve current OpenCode team, Morph integration and zero-extra-spend constraint.

## Non-negotiable north star — Engineering excellence

> **«هدفنا أن ينبهر كل مهندس ومبرمج ومطور يرى الكود، ويقول: هذا الكود مثير للاهتمام.»**

The owner's explicit standard: **"We want every engineer, programmer, and developer who examines BizLens code to be impressed and say: 'This code is interesting.'"**

This is an **aspiration to earn through engineering quality**, not a claim about other developers' opinions. We do not optimize for clever-looking or needlessly complicated code. We earn that reaction by delivering unusually rigorous, elegant, understandable, dependable software.

### What "impressive" must mean in code review

1. **Mathematical and epistemic correctness:** deterministic financial metrics, defined data grain and periods, no fabricated numbers, confidence separate from business severity, never infer proven causality from co-occurrence.
2. **Clean architecture:** clear boundaries among ingestion, data quality, metrics, diagnostic rules, evidence, AI explanations, reports, and optional Base adapter; small composable interfaces; low coupling.
3. **Transparent evidence:** reproducible metric calculations and sources, versioned inputs, traceable limitations, explicit observed vs inferred vs hypothetical labels.
4. **Excellent tests:** unit/integration/end-to-end tests, property/invariant checks where useful, negative/edge cases, golden fixtures, reproducible CI, no demo-only fake success states.
5. **Type-safe maintainable work:** documented contracts, helpful error handling, readable names, consistent formatting/lint, security/privacy by design, avoid overengineering and unused dependencies.
6. **Open-source developer experience:** fast onboarding, runnable examples, reference docs, contributor guidance, thoughtful APIs, extensible standalone public-good modules.
7. **Polished product UX:** approved Cinematic Minimal Intelligence visual direction (70% earlier funder demo, 30% newer navigation reference), accessibility, meaningful chart interaction and **no more than three primary home-screen charts**.
8. **Independent verification:** engineers and funders can reproduce reported results with public fixtures and inspect the implementation. Never present generated design imagery as shipped code.

### Quality gate for every engineering PR

- State what problem is solved and why the abstraction/approach is appropriate.
- Include evidence-backed tests, especially accounting/data-quality and failure-path cases.
- Keep compatibility with existing flows; preserve Morph and working model integrations.
- Typecheck, lint, test, build and CI must pass before merging; record exceptions honestly.
- Include docs and relevant demo/benchmark cases. Require human review for claims about financial behavior.
- Prefer simple clear code over novel complexity. A feature does not count as done until verifiable.

## Product identity: one BizLens, six funder-specific reasons to support it

One cohesive open-source **Evidence-to-Outcome Decision Intelligence** product across business commerce, digital business, and optional Web3/Base evidence. **No six forked products.**

Funder-specific public-good proofs may reuse the same open diagnostic/evidence engine and optional USDC adapter. Funding proposals describe eligible open-source deliverables; optional future Cloud hosting is **not** the purpose of these grants.

## Approved minimum pre-funding public demo scope

**Launch a real, small, useful BizLens Community release before applying broadly**. It is not just a marketing video or an untestable mockup.

- **Trusted business diagnosis:** user uploads CSV or clearly labeled synthetic fixture; deterministic metrics, strong data quality/error states, ranked diagnoses, honest confidence, period comparison.
- **Evidence:** Show Me Why, exact calculation/source references as supported, explicit limitations/abstention, Ask BizLens grounded in real analysis (free/rule-based fallback), basic replay and printable/exportable report.
- **Premium UI:** approved visual identity and restrained meaningful charts; reliable responsive walkthrough.
- **Base / USDC Starter:** a *read-only, small but real*, open-source module for documented invoice-to-USDC transaction matching on Base with verified transaction evidence and missing/duplicate/mismatch cases; include only after it is built and tested. Label chain/testnet and synthetic invoices clearly. Do not pretend it is a full payments system.
- **Developer Toolkit:** independently runnable documented examples for the diagnosis/evidence core and USDC starter, with tests, install/run instructions, and practical licenses.
- **Public credibility:** GitHub code, reproducible fixtures, passing CI, release notes, transparent limitations and consented feedback from real pilot testers.

**The Base Starter and developer toolkit are additions to the pre-funding V1 goal** over earlier planning drafts; if not verified by release time, label them planned and never pretend they were shipped. Keep scope small enough to finish well.

### Deliberately *not* promised in Demo V1

- Full Advanced Diagnostic Brain / systematic hypotheses engine.
- Full Decision Twin simulations, scenario sensitivity and forecasts.
- Durable Business Memory / Outcome Learning.
- Complete Base/USDC reconciliation product, custodial payments or payments processing.
- Broad third-party SaaS connectors, enterprise/Cloud operations or large user base.

Any navigational teaser for planned modules must say **Planned / Roadmap** and may not mimic a functioning feature.

## Approved fundable milestones after Demo V1

| Fundable public-good work package | Outcomes to publish and verify |
|---|---|
| **Diagnostic Brain 2.0** | typed trustworthy evidence, deeper hypotheses, causal humility, benchmark fixtures, demonstrable correctness gains |
| **Base / USDC Intelligence** | extend read-only starter into reusable robust matching & onchain provenance; independent module + tests + docs |
| **Decision Twin** | reproducible bounded scenario comparisons with labeled assumptions, sensitivity and limitations |
| **Business Memory & Outcome Learning** | decision/action records, actual-vs-expected comparisons, transparent confounders and outcome measurement |
| **Adoption & Ecosystem** | tested APIs, examples/integrations, contributor infrastructure and measurable real community benefit |

Milestones are **work packages, not claims of five guaranteed grants**. Each program has different eligibility and evidence criteria; Base, Gitcoin, Giveth, Ethereum Foundation ESP, Octant and Drips should each receive a tailored explanation of genuine community value from the **same unified product**.

## Funding credibility before funding

A funder should be able to:
1. Try a live demo, understand the diagnosis and open its evidence;
2. Reproduce key calculations and Base tx evidence;
3. Inspect source, CI, tests, docs, releases and limitations;
4. See what has actually shipped versus the future work and objective acceptance criteria;
5. Understand costs, realistic milestones, maintenance plan and public-good beneficiaries.

Never invent adoption, accuracy, donations or grant acceptance. Residency/KYC and Sudan eligibility are independent from technical merit and must be checked for each program.

## Implementation guardrails

- **Do not begin code modifications merely because this charter is approved.** Use the established multi-agent OpenCode engineering workflow and the user's readiness/implementation approvals.
- Preserve actual working code and Morph integration, zero additional model/API spending.
- Prioritize a small trusted release over a bloated showcase.
- Keep product design references in [visual-identity.md](visual-identity.md).
- See [unified-product-demo-roadmap.md](unified-product-demo-roadmap.md) for broader full-product concept; **where it includes Decision Twin/Business Memory in the first demo, this more recent approved V1 charter supersedes it.**
