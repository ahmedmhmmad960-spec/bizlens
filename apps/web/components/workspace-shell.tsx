"use client";

import type { ReactNode } from "react";
import {
  ArrowLeft,
  ArrowRightLeft,
  ChartNoAxesCombined,
  CircleHelp,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Plus,
} from "lucide-react";
import type { AnalysisResponse } from "@/lib/api";

export type WorkspaceView = "overview" | "feed" | "changes" | "ask" | "report";

const navigation = [
  { view: "overview", label: "Overview", Icon: LayoutDashboard },
  { view: "feed", label: "Diagnoses", Icon: ClipboardList },
  { view: "changes", label: "What Changed", Icon: ArrowRightLeft },
  { view: "ask", label: "Ask BizLens", Icon: CircleHelp },
  { view: "report", label: "Report", Icon: FileText },
] as const;

type Props = {
  active: WorkspaceView;
  analysis: AnalysisResponse;
  onNavigate: (view: WorkspaceView) => void;
  onNewAnalysis: () => void;
  onLanding: () => void;
  children: ReactNode;
};

/** Figma journey and approved dashboard share one persistent workspace. */
export default function WorkspaceShell({
  active,
  analysis,
  onNavigate,
  onNewAnalysis,
  onLanding,
  children,
}: Props) {
  const currentLabel = navigation.find((item) => item.view === active)?.label ?? "Overview";
  const diagnosisCount = analysis.diagnoses?.length ?? 0;
  const quality = analysis.analysis?.data_quality as Record<string, unknown> | undefined;
  const currency = quality?.currency === "unspecified" ? "Currency unspecified" : "Source currency unverified";

  return (
    <div className="workspace-frame">
      <aside className="workspace-sidebar" aria-label="BizLens workspace">
        <div className="workspace-brand">
          <span className="workspace-brand-symbol" aria-hidden="true"><span /></span>
          <span>BizLens</span>
        </div>

        <div className="workspace-session">
          <span className="workspace-session-symbol" aria-hidden="true">B</span>
          <span>
            <strong>Current analysis</strong>
            <small>Imported sales data</small>
          </span>
        </div>

        <nav className="workspace-nav" aria-label="Workspace sections">
          <div className="workspace-nav-heading">Workspace</div>
          {navigation.map(({ view, label, Icon }) => (
            <button
              type="button"
              key={view}
              className={`workspace-nav-item ${active === view ? "is-active" : ""}`}
              aria-current={active === view ? "page" : undefined}
              onClick={() => onNavigate(view)}
            >
              <Icon size={16} strokeWidth={1.8} aria-hidden="true" />
              <span>{label}</span>
              {view === "feed" && diagnosisCount > 0 ? (
                <span className="workspace-nav-count">{diagnosisCount}</span>
              ) : null}
            </button>
          ))}
        </nav>

        <div className="workspace-sidebar-footer">
          <div className="workspace-data-state">
            <span className="workspace-state-dot" aria-hidden="true" />
            <strong>Analysis ready</strong>
            <small>{currency}</small>
          </div>
          <button type="button" className="workspace-footer-link" onClick={onNewAnalysis}>
            <Plus size={15} aria-hidden="true" /> New diagnosis
          </button>
          <button type="button" className="workspace-footer-link" onClick={onLanding}>
            <ArrowLeft size={15} aria-hidden="true" /> Landing
          </button>
        </div>
      </aside>

      <div className="workspace-main">
        <header className="workspace-topbar">
          <div className="workspace-breadcrumb">
            <span>Current analysis</span>
            <span aria-hidden="true">›</span>
            <strong>{currentLabel}</strong>
          </div>
          <div className="workspace-topbar-trust">
            <ChartNoAxesCombined size={14} aria-hidden="true" />
            Evidence-backed analysis
          </div>
        </header>
        <div className="workspace-content">{children}</div>
      </div>
    </div>
  );
}
