import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  CheckCircle,
  Clock,
  ArrowRight,
  Sparkles,
  HelpCircle,
  AlertCircle,
  Filter,
  CheckSquare,
  Square,
  ChevronDown
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

export const InsightsView: React.FC = () => {
  const { activeDatasetId } = useAppStore();
  
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>("All");

  useEffect(() => {
    if (activeDatasetId) {
      loadInsightsData();
    }
  }, [activeDatasetId]);

  const loadInsightsData = async () => {
    if (!activeDatasetId) return;
    try {
      setLoading(true);
      const [insData, recData] = await Promise.all([
        api.getInsights(activeDatasetId),
        api.getRecommendations(activeDatasetId)
      ]);
      setInsights(insData.insights || []);
      setRecommendations(recData || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (recId: string, currentStatus: string) => {
    const nextStatus = currentStatus === "To-do" ? "Doing" : currentStatus === "Doing" ? "Done" : "To-do";
    try {
      await api.updateRecommendationStatus(activeDatasetId!, recId, nextStatus);
      setRecommendations(prev =>
        prev.map(r => (r.id === recId ? { ...r, status: nextStatus } : r))
      );
    } catch (e) {
      console.error(e);
    }
  };

  if (!activeDatasetId) {
    return <div className="p-12 text-center text-slate-500">Please select a dataset to inspect insights.</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Ranked Strategic Insights</h1>
          <HonestBadge type="Statistical test" />
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Scored by: <span className="font-mono text-indigo-600 dark:text-indigo-400 font-semibold">Effect Size × Significance × Coverage × Business Relevance</span>. Fully grounded in deterministic query executions.
        </p>
      </div>

      {/* Ranked Insights List */}
      <div className="space-y-4">
        {insights.map((ins, idx) => (
          <div
            key={ins.id}
            className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3 hover:border-indigo-400 dark:hover:border-indigo-600 transition"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 font-mono text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  #{idx + 1}
                </span>
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
                    {ins.headline}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                    {ins.why_it_matters}
                  </p>
                </div>
              </div>

              <div className="flex flex-col items-end gap-1 shrink-0">
                <HonestBadge type={ins.tag} />
                <span className="text-[10px] font-mono text-slate-400">Score: {ins.score}</span>
              </div>
            </div>

            {/* Evidence & Query Formula */}
            <div className="bg-slate-50 dark:bg-slate-900/60 rounded-xl p-3 border border-slate-100 dark:border-slate-750 text-xs flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div>
                <span className="text-slate-400 text-[10px] uppercase font-semibold">Evidence:</span>{" "}
                <span className="font-semibold text-slate-800 dark:text-slate-200">{ins.evidence}</span>
              </div>
              <div className="text-[11px] font-mono text-indigo-600 dark:text-indigo-400 truncate max-w-md">
                {ins.sql}
              </div>
            </div>

            {/* Caveat if present */}
            {ins.caveat && (
              <div className="text-[11px] text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 p-2 rounded-lg border border-amber-200 dark:border-amber-900">
                {ins.caveat}
              </div>
            )}

            {/* Action Box */}
            <div className="pt-2 flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                <span className="font-semibold text-slate-900 dark:text-white">Recommended Action:</span>
                <span>{ins.suggested_action}</span>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                Confidence: {Math.round(ins.confidence * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Actionable Recommendations Tracker */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Strategic Recommendations Tracker
            </h2>
            <p className="text-xs text-slate-400">
              Track decisions from ideation to completion. Monitor the associated outcome metric.
            </p>
          </div>
          <HonestBadge type="AI-generated" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-850 flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400 font-mono">
                    Impact: {rec.impact} • Effort: {rec.effort}
                  </span>
                  <span className="text-slate-400 font-mono">{rec.confidence_pct}% Conf.</span>
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-white mt-1.5 leading-snug">
                  {rec.title}
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  Rationale: {rec.rationale}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <span className="text-[10px] text-slate-400 truncate max-w-[120px]">
                  {rec.linked_metric || "Metric tracker"}
                </span>

                <button
                  onClick={() => handleUpdateStatus(rec.id, rec.status)}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold transition ${
                    rec.status === "Done"
                      ? "bg-emerald-600 text-white"
                      : rec.status === "Doing"
                      ? "bg-cyan-600 text-white"
                      : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                  }`}
                >
                  {rec.status} (Click to advance)
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
