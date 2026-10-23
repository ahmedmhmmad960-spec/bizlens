"use client";

import { useState } from "react";

type Quarter = {
  period: string;
  revenue: number;
  gross_profit: number | null;
  gross_margin: number | null;
};

type Props = { data: unknown };
type FinancialSeries = "revenue" | "gross_profit";

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function validatedQuarters(value: unknown): Quarter[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item: unknown) => {
    if (!item || typeof item !== "object") return [];
    const candidate = item as Record<string, unknown>;
    if (
      typeof candidate.period !== "string" ||
      !/^\d{4}-Q[1-4]$/.test(candidate.period) ||
      !isNumber(candidate.revenue) ||
      !(candidate.gross_profit === null || isNumber(candidate.gross_profit)) ||
      !(candidate.gross_margin === null || isNumber(candidate.gross_margin))
    ) return [];
    return [candidate as Quarter];
  }).sort((a: Quarter, b: Quarter) => a.period.localeCompare(b.period));
}

function formatNumber(value: number | null, percent = false): string {
  if (value === null) return "Not available";
  const formatted = value.toLocaleString("en-US", {
    minimumFractionDigits: 2, maximumFractionDigits: 2,
  });
  return percent ? `${formatted}%` : formatted;
}

function axisNumber(value: number) {
  return Intl.NumberFormat("en-US", { maximumFractionDigits: 1, notation: "compact" }).format(value);
}

const H = 278;
const TOP = 20;
const BASE = 212;
const LEFT = 65;
const RIGHT = 24;

function ticks(min: number, max: number): number[] {
  return Array.from({ length: 5 }, (_, index) => min + ((max - min) * index) / 4);
}

function QuarterControls({ quarters, selected, setSelected }: {
  quarters: Quarter[];
  selected: number;
  setSelected: (index: number) => void;
}) {
  return <div className="quarter-point-controls" role="group" aria-label="Inspect a calendar quarter">
    {quarters.map((item, index) => (
      <button key={item.period} type="button" aria-pressed={selected === index}
        className={selected === index ? "quarter-point-choice selected" : "quarter-point-choice"}
        onFocus={() => setSelected(index)} onMouseEnter={() => setSelected(index)}
        onClick={() => setSelected(index)}>{item.period.replace("-", " ")}</button>
    ))}
  </div>;
}

