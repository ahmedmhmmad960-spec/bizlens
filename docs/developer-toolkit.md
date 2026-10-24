# BizLens Developer Toolkit V1 — evidence first, reproducible by anyone

**Scope:** portable local Python CLI + importable API for diagnosis and the
read-only Base USDC starter. **Status:** draft PR #24, not yet a released
SDK, payment processor, or transaction settlement verifier.

The point of this toolkit is that another developer can reproduce both
financial diagnosis and Base evidence outcomes without depending on a visual
dashboard, proprietary model, API key, wallet, or payment provider.

## Quickstart (clean checkout; Python 3.11+)

```sh
git clone https://github.com/ahmedmhmmad960-spec/bizlens.git
cd bizlens
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m examples.developer_toolkit.quickstart
```

**Windows PowerShell:** use `.venv\Scripts\Activate.ps1`. A checkout
must contain this feature branch (PR #24) until the toolkit is merged; the
published `main` branch does **not** yet contain the toolkit.

The quickstart runs an independently hand-audited synthetic financial
fixture, checks the expected figures and emits a second **synthetic USDC**
matching example. It does **not** call Base RPC, transfer funds, access AI
provider APIs, or start a web server. Installing Python dependencies may
download open-source packages but requires no paid service or API keys.

## Reproduce the two open-source capabilities separately

**Deterministic diagnosis, evidence and actions:**

```sh
python -m bizlens_toolkit diagnose \
  --csv tests/fixtures/golden/profit_reversal.csv
```

The same code is callable as a library:

```python
from bizlens_toolkit import diagnose_csv

result = diagnose_csv("tests/fixtures/golden/profit_reversal.csv")
assert result["metrics"]["revenue"] == 500.0
assert result["metrics"]["gross_profit"] == 150.0
assert result["metrics"]["gross_margin"] == 30.0
assert "analysis_id" not in result
print(result["recommended_actions"])
```

The JSON output has `schema_version: "bizlens.toolkit.v1"` and contains:
financial metrics, import quality, midpoint-period comparison (if available),
observed quarterly trend, supported diagnoses and numeric evidence,
confidence, recommended actions and limitations. It deliberately omits a
random session ID and raw CSV rows, so a fixed fixture produces stable output.
**It does not imply a business cause is proven**. Its rule-based explanations
can be basic; it does not use a language model.

**Independently audited expected results (not snapshots):**

```sh
python -m bizlens_toolkit verify-golden \
  --csv tests/fixtures/golden/profit_reversal.csv \
  --expected tests/fixtures/golden/profit_reversal.expected.json
```

Pass = process exit code `0` with `passed: true`; mismatch = exit code
`1` and nonempty discrepancies. A bad CSV, missing fixture or invalid
expectation exits `2`; **the verifier never modifies expected baselines**.
The second example is `order_lines.csv` with the adjacent expected JSON.
These expectations are independently recorded and hand-audited; see
[Golden financial fixtures](golden-financial-fixtures.md).

**USDC supplied-record matching (no chain access):**

```sh
python -m bizlens_toolkit usdc-demo
```

Reusable typed Python API:

```python
from bizlens_toolkit import Invoice, TransferRecord, match_invoice
from integrations.base_usdc.matcher import USDC_CONTRACTS

recipient = "0x" + "a" * 40  # FICTIONAL; never request real funds
tx_hash = "0x" + "1" * 64   # FICTIONAL transaction hash
invoice = Invoice("SYNTH-01", 84532, recipient, "12.345678", tx_hash, 0)
record = TransferRecord(
    tx_hash, 0, 84532, USDC_CONTRACTS[84532], recipient, 12_345_678,
)
match = match_invoice(invoice, [record])
assert match.status == "candidate_match"
assert match.onchain_verified is False
```

No amount-only guessing, no wallet signing, no Ethereum JSON-RPC request. A
matching record is merely **caller-supplied matching fields**.

**Optional Base RPC evidence inspection**, with explicit real public
transaction fields, is documented separately in
[Base/USDC Starter Contract](base-usdc-starter-contract.md). Public Base
RPC is rate-limited, not suitable for production; it has its own trust
boundary and is **disabled by default** in the web demo.

## Public Base Sepolia evidence reference (opt-in)

We have located an openly viewable native USDC transfer on Base Sepolia.
You can reproduce its *attributed explorer details* safely and offline:

```sh
python -m examples.developer_toolkit.base_sepolia_reference
```

Only with deliberate permission should you query the public read-only RPC:

```sh
python -m examples.developer_toolkit.base_sepolia_reference --inspect
```

The first command is **not** a chain verification. The second requires
network access but no account, payment or private key; it will not claim
success if RPC evidence is unavailable or contradicts the public reference.
Full transaction, provenance, limitations and verification policy:
[Public Base Sepolia reference](base-sepolia-public-reference.md).

## Truth table — what is and is not established

| Capability | What you may claim | What you must NOT claim |
| --- | --- | --- |
| Diagnosis | Metrics and diagnoses from validated imported facts | Statistical certainty, proven causality |
| Confidence | Heuristic evidence support | Calibrated probability |
| Offline USDC | Supplied transfer fields match an invoice | A real USDC transfer happened |
| RPC receipt | An allowlisted Base RPC observed a successful matching L2 Transfer log with checks | Cryptographic chain proof, Ethereum L1 finality, paid-invoice status |
| Golden check | Engine output matches separately audited fixture | Accuracy certified for all businesses |

The commerce and Base adapters are **separate components**: never merge
synthetic USDC rows into the merchant's revenue or gross profit, and never
report two simultaneous proof levels as one status.

## Installability and limits

`pyproject.toml` includes `bizlens_toolkit*` and `integrations*` in the
wheel packages; the console entry point after installation is
`bizlens-toolkit`. You can also run `python -m bizlens_toolkit` from an
uninstalled source checkout with dependencies already present.

The example's `tests/fixtures/` directory is stored in the repository,
**not guaranteed to be shipped inside a pip wheel**. Once installed on
another machine, pass the path to your own local CSV and expected file.
Do not upload customer data or tx/private keys to public issues. The toolkit
currently has no persisted records, hosted SaaS, analytics telemetry or
transaction execution. Source license: [MIT](../LICENSE).

## Verification / contributor acceptance gate

```sh
python -m pytest tests/toolkit tests/integrations tests/metrics/test_financial_golden.py -q
python -m bizlens_toolkit verify-golden \
  --csv tests/fixtures/golden/order_lines.csv \
  --expected tests/fixtures/golden/order_lines.expected.json
python -m bizlens_toolkit usdc-demo
```

CI also runs backend lint/tests, frontend lint/build and the actual
Next.js → FastAPI HTTP demo journey. **CI does not operate a graphical
browser** and no actual Base Sepolia transaction is claimed as tested.
See [demo acceptance](demo-acceptance.md).

### Extending the adapter responsibly

Add tests for malformed RPC/CSV data and contradictory evidence; enforce
network/asset/receipt checks and duplicate-claim policy; document any
assumption or confidence thresholds; never add token-spending or custody
without a separate explicitly approved design. Production-grade RPC use
requires authentication, rate limiting, observability and reviewed provider
policies. Keep reproducibility offline by default.
