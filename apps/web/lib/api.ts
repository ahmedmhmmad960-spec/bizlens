export type EvidenceItem = {
  label?: string;
  value?: string | number;
  direction?: string;
  source?: string;
  trust?: string;
  [key: string]: unknown;
};

export type Diagnosis = {
  id?: string;
  code?: string;
  diagnosis: string;
  title?: string;
  description?: string;
  severity?: string;
  priority?: number;
  confidence?: string;
  confidence_score?: number;
  limitations?: string[];
  evidence?: Record<string, unknown>;
  impact?: Record<string, unknown>;
  action?: Record<string, unknown>;
  [key: string]: unknown;
};

export type ReplayStep = {
  step?: number;
  key?: string;
  title?: string;
  description?: string;
  data?: unknown;
};

export type AnalysisResponse = {
  success: boolean;
  analysis_id: string;
  analysis: Record<string, unknown>;
  diagnoses: Diagnosis[];
  top_diagnoses: Diagnosis[];
  diagnosis_chains: Record<string, unknown>[];
  evidence: Record<string, unknown>[];
  what_changed: Record<string, unknown>[];
  ai_explanations: Record<string, unknown>[];
  business_report: Record<string, unknown>;
  demo_replay: {
    title?: string;
    description?: string;
    total_steps?: number;
    steps?: ReplayStep[];
  };
};

async function parseResponse(response: Response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(payload?.error || `Request failed with status ${response.status}`);
  }
  if (!payload?.success) {
    throw new Error(payload?.error || "BizLens could not analyze this file.");
  }
  return payload;
}

export async function analyzeCsv(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/analyze", {
    method: "POST",
    body: formData,
  });

  return parseResponse(response) as Promise<AnalysisResponse>;
}

export async function askBizLens(analysisId: string, question: string) {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, question }),
  });

  return parseResponse(response) as Promise<{
    success: true;
    analysis_id: string;
    question: string;
    answer: unknown;
  }>;
}
