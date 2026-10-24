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
2. **P0 — Receipt provenance.** No independently reproduced real publicly
   referenced Base Sepolia native-USDC transaction plus exact block/log has
   been attached. Synthetic tests validate code paths, not a chain claim.
   Cite actual public transaction source and review the expected recipient
   and amount before making any external claim.
3. **P0 — Proof terminology.** `rpc_observed_match` is an observation from
   one RPC provider under a policy of six L2 blocks by default. It is not a
   cryptographic proof, Ethereum L1 finality, invoice paid or funds available.
   `candidate_match` is still weaker: just matching supplied fields.
4. **P1 — GUI acceptance.** CI exercises Next.js HTTP, not a graphical
   browser. Test responsive view, operator-key handling, field errors,
   accessible status announcements, report isolation, printing and keyboard
   navigation. Codespace preview/auth issue is tracked separately.
5. **P1 — Independent review.** Separate reviewer must inspect matching
   contract, URI/authorization boundaries, tests, package interface and
   negative cases before owner approves merge; internal review is not enough.
6. **P1 — Local vs release install.** Verify clean editable installation and
   an isolated wheel; third-party reuse needs documented stable API,
   versioning, licensing and migration expectations.

## Evidence acceptance checklist (maintain separate from claims)

- [x] Fully offline synthetic USDC path and financial golden fixtures.
- [x] Defensive test suite for malformed receipt, wrong chain/token/recipient,
      missing/failed tx, partial amount, duplicate claims, RPC unavailability.
- [x] CI includes standalone wheel smoke, Developer Toolkit and HTTP journey.
- [ ] Real **public**, independently cited Base Sepolia USDC receipt/transfer.
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
