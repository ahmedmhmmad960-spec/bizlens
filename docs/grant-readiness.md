# BizLens Grant & Public-Goods Readiness Plan

> Status: implementation plan, not an eligibility approval or funding claim.  
> Updated: 2026-10-13  
> Scope: grant-ready BizLens Community, Base/Ethereum public-good module, evidence package, and ethical fundraising.  
> Rule: preserve the existing deterministic metrics/diagnosis/evidence/AI boundary and all current product features.

## Current verified repository baseline

The existing repository already documents FastAPI + Next.js, CSV ingestion, deterministic business metrics, diagnoses, evidence, confidence, ranking, diagnosis chains, period comparisons, analysis replay, explainable AI, tests and CI. The code is MIT-licensed.

**Do not replace this foundation, fork six product variants, or present planned features as shipped.**

## Shared implementation track (one product, six funding channels)

### Stage 0 — Verify baseline and create truth inventory

- [ ] Record branch/commit, working tree and active CI status before changes.
- [ ] Run existing Python tests and frontend build; fix regressions without changing business logic.
- [ ] Publish an evidence-based feature inventory: live, partial, planned.
- [ ] Document data handling, limitations, security boundaries and reproducible demo steps.
- [ ] Preserve existing OpenCode agent/Morph setup and use zero additional paid model subscriptions.

**Exit:** reproducible clean build, test output and honest feature status.

### Stage 1 — Outstanding Community experience

- [ ] Public runnable demo with **clearly labeled synthetic** datasets and replayable outputs.
- [ ] Show Me Why / Evidence Trace for every material diagnosis: source row, rule, calculation, confidence and caveats.
- [ ] Diagnosis Chains and evidence-grounded Ask BizLens (no unsupported causality).
- [ ] Reproducible test fixtures for negative/edge cases and stable CI.
- [ ] Document an open Community version that remains genuinely useful without subscription, including evidence/explanations.

**Exit:** a new user can reproduce findings and inspect how the conclusions were reached.

### Stage 2 — Reusable Base / Ethereum public-good component

- [ ] Implement an **optional** USDC-on-Base transaction reconciliation module; do not embed crypto assumptions into core business calculations.
- [ ] Inputs: exported onchain transaction data and **synthetic** invoices/orders. RPC/indexer integration is optional and must respect free-tier and privacy constraints.
- [ ] Match deterministic transaction evidence using chain ID, transaction hash, log index, token contract, amount, timestamp, receiver and invoice reference when provided.
- [ ] Validate native USDC address and chain ID from *current official sources*, and protect against testnet/mainnet confusion. Never hard-code guessed contract addresses.
- [ ] Detect duplicate transfers, partial payments, missing/unmatched payments and timing mismatches; track unmatched cases without invented explanations.
- [ ] Provide provenance links or verifiable transaction references, reconciliation reports and repeatable tests for known edge cases.
- [ ] Keep this module MIT-licensed and useful independently of the hosted product.

**Exit:** external Ethereum/Base builders can use the open module and verify its claims.

### Stage 3 — Evidence of real adoption and project operations

- [ ] Demo URL, short factual walkthrough, screenshots/video, open-source README and contributor onboarding.
- [ ] Changelog, CI status, release tags, issue tracker and security disclosure policy.
- [ ] Publish **verified** usage evidence: testers, feedback, public contributions and reproducible before/after results. Never invent users, transactions or traction.
- [ ] Project-owned web/social identity and updates; no misleading claims or artificial donations.
- [ ] Clear funding goals, expense breakdown, milestones, reporting cadence, refund/risk statement where appropriate.
- [ ] Separate public-good grant budget from commercial hosted service revenue.

**Exit:** public proof package supports each funding application.

## Grant-specific evidence matrix

