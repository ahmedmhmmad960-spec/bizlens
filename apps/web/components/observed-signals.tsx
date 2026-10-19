"use client";

type Signal = {
  key: string;
  name: string;
  previous: number;
  current: number;
  change: number;
  changePercent: number | null;
  direction: "up" | "down" | "unchanged";
};

const SUPPORTED: Record<string, string> = {
  revenue: "Revenue",
  orders: "Orders",
  cost: "Cost",
  discount: "Discounts",
  gross_profit: "Gross profit",
  gross_margin: "Gross margin",
};

const BAR_KEYS = ["revenue", "orders", "cost", "discount", "gross_profit"];

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function asSignal(value: unknown): Signal | null {
  if (!value || typeof value !== "object") return null;
  const row = value as Record<string, unknown>;
  if (typeof row.key !== "string" || !(row.key in SUPPORTED)) return null;
  if (!finite(row.previous) || !finite(row.current) || !finite(row.change)) return null;

  const changePercent =
    row.change_percent === null || row.change_percent === undefined
      ? null
      : finite(row.change_percent) ? row.change_percent : null;
  const direction =
    row.change > 0 ? "up" : row.change < 0 ? "down" : "unchanged";

  return {
    key: row.key,
    name: SUPPORTED[row.key],
    previous: row.previous,
    current: row.current,
    change: row.change,
    changePercent,
    direction,
  };
}

function amount(value: number, suffix = ""): string {
  return `${value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}${suffix}`;
}

export default function ObservedSignals({ changes }: { changes: unknown }) {
  const provided = Array.isArray(changes) ? changes : [];
  const signals = provided
    .map(asSignal)
    .filter((signal): signal is Signal => signal !== null);

  const bars = BAR_KEYS.flatMap((key) => {
    const signal = signals.find((item) => item.key === key);
    return signal ? [signal] : [];
  });
  const magnitude = Math.max(
    1,
    ...bars.filter((item) => item.changePercent !== null)
      .map((item) => Math.abs(item.changePercent!)),
  );
  const margin = signals.find((item) => item.key === "gross_margin");

  return (
    <section className="observed-panel" aria-labelledby="observed-title">
      <header className="observed-header">
        <div>
          <span className="category">Observed signals</span>
          <h2 id="observed-title">Movement in the financial facts</h2>
        </div>
        <span className="observed-context">Previous half → current half</span>
      </header>
      <p className="observed-description">
        Percentage change from the previous period. Bar lengths are scaled to
        the largest available change within this dataset, not to business impact
        or diagnostic confidence. Direction alone does not indicate good or bad performance.
      </p>

      {bars.length ? (
        <div className="observed-bars" role="list" aria-label="Observed percentage changes">
          {bars.map((item) => (
            <div className="observed-item" role="listitem" key={item.key}>
              <div className="observed-item-top">
                <strong>{item.name}</strong>
                <span className="observed-delta">
                  {item.changePercent === null
                    ? "Percentage unavailable"
                    : `${item.changePercent > 0 ? "+" : ""}${amount(item.changePercent, "%")}`}
                </span>
              </div>
              <div className="observed-track" aria-hidden="true">
                {item.changePercent !== null && item.changePercent !== 0 ? (
                  <span className={`observed-bar observed-${item.direction}`}
                    style={{ width: `${100 * Math.abs(item.changePercent) / magnitude}%` }} />
                ) : null}
              </div>
              <div className="observed-detail">
                <span>Previous: {amount(item.previous)} · Current: {amount(item.current)}</span>
                <span>
                  {item.changePercent === null
                    ? "Cannot calculate percentage: previous value is zero"
                    : `${item.direction} · absolute change ${amount(item.change)}`}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="observed-empty">No comparable financial signals are available.</p>
      )}

      {margin ? (
        <div className="observed-margin">
          <div>
            <span>Gross margin movement</span>
            <strong>
              {margin.change > 0 ? "+" : ""}
              {amount(margin.change, " percentage points")}
            </strong>
          </div>
          <span>{amount(margin.previous, "%")} → {amount(margin.current, "%")}</span>
        </div>
      ) : null}
      <p className="observed-footnote">
        Observations use the current V1 midpoint-period comparison, not
        quarter-on-quarter changes. Gross margin is shown separately in
        percentage points because it is not comparable to revenue growth percentages.
      </p>
    </section>
  );
}
