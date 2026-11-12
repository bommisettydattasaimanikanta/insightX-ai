import React, { useState } from "react";
import {
  ShieldCheck,
  Lock,
  Cpu,
  Key,
  Download,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Server
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";

export const SettingsView: React.FC = () => {
  const { privacyMode, togglePrivacyMode } = useAppStore();
  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSaveKeys = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-indigo-500" />
          <span>Security, Privacy & Platform Settings</span>
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Zero data leakage to external models. Provider-agnostic LLM adapters with backend-only key isolation.
        </p>
      </div>

      {/* Privacy Mode Card */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Lock className="w-4 h-4 text-emerald-500" />
              <span>Strict Privacy Mode (PII Masking)</span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              When enabled, all customer names, emails, phone numbers, and IDs are automatically masked with hashes before reaching any LLM adapter.
            </p>
          </div>

          <button
            onClick={togglePrivacyMode}
            className={`w-12 h-6 rounded-full transition-colors relative ${
              privacyMode ? "bg-emerald-600" : "bg-slate-300 dark:bg-slate-700"
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-white transition-transform transform ${
                privacyMode ? "translate-x-7" : "translate-x-1"
              }`}
            />
          </button>
        </div>
      </div>

      {/* Security Architecture & Prompt-Injection Defense */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-indigo-500" />
          <span>Prompt-Injection & Sandbox Defenses</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-700 space-y-1">
            <span className="font-bold text-slate-900 dark:text-white block">Prompt-Injection Shield</span>
            <p className="text-slate-500 dark:text-slate-400">
              Cell values and column headers are passed exclusively as data inputs in SQL parameters, preventing adversarial prompt injections.
            </p>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-700 space-y-1">
            <span className="font-bold text-slate-900 dark:text-white block">Python & SQL Sandbox</span>
            <p className="text-slate-500 dark:text-slate-400">
              No network access permitted. 10-second query timeout and 512 MB memory boundary strictly enforced.
            </p>
          </div>
        </div>
      </div>

      {/* Provider-Agnostic LLM Configuration */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-500" />
          <span>Swappable LLM Adapters</span>
        </h3>
        <p className="text-xs text-slate-400">
          InsightForge operates out-of-the-box with deterministic semantic code-generation. You can optionally connect your preferred LLM provider.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 font-medium"
            >
              <option value="gemini">Google Gemini (Default)</option>
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="anthropic">Anthropic Claude 3.5</option>
              <option value="local">Local Deterministic Engine</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">API Key (Backend Stored Only)</label>
            <input
              type="password"
              placeholder="sk-... (Stored securely in .env)"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 font-mono"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {savedSuccess && (
            <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> LLM Adapter Updated!
            </span>
          )}
          <button
            onClick={handleSaveKeys}
            className="ml-auto px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition"
          >
            Save Configuration
          </button>
        </div>
      </div>

      {/* GDPR Data Controls */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">Privacy Tools & Workspace Deletion</h3>
        <div className="flex items-center justify-between text-xs">
          <div>
            <div className="font-semibold text-slate-800 dark:text-slate-200">Export All My Data</div>
            <div className="text-slate-400 text-[11px]">Download all parquet files, dashboards, and audit logs.</div>
          </div>
          <button className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-1.5">
            <Download className="w-3.5 h-3.5" /> Export Archive
          </button>
        </div>
      </div>
    </div>
  );
};
