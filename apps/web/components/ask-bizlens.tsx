"use client";

import { useState } from "react";
import { askBizLens, type AnalysisResponse } from "@/lib/api";

type Props = { analysis: AnalysisResponse; onBack: () => void; onContinue: () => void };

function answerText(answer: unknown) {
  if (typeof answer === "string") return answer;
  if (answer && typeof answer === "object") {
    const data = answer as Record<string, unknown>;
    return String(data.answer ?? JSON.stringify(answer));
  }
  return "BizLens could not produce an answer from the available evidence.";
}

export default function AskBizLens({ analysis, onBack, onContinue }: Props) {
  const [question, setQuestion] = useState("Why did profit decline even though revenue increased?");
  const [answer, setAnswer] = useState<string | null>(null);
  const [evidence, setEvidence] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    if (!question.trim()) return;
    setLoading(true); setError(null);
    try {
      const result = await askBizLens(analysis.analysis_id, question.trim());
      setAnswer(answerText(result.answer));
      const raw = result.answer && typeof result.answer === "object" ? (result.answer as Record<string, unknown>).evidence : null;
      setEvidence(Array.isArray(raw) ? raw.map(String) : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to answer this question.");
    } finally { setLoading(false); }
  }

  return <main className="insight-page ask-page">
    <header className="flow-header"><div className="logo"><span className="logo-mark"><span /></span><span>BizLens</span></div><span className="flow-label">Ask BizLens</span></header>
    <div className="insight-content">
      <button className="flow-back" onClick={onBack}>← Back</button>
      <span className="flow-kicker">Grounded questions</span>
      <h1>Ask about the business.</h1>
      <p className="insight-intro">Answers are grounded in the analysis already performed. If the data cannot support an answer, BizLens says so.</p>
      <section className="ask-box"><label htmlFor="bizlens-question">Your question</label><textarea id="bizlens-question" value={question} onChange={(e) => setQuestion(e.target.value)} rows={3} /><button className="button primary" onClick={ask} disabled={loading}>{loading ? "Thinking…" : "Ask BizLens"} <span>→</span></button></section>
      {error && <div className="ask-error">{error}</div>}
      {answer && <section className="answer-card"><span className="flow-kicker">Evidence-backed answer</span><h2>{answer}</h2>{evidence.length ? <div className="answer-evidence">{evidence.map((item, index) => <div key={`${item}-${index}"><span>Evidence</span><strong>{item}</strong></div>)}</div> : null}</section>}
      <div className="insight-actions"><button className="button secondary" onClick={onBack}>Back</button><button className="button primary" onClick={onContinue}>Business report <span>→</span></button></div>
    </div>
  </main>;
}
