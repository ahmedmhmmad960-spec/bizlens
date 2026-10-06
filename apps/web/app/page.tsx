"use client";

import { useState } from "react";
import DiagnosisFlow from "@/components/diagnosis-flow";
import EntryScreen from "@/components/entry-screen";

type View = "entry" | "diagnosis" | "complete";

export default function Home() {
  const [view, setView] = useState<View>("entry");

  if (view === "diagnosis") {
    return <DiagnosisFlow onComplete={() => setView("complete")} />;
  }

  if (view === "complete") {
    return (
      <main className="flow-page completion-page">
        <header className="flow-header">
          <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>
        </header>
        <section className="completion-card">
          <span className="flow-kicker">Analysis complete</span>
          <h1>Your business picture is ready.</h1>
          <p>The next layer is the diagnosis feed: problems, evidence, impact, confidence, and recommended actions.</p>
          <button className="button primary" type="button" onClick={() => setView("entry")}>Back to BizLens <span>→</span></button>
        </section>
      </main>
    );
  }

  return <EntryScreen onStart={() => setView("diagnosis")} />;
}
