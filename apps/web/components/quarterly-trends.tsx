"use client";

type Quarter = {
  period: string;
  revenue: number;
  gross_profit: number | null;
  gross_margin: number | null;
};

type Props = { data: unknown };

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
  });
}

function formatNumber(value: number | null, percent = false): string {
  if (value === null) return "Not available";
  const formatted = value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return percent ? `${formatted}%` : formatted;
}

function QuarterlyAmounts({ quarters }: { quarters: Quarter[] }) {
  const width = Math.max(540, quarters.length * 112);
  const top = 24;
  const bottom = 178;
  const observed = quarters.flatMap((item) =>
    item.gross_profit === null ? [item.revenue] : [item.revenue, item.gross_profit]
  );
  const upper = Math.max(1, ...observed);
  const lower = Math.min(0, ...observed);
  const y = (value: number) => top + ((upper - value) / (upper - lower)) * (bottom - top);
  const zero = y(0);
  const step = (width - 64) / quarters.length;

  return (
    <figure className="quarter-figure">
      <figcaption>
        <strong>Revenue vs. gross profit</strong>
        <span>Observed calendar quarters · amounts in source dataset units</span>
      </figcaption>
      <div className="quarter-legend">
        <span><i className="quarter-legend-revenue" /> Revenue</span>
        <span><i className="quarter-legend-profit" /> Gross profit</span>
      </div>
      <div className="quarter-svg-wrap">
        <svg viewBox={`0 0 ${width} 226`} role="img"
          aria-label="Revenue and gross profit by quarter. Exact numbers are in the table below.">
          <line x1={24} x2={width - 16} y1={zero} y2={zero} className="quarter-axis" />
          {quarters.map((item, index) => {
            const x = 32 + step * index + step / 2;
            const profit = item.gross_profit;
            const bar = (value: number, left: number, className: string) => (
              <rect x={left} y={Math.min(zero, y(value))} width={19}
                height={Math.max(1, Math.abs(zero - y(value)))} rx={3} className={className} />
            );
            return (
              <g key={item.period}>
                {bar(item.revenue, x - 23, "quarter-bar-revenue")}
                {profit !== null ? bar(profit, x + 2, "quarter-bar-profit") : null}
                <text x={x - 1} y={207} textAnchor="middle" className="quarter-label">
                  {item.period.replace("-", " ")}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </figure>
  );
}

function QuarterlyMargins({ quarters }: { quarters: Quarter[] }) {
  const width = Math.max(540, quarters.length * 112);
  const values = quarters
    .map((item) => item.gross_margin)
    .filter((value): value is number => value !== null);
  const maximum = Math.max(100, ...values);
  const minimum = Math.min(0, ...values);
  const top = 24;
  const bottom = 178;
  const x = (index: number) => 36 + ((width - 72) / Math.max(1, quarters.length - 1)) * index;
  const y = (value: number) =>
    top + ((maximum - value) / (maximum - minimum)) * (bottom - top);
  // Null values break the line: an unknown gross margin is not a zero.
  const segments: string[] = [];
  let path = "";
  quarters.forEach((item, index) => {
    if (item.gross_margin === null) {
      if (path) segments.push(path);
      path = "";
    } else {
      path += `${path ? " L" : "M"}${x(index)} ${y(item.gross_margin)}`;
    }
  });
  if (path) segments.push(path);

  return (
    <figure className="quarter-figure">
      <figcaption>
        <strong>Gross margin trend</strong>
        <span>Gross profit ÷ revenue · calculated from quarterly totals</span>
      </figcaption>
      <div className="quarter-svg-wrap">
        <svg viewBox={`0 0 ${width} 226`} role="img"
          aria-label="Quarterly gross margin percent. Missing costs or nonpositive revenue are left unplotted. Exact values are in the table below.">
          <line x1={24} x2={width - 16} y1={y(0)} y2={y(0)} className="quarter-axis" />
          {segments.map((segment, index) => (
            <path key={index} d={segment} className="quarter-margin-path" />
          ))}
          {quarters.map((item, index) => (
            <g key={item.period}>
              {item.gross_margin === null ? null : (
                <circle cx={x(index)} cy={y(item.gross_margin)} r={4.5}
                  className="quarter-margin-point" />
              )}
              <text x={x(index)} y={207} textAnchor="middle" className="quarter-label">
                {item.period.replace("-", " ")}
              </text>
            </g>
          ))}
        </svg>
      </div>
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
        <p className="quarter-empty">
          Quarterly charts are unavailable. Upload dated sales records to see observed trends.
        </p>
      ) : (
        <>
          <div className="quarter-grid">
            <QuarterlyAmounts quarters={quarters} />
            <QuarterlyMargins quarters={quarters} />
          </div>
          <div className="quarter-table-wrap">
            <table className="quarter-table">
              <caption>Exact quarterly figures (source dataset units; currency unspecified)</caption>
              <thead>
                <tr>
                  <th scope="col">Quarter</th>
                  <th scope="col">Revenue</th>
                  <th scope="col">Gross profit</th>
                  <th scope="col">Gross margin</th>
                </tr>
              </thead>
              <tbody>
                {quarters.map((item) => (
                  <tr key={item.period}>
                    <th scope="row">{item.period}</th>
                    <td>{formatNumber(item.revenue)}</td>
                    <td>{formatNumber(item.gross_profit)}</td>
                    <td>{formatNumber(item.gross_margin, true)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="quarter-footnote">
            Periods with no uploaded transactions are omitted. Margin is unavailable when
            costs are missing or revenue is not positive. No currency is assumed.
          </p>
        </>
      )}
    </section>
  );
}
