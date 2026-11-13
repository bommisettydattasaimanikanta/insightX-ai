import { create } from "zustand";
import { api } from "../api/client";

export type NavigationTab =
  | "dashboard"
  | "ingestion"
  | "analysis"
  | "predictions"
  | "insights"
  | "settings";

interface PipelineProgress {
  jobId?: string;
  progressPct: number;
  message: string;
  status: "idle" | "running" | "completed" | "failed";
  step?: string;
  kpiCards?: any[];
}

interface AppState {
  activeTab: NavigationTab;
  datasets: any[];
  activeDatasetId: string | null;
  activeDataset: any | null;
  mode: "autopilot" | "review";
  viewMode: "simple" | "pro";
  darkMode: boolean;
  privacyMode: boolean;
  isLoading: boolean;
  error: string | null;
  pipelineProgress: PipelineProgress | null;
  pinnedQueries: any[];
  
  setActiveTab: (tab: NavigationTab) => void;
  setMode: (mode: "autopilot" | "review") => void;
  setViewMode: (vm: "simple" | "pro") => void;
  toggleDarkMode: () => void;
  togglePrivacyMode: () => void;
  setError: (err: string | null) => void;
  setPipelineProgress: (prog: PipelineProgress | null) => void;
  pinQueryToDashboard: (queryResult: any) => void;
  
  fetchDatasets: () => Promise<void>;
  selectDataset: (id: string) => Promise<void>;
  loadSampleDataset: (sampleType: "cricket" | "sales" | "traffic") => Promise<void>;
  reanalyzeDataset: (id: string) => Promise<void>;
  undoClean: (id: string) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  activeTab: "dashboard",
  datasets: [],
  activeDatasetId: null,
  activeDataset: null,
  mode: "autopilot",
  viewMode: "simple",
  darkMode: true, // Mockup style: dark navy default
  privacyMode: false,
  isLoading: false,
  error: null,
  pipelineProgress: null,
  pinnedQueries: [],

  setActiveTab: (tab) => set({ activeTab: tab }),
  setMode: (mode) => set({ mode }),
  setViewMode: (viewMode) => set({ viewMode }),
  setPipelineProgress: (pipelineProgress) => set({ pipelineProgress }),
  pinQueryToDashboard: (queryResult) => set((state) => ({ pinnedQueries: [queryResult, ...state.pinnedQueries] })),
  
  toggleDarkMode: () => {
    const next = !get().darkMode;
    set({ darkMode: next });
    if (next) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  },

  togglePrivacyMode: () => set((state) => ({ privacyMode: !state.privacyMode })),
  setError: (error) => set({ error }),

  fetchDatasets: async () => {
    try {
      set({ isLoading: true, error: null });
      const data = await api.getDatasets();
      set({ datasets: data });
      if (data.length > 0 && !get().activeDatasetId) {
        await get().selectDataset(data[0].id);
      }
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ isLoading: false });
    }
  },

  selectDataset: async (id: string) => {
    try {
      set({ isLoading: true, activeDatasetId: id, error: null });
      const dataset = await api.getDataset(id);
      set({ activeDataset: dataset });
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ isLoading: false });
    }
  },

  loadSampleDataset: async (sampleType: "cricket" | "sales" | "traffic") => {
    try {
      set({
        isLoading: true,
        error: null,
        pipelineProgress: {
          progressPct: 20,
          message: "Ingesting sample dataset into columnar storage...",
          status: "running"
        }
      });

      const created = await api.loadDemoDataset(sampleType);

      set({
        pipelineProgress: {
          progressPct: 60,
          message: "Auto-cleaning dates, numbers, whitespace, and subtotal rows...",
          status: "running"
        }
      });

      await get().fetchDatasets();
      await get().selectDataset(created.id);

      set({
        pipelineProgress: {
          progressPct: 100,
          message: "Done! Opening your executive dashboard...",
          status: "completed"
        }
      });

      setTimeout(() => {
        set({ pipelineProgress: null, activeTab: "dashboard" });
      }, 500);
    } catch (e: any) {
      set({ error: e.message, pipelineProgress: null });
    } finally {
      set({ isLoading: false });
    }
  },

  reanalyzeDataset: async (id: string) => {
    try {
      set({
        isLoading: true,
        error: null,
        pipelineProgress: {
          progressPct: 25,
          message: "Re-analyzing dataset and rebuilding semantic models...",
          status: "running"
        }
      });

      await api.reanalyze(id);

      set({
        pipelineProgress: {
          progressPct: 100,
          message: "Re-analysis complete! Updating dashboard...",
          status: "completed"
        }
      });

      await get().fetchDatasets();
      await get().selectDataset(id);

      setTimeout(() => {
        set({ pipelineProgress: null, activeTab: "dashboard" });
      }, 600);
    } catch (e: any) {
      set({ error: e.message, pipelineProgress: null });
    } finally {
      set({ isLoading: false });
    }
  },

  undoClean: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      await api.undoClean(id);
      await get().fetchDatasets();
      await get().selectDataset(id);
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ isLoading: false });
    }
  }
}));
