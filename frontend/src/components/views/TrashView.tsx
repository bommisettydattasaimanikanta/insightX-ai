import React, { useState, useEffect } from "react";
import {
  Trash2,
  RefreshCw,
  RotateCcw,
  AlertTriangle,
  History,
  ShieldAlert,
  GitBranch,
  Layers,
  CheckCircle
} from "lucide-react";
import { useAppStore } from "../../stores/useAppStore";
import { api } from "../../api/client";

export const TrashView: React.FC = () => {
  const { activeDatasetId, activeDataset, fetchDatasets, selectDataset } = useAppStore();
  
  const [trashedDatasets, setTrashedDatasets] = useState<any[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [confirmNameInput, setConfirmNameInput] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadTrashAndVersions();
  }, [activeDatasetId]);

  const loadTrashAndVersions = async () => {
    try {
      setLoading(true);
      const trashList = await api.getTrash();
      setTrashedDatasets(trashList);

      if (activeDatasetId) {
        const verList = await api.getVersions(activeDatasetId);
        setVersions(verList);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (id: string) => {
    try {
      await api.restoreDataset(id);
      setMessage("Dataset successfully restored from Trash!");
      await fetchDatasets();
      await loadTrashAndVersions();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handlePermanentDelete = async (id: string) => {
    try {
      await api.permanentDelete(id, confirmNameInput);
      setConfirmDeleteId(null);
      setConfirmNameInput("");
      setMessage("Dataset and all underlying Parquet artifacts permanently erased.");
      await fetchDatasets();
      await loadTrashAndVersions();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Trash2 className="w-5 h-5 text-red-500" />
          <span>Trash & Dataset Version Lifecycle</span>
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Non-destructive data management. Trashed datasets are retrievable for 30 days. Permanent delete wipes Parquet lakes, metadata, caches, and ML artifacts.
        </p>
      </div>

      {message && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-500" />
          <span>{message}</span>
        </div>
      )}

      {/* Trashed Datasets Section */}
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider">
          Trash Bin (30-Day Soft Retention)
        </h2>

        {trashedDatasets.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">Trash bin is empty.</p>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-750">
            {trashedDatasets.map((d) => (
              <div key={d.id} className="py-3 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100">{d.name}</h4>
                  <p className="text-[10px] text-slate-400">
                    {d.row_count} rows • Deleted at: {new Date(d.deleted_at).toLocaleString()}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleRestore(d.id)}
                    className="px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 text-xs font-semibold hover:bg-indigo-100 flex items-center gap-1"
                  >
                    <RotateCcw className="w-3.5 h-3.5" /> Restore
                  </button>
                  <button
                    onClick={() => setConfirmDeleteId(d.id)}
                    className="px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-300 text-xs font-semibold hover:bg-red-100"
                  >
                    Delete Permanently
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Permanent Delete Modal */}
      {confirmDeleteId && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-800 border border-red-300 dark:border-red-900 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-bold text-sm">
              <ShieldAlert className="w-5 h-5" />
              <span>Confirm Permanent Deletion</span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-300">
              This action cannot be undone. To prevent accidental data loss, please type the exact dataset name{" "}
              <strong className="text-slate-900 dark:text-white">
                {trashedDatasets.find((d) => d.id === confirmDeleteId)?.name}
              </strong>{" "}
              to confirm.
            </p>
            <input
              type="text"
              value={confirmNameInput}
              onChange={(e) => setConfirmNameInput(e.target.value)}
              placeholder="Type dataset name..."
              className="w-full p-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs font-mono"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs"
              >
                Cancel
              </button>
              <button
                onClick={() => handlePermanentDelete(confirmDeleteId)}
                className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold"
              >
                Permanently Wipe All Data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Version History */}
      {activeDataset && (
        <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-4 h-4 text-indigo-500" />
              <span>Version History: {activeDataset.name}</span>
            </h2>
            <span className="text-[10px] font-mono text-slate-400">Current: v{activeDataset.current_version}</span>
          </div>

          <div className="space-y-3">
            {versions.map((ver) => (
              <div
                key={ver.version_num}
                className={`p-4 rounded-xl border flex items-center justify-between ${
                  ver.version_num === activeDataset.current_version
                    ? "bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-800"
                    : "bg-slate-50 dark:bg-slate-850 border-slate-200 dark:border-slate-700"
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold font-mono text-indigo-600 dark:text-indigo-400">
                      Version {ver.version_num}
                    </span>
                    <span className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                      {ver.change_summary}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1 font-mono">
                    {ver.row_count} rows • {ver.col_count} columns • Quality Score: {ver.quality_score} • {new Date(ver.created_at).toLocaleString()}
                  </div>
                </div>

                {ver.version_num === activeDataset.current_version && (
                  <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-full">
                    Active
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
