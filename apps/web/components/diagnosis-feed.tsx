"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Diagnosis } from "@/lib/api";

type DiagnosisFeedProps = { diagnoses: Diagnosis[]; onBack: () => void; onContinue?: () => void };
type EvidenceRow = { label: string; value: string; tone: "positive" | "critical" | "warning" | "info" | "neutral" };

function text(value: unknown, fallback = "Not available") {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function entries(diagnosis: Diagnosis): EvidenceRow[] {
  const raw = diagnosis.evidence;
  if (!raw || typeof raw !== "object") return [];
  return Object.entries(raw)
    .filter(([key]) => !["confidence", "confidence_score", "limitations"].includes(key))
    .slice(0, 6)
    .map(([label, value]) => ({
      label: label.replaceAll("_", " "),
      value: text(value),
      tone: /cost|loss|margin|profit|discount/i.test(label) ? "critical" : /revenue|order/i.test(label) ? "positive" : "neutral",
    }));
}

function confidenceLevel(diagnosis: Diagnosis) {
  return diagnosis.confidence ? `${diagnosis.confidence[0].toUpperCase()}${diagnosis.confidence.slice(1)}` : "Not available";
}

function impact(diagnosis: Diagnosis) {
  const raw = diagnosis.impact;
  if (!raw || typeof raw !== "object") return { title: "Impact", value: "Not available", detail: "The current data does not support an impact estimate." };
  return {
    title: raw.state === "estimated" ? "Estimated impact" : "Impact",
    value: text(raw.summary ?? raw.value ?? raw.state, "Not available"),
    detail: text(raw.supporting_text ?? raw.supportingText, raw.state === "insufficient" ? "More data is required." : "Based on the analyzed data."),
  };
}

function ShowMeWhy({ diagnosis, onClose }: { diagnosis: Diagnosis; onClose: () => void }) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const rows = entries(diagnosis);
  const impactState = impact(diagnosis);
  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = previous; };
  }, [onClose]);

  const steps = [
    ["Signal", text(diagnosis.explanation || diagnosis.diagnosis), "Observed"],
    ["Calculation", rows.slice(0, 4), ""],
    ["Evidence", rows, "Observed"],
    ["What this suggests", text(diagnosis.explanation, "This is an evidence-backed signal worth investigating."), "Based on your data"],
    [impactState.title, `${impactState.value} — ${impactState.detail}`, impactState.title === "Estimated impact" ? "Estimated" : ""],
    ["Confidence", `${confidenceLevel(diagnosis)}${diagnosis.confidence_score !== undefined ? ` · ${Math.round(diagnosis.confidence_score * 100)} / 100` : ""}`, ""],
    ["Recommended action", text(diagnosis.recommended_action || diagnosis.action?.summary ?? diagnosis.action?.text, "Review the evidence and decide on the next business action."), ""],
  ] as const;

  return <div className="dialog-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
    <aside className="why-dialog" role="dialog" aria-modal="true" aria-labelledby="why-title">
      <header className="dialog-header"><div><span className="flow-kicker">{text(diagnosis.category, "Business case")} · Evidence view</span><h2 id="why-title">{text(diagnosis.diagnosis)}</h2></div><button ref={closeRef} className="dialog-close" onClick={onClose} aria-label="Close evidence view">×</button></header>
      <div className="reasoning-list">
        {steps.map(([title, content, badge], index) => <article className="reasoning-step" key={title}><div className="reasoning-rail"><span>{index + 1}</span>{index < steps.length - 1 && <i />}</div><div><div className="reasoning-title"><h3>{title}</h3>{badge && <span className="trust-badge">{badge}</span>}</div>{Array.isArray(content) ? <div className="evidence-grid">{content.map((row) => <div className="evidence-item" key={`${row.label}-${row.value}`}><span>{row.label}</span><strong className={`tone-${row.tone}`}>{row.value}</strong></div>)}</div> : <p>{content}</p>}</div></article>)}
      </div>
      {diagnosis.limitations?.length ? <div className="dialog-limitation"><strong>Limitation</strong><p>{diagnosis.limitations.join(" ")}</p></div> : null}
      <footer className="dialog-footer"><button className="button secondary" onClick={onClose}>Close evidence view</button></footer>
    </aside>
  </div>;
}

