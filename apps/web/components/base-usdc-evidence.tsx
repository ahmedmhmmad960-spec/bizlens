"use client";

import { useState } from "react";

type MatchResult = {
  invoice_id: string;
  status: string;
  reason: string;
  onchain_verified: boolean;
  record?: { tx_hash: string; log_index: number; amount_raw: number } | null;
};
type DemoResponse = {
  success: true;
  source: "synthetic_fixture";
  network: string;
  real_transaction: false;
  onchain_verified: false;
  warning: string;
  results: MatchResult[];
};
type ReceiptObservation = {
  invoice_id: string;
  status: string;
  explanation: string;
  chain_id: number;
  tx_hash: string | null;
  block_number: number | null;
  confirmations: number | null;
  log_index: number | null;
  rpc_observed: boolean;
};
type VerifyResponse = {
  success: true;
  mode: string;
  network: string;
  warning: string;
  result: ReceiptObservation;
};

const OUTCOMES: Record<string, string> = {
  candidate_match: "Fields match · unverified record",
  rpc_observed_match: "Matching transfer observed by Base RPC",
  missing: "Not found in supplied data",
  duplicate: "Ambiguous or duplicate transfer reference",
  partial: "Amount is below invoice",
  amount_mismatch: "Amount differs from invoice",
  wrong_chain: "Incorrect network",
  wrong_token: "Not native USDC",
  wrong_address: "Different recipient",
  pending_or_missing: "No receipt observed",
  insufficient_confirmations: "Too few L2 block confirmations",
  noncanonical_block: "Receipt block no longer canonical",
  missing_transfer: "No matching Transfer event",
  ambiguous_transfer: "Multiple Transfer events",
  invalid_evidence: "Invalid evidence",
  rpc_unavailable: "Base RPC unavailable",
  failed_transaction: "Transaction reverted",
  duplicate_claim: "Transfer claimed by multiple invoices",
};

function statusLabel(status: string) {
  return OUTCOMES[status] ?? "Unclassified evidence status";
}

async function responseData<T>(response: Response): Promise<T> {
  const payload: unknown = await response.json().catch(() => null);
  if (!payload || typeof payload !== "object") throw new Error("Invalid API response.");
  const data = payload as Record<string, unknown>;
  if (!response.ok || data.success !== true) {
    throw new Error(typeof data.error === "string" ? data.error : "Evidence request failed.");
  }
  return payload as T;
}

