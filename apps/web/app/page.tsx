"use client";

import { useState } from "react";
import BusinessOverview from "@/components/business-overview";
import DiagnosisFlow from "@/components/diagnosis-flow";
import DiagnosisFeed from "@/components/diagnosis-feed";
import EntryScreen from "@/components/entry-screen";
import type { AnalysisResponse } from "@/lib/api";

type View = "entry" | "diagnosis" | "overview" | "feed";

export default function Home() {
  const [view, setView] = useState<View>("entry");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  if (view === "diagnosis") {
    return <DiagnosisFlow onComplete={(result) => {
      if (result?.success) {
        setAnalysis(result);
        setView("overview");
      } else {
        setView("entry");
      }
    }} />;
  }

  if (view === "overview" && analysis) {
    return <BusinessOverview analysis={analysis} onBack={() => setView("diagnosis")} onContinue={() => setView("feed")} />;
  }

  if (view === "feed" && analysis) {
    return <DiagnosisFeed diagnoses={analysis.top_diagnoses} onBack={() => setView("overview")} />;
  }

  return <EntryScreen onStart={() => setView("diagnosis")} />;
}
