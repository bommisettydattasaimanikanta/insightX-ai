import React from "react";
import {
  Database,
  Sparkles,
  Layers,
  LayoutDashboard,
  Cpu,
  TrendingUp,
  Sliders,
  MessageSquare,
  Trash2,
  Settings,
  ShieldCheck,
  Zap,
  Eye,
  SlidersHorizontal,
} from "lucide-react";
import { useAppStore, type NavigationTab } from "../../stores/useAppStore";

export const Sidebar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    mode,
    setMode,
    viewMode,
    setViewMode,
    privacyMode,
  } = useAppStore();

  const navItems: { id: NavigationTab; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: "ingestion", label: "Data Ingestion", icon: <Database className="w-4 h-4" /> },
    { id: "cleaning", label: "Cleaning Studio", icon: <Sparkles className="w-4 h-4" />, badge: "Reversible" },
    { id: "semantic", label: "Semantic Layer", icon: <Layers className="w-4 h-4" />, badge: "Unified" },
    { id: "dashboard", label: "Auto Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: "ml", label: "ML Lab & Forecast", icon: <Cpu className="w-4 h-4" /> },
    { id: "insights", label: "Ranked Insights", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "decision", label: "Decision Support", icon: <Sliders className="w-4 h-4" /> },
    { id: "chat", label: "Safe Agent Chat", icon: <MessageSquare className="w-4 h-4" /> },
    { id: "trash", label: "Trash & Versions", icon: <Trash2 className="w-4 h-4" /> },
    { id: "settings", label: "Settings & Security", icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 font-bold">
            <Zap className="w-5 h-5 fill-current" />
          </div>
          <div>
            <span className="font-bold text-white tracking-tight text-base block leading-tight">InsightForge AI</span>
            <span className="text-[10px] text-cyan-400 font-mono tracking-wider uppercase font-semibold">Autonomous v2.0</span>
          </div>
        </div>
      </div>

      {/* Control Modes (Autopilot vs Review, Simple vs Pro) */}
      <div className="p-3 border-b border-slate-800 space-y-2 bg-slate-950/40">
        <div className="flex items-center justify-between text-xs px-1">
          <span className="text-slate-400 flex items-center gap-1">
            <SlidersHorizontal className="w-3.5 h-3.5" /> Pipeline Mode
          </span>
          <div className="flex bg-slate-800 rounded p-0.5 text-[11px] font-medium">
            <button
              onClick={() => setMode("autopilot")}
              className={`px-2 py-0.5 rounded transition ${
                mode === "autopilot" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
              }`}
            >
              Autopilot
            </button>
            <button
              onClick={() => setMode("review")}
              className={`px-2 py-0.5 rounded transition ${
                mode === "review" ? "bg-amber-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
              }`}
            >
              Review
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs px-1">
          <span className="text-slate-400 flex items-center gap-1">
            <Eye className="w-3.5 h-3.5" /> View Level
          </span>
          <div className="flex bg-slate-800 rounded p-0.5 text-[11px] font-medium">
            <button
              onClick={() => setViewMode("simple")}
              className={`px-2 py-0.5 rounded transition ${
                viewMode === "simple" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
              }`}
            >
              Simple
            </button>
            <button
              onClick={() => setViewMode("pro")}
              className={`px-2 py-0.5 rounded transition ${
                viewMode === "pro" ? "bg-cyan-600 text-white" : "text-slate-400 hover:text-white"
              }`}
            >
              Pro
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                isActive
                  ? "bg-indigo-600 text-white shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center space-x-2.5">
                {item.icon}
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                    isActive ? "bg-indigo-700 text-indigo-100" : "bg-slate-800 text-cyan-400 border border-slate-700"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Privacy Mode & Workspace Badge */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/50">
        {privacyMode && (
          <div className="mb-2 bg-emerald-950/60 border border-emerald-800/80 rounded px-2.5 py-1 flex items-center gap-1.5 text-[11px] text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
            <span>Privacy Mode: PII Masked</span>
          </div>
        )}
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs text-white font-semibold">
            LA
          </div>
          <div className="flex-1 truncate">
            <div className="text-xs font-medium text-white truncate">Lead Analyst</div>
            <div className="text-[10px] text-slate-500 truncate">Default Workspace (Owner)</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
