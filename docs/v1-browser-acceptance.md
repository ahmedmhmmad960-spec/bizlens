# BizLens V1 — Manual browser and accessibility acceptance checklist

**Status: NOT YET EXECUTED.** This is a test plan, **not** evidence of browser
compatibility, accessibility conformance, or a release sign-off.

The existing GitHub CI exercises Python, Next.js lint/build, and real HTTP
requests through the running Next.js ↔ FastAPI apps. It does **not** run a
graphical browser or test React event timing, mobile layout or assistive
technologies. Keep PR #24 in draft until the owner/reviewer signs this off.

## Test environment boundaries

- Test only the isolated PR build on a private local/preview environment.
  Never publish a private Codespaces port or expose an operator access key.
- `BIZLENS_BASE_RPC_ENABLED` remains unset for default public-facing V1.
  Use a private throwaway operator token only for separately authorized
  inspection; never screenshot or commit the token, or use a wallet key.
- Use the synthetic `store.csv` demo as commerce data. Do not enter actual
  merchant/customer secrets or confuse Base evidence with commerce KPIs.
- Since Codespaces previews may be blocked by authentication/forwarding,
  a screenshot of a 404 or refused connection is **not** a passing GUI test.

## Functional acceptance — required manual observations

- [ ] Load the landing screen in Chrome; use **Try Interactive Demo** and
      verify a valid diagnosis. Navigate to **Base / USDC** in Workspace.
- [ ] Click **Run offline sample**. Verify statuses:
      `candidate_match`, `partial`, `missing`. Confirm the page labels
      all records **synthetic** and not on-chain verified.
- [ ] Inspect the independent business report before/after entering the Base
      panel. Revenue, gross margin and diagnoses must not change.
- [ ] In the default environment, try a syntactically valid Base Sepolia
      reference. Confirm the server reports **RPC disabled**; no wallet or
      payment prompt appears.
- [ ] Enter an invalid address, amount, log index or tx hash. Verify clear
      input/error states and no positive payment claims.
- [ ] With explicit *private* operator authorization and a **mocked or local
      reviewed RPC** only, confirm unconfirmed/error statuses do not look
      like settled payments. Do **not** use live funds.
- [ ] After a result appears, edit **each** input field (recipient, tx,
      amount, network, invoice ID, index and operator key). The old result
      must disappear immediately.
- [ ] Trigger a deliberately delayed inspection response in a controlled
      local environment, then edit an input before it arrives. The late
      response must **not** display as evidence for the new input.
- [ ] Validate keyboard-only navigation (tab order, visible focus, form
      labels, error announcements, mobile menu open/close).
- [ ] At viewport widths 320, 390, 768 and 1440 px, verify no clipped
      labels, unscrollable fields, masked key disclosure or overflow.
- [ ] Inspect DevTools Network with a throwaway operator token and verify
      no token is included in the response body or persisted storage.
      Remember: an operator key still transits browser → Next → FastAPI;
      this remains **private demo authentication, not public IAM**.
- [ ] Recheck Chrome, Firefox and Safari (or note unavailable platform),
      accessible zoom (200%) and reduced-motion usability.
- [ ] Capture reviewer initials, browser versions, environment, time,
      screenshots with secrets redacted, issues and final explicit approval.

## Automated boundary checks already enforced

- An unverified or inaccessible RPC returns `evidence_status=unconfirmed`,
  `invoice_paid=false`, `settlement_finality_established=false`. Successful
  HTTP transport does not imply payment settlement.
- Next.js inspection proxy rejects non-JSON requests (HTTP 415) and requests
  exceeding **2 KiB** (HTTP 413) before contacting FastAPI. This limit
  is **at the Next proxy**; a public deployment needs a shared gateway/body
  limit at every ingress, not just the web application.
- The React Base inspector clears old result/error state after any form
  edit and refuses to display an earlier in-flight response following edits.
  This implementation must still pass the **manual race test** above.
- The default HTTP smoke confirms Base RPC remains disabled, sample evidence
  is synthetic and oversized/wrong-content-type requests are rejected.

## Open risks / no-release notes

- The server does **not** persist transaction-claim ownership. Duplicate
  use of a transfer is detected within a supplied batch, but two separate
  API calls are **not** an anti-double-payment ledger. Never present the
  evidence screen as a merchant payment reconciliation system.
- Rate limits are per-process and operator token access is for a private
  demo only, not public traffic or multi-tenant deployment.
- A six-L2-block confirmation threshold is an illustrative confidence
  policy, not Ethereum L1 finality or a settlement guarantee.
- Real third-party Base Sepolia explorer fields were found, but the first
  independent public RPC attempt returned `rpc_unavailable`. Do not claim
  successful chain verification without new attributable evidence.

**Release gate: FAIL/OPEN until manual browser evidence, independent security
review and explicit owner merge/release approval are recorded.**
