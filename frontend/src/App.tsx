import React, { useEffect, useState } from "react";
import { useAppStore } from "./stores/useAppStore";
import { useAuthStore } from "./stores/useAuthStore";
import { Sidebar } from "./components/layout/Sidebar";
import { Header } from "./components/layout/Header";
import { LoginView } from "./components/views/LoginView";
import { DashboardView } from "./components/views/DashboardView";
import { IngestionView } from "./components/views/IngestionView";
import { AnalysisView } from "./components/views/AnalysisView";
import { PredictionsView } from "./components/views/PredictionsView";
import { InsightsView } from "./components/views/InsightsView";
import { SettingsView } from "./components/views/SettingsView";
import { Sparkles } from "lucide-react";

export function App() {
  const { activeTab, setActiveTab, fetchDatasets, darkMode } = useAppStore();
  const { isAuthenticated, checkAuth } = useAuthStore();
  const [isInitializing, setIsInitializing] = useState(true);

  // Validate session on app startup via /api/auth/me
  useEffect(() => {
    const initSession = async () => {
      try {
        const valid = await checkAuth();
        if (valid) {
          await fetchDatasets();
        }
      } finally {
        setIsInitializing(false);
      }
    };
    initSession();
  }, [checkAuth, fetchDatasets]);

  // Global Ctrl+K keyboard shortcut opens AI Insights search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setActiveTab("insights");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setActiveTab]);

  // If still verifying initial token on boot
  if (isInitializing) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#070b19] text-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-cyan-600/30 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4 animate-spin" />
          </div>
          <span className="text-sm font-medium text-slate-300">Validating InsightX session...</span>
        </div>
      </div>
    );
  }

  // Route guard: if not authenticated, redirect to Login
  if (!isAuthenticated) {
    return <LoginView />;
  }

  // Exactly 6 routes as requested
  const renderActiveView = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardView />;
      case "ingestion":
        return <IngestionView />;
      case "analysis":
        return <AnalysisView />;
      case "predictions":
        return <PredictionsView />;
      case "insights":
        return <InsightsView />;
      case "settings":
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className={`min-h-screen flex bg-[#070b19] text-slate-100 font-sans ${darkMode ? "dark" : ""}`}>
      {/* Reduced 6-item Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#070b19]">
        <Header />
        <main className="flex-1 overflow-y-auto bg-[#070b19]">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
