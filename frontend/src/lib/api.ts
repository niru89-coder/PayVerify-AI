/**
 * Typed API client for the PayVerify AI FastAPI backend.
 * All requests go to NEXT_PUBLIC_API_BASE_URL (defaults to http://localhost:8000).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface Project {
  id: number;
  name: string;
  country: string;
  pay_period_year: number;
  pay_period_month: number;
  created_at: string;
}

export interface MappingSuggestion {
  source_column: string;
  canonical_code: string | null;
  confidence: number;
  method: "exact" | "fuzzy" | "unmapped";
}

export interface MappingPreview {
  suggestions: MappingSuggestion[];
  auto_accepted_column_map: Record<string, string>;
  needs_review: MappingSuggestion[];
}

export interface RegisterUploadResult {
  register_id: number;
  register_type: string;
  row_count: number;
  employees_created: number;
  employees_matched: number;
}

export interface ValidationRunResult {
  project_id: number;
  variances_created: number;
  classification_summary: Record<string, number>;
}

export interface Variance {
  id: number;
  project_id: number;
  employee_id: number;
  component_code: string;
  client_value: number | null;
  platform_value: number | null;
  expected_value: number | null;
  rule_id: string | null;
  classification: string;
  suggestion_outcome: string;
  recommended_action: string;
  explanation: string;
  confidence_score: number;
  ai_explanation: string | null;
  resolution_status: string;
  created_at: string;
}

export interface RuleSummary {
  rule_id: string;
  component: string;
  country: string;
  status: string;
  version: string;
  effective_date: string;
  source_document: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore parse errors, fall back to statusText
    }
    throw new Error(`API error ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listProjects: () => request<Project[]>("/api/projects"),
  getProject: (id: number) => request<Project>(`/api/projects/${id}`),
  createProject: (payload: { name: string; country: string; pay_period_year: number; pay_period_month: number }) =>
    request<Project>("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  uploadEmployeeMaster: (projectId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ rows_processed: number; employees_created: number }>(
      `/api/projects/${projectId}/employees/upload`,
      { method: "POST", body: form }
    );
  },

  previewRegisterMapping: (projectId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<MappingPreview>(`/api/projects/${projectId}/registers/preview-mapping`, {
      method: "POST",
      body: form,
    });
  },

  uploadRegister: (
    projectId: number,
    registerType: "client" | "platform",
    file: File,
    columnMap?: Record<string, string>
  ) => {
    const form = new FormData();
    form.append("file", file);
    if (columnMap) form.append("column_map", JSON.stringify(columnMap));
    const params = new URLSearchParams({ register_type: registerType });
    return request<RegisterUploadResult>(`/api/projects/${projectId}/registers/upload?${params}`, {
      method: "POST",
      body: form,
    });
  },

  runValidation: (projectId: number) =>
    request<ValidationRunResult>(`/api/projects/${projectId}/validate`, { method: "POST" }),

  listVariances: (projectId: number, filters?: { classification?: string; resolution_status?: string }) => {
    const params = new URLSearchParams();
    if (filters?.classification) params.set("classification", filters.classification);
    if (filters?.resolution_status) params.set("resolution_status", filters.resolution_status);
    const qs = params.toString();
    return request<Variance[]>(`/api/projects/${projectId}/variances${qs ? `?${qs}` : ""}`);
  },

  getVariance: (varianceId: number) => request<Variance>(`/api/variances/${varianceId}`),

  explainVariance: (varianceId: number) =>
    request<Variance>(`/api/variances/${varianceId}/explain`, { method: "POST" }),

  submitFeedback: (
    varianceId: number,
    payload: { action: "confirmed" | "rejected" | "needs_correction"; consultant: string; notes: string }
  ) =>
    request<{ id: number }>(`/api/variances/${varianceId}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  listRules: () => request<RuleSummary[]>("/api/rules"),
};
