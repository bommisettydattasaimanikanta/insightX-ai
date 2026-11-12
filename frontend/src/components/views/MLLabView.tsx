import React, { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import {
  Cpu,
  TrendingUp,
  BrainCircuit,
  AlertTriangle,
  Play,
  CheckCircle,
  HelpCircle,
  Clock,
  Layers,
  ChevronRight,
  ShieldCheck
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

export const MLLabView: React.FC = () => {
  const { activeDatasetId, darkMode } = useAppStore();
  
  const [columns, setColumns] = useState<any[]>([]);
  const [targetCol, setTargetCol] = useState<string>("");
  const [isTraining, setIsTraining] = useState(false);
  const [mlResults, setMlResults] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Forecasting state
  const [timeCol, setTimeCol] = useState<string>("");
  const [metricCol, setMetricCol] = useState<string>("");
  const [horizon, setHorizon] = useState<number>(30);
  const [forecastResults, setForecastResults] = useState<any | null>(null);
  const [isForecasting, setIsForecasting] = useState(false);

  useEffect(() => {
    if (activeDatasetId) {
      loadColumnsAndDefaults();
    }
  }, [activeDatasetId]);

  const loadColumnsAndDefaults = async () => {
    if (!activeDatasetId) return;
    try {
      const [profData, semData] = await Promise.all([
        api.getProfile(activeDatasetId),
        api.getSemanticLayer(activeDatasetId)
      ]);
      setColumns(profData.columns || []);
      
      const suggestedTarget = semData.suggested_target || profData.columns?.find((c: any) => c.type === "numeric")?.name || "";
      setTargetCol(suggestedTarget);

      const timeC = semData.time_grains?.[0]?.column || profData.columns?.find((c: any) => c.type === "datetime")?.name || "";
      const metricC = semData.metrics?.[0]?.name || suggestedTarget;
      setTimeCol(timeC);
      setMetricCol(metricC);
    } catch (e) {
      console.error(e);
    }
  };

  const handleTrain = async () => {
    if (!activeDatasetId || !targetCol) return;
    try {
      setIsTraining(true);
      setErrorMsg(null);
      const res = await api.trainModel(activeDatasetId, targetCol);
      setMlResults(res);
    } catch (e: any) {
      setErrorMsg(e.message || "Failed to train models.");
    } finally {
      setIsTraining(false);
    }
  };

  const handleForecast = async () => {
    if (!activeDatasetId || !timeCol || !metricCol) return;
    try {
      setIsForecasting(true);
      const res = await api.runForecast(activeDatasetId, timeCol, metricCol, horizon);
      setForecastResults(res);
    } catch (e: any) {
      console.error(e);
    } finally {
      setIsForecasting(false);
    }
  };

  const getForecastChartOption = () => {
    if (!forecastResults) return {};
    const histDates = forecastResults.historical.map((d: any) => d.date);
    const histVals = forecastResults.historical.map((d: any) => d.actual);
    
    const foreDates = forecastResults.forecast.map((d: any) => d.date);
    const baseVals = forecastResults.forecast.map((d: any) => d.base_case);
    const bestVals = forecastResults.forecast.map((d: any) => d.best_case);
    const worstVals = forecastResults.forecast.map((d: any) => d.worst_case);

    const allDates = [...histDates, ...foreDates];
    const paddedHist = [...histVals, ...new Array(foreDates.length).fill(null)];
    const paddedBase = [...new Array(histDates.length - 1).fill(null), histVals[histVals.length - 1], ...baseVals];
    const paddedBest = [...new Array(histDates.length - 1).fill(null), histVals[histVals.length - 1], ...bestVals];
    const paddedWorst = [...new Array(histDates.length - 1).fill(null), histVals[histVals.length - 1], ...worstVals];

    const textColor = darkMode ? "#94A3B8" : "#64748B";
    const gridLineColor = darkMode ? "#334155" : "#E2E8F0";

    return {
      tooltip: { trigger: "axis" },
      legend: { bottom: 0, textStyle: { color: textColor } },
      grid: { left: "3%", right: "4%", bottom: "10%", top: "10%", containLabel: true },
      xAxis: { type: "category", data: allDates, axisLabel: { color: textColor } },
      yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
      series: [
        { name: "Historical Actuals", type: "line", data: paddedHist, lineStyle: { color: "#4F46E5", width: 2.5 } },
        { name: "Forecast Base Case", type: "line", data: paddedBase, lineStyle: { color: "#06B6D4", width: 2.5, type: "dashed" } },
        { name: "Best Case (+1.5σ)", type: "line", data: paddedBest, lineStyle: { color: "#10B981", width: 1.5 } },
        { name: "Worst Case (-1.5σ)", type: "line", data: paddedWorst, lineStyle: { color: "#EF4444", width: 1.5 } },
      ]
    };
  };

  if (!activeDatasetId) {
    return <div className="p-12 text-center text-slate-500">Please select a dataset to access the ML Lab.</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">ML Lab & AutoML</h1>
            <HonestBadge type="ML prediction" />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Always trains a naive baseline first. Optuna-tuned tree ensembles & time-series models with explicit uncertainty bounds.
          </p>
        </div>

        {/* Target Column Selector & Train Action */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-medium">Target:</span>
            <select
              value={targetCol}
              onChange={(e) => setTargetCol(e.target.value)}
              className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-mono text-xs font-semibold"
            >
              {columns.map((c: any) => (
                <option key={c.name} value={c.name}>
                  {c.name} ({c.type})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleTrain}
            disabled={isTraining}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold shadow-sm transition flex items-center gap-1.5"
          >
            {isTraining ? <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>Train AutoML</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Model Leaderboard */}
      {mlResults && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
                  Model Leaderboard: {mlResults.task_type.toUpperCase()}
                </h2>
                <p className="text-xs text-slate-400">Ranked by test set performance vs naive baseline.</p>
              </div>
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                Champion: {mlResults.best_algorithm}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-400 text-[11px] font-semibold">
                    <th className="py-2 px-3">Algorithm</th>
                    {mlResults.task_type === "regression" ? (
                      <>
                        <th className="py-2 px-3">R² Score</th>
                        <th className="py-2 px-3">RMSE</th>
                        <th className="py-2 px-3">MAE</th>
                      </>
                    ) : (
                      <>
                        <th className="py-2 px-3">Accuracy</th>
                        <th className="py-2 px-3">F1 Score</th>
                      </>
                    )}
                    <th className="py-2 px-3">Label</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-750 font-mono text-[11px]">
                  {mlResults.leaderboard.map((item: any, idx: number) => (
                    <tr key={idx} className={item.algorithm === mlResults.best_algorithm ? "bg-indigo-50/50 dark:bg-indigo-950/30 font-bold" : ""}>
                      <td className="py-2.5 px-3 text-slate-900 dark:text-slate-100">{item.algorithm}</td>
                      {mlResults.task_type === "regression" ? (
                        <>
                          <td className="py-2.5 px-3 text-indigo-600 dark:text-indigo-400">{item.r2}</td>
                          <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{item.rmse}</td>
                          <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{item.mae}</td>
                        </>
                      ) : (
                        <>
                          <td className="py-2.5 px-3 text-indigo-600 dark:text-indigo-400">{item.accuracy}</td>
                          <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{item.f1}</td>
                        </>
                      )}
                      <td className="py-2.5 px-3">
                        <HonestBadge type={item.tag} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model Card & Feature Importance */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Model Card */}
            <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>Transparent Model Card</span>
              </h3>
              <div className="text-xs space-y-2 text-slate-600 dark:text-slate-300">
                <div>
                  <span className="font-semibold text-slate-900 dark:text-white">Sample Size:</span>{" "}
                  {mlResults.model_card.training_samples} training rows, {mlResults.model_card.test_samples} test rows.
                </div>
                <div>
                  <span className="font-semibold text-slate-900 dark:text-white">Performance Summary:</span>{" "}
                  {mlResults.model_card.performance_summary}
                </div>
                {mlResults.warnings.length > 0 && (
                  <div className="mt-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300">
                    <span className="font-bold block mb-1">Audit Caveats:</span>
                    <ul className="list-disc list-inside space-y-0.5">
                      {mlResults.warnings.map((w: string, i: number) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Feature Importance Bars */}
            <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
                Top Driving Features
              </h3>
              <div className="space-y-2">
                {mlResults.feature_importance.map((f: any, idx: number) => (
                  <div key={idx} className="text-xs">
                    <div className="flex justify-between text-[11px] mb-1 font-mono">
                      <span className="text-slate-800 dark:text-slate-200 truncate pr-2">{f.feature}</span>
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold">{f.importance}</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-indigo-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, f.importance * 100 * 2)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Time-Series Forecasting Section */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-700">
          <div>
            <h2 className="text-base font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-500" />
              <span>Time-Series Forecasting & Scenarios</span>
            </h2>
            <p className="text-xs text-slate-400">
              Evaluates Holt-Winters against a naive baseline with confidence bands (80% and 95%).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs font-medium text-slate-800 dark:text-slate-200"
            >
              <option value={7}>7 Days Ahead</option>
              <option value={30}>30 Days Ahead</option>
              <option value={90}>90 Days Ahead</option>
            </select>

            <button
              onClick={handleForecast}
              disabled={isForecasting || !timeCol || !metricCol}
              className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold shadow-sm transition"
            >
              {isForecasting ? "Forecasting..." : "Run Forecast"}
            </button>
          </div>
        </div>

        {forecastResults && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block">Model MAPE</span>
                <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400 font-mono">
                  {forecastResults.backtest.model_mape_pct}%
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block">Naive Baseline MAPE</span>
                <span className="text-lg font-bold text-slate-600 dark:text-slate-300 font-mono">
                  {forecastResults.backtest.naive_baseline_mape_pct}%
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                <span className="text-slate-400 text-[10px] uppercase font-semibold block">Backtest Benchmark</span>
                <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 mt-1 block">
                  {forecastResults.backtest.outperforms_baseline ? "✓ Outperforms Baseline" : "Matches Baseline"}
                </span>
              </div>
            </div>

            <div className="h-72 w-full pt-2">
              <ReactECharts
                option={getForecastChartOption()}
                style={{ height: "100%", width: "100%" }}
                theme={darkMode ? "dark" : undefined}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
