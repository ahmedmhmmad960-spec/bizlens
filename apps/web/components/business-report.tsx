"use client";

import type { AnalysisResponse } from "@/lib/api";

type Props = { analysis: AnalysisResponse; onBack: () => void };

function list(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => typeof item === "string" ? item : JSON.stringify(item));
}

export default function BusinessReport({ analysis, onBack }: Props) {
  const report = analysis.business_report ?? {};
  const findings = list(report.findings ?? report.key_findings);
  const actions = list(report.recommended_actions ?? report.actions);
  const limitations = list(report.limitations);
  return <main className="report-page">
    <header className="flow-header"><div className="logo"><span className="logo-mark"><span /></span><span>BizLens</span></div><span className="flow-label">Business report</span></header>
    <div className="report-content">
      <button className="flow-back" onClick={onBack}>← Back</button>
      <div className="report-cover"><span className="flow-kicker">BizLens · Business Diagnosis Report</span><h1>{String(report.title ?? "Your business diagnosis")}</h1><p>{String(report.summary ?? report.executive_summary ?? "Evidence-backed findings and recommended next actions from your analyzed business data.")}</p></div>
      <section className="report-section"><span className="section-label">Findings</span>{findings.length ? findings.map((item, index) => <article className="report-item" key={`${item}-${index}`}><span>0{index + 1}</span><p>{item}</p></article>) : analysis.top_diagnoses.slice(0, 3).map((item, index) => <article className="report-item" key={item.id ?? index}><span>0{index + 1}</span><p>{item.diagnosis}</p></article>)}</section>
      <section className="report-section"><span className="section-label">Recommended actions</span>{actions.length ? actions.map((item, index) => <article className="report-item action" key={`${item}-${index}`}><span>→</span><p>{item}</p></article>) : <div className="report-empty">Recommendations remain attached to each diagnosis.</div>}</section>
      {limitations.length ? <section className="report-section report-limitations"><span className="section-label">Limitations</span>{limitations.map((item, index) => <p key={`${item}-${index}`}>{item}</p>)}</section> : null}
      <footer className="report-footer"><span>Evidence-backed business intelligence</span><button className="button secondary" onClick={() => window.print()}>Print / Save PDF</button></footer>
    </div>
  </main>;
}
