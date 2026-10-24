# Base/USDC Starter — read-only evidence contract (V1)

**Status: draft feature branch, not a shipped payment/reconciliation product.**

This slice offers dependency-free deterministic matching of invoices to
**caller-supplied ERC-20 Transfer records** and an **optional read-only RPC
receipt check** on Base. The offline mode does not access the network; the
optional RPC mode is explicitly requested and **never verifies final settlement**.
Even `candidate_match` must never be shown as "paid" or "on-chain verified".
No wallets, private keys, signing, funds, custodial flows or external API costs.

## Provenance and supported assets

- Base Mainnet chain ID **8453**; Circle-issued native USDC address
  `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
- Base Sepolia chain ID **84532**; Circle-issued test USDC address
  `0x036CbD53842c5426634e7929541eC2318f3dCF7e`.
- The two chains are never interchangeable. Circle's **USDbC** bridged token
  is not Circle-issued native USDC.
- USDC uses **six** decimal places. Invoice inputs are decimal *strings*;
  supplied transfer event amounts are **integer base units**, never floats.
- Base Sepolia USDC is a test token without real-world monetary value.

Official references:
- https://docs.base.org/base-chain/api-reference/ethereum-json-rpc-api/eth_chainId
- https://developers.circle.com/stablecoins/usdc-contract-addresses

## Data boundary

`Invoice(invoice_id, chain_id, recipient, amount_usdc, tx_hash, log_index)`
specifies the expected invoice amount and explicit transaction/log reference.

`TransferRecord(tx_hash, log_index, chain_id, token_contract, recipient,
amount_raw)` holds unverified externally supplied event fields.

The matcher compares transaction hash, optional log index, chain, native-USDC
token contract, recipient and exact integer amount. **It never guesses**
which transfer belongs to an invoice merely from an equal amount.

Results:
- `candidate_match`: supplied fields align, **not a verification of a payment**.
- `missing`: no reference or referenced record **in supplied data**; this is
  not proof that a payment is missing on-chain.
- `duplicate`: ambiguous or repeated referenced logs, or the same log is
  claimed by multiple invoices.
- `wrong_chain`, `wrong_token`, `wrong_address`: specific evidence mismatch.
- `partial`: supplied amount lower than invoice.
- `amount_mismatch`: supplied amount higher than invoice.

All `MatchResult` objects carry `onchain_verified=False`. The module will
not silently mark invoices settled, credit a ledger or modify business
financial KPIs. There are no user-provided RPC endpoints or untrusted
screenshots treated as proof.

## Independent reproduction: developer-first

The offline mode has no credentials, wallet, RPC calls or network dependency:

```bash
python -m integrations.base_usdc --demo
python -m pytest tests/integrations/ -q
```

The CLI prints three **synthetic** cases (candidate match, partial, missing)
with `onchain_verified: false` and `real_transaction: false`. It is safe to
use as an illustration, **not** an example of a real onchain payment.

### Optional real receipt inspection

Read-only mode is **opt-in** and sends an explicit tx hash to the appropriate
Base public RPC. Example, replacing each placeholder with your *own*
public testnet transaction evidence:

```bash
python -m integrations.base_usdc --verify --chain 84532 \
  --invoice-id "EXAMPLE-001" \
  --recipient "0xYOUR_40_HEX_CHARACTER_RECIPIENT" \
  --amount-usdc "12.345678" \
  --tx-hash "0xYOUR_64_HEX_CHARACTER_TRANSACTION_HASH" \
  --log-index 0
```

`--chain 8453` selects Base Mainnet explicitly. The program uses **only**
`https://mainnet.base.org` / `https://sepolia.base.org` and permits only
`eth_chainId`, `eth_getTransactionReceipt`, `eth_getBlockByNumber`, and
`eth_blockNumber`. It has bounded response size and timeout, uses no
API keys, and NEVER calls a transaction-sending method.

The new `inspect_invoice` function checks:

1. RPC network ID and transaction hash equal the invoice reference.
2. Receipt execution status is successful, not pending or reverted.
3. Receipt block matches the currently canonical L2 block hash reported
   by the same RPC source.
4. A documented **six L2-block observation policy** by default. This is
   a *demo confidence threshold*, **not Base or Ethereum finality**.
5. Exact ERC-20 `Transfer(address,address,uint256)` event signature and
   indexed recipient, native Circle USDC contract, log index, and integer
   6-decimal amount. Multiple events without an index are ambiguous.
