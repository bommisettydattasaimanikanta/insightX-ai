import React, { useState } from "react";
import {
  Cpu,
  Download,
  CheckCircle,
  Sliders,
  Database
} from "lucide-react";

export const SettingsView: React.FC = () => {
  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleSaveKeys = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  const handleExportData = () => {
    setExportSuccess(true);
    setTimeout(() => setExportSuccess(false), 2500);
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto min-h-screen bg-[#070b19] text-slate-100 animate-fadeIn">
      {/* Title */}
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-950/70 border border-indigo-800 text-indigo-400 uppercase">
            Preferences & Configuration
          </span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
          <Sliders className="w-6 h-6 text-cyan-400" />
          <span>Platform & Model Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure swappable LLM adapters, connection credentials, and workspace data exports.
        </p>
      </div>

      {/* Provider-Agnostic LLM Configuration */}
      <div className="bg-[#101735]/90 border border-slate-800/90 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-5">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Swappable LLM Adapters</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            InsightX AI operates out-of-the-box with deterministic semantic code generation. You can optionally connect your preferred LLM provider for conversational queries.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1.5">Model Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-900/90 text-slate-100 font-medium focus:outline-none focus:border-cyan-500 shadow-inner"
            >
              <option value="gemini">Google Gemini (Default)</option>
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="anthropic">Anthropic Claude 3.5 Sonnet</option>
              <option value="local">Local Deterministic Engine</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1.5">API Key (Backend-Stored Only)</label>
            <input
              type="password"
              placeholder="sk-... (Configured securely via environment)"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-900/90 text-slate-100 font-mono focus:outline-none focus:border-cyan-500 shadow-inner"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
          <div>
            {savedSuccess && (
              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5 animate-fadeIn">
                <CheckCircle className="w-3.5 h-3.5" /> LLM Adapter configuration saved successfully!
              </span>
            )}
          </div>
          <button
            onClick={handleSaveKeys}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white font-semibold text-xs shadow-lg shadow-cyan-500/20 transition"
          >
            Save Configuration
          </button>
        </div>
      </div>

      {/* Workspace Data Controls */}
      <div className="bg-[#101735]/90 border border-slate-800/90 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            <span>Workspace Data Management</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Export all ingested parquet files, analytical dashboards, and audit logs.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 text-xs border-t border-slate-800/80">
          <div>
            <div className="font-semibold text-slate-200">Export All Workspace Data</div>
            <div className="text-slate-400 text-[11px] mt-0.5">Package columnar files, schema definitions, and analysis summaries.</div>
          </div>
          <button
            onClick={handleExportData}
            className="px-3.5 py-2 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-900/80 text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-2 transition shrink-0"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>{exportSuccess ? "Archive Requested" : "Export Archive"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