export default function DiagnosisFeed({ diagnoses, onBack, onContinue }: DiagnosisFeedProps) {
  const [selected, setSelected] = useState<Diagnosis | null>(null);
  const top = useMemo(() => diagnoses.slice(0, 5), [diagnoses]);

  return <main className="diagnosis-page">
    <header className="flow-header"><div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div><span className="flow-label">Diagnosis</span></header>
    <div className="diagnosis-content">
      <button className="flow-back" onClick={onBack}>← Back</button>
      <section className="diagnosis-hero"><div><span className="flow-kicker">Business diagnosis</span><h1>Here is what deserves your attention.</h1><p>Every finding is connected to measurable evidence from the data you analyzed.</p></div><span className="diagnosis-count">{top.length} findings</span></section>
      <section className="diagnosis-list" aria-label="Business diagnoses">
        {top.map((diagnosis, index) => { const rows = entries(diagnosis); const imp = impact(diagnosis); return <article className="diagnosis-card-v2" key={diagnosis.id ?? diagnosis.code ?? index}>
          <header className="diagnosis-card-header"><div><span className="diagnosis-category">{text(diagnosis.category, "Business signal")}</span><span className={`priority-label tone-${diagnosis.severity === "high" ? "critical" : "warning"}`}>{diagnosis.severity === "high" ? "High priority" : "Needs attention"}</span></div><h2>{text(diagnosis.diagnosis)}</h2></header>
          <section className="diagnosis-signal"><span className="section-label">Key signal</span><strong>{text(diagnosis.key_signal ?? diagnosis.signal, text(diagnosis.explanation, "Meaningful business signal detected"))}</strong><span className="trust-badge">Observed</span></section>
          <section className="evidence-block-v2"><span className="section-label">What changed</span><div className="evidence-list">{rows.slice(0, 3).map((row) => <div className="evidence-row" key={row.label}><span>{row.label}</span><strong className={`tone-${row.tone}`}>{row.value}</strong></div>)}</div></section>
          <section className="evidence-block-v2"><span className="section-label">Evidence</span><div className="evidence-list">{rows.slice(3).map((row) => <div className="evidence-row" key={row.label}><span>{row.label}</span><strong className={`tone-${row.tone}`}>{row.value}</strong></div>)}{rows.length === 0 && <p className="dialog-muted">No supporting evidence is available.</p>}</div></section>
          <section className="impact-state"><span className="section-label">{imp.title}</span><strong>{imp.value}</strong><p>{imp.detail}</p></section>
          <section className="diagnosis-confidence"><span className="section-label">Confidence</span><div className="confidence-heading"><span className="confidence-bars">{[1,2,3].map((bar) => <i key={bar} className={bar <= (diagnosis.confidence === "high" ? 3 : diagnosis.confidence === "medium" ? 2 : 1) ? "active" : ""} />)}</span><strong>{confidenceLevel(diagnosis)}</strong></div><p>{diagnosis.limitations?.[0] || "Based on the available evidence in the analyzed period."}</p></section>
          <section className="recommended-action"><span className="section-label">Recommended action</span><h4>{text(diagnosis.recommended_action, "Review the evidence behind this finding.")}</h4></section>
          <footer className="diagnosis-card-footer"><button className="show-why-button" onClick={() => setSelected(diagnosis)} aria-haspopup="dialog">Show me why <span>→</span></button></footer>
        </article>; })}
      </section>
      <div className="diagnosis-next"><div><span className="flow-kicker">Next</span><h2>Understand what changed.</h2><p>Trace the period comparison before asking BizLens what to do next.</p></div><button className="button primary" onClick={onContinue}>What changed <span>→</span></button></div>
    </div>
    {selected ? <ShowMeWhy diagnosis={selected} onClose={() => setSelected(null)} /> : null}
  </main>;
}
