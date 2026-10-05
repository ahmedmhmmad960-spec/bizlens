import Link from "next/link";
import { ArrowRight, Play } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pt-16">
      <div className="relative z-10 mx-auto w-full max-w-5xl text-center">
        <div className="mb-7 inline-flex items-center rounded-full border border-[#24282D] bg-[#101214] px-3.5 py-1.5 text-xs font-medium text-[#A1A7B0]">
          Evidence-backed business intelligence
        </div>

        <h1 className="mx-auto max-w-4xl text-5xl font-semibold tracking-[-0.045em] text-[#F5F5F5] sm:text-6xl lg:text-7xl lg:leading-[1.05]">
          See your business clearly.
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-[#A1A7B0] sm:text-lg">
          Turn business data into clear decisions.
        </p>

        <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/question"
            className="group flex h-12 items-center justify-center gap-2 rounded-xl bg-[#FFD84D] px-6 text-sm font-semibold text-[#08090A] transition-transform duration-200 hover:-translate-y-0.5"
          >
            Start a Diagnosis
            <ArrowRight
              size={16}
              strokeWidth={2}
              className="transition-transform group-hover:translate-x-0.5"
            />
          </Link>

          <Link
            href="/demo"
            className="flex h-12 items-center justify-center gap-2 rounded-xl border border-[#24282D] bg-[#101214] px-6 text-sm font-medium text-[#F5F5F5] transition-colors hover:bg-[#15181B]"
          >
            <Play size={15} strokeWidth={1.8} />
            Try Demo
          </Link>
        </div>
      </div>
    </section>
  );
}
