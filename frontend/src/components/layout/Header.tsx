import React, { useState } from "react";
import {
  Database,
  ChevronDown,
  Sun,
  Moon,
  Sparkles,
  Command,
  FileSpreadsheet,
  LineChart,
  ArrowRight,
  Shield,
  Layers,
  LayoutDashboard,
  MessageSquare
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";

export const Header: React.FC = () => {
  const {
    datasets,
    activeDatasetId,
    activeDataset,
    selectDataset,
    darkMode,
    toggleDarkMode,
    privacyMode,
    togglePrivacyMode,
    loadSampleDataset,
    activeTab,
    setActiveTab,
  } = useAppStore();

  const [showDatasetMenu, setShowDatasetMenu] = useState(false);
  const [showDemoMenu, setShowDemoMenu] = useState(false);

  const pipelineSteps = [
    { id: "ingestion", label: "Upload" },
    { id: "cleaning", label: "Clean" },
    { id: "semantic", label: "Semantic" },
    { id: "dashboard", label: "Dashboard" },
    { id: "chat", label: "Ask" },
  ];

  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 flex items-center justify-between z-10">
      {/* Left: Dataset Selector & Pipeline Steps */}
      <div className="flex items-center space-x-4">
        {/* Dataset Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowDatasetMenu(!showDatasetMenu)}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-800 dark:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-750 transition shadow-sm"
          >
            <Database className="w-3.5 h-3.5 text-indigo-500" />
            <span className="max-w-[180px] truncate">
              {activeDataset ? activeDataset.name : datasets.length > 0 ? "Select Dataset" : "No Dataset Loaded"}
            </span>
            {activeDataset && (
              <span className="text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.2 rounded font-mono">
                v{activeDataset.current_version}
              </span>
            )}
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showDatasetMenu && (
            <div className="absolute left-0 mt-1 w-64 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl py-1 z-50">
              <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Available Datasets ({datasets.length})
              </div>
              <div className="max-h-56 overflow-y-auto">
                {datasets.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => {
                      selectDataset(d.id);
                      setShowDatasetMenu(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-700 ${
                      activeDatasetId === d.id ? "bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-300 font-semibold" : "text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="truncate">{d.name}</div>
                      <div className="text-[10px] text-slate-400">{d.row_count} rows • {d.file_type.toUpperCase()}</div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">v{d.current_version}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Guided Flow Step Indicators */}
        <div className="hidden lg:flex items-center space-x-1 text-xs">
          {pipelineSteps.map((step, idx) => {
            const isCurrent = activeTab === step.id;
            return (
              <React.Fragment key={step.id}>
                {idx > 0 && <span className="text-slate-300 dark:text-slate-700">/</span>}
                <button
                  onClick={() => setActiveTab(step.id as any)}
                  className={`px-2 py-0.5 rounded transition ${
                    isCurrent
                      ? "text-indigo-600 dark:text-indigo-400 font-bold bg-indigo-50 dark:bg-indigo-950/60"
                      : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 font-medium"
                  }`}
                >
                  {step.label}
                </button>
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Right Controls: Demo Data, Privacy Mode, Theme */}
      <div className="flex items-center space-x-2.5">
        {/* Instant Demo Data Menu */}
        <div className="relative">
          <button
            onClick={() => setShowDemoMenu(!showDemoMenu)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-cyan-500 text-white text-xs font-medium hover:opacity-95 shadow-sm shadow-indigo-500/20"
          >
            <Sparkles className="w-3.5 h-3.5 fill-current" />
            <span>Load Demo Data</span>
            <ChevronDown className="w-3 h-3 opacity-80" />
          </button>

          {showDemoMenu && (
            <div className="absolute right-0 mt-1 w-64 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl p-1 z-50">
              <button
                onClick={() => {
                  loadSampleDataset("sales");
                  setShowDemoMenu(false);
                }}
                className="w-full text-left p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 flex items-start space-x-2 text-xs"
              >
                <FileSpreadsheet className="w-4 h-4 text-emerald-500 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-800 dark:text-slate-100">Messy Retail Sales (Excel)</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400">Merged cells, subtotal rows, Indian numbers, currencies.</div>
                </div>
              </button>

              <button
                onClick={() => {
                  loadSampleDataset("traffic");
                  setShowDemoMenu(false);
                }}
                className="w-full text-left p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 flex items-start space-x-2 text-xs mt-1"
              >
                <LineChart className="w-4 h-4 text-cyan-500 mt-0.5" />
                <div>
                  <div className="font-semibold text-slate-800 dark:text-slate-100">Web Traffic Time-Series</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400">Daily visitors, bounce rate, revenue, 180 days.</div>
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Command Palette Trigger */}
        <button
          onClick={() => setActiveTab("chat")}
          className="hidden md:flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-850 hover:bg-slate-100"
          title="Quick Search and Ask Dataset (Ctrl+K)"
        >
          <Command className="w-3.5 h-3.5" />
          <span className="font-mono text-[10px]">Ctrl+K</span>
        </button>

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          title="Toggle Light / Dark Theme"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </header>
  );
};
