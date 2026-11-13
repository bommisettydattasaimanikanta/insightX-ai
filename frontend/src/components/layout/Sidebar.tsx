import React from "react";
import {
  LayoutDashboard,
  UploadCloud,
  BarChart3,
  TrendingUp,
  Sparkles,
  Settings,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { useAppStore, type NavigationTab } from "../../stores/useAppStore";

export const Sidebar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    privacyMode,
  } = useAppStore();

  // Exactly the 6 requested sidebar navigation items
  const navItems: { id: NavigationTab; label: string; icon: React.ReactNode }[] = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: "ingestion", label: "Data Upload", icon: <UploadCloud className="w-4 h-4" /> },
    { id: "analysis", label: "Analysis", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "predictions", label: "Predictions", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "insights", label: "AI Insights", icon: <Sparkles className="w-4 h-4" /> },
    { id: "settings", label: "Settings", icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-60 bg-[#070b19] border-r border-slate-800/80 text-slate-300 flex flex-col h-screen select-none shrink-0 shadow-2xl">
      {/* Brand Header & Tagline */}
      <div className="p-4 border-b border-slate-800/80 flex items-center space-x-3 bg-slate-950/40">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20 font-bold shrink-0">
          <Zap className="w-5 h-5 fill-current" />
        </div>
        <div className="min-w-0">
          <div className="font-bold text-white tracking-tight text-base leading-tight truncate">InsightX AI</div>
          <div className="text-[10px] text-cyan-400 font-medium tracking-wide truncate">
            Autonomous Analytics
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1.5">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-300 px-3 py-1">
          Menu
        </div>
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-lg shadow-indigo-500/25 font-semibold translate-x-0.5"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className={isActive ? "text-white" : "text-slate-400"}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              {isActive && (
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-300 animate-pulse shadow-sm shadow-cyan-300" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Privacy Mode & Lead Analyst Profile */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        {privacyMode && (
          <div className="mb-2 bg-emerald-950/60 border border-emerald-800/80 rounded-lg px-2.5 py-1 flex items-center gap-1.5 text-[11px] text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
            <span>Privacy Mode Active</span>
          </div>
        )}
        <div className="flex items-center space-x-2.5 p-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 border border-slate-700 flex items-center justify-center text-xs text-white font-bold shadow-sm">
            LA
          </div>
          <div className="flex-1 truncate">
            <div className="text-xs font-semibold text-white truncate">Lead Analyst</div>
            <div className="text-[10px] text-slate-400 truncate">Workspace Lead</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