export default function BaseUsdcEvidence() {
  const [demo, setDemo] = useState<DemoResponse | null>(null);
  const [inspection, setInspection] = useState<VerifyResponse | null>(null);
  const [demoBusy, setDemoBusy] = useState(false);
  const [verifyBusy, setVerifyBusy] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [chain, setChain] = useState<84532 | 8453>(84532);
  const [invoiceId, setInvoiceId] = useState("");
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  const [txHash, setTxHash] = useState("");
  const [logIndex, setLogIndex] = useState("");

  async function showDemo() {
    if (demoBusy) return;
    setDemoBusy(true);
    setDemo(null);
    setDemoError(null);
    try {
      const response = await fetch("/api/base-usdc/demo", { cache: "no-store" });
      setDemo(await responseData<DemoResponse>(response));
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : "Unable to load synthetic examples.");
    } finally {
      setDemoBusy(false);
    }
  }

  async function verify(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (verifyBusy) return;
    setVerifyBusy(true);
    setVerifyError(null);
    setInspection(null);
    try {
      const idx = logIndex.trim() ? Number(logIndex) : null;
      if (idx !== null && (!Number.isSafeInteger(idx) || idx < 0)) {
        throw new Error("Log index must be a nonnegative integer.");
      }
      const response = await fetch("/api/base-usdc/inspect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          invoice_id: invoiceId.trim(),
          chain_id: chain,
          recipient: recipient.trim(),
          amount_usdc: amount.trim(),
          tx_hash: txHash.trim(),
          log_index: idx,
        }),
      });
      setInspection(await responseData<VerifyResponse>(response));
    } catch (error) {
      setVerifyError(error instanceof Error ? error.message : "RPC evidence could not be inspected.");
    } finally {
      setVerifyBusy(false);
    }
  }

  return (
    <main className="base-evidence-page">
      <span className="flow-kicker">Optional evidence adapter · Base / native USDC</span>
      <h1>Match an invoice to transaction evidence.</h1>
      <p className="base-evidence-intro">
        Compare USDC payment references without transferring funds or connecting a wallet.
        This does not change BizLens sales metrics, mark an invoice paid, or prove final settlement.
      </p>

      <section className="base-evidence-section" aria-labelledby="base-offline-heading">
        <div className="base-evidence-section-head">
          <div>
            <span className="category">01 · Offline reproducibility</span>
            <h2 id="base-offline-heading">Explore the synthetic evidence cases</h2>
          </div>
          <span className="base-evidence-tag">No network · synthetic only</span>
        </div>
        <p>See how the same matcher distinguishes a matching record, a partial amount, and a missing reference.</p>
        <button className="button secondary" type="button" onClick={() => void showDemo()}
          disabled={demoBusy}>{demoBusy ? "Loading cases…" : "Run offline sample"} →</button>
        {demoError ? <p className="base-evidence-error" role="alert">{demoError}</p> : null}
        {demo ? (
          <div className="base-evidence-output" aria-live="polite">
            <p className="base-evidence-warning">{demo.warning}</p>
            <div className="base-evidence-results">
              {demo.results.map((item) => (
                <article key={item.invoice_id} className="base-evidence-result">
                  <strong>{item.invoice_id}</strong>
                  <span>{statusLabel(item.status)}</span>
                  <p>{item.reason}</p>
                </article>
              ))}
            </div>
            <p className="base-evidence-limits">
              Source: {demo.source} · {demo.network} · No real transaction and no onchain verification.
            </p>
          </div>
        ) : null}
      </section>

      <section className="base-evidence-section" aria-labelledby="base-live-heading">
        <div className="base-evidence-section-head">
          <div>
            <span className="category">02 · Opt-in read-only inspection</span>
            <h2 id="base-live-heading">Inspect a Base receipt</h2>
          </div>
          <span className="base-evidence-tag">RPC disabled by default</span>
        </div>
        <p>
          This sends public transaction fields to an allowlisted Base RPC only when
          the server administrator explicitly enables inspection. Use no private keys.
          Base RPC evidence is not Ethereum finality or proof of settlement.
        </p>
        <form className="base-evidence-form" onSubmit={(event) => void verify(event)}>
          <label>Network
            <select value={chain} onChange={(event) => setChain(Number(event.target.value) as 84532 | 8453)}>
              <option value={84532}>Base Sepolia (testnet)</option>
              <option value={8453}>Base Mainnet</option>
            </select>
          </label>
          <label>Invoice reference
            <input required maxLength={80} value={invoiceId} onChange={(event) => setInvoiceId(event.target.value)}
              placeholder="INV-001" />
          </label>
          <label>Recipient (EVM address)
            <input required minLength={42} maxLength={42} spellCheck={false} autoComplete="off"
              value={recipient} onChange={(event) => setRecipient(event.target.value)}
              placeholder="0x… (40 hex characters)" />
          </label>
          <label>Invoice amount (USDC, 6 decimals max)
            <input required maxLength={64} spellCheck={false} inputMode="decimal"
              value={amount} onChange={(event) => setAmount(event.target.value)}
              placeholder="12.345678" />
          </label>
          <label>Transaction hash
            <input required minLength={66} maxLength={66} spellCheck={false} autoComplete="off"
              value={txHash} onChange={(event) => setTxHash(event.target.value)}
              placeholder="0x… (64 hex characters)" />
          </label>
          <label>Transfer log index (optional)
            <input min={0} step={1} type="number" value={logIndex}
              onChange={(event) => setLogIndex(event.target.value)}
              placeholder="Use when the transaction contains multiple transfers" />
          </label>
          <button type="submit" className="button primary" disabled={verifyBusy}>
            {verifyBusy ? "Inspecting receipt…" : "Inspect read-only receipt"} →
          </button>
        </form>
        {verifyError ? <div className="base-evidence-error" role="alert">{verifyError}</div> : null}
        {inspection ? (
          <div className="base-evidence-output" role="status">
            <span className="category">Receipt observation · {inspection.network}</span>
            <h3>{statusLabel(inspection.result.status)}</h3>
            <p>{inspection.result.explanation}</p>
            <dl className="base-evidence-facts">
              <div><dt>Invoice</dt><dd>{inspection.result.invoice_id}</dd></div>
              <div><dt>Block</dt><dd>{inspection.result.block_number ?? "Not observed"}</dd></div>
              <div><dt>L2 confirmations</dt><dd>{inspection.result.confirmations ?? "Not observed"}</dd></div>
              <div><dt>Transfer log</dt><dd>{inspection.result.log_index ?? "Not observed"}</dd></div>
              <div><dt>Evidence source</dt><dd>Read-only Base RPC</dd></div>
              <div><dt>Final settlement</dt><dd>Not established</dd></div>
            </dl>
            <p className="base-evidence-warning">{inspection.warning}</p>
          </div>
        ) : null}
      </section>
      <p className="base-evidence-limits">
        Experimental V1 evidence adapter · separate from commerce analysis · zero wallet signing.
      </p>
    </main>
  );
}
