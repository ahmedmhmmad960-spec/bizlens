"use client";

import { useMemo, useRef, useState, type ReactNode } from "react";
import { analyzeCsv, type AnalysisResponse } from "@/lib/api";

export type FlowScreen = "question" | "upload" | "understand" | "quality" | "replay";

const fallbackReplaySteps = [
  "Understanding your data",
  "Checking data quality",
  "Building the business picture",
  "Finding business signals",
  "Checking the evidence",
  "Connecting the signals",
  "Understanding what changed",
  "Explaining what it means",
  "Deciding what to do next",
  "Creating your business report",
];

function BackButton({ onClick }: { onClick: () => void }) {
  return <button className="flow-back" type="button" onClick={onClick}>← Back</button>;
}

function FlowShell({ children, onBack }: { children: ReactNode; onBack: () => void }) {
  return (
    <main className="flow-page">
      <header className="flow-header">
        <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>
        <span className="flow-label">New diagnosis</span>
      </header>
      <div className="flow-content">
        <BackButton onClick={onBack} />
        {children}
      </div>
    </main>
  );
}

export default function DiagnosisFlow({
  initialScreen = "question",
  onComplete,
}: {
  initialScreen?: FlowScreen;
  onComplete: (analysis: AnalysisResponse) => void;
}) {
  const [screen, setScreen] = useState<FlowScreen>(initialScreen);
  const [question, setQuestion] = useState("Full business diagnosis");
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [replayIndex, setReplayIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const progress = useMemo(() => ({ question: 1, upload: 2, understand: 3, quality: 4, replay: 5 }[screen]), [screen]);

  async function loadDemo() {
    setError(null);
    try {
      const response = await fetch("/demo/store.csv", { cache: "no-store" });
      if (!response.ok) throw new Error("Demo dataset could not be loaded.");
      const blob = await response.blob();
      const demoFile = new File([blob], "store.csv", { type: "text/csv" });
      setFile(demoFile);
      setFileName("demo/store.csv");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Demo dataset could not be loaded.");
    }
  }

  async function runAnalysis() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCsv(file);
      setAnalysis(result);
      setReplayIndex(0);
      setScreen("understand");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "BizLens could not analyze this CSV.");
    } finally {
      setLoading(false);
    }
  }

  function next() {
    if (screen === "question") setScreen("upload");
    else if (screen === "upload") void runAnalysis();
    else if (screen === "understand") setScreen("quality");
    else if (screen === "quality") setScreen("replay");
  }

  function back() {
    if (screen === "question") onComplete({} as AnalysisResponse);
    else if (screen === "upload") setScreen("question");
    else if (screen === "understand") setScreen("upload");
    else if (screen === "quality") setScreen("understand");
    else setScreen("quality");
  }

  const metrics = analysis?.analysis?.metrics as Record<string, unknown> | undefined;
  const quality = analysis?.analysis?.data_quality as Record<string, unknown> | undefined;
  const replay = analysis?.demo_replay?.steps as Record<string, unknown>[] | undefined;
  const replaySteps = replay?.length ? replay.map((step) => String(step.title || "Analysis step")) : fallbackReplaySteps;
  const currentReplayStep = replay?.[replayIndex];

  if (screen === "question") {
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero">
        <span className="flow-kicker">Step 01 / 05</span>
        <h1>What do you want to understand?</h1>
        <p>Start with a business question. BizLens will use your data to find the signals that matter.</p>
      </section>
      <section className="question-grid" aria-label="Business questions">
        {["Full business diagnosis", "Profitability", "Revenue", "Products", "Unusual issues"].map((item) => (
          <button key={item} type="button" className={`question-card ${question === item ? "selected" : ""}`} onClick={() => setQuestion(item)}>
            <span>{item}</span><b>{question === item ? "✓" : "→"}</b>
          </button>
        ))}
      </section>
      <div className="flow-actions"><button className="button primary" type="button" onClick={next}>Continue <span>→</span></button></div>
    </FlowShell>;
  }

  if (screen === "upload") {
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero">
        <span className="flow-kicker">Step 02 / 05</span>
        <h1>Bring your business data.</h1>
        <p>Upload an Orders CSV. BizLens will first understand the data before making any diagnosis.</p>
      </section>
      <section className="upload-card">
        <input ref={inputRef} type="file" accept=".csv,text/csv" hidden onChange={(event) => { const selected = event.target.files?.[0] ?? null; setFile(selected); setFileName(selected?.name ?? null); setError(null); }} />
        <div className="upload-icon">↑</div>
        <h2>{fileName ?? "Drop your CSV here"}</h2>
        <p>{fileName ? "File ready for analysis." : "Orders CSV · Up to 50 MB"}</p>
        <button className="button secondary" type="button" onClick={() => inputRef.current?.click()}>{fileName ? "Choose another file" : "Choose CSV"}</button>
        <div className="upload-divider"><span>or</span></div>
        <button className="demo-link" type="button" onClick={() => void loadDemo()}>Use demo dataset</button>
      </section>
      {error ? <div className="flow-error" role="alert">{error}</div> : null}
      <div className="flow-trust">Your file stays in the analysis flow. BizLens will not invent findings when the data cannot support them.</div>
      <div className="flow-actions"><button className="button primary" type="button" disabled={!file || loading} onClick={next}>{loading ? "Analyzing…" : "Analyze data"} <span>→</span></button></div>
    </FlowShell>;
  }

  if (!analysis) return null;

  if (screen === "understand") {
    const items = [
      ["Rows", formatNumber(analysis.analysis.rows)],
      ["Columns", formatNumber(Array.isArray(analysis.analysis.columns) ? analysis.analysis.columns.length : 0)],
      ["Revenue", formatNumber(metrics?.revenue)],
      ["Orders", formatNumber(metrics?.orders)],
      ["Gross profit", formatNumber(metrics?.gross_profit)],
      ["Gross margin", formatPercent(metrics?.gross_margin)],
    ];
    const hasCost = Boolean(quality?.has_cost);
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero compact">
        <span className="flow-kicker">Step 03 / 05</span>
        <h1>BizLens understands your data.</h1>
        <p>Before diagnosis, we establish what the dataset can actually tell us.</p>
      </section>
      <section className="data-summary">{items.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</section>
      <div className={`interpretation ${hasCost ? "" : "warning"}`}><span>{hasCost ? "✓" : "!"}</span><div><strong>{hasCost ? "Profitability analysis is available." : "Profitability analysis is limited."}</strong><p>{hasCost ? "Revenue and cost fields are present, so BizLens can evaluate gross profit and margin." : "No cost field was found, so BizLens will avoid unsupported profitability findings."}</p></div></div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={next}>Check data quality <span>→</span></button></div>
    </FlowShell>;
  }

  if (screen === "quality") {
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero compact">
        <span className="flow-kicker">Step 04 / 05</span>
        <h1>Your data is ready for diagnosis.</h1>
        <p>BizLens uses the actual dataset quality to determine how much confidence each diagnosis deserves.</p>
      </section>
      <section className="quality-card">
        <div className="quality-row"><span>Rows analyzed</span><strong className="positive">{formatNumber(analysis.analysis.rows)}</strong><b>✓</b></div>
        <div className="quality-row"><span>Missing values</span><strong>{formatNumber(quality?.missing_values)}</strong><b>✓</b></div>
        <div className="quality-row"><span>Duplicate rows</span><strong>{formatNumber(quality?.duplicate_rows)}</strong><b>✓</b></div>
        <div className="quality-row"><span>Date coverage</span><strong>{quality?.has_date ? "Available" : "Not available"}</strong><b>{quality?.has_date ? "✓" : "!"}</b></div>
      </section>
      <div className="quality-note"><strong>Why this matters</strong><p>Confidence depends on data completeness, sample size, signal strength, and historical coverage.</p></div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={next}>Review analysis <span>→</span></button></div>
    </FlowShell>;
  }

  const step = replaySteps[replayIndex];
  const stepDescription = String(currentReplayStep?.description || "BizLens is working through the verified business evidence.");
  return <FlowShell onBack={back}>
    <div className="flow-progress"><span style={{ width: "100%" }} /></div>
    <section className="replay-screen">
      <span className="flow-kicker">Step 05 / 05 · Analysis</span>
      <h1>BizLens is working through the evidence.</h1>
      <p>We do the analysis first. AI explains the verified signals after the evidence is established.</p>
      <div className="replay-card">{replaySteps.map((item, index) => { const done = index < replayIndex; const active = index === replayIndex; return <div className={`replay-row ${done ? "done" : ""} ${active ? "active" : ""}`} key={`${item}-${index}`}><span>{done ? "✓" : active ? "•" : String(index + 1).padStart(2, "0")}</span><strong>{item}</strong>{active ? <i /> : null}</div>; })}</div>
      <div className="replay-status"><span className="replay-dot" />{step}<small>{stepDescription}</small></div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={() => replayIndex < replaySteps.length - 1 ? setReplayIndex((value) => value + 1) : onComplete(analysis)}>{replayIndex < replaySteps.length - 1 ? "Continue analysis" : "View diagnosis"} <span>→</span></button></div>
    </section>
  </FlowShell>;
}

function formatNumber(value: unknown) {
  if (typeof value !== "number") return "Not available";
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function formatPercent(value: unknown) {
  if (typeof value !== "number") return "Not available";
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
}
