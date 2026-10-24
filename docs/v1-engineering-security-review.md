# BizLens V1 — Preliminary engineering/security review (not an independent audit)

**Review status:** PR #24 draft. Reviewed source-level contracts on 2026-10-24.
This is an internal preliminary review, **not** an independent security audit,
pentest, chain verification, production authorization, or a Base endorsement.

## What this review actually inspected

- `apps/api/app/base_usdc_routes.py`: operator token gate, explicit RPC
  enable flag, strict request validation, in-process 10/min rate and
  2-concurrent limits, masked error responses.
- `apps/web/app/api/base-usdc/inspect/route.ts`: Next.js gateway forwards
  the operator's header to FastAPI. It does not mint/own authorization.
- `integrations/base_usdc/rpc_evidence.py`: allowlisted read-only Base RPC
  endpoints/methods; bounded response and timeout, redirect refusal,
  receipt status, canonical L2 block, confirmations, ERC-20 event details.
- `integrations/base_usdc/matcher.py`: no amount-only guessing, native
  Circle USDC contract IDs, fixed-point amounts, duplicate claiming.
- `bizlens_toolkit/`: offline rule-based provider, deterministic output,
  separate hand-audited expected JSON, no random analysis ID.
- Existing negative tests and GitHub CI checks (link exact run in PR).

## High-value controls already implemented

| Risk | Current mechanism | Scope boundary |
| --- | --- | --- |
| Unintended paid/network requests | Demo offline; RPC requires explicit opt-in | No public production promise |
| Unauthorized RPC abuse | Disabled by default, 64-lowercase-hex operator token, 403 on mismatch | Shared auth/gateway still needed |
| RPC flood | 10 authenticated attempts/min and 2 concurrent **per process** | No distributed quota |
| RPC redirects / arbitrary destinations | Hard-coded HTTPS URLs, redirect denial, fixed RPC read methods | Still trusts a public RPC provider |
| Forged/contradictory log | Receipt success/hash, canonical block hash, token, event topics, recipient, amount | Not cryptographic L1 finality |
| Duplicate payments | Cross-invoice duplicate log claim detection in batch matching | No persistent ledger/claim store |
| Misleading business facts | Golden CSV/JSON independently audited; deterministic monetary validation | Not accounting certification |
| Leak of customer records | Local Toolkit accepts local CSV; analysis ID omitted from stable export | End users must protect local inputs |

## Release blockers (must not be represented as complete)

1. **P0 — Trust and deployment.** Browser-supplied operator keys are for
   private development only. They must never be bundled into frontend code,
   included in demo screenshots, committed or treated as end-user login.
   Public deployment must add proper user authentication, gateway/global
   rate limits, privacy/security headers, logging redaction and threat-model
   review. Keep real inspection disabled publicly until then.
2. **P0 — Independent receipt reproduction.** A real third-party native
   USDC transfer, recipient, amount and block are now referenced from the
   [Base Sepolia public explorer case](base-sepolia-public-reference.md).
   The maintainers **have not yet successfully re-read its receipt via
   independent RPC or confirmed the exact onchain log index**. The pinned
   attribution is not a proof, and no real business invoice is implied.
   Before any stronger claim, obtain a successful opt-in RPC observation
   and record its provenance and date; review via an independent source.
3. **P0 — Proof terminology.** `rpc_observed_match` is an observation from
   one RPC provider under a policy of six L2 blocks by default. It is not a
   cryptographic proof, Ethereum L1 finality, invoice paid or funds available.
   `candidate_match` is still weaker: just matching supplied fields.
4. **P1 — GUI acceptance.** GitHub CI now executes actual headless Chrome
   clicks and synthetic delayed-response/390px-mobile checks in addition
   to Next.js HTTP. The [browser acceptance plan](v1-browser-acceptance.md)
   distinguishes these automated checks from **uncompleted manual
   keyboard/screen-reader/cross-browser/visual review**. Codespace
   preview/auth remains separate.
5. **P1 — Independent review.** A separate reviewer must follow the
   [threat-model handoff](v1-independent-security-review-handoff.md),
   independently reproduce the matching/security tests and record
   findings on the exact PR SHA. Maintainer tests and source review
   are **not** an independent audit or approval.
6. **P1 — Local vs release install.** Verify clean editable installation and
   an isolated wheel; third-party reuse needs documented stable API,
   versioning, licensing and migration expectations.

## Current hardening delta (2026-10-24, PR #24)

- UI clears prior observations if any invoice, network, tokenless RPC
  reference or operator-key input changes; late asynchronous responses are
  ignored when input state changed. **Manual race validation remains open.**
- API success means a request was processed, NOT a paid invoice. Responses
  now explicitly include `evidence_status` (`rpc_observed` or `unconfirmed`),
  `invoice_paid=false`, and `settlement_finality_established=false`.
- The Next.js inspection proxy now rejects non-JSON and requests over
  2 KiB before proxying to FastAPI. Its HTTP smoke checks both rejection
  states and ensures public RPC remains disabled.
- **Residual high-risk limitation:** a transfer event reused in separate
  API calls has no persisted claim lock/ledger. Batch duplicate detection
  must never be presented as durable anti-double-payment enforcement.
  Production reconciliation requires an independently reviewed persistent
  claim store and replay policy; this is outside the approved V1 scope.
- Public RPC transport is now schema-constrained to its four inspection
  methods and their exact parameter shapes; response JSON rejects duplicate
  keys at every depth, nonstandard nonfinite constants, and boolean/float
  IDs masquerading as numeric ID 1. Invalid timeouts also fail before
  network access. Synthetic negative tests cover these boundaries.
- Automated headless Chrome now proves click-through, synthetic Base outcome
  labels, 390px viewport and stale/late response behavior. Manual
  accessibility, cross-browser and visual acceptance remain unsigned.
- This review is **maintainer source review only**; no independent human
  audit or verified live chain proof has been performed.

## Evidence acceptance checklist (maintain separate from claims)

- [x] Fully offline synthetic USDC path and financial golden fixtures.
- [x] Defensive test suite for malformed receipt, wrong chain/token/recipient,
      missing/failed tx, partial amount, duplicate claims, RPC unavailability.
- [x] CI includes standalone wheel smoke, Developer Toolkit and HTTP journey.
- [x] Real **public** Base Sepolia native-USDC transfer attributed to a
      third-party explorer, with pinned public fields and source link.
- [ ] Independently reproduced live RPC receipt/log evidence (not only
      explorer text and mocked tests); capture source/date of verification.
- [ ] Independent engineering/security review and fix all blocking findings.
- [ ] Authenticated operator-only manual interaction tested in real browser.
- [ ] Desktop/mobile/keyboard QA and final visual comparison.
- [ ] Product owner explicitly approves final merge/release.

## Decision

**CONTINUE AS DRAFT. DO NOT MERGE OR CLAIM BASE PRODUCTION READINESS.**
The code demonstrates concrete reusable capabilities. A successful CI run
supports reproducibility, not independent security assessment or public
network attestation. Keep the approved two-feature V1 scope and zero-spend
policy. Final visual polish is scheduled after functionality/safety gates.
