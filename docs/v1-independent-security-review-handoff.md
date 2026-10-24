# BizLens Demo V1 — Independent security-review handoff

**State: READY FOR REVIEW; NOT INDEPENDENTLY REVIEWED.** 2026-10-24.
Scope is the two authorized Demo V1 additions: Base/USDC Starter and
Developer Toolkit. This file is a handoff specification, not a security
certification. Keep PR #24 as a **draft** until a separate reviewer records
a decision and the owner explicitly approves merging.

## Reviewer setup (zero-cost, no funds or model keys)

Read the **diff** of
[PR #24](https://github.com/ahmedmhmmad960-spec/bizlens/pull/24) against
`main` and the source files listed below. Run in an isolated checkout of
the PR branch, not in the owner's existing Codespace:

```sh
python -m pip install -r requirements.txt
python -m pip install "pytest>=8,<9" "ruff>=0.12,<1"
ruff check .
python -m pytest
python -m bizlens_toolkit verify-golden \
  --csv tests/fixtures/golden/profit_reversal.csv \
  --expected tests/fixtures/golden/profit_reversal.expected.json
python -m examples.developer_toolkit.base_sepolia_reference
```

These commands use only offline test and synthetic blockchain evidence.
**Do not** run `--inspect` against live RPC, spend ETH/USDC, generate wallets,
or connect billing/API keys during ordinary review. Live public RPC is an
optional separate owner-authorized investigation; a passing offline suite
does not prove any real onchain receipt.

CI additionally performs a real Next.js↔FastAPI HTTP journey and automated
Chrome click/race/mobile tests against *synthetic local data*. View the CI
result for the **same PR head SHA**; do not cite a prior green build for a
later untested commit.

## Exact trust boundaries

| Boundary | Files | Reviewer challenge |
| --- | --- | --- |
| CSV into diagnosis | `core/analysis/service.py`, `bizlens_toolkit/diagnosis.py` | Decimal precision, row-grain/IDs, invalid CSV, leaks, determinism |
| Supplied transfer record into offline matcher | `integrations/base_usdc/matcher.py` | Wrong chain/token/address, duplicated log claims, amount decimals |
| Internet JSON-RPC into receipt observation | `integrations/base_usdc/rpc_evidence.py` | Forged receipts, noncanonical blocks, malformed logs, duplicate keys, unusual JSON, redirects, method/parameter allowlists |
| Unauthenticated browser into Next proxy | `apps/web/app/api/base-usdc/inspect/route.ts` | 2 KiB cap, streaming bodies, exact MIME, header forwarding and no payment actions |
| Direct or proxied request into FastAPI | `apps/api/app/base_usdc_ingress.py`, `apps/api/app/main.py` | Independent 2 KiB stream/declared-length cap; forged length, chunked body, 413 before RPC | 
| Private demo operator key into FastAPI | `apps/api/app/base_usdc_routes.py` | Disabled-by-default, auth mismatch, timing-safe comparison, 429/503, cross-worker limits |
| React form into displayed evidence | `apps/web/components/base-usdc-evidence.tsx`, `scripts/browser_cdp_smoke.py` | Stale/misassociated async replies, synthetic labels, missing evidence, private key handling |
| Reusable developer distribution | `bizlens_toolkit/`, `pyproject.toml`, `tests/toolkit/` | Wheel install isolation, public API clarity, no paid provider fallback |

## Attack/abuse scenarios to independently challenge

1. **Fake payment:** A transaction receipt with unrelated USDC token, wrong
   chain, recipient, amount or log; block hash mismatches; failed receipt,
   insufficient L2 confirmations; event reused across two invoice claims.
   No result may mark `invoice_paid=true` or imply Ethereum L1 finality.
2. **RPC manipulation:** Duplicate JSON keys including nested event fields,
   boolean `id=true` masquerading as `id=1`, NaN/Infinity, wrong
   `jsonrpc` version, HTTP redirect, oversized response, 429/403, malicious
   error text, unexpected method arguments. The adapter should fail closed
   with sanitized categories and no secrets.
3. **Unauthorized inspection/denial-of-service:** No operator token, invalid
   token, missing feature opt-in, malformed body, malicious content type,
   large streamed input, concurrent traffic or key brute force. Per-process
   rate limits do **not** replace shared deployment-level controls.
4. **Frontend evidence confusion:** Trigger a positive fake result for
   Invoice A but edit form to Invoice B before resolve; no stale positive
   finding may appear. Current negative results must clearly show
   `unconfirmed`. This is tested in synthetic browser CI only.
5. **Financial reproducibility:** Wrong decimal precision, duplicate order
   line accounting, missing required fields, leading-zero IDs, golden
   expectation changes. Never regenerate goldens from the code being
   checked.
6. **Privacy:** No private data or operator key may be added to logs,
   committed test fixtures, screenshots, GitHub comments or telemetry.

## High-priority unresolved risks (do not silently accept)

- **Production authentication:** Browser-present operator token is for
  private test/demo use only. No end-user IAM, session isolation or public
  secret lifecycle; operator endpoints must remain disabled in public.
- **Durable cross-request double-claims:** Duplicate checking applies to
  batches. No persistent ledger prevents claiming the same transfer in
  separate independent API requests. This is evidence inspection, NOT
  a merchant payment-settlement/reconciliation product.
- **Global rate limiting and ingress:** Next.js and the direct FastAPI
  inspection route now each reject payloads over 2 KiB, including chunked
  bodies at FastAPI, but these application checks do **not** protect all
  ingress paths, other upload endpoints or multi-process deployments.
  Production use still needs shared gateway-level auth, body limits,
  rate controls, logging policy and independent assessment.
- **RPC trust/finality:** One public RPC provider is not independent
  cryptographic chain verification or Ethereum L1 finality.
  Prior live Base Sepolia inspection returned `rpc_unavailable`; no real
  receipt observation may be claimed until independently corroborated.
- **Browser/manual QA:** Automated headless Chrome click-through and
  synthetic delayed-response checks passed on a previous tested head;
  keyboard/screen-reader/Firefox/Safari/mobile human QA is still open.

## Required reviewer output

Record in a dated PR review/comment (not just a checkmark):

- Exact commit SHA reviewed, test command output/CI run, and reviewer identity
  or pseudonym that clearly differs from the author.
- Findings grouped **Critical / High / Medium / Low**, exploit condition,
  affected source location, and reproducible steps **without secrets**.
- Whether any finding blocks a private demo versus a public deployment.
- Whether all **Critical/High** issues are resolved and retested.
- Explicit judgment: `APPROVE FOR PRIVATE DEMO`, `REQUEST CHANGES`, or
  `NOT REVIEWED`; distinguish from full public production security approval.
- Owner's separate manual browser/UX and merge approval remains required.

**No GitHub Actions result, static source inspection by the author,
mocked blockchain response or status page is a substitute for this
independent review.**
