import React, { useState, useRef, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import {
  Send,
  Sparkles,
  Code,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Pin,
  Bot,
  User,
  Table,
  BarChart3,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  sql?: string;
  data?: any[];
  chart?: any;
  tag?: string;
  confidence?: number;
  columns_used?: string[];
  showSql?: boolean;
}

export const ChatView: React.FC = () => {
  const { activeDatasetId, activeDataset, privacyMode, darkMode } = useAppStore();
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "What is the total sales amount by region?",
    "What are the top 5 categories by sales?",
    "Show average quantity per category",
    "What is the total revenue over time?",
    "What is the overall count of records?"
  ];

  useEffect(() => {
    // Initial welcome message
    if (activeDataset && messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          sender: "bot",
          text: `Hello! I'm your grounded AI data analyst. You can ask questions in English, Hindi, or any language. Every number is deterministically computed via validated DuckDB SQL linked directly to your Semantic Layer.`,
          tag: "AI-generated"
        }
      ]);
    }
  }, [activeDataset]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (qText?: string) => {
    const question = qText || inputQuestion.trim();
    if (!question || !activeDatasetId || isLoading) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: question
    };
    setMessages(prev => [...prev, userMsg]);
    setInputQuestion("");
    setIsLoading(true);

    try {
      const res = await api.chatQuery(activeDatasetId, question, [], privacyMode);
      const botMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "bot",
        text: res.answer,
        sql: res.sql,
        data: res.data,
        chart: res.chart,
        tag: res.tag || "Computed",
        confidence: res.confidence,
        columns_used: res.columns_used,
        showSql: false
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (e: any) {
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "bot",
        text: `Error processing query: ${e.message}`,
        tag: "AI-generated"
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleShowSql = (msgId: string) => {
    setMessages(prev =>
      prev.map(m => (m.id === msgId ? { ...m, showSql: !m.showSql } : m))
    );
  };

  if (!activeDatasetId) {
    return <div className="p-12 text-center text-slate-500">Please select a dataset to start chatting.</div>;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] max-w-5xl mx-auto p-4 animate-fadeIn">
      {/* Top Banner */}
      <div className="pb-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>Dataset Q&A Grounded Agent</span>
            <span className="badge-computed">sqlglot AST Validated</span>
          </h1>
          <p className="text-xs text-slate-400">
            Enforces SELECT-only, table allow-listing, and forced LIMIT. The LLM never invents numbers.
          </p>
        </div>
      </div>

      {/* Suggested Questions Pill Row */}
      <div className="py-2 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-slate-400 font-medium shrink-0">Try asking:</span>
        {suggestedQuestions.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 hover:text-indigo-600 transition shrink-0 font-medium text-[11px]"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Messages Thread */}
      <div className="flex-1 overflow-y-auto space-y-4 py-4 pr-1">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
                msg.sender === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800 text-cyan-400 border border-slate-700"
              }`}
            >
              {msg.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-2xl rounded-2xl p-4 space-y-3 text-xs leading-relaxed ${
                msg.sender === "user"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 shadow-sm"
              }`}
            >
              <div>{msg.text}</div>

              {/* Bot Extras: SQL Toggle, Table, Chart */}
              {msg.sender === "bot" && (
                <div className="pt-2 border-t border-slate-100 dark:border-slate-750 space-y-3">
                  <div className="flex items-center justify-between">
                    <HonestBadge type={msg.tag || "Computed"} />
                    {msg.sql && (
                      <button
                        onClick={() => toggleShowSql(msg.id)}
                        className="text-indigo-600 dark:text-indigo-400 font-mono text-[11px] font-semibold flex items-center gap-1 hover:underline"
                      >
                        <Code className="w-3.5 h-3.5" />
                        <span>{msg.showSql ? "Hide SQL" : "Show SQL"}</span>
                      </button>
                    )}
                  </div>

                  {msg.showSql && msg.sql && (
                    <div className="p-2.5 rounded-lg bg-slate-900 text-emerald-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap border border-slate-800">
                      {msg.sql}
                    </div>
                  )}

                  {/* Chart Rendering if returned */}
                  {msg.chart && msg.chart.data && (
                    <div className="h-48 w-full mt-2">
                      <ReactECharts
                        option={{
                          tooltip: { trigger: "axis" },
                          grid: { left: "3%", right: "4%", bottom: "12%", top: "10%", containLabel: true },
                          xAxis: {
                            type: "category",
                            data: msg.chart.data.map((d: any) => String(d[msg.chart.x_axis])),
                            axisLabel: { color: darkMode ? "#94A3B8" : "#64748B", rotate: 20 }
                          },
                          yAxis: { type: "value", splitLine: { lineStyle: { color: darkMode ? "#334155" : "#E2E8F0" } } },
                          series: [{
                            type: "bar",
                            data: msg.chart.data.map((d: any) => d[msg.chart.y_axis]),
                            itemStyle: { color: "#4F46E5", borderRadius: [4, 4, 0, 0] }
                          }]
                        }}
                        style={{ height: "100%", width: "100%" }}
                        theme={darkMode ? "dark" : undefined}
                      />
                    </div>
                  )}

                  {/* Table Data Preview */}
                  {msg.data && msg.data.length > 0 && !msg.chart && (
                    <div className="overflow-x-auto max-h-40 border border-slate-100 dark:border-slate-750 rounded-lg">
                      <table className="w-full text-left font-mono text-[11px]">
                        <thead className="bg-slate-50 dark:bg-slate-850 text-slate-400">
                          <tr>
                            {Object.keys(msg.data[0]).map((k) => (
                              <th key={k} className="p-1.5">{k}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                          {msg.data.slice(0, 5).map((row, rIdx) => (
                            <tr key={rIdx}>
                              {Object.values(row).map((val: any, cIdx) => (
                                <td key={cIdx} className="p-1.5">
                                  {typeof val === "number" ? val.toLocaleString() : String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-600" />
            <span>Validating SQL AST & querying DuckDB...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            placeholder="Ask anything about this dataset (e.g., 'What is the highest sales amount by region?')..."
            className="flex-1 p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
          />
          <button
            type="submit"
            disabled={isLoading || !inputQuestion.trim()}
            className="p-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white shadow-sm transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
