import { ArrowDownRight, ArrowUpRight, Sparkles } from "lucide-react";

export default function InsightPreview() {
  return (
    <div className="mx-auto mt-20 w-full max-w-3xl">
      <div className="overflow-hidden rounded-2xl border border-[#24282D] bg-[#101214] shadow-2xl">
        <div className="flex items-center justify-between border-b border-[#24282D] px-5 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#FFD84D]/10 text-[#FFD84D]">
              <Sparkles size={14} strokeWidth={1.8} />
            </div>

            <span className="text-xs font-medium text-[#A1A7B0]">
              BizLens Insight
            </span>
          </div>

          <span className="text-xs text-[#6B7280]">Observed</span>
        </div>

        <div className="p-6 sm:p-7">
          <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#6B7280]">
            Profitability
          </p>

          <h2 className="mt-2 text-xl font-semibold tracking-[-0.02em] text-[#F5F5F5] sm:text-2xl">
            Revenue increased, but profit declined.
          </h2>

          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <Metric
              label="Revenue"
              value="+18.4%"
              positive
            />

            <Metric
              label="Costs"
              value="+27.4%"
              negative
            />

            <Metric
              label="Gross margin"
              value="−11.3 pp"
              negative
            />
          </div>

          <div className="mt-6 flex items-center justify-between border-t border-[#24282D] pt-5">
            <p className="max-w-md text-sm leading-6 text-[#A1A7B0]">
              Costs grew faster than revenue, putting pressure on
              profitability.
            </p>

            <button className="hidden text-sm font-medium text-[#FFD84D] transition-opacity hover:opacity-80 sm:block">
              Show me why →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  positive = false,
  negative = false,
}: {
  label: string;
  value: string;
  positive?: boolean;
  negative?: boolean;
}) {
  return (
    <div className="rounded-xl border border-[#24282D] bg-[#15181B] p-4">
      <p className="text-xs text-[#6B7280]">{label}</p>

      <div className="mt-2 flex items-center gap-1.5">
        {positive && (
          <ArrowUpRight
            size={15}
            className="text-[#4ADE80]"
            strokeWidth={2}
          />
        )}

        {negative && (
          <ArrowDownRight
            size={15}
            className="text-[#F87171]"
            strokeWidth={2}
          />
        )}

        <span className="text-lg font-semibold tracking-[-0.02em] text-[#F5F5F5]">
          {value}
        </span>
      </div>
    </div>
  );
}
