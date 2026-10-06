"use client";

import { useState, type ReactNode } from "react";

type IconName = "arrow" | "github";

function Icon({ name, size = 16 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    github: <><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3.3-.4 6.8-1.6 6.8-7A5.4 5.4 0 0 0 19.3 4 5 5 0 0 0 19.1.5S18 0 15 2a13.4 13.4 0 0 0-7 0C5 .1 3.9.5 3.9.5A5 5 0 0 0 3.7 4a5.4 5.4 0 0 0-1.5 3.7c0 5.4 3.5 6.6 6.8 7A4.8 4.8 0 0 0 8 18v4" /><path d="M8 19c-3 .9-3-1.5-4.2-2" /></>,
  };

  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function Logo() {
  return <div className="logo"><span className="logo-mark" aria-hidden="true"><span /></span><span>BizLens</span></div>;
}

function Button({ children, variant = "primary", icon, onClick }: { children: ReactNode; variant?: "primary" | "secondary"; icon?: IconName; onClick?: () => void }) {
  return <button className={`button ${variant}`} onClick={onClick} type="button">{children}{icon ? <Icon name={icon} size={16} /> : null}</button>;
}

function Badge({ children }: { children: ReactNode }) {
  return <span className="badge high">{children}</span>;
}

function MetricMini({ label, value, tone }: { label: string; value: string; tone: "positive" | "critical" }) {
  return <div className="metric-mini"><span>{label}</span><strong className={tone}>{value}</strong></div>;
}

export default function EntryScreen() {
  const [message, setMessage] = useState<string | null>(null);

  return (
    <div className="page landing">
      <header className="topbar">
        <button className="logo-button" type="button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} aria-label="BizLens home"><Logo /></button>
        <nav className="public-nav" aria-label="Public navigation">
          <button type="button" onClick={() => setMessage("Docs are coming with the first public release.")}>Docs</button>
          <button type="button" onClick={() => window.open("https://github.com/ahmedmhmmad960-spec/bizlens", "_blank", "noopener,noreferrer")}><Icon name="github" size={16} />GitHub</button>
        </nav>
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="eyebrow"><span className="eyebrow-dot" />Evidence-backed business intelligence</div>
          <h1 id="hero-title">See your business<br /><span>clearly.</span></h1>
          <p>Turn business data into clear decisions.</p>
          <div className="hero-actions">
            <Button icon="arrow" onClick={() => setMessage("The diagnosis flow is the next screen we are implementing.")}>Start a Diagnosis</Button>
            <Button variant="secondary" onClick={() => document.getElementById("example-diagnosis")?.scrollIntoView({ behavior: "smooth" })}>Try Demo</Button>
          </div>
          <div className="philosophy" aria-label="BizLens product philosophy"><span>Business data</span><i /><span>Intelligence</span><i /><span>Clear decisions</span></div>
        </section>

        <section className="preview-wrap" id="example-diagnosis" aria-labelledby="example-title">
          <div className="preview-label"><span>Example diagnosis</span><Badge>High confidence</Badge></div>
          <div className="preview-card">
            <div className="preview-head">
              <div><span className="category">Profitability</span><h2 id="example-title">Revenue increased, but profit declined</h2></div>
              <div className="signal-mark" aria-hidden="true">B</div>
            </div>
            <div className="preview-metrics">
              <MetricMini label="Revenue" value="+51.6%" tone="positive" />
              <MetricMini label="Costs" value="+276.7%" tone="critical" />
              <MetricMini label="Gross Margin" value="−87.4 pts" tone="critical" />
            </div>
            <button className="why-button" type="button" onClick={() => setMessage("The full evidence view will be connected after the core setup flow.")}>Why did this happen?<Icon name="arrow" size={15} /></button>
          </div>
        </section>

        <section className="method-strip" aria-labelledby="method-title">
          <div><span className="section-kicker">Built for trust</span><h2 id="method-title">Analysis first. AI second.</h2></div>
          <p>BizLens does not ask AI to guess what is happening. Its diagnosis engine finds and verifies business signals before AI explains them.</p>
          <button type="button" onClick={() => setMessage("Methodology is part of the next implementation pass.")}>Explore the methodology <Icon name="arrow" size={15} /></button>
        </section>
      </main>

      <footer><Logo /><span>Open-source business diagnosis.</span><span>© 2026 BizLens</span></footer>

      {message ? <div className="entry-toast" role="status"><span>{message}</span><button type="button" onClick={() => setMessage(null)} aria-label="Close message">×</button></div> : null}
    </div>
  );
}
