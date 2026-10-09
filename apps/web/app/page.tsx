"use client";

import { useState } from "react";
import AskBizLens from "@/components/ask-bizlens";
import BusinessOverview from "@/components/business-overview";
import BusinessReport from "@/components/business-report";
import DiagnosisFeed from "@/components/diagnosis-feed";
import DiagnosisFlow from "@/components/diagnosis-flow";
import EntryScreen from "@/components/entry-screen";
import WhatChanged from "@/components/what-changed";
import type { AnalysisResponse } from "@/lib/api";

type View = "entry" | "diagnosis" | "overview" | "feed" | "changes" | "ask" | "report";

export default function Home() {
  const [view, setView] = useState<View>("entry");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  if (view === "diagnosis") return <DiagnosisFlow onComplete={(result) => { if (result?.success) { setAnalysis(result); setView("overview"); } else setView("entry"); }} />;
  if (!analysis) return <EntryScreen onStart={() => setView("diagnosis")} />;
  if (view === "overview") return <BusinessOverview analysis={analysis} onBack={() => setView("diagnosis")} onContinue={() => setView("feed")} />;
  if (view === "feed") return <DiagnosisFeed diagnoses={analysis.top_diagnoses} onBack={() => setView("overview")} onContinue={() => setView("changes")} />;
  if (view === "changes") return <WhatChanged analysis={analysis} onBack={() => setView("feed")} onContinue={() => setView("ask")} />;
  if (view === "ask") return <AskBizLens analysis={analysis} onBack={() => setView("changes")} onContinue={() => setView("report")} />;
  return <BusinessReport analysis={analysis} onBack={() => setView("ask")} />;
}
