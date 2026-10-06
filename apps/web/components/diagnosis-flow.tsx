"use client";

import { useMemo, useRef, useState } from "react";

export type FlowScreen = "question" | "upload" | "understand" | "quality" | "replay";

const replaySteps = [
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

function FlowShell({ children, onBack }: { children: React.ReactNode; onBack: () => void }) {
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

export default function DiagnosisFlow({ initialScreen = "question", onComplete }: { initialScreen?: FlowScreen; onComplete: () => void }) {
  const [screen, setScreen] = useState<FlowScreen>(initialScreen);
  const [question, setQuestion] = useState("Full business diagnosis");
  const [fileName, setFileName] = useState<string | null>(null);
  const [replayIndex, setReplayIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const progress = useMemo(() => ({ question: 1, upload: 2, understand: 3, quality: 4, replay: 5 }[screen]), [screen]);

  function next() {
    if (screen === "question") setScreen("upload");
    else if (screen === "upload") setScreen("understand");
    else if (screen === "understand") setScreen("quality");
    else if (screen === "quality") {
      setReplayIndex(0);
      setScreen("replay");
    }
  }

  function back() {
    if (screen === "question") onComplete();
    else if (screen === "upload") setScreen("question");
    else if (screen === "understand") setScreen("upload");
    else if (screen === "quality") setScreen("understand");
    else setScreen("quality");
  }

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
        <input ref={inputRef} type="file" accept=".csv,text/csv" hidden onChange={(event) => setFileName(event.target.files?.[0]?.name ?? null)} />
        <div className="upload-icon">↑</div>
        <h2>{fileName ?? "Drop your CSV here"}</h2>
        <p>{fileName ? "File ready for analysis." : "Orders CSV · Up to 50 MB"}</p>
        <button className="button secondary" type="button" onClick={() => inputRef.current?.click()}>{fileName ? "Choose another file" : "Choose CSV"}</button>
        <div className="upload-divider"><span>or</span></div>
        <button className="demo-link" type="button" onClick={() => setFileName("demo/store.csv")}>Use demo dataset</button>
      </section>
      <div className="flow-trust">Your file stays in the analysis flow. BizLens will not invent findings when the data cannot support them.</div>
      <div className="flow-actions"><button className="button primary" type="button" disabled={!fileName} onClick={next}>Continue <span>→</span></button></div>
    </FlowShell>;
  }

  if (screen === "understand") {
    const items = [["Orders", "4,812"], ["Date range", "9 months"], ["Products", "42"], ["Customers", "3,184"], ["Revenue", "Available"], ["Cost", "Available"]];
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero compact">
        <span className="flow-kicker">Step 03 / 05</span>
        <h1>BizLens understands your data.</h1>
        <p>Before diagnosis, we establish what the dataset can actually tell us.</p>
      </section>
      <section className="data-summary">
        {items.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </section>
      <div className="interpretation"><span>✓</span><div><strong>Profitability analysis is available.</strong><p>Revenue and cost fields are present, so BizLens can evaluate gross profit and margin.</p></div></div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={next}>Check data quality <span>→</span></button></div>
    </FlowShell>;
  }

  if (screen === "quality") {
    return <FlowShell onBack={back}>
      <div className="flow-progress"><span style={{ width: `${progress * 20}%` }} /></div>
      <section className="flow-hero compact">
        <span className="flow-kicker">Step 04 / 05</span>
        <h1>Your data is ready for diagnosis.</h1>
        <p>We found a complete enough dataset for the core profitability signals.</p>
      </section>
      <section className="quality-card">
        <div className="quality-row"><span>Valid orders</span><strong className="positive">4,812</strong><b>✓</b></div>
        <div className="quality-row"><span>Required fields</span><strong className="positive">Complete</strong><b>✓</b></div>
        <div className="quality-row"><span>Duplicate orders</span><strong>0 detected</strong><b>✓</b></div>
        <div className="quality-row"><span>Invalid dates</span><strong>0 detected</strong><b>✓</b></div>
      </section>
      <div className="quality-note"><strong>Why this matters</strong><p>Confidence in a diagnosis depends on data completeness, sample size, signal strength, and historical coverage.</p></div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={next}>Run diagnosis <span>→</span></button></div>
    </FlowShell>;
  }

  const step = replaySteps[replayIndex];
  return <FlowShell onBack={back}>
    <div className="flow-progress"><span style={{ width: "100%" }} /></div>
    <section className="replay-screen">
      <span className="flow-kicker">Step 05 / 05 · Analysis</span>
      <h1>BizLens is working through the evidence.</h1>
      <p>We do the analysis first. AI explains the verified signals after the evidence is established.</p>
      <div className="replay-card">
        {replaySteps.map((item, index) => {
          const done = index < replayIndex;
          const active = index === replayIndex;
          return <div className={`replay-row ${done ? "done" : ""} ${active ? "active" : ""}`} key={item}><span>{done ? "✓" : active ? "•" : String(index + 1).padStart(2, "0")}</span><strong>{item}</strong>{active ? <i /> : null}</div>;
        })}
      </div>
      <div className="replay-status"><span className="replay-dot" />{step}</div>
      <div className="flow-actions"><button className="button primary" type="button" onClick={() => replayIndex < replaySteps.length - 1 ? setReplayIndex((value) => value + 1) : onComplete()}>{replayIndex < replaySteps.length - 1 ? "Continue analysis" : "View diagnosis"} <span>→</span></button></div>
    </section>
  </FlowShell>;
}