function QuarterlyAmounts({ quarters }: { quarters: Quarter[] }) {
  const [selected, setSelected] = useState(quarters.length - 1);
  const [series, setSeries] = useState<FinancialSeries>("revenue");
  const activeIndex = Math.min(Math.max(selected, 0), quarters.length - 1);
  const active = quarters[activeIndex];
  const width = Math.max(530, quarters.length * 112);
  const chartRight = width - RIGHT;
  const plotted = quarters.flatMap((item) =>
    item.gross_profit === null ? [item.revenue] : [item.revenue, item.gross_profit]
  );
  const extent = Math.max(1, ...plotted.map(Math.abs));
  const max = Math.max(0, ...plotted) + extent * 0.08;
  const min = Math.min(0, ...plotted) - (Math.min(...plotted) < 0 ? extent * 0.08 : 0);
  const y = (value: number) => TOP + ((max - value) / (max - min)) * (BASE - TOP);
  const zero = y(0);
  const step = (chartRight - LEFT) / quarters.length;
  const xAt = (index: number) => LEFT + step * (index + 0.5);
  const barWidth = Math.max(12, Math.min(23, step * 0.26));
  const selectedValue = active[series];

  return (
    <figure className="quarter-figure quarter-premium-figure">
      <figcaption>
        <strong>Revenue vs. gross profit</strong>
        <span>Calendar quarter totals · source dataset units</span>
      </figcaption>
      <div className="quarter-legend" role="group" aria-label="Inspect revenue or gross profit">
        <button type="button" aria-pressed={series === "revenue"}
          onClick={() => setSeries("revenue")} className={series === "revenue" ? "quarter-legend-choice chosen" : "quarter-legend-choice"}>
          <i className="quarter-legend-revenue" /> Revenue
        </button>
        <button type="button" aria-pressed={series === "gross_profit"}
          onClick={() => setSeries("gross_profit")} className={series === "gross_profit" ? "quarter-legend-choice chosen" : "quarter-legend-choice"}>
          <i className="quarter-legend-profit" /> Gross profit
        </button>
      </div>
      <div className="quarter-svg-wrap quarter-premium-svg">
        <svg viewBox={`0 0 ${width} ${H}`} role="img"
          aria-label="Quarterly revenue and gross profit. Select a quarter for exact values, or read the data table below.">
          <defs>
            <linearGradient id="quarter-revenue-gradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#5debf2" stopOpacity="1"/>
              <stop offset="100%" stopColor="#158b9c" stopOpacity=".88"/>
            </linearGradient>
            <linearGradient id="quarter-profit-gradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#bba6ff" stopOpacity="1"/>
              <stop offset="100%" stopColor="#7252bd" stopOpacity=".88"/>
            </linearGradient>
          </defs>
          {ticks(min, max).map((tick, i) => <g key={i}>
            <line x1={LEFT} x2={chartRight} y1={y(tick)} y2={y(tick)}
              className={Math.abs(tick) < 1e-9 ? "quarter-zero-axis" : "quarter-gridline"}/>
            <text x={LEFT - 13} y={y(tick) + 4} textAnchor="end" className="quarter-axis-label">{axisNumber(tick)}</text>
          </g>)}
          <line x1={LEFT} x2={chartRight} y1={zero} y2={zero} className="quarter-zero-axis" />
          {quarters.map((item, index) => {
            const x = xAt(index);
            const bar = (value: number, bx: number, kind: FinancialSeries) =>
              <rect x={bx} y={Math.min(y(value), zero)} width={barWidth}
                height={Math.max(1, Math.abs(y(value) - zero))} rx={4}
                className={`quarter-premium-bar ${kind === "revenue" ? "quarter-revenue-fill" : "quarter-profit-fill"} ${selected === index && series === kind ? "quarter-bar-focused" : ""}`}
                onMouseEnter={() => { setSelected(index); setSeries(kind); }}/>;
            return <g key={item.period}>
              {activeIndex === index ? <rect className="quarter-highlight-column" x={LEFT + index * step + 2} y={TOP - 8} width={step - 4} height={BASE - TOP + 28} rx={8}/> : null}
              {bar(item.revenue, x - barWidth - 3, "revenue")}
              {item.gross_profit === null ? null : bar(item.gross_profit, x + 3, "gross_profit")}
              <text x={x} y={252} textAnchor="middle" className="quarter-label">{item.period.replace("-", " ")}</text>
            </g>;
          })}
        </svg>
      </div>
      <QuarterControls quarters={quarters} selected={activeIndex} setSelected={setSelected} />
      <div className="quarter-chart-detail" aria-live="polite">
        <span>{active.period.replace("-", " ")} · {series === "revenue" ? "Revenue" : "Gross profit"}</span>
        <strong className={series === "revenue" ? "detail-cyan" : "detail-iris"}>{formatNumber(selectedValue)}</strong>
        <small>Observed quarter · currency not specified</small>
      </div>
      {quarters.length === 1 ? <p className="quarter-sparse-note">One observed quarter: this is a single total, not evidence of a trend.</p> : null}
    </figure>
  );
}

