"use client";

import type { AnalysisResponse } from "@/lib/api";

type Props = { analysis: AnalysisResponse; onBack: () => void; onContinue: () => void };

function value(v: unknown) {
  if (v === null || v === undefined || v === "") return "Not available";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export default function WhatChanged({ analysis, onBack, onContinue }: Props) {
  const rows = analysis.what_changed ?? [];
  return <main className="insight-page">
    <header className="flow-header"><div className="logo"><span className="logo-mark"><span /></span><span>BizLens</span></div><span className="flow-label">What changed</span></header>
    <div className="insight-content">
      <button className="flow-back" onClick={onBack}>← Back</button>
      <span className="flow-kicker">Period comparison</span>
      <h1>What changed in the business?</h1>
      <p className="insight-intro">BizLens compares the available periods so you can separate meaningful movement from noise.</p>
      <section className="change-list">
        {rows.length ? rows.map((row, index) => <article className="change-card" key={`${value(row.metric ?? row.label)}-${index}`}><div><span>{value(row.metric ?? row.label ?? "Business metric")}</span><strong>{value(row.change ?? row.value ?? row.current)}</strong></div><p>{value(row.description ?? row.interpretation ?? row.direction, "Observed period movement in the analyzed data.")}</p></article>) : <div className="empty-insight"><strong>No period comparison available.</strong><p>The uploaded data did not contain enough comparable periods for a reliable change view.</p></div>}
      </section>
      <div className="insight-actions"><button className="button secondary" onClick={onBack}>Back to diagnoses</button><button className="button primary" onClick={onContinue}>Ask BizLens <span>→</span></button></div>
    </div>
  </main>;
}
