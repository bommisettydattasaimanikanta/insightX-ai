const API_BASE = "http://localhost:8000/api";

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token") || "demo_token";
  const headers = new Headers(options.headers || {});
  
  if (!headers.has("Authorization") && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  // Only set Content-Type to application/json if not sending FormData
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (formData: FormData) => apiRequest("/auth/login", { method: "POST", body: formData }),
  getMe: () => apiRequest("/auth/me"),

  // Datasets
  getDatasets: () => apiRequest("/datasets/"),
  getDataset: (id: string) => apiRequest(`/datasets/${id}`),
  uploadDataset: (formData: FormData) => apiRequest("/datasets/upload", { method: "POST", body: formData }),
  getProfile: (id: string) => apiRequest(`/datasets/${id}/profile`),
  getVersions: (id: string) => apiRequest(`/datasets/${id}/versions`),
  editCell: (id: string, data: { row_index: number; column_name: string; new_value: any }) =>
    apiRequest(`/datasets/${id}/edit-cell`, { method: "POST", body: JSON.stringify(data) }),
  getImpact: (id: string) => apiRequest(`/datasets/${id}/impact`),
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
  getPDFUrl: (id: string) => `${API_BASE}/reports/${id}/pdf`,
  getNotebookUrl: (id: string) => `${API_BASE}/reports/${id}/notebook`,
};
