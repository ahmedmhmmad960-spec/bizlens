"use client";

import { ArrowRight, GitBranch } from "lucide-react";

export default function EntryScreen() {
  return (
    <main className="min-h-screen bg-[#08090A] text-[#F5F5F5]">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="text-lg font-semibold tracking-tight">
          BizLens
        </div>

        <div className="flex items-center gap-6 text-sm text-[#A1A7B0]">
          <a href="#" className="transition hover:text-white">
            Docs
          </a>

          <a
            href="#"
            className="flex items-center gap-2 transition hover:text-white"
          >
            <GitBranch size={16} />
            GitHub
          </a>
        </div>
      </nav>

      <section className="mx-auto flex min-h-[calc(100vh-88px)] max-w-7xl items-center px-6 py-20">
        <div className="max-w-3xl">
          <div className="mb-6 inline-flex items-center rounded-full border border-[#24282D] bg-[#101214] px-4 py-2 text-xs text-[#A1A7B0]">
            Evidence-backed business intelligence
          </div>

          <h1 className="text-5xl font-semibold tracking-[-0.04em] sm:text-6xl">
            See your business clearly.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-[#A1A7B0]">
            Turn business data into clear decisions.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <button className="inline-flex items-center gap-2 rounded-xl bg-[#FFD84D] px-6 py-3.5 font-medium text-[#08090A] transition hover:brightness-95">
              Start a Diagnosis
              <ArrowRight size={18} />
            </button>

            <button className="rounded-xl border border-[#24282D] bg-[#101214] px-6 py-3.5 font-medium text-[#F5F5F5] transition hover:bg-[#15181B]">
              Try Demo
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
