# BizLens Base/USDC Starter V1 — threat model and review gate

**Status:** internal static engineering review of draft PR #24; **not** an
independent penetration test, external audit, or certification. This report
records current mitigations and unresolved conditions honestly.

## Assets, trust boundaries and intentionally absent powers

The adapter compares **invoice claims** against (a) caller-supplied
synthetic/offline Transfer records and (b) optional read-only observations of
Base RPC receipts. Caller-supplied records are **not trust anchors**.

- The application cannot send a transaction, sign with a wallet, access a
  private key, operate a merchant ledger, or mark an invoice paid.
- Commerce metrics and Base evidence are separate; Base results must never
  silently alter revenue or profit.
- The configured public Base RPC node is a third-party **data source**,
  not a cryptographic verifier or guarantee of Ethereum L1 finality.
- Synthetic fixtures are identified as synthetic in API, CLI and UI.
- Only Base Mainnet (8453) and Base Sepolia (84532) native Circle-issued
  USDC are supported. Do not treat USDbC or another chain as equivalent.

## Threats, mitigations, and proof obligations

| Threat | Implemented mitigation | Evidence / limitation |
|---|---|---|
| Arbitrary RPC target / SSRF | Fixed HTTPS Base RPC origins, no user-specified URL, approved read-only JSON-RPC methods, **no redirects** | Offline tests for method and redirect rejection; HTTPS RPC provider remains trusted |
| Publicly farmed RPC reads | Disabled by default; requires explicit opt-in plus separately generated 32-byte operator key in a private header; constant-time comparison | Per-process max 10 calls/60s and 2 concurrent; no shared gateway or user-level auth yet |
| Input-driven resource exhaustion | Strict request length/type validation, bounded full decimal grammar (18 whole, 6 fractional digits), raw amount cap, timeout and 1 MB RPC response cap | Does not replace reverse-proxy body size and connection limits |
| False matching due to wrong chain/token | Compare `eth_chainId`, fixed native USDC contract, ERC-20 Transfer topics, recipient and exact integer amount | Mock-only negative paths |
| Fabricated successful payment | Successful receipt status, transaction hash, canonical L2 block match, observed block confirmations and transfer log consistency | Single RPC observation is **not** independent cryptographic proof or L1 finality |
| Event replay across invoices | Reject duplicate `(chain, tx_hash, log_index)` claims within one batch | **No durable/global invoice registry**; cannot guarantee global replay prevention |
| Invalid, pending, reverted or partial transfer | Explicit states, no successful claim, no automatic settlement updates | User should not interpret `rpc_observed_match` as "paid" |
| Leaking access credentials | Operator key is never hard-coded, output, sent as URL parameter, saved in browser storage or shown in response; secret stays server-side and in the active form memory | Secure deployment, HTTPS, proxy logging, key rotation and storage remain operator responsibilities |
| Compromised packages / deployment | Python wheel smoke and CI tests; no extra paid services | No independently audited dependency provenance or production hardening claim |

## Current reviewer findings

1. **Closed in draft**: scientific-notation / extreme-decimal inputs formerly
   reached a Decimal calculation; now rejected before conversion.
2. **Closed in draft**: `BIZLENS_BASE_RPC_ENABLED=1` previously allowed an
   anonymous endpoint; now additionally requires a strict random 64-character
   lowercase hex operator token and correct request header, plus an
   in-process concurrency/rate guard.
3. **Closed in draft**: default urllib redirect behavior formerly could
   follow a redirect away from allowlisted Base endpoints; redirects are
   explicitly refused.
4. **Not closed / release blocker**: public production service needs gateway
   or shared limiter, user-level access control, request body limits,
   trustworthy secret storage, key rotation, TLS and operational review.
5. **Not closed / release blocker**: no independently inspected, cited **real
   Base Sepolia USDC** receipt has been accepted as a golden example.
6. **Not closed / release blocker**: manual real-browser desktop/mobile,
   keyboard and failure-state QA; HTTP CI is not visual acceptance.

## Operator-only local validation

Generate a new random 32-byte token for an **isolated private** environment:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Store it privately in `BIZLENS_BASE_RPC_TOKEN`, and enable
`BIZLENS_BASE_RPC_ENABLED=1` only when local inspection is expressly
desired. Use `X-BizLens-Rpc-Key` as a header (or the operator key field in
the UI). Do not paste this token in public chat, issues or command logs.
Never confuse this token with a wallet seed phrase or private key.

Production mode is **not approved** by this document. Without both
settings, the HTTP inspector must answer HTTP 503 and perform no RPC call.
Wrong/missing keys return 403. Rate-limited calls return 429.

## Independent acceptance still required

Run all CI checks, review security of exact release diff, inspect an actual
public Sepolia receipt via read-only evidence with independently verifiable
chain/explorer provenance, test noncanonical/partial/wrong-token cases,
verify no changes to Commerce results and manually test the graphical
workflow. Do not merge or announce general availability without explicit
owner approval. This document is a checklist, not a claim of external audit.

References: [Base evidence contract](base-usdc-starter-contract.md),
[Developer Toolkit](developer-toolkit.md),
[OWASP API4:2023](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/),
[OWASP REST API security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html).
