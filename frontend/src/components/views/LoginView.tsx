import React, { useState } from "react";
import { LogIn, UserPlus, Sparkles, AlertCircle, CheckCircle2, Shield, ArrowRight } from "lucide-react";
import { useAuthStore } from "../../stores/useAuthStore";
import { useAppStore } from "../../stores/useAppStore";

export const LoginView: React.FC = () => {
  const { login, register, error, sessionExpiredMessage, isLoading, clearError, clearSessionExpiredMessage } = useAuthStore();
  const { fetchDatasets } = useAppStore();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    clearSessionExpiredMessage();

    let success = false;
    if (mode === "login") {
      success = await login(email, password);
    } else {
      success = await register(email, password, fullName);
    }

    if (success) {
      await fetchDatasets();
    }
  };

  const handleDemoLogin = async () => {
    clearError();
    clearSessionExpiredMessage();
    setEmail("demo@insightx.ai");
    setPassword("insightx123");
    let success = await login("demo@insightx.ai", "insightx123");
    if (!success) {
      // Fallback for previously seeded database
      success = await login("demo@insightforge.ai", "insightforge123");
    }
    if (success) {
      await fetchDatasets();
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-900 px-4 py-12 relative overflow-hidden font-sans">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-slate-800/90 backdrop-blur-xl border border-slate-700/80 rounded-2xl p-8 shadow-2xl relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 mb-4 shadow-inner">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            InsightX <span className="text-indigo-400">AI</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Autonomous Data Analyst & Grounded Decision Intelligence
          </p>
        </div>

        {/* Session Expired / Status Notice */}
        {sessionExpiredMessage && (
          <div className="mb-6 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-amber-200 text-xs">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{sessionExpiredMessage}</div>
          </div>
        )}

        {/* Error Notice */}
        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-200 text-xs">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{error}</div>
          </div>
        )}

        {/* Mode Toggle Tabs */}
        <div className="flex p-1 bg-slate-900/60 rounded-xl mb-6 border border-slate-700/50">
          <button
            type="button"
            onClick={() => {
              setMode("login");
              clearError();
            }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "login"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("register");
              clearError();
            }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "register"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Alex Rivera"
                className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Work Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@organization.com"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            ) : mode === "login" ? (
              <>
                <LogIn className="w-4 h-4" />
                <span>Sign In to InsightForge</span>
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Create Workspace Account</span>
              </>
            )}
          </button>
        </form>

        {/* Quick Demo Access Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-700" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-slate-800 px-2 text-slate-500 font-semibold tracking-wider">
              Or Instant Demo
            </span>
          </div>
        </div>

        {/* Demo Fast Login Button */}
        <button
          type="button"
          onClick={handleDemoLogin}
          disabled={isLoading}
          className="w-full py-2.5 px-4 bg-slate-900/90 hover:bg-slate-900 border border-slate-700/80 text-slate-200 text-xs font-medium rounded-xl flex items-center justify-between group transition-all"
        >
          <div className="flex items-center gap-2 text-left">
            <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <div className="font-semibold text-white">Demo Lead Analyst</div>
              <div className="text-[11px] text-slate-400">demo@insightforge.ai</div>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-indigo-400 group-hover:translate-x-0.5 transition-transform text-xs font-semibold">
            <span>Fast Sign In</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </button>

        {/* Security badge footer */}
        <div className="mt-8 pt-4 border-t border-slate-700/50 text-center">
          <p className="text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            <span>256-bit JWT Protected &bull; Private by Default &bull; Role-Governed</span>
          </p>
        </div>
      </div>
    </div>
  );
};
