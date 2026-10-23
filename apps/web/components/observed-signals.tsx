"use client";

import { useState } from "react";

type SignalKey = "revenue" | "orders" | "cost" | "discount" | "gross_profit" | "gross_margin";
type Signal = {
  key: SignalKey;
  name: string;
  previous: number;
  current: number;
  change: number;
  changePercent: number | null;
  direction: "up" | "down" | "unchanged";
};

const SUPPORTED: Record<SignalKey, string> = {
  revenue: "Revenue",
  orders: "Orders",
  cost: "Cost",
  discount: "Discounts",
  gross_profit: "Gross profit",
  gross_margin: "Gross margin",
};

const BAR_KEYS: SignalKey[] = ["revenue", "orders", "cost", "discount", "gross_profit"];

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function asSignal(value: unknown): Signal | null {
  if (!value || typeof value !== "object") return null;
  const row = value as Record<string, unknown>;
  if (typeof row.key !== "string" || !Object.hasOwn(SUPPORTED, row.key)) return null;
  if (!finite(row.previous) || !finite(row.current) || !finite(row.change)) return null;
  const changePercent = finite(row.change_percent) ? row.change_percent : null;
  const direction = row.change > 0 ? "up" : row.change < 0 ? "down" : "unchanged";
  return {
    key: row.key as SignalKey,
    name: SUPPORTED[row.key as SignalKey],
    previous: row.previous,
    current: row.current,
    change: row.change,
    changePercent,
    direction,
  };
}

function amount(value: number, key: SignalKey) {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: key === "orders" ? 0 : 2,
    maximumFractionDigits: key === "orders" ? 0 : 2,
  }) + (key === "gross_margin" ? "%" : "");
}

function signed(value: number, suffix = "") {
  return `${value > 0 ? "+" : value < 0 ? "−" : ""}${Math.abs(value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}${suffix}`;
}

export default function ObservedSignals({ changes }: { changes: unknown }) {
  const [selectedKey, setSelectedKey] = useState<SignalKey | null>(null);
  const provided = Array.isArray(changes) ? changes : [];
  const signals = provided.map(asSignal).filter((signal): signal is Signal => signal !== null);
  const bars = BAR_KEYS.flatMap(key => {
    const signal = signals.find(item => item.key === key);
    return signal ? [signal] : [];
  });
  const maximumRelative = Math.max(1,
    ...bars.filter(item => item.changePercent !== null)
      .map(item => Math.abs(item.changePercent!)),
  );
  const margin = signals.find(item => item.key === "gross_margin");
  const active = bars.find(item => item.key === selectedKey) ?? bars[0];

  return (
    <section className="observed-panel observed-premium-panel" aria-labelledby="observed-title">
      <header className="observed-header">
        <div>
          <span className="category">Observed signals</span>
          <h2 id="observed-title">Movement in the financial facts</h2>
        </div>
        <span className="observed-context">Earlier half → Later half</span>
      </header>
      <p className="observed-description">
        Compare relative movements across measured metrics. Bars are scaled to
        the largest available absolute percentage change within this dataset,
        not to profit contribution, business impact, or diagnostic confidence.
        An increase alone does not prove an improvement.
      </p>

      {bars.length ? (
        <>
          <div className="observed-bars observed-premium-bars" role="group" aria-label="Inspect observed financial movements">
            {bars.map(item => {
              const selected = active?.key === item.key;
              return (
                <button key={item.key} type="button" aria-pressed={selected}
                  onFocus={() => setSelectedKey(item.key)}
                  onMouseEnter={() => setSelectedKey(item.key)}
                  onClick={() => setSelectedKey(item.key)}
                  className={`observed-item observed-premium-item ${selected ? "observed-selected" : ""}`}>
                  <div className="observed-item-top">
                    <strong>{item.name}</strong>
                    <span className="observed-delta">
                      {item.changePercent === null
                        ? "Relative % not available"
                        : signed(item.changePercent, "%")}
                    </span>
                  </div>
                  <div className="observed-track" aria-hidden="true">
                    {item.changePercent !== null && item.changePercent !== 0 ? (
                      <span className={`observed-bar observed-${item.key} observed-${item.direction}`}
                        style={{ width: `${Math.abs(item.changePercent) / maximumRelative * 100}%` }} />
                    ) : <span className="observed-zero-track" />}
                  </div>
                  <div className="observed-detail">
                    <span>{item.direction === "up" ? "Increased" : item.direction === "down" ? "Decreased" : "Unchanged"}</span>
                    <span>{item.changePercent === null ? "Previous baseline was zero" : "Select to inspect exact amounts"} <span aria-hidden="true">↗</span></span>
                  </div>
                </button>
              );
            })}
          </div>
          {active ? (
            <div className="observed-inspection" aria-live="polite">
              <div className="observed-inspection-head">
                <span>Inspecting · {active.name}</span>
                <strong>{active.changePercent === null
                  ? "Relative change undefined"
                  : signed(active.changePercent, "%")}</strong>
              </div>
              <div className="observed-inspection-values">
                <div><span>Earlier half</span><strong>{amount(active.previous, active.key)}</strong></div>
                <div><span>Later half</span><strong>{amount(active.current, active.key)}</strong></div>
                <div><span>Observed difference</span><strong>{active.change > 0 ? "+" : active.change < 0 ? "−" : ""}{amount(Math.abs(active.change), active.key)}</strong></div>
              </div>
              <p>{active.changePercent === null
                ? "A relative percentage cannot be calculated from a zero previous value; the absolute difference remains available."
                : "Exact differences use the same deterministic midpoint-period comparison as the results below."}</p>
            </div>
          ) : null}
        </>
      ) : (
        <p className="observed-empty">No comparable financial signals are available.</p>
      )}

      {margin ? (
        <div className="observed-margin">
          <div>
            <span>Gross margin movement</span>
            <strong>{signed(margin.change, " percentage points")}</strong>
          </div>
          <span>{amount(margin.previous, margin.key)} → {amount(margin.current, margin.key)}</span>
        </div>
      ) : null}
      <p className="observed-footnote">
        Midpoint-period comparison across the uploaded date range, not quarter-on-quarter.
        Gross margin is presented separately in percentage points (pp), not a relative
        percentage. Source currency is unspecified.
      </p>
    </section>
  );
}
