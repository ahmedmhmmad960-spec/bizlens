"use client";

import { useState } from "react";
import DiagnosisFlow from "@/components/diagnosis-flow";
import DiagnosisFeed from "@/components/diagnosis-feed";
import EntryScreen from "@/components/entry-screen";
import type { AnalysisResponse } from "@/lib/api";

type View = "entry" | "diagnosis" | "feed";

export default function Home() {
  const [view, setView] = useState<View>("entry");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  if (view === "diagnosis") {
    return <DiagnosisFlow onComplete={(result) => { if (result?.success) { setAnalysis(result); setView("feed"); } else { setView("entry"); } }} />;
  }

  if (view === "feed" && analysis) {
    return <DiagnosisFeed diagnoses={analysis.top_diagnoses} onBack={() => setView("diagnosis")} />;
  }

  return <EntryScreen onStart={() => setView("diagnosis")} />;
}
