import React, { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import {
  Download,
  FileText,
  FileCode,
  Filter,
  Info,
  Calendar,
  Layers,
  Sparkles,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Code
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

const COLORBLIND_PALETTE = [
  "#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#64748B"
];

export const DashboardView: React.FC = () => {
  const { activeDatasetId, activeDataset, darkMode } = useAppStore();
  
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<any | null>(null);
  const [selectedKpiSql, setSelectedKpiSql] = useState<string | null>(null);
  const [filterValue, setFilterValue] = useState<string>("All");

  useEffect(() => {
    if (activeDatasetId) {
      loadDashboard();
    }
  }, [activeDatasetId]);

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

  const formatValue = (val: number, format: string) => {
    if (val === undefined || val === null) return "0";
    if (format === "currency") return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (format === "percentage") return `${(val * 100).toFixed(1)}%`;
    return val.toLocaleString();
  };

  const getChartOption = (chart: any) => {
    const textColor = darkMode ? "#94A3B8" : "#64748B";
    const gridLineColor = darkMode ? "#334155" : "#E2E8F0";
    
    if (chart.chart_type === "line") {
      const dates = chart.data?.map((d: any) => d[chart.x_axis]) || [];
      const values = chart.data?.map((d: any) => d[chart.y_axis]) || [];
      return {
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "axis" },
        grid: { left: "3%", right: "4%", bottom: "8%", top: "12%", containLabel: true },
        xAxis: { type: "category", data: dates, axisLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          name: chart.y_axis,
          type: "line",
          smooth: true,
          data: values,
          areaStyle: { opacity: 0.15 },
          lineStyle: { width: 3 }
        }]
      };
    }

    if (chart.chart_type === "donut") {
      const pieData = chart.data?.map((d: any) => ({ name: String(d[chart.x_axis]), value: d[chart.y_axis] })) || [];
      return {
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "item" },
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
        color: COLORBLIND_PALETTE,
        tooltip: { trigger: "axis" },
        grid: { left: "3%", right: "4%", bottom: "12%", top: "12%", containLabel: true },
        xAxis: { type: "category", data: categories, axisLabel: { color: textColor, rotate: 25 }, axisLine: { lineStyle: { color: gridLineColor } } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          type: "bar",
          data: values,
          itemStyle: { borderRadius: [6, 6, 0, 0] }
        }]
      };
    }

    if (chart.chart_type === "scatter") {
      const points = chart.data?.map((d: any) => [d[chart.x_axis], d[chart.y_axis]]) || [];
      return {
        color: [COLORBLIND_PALETTE[1]],
        tooltip: { trigger: "item" },
        grid: { left: "3%", right: "4%", bottom: "8%", top: "12%", containLabel: true },
        xAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: gridLineColor } }, axisLabel: { color: textColor } },
        series: [{
          type: "scatter",
          symbolSize: 8,
          data: points
        }]
      };
    }

    // Default fallback
    return {};
  };

  if (!activeDatasetId) {
    return <div className="p-12 text-center text-slate-500">Please select a dataset to view its dashboard.</div>;
  }

  if (loading || !dashboard) {
    return (
      <div className="p-12 text-center text-slate-500 flex items-center justify-center gap-2">
        <RefreshCw className="w-5 h-5 animate-spin text-indigo-600" />
        <span>Synthesizing declarative dashboard from Semantic Layer...</span>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Dashboard Top Header & Exports */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{dashboard.title}</h1>
            <HonestBadge type="Computed" />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Domain: <span className="capitalize font-semibold text-indigo-600 dark:text-indigo-400">{dashboard.domain}</span> • Live data grounded to Semantic Layer v{activeDataset?.current_version}.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={api.getPDFUrl(activeDatasetId)}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-750 flex items-center gap-1.5 shadow-sm"
          >
            <FileText className="w-3.5 h-3.5 text-red-500" />
            <span>Executive PDF</span>
          </a>

          <a
            href={api.getNotebookUrl(activeDatasetId)}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-750 flex items-center gap-1.5 shadow-sm"
          >
            <FileCode className="w-3.5 h-3.5 text-amber-500" />
            <span>Jupyter Notebook (.ipynb)</span>
          </a>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {dashboard.kpi_cards?.map((kpi: any) => (
          <div
            key={kpi.id}
            className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm relative group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 truncate pr-2">
                {kpi.title}
              </span>
              <button
                onClick={() => setSelectedKpiSql(selectedKpiSql === kpi.formula_sql ? null : kpi.formula_sql)}
                className="text-[10px] text-indigo-600 dark:text-indigo-400 hover:underline font-mono flex items-center gap-0.5"
                title="Show deterministic query / formula"
              >
                <Code className="w-3 h-3" /> Show how
              </button>
            </div>

            <div className="text-2xl font-extrabold text-slate-900 dark:text-white mt-2">
              {formatValue(kpi.value, kpi.format)}
            </div>

            <div className="mt-2 flex items-center justify-between text-xs">
              {kpi.delta_pct !== null ? (
                <div
                  className={`flex items-center gap-0.5 font-semibold text-[11px] ${
                    kpi.delta_pct >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {kpi.delta_pct >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  <span>{kpi.delta_pct >= 0 ? `+${kpi.delta_pct}%` : `${kpi.delta_pct}%`} vs prev period</span>
                </div>
              ) : (
                <span className="text-slate-400 text-[11px]">Baseline</span>
              )}
              <HonestBadge type="Computed" />
            </div>

            {/* SQL Formula Popover */}
            {selectedKpiSql === kpi.formula_sql && (
              <div className="absolute inset-0 bg-slate-900/95 text-slate-200 p-4 rounded-2xl flex flex-col justify-between z-20 animate-fadeIn">
                <div>
                  <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">Deterministic SQL Formula</div>
                  <pre className="text-[11px] font-mono mt-2 overflow-x-auto whitespace-pre-wrap text-emerald-300">
                    {kpi.formula_sql}
                  </pre>
                </div>
                <button
                  onClick={() => setSelectedKpiSql(null)}
                  className="self-end text-[10px] text-slate-400 hover:text-white underline mt-2"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {dashboard.charts?.map((chart: any) => (
          <div
            key={chart.id}
            className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm space-y-3"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">{chart.title}</h3>
                <span className="text-[10px] font-mono text-slate-400">Grounded DuckDB Parquet Query</span>
              </div>
              <HonestBadge type={chart.tag || "Computed"} />
            </div>

            <div className="h-64 w-full">
              <ReactECharts
                option={getChartOption(chart)}
                style={{ height: "100%", width: "100%" }}
                theme={darkMode ? "dark" : undefined}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