| Program | What reviewers or donors need to see | Submission/effect |
|---|---|---|
| **Base Builder Grants** | Unique contribution, a *live* Base-relevant feature, onchain/user impact, tested demo | May be discovered or nominated. Grant tax/KYC paperwork including W8/W9 can apply; geography remains eligibility-dependent. |
| **Gitcoin Grants** | Public MIT code, repository history, Ethereum ecosystem impact, eligible round-specific criteria, legitimate community | Matching depends on genuine independent donors, not manufactured Sybil donations; one application does not secure matching. |
| **Giveth (core)** | Real public benefit, evidence of action, legitimate project ownership, updates, transparent wallet/use of funds | A donation page may be initially unlisted; Verified and GIVbacks Eligible statuses require separate checks. **Never promise donor goods or services in exchange for GIVbacks-linked donations.** |
| **Ethereum Foundation ESP** | Non-commercial, free/open-source Ethereum builder infrastructure with credible approach, milestones and budget | Apply to an active Wishlist/RFP/open round if aligned; successful grants commonly pay onchain in ETH, after identity verification. |
| **Octant Atlas** | Invitation, owner wallet, verification, project pitch, past outputs and concrete funding plan | Invitation and verification required before publication; participation is not automatic. |
| **Drips** | Public GitHub repository, maintained dependencies, claimed project wallet, transparent maintainer splits | Claim uses default-branch `FUNDING.json`; do not commit wallet-control data before owner verifies it. Distinguish direct support from Wave awards. |

### Official program references

- Base: https://paragraph.com/@grants.base.eth/calling-based-builders
- Gitcoin: https://gitcoin.co/program
- Giveth: https://docs.giveth.io/projectverification
- Ethereum Foundation ESP: https://esp.ethereum.foundation/applicants
- Octant: https://docs.octant.app/docs/projects/apply-for-funding/
- Drips: https://docs.drips.network/get-support/claim-your-repository/

## Payments: separate *funding donations/grants* from *customer checkout*

1. **Grants and onchain donations**: receive the awarded token directly at a project wallet when explicitly allowed by the program. Check jurisdiction/KYC/AML and legal/tax requirements independently. Card checkout providers are **not** a prerequisite for receiving grants.
2. **SaaS revenue from international cards**: evaluate a licensed Merchant of Record (MoR) or processor that explicitly supports the real merchant's country of residence, individual registration, card processing and actual **crypto payouts**. Check exact payout token/network, limits, disputes, reserves, fees and contractual roles.
3. **Card-funded crypto purchase** (onramp) is **not equivalent** to a merchant acquiring product. Do not assume users can pay SaaS invoices by making a personal crypto purchase through an unrelated onramp.
4. Never bypass geographic restrictions, represent someone else's company as owner, rent unapproved merchant accounts, or accept customer money before payout eligibility is established.
5. Keep payment integration behind an interface so the Community app runs with payments **disabled** until an approved provider is selected.

### Candidate evaluation checklist

- [ ] Published company/legal identity and evidence of regulated/acquiring relationships
- [ ] Seller/merchant residency and **individual** eligibility confirmed for target country
- [ ] Customer card acceptance for software and recurring SaaS billing
- [ ] Contract explicitly permits processing sales **for BizLens**
- [ ] Provider-controlled chargeback, refunds, reserves and subscription cancellation
- [ ] Onchain merchant payout (exact asset, network, timing and fees) confirmed
- [ ] Sandbox + signed webhooks / reconciliation API
- [ ] Transparent pricing, dispute path, security and account-closure procedures

**Important:** No card→USDC provider is marked approved or integrated by this document.

## Suggested implementation order and acceptance gates

1. Stabilize and demonstrate existing BizLens Community without altering the deterministic core.
2. Deliver the optional open-source Base reconciliation adapter with verifiable synthetic fixtures.
3. Publish docs/demo and measure truthful adoption/utility; prepare evidence, budget and milestones.
4. Publish eligible project listings and apply to actual open rounds. No automatic grant claims.
5. Evaluate compliant MoR/card providers separately, with payment integration off until geographic and withdrawal eligibility are verified.

## Verification before claiming readiness

- All existing unit/integration tests green and CI reproducible.
- Base reconciliation tests cover chain mismatch, duplicates, decimals, reorg/event provenance assumptions, unmatched entries and wrong-wallet cases.
- No transaction or grant data is fabricated; demo is labeled synthetic.
- All public-good features remain accessible in Community.
- No stored API keys, private wallet keys or customer data in repo.
- Technical/legal funding criteria verified against each **current round**, not a generic platform website.

This plan is a collaboration document: it does not prove the project is ready for grants, and it does not replace the relevant program's current eligibility rules.
