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
import type { AnalysisResponse } from "@/lib/api";

type View = "entry" | "diagnosis" | WorkspaceView;

export default function Home() {
  const [view, setView] = useState<View>("entry");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  if (view === "diagnosis") {
    return (
      <DiagnosisFlow
        onComplete={(result) => {
          if (result?.success) {
            setAnalysis(result);
            setView("overview");
          } else {
            setView("entry");
          }
        }}
      />
    );
  }

  if (view === "entry" || !analysis) {
    return <EntryScreen onStart={() => setView("diagnosis")} />;
  }

  const content =
    view === "overview" ? (
      <BusinessOverview
        analysis={analysis}
        onBack={() => setView("diagnosis")}
        onContinue={() => setView("feed")}
      />
    ) : view === "feed" ? (
      <DiagnosisFeed
        diagnoses={analysis.top_diagnoses}
        onBack={() => setView("overview")}
        onContinue={() => setView("changes")}
      />
    ) : view === "changes" ? (
      <WhatChanged
        analysis={analysis}
        onBack={() => setView("feed")}
        onContinue={() => setView("ask")}
      />
    ) : view === "ask" ? (
      <AskBizLens
        analysis={analysis}
        onBack={() => setView("changes")}
        onContinue={() => setView("report")}
      />
    ) : (
      <BusinessReport analysis={analysis} onBack={() => setView("ask")} />
    );

  return (
    <WorkspaceShell
      active={view}
      analysis={analysis}
      onNavigate={setView}
      onNewAnalysis={() => setView("diagnosis")}
      onLanding={() => {
        setAnalysis(null);
        setView("entry");
      }}
    >
      {content}
    </WorkspaceShell>
  );
}
