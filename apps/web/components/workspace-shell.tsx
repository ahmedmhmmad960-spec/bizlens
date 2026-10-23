"use client";

import { useState, type ReactNode } from "react";
import {
  ArrowLeftRight, ArrowUpRight, FileText, LayoutDashboard,
  ListChecks, Menu, MessageSquare, X,
} from "lucide-react";

export type WorkspaceView = "overview" | "feed" | "changes" | "ask" | "report";

const navigation = [
  { view: "overview", label: "Overview", Icon: LayoutDashboard },
  { view: "feed", label: "Diagnoses", Icon: ListChecks },
  { view: "changes", label: "What Changed", Icon: ArrowLeftRight },
  { view: "ask", label: "Ask BizLens", Icon: MessageSquare },
  { view: "report", label: "Report", Icon: FileText },
] as const;

type Props = {
  active: WorkspaceView;
  orderCount: unknown;
  sample: boolean;
  onNavigate: (view: WorkspaceView) => void;
  onExit: () => void;
  children: ReactNode;
};

export default function WorkspaceShell({
  active, orderCount, sample, onNavigate, onExit, children,
}: Props) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const orders = typeof orderCount === "number" && Number.isFinite(orderCount)
    ? orderCount.toLocaleString("en-US")
    : "—";
  const current = navigation.find((item) => item.view === active);

  function navigate(view: WorkspaceView) {
    setMobileOpen(false);
    onNavigate(view);
  }

  return (
    <div className="workspace-layout">
      {mobileOpen ? (
        <button className="workspace-scrim" type="button" onClick={() => setMobileOpen(false)}
          aria-label="Close workspace navigation" />
      ) : null}
      <aside className={`workspace-sidebar${mobileOpen ? " workspace-sidebar-open" : ""}`}
        aria-label="Workspace navigation">
        <div className="workspace-brand">
          <span className="workspace-brand-mark" aria-hidden="true"><i /></span>
          <span>BizLens</span>
          <button className="workspace-close" type="button"
            aria-label="Close navigation" onClick={() => setMobileOpen(false)}><X size={19}/></button>
        </div>
        <div className="workspace-dataset">
          <div className="workspace-dataset-mark" aria-hidden="true">B</div>
          <div><strong>{sample ? "Demo dataset" : "Your business data"}</strong>
            <span>{sample ? "Illustrative CSV" : "Uploaded CSV"} · {orders} orders</span></div>
        </div>
        <div className="workspace-nav-label">WORKSPACE</div>
        <nav className="workspace-navigation" aria-label="Business analysis sections">
          {navigation.map(({ view, label, Icon }) => (
            <button key={view} type="button"
              className={`workspace-nav-link${active === view ? " workspace-nav-active" : ""}`}
              aria-current={active === view ? "page" : undefined}
              onClick={() => navigate(view)}>
              <Icon size={17} aria-hidden="true" /><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="workspace-sidebar-footer">
          <div className="workspace-status"><span className="workspace-online-dot" />
            Analysis available</div>
          <span className="workspace-order-note">{orders} orders · data-backed results</span>
          <button type="button" onClick={onExit}>← Landing</button>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="workspace-topbar">
          <div className="workspace-topbar-left">
            <button className="workspace-mobile-toggle" type="button"
              aria-label="Open workspace navigation" aria-expanded={mobileOpen}
              onClick={() => setMobileOpen(true)}><Menu size={21}/></button>
            <span className="workspace-breadcrumb">{sample ? "Demo dataset" : "Your data"}</span>
            <span className="workspace-breadcrumb-chevron" aria-hidden="true">›</span>
            <strong>{current?.label}</strong>
          </div>
          <div className="workspace-topbar-right">
            {sample ? <span className="workspace-illustrative">◆ Demo dataset</span>
              : <span className="workspace-source">Uploaded CSV</span>}
            {active !== "report" ? (
              <button type="button" className="workspace-report-link"
                onClick={() => navigate("report")}>View report <ArrowUpRight size={15} /></button>
            ) : null}
          </div>
        </header>
        <div className="workspace-screen">{children}</div>
      </div>
    </div>
  );
}
