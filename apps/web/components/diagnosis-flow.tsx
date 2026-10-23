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

function Icon({ name, size = 18 }: { name: "arrow" | "upload" | "check" | "file" | "spark" | "lock" | "back"; size?: number }) {
  const paths = {
    arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
    upload: <><path d="M12 16V4M7 9l5-5 5 5" /><path d="M5 20h14" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    file: <><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v5h5M9 13h6M9 17h4" /></>,
    spark: <><path d="m12 3 1.3 4.2L17 8.5l-3.7 1.8L12 15l-1.3-4.7L7 8.5l3.7-1.3z" /><path d="m18.5 14 .7 2.3 2.3.7-.7 2.3-.7-2.3-2.3-.7 2.3-.7z" /></>,
    lock: <><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>,
    back: <><path d="M19 12H5M11 18l-6-6 6-6" /></>,
  };
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function Logo() {
  return <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>;
}

function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "accent" | "positive" | "high" | "warning" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function Button({ children, variant = "primary", icon, onClick, type = "button", disabled = false }: {
  children: ReactNode; variant?: "primary" | "secondary"; icon?: "arrow" | "spark"; onClick?: () => void; type?: "button" | "submit"; disabled?: boolean;
}) {
  return <button type={type} className={`button ${variant}`} onClick={onClick} disabled={disabled}>{children}{icon && <Icon name={icon} size={16} />}</button>;
}

function FlowShell({ step, children, onBack }: { step: number; children: ReactNode; onBack: () => void }) {
  return (
    <main className="flow-page">
      <header className="flow-header">
        <button className="logo-button" type="button" onClick={onBack} aria-label="BizLens home"><Logo /></button>
        <span className="flow-label">New diagnosis</span>
      </header>
      <div className="flow-content">
        <button className="flow-back" type="button" onClick={onBack}><Icon name="back" size={16} /> Back</button>
        <div className="flow-progress" aria-label={`Diagnosis progress: ${step} of 4`}><span style={{ width: `${Math.min(step, 4) * 25}%` }} /></div>
        {children}
      </div>
    </main>
  );
}

export default function DiagnosisFlow({ initialScreen = "question", onComplete }: { initialScreen?: FlowScreen; onComplete: (analysis: AnalysisResponse) => void }) {
  const [screen, setScreen] = useState<FlowScreen>(initialScreen);
  const [question, setQuestion] = useState("Full business diagnosis");
  const [customQuestion, setCustomQuestion] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [replayIndex, setReplayIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const progress = useMemo(() => ({ question: 1, upload: 2, understand: 3, quality: 4, replay: 4 }[screen]), [screen]);

  function selectFile(selected: File | null) {
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setError("Please upload a CSV file with one row per order or line item.");
      setFile(null);
      setFileName(null);
      return;
    }
    if (selected.size > 50 * 1024 * 1024) {
      setError("This file is larger than 50 MB. Please choose a smaller CSV.");
      setFile(null);
      setFileName(null);
      return;
    }
    setError(null);
    setAnalysis(null);
    setFile(selected);
    setFileName(selected.name);
  }

  async function loadDemo() {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch("/demo/store.csv", { cache: "no-store" });
      if (!response.ok) throw new Error("Demo dataset could not be loaded.");
      const blob = await response.blob();
      const demoFile = new File([blob], "store.csv", { type: "text/csv" });
      setAnalysis(null);
      setFile(demoFile);
      setFileName("store.csv");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Demo dataset could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function runAnalysis() {
    if (!file || loading) return;
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
    const questions = [
      ["Profitability", "Why did my profit change?", "chart"],
      ["Revenue", "What happened to my sales?", "chart"],
      ["Products", "Which products need attention?", "file"],
      ["Unusual issues", "Find something unusual.", "spark"],
    ] as const;
    return <FlowShell step={progress} onBack={back}>
      <section className="flow-hero question-hero">
        <Badge>Step 1 of 4</Badge>
        <h1>What do you want to understand?</h1>
        <p>Choose an area to review. BizLens analyzes every supported signal in your CSV regardless of your choice.</p>
      </section>
      <section className="question-grid premium-question-grid" aria-label="Business questions">
        {questions.map(([title, subtitle, icon]) => <button className={`question-card ${question === title ? "selected" : ""}`} key={title} type="button" aria-pressed={question === title} onClick={() => setQuestion(title)}>
          <span className="question-icon"><Icon name={icon === "chart" ? "arrow" : icon === "file" ? "file" : "spark"} /></span>
          <span><strong>{title}</strong><small>{subtitle}</small></span><Icon name="arrow" size={16} />
        </button>)}
        <button className={`question-card primary-path ${question === "Full business diagnosis" ? "selected" : ""}`} type="button" aria-pressed={question === "Full business diagnosis"} onClick={() => setQuestion("Full business diagnosis")}>
          <span className="question-icon"><Icon name="spark" /></span>
          <span><Badge tone="accent">Recommended</Badge><strong>Full Diagnosis</strong><small>Let BizLens find what deserves my attention.</small></span><Icon name="arrow" size={16} />
        </button>
      </section>
      <div className="own-question">
        <label htmlFor="own-question">Or write a review focus of your own</label>
        <div><input id="own-question" value={customQuestion} onChange={(event) => {
          setCustomQuestion(event.target.value);
          if (event.target.value.trim()) setQuestion("Custom");
          else if (question === "Custom") setQuestion("Full business diagnosis");
        }} placeholder="e.g. Where did my margin change?" /></div>
      </div>
      <div className="review-focus-note" role="status">
        <strong>Review focus: {question === "Custom" ? customQuestion.trim() : question}</strong>
        <p>This choice is for navigating your review, not a filter on calculations. All supported diagnoses are still checked.</p>
      </div>
      <div className="flow-actions"><Button onClick={next} icon="arrow">Continue to data</Button></div>
    </FlowShell>;
  }

  if (screen === "upload") {
    return <FlowShell step={progress} onBack={back}>
      <section className="flow-hero upload-hero">
        <Badge>Step 2 of 4</Badge>
        <h1>Bring your business data.<br />BizLens will do the rest.</h1>
        <p>Upload your sales CSV. BizLens checks every supported business signal; your earlier review focus does not change the calculations.</p>
      </section>
      <section className={`upload-card ${file ? "success" : ""}`} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); selectFile(event.dataTransfer.files?.[0] ?? null); }}>
        <input ref={inputRef} type="file" accept=".csv,text/csv" hidden onChange={(event) => selectFile(event.target.files?.[0] ?? null)} />
        {!file && !loading && <><span className="upload-icon"><Icon name="upload" size={25} /></span><h2>Drop your CSV here</h2><p>or <button type="button" onClick={() => inputRef.current?.click()}>browse your files</button></p><small>CSV up to 50 MB</small></>}
        {loading && <><span className="upload-icon active"><Icon name="file" size={25} /></span><h2>Analyzing the selected CSV</h2><p>{fileName} is being processed by the BizLens engine.</p><small>The next screen appears once the analysis is complete.</small></>}
        {file && !loading && <><span className="upload-icon success-icon"><Icon name="check" size={25} /></span><h2>{fileName} is ready</h2><p>CSV selected · ready for diagnosis</p><Badge tone="positive">File selected</Badge><button className="text-action" type="button" onClick={() => { setFile(null); setFileName(null); setAnalysis(null); }}>Choose another file</button></>}
      </section>
      {error ? <div className="flow-error" role="alert">{error}</div> : null}
      <div className="upload-actions"><div className="trust"><Icon name="lock" size={16} /><span><strong>Your data stays yours.</strong> Files are only used for your diagnosis.</span></div><Button variant="secondary" onClick={() => void loadDemo()} icon="spark">Try the demo dataset</Button></div>
      <div className="flow-actions"><Button onClick={next} disabled={!file || loading} icon="arrow">{loading ? "Analyzing…" : "Understand my data"}</Button></div>
    </FlowShell>;
  }

  if (!analysis) return null;

  if (screen === "understand") {
    const items = [
      ["Orders", formatNumber(metrics?.orders)],
      ["Rows analyzed", formatNumber(analysis.analysis.rows)],
      ["Gross profit", formatNumber(metrics?.gross_profit)],
      ["Gross margin", typeof metrics?.gross_margin === "number" ? `${formatNumber(metrics.gross_margin)}%` : "Not available"],
      ["Revenue", formatNumber(metrics?.revenue)],
      ["Cost data", quality?.has_cost ? "Available" : "Not available"],
      ["Discounts", quality?.has_discount ? "Available" : "Not available"],
      ["Analysis status", analysis.success ? "Completed" : "Needs review"],
    ];
    const hasCost = Boolean(quality?.has_cost);
    return <FlowShell step={progress} onBack={back}>
      <section className="flow-hero compact"><Badge>Step 3 of 4</Badge><h1>Understanding your business</h1><p>Before diagnosing anything, BizLens maps the file into a business picture and checks which conclusions are actually supported.</p></section>
      <div className="snapshot-layout"><section className="snapshot-card"><div className="card-title"><div><span className="category">Business snapshot</span><h2>{fileName ?? "Uploaded sales data"}</h2></div><Badge tone="positive">Analyzed</Badge></div><div className="snapshot-grid">{items.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong><Icon name="check" size={14} /></div>)}</div></section><aside className="understanding-note"><span className="question-icon"><Icon name="spark" /></span><span className="category">What we can safely see</span><h3>BizLens only diagnoses signals supported by the uploaded data.</h3><p>Available fields determine which metrics, diagnoses, impacts, and recommendations can be shown.</p></aside></div>
      <div className={`interpretation ${hasCost ? "" : "warning"}`}><span>{hasCost ? "✓" : "!"}</span><div><strong>{hasCost ? "Profitability analysis is available." : "Profitability analysis is limited."}</strong><p>{hasCost ? "Revenue and cost fields are present, so BizLens can evaluate gross profit and margin." : "No cost field was found, so BizLens will avoid unsupported profitability findings."}</p></div></div>
      <div className="flow-actions"><Button onClick={next} icon="arrow">Check data quality</Button></div>
    </FlowShell>;
  }

  if (screen === "quality") {
    const rows = Number(quality?.duplicate_rows ?? 0);
    const missing = Number(quality?.missing_values ?? 0);
    const hasDate = Boolean(quality?.has_date);
    const qualityLabel = rows === 0 && missing === 0 && hasDate ? "Strong data quality" : "Review recommended";
    return <FlowShell step={progress} onBack={back}>
      <section className="flow-hero compact"><Badge tone={qualityLabel === "Strong data quality" ? "positive" : "warning"}>Step 4 of 4</Badge><h1>{qualityLabel === "Strong data quality" ? "Your data is ready for diagnosis." : "A few data quality signals need attention."}</h1><p>BizLens uses data quality as part of its confidence model, so weak inputs do not become overconfident conclusions.</p></section>
      <section className="quality-card">
        <div className="quality-row"><span>Rows analyzed</span><strong className="positive">{formatNumber(analysis.analysis.rows)}</strong><b className="quality-ok">✓</b></div>
        <div className="quality-row"><span>Missing values</span><strong>{formatNumber(quality?.missing_values)}</strong><b className={missing ? "quality-warn" : "quality-ok"}>{missing ? "!" : "✓"}</b></div>
        <div className="quality-row"><span>Duplicate rows</span><strong>{formatNumber(quality?.duplicate_rows)}</strong><b className={rows ? "quality-warn" : "quality-ok"}>{rows ? "!" : "✓"}</b></div>
        <div className="quality-row"><span>Date coverage</span><strong>{hasDate ? "Available" : "Not available"}</strong><b className={hasDate ? "quality-ok" : "quality-warn"}>{hasDate ? "✓" : "!"}</b></div>
      </section>
      <div className={`quality-note ${qualityLabel === "Strong data quality" ? "" : "warning"}`}><strong>Why this matters</strong><p>Confidence depends on completeness, sample size, signal strength, and historical coverage. BizLens keeps those limitations visible instead of hiding them.</p></div>
      <div className="flow-actions"><Button onClick={next} icon="arrow">Review analysis</Button></div>
    </FlowShell>;
  }

  const step = replaySteps[replayIndex];
  const stepDescription = String(currentReplayStep?.description || "Review the evidence and conclusions already produced from the uploaded CSV.");
  const replayPercent = Math.round(((replayIndex + 1) / replaySteps.length) * 100);
  return <FlowShell step={4} onBack={back}>
    <section className="replay-screen">
      <Badge tone="positive">Analysis complete · Review</Badge>
      <h1>Review how BizLens reached its findings.</h1>
      <p>Analysis has already finished. Walk through the recorded stages to understand the evidence, or open your business overview now.</p>
      <div className="premium-replay-progress" role="progressbar" aria-label="Review walkthrough progress"
        aria-valuemin={0} aria-valuemax={100} aria-valuenow={replayPercent}>
        <span style={{ width: `${replayPercent}%` }} />
      </div>
      <div className="replay-insight">
        <span>Review checkpoint {replayIndex + 1} of {replaySteps.length}</span>
        <strong>{stepDescription}</strong>
      </div>
      <div className="replay-card" aria-label="Completed analysis checkpoints">
        {replaySteps.map((item, index) => (
          <div className={`replay-row ${index === replayIndex ? "active" : "done"}`}
            key={`${item}-${index}`} aria-current={index === replayIndex ? "step" : undefined}>
            <span><Icon name="check" size={13} /></span>
            <strong>{item}</strong>
            {index === replayIndex ? <small>Viewing</small> : null}
          </div>
        ))}
      </div>
      <div className="replay-status">{step}<small>Review {replayIndex + 1}/{replaySteps.length}</small></div>
      <div className="replay-review-actions">
        {replayIndex < replaySteps.length - 1 ? (
          <Button onClick={() => setReplayIndex((value) => value + 1)} icon="arrow">Next checkpoint</Button>
        ) : (
          <Button onClick={() => onComplete(analysis)} icon="arrow">View business overview</Button>
        )}
        {replayIndex < replaySteps.length - 1 ? (
          <Button variant="secondary" onClick={() => onComplete(analysis)}>Skip review · View overview</Button>
        ) : null}
      </div>
    </section>
  </FlowShell>;
}

function formatNumber(value: unknown) { if (typeof value !== "number") return "Not available"; return value.toLocaleString(undefined, { maximumFractionDigits: 2 }); }
