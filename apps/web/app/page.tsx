"use client";

import { useState } from "react";
import AskBizLens from "@/components/ask-bizlens";
import BusinessOverview from "@/components/business-overview";
import BusinessReport from "@/components/business-report";
import DiagnosisFeed from "@/components/diagnosis-feed";
import DiagnosisFlow from "@/components/diagnosis-flow";
import EntryScreen from "@/components/entry-screen";
import WhatChanged from "@/components/what-changed";
import WorkspaceShell, { type WorkspaceView } from "@/components/workspace-shell";
import { analyzeCsv, type AnalysisResponse } from "@/lib/api";

type View = "entry" | "diagnosis" | WorkspaceView;

export default function Home() {
  const [view, setView] = useState<View>("entry");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [sample, setSample] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);

  async function tryDemo() {
    if (demoLoading) return;
    setDemoLoading(true);
    setDemoError(null);
    try {
      const response = await fetch("/demo/store.csv", { cache: "no-store" });
      if (!response.ok) throw new Error("The demo dataset could not be loaded.");
      const csv = new File([await response.blob()], "store.csv", { type: "text/csv" });
      // This must be the same live analysis endpoint used by uploaded CSVs.
      const result = await analyzeCsv(csv);
      setAnalysis(result);
      setSample(true);
      setView("overview");
    } catch (reason) {
      setDemoError(reason instanceof Error ? reason.message : "Unable to start the demo.");
    } finally {
      setDemoLoading(false);
    }
  }

  if (view === "entry" || (!analysis && view !== "diagnosis")) {
    return <EntryScreen onStart={() => { setDemoError(null); setView("diagnosis"); }}
      onTryDemo={() => void tryDemo()} demoLoading={demoLoading} demoError={demoError}/>;
  }
  if (view === "diagnosis") {
    return <DiagnosisFlow onComplete={(result) => {
      if (result?.success) {
        setAnalysis(result);
        setSample(false);
        setView("overview");
      } else {
        setView("entry");
      }
    }}/>;
  }
  if (!analysis) return null;

  const content = view === "overview"
    ? <BusinessOverview analysis={analysis} onBack={() => setView("diagnosis")}
        onContinue={() => setView("feed")}/>
    : view === "feed"
    ? <DiagnosisFeed diagnoses={analysis.top_diagnoses}
        onBack={() => setView("overview")} onContinue={() => setView("changes")}/>
    : view === "changes"
    ? <WhatChanged analysis={analysis}
        onBack={() => setView("feed")} onContinue={() => setView("ask")}/>
    : view === "ask"
    ? <AskBizLens analysis={analysis}
        onBack={() => setView("changes")} onContinue={() => setView("report")}/>
    : <BusinessReport analysis={analysis} onBack={() => setView("ask")}/>;

  const current: WorkspaceView = view;
  const metrics = analysis.analysis?.metrics as Record<string, unknown> | undefined;
  return (
    <WorkspaceShell active={current} orderCount={metrics?.orders} sample={sample}
      onNavigate={setView} onExit={() => setView("entry")}>
      {content}
    </WorkspaceShell>
  );
}