function QuarterlyMargins({ quarters }: { quarters: Quarter[] }) {
  const [selected, setSelected] = useState(quarters.length - 1);
  const activeIndex = Math.min(Math.max(selected, 0), quarters.length - 1);
  const active = quarters[activeIndex];
  const width = Math.max(530, quarters.length * 112);
  const chartRight = width - RIGHT;
  const values = quarters.map(item => item.gross_margin).filter(isNumber);
  const observedMin = Math.min(0, ...values);
  const observedMax = Math.max(100, ...values);
  const pad = Math.max(1, (observedMax - observedMin) * .025);
  const minimum = observedMin < 0 ? observedMin - pad : observedMin;
  const maximum = observedMax > 100 ? observedMax + pad : observedMax;
  const x = (index: number) =>
    quarters.length === 1 ? (LEFT + chartRight) / 2 :
      LEFT + ((chartRight - LEFT) / (quarters.length - 1)) * index;
  const y = (value: number) => TOP + ((maximum - value) / (maximum - minimum)) * (BASE - TOP);
  // Missing margins break paths: never fill an unknown value with zero.
  const segments: string[] = [];
  let segment = "";
  quarters.forEach((item, index) => {
    if (item.gross_margin === null) {
      if (segment) segments.push(segment);
      segment = "";
    } else {
      segment += `${segment ? " L" : "M"}${x(index)} ${y(item.gross_margin)}`;
    }
  });
  if (segment) segments.push(segment);

  return (
    <figure className="quarter-figure quarter-premium-figure">
      <figcaption>
        <strong>Gross margin trend</strong>
        <span>Gross profit ÷ revenue · quarter-by-quarter (%)</span>
      </figcaption>
      <div className="quarter-chart-tag">Measured margin · not an estimated projection</div>
      <div className="quarter-svg-wrap quarter-premium-svg">
        <svg viewBox={`0 0 ${width} ${H}`} role="img"
          aria-label="Observed quarterly gross margin percentages. Select a quarter for the exact value, or read the data table below.">
          <defs>
            <linearGradient id="quarter-margin-shade" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#FFD84D" stopOpacity=".16"/>
              <stop offset="100%" stopColor="#FFD84D" stopOpacity="0"/>
            </linearGradient>
          </defs>
          {ticks(minimum, maximum).map((tick, i) => <g key={i}>
            <line x1={LEFT} x2={chartRight} y1={y(tick)} y2={y(tick)} className="quarter-gridline"/>
            <text x={LEFT - 12} y={y(tick) + 4} textAnchor="end" className="quarter-axis-label">{axisNumber(tick)}%</text>
          </g>)}
          {segments.map((path, index) => <path key={index} d={path} className="quarter-premium-margin-line"/>)}
          {active.gross_margin !== null ? <line x1={x(activeIndex)} x2={x(activeIndex)} y1={TOP} y2={BASE}
            className="quarter-focus-guide"/> : null}
          {quarters.map((item, index) => <g key={item.period}>
            {item.gross_margin === null ? null : <circle
              cx={x(index)} cy={y(item.gross_margin)} r={activeIndex === index ? 6.5 : 4.5}
              className={activeIndex === index ? "quarter-margin-point is-active" : "quarter-margin-point"}
              onMouseEnter={() => setSelected(index)}/>}
            <text x={x(index)} y={252} textAnchor="middle" className="quarter-label">
              {item.period.replace("-", " ")}
            </text>
          </g>)}
        </svg>
      </div>
      <QuarterControls quarters={quarters} selected={activeIndex} setSelected={setSelected} />
      <div className="quarter-chart-detail" aria-live="polite">
        <span>{active.period.replace("-", " ")} · Gross margin</span>
        <strong className="detail-gold">{formatNumber(active.gross_margin, true)}</strong>
        <small>Calculated from observed quarter totals</small>
      </div>
      {quarters.length === 1 ? <p className="quarter-sparse-note">Only one quarter is present; a margin trend cannot be established.</p> : null}
    </figure>
  );
}

export default function QuarterlyTrends({ data }: Props) {
  const quarters = validatedQuarters(data);

  return (
    <section className="quarter-section" aria-labelledby="quarter-title">
      <div className="quarter-section-header">
        <div>
          <span className="category">Financial trends</span>
          <h2 id="quarter-title">Performance by quarter</h2>
        </div>
        <span className="quarter-data-label">Observed data · calendar quarters (UTC)</span>
      </div>
      {!quarters.length ? (
        <p className="quarter-empty">Quarterly charts are unavailable. Upload dated sales records to see observed trends.</p>
      ) : (
        <>
          <div className="quarter-grid">
            <QuarterlyAmounts quarters={quarters} />
            <QuarterlyMargins quarters={quarters} />
          </div>
          <div className="quarter-table-wrap">
            <table className="quarter-table">
              <caption>Exact quarterly figures (source dataset units; currency unspecified)</caption>
              <thead><tr>
                <th scope="col">Quarter</th><th scope="col">Revenue</th>
                <th scope="col">Gross profit</th><th scope="col">Gross margin</th>
              </tr></thead>
              <tbody>
                {quarters.map(item => <tr key={item.period}>
                  <th scope="row">{item.period}</th>
                  <td>{formatNumber(item.revenue)}</td>
                  <td>{formatNumber(item.gross_profit)}</td>
                  <td>{formatNumber(item.gross_margin, true)}</td>
                </tr>)}
              </tbody>
            </table>
          </div>
          <p className="quarter-footnote">Periods with no uploaded transactions are omitted. Margin is unavailable when costs are missing or revenue is nonpositive. Axes are labeled; quarter values and currency provenance are given in the table and interactive detail. No currency is assumed.</p>
        </>
      )}
    </section>
  );
}
