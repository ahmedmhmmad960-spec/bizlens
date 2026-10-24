# Base Sepolia public native-USDC reference — evidence provenance V1

**Status: public explorer reference located. Direct RPC reproduction has NOT
been executed or confirmed by the maintainers in this evidence gate.**

This is a **real, publicly indexed third-party Base Sepolia testnet
transaction**. We are not the sender or recipient. The example invoice is
hypothetical and does not establish that any merchant billed or got paid.
Base Sepolia testnet USDC is not monetary settlement.

## Public reference

- **Explorer:** [BaseScan transaction](https://sepolia.basescan.org/tx/0x32def9a45ee1ba8dadc6fd557719b89ea9b43c87792de9c496ed9b08728a57d0)
- **Transaction:** `0x32def9a45ee1ba8dadc6fd557719b89ea9b43c87792de9c496ed9b08728a57d0`
- **Network:** Base Sepolia, chain ID `84532`
- **Native Circle testnet USDC:** `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **Token Transfer recipient:** `0xBB7Bc0b596d471b34F2770E95f93f0AB9596A649`
- **Transfer amount:** `0.001` USDC = exactly `1000` base units (six decimals)
- **Block reported by explorer:** `42173271`
- **Transaction status shown by explorer:** Success
- **Explorer timestamp:** 2026-05-30 04:20:30 UTC
- **Function on explorer:** `transferWithAuthorization` with a native USDC
  ERC-20 Transfer log. A USDC token transfer is visible; this is **not**
  evidence of an actual BizLens-generated invoice or a purchase.

The contract can also be checked independently in
[Circle's USDC contract list](https://developers.circle.com/stablecoins/usdc-contract-addresses).
The values above are **attributed to the BaseScan explorer page**.
They are not a locally fetched receipt, not a cryptographic proof,
not Ethereum L1 finality and not proof of paid-invoice status.

## Reproduction that does not move any funds

After installing the open-source toolkit from this draft feature branch,
the first command is completely offline. It validates the pinned JSON
reference and displays the explorer attribution **without claiming an RPC
observation**:

```sh
python -m examples.developer_toolkit.base_sepolia_reference
```

The second command is **an explicitly optional read-only network check**
against `https://sepolia.base.org`:

```sh
python -m examples.developer_toolkit.base_sepolia_reference --inspect
```

On `--inspect`, the code calls only `eth_chainId`,
`eth_getTransactionReceipt`, `eth_getBlockByNumber` and
`eth_blockNumber` using the existing allowlisted Base public RPC adapter.
It checks an exact native-USDC transfer, receipt success, RPC chain, canonical
L2 block hash, the 6-block L2 observation policy and that the receipt's
block number matches the explorer's reported block. It does not know an
authoritative log index from the explorer annotation, so it deliberately
leaves the index **unset** and only accepts a single matching Transfer event
in the receipt. It does not guess a log index.

It returns exit code `0` **only** if the current RPC observation passes
these checks; it returns `2` when the observation is absent, contradictory,
noncanonical or unavailable. The program never prints a paid invoice or
L1 finality claim. Even a positive result relies on the public RPC provider.
Public Base RPC access is rate-limited and not suitable for production.

**Important:** tests of this optional RPC workflow use injected **fake**
transports and fake observations. Passing pytest/CI means the validation
policy works as coded; it **does not** assert that a live public RPC request
ran successfully.

## Why include this in a credible open-source demo?

Our deterministic golden financial fixtures demonstrate independently
audited business arithmetic, and this third-party public blockchain
reference lets another engineer reproduce (or dispute) the onchain
observation using their own read-only node. Both are transparent about
provenance and abstain when evidence is insufficient.

The original reference fields are pinned in
[`examples/developer_toolkit/base_sepolia_reference.json`](../examples/developer_toolkit/base_sepolia_reference.json).
They must not be silently changed to fit a failing test.

Before marketing a verified onchain match, retain actual observations from
a successful independent RPC run, note the verification date, block/log
details, and ideally compare multiple independent providers. Production
readiness and security review remain separate acceptance gates.
