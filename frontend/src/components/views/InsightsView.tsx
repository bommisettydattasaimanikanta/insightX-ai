import React, { useState } from "react";
import {
  MessageSquare,
  Send,
  Pin,
  RefreshCw,
  Check,
  Code,
  AlertTriangle,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";
import { HonestBadge } from "../common/HonestBadge";

export const InsightsView: React.FC = () => {
  const { activeDatasetId, activeDataset, pinQueryToDashboard } = useAppStore();
  
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [chatResponse, setChatResponse] = useState<any | null>(null);
  const [pinnedSuccess, setPinnedSuccess] = useState(false);
  const [showSql, setShowSql] = useState(true);

  const handleAsk = async (queryText?: string) => {
    const q = queryText || question;
    if (!activeDatasetId || !q.trim()) return;
    try {
      setAsking(true);
      setPinnedSuccess(false);
      const res = await api.chatQuery(activeDatasetId, q);
      setChatResponse({ ...res, question: q });
      if (!queryText) setQuestion("");
    } catch (e: any) {
      console.error(e);
      setChatResponse({
        question: q,
        answer: `I couldn't safely compute that from the dataset. ${e.message}`,
        explanation: `I couldn't safely compute that from the dataset. ${e.message}`,
        sql: "SELECT * FROM data LIMIT 10",
        error: e.message,
        friendly_message: "Could not execute query on dataset.",
        suggested_fix: "Try asking for a specific metric like 'total runs', 'highest score', or 'average runs per match'."
      });
    } finally {
      setAsking(false);
    }
  };

  const handlePin = () => {
    if (!chatResponse) return;
    pinQueryToDashboard(chatResponse);
    setPinnedSuccess(true);
    setTimeout(() => setPinnedSuccess(false), 3000);
  };

  // Sample query chips tailored to dataset
  const isCricket = activeDataset?.name?.toLowerCase().includes("cricket") || activeDataset?.description?.toLowerCase().includes("cricket");
  const suggestedQueries = isCricket ? [
    "total runs",
    "average runs per match",
    "which opponent has the highest average",
    "runs by year",
    "highest score"
  ] : [
    "What is the total sales revenue by region?",
    "Show the top 5 customers by sales volume",
    "Which category generated highest average order?",
    "Monthly trend of revenue and transactions"
  ];

  if (!activeDatasetId) {
    return (
      <div className="p-16 text-center text-slate-400">
        Please select a dataset to inspect AI insights and ask questions.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto min-h-screen bg-[#070b19] text-slate-100 animate-fadeIn">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-950/70 border border-cyan-800 text-cyan-400 uppercase">
            AI Synthesis & Agent
          </span>
          <span className="text-xs text-slate-400">{activeDataset?.name}</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight mt-1">
          AI Insights & "Ask Your Data"
        </h1>
        <p className="text-xs text-slate-400">
          Safe text-to-SQL conversational analysis and grounded question answering.
        </p>
      </div>

      {/* "Ask Your Data" Box */}
      <div className="rounded-2xl p-6 bg-[#101735]/90 border border-slate-800/90 shadow-2xl backdrop-blur-md space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Ask your data in plain English</h3>
              <p className="text-[11px] text-slate-400">
                The agent converts your question to verified SQL, computes the exact result, and explains it.
              </p>
            </div>
          </div>
          <HonestBadge tag="AI-generated" />
        </div>

        {/* Suggested Chips */}
        <div className="flex flex-wrap gap-2 pt-1">
          {suggestedQueries.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(q)}
              className="text-[11px] px-3 py-1 rounded-full bg-slate-900 border border-slate-700/80 hover:border-cyan-500 text-slate-300 hover:text-white transition shadow-sm"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="e.g. Which opponent has the highest average?"
            className="flex-1 bg-slate-900/90 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 shadow-inner"
          />
          <button
            onClick={() => handleAsk()}
            disabled={asking || !question.trim()}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white text-xs font-bold rounded-xl shadow-lg shadow-cyan-500/20 flex items-center space-x-2 disabled:opacity-50"
          >
            {asking ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Ask</span>
          </button>
        </div>

        {/* Loading Indicator */}
        {asking && (
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center space-x-3 text-xs text-slate-300 animate-fadeIn">
            <RefreshCw className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
            <span>Analyzing query, verifying SQL schema, and executing against columnar dataset...</span>
          </div>
        )}

        {/* Answer Display */}
        {chatResponse && !asking && (
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3 animate-fadeIn">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300">
                Q: <span className="text-white italic">"{chatResponse.question}"</span>
              </span>
              <div className="flex items-center space-x-2">
                {chatResponse.sql && (
                  <button
                    onClick={() => setShowSql(!showSql)}
                    className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white text-xs font-medium transition"
                  >
                    <Code className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{showSql ? "Hide SQL" : "Show SQL"}</span>
                    {showSql ? <ChevronUp className="w-3 h-3 opacity-60" /> : <ChevronDown className="w-3 h-3 opacity-60" />}
                  </button>
                )}
                <button
                  onClick={handlePin}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-indigo-950 border border-indigo-700 text-cyan-400 hover:text-white text-xs font-semibold transition"
                >
                  {pinnedSuccess ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Pin className="w-3.5 h-3.5" />}
                  <span>{pinnedSuccess ? "Pinned to Dashboard!" : "Pin to Dashboard"}</span>
                </button>
              </div>
            </div>

            {/* Answer Text */}
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {chatResponse.answer || chatResponse.explanation}
            </p>

            {/* Error banner if query failed */}
            {chatResponse.error && (
              <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-rose-200">
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{chatResponse.friendly_message || "Could not execute query on dataset."}</span>
                </div>
                {chatResponse.suggested_fix && (
                  <div className="text-[11px] text-slate-400">
                    Suggestion: {chatResponse.suggested_fix}
                  </div>
                )}
              </div>
            )}

            {/* Grounded SQL Display with Show/Hide toggle */}
            {chatResponse.sql && showSql && (
              <div className="p-2.5 rounded-lg bg-slate-900 font-mono text-[11px] text-cyan-400 border border-slate-800 overflow-x-auto space-y-1 animate-fadeIn">
                <div className="text-[9px] text-slate-400 uppercase tracking-wider font-sans font-bold">Grounded SQL:</div>
                <div className="text-cyan-300">{chatResponse.sql}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
