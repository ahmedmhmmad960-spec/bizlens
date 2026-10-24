# Base Sepolia public reference — first live RPC observation attempt

**Date:** 2026-10-24 UTC

**Result: UNCONFIRMED / RPC UNAVAILABLE. Not a verified transfer attestation.**

This note is a permanent, reviewable record of the first attempted
**read-only public Base Sepolia RPC recheck** of the third-party explorer
reference described in [Public Base Sepolia evidence](base-sepolia-public-reference.md).

## Auditable run evidence

- GitHub Actions run: [40099077430](https://github.com/ahmedmhmmad960-spec/bizlens/actions/runs/40099077430)
- Test revision: `8296da94cbf789f97d3b0cc9fd6ac2ef5ef57a50`
- Step: `One-shot external Base Sepolia receipt observation`
- Run command: `python -m examples.developer_toolkit.base_sepolia_reference --inspect`
- Transport: fixed public HTTPS Base Sepolia RPC (`https://sepolia.base.org`).
- Transaction: `0x32def9a45ee1ba8dadc6fd557719b89ea9b43c87792de9c496ed9b08728a57d0`
- CLI results: `inspection=unconfirmed`,
  `receipt_consistent_with_explorer=false`,
  `rpc_observation.status=rpc_unavailable`,
  `rpc_observation.rpc_observed=false`,
  `invoice_paid=false`, `settlement_finality_established=false`.
- The inspection step returned process exit code **2**. Its GitHub Actions
  step was configured as *continue-on-error* intentionally, so a green
  **overall CI status cannot be read as a successful RPC check**.
- The offline financial and synthetic Base test checks ran independently.

The RPC observation did **not** furnish a receipt block, hash,
confirmations, log index, or a successful transfer check. This run
**does not establish whether the explorer annotation was accurate or not**.
The current generic `rpc_unavailable` response does not expose enough
detail to assign a definitive cause to DNS, network gateway, rate limit,
public node availability or response validation. Do not guess.

Base's [public status page](https://status.base.org/) reported a recent
2026-10-23 Sepolia public RPC latency incident. This is only contextual,
**not proof of why this particular call failed**.

## Conservative outcome

- No funds or wallet signatures were used.
- No API keys, secrets or paid RPC providers were required.
- No retry or paid-provider fallback was attempted.
- The one-time live probe was **removed from CI after recording the
  observation**, keeping everyday V1 regression checks offline and
  deterministic.
- A future explicit authorized **single** read-only RPC recheck can use
  the existing `--inspect` entry point, but must attach real receipt/log
  results and corroborate them independently **before** changing the
  release-gate status. Do not infer L1 finality from six L2 blocks.
- Operator-authorized production API access, independent code/security
  review, and manual browser QA remain distinct gates.

**Do not change explorer-reported values or golden fixtures just to turn
an unconfirmed RPC attempt into a passing match.**
