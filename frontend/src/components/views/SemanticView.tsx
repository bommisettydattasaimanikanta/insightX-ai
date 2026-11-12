import React, { useState, useEffect } from "react";
import {
  Layers,
  Edit2,
  Check,
  Plus,
  Trash2,
  Save,
  AlertTriangle,
  HelpCircle,
  ShieldAlert,
  ArrowRight
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

export const SemanticView: React.FC = () => {
  const { activeDatasetId, setActiveTab } = useAppStore();
  
  const [loading, setLoading] = useState(false);
  const [semantic, setSemantic] = useState<any | null>(null);
  const [columns, setColumns] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [dimensions, setDimensions] = useState<any[]>([]);
  const [timeGrains, setTimeGrains] = useState<any[]>([]);
  const [domain, setDomain] = useState("general");
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (activeDatasetId) {
      loadSemantic();
    }
  }, [activeDatasetId]);

  const loadSemantic = async () => {
    if (!activeDatasetId) return;
    try {
      setLoading(true);
      const [semData, profData] = await Promise.all([
        api.getSemanticLayer(activeDatasetId),
        api.getProfile(activeDatasetId)
      ]);
      setSemantic(semData);
      setDomain(semData.domain || "general");
      setMetrics(semData.metrics || []);
      setDimensions(semData.dimensions || []);
      setTimeGrains(semData.time_grains || []);
      setColumns(profData.columns || []);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!activeDatasetId) return;
    try {
      setLoading(true);
      await api.updateSemanticLayer(activeDatasetId, {
        domain,
        metrics,
        dimensions,
        time_grains: timeGrains,
        suggested_target: semantic?.suggested_target,
        suggested_ml_task: semantic?.suggested_ml_task
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleMetricChange = (index: number, field: string, val: any) => {
    const updated = [...metrics];
    updated[index][field] = val;
    setMetrics(updated);
  };

  const addMetric = () => {
    const newM = {
      name: `custom_metric_${metrics.length + 1}`,
      label: `Custom Metric ${metrics.length + 1}`,
      expression: "SUM(`col`)",
      aggregation: "SUM",
      format: "number",
      description: "User defined metric expression"
    };
    setMetrics([...metrics, newM]);
  };

  const removeMetric = (index: number) => {
    setMetrics(metrics.filter((_, i) => i !== index));
  };

  if (!activeDatasetId) {
    return <div className="p-12 text-center text-slate-500">Please select a dataset to inspect the Semantic Layer.</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Title & Save Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Unified Semantic Layer</h1>
            <span className="badge-computed">Single Source of Truth</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            The dashboard, insights engine, and chatbot all read from these exact definitions, guaranteeing numbers always match.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {saveSuccess && (
            <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
              <Check className="w-3.5 h-3.5" /> Saved!
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Definitions</span>
          </button>
          <button
            onClick={() => setActiveTab("dashboard")}
            className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-1"
          >
            <span>Open Dashboard</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Domain Classification Banner */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-4 flex items-center justify-between shadow-sm text-xs">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Detected Business Domain</span>
            <div className="flex items-center gap-2 mt-0.5">
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="font-bold text-slate-900 dark:text-white bg-transparent border-b border-indigo-400 focus:outline-none capitalize text-sm"
              >
                <option value="sales">Sales & Revenue</option>
                <option value="finance">Finance & Accounting</option>
                <option value="marketing">Marketing & Growth</option>
                <option value="e-commerce">E-Commerce & Orders</option>
                <option value="hr">Human Resources & Talent</option>
                <option value="healthcare">Healthcare & Clinical</option>
                <option value="operations">Supply Chain & Operations</option>
                <option value="general">General Tabular</option>
              </select>
              <span className="text-slate-400">
                (Confidence: {Math.round((semantic?.confidence || 0.95) * 100)}%)
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <span className="text-slate-400 text-[10px] uppercase font-semibold block">Suggested ML Task</span>
          <span className="font-mono text-cyan-600 dark:text-cyan-400 capitalize font-bold">
            {semantic?.suggested_ml_task || "Regression"} (Target: {semantic?.suggested_target || "None"})
          </span>
        </div>
      </div>

      {/* Editable Metrics Definitions Table */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
            Active Metric Definitions ({metrics.length})
          </h2>
          <button
            onClick={addMetric}
            className="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-[11px] font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1 transition"
          >
            <Plus className="w-3 h-3" /> Add Custom Metric
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-400 text-[11px] font-semibold">
                <th className="py-2 px-3">Metric Name</th>
                <th className="py-2 px-3">Display Label</th>
                <th className="py-2 px-3">SQL Expression</th>
                <th className="py-2 px-3">Format</th>
                <th className="py-2 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-750">
              {metrics.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-750/50">
                  <td className="py-2 px-3 font-mono font-medium text-slate-800 dark:text-slate-200">{m.name}</td>
                  <td className="py-2 px-3">
                    <input
                      type="text"
                      value={m.label}
                      onChange={(e) => handleMetricChange(idx, "label", e.target.value)}
                      className="p-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-medium w-full max-w-[150px]"
                    />
                  </td>
                  <td className="py-2 px-3">
                    <input
                      type="text"
                      value={m.expression}
                      onChange={(e) => handleMetricChange(idx, "expression", e.target.value)}
                      className="p-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-mono text-[11px] w-full"
                    />
                  </td>
                  <td className="py-2 px-3">
                    <select
                      value={m.format}
                      onChange={(e) => handleMetricChange(idx, "format", e.target.value)}
                      className="p-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-300 font-medium text-[11px]"
                    >
                      <option value="currency">Currency ($ / ₹)</option>
                      <option value="percentage">Percentage (%)</option>
                      <option value="number">Numeric</option>
                    </select>
                  </td>
                  <td className="py-2 px-3 text-right">
                    <button
                      onClick={() => removeMetric(idx)}
                      className="p-1 text-slate-400 hover:text-red-500 rounded"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Column Schema & PII Inspection Table */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
          Column Roles & PII Security Profiling ({columns.length})
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-400 text-[11px] font-semibold">
                <th className="py-2 px-3">Column Name</th>
                <th className="py-2 px-3">Detected Type</th>
                <th className="py-2 px-3">Missing %</th>
                <th className="py-2 px-3">Distinct Values</th>
                <th className="py-2 px-3">PII Guard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-750 font-mono text-[11px]">
              {columns.map((col, idx) => (
                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-750/50">
                  <td className="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">{col.name}</td>
                  <td className="py-2 px-3 text-slate-600 dark:text-slate-300 capitalize">{col.type}</td>
                  <td className="py-2 px-3 text-slate-600 dark:text-slate-300">{col.missing_pct}%</td>
                  <td className="py-2 px-3 text-slate-600 dark:text-slate-300">{col.unique_count}</td>
                  <td className="py-2 px-3">
                    {col.pii_type ? (
                      <span className="bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 px-2 py-0.5 rounded text-[10px] font-semibold inline-flex items-center gap-1 border border-red-200 dark:border-red-900">
                        <ShieldAlert className="w-3 h-3" /> PII Detected ({col.pii_type})
                      </span>
                    ) : (
                      <span className="text-slate-400">Clean</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
