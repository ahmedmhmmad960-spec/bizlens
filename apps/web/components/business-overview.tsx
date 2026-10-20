"use client";

import { useMemo } from "react";
import QuarterlyTrends from "@/components/quarterly-trends";
import type { AnalysisResponse, Diagnosis } from "@/lib/api";

function text(value: unknown, fallback = "—"): string {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") return fallback;
  return String(value);
}

function number(value: unknown, suffix = ""): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return text(value);
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}${suffix}`;
}

function comparisonFact(period: unknown, field: string): number | null {
  if (!period || typeof period !== "object") return null;
  const value = (period as Record<string, unknown>)[field];
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export default function BusinessOverview({ analysis, onContinue, onBack }: {
  analysis: AnalysisResponse;
  onContinue: () => void;
  onBack: () => void;
}) {
  const metrics = analysis.analysis?.metrics as Record<string, unknown> | undefined;
  const quality = analysis.analysis?.data_quality as Record<string, unknown> | undefined;
  const diagnoses = useMemo(
    () => analysis.top_diagnoses?.slice(0, 3) ?? [],
    [analysis.top_diagnoses],
  );
  const comparison = analysis.analysis?.period_comparison as
    { previous?: unknown; current?: unknown } | undefined;
  const previousRevenue = comparisonFact(comparison?.previous, "revenue");
  const currentRevenue = comparisonFact(comparison?.current, "revenue");
  const previousProfit = comparisonFact(comparison?.previous, "gross_profit");
  const currentProfit = comparisonFact(comparison?.current, "gross_profit");
  const revenueUpProfitDown = previousRevenue !== null && currentRevenue !== null
    && previousProfit !== null && currentProfit !== null
    && currentRevenue > previousRevenue && currentProfit < previousProfit;

  const mainFinding = diagnoses[0];
  const headline = revenueUpProfitDown
    ? "Revenue grew, but profit declined."
    : mainFinding ? text(mainFinding.diagnosis) : "Your business performance, clearly.";
  const subheadline = revenueUpProfitDown
    ? "Revenue increased between observed periods while gross profit decreased."
    : mainFinding
    ? "The most important detected signal is shown first. Explore the evidence before acting."
    : "These are the observed financial facts in the uploaded data.";
  const cards = [
    { name: "Revenue", value: number(metrics?.revenue), note: "Observed amount" },
    { name: "Gross profit", value: number(metrics?.gross_profit), note: "Observed amount" },
    { name: "Overall gross margin", value: number(metrics?.gross_margin, "%"), note: "From total revenue and cost" },
    { name: "Orders", value: number(metrics?.orders), note: quality?.order_count_basis === "order_id" ? "Distinct order IDs" : "Row-based estimate" },
    { name: "Average order value", value: number(metrics?.aov), note: "Revenue per order" },
  ];

  return (
    <main className="overview-page">
      <header className="overview-header">
        <button className="logo-button" type="button" onClick={onBack} aria-label="Back to analysis">
          <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>
        </button>
        <span className="flow-label">Business overview</span>
      </header>

      <div className="overview-content">
        <div className="overview-kicker">◆ Overview · Business performance</div>
        <div className="workspace-overview-lead">
          <div>
            <h1>{headline}</h1>
            <p className="overview-intro">{subheadline}</p>
          </div>
          <aside className="workspace-key-takeaway">
            <span>◆ The key takeaway</span>
            <p>{mainFinding
              ? text(mainFinding.explanation, "A financial change warrants review.")
              : "No prioritized diagnosis was supported by this dataset."}</p>
            <button type="button" onClick={onContinue} disabled={!mainFinding}>
              Explore the evidence →
            </button>
          </aside>
        </div>

        <section className="overview-snapshot" aria-label="Business snapshot">
          {cards.map((item) => (
            <div key={item.name}>
              <span>{item.name}</span>
              <strong>{item.value}</strong>
              <small>{item.note}</small>
            </div>
          ))}
        </section>

        <QuarterlyTrends data={analysis.analysis?.quarterly_trend} />

        <section className="overview-findings">
          <div className="section-heading">
            <span className="category">Prioritized findings · What deserves your attention</span>
            <span>Up to three findings</span>
          </div>
          {diagnoses.length ? (
            <div className="finding-list">
              {diagnoses.map((diagnosis: Diagnosis, index) => (
                <article key={diagnosis.id ?? diagnosis.code ?? index} className="overview-finding">
                  <span className="finding-index">0{index + 1} · {text(diagnosis.severity, "Signal")}</span>
                  <div>
                    <h3>{text(diagnosis.title || diagnosis.diagnosis)}</h3>
                    <p>{text(diagnosis.explanation || diagnosis.description, "The diagnosis view contains available supporting evidence.")}</p>
                  </div>
                  <button className="workspace-show-evidence" type="button" onClick={onContinue}>
                    Show me why ↗
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="quarter-empty">No prioritized diagnosis is supported by the uploaded data.</p>
          )}
        </section>
        <div className="overview-actions">
          <button className="button secondary" type="button" onClick={onBack}>Back to analysis</button>
          <button className="button primary" type="button" onClick={onContinue}>
            View diagnoses <span aria-hidden="true">→</span>
          </button>
        </div>
      </div>
    </main>
  );
}