6. Contradictory or invalid evidence fails closed: no positive match.

Only `rpc_observed_match` sets `rpc_observed: true`. The result means that
a read-only Base RPC node reported a successful matching event in a currently
canonical L2 block with the requested number of confirmations. **It is not
a cryptographic light-client proof, L1-finalized settlement, or authority
to mark an invoice paid.** The RPC provider remains a trust dependency.
A partial, duplicate, stale, wrong-address, fake-token, missing or failed
receipt must not be shown as an accepted payment.

Public Base RPCs are **rate limited and unsuitable for production traffic**.
This adapter is for a small reproducible, noncommercial V1 demo and engineer
evaluation. Network failures return an unverified state, never fabricated
success.

Official references:
- https://docs.base.org/get-started/connect-to-base
- https://docs.base.org/specifications/node-operators/run-a-node
- https://ethereum.org/developers/docs/apis/json-rpc/
- https://developers.circle.com/stablecoins/usdc-contract-addresses

## BizLens workspace and HTTP integration (draft PR)

The main BizLens workspace now includes a **Base / USDC** evidence tab after
starting an analysis. It does not change the deterministic Commerce metrics.

- `GET /base-usdc/demo` returns the same explicitly synthetic
  offline matching results as the developer CLI.
- `POST /base-usdc/inspect` accepts strict invoice fields and never exposes a
  wallet-signing or transaction-sending function. The server returns HTTP 503
  and `mode=disabled` unless an operator explicitly sets both
  `BIZLENS_BASE_RPC_ENABLED=1` and a fresh 64-character lowercase hex
  `BIZLENS_BASE_RPC_TOKEN`. Authorized requests must include the
  `X-BizLens-Rpc-Key` header; absent/wrong keys receive HTTP 403.
  A per-process demo guard allows at most 10 authenticated attempts per
  minute and 2 simultaneous inspections, then HTTP 429. **These limits
  do not replace a shared production gateway limiter or user management.**
- Next.js forwards the two endpoints through
  `/api/base-usdc/demo` and `/api/base-usdc/inspect` using the same
  private FastAPI origin as the existing analysis API. Responses use
  `Cache-Control: no-store` where relevant.
- A live inspection result is labeled as **RPC-observed evidence**; it is not
  a 'paid' decision, an L1 finality proof or an update to the sales report.
- The sample tab uses synthetic addresses/transactions; it must never link
  those placeholders to a real explorer or misrepresent them as chain data.

The smoke test `scripts/demo_http_smoke.py` now verifies both the offline
sample through the real web proxy and the explicit default RPC-disable path.
CI clears the enable flag and makes **zero live chain calls**.

## Safe private operator configuration (no paid services)

Generate a *new* key locally without committing, printing in public logs, or
posting it to any issue:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Store it privately as `BIZLENS_BASE_RPC_TOKEN`; set
`BIZLENS_BASE_RPC_ENABLED=1` only in an isolated local/authorized
environment. Pass the key in the web inspector password field or the
`X-BizLens-Rpc-Key` API request header, **never a wallet private key**.
The browser holds it only in active component memory, not persistent storage.
Default CI and public V1 demo remain disabled. No keys are bundled.

For this draft: the operator key is an access gate, **not enterprise IAM**;
the per-process limiter is reset by restarts and is not shared across
replicas. Production access needs per-user authentication, a reverse-proxy
limit, deployment controls and independent security review. Public RPC
redirects are refused. Monetary input must use plain decimal notation,
at most 18 whole digits and six fractional digits, with no exponents,
overflow or implicit rounding.

## Open scope and next quality gates

This draft PR supplies the standalone offline matcher, a bounded optional
RPC observation adapter, CLI examples and synthetic negative-case tests.
**No production UI, report wiring, live Mainnet payment or verified real
transaction has yet been demonstrated.** Before Demo V1 release:

- Integrate a separately labeled *evidence-only* Base section in BizLens;
  do not alter commerce KPIs or claim it is a complete payments system.
- Check any intended real Base Sepolia fixture against an independently
  inspected public receipt; include the actual tx/explorer citation.
- Validate chain replay resistance, duplicate invoice claims, RPC outages,
  noncanonical receipts, wrong contract, partial amount, and frontend error
  presentation across the complete API/UI flow.
- Deliver Developer Toolkit docs and stable typed public interfaces, then
  perform independent reproducibility review, accessibility checks and CI.
- Require human code review and final approval before merge or demo release.

