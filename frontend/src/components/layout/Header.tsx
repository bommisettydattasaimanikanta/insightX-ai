import React, { useState } from "react";
import {
  Database,
  ChevronDown,
  Sun,
  Moon,
  Sparkles,
  Search,
  Bell,
  RefreshCw,
  LogOut,
  Trophy,
  FileSpreadsheet,
  LineChart
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { useAuthStore } from "../../stores/useAuthStore";

export const Header: React.FC = () => {
  const {
    datasets,
    activeDatasetId,
    activeDataset,
    selectDataset,
    darkMode,
    toggleDarkMode,
    loadSampleDataset,
    reanalyzeDataset,
    setActiveTab,
  } = useAppStore();

  const { user, logout } = useAuthStore();
  const [showDatasetMenu, setShowDatasetMenu] = useState(false);
  const [showDemoMenu, setShowDemoMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setActiveTab("insights");
    }
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#070b19] px-5 flex items-center justify-between z-20 shadow-md">
      {/* Left: Dataset Switcher */}
      <div className="flex items-center space-x-3">
        <div className="relative">
          <button
            onClick={() => setShowDatasetMenu(!showDatasetMenu)}
            className="flex items-center space-x-2.5 px-3.5 py-1.5 rounded-xl border border-slate-700/80 bg-slate-900/80 text-xs font-semibold text-slate-100 hover:border-cyan-500/50 hover:bg-slate-800/80 transition shadow-sm backdrop-blur-md"
            title="Switch Dataset"
          >
            <div className="w-5 h-5 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-cyan-400">
              <Database className="w-3 h-3" />
            </div>
            <span className="max-w-[190px] truncate">
              {activeDataset ? activeDataset.name : datasets.length > 0 ? "Select Dataset" : "No Dataset"}
            </span>
            {activeDataset && (
              <span className="text-[10px] bg-cyan-950/70 border border-cyan-800/60 text-cyan-400 px-1.5 py-0.2 rounded-md font-mono">
                v{activeDataset.current_version}
              </span>
            )}
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showDatasetMenu && (
            <div className="absolute left-0 mt-2 w-72 rounded-2xl bg-[#0f172a] border border-slate-700/80 shadow-2xl py-1.5 z-50 backdrop-blur-xl animate-fadeIn">
              <div className="px-3.5 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex justify-between items-center">
                <span>Available Datasets</span>
                <span className="text-cyan-400 font-mono">{datasets.length}</span>
              </div>
              <div className="max-h-64 overflow-y-auto divide-y divide-slate-800/40">
                {datasets.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => {
                      selectDataset(d.id);
                      setShowDatasetMenu(false);
                    }}
                    className={`w-full text-left px-3.5 py-2.5 text-xs flex items-center justify-between hover:bg-slate-800/70 transition ${
                      activeDatasetId === d.id
                        ? "bg-indigo-950/60 text-cyan-400 font-semibold border-l-2 border-cyan-400"
                        : "text-slate-300"
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="truncate font-medium">{d.name}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">
                        {d.row_count?.toLocaleString()} rows • {d.file_type?.toUpperCase()}
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                      v{d.current_version}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* One-click Re-analyze */}
        {activeDatasetId && (
          <button
            onClick={() => reanalyzeDataset(activeDatasetId)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900/60 text-slate-300 text-xs font-medium hover:border-slate-700 hover:text-white transition shadow-sm"
            title="Re-run autonomous cleaning, semantic layer, and dashboard generation"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden md:inline">Re-analyze</span>
          </button>
        )}
      </div>

      {/* Center: Search Bar (Mockup Style) */}
      <form onSubmit={handleSearchSubmit} className="hidden md:flex flex-1 max-w-md mx-4">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search metrics, questions, or ask data..."
            className="w-full bg-slate-900/70 border border-slate-800/90 rounded-xl pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/40 transition shadow-inner"
          />
        </div>
      </form>

      {/* Right Controls: Demo Data, Notification Bell, Theme, Avatar */}
      <div className="flex items-center space-x-3">
        {/* Load Demo Data Menu */}
        <div className="relative">
          <button
            onClick={() => setShowDemoMenu(!showDemoMenu)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500/90 to-indigo-600/90 text-white text-xs font-semibold hover:opacity-95 shadow-md shadow-cyan-500/20 transition"
          >
            <Sparkles className="w-3.5 h-3.5 fill-current" />
            <span>Load Demo</span>
            <ChevronDown className="w-3 h-3 opacity-80" />
          </button>

          {showDemoMenu && (
            <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-[#0f172a] border border-slate-700/80 shadow-2xl p-1.5 z-50 animate-fadeIn backdrop-blur-xl">
              <button
                onClick={() => {
                  loadSampleDataset("cricket");
                  setShowDemoMenu(false);
                }}
                className="w-full text-left p-2.5 rounded-xl hover:bg-slate-800/80 flex items-start space-x-2.5 text-xs transition"
              >
                <div className="w-7 h-7 rounded-lg bg-emerald-950/70 border border-emerald-700/60 flex items-center justify-center text-emerald-400 mt-0.5 shrink-0">
                  <Trophy className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="font-semibold text-white">Cricket Match Records</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">516 matches with runs, opponent, ground, format, and totals.</div>
                </div>
              </button>

              <button
                onClick={() => {
                  loadSampleDataset("sales");
                  setShowDemoMenu(false);
                }}
                className="w-full text-left p-2.5 rounded-xl hover:bg-slate-800/80 flex items-start space-x-2.5 text-xs transition mt-1"
              >
                <div className="w-7 h-7 rounded-lg bg-indigo-950/70 border border-indigo-700/60 flex items-center justify-center text-cyan-400 mt-0.5 shrink-0">
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="font-semibold text-white">Retail Sales (Excel)</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Merged cells, subtotal rows, Indian numbers, currencies.</div>
                </div>
              </button>

              <button
                onClick={() => {
                  loadSampleDataset("traffic");
                  setShowDemoMenu(false);
                }}
                className="w-full text-left p-2.5 rounded-xl hover:bg-slate-800/80 flex items-start space-x-2.5 text-xs transition mt-1"
              >
                <div className="w-7 h-7 rounded-lg bg-cyan-950/70 border border-cyan-700/60 flex items-center justify-center text-cyan-400 mt-0.5 shrink-0">
                  <LineChart className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="font-semibold text-white">Web Traffic Time-Series</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Daily visitors, bounce rate, revenue, 180 days.</div>
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Notification Bell */}
        <button
          className="relative p-2 rounded-xl border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60 transition"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400 animate-pulse" />
        </button>

        {/* Theme Mode Toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-xl border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60 transition"
          title="Toggle Light / Dark Mode"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-400" />}
        </button>

        {/* User Avatar & Logout */}
        {user && (
          <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 border border-slate-700 flex items-center justify-center text-xs text-white font-bold shadow-md">
              {user.full_name ? user.full_name.substring(0, 2).toUpperCase() : "LA"}
            </div>
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-semibold text-slate-200 leading-tight">{user.full_name || "Lead Analyst"}</span>
              <span className="text-[10px] text-slate-400 leading-tight">{user.role || "Lead Analyst"}</span>
            </div>
            <button
              onClick={() => logout("You have logged out successfully.")}
              className="p-1.5 rounded-lg border border-slate-800 text-slate-400 hover:bg-rose-950/40 hover:text-rose-400 transition ml-1"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
