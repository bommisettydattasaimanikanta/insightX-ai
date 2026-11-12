import React, { useState, useEffect } from "react";
import {
  Sparkles,
  CheckCircle,
  XCircle,
  AlertCircle,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  Sliders,
  Check,
  X
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

export const CleaningView: React.FC = () => {
  const { activeDatasetId, activeDataset, selectDataset, mode, setActiveTab } = useAppStore();
  
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<any | null>(null);
  const [proposedSteps, setProposedSteps] = useState<any[]>([]);
  const [approvedSteps, setApprovedSteps] = useState<Record<number, boolean>>({});
  const [appliedReport, setAppliedReport] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (activeDatasetId) {
      loadCleaningData();
    }
  }, [activeDatasetId]);

  const loadCleaningData = async () => {
    if (!activeDatasetId) return;
    try {
      setLoading(true);
      setErrorMsg(null);
      const [profData, planData] = await Promise.all([
        api.getProfile(activeDatasetId),
        api.getCleaningPlan(activeDatasetId)
      ]);
      setProfile(profData);
      setProposedSteps(planData.proposed_steps || []);
      
      // Default approval: if Autopilot mode, approve all; if Review mode, require explicit check
      const initialApproval: Record<number, boolean> = {};
      (planData.proposed_steps || []).forEach((s: any) => {
        initialApproval[s.step_index] = mode === "autopilot";
      });
      setApprovedSteps(initialApproval);
    } catch (e: any) {
      setErrorMsg(e.message || "Failed to load cleaning plan.");
    } finally {
      setLoading(false);
    }
  };

  const toggleStep = (stepIndex: number) => {
    setApprovedSteps(prev => ({
      ...prev,
      [stepIndex]: !prev[stepIndex]
    }));
  };

  const handleApplySteps = async () => {
    if (!activeDatasetId) return;
    const stepsToApply = proposedSteps.filter(s => approvedSteps[s.step_index]);
    if (stepsToApply.length === 0) {
      setErrorMsg("Please approve at least one cleaning step to apply.");
      return;
    }

    try {
      setLoading(true);
      const res = await api.applyCleaning(activeDatasetId, stepsToApply);
      setAppliedReport(res.report);
      // Refresh active dataset
      await selectDataset(activeDatasetId);
      // Refresh profile
      const updatedProfile = await api.getProfile(activeDatasetId);
      setProfile(updatedProfile);
    } catch (e: any) {
      setErrorMsg(e.message || "Failed to execute cleaning steps.");
    } finally {
      setLoading(false);
    }
  };

  if (!activeDatasetId) {
    return (
      <div className="p-12 text-center text-slate-500">
        Please upload or select a dataset to access the Cleaning Studio.
      </div>
    );
  }

  const qualityScore = profile?.quality_score || { overall: 100, completeness: 100, uniqueness: 100, validity: 100, consistency: 100 };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Title & Mode Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cleaning Studio</h1>
            <HonestBadge type="Computed" />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Reversible transformations. Original Parquet data is immutable; every step increments the version number.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const all: Record<number, boolean> = {};
              proposedSteps.forEach(s => (all[s.step_index] = true));
              setApprovedSteps(all);
            }}
            className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            Approve All
          </button>
          <button
            onClick={handleApplySteps}
            disabled={loading || proposedSteps.length === 0}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>Apply Selected Steps</span>
          </button>
        </div>
      </div>

      {/* Data Quality Score Card */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm">
        <div className="md:col-span-1 border-r border-slate-100 dark:border-slate-700 pr-4 flex flex-col justify-center items-center text-center">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Quality Score</div>
          <div className="text-4xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-1">
            {appliedReport ? appliedReport.score_after.overall : qualityScore.overall}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">out of 100.0</div>
          {appliedReport && (
            <div className="mt-2 text-[10px] font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-full flex items-center gap-1">
              <TrendingUp className="w-3 h-3" /> +{appliedReport.improvement} pts
            </div>
          )}
        </div>

        <div className="md:col-span-4 grid grid-cols-2 md:grid-cols-4 gap-4 pl-2 items-center text-xs">
          <div>
            <div className="text-slate-400 text-[11px]">Completeness (40%)</div>
            <div className="font-bold text-slate-800 dark:text-slate-100 text-base mt-0.5">{qualityScore.completeness}%</div>
            <div className="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full mt-1.5 overflow-hidden">
              <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${qualityScore.completeness}%` }} />
            </div>
          </div>

          <div>
            <div className="text-slate-400 text-[11px]">Uniqueness (20%)</div>
            <div className="font-bold text-slate-800 dark:text-slate-100 text-base mt-0.5">{qualityScore.uniqueness}%</div>
            <div className="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full mt-1.5 overflow-hidden">
              <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${qualityScore.uniqueness}%` }} />
            </div>
          </div>

          <div>
            <div className="text-slate-400 text-[11px]">Validity (20%)</div>
            <div className="font-bold text-slate-800 dark:text-slate-100 text-base mt-0.5">{qualityScore.validity}%</div>
            <div className="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full mt-1.5 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${qualityScore.validity}%` }} />
            </div>
          </div>

          <div>
            <div className="text-slate-400 text-[11px]">Consistency (20%)</div>
            <div className="font-bold text-slate-800 dark:text-slate-100 text-base mt-0.5">{qualityScore.consistency}%</div>
            <div className="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full mt-1.5 overflow-hidden">
              <div className="bg-purple-500 h-full rounded-full" style={{ width: `${qualityScore.consistency}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Applied Success Message */}
      {appliedReport && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0 text-emerald-500" />
            <span>
              Applied {appliedReport.applied_steps.length} cleaning operations. Created Dataset Version v{activeDataset?.current_version}.
            </span>
          </div>
          <button
            onClick={() => setActiveTab("semantic")}
            className="font-semibold underline flex items-center gap-1 hover:text-emerald-900"
          >
            Proceed to Semantic Layer <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Proposed Cleaning Plan Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
            Proposed Actionable Cleaning Steps ({proposedSteps.length})
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            {Object.values(approvedSteps).filter(Boolean).length} approved
          </span>
        </div>

        {proposedSteps.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-8 text-center text-xs text-slate-500">
            No critical data issues detected! Your dataset is clean and ready for analysis.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {proposedSteps.map((step) => {
              const isApproved = approvedSteps[step.step_index] ?? false;
              return (
                <div
                  key={step.step_index}
                  className={`p-4 rounded-xl border transition-all ${
                    isApproved
                      ? "bg-white dark:bg-slate-800 border-indigo-300 dark:border-indigo-800 shadow-sm"
                      : "bg-slate-50 dark:bg-slate-850 border-slate-200 dark:border-slate-800 opacity-60"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                          {step.category}
                        </span>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">{step.title}</h4>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                        {step.description}
                      </p>
                    </div>

                    <button
                      onClick={() => toggleStep(step.step_index)}
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition ${
                        isApproved
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "bg-slate-200 dark:bg-slate-700 text-slate-500 hover:text-slate-800"
                      }`}
                      title={isApproved ? "Approved (Click to Reject)" : "Rejected (Click to Approve)"}
                    >
                      {isApproved ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                    </button>
                  </div>

                  <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-750 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>Impact Preview:</span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-semibold">
                      {step.impact_rows} rows affected ({step.impact_pct}%)
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
