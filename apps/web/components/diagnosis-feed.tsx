"use client";

import { useMemo, useState, type ReactNode } from "react";
import type { Diagnosis } from "@/lib/api";
import "./diagnosis-feed.css";

type DiagnosisFeedProps = {
  diagnoses: Diagnosis[];
  onBack: () => void;
};

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "Not available";
  if (typeof value === "number") return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return String(value);
}

function humanize(key: string): string {
  return key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function severityLabel(severity?: string) {
  if (severity === "high") return "High priority";
  if (severity === "medium") return "Medium priority";
  return "Signal";
}

function evidenceEntries(diagnosis: Diagnosis) {
  const evidence = diagnosis.evidence;
  if (!evidence || typeof evidence !== "object") return [];
  return Object.entries(evidence).filter(([key]) => !["confidence", "confidence_score", "limitations"].includes(key));
}

function ShowMeWhyDialog({ diagnosis, onClose }: { diagnosis: Diagnosis; onClose: () => void }) {
  const entries = evidenceEntries(diagnosis);
  const confidence = diagnosis.confidence || "Not available";
  const limitations = diagnosis.limitations || [];

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="why-dialog" role="dialog" aria-modal="true" aria-labelledby="why-title" onMouseDown={(event) => event.stopPropagation()}>
        <div className="dialog-header">
          <div>
            <span className="flow-kicker">Evidence view</span>
            <h2 id="why-title">Why BizLens found this</h2>
            <p>{diagnosis.diagnosis}</p>
          </div>
          <button className="dialog-close" type="button" onClick={onClose} aria-label="Close evidence view">×</button>
        </div>

        <div className="reasoning-list">
          <ReasoningStep number="01" title="Signal"><p>{diagnosis.explanation || diagnosis.description || "BizLens detected a meaningful business signal."}</p></ReasoningStep>
          <ReasoningStep number="02" title="Calculation"><div className="evidence-grid">{entries.length ? entries.slice(0, 4).map(([key, value]) => <div className="evidence-item" key={key}><span>{humanize(key)}</span><strong>{formatValue(value)}</strong></div>) : <div className="evidence-empty">No structured calculation was returned for this diagnosis.</div>}</div></ReasoningStep>
          <ReasoningStep number="03" title="Evidence"><div className="evidence-source"><span className="trust-badge">Observed</span><span>Based on the analyzed business data</span></div></ReasoningStep>
          <ReasoningStep number="04" title="What this suggests"><p>{diagnosis.explanation || "This signal indicates an area worth investigating."}</p><span className="trust-badge">Possible driver</span></ReasoningStep>
          <ReasoningStep number="05" title="Impact"><p>{formatValue(diagnosis.impact?.summary || diagnosis.impact?.value || diagnosis.impact)}</p></ReasoningStep>
          <ReasoningStep number="06" title="Confidence"><div className="confidence-row"><strong>{confidence}</strong>{typeof diagnosis.confidence_score === "number" ? <span>{Math.round(diagnosis.confidence_score)} / 100</span> : null}</div>{limitations.length ? <p className="dialog-muted">{limitations.join(" ")}</p> : null}</ReasoningStep>
          <ReasoningStep number="07" title="Recommended action"><p>{diagnosis.recommended_action || diagnosis.action?.summary || diagnosis.action?.text || "Review the evidence and decide on the next business action."}</p></ReasoningStep>
        </div>

        <div className="dialog-footer"><button className="button secondary" type="button" onClick={onClose}>Close evidence view</button></div>
      </section>
    </div>
  );
}

function ReasoningStep({ number, title, children }: { number: string; title: string; children: ReactNode }) {
  return <article className="reasoning-step"><span className="reasoning-number">{number}</span><div><h3>{title}</h3>{children}</div></article>;
}

export default function DiagnosisFeed({ diagnoses, onBack }: DiagnosisFeedProps) {
  const [selected, setSelected] = useState<Diagnosis | null>(null);
  const top = useMemo(() => diagnoses.slice(0, 3), [diagnoses]);

  return (
    <main className="diagnosis-page">
      <header className="flow-header"><div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div><span className="flow-label">Diagnosis</span></header>
      <div className="diagnosis-content">
        <button className="flow-back" type="button" onClick={onBack}>← Back</button>
        <section className="diagnosis-hero"><div><span className="flow-kicker">Business diagnosis</span><h1>Here is what deserves your attention.</h1><p>Every signal below is tied to evidence from the data you analyzed.</p></div><span className="diagnosis-count">{top.length} priority signals</span></section>

        {top.length === 0 ? <section className="empty-diagnosis"><h2>No supported diagnosis found.</h2><p>BizLens did not find a strong enough signal to present as a priority finding.</p></section> : <section className="diagnosis-list" aria-label="Business diagnoses">
          {top.map((diagnosis, index) => <article className="diagnosis-card" key={`${diagnosis.diagnosis}-${index}`}>
            <div className="diagnosis-card-top"><span className={`severity severity-${diagnosis.severity || "signal"}`}>{severityLabel(diagnosis.severity)}</span><span className="confidence-mini">Confidence · {diagnosis.confidence || "Not available"}</span></div>
            <h2>{diagnosis.diagnosis}</h2>
            <p className="diagnosis-explanation">{diagnosis.explanation || diagnosis.description || "BizLens found a meaningful signal in your business data."}</p>
            <div className="diagnosis-evidence-preview">{evidenceEntries(diagnosis).slice(0, 3).map(([key, value]) => <div key={key}><span>{humanize(key)}</span><strong>{formatValue(value)}</strong></div>)}</div>
            <div className="diagnosis-card-footer"><span className="impact-label">Impact {formatValue(diagnosis.impact?.summary || diagnosis.impact?.value || "Review")}</span><button className="button secondary" type="button" onClick={() => setSelected(diagnosis)}>Show me why <span>→</span></button></div>
          </article>)}
        </section>}

        <div className="diagnosis-next"><div><span className="flow-kicker">Next</span><h2>Turn evidence into action.</h2><p>Recommended actions stay attached to the diagnosis that supports them.</p></div><button className="button primary" type="button" onClick={() => top[0] && setSelected(top[0])}>Review first diagnosis <span>→</span></button></div>
      </div>
      {selected ? <ShowMeWhyDialog diagnosis={selected} onClose={() => setSelected(null)} /> : null}
    </main>
  );
}
