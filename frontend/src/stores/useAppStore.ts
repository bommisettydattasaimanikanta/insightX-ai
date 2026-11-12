import { create } from "zustand";
import { api } from "../api/client";

export type NavigationTab =
  | "ingestion"
  | "cleaning"
  | "semantic"
  | "dashboard"
  | "ml"
  | "insights"
  | "decision"
  | "chat"
  | "trash"
  | "settings";

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
  
  setActiveTab: (tab: NavigationTab) => void;
  setMode: (mode: "autopilot" | "review") => void;
  setViewMode: (vm: "simple" | "pro") => void;
  toggleDarkMode: () => void;
  togglePrivacyMode: () => void;
  setError: (err: string | null) => void;
  
  fetchDatasets: () => Promise<void>;
  selectDataset: (id: string) => Promise<void>;
  loadSampleDataset: (sampleType: "sales" | "traffic") => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  activeTab: "ingestion",
  datasets: [],
  activeDatasetId: null,
  activeDataset: null,
  mode: "autopilot",
  viewMode: "pro",
  darkMode: false,
  privacyMode: false,
  isLoading: false,
  error: null,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setMode: (mode) => set({ mode }),
  setViewMode: (viewMode) => set({ viewMode }),
  
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

  loadSampleDataset: async (sampleType: "sales" | "traffic") => {
    try {
      set({ isLoading: true, error: null });
      const filename = sampleType === "sales" ? "sample_data/messy_sales_data.xlsx" : "sample_data/web_traffic_timeseries.csv";
      const name = sampleType === "sales" ? "Messy Retail Sales (Demo)" : "Web Traffic Time-Series (Demo)";
      
      // In local setup, we can upload using a sample blob or trigger the ingestion API
      const res = await fetch(`/${filename}`).catch(() => null);
      let blob: Blob;
      if (res && res.ok) {
        blob = await res.blob();
      } else {
        // Fallback demo mock payload
        blob = new Blob(["Order Date,Region,Sales Amount,Quantity\n2025-01-01,North,1200,4\n2025-01-02,South,2400,6"], { type: "text/csv" });
      }

      const fd = new FormData();
      fd.append("file", blob, sampleType === "sales" ? "messy_sales_data.xlsx" : "web_traffic_timeseries.csv");
      fd.append("name", name);
      
      const created = await api.uploadDataset(fd);
      await get().fetchDatasets();
      await get().selectDataset(created.id);
      set({ activeTab: "dashboard" }); // Switch to auto dashboard immediately
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ isLoading: false });
    }
  }
}));
