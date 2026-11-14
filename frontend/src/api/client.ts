import { useAuthStore } from "../stores/useAuthStore";

const API_BASE = "/api";

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  // Read token from Zustand auth store or localStorage fallback
  const token = useAuthStore.getState().token || localStorage.getItem("token");
  const headers = new Headers(options.headers || {});

  // Attach Authorization header if token exists and not already set
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // Handle FormData: NEVER set Content-Type header manually for FormData (the browser auto-sets multipart/form-data with boundary)
  if (options.body instanceof FormData) {
    if (headers.has("Content-Type")) {
      headers.delete("Content-Type");
    }
  } else if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Intercept 401 Unauthorized responses
  if (response.status === 401) {
    // Only trigger session expiration logout if this isn't the login endpoint itself
    if (!endpoint.includes("/auth/login")) {
      useAuthStore.getState().logout("Session expired, please log in again");
    }
    const errorData = await response.json().catch(() => ({ detail: "Session expired, please log in again" }));
    throw new Error(errorData.detail || "Session expired, please log in again");
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (formData: FormData | URLSearchParams) =>
    apiRequest("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    }),
  register: (data: { email: string; password: string; full_name?: string }) =>
    apiRequest("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  getMe: () => apiRequest("/auth/me"),

  // Datasets
  getDatasets: () => apiRequest("/datasets/"),
  getDataset: (id: string) => apiRequest(`/datasets/${id}`),
  uploadDataset: (formData: FormData) => apiRequest("/datasets/upload", { method: "POST", body: formData }),
  loadDemoDataset: (sampleType: "cricket" | "sales" | "traffic") => apiRequest(`/datasets/demo/${sampleType}`, { method: "POST" }),
  getProfile: (id: string) => apiRequest(`/datasets/${id}/profile`),
  getVersions: (id: string) => apiRequest(`/datasets/${id}/versions`),
  editCell: (id: string, data: { row_index: number; column_name: string; new_value: any }) =>
    apiRequest(`/datasets/${id}/edit-cell`, { method: "POST", body: JSON.stringify(data) }),
  getImpact: (id: string) => apiRequest(`/datasets/${id}/impact`),
  reanalyze: (id: string) => apiRequest(`/datasets/${id}/reanalyze`, { method: "POST" }),
  undoClean: (id: string) => apiRequest(`/datasets/${id}/undo-clean`, { method: "POST" }),
  moveToTrash: (id: string) => apiRequest(`/datasets/${id}/trash`, { method: "DELETE" }),
  restoreDataset: (id: string) => apiRequest(`/datasets/${id}/restore`, { method: "POST" }),
  permanentDelete: (id: string, confirmation_name: string) =>
    apiRequest(`/datasets/${id}/permanent`, { method: "POST", body: JSON.stringify({ confirmation_name }) }),

  // Cleaning
  getCleaningPlan: (id: string) => apiRequest(`/clean/${id}/plan`),
  applyCleaning: (id: string, approved_steps: any[]) =>
    apiRequest(`/clean/${id}/apply`, { method: "POST", body: JSON.stringify({ approved_steps }) }),

  // Semantic
  getSemanticLayer: (id: string) => apiRequest(`/semantic/${id}`),
  updateSemanticLayer: (id: string, data: any) =>
    apiRequest(`/semantic/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  // Statistics
  getCorrelations: (id: string) => apiRequest(`/stats/${id}/correlations`),
  getHypothesis: (id: string) => apiRequest(`/stats/${id}/hypothesis`),
  getTrends: (id: string, time_col: string, metric_col: string) =>
    apiRequest(`/stats/${id}/trends?time_col=${encodeURIComponent(time_col)}&metric_col=${encodeURIComponent(metric_col)}`),

  // Dashboards
  getDashboard: (id: string) => apiRequest(`/dashboards/${id}`),
  updateDashboard: (id: string, spec: any) =>
    apiRequest(`/dashboards/${id}`, { method: "PUT", body: JSON.stringify({ spec }) }),

  // ML
  trainModel: (id: string, target_column: string) =>
    apiRequest(`/ml/${id}/train`, { method: "POST", body: JSON.stringify({ target_column }) }),
  runForecast: (id: string, time_column: string, metric_column: string, horizon: number = 30) =>
    apiRequest(`/ml/${id}/forecast`, { method: "POST", body: JSON.stringify({ time_column, metric_column, horizon }) }),
  simulateWhatIf: (id: string, model_name: string, base_features: any, feature_tweaks: any) =>
    apiRequest(`/ml/${id}/what-if`, { method: "POST", body: JSON.stringify({ model_name, base_features, feature_tweaks }) }),
  getTornado: (id: string, model_name: string) =>
    apiRequest(`/ml/${id}/tornado?model_name=${encodeURIComponent(model_name)}`, { method: "POST" }),
  goalSeek: (id: string, data: any) =>
    apiRequest(`/ml/${id}/goal-seek`, { method: "POST", body: JSON.stringify(data) }),

  // Insights
  getInsights: (id: string) => apiRequest(`/insights/${id}`),
  getRecommendations: (id: string) => apiRequest(`/insights/${id}/recommendations`),
  updateRecommendationStatus: (id: string, recId: string, status: string) =>
    apiRequest(`/insights/${id}/recommendations/${recId}`, { method: "PATCH", body: JSON.stringify({ status }) }),

  // Chat
  chatQuery: (id: string, question: string, history: any[] = [], privacy_mode: boolean = false) =>
    apiRequest(`/chat/${id}/query`, {
      method: "POST",
      body: JSON.stringify({ question, history, privacy_mode }),
    }),

  // Trash
  getTrash: () => apiRequest("/trash/"),

  // Exports
  getPDFUrl: (id: string) => `${API_BASE}/dashboards/${id}/export/pdf`,
  getNotebookUrl: (id: string) => `${API_BASE}/reports/${id}/notebook`,
  downloadExport: async (datasetId: string, format: "pdf" | "png" | "pptx" | "excel" | "csv", filename?: string) => {
    const token = useAuthStore.getState().token || localStorage.getItem("token");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/dashboards/${datasetId}/export/${format}`, { headers });
    if (!res.ok) throw new Error(`Export failed with status ${res.status}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || `dashboard_${datasetId}.${format === "excel" ? "xlsx" : format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
};
