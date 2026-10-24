# Base/USDC Starter — offline matching contract (V1 slice 1)

**Status: draft feature branch, not a shipped payment/reconciliation product.**

This slice offers a dependency-free, deterministic comparison of an invoice to
**caller-supplied ERC-20 Transfer event records** on Base. It has **no network
access**, does not retrieve chain receipts, and **never verifies settlement**.
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

## Reproduce without services

```bash
python -m pytest tests/integrations/test_base_usdc_matcher.py -q
```

This uses only synthetic typed records. The next separate PR can add a
**read-only chain-evidence adapter** that verifies network chain ID,
transaction receipt success, the native USDC token contract, exact ERC-20
Transfer log, block inclusion and a documented confirmation policy, using
public read-only infrastructure without credentials or transfers. Until
such verification exists, the user interface must say "unverified supplied
record" or leave the feature in planned status.

A later small PR can integrate the read-only result into the report and
UI, and a Developer Toolkit PR can expose reproducible standalone examples.
