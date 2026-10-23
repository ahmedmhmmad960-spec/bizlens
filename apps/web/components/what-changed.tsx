"use client";

import ObservedSignals from "@/components/observed-signals";
import type { AnalysisResponse } from "@/lib/api";

type Props = { analysis: AnalysisResponse; onBack: () => void; onContinue: () => void };
type MetricKey = "revenue" | "orders" | "cost" | "discount" | "gross_profit" | "gross_margin";
type Change = {
  key: MetricKey;
  name: string;
  previous: number;
  current: number;
  delta: number;
  relativePercent: number | null;
};

const METRICS: Record<MetricKey, string> = {
  revenue: "Revenue",
  orders: "Orders",
  cost: "Cost",
  discount: "Discounts",
  gross_profit: "Gross profit",
  gross_margin: "Gross margin",
};

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function asChange(value: unknown): Change | null {
  if (!value || typeof value !== "object") return null;
  const row = value as Record<string, unknown>;
  if (typeof row.key !== "string" || !Object.hasOwn(METRICS, row.key)) return null;
  if (!finite(row.previous) || !finite(row.current) || !finite(row.change)) return null;
  return {
    key: row.key as MetricKey,
    name: METRICS[row.key as MetricKey],
    previous: row.previous,
    current: row.current,
    delta: row.change,
    relativePercent: finite(row.change_percent) ? row.change_percent : null,
  };
}

function formatted(value: number, key: MetricKey) {
  const fractionDigits = key === "orders" ? 0 : 2;
  const amount = value.toLocaleString("en-US", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
  return key === "gross_margin" ? `${amount}%` : amount;
}

function signed(value: number, key: MetricKey) {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  return key === "gross_margin"
    ? `${sign}${Math.abs(value).toFixed(2)} pp`
    : `${sign}${formatted(Math.abs(value), key)}`;
}

function relativeLabel(change: Change) {
  if (change.key === "gross_margin") return "Percentage-point movement";
  if (change.relativePercent === null) {
    return change.previous === 0
      ? "Relative change unavailable — previous value was zero"
      : "Relative change unavailable";
  }
  const sign = change.relativePercent > 0 ? "+" : change.relativePercent < 0 ? "−" : "";
  return `${sign}${Math.abs(change.relativePercent).toFixed(2)}% vs previous`;
}

export default function WhatChanged({ analysis, onBack, onContinue }: Props) {
  const raw = analysis.what_changed ?? [];
  const changes = raw.map(asChange).filter((item): item is Change => item !== null);

  return (
    <main className="insight-page">
      <header className="flow-header">
        <div className="logo"><span className="logo-mark"><span /></span><span>BizLens</span></div>
        <span className="flow-label">What changed</span>
      </header>
      <div className="insight-content">
        <button className="flow-back" type="button" onClick={onBack}>← Back</button>
        <span className="flow-kicker">Period comparison</span>
        <h1>What changed in the business?</h1>
        <p className="insight-intro">
          Compare the measured financial facts from the earlier and later halves of the
          uploaded date range. These are observed changes, not explanations of their causes.
        </p>

        <ObservedSignals changes={raw} />

        <section className="change-breakdown" aria-labelledby="change-breakdown-title">
          <div className="change-breakdown-heading">
            <div>
              <span className="category">The supporting numbers</span>
              <h2 id="change-breakdown-title">Earlier vs later</h2>
            </div>
            <span className="change-period-note">Earlier half → Later half</span>
          </div>

          {changes.length ? (
            <div className="change-comparison-grid">
              {changes.map((change) => {
                const direction = change.delta > 0 ? "up" : change.delta < 0 ? "down" : "flat";
                return (
                  <article className="change-comparison-card" key={change.key}
                    aria-label={`${change.name}: earlier ${formatted(change.previous, change.key)}, later ${formatted(change.current, change.key)}, change ${signed(change.delta, change.key)}`}>
                    <header className="change-comparison-title">
                      <h3>{change.name}</h3>
                      <span className={`change-direction change-${direction}`}>
                        {direction === "up" ? "Increased" : direction === "down" ? "Decreased" : "Unchanged"}
                      </span>
                    </header>
                    <div className="change-period-values">
                      <div><span>Earlier half</span><strong>{formatted(change.previous, change.key)}</strong></div>
                      <span className="change-period-arrow" aria-hidden="true">→</span>
                      <div><span>Later half</span><strong>{formatted(change.current, change.key)}</strong></div>
                    </div>
                    <footer className="change-comparison-footer">
                      <div><span>Measured difference</span><strong>{signed(change.delta, change.key)}</strong></div>
                      <p>{relativeLabel(change)}</p>
                    </footer>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="empty-insight" role="status">
              <strong>No period comparison available.</strong>
              <p>The uploaded data does not have enough comparable, dated financial facts to display changes.</p>
            </div>
          )}
          <p className="change-disclosure">
            Comparison method: midpoint of the observed date range, not calendar
            quarter-on-quarter results. Gross margin differences are percentage
            points (pp), not relative percentages. Financial amounts use the
            uploaded dataset's units; BizLens has not verified a currency.
            An increase or decrease alone does not prove improvement, harm, or causation.
          </p>
        </section>

        <div className="insight-actions">
          <button className="button secondary" type="button" onClick={onBack}>Back to diagnoses</button>
          <button className="button primary" type="button" onClick={onContinue}>Ask BizLens <span>→</span></button>
        </div>
      </div>
    </main>
  );
}
