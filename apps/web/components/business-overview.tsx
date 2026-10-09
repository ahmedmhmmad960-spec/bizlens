"use client";

import { useMemo } from "react";
import type { AnalysisResponse, Diagnosis } from "@/lib/api";

function number(value: unknown, suffix = "") {
  if (typeof value !== "number") return "—";
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })}${suffix}`;
}

function pickMetric(metrics: Record<string, unknown> | undefined, keys: string[]) {
  for (const key of keys) {
    if (metrics && metrics[key] !== undefined && metrics[key] !== null) return metrics[key];
  }
  return undefined;
}

export default function BusinessOverview({ analysis, onContinue, onBack }: {
  analysis: AnalysisResponse;
  onContinue: () => void;
  onBack: () => void;
}) {
  const metrics = analysis.analysis?.metrics as Record<string, unknown> | undefined;
  const quality = analysis.analysis?.data_quality as Record<string, unknown> | undefined;
  const diagnoses = useMemo(() => analysis.top_diagnoses?.slice(0, 3) ?? [], [analysis.top_diagnoses]);
  const revenue = pickMetric(metrics, ["revenue", "total_revenue"]);
  const grossProfit = pickMetric(metrics, ["gross_profit", "profit"]);
  const margin = pickMetric(metrics, ["gross_margin", "margin"]);
  const orders = pickMetric(metrics, ["orders", "order_count"]);

  return (
    <main className="overview-page">
      <header className="overview-header">
        <button className="logo-button" type="button" onClick={onBack} aria-label="Back to analysis">
          <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>
        </button>
        <span className="flow-label">Business overview</span>
      </header>

      <div className="overview-content">
        <div className="overview-kicker">Your business, clearly</div>
        <h1>Here’s what the data says.</h1>
        <p className="overview-intro">A concise view of the business picture before we move into the diagnoses that deserve your attention.</p>

        <section className="overview-snapshot" aria-label="Business snapshot">
          <div><span>Revenue</span><strong>{typeof revenue === "number" ? number(revenue) : "Available"}</strong><small>Observed</small></div>
          <div><span>Gross profit</span><strong>{typeof grossProfit === "number" ? number(grossProfit) : "Available"}</strong><small>Observed</small></div>
          <div><span>Gross margin</span><strong>{typeof margin === "number" ? number(margin, "%") : "Available"}</strong><small>Observed</small></div>
          <div><span>Orders</span><strong>{number(orders)}</strong><small>Observed</small></div>
        </section>

        <section className="executive-summary">
          <div>
            <span className="category">Executive summary</span>
            <h2>{diagnoses.length ? diagnoses[0].diagnosis : "BizLens found no high-confidence diagnosis."}</h2>
            <p>{diagnoses.length ? "The strongest signal is shown first. The next step is to inspect the evidence behind each finding." : "The available data did not support a strong conclusion."}</p>
          </div>
          <div className="summary-meta">
            <span>Diagnoses</span><strong>{diagnoses.length}</strong>
            <span>Data quality</span><strong>{quality ? "Reviewed" : "Available"}</strong>
          </div>
        </section>

        <section className="overview-findings">
          <div className="section-heading"><span className="category">Top findings</span><span>Evidence-backed</span></div>
          <div className="finding-list">
            {diagnoses.map((diagnosis: Diagnosis, index) => (
              <article key={diagnosis.id ?? diagnosis.code ?? index} className="overview-finding">
                <span className="finding-index">0{index + 1}</span>
                <div><span className="finding-category">{diagnosis.severity || diagnosis.category || "Business signal"}</span><h3>{diagnosis.title || diagnosis.diagnosis}</h3><p>{diagnosis.explanation || diagnosis.description || "Evidence is available in the diagnosis view."}</p></div>
                <span className="finding-confidence">{diagnosis.confidence || "Reviewed"}</span>
              </article>
            ))}
          </div>
        </section>

        <div className="overview-actions"><button className="button secondary" type="button" onClick={onBack}>Back</button><button className="button primary" type="button" onClick={onContinue}>View diagnoses <span aria-hidden="true">→</span></button></div>
      </div>
    </main>
  );
}
