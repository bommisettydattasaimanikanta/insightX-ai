import React, { useEffect } from "react";
import { useAppStore } from "./stores/useAppStore";
import { Sidebar } from "./components/layout/Sidebar";
import { Header } from "./components/layout/Header";
import { IngestionView } from "./components/views/IngestionView";
import { CleaningView } from "./components/views/CleaningView";
import { SemanticView } from "./components/views/SemanticView";
import { DashboardView } from "./components/views/DashboardView";
import { MLLabView } from "./components/views/MLLabView";
import { InsightsView } from "./components/views/InsightsView";
import { DecisionSupportView } from "./components/views/DecisionSupportView";
import { ChatView } from "./components/views/ChatView";
import { TrashView } from "./components/views/TrashView";
import { SettingsView } from "./components/views/SettingsView";

export function App() {
  const { activeTab, setActiveTab, fetchDatasets, darkMode } = useAppStore();

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  // Global Ctrl+K keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setActiveTab("chat");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setActiveTab]);

  const renderActiveView = () => {
    switch (activeTab) {
      case "ingestion":
        return <IngestionView />;
      case "cleaning":
        return <CleaningView />;
      case "semantic":
        return <SemanticView />;
      case "dashboard":
        return <DashboardView />;
      case "ml":
        return <MLLabView />;
      case "insights":
        return <InsightsView />;
      case "decision":
        return <DecisionSupportView />;
      case "chat":
        return <ChatView />;
      case "trash":
        return <TrashView />;
      case "settings":
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className={`min-h-screen flex bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans ${darkMode ? "dark" : ""}`}>
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-slate-50/50 dark:bg-slate-950/50">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
