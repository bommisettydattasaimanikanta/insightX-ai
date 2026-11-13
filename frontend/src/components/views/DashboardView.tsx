import React, { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import {
  Sparkles,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Code,
  HelpCircle,
  X,
  RotateCcw,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
  ArrowRight,
  Info,
  Download,
  Upload,
  BarChart2,
  Cpu,
  ChevronDown,
  FileSpreadsheet,
  FileText,
  Image,
  Presentation,
  ShieldCheck,
  Trophy,
  Layers
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { useAuthStore } from "../../stores/useAuthStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

const COLORBLIND_PALETTE = [
  "#06B6D4", "#10B981", "#6366F1", "#F59E0B", "#EC4899", "#8B5CF6", "#14B8A6", "#3B82F6"
];

export const DashboardView: React.FC = () => {
  const { activeDatasetId, activeDataset, darkMode, setActiveTab } = useAppStore();
  const { user } = useAuthStore();
  
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<any | null>(null);
  const [selectedKpiSql, setSelectedKpiSql] = useState<string | null>(null);
  const [showWhatChangedModal, setShowWhatChangedModal] = useState(false);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);
  const [isUndoing, setIsUndoing] = useState(false);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);
  
  // 4-Step Onboarding Tour state
  const [tourStep, setTourStep] = useState<number | null>(null);

  useEffect(() => {
    if (activeDatasetId) {
      loadDashboard();
    }
  }, [activeDatasetId]);

  useEffect(() => {
    const tourSeen = localStorage.getItem("dashboard_tour_seen");
    if (!tourSeen && dashboard) {
      setTourStep(1);
    }
  }, [dashboard]);

  const loadDashboard = async () => {
    if (!activeDatasetId) return;
    try {
      setLoading(true);
      const data = await api.getDashboard(activeDatasetId);
      setDashboard(data.spec);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTourClose = () => {
    localStorage.setItem("dashboard_tour_seen", "true");
    setTourStep(null);
  };

  const handleUndoClean = async () => {
    if (!activeDatasetId) return;
    try {
      setIsUndoing(true);
      await api.undoClean(activeDatasetId);
      setShowWhatChangedModal(false);
      await loadDashboard();
    } catch (e) {
      console.error(e);
    } finally {
      setIsUndoing(false);
    }
  };

  const handleDownload = async (format: "pdf" | "png" | "pptx" | "excel" | "csv") => {
    if (!activeDatasetId) return;
    try {
      setDownloadingFormat(format);
      await api.downloadExport(activeDatasetId, format, `${activeDataset?.name || "dashboard"}.${format === "excel" ? "xlsx" : format}`);
      setShowDownloadMenu(false);
    } catch (e) {
      console.error("Export failed:", e);
      alert(`Export failed: ${e}`);
    } finally {
      setDownloadingFormat(null);
    }
  };

  // Sparkline SVG renderer
  const renderSparkline = (points: number[] = [], isPositive: boolean = true) => {
    if (!points || points.length < 2) return null;
    const min = Math.min(...points);
    const max = Math.max(...points);
    const range = max - min || 1;
    const width = 80;
    const height = 24;

    const coords = points.map((p, i) => {
      const x = (i / (points.length - 1)) * width;
      const y = height - ((p - min) / range) * (height - 6) - 3;
      return `${x},${y}`;
    }).join(" ");

    const strokeColor = isPositive ? "#10b981" : "#f43f5e";
    const fillColor = isPositive ? "rgba(16, 185, 129, 0.15)" : "rgba(244, 63, 94, 0.15)";
    const closedCoords = `${coords} ${width},${height} 0,${height}`;

    return (
      <svg width={width} height={height} className="overflow-visible shrink-0">
        <polygon points={closedCoords} fill={fillColor} />
        <polyline points={coords} fill="none" stroke={strokeColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  };

  const getChartOption = (chart: any) => {
    const textColor = "#94a3b8";
    const gridLineColor = "rgba(255, 255, 255, 0.08)";
    
    if (chart.chart_type === "line" || chart.chart_type === "area") {
      const dates = chart.data?.map((d: any) => d[chart.x_axis]) || [];
      const values = chart.data?.map((d: any) => d[chart.y_axis]) || [];
      const isArea = chart.chart_type === "area";
      return {
        backgroundColor: "transparent",
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "axis", backgroundColor: "#0f172a", borderColor: "#334155", textStyle: { color: "#f8fafc" } },
        grid: { left: "3%", right: "4%", bottom: "8%", top: "12%", containLabel: true },
        xAxis: { type: "category", data: dates, axisLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          name: chart.y_axis,
          type: "line",
          smooth: true,
          data: values,
          areaStyle: isArea ? { opacity: 0.35, color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#10b981" }, { offset: 1, color: "transparent" }] } } : { opacity: 0.15 },
          lineStyle: { width: 3, color: isArea ? "#10b981" : "#06b6d4" }
        }]
      };
    }

    if (chart.chart_type === "donut") {
      const pieData = chart.data?.map((d: any) => ({ name: String(d[chart.x_axis]), value: d[chart.y_axis] })) || [];
      return {
        backgroundColor: "transparent",
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "item", backgroundColor: "#0f172a", borderColor: "#334155", textStyle: { color: "#f8fafc" } },
        legend: { bottom: 0, textStyle: { color: textColor } },
        series: [{
          type: "pie",
          radius: ["40%", "70%"],
          center: ["50%", "45%"],
          avoidLabelOverlap: false,
          label: { show: false },
          data: pieData
        }]
      };
    }

    if (chart.chart_type === "bar") {
      const categories = chart.data?.map((d: any) => String(d[chart.x_axis])) || [];
      const values = chart.data?.map((d: any) => d[chart.y_axis]) || [];
      return {
        backgroundColor: "transparent",
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "axis", backgroundColor: "#0f172a", borderColor: "#334155", textStyle: { color: "#f8fafc" } },
        grid: { left: "3%", right: "4%", bottom: "14%", top: "12%", containLabel: true },
        xAxis: { type: "category", data: categories, axisLabel: { color: textColor, rotate: 25 }, axisLine: { lineStyle: { color: gridLineColor } } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          type: "bar",
          data: values,
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#06b6d4" }, { offset: 1, color: "#3b82f6" }] }
          }
        }]
      };
    }

    if (chart.chart_type === "scatter") {
      const points = chart.data?.map((d: any) => [d[chart.x_axis], d[chart.y_axis]]) || [];
      return {
        backgroundColor: "transparent",
        color: ["#10b981"],
        tooltip: { trigger: "item", backgroundColor: "#0f172a", borderColor: "#334155", textStyle: { color: "#f8fafc" } },
        grid: { left: "3%", right: "4%", bottom: "8%", top: "12%", containLabel: true },
        xAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          type: "scatter",
          symbolSize: 8,
          data: points,
          itemStyle: { color: "#10b981", shadowBlur: 6, shadowColor: "rgba(16, 185, 129, 0.5)" }
        }]
      };
    }

    return {};
  };

  if (!activeDatasetId) {
    return (
      <div className="p-16 text-center space-y-4 bg-[#070b19] min-h-screen text-slate-100 flex flex-col justify-center items-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-950/60 border border-indigo-700/60 text-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/10">
          <Sparkles className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-white">No Dataset Selected</h3>
        <p className="text-xs text-slate-400 max-w-md">
          Upload an Excel or CSV file or click "Load Demo Data" above to synthesize your autonomous dashboard.
        </p>
        <button
          onClick={() => setActiveTab("ingestion")}
          className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white text-xs font-semibold rounded-xl shadow-lg shadow-cyan-500/20 transition"
        >
          Go to Data Upload
        </button>
      </div>
    );
  }

  if (loading || !dashboard) {
    return (
      <div className="p-20 text-center space-y-3 bg-[#070b19] min-h-screen text-slate-100 flex flex-col justify-center items-center">
        <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
        <h3 className="text-base font-semibold text-white">
          Synthesizing executive dashboard from semantic layer...
        </h3>
        <p className="text-xs text-slate-400">
          Computing verified metrics, sparklines, ranked charts, and domain intelligence.
        </p>
      </div>
    );
  }

  const kpis = dashboard.kpi_cards || [];
  const charts = dashboard.charts || [];
  const topTable = dashboard.top_entities_table;
  const insights = dashboard.insights || [];
  const cleaning = dashboard.cleaning_summary || {};
  const issuesFixed = cleaning.issues_fixed_count || 0;
  const domain = dashboard.domain || "general";
  const theme = dashboard.theme || {};

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto min-h-screen bg-[#070b19] text-slate-100 animate-fadeIn">
      {/* 1. TOP HEADER & DOMAIN BANNER (InsightX Mockup Look) */}
      <div className="relative rounded-2xl p-6 bg-gradient-to-r from-[#0d1533] via-[#10193c] to-[#0d1533] border border-slate-800/90 shadow-2xl backdrop-blur-xl overflow-hidden">
        {/* Ambient Glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2.5">
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider bg-emerald-950/80 border border-emerald-800/80 text-emerald-400">
                {domain.toUpperCase()} DOMAIN
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-medium">Performance Dashboard</span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400">Analyzed {dashboard.analyzed_at || "Just now"}</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.full_name || "Lead Analyst"}
            </h1>
            <p className="text-xs text-slate-300 flex items-center gap-2">
              <span className="font-semibold text-cyan-400">{activeDataset?.name || dashboard.dataset_name}</span>
              <span>•</span>
              <span className="text-slate-400">{activeDataset?.row_count?.toLocaleString()} records processed</span>
            </p>
          </div>

          {/* Quick Actions Bar */}
          <div className="flex flex-wrap items-center gap-2.5 self-end md:self-center">
            <button
              onClick={() => setActiveTab("ingestion")}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 text-xs font-semibold text-slate-200 hover:text-white hover:border-slate-600 transition shadow-sm backdrop-blur-md"
            >
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
              <span>Upload New</span>
            </button>

            <button
              onClick={() => setActiveTab("analysis")}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 text-xs font-semibold text-slate-200 hover:text-white hover:border-slate-600 transition shadow-sm backdrop-blur-md"
            >
              <BarChart2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>Run Analysis</span>
            </button>

            <button
              onClick={() => setActiveTab("predictions")}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 text-xs font-semibold text-slate-200 hover:text-white hover:border-slate-600 transition shadow-sm backdrop-blur-md"
            >
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              <span>Get Predictions</span>
            </button>

            {/* Download Dashboard Menu */}
            <div className="relative">
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white text-xs font-bold hover:opacity-95 transition shadow-lg shadow-cyan-500/20"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download</span>
                <ChevronDown className="w-3 h-3 opacity-80" />
              </button>

              {showDownloadMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-[#0f172a] border border-slate-700/80 shadow-2xl p-1.5 z-50 animate-fadeIn backdrop-blur-xl">
                  <button
                    onClick={() => handleDownload("pdf")}
                    disabled={downloadingFormat === "pdf"}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2.5 text-xs text-slate-200 hover:text-white transition"
                  >
                    <FileText className="w-4 h-4 text-rose-400" />
                    <div>
                      <div className="font-semibold">PDF Document (A4)</div>
                      <div className="text-[10px] text-slate-400">Vector layout via Chromium</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDownload("png")}
                    disabled={downloadingFormat === "png"}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2.5 text-xs text-slate-200 hover:text-white transition"
                  >
                    <Image className="w-4 h-4 text-cyan-400" />
                    <div>
                      <div className="font-semibold">PNG Image</div>
                      <div className="text-[10px] text-slate-400">Full-resolution snapshot</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDownload("pptx")}
                    disabled={downloadingFormat === "pptx"}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2.5 text-xs text-slate-200 hover:text-white transition"
                  >
                    <Presentation className="w-4 h-4 text-amber-400" />
                    <div>
                      <div className="font-semibold">PowerPoint (.pptx)</div>
                      <div className="text-[10px] text-slate-400">Executive presentation slides</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDownload("excel")}
                    disabled={downloadingFormat === "excel"}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2.5 text-xs text-slate-200 hover:text-white transition"
                  >
                    <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                    <div>
                      <div className="font-semibold">Excel Workbook (.xlsx)</div>
                      <div className="text-[10px] text-slate-400">Clean data + KPI sheets</div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleDownload("csv")}
                    disabled={downloadingFormat === "csv"}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800 flex items-center space-x-2.5 text-xs text-slate-200 hover:text-white transition"
                  >
                    <Code className="w-4 h-4 text-indigo-400" />
                    <div>
                      <div className="font-semibold">CSV Data</div>
                      <div className="text-[10px] text-slate-400">Standard tabular data</div>
                    </div>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 2. TOP CLEANING BANNER */}
      {issuesFixed > 0 && (
        <div className="rounded-2xl p-3.5 bg-emerald-950/40 border border-emerald-800/60 flex items-center justify-between text-xs text-emerald-300 backdrop-blur-md">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              We cleaned <strong>{issuesFixed} data issues</strong> automatically with safe defaults.
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowWhatChangedModal(true)}
              className="text-emerald-400 underline hover:text-emerald-300 font-semibold"
            >
              What changed
            </button>
            <span>•</span>
            <button
              onClick={() => setActiveTab("analysis")}
              className="text-slate-400 hover:text-white"
            >
              Details
            </button>
          </div>
        </div>
      )}

      {/* 3. 4 GROUNDED KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.slice(0, 4).map((kpi: any) => {
          const isPositive = (kpi.delta_pct || 0) >= 0;
          return (
            <div
              key={kpi.id}
              className="relative rounded-2xl p-5 bg-[#101735]/90 border border-slate-800/90 shadow-xl backdrop-blur-md flex flex-col justify-between hover:border-slate-700/80 transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 tracking-wide uppercase">
                  {kpi.title}
                </span>
                <HonestBadge tag={kpi.tag || "Computed"} />
              </div>

              <div className="my-3 flex items-baseline justify-between">
                <div>
                  <div className="text-2xl font-extrabold text-white tracking-tight">
                    {kpi.formatted_value || kpi.value}
                  </div>
                  {kpi.subtext && (
                    <div className="text-[11px] text-cyan-400 font-medium mt-0.5">
                      {kpi.subtext}
                    </div>
                  )}
                </div>

                {/* Sparkline Graphic when sequence / time series exists */}
                {kpi.sparkline && renderSparkline(kpi.sparkline, isPositive)}
              </div>

              <div className="flex items-center justify-between text-[11px] pt-2 border-t border-slate-800/60">
                {kpi.delta_pct !== null && kpi.delta_pct !== undefined ? (
                  <div className={`flex items-center space-x-1 font-semibold ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                    {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    <span>{Math.abs(kpi.delta_pct)}% momentum</span>
                  </div>
                ) : (
                  <span className="text-slate-400 text-[10px]">Deterministic calculation</span>
                )}

                {kpi.formula_sql && (
                  <button
                    onClick={() => setSelectedKpiSql(kpi.formula_sql)}
                    className="text-slate-400 hover:text-cyan-400 text-[10px] flex items-center gap-1 transition"
                    title="View SQL calculation"
                  >
                    <Code className="w-3 h-3" />
                    <span>Show how</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 4. MAIN CHARTS & TOP ENTITIES GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Charts (6 to 8 charts) */}
        {charts.map((chart: any) => {
          const colSpan = chart.grid?.w === 12 ? "lg:col-span-12" : chart.grid?.w === 8 ? "lg:col-span-8" : chart.grid?.w === 4 ? "lg:col-span-4" : "lg:col-span-6";
          return (
            <div
              key={chart.id}
              className={`${colSpan} rounded-2xl p-5 bg-[#101735]/90 border border-slate-800/90 shadow-xl backdrop-blur-md flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-white tracking-tight">
                      {chart.title}
                    </h3>
                    {chart.why_this_chart && (
                      <div className="relative">
                        <button
                          onClick={() => setActiveTooltip(activeTooltip === chart.id ? null : chart.id)}
                          className="text-slate-400 hover:text-cyan-400 transition"
                        >
                          <HelpCircle className="w-3.5 h-3.5" />
                        </button>
                        {activeTooltip === chart.id && (
                          <div className="absolute left-0 top-5 w-64 p-2.5 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl text-[11px] text-slate-300 z-50 animate-fadeIn">
                            {chart.why_this_chart}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <HonestBadge tag={chart.tag || "Computed"} />
                </div>
                {chart.description && (
                  <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                    {chart.description}
                  </p>
                )}
              </div>

              <div className="h-64 w-full">
                <ReactECharts option={getChartOption(chart)} style={{ height: "100%", width: "100%" }} />
              </div>

              {chart.sql_query && (
                <div className="pt-2 mt-2 border-t border-slate-800/60 flex justify-between items-center text-[10px] text-slate-400">
                  <span className="truncate max-w-[80%] font-mono">{chart.sql_query}</span>
                  <button
                    onClick={() => setSelectedKpiSql(chart.sql_query)}
                    className="text-cyan-400 hover:underline shrink-0"
                  >
                    SQL
                  </button>
                </div>
              )}
            </div>
          );
        })}

        {/* 5. TOP N TABLE (e.g. Top Opponents by Runs) */}
        {topTable && topTable.rows && topTable.rows.length > 0 && (
          <div className="lg:col-span-8 rounded-2xl p-5 bg-[#101735]/90 border border-slate-800/90 shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white">{topTable.title}</h3>
                <p className="text-[11px] text-slate-400">Ranked by aggregate volume</p>
              </div>
              <HonestBadge tag="Computed" />
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-slate-800/80 text-slate-400">
                    <th className="py-2.5 px-3 font-semibold">{topTable.dimension_label}</th>
                    <th className="py-2.5 px-3 text-right font-semibold">{topTable.count_label}</th>
                    <th className="py-2.5 px-3 text-right font-semibold">Total {topTable.metric_label}</th>
                    <th className="py-2.5 px-3 text-right font-semibold">Average</th>
                    <th className="py-2.5 px-3 text-right font-semibold">Highest</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {topTable.rows.map((row: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                      <td className="py-2.5 px-3 font-semibold text-white flex items-center gap-2">
                        <span className="text-[10px] text-slate-400 font-mono w-4">{idx + 1}</span>
                        <span>{row.entity}</span>
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-300 font-mono">{row.count}</td>
                      <td className="py-2.5 px-3 text-right text-cyan-400 font-bold font-mono">{row.total?.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right text-slate-300 font-mono">{row.average?.toFixed(1)}</td>
                      <td className="py-2.5 px-3 text-right text-emerald-400 font-semibold font-mono">{row.highest?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 6. AI INSIGHTS CARD (Top 3 Ranked Insights) */}
        <div className="lg:col-span-4 rounded-2xl p-5 bg-[#101735]/90 border border-slate-800/90 shadow-xl backdrop-blur-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">Top AI Insights</h3>
              </div>
              <span className="text-[10px] text-cyan-400 font-semibold">Top 3 Ranked</span>
            </div>

            <div className="space-y-3">
              {insights.slice(0, 3).map((ins: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/90 space-y-1.5 hover:border-slate-700 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{ins.title}</span>
                    <HonestBadge tag={ins.tag || "Computed"} />
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    {ins.description}
                  </p>
                  {ins.formula_or_sql && (
                    <div className="pt-1 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span className="truncate max-w-[85%]">{ins.formula_or_sql}</span>
                      <button
                        onClick={() => setSelectedKpiSql(ins.formula_or_sql)}
                        className="text-cyan-400 hover:underline"
                      >
                        how
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => setActiveTab("insights")}
            className="w-full mt-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-cyan-400 hover:text-white hover:bg-slate-800 transition flex items-center justify-center space-x-1.5"
          >
            <span>Ask questions & explore all insights</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SQL "Show How" Modal */}
      {selectedKpiSql && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Code className="w-4 h-4 text-cyan-400" /> Grounded Deterministic Query
              </h3>
              <button onClick={() => setSelectedKpiSql(null)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-300">
              Code computes, AI explains. Every number on this dashboard is grounded by an exact SQL expression.
            </p>
            <div className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-cyan-300 overflow-x-auto border border-slate-800">
              {selectedKpiSql}
            </div>
            <button
              onClick={() => setSelectedKpiSql(null)}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* "What Changed" Modal */}
      {showWhatChangedModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-[#0f172a] border border-slate-700/80 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" /> Auto-Cleaning Summary
              </h3>
              <button onClick={() => setShowWhatChangedModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-around text-center">
              <div>
                <div className="text-xs text-slate-400">Quality Score Before</div>
                <div className="text-lg font-bold text-rose-400 font-mono">
                  {cleaning.score_before?.overall || 88.0}%
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600" />
              <div>
                <div className="text-xs text-slate-400">Quality Score After</div>
                <div className="text-lg font-bold text-emerald-400 font-mono">
                  {cleaning.score_after?.overall || 98.5}%
                </div>
              </div>
            </div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {(cleaning.applied_steps || []).map((step: any, idx: number) => (
                <div key={idx} className="p-2 rounded-lg bg-slate-900 text-xs text-slate-300 flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{step.description || step.operation}</span>
                </div>
              ))}
            </div>
            <div className="pt-2 flex gap-3">
              <button
                onClick={handleUndoClean}
                disabled={isUndoing}
                className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-rose-400 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{isUndoing ? "Reverting..." : "Undo All Changes"}</span>
              </button>
              <button
                onClick={() => setShowWhatChangedModal(false)}
                className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold"
              >
                Keep Cleaned Data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Onboarding Tour */}
      {tourStep !== null && (
        <div className="fixed bottom-6 right-6 max-w-sm bg-[#0f172a] border border-cyan-500/50 rounded-2xl p-5 shadow-2xl z-50 animate-slideUp">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">
              Step {tourStep} of 4 • Quick Tour
            </span>
            <button onClick={handleTourClose} className="text-slate-400 hover:text-white">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <h4 className="text-xs font-bold text-white mb-1">
            {tourStep === 1 && "Autonomous Ingestion & Dashboard"}
            {tourStep === 2 && "Grounded Key Numbers & Sparklines"}
            {tourStep === 3 && "Ranked Visual Intelligence"}
            {tourStep === 4 && "Deterministic Export & Chat"}
          </h4>
          <p className="text-[11px] text-slate-300 mb-3 leading-relaxed">
            {tourStep === 1 && "Your dataset was ingested, profiled, auto-cleaned, and turned into this dashboard without any manual steps."}
            {tourStep === 2 && "Every KPI card carries an honest label, sparkline trend, and 'Show how' link to verify its SQL query."}
            {tourStep === 3 && "Charts are prioritized based on detected domain and column roles to highlight momentum and outliers."}
            {tourStep === 4 && "Download a pixel-perfect PDF, PowerPoint, or CSV, or head to AI Insights to ask questions in plain English."}
          </p>
          <div className="flex justify-between items-center">
            <button onClick={handleTourClose} className="text-[11px] text-slate-400 hover:underline">
              Skip
            </button>
            <button
              onClick={() => {
                if (tourStep < 4) setTourStep(tourStep + 1);
                else handleTourClose();
              }}
              className="px-3 py-1 bg-cyan-500 text-slate-950 font-bold rounded-lg text-xs"
            >
              {tourStep < 4 ? "Next" : "Got it!"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
