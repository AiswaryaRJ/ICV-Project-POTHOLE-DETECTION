import React, { useState, useEffect } from 'react';
import { WorkOrder } from '../types';
import { User, Clock, AlertCircle, Upload, CheckCircle2, DollarSign } from 'lucide-react';

export const WorkOrders: React.FC = () => {
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadingWoId, setUploadingWoId] = useState<number | null>(null);

  useEffect(() => {
    fetchWorkOrders();
  }, []);

  const fetchWorkOrders = async () => {
    try {
      const res = await fetch('/api/work-orders');
      setOrders(await res.json());
    } catch (err) {
      console.error('Failed to fetch work orders', err);
    } finally {
      setLoading(false);
    }
  };

  const columns = ['Reported', 'Dispatched', 'In progress', 'Repaired'];

  const handleStatusChange = async (id: number, newStatus: string) => {
    try {
      await fetch(`/api/work-orders/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchWorkOrders();
    } catch (err) {
      console.error('Status update error', err);
    }
  };

  const handleProofUpload = async (id: number, file: File) => {
    setUploadingWoId(id);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await fetch(`/api/work-orders/${id}/proof`, {
        method: 'POST',
        body: formData
      });
      fetchWorkOrders();
    } catch (err) {
      console.error('Proof upload error', err);
    } finally {
      setUploadingWoId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Municipal Work Orders Kanban & Proof Verification</h2>
          <p className="text-xs text-slate-500">Manage crew assignments, cost estimates, and upload before/after repair proof photos.</p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading Kanban board...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {columns.map((col) => {
            const colOrders = orders.filter(o => o.status === col);
            return (
              <div key={col} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 flex flex-col min-h-[520px]">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold text-xs text-slate-700 dark:text-slate-300 uppercase tracking-wider">{col}</span>
                  <span className="px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-[11px] text-slate-600 dark:text-slate-400 font-bold">{colOrders.length}</span>
                </div>

                <div className="space-y-3 flex-1">
                  {colOrders.length === 0 ? (
                    <div className="h-32 border border-dashed border-slate-200 dark:border-slate-800/80 rounded-lg flex items-center justify-center text-slate-400 text-[11px]">
                      No work orders
                    </div>
                  ) : (
                    colOrders.map((wo) => (
                      <div key={wo.id} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-mono font-semibold text-slate-400">WO-{wo.id}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            wo.priority === 'Urgent' ? 'bg-rose-500 text-white' :
                            wo.priority === 'High' ? 'bg-rose-500/10 text-rose-600' : 'bg-amber-500/10 text-amber-600'
                          }`}>
                            {wo.priority}
                          </span>
                        </div>

                        <p className="text-xs font-semibold text-slate-900 dark:text-white">{wo.title}</p>

                        {/* Repair Proof Display */}
                        {wo.repair_proof_path && (
                          <div className="space-y-1">
                            <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center space-x-1">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Verified Repair Proof Photo:</span>
                            </span>
                            <img src={wo.repair_proof_path} alt="Repair Proof" className="w-full h-24 object-cover rounded-lg border border-emerald-500/30" />
                          </div>
                        )}

                        <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-100 dark:border-slate-800/80 pt-2">
                          <div className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{wo.assignee}</span>
                          </div>
                          <div className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 font-bold">
                            <DollarSign className="w-3 h-3" />
                            <span>Est: ${wo.cost_estimate || 250}</span>
                          </div>
                        </div>

                        {/* Upload Proof Button for In progress / Repaired */}
                        {(col === 'In progress' || col === 'Repaired') && !wo.repair_proof_path && (
                          <div className="pt-1">
                            <label className="cursor-pointer block text-center px-2 py-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-[11px] font-semibold transition-all">
                              <input
                                type="file"
                                accept="image/*"
                                onChange={(e) => {
                                  if (e.target.files?.[0]) handleProofUpload(wo.id, e.target.files[0]);
                                }}
                                className="hidden"
                              />
                              <span className="flex items-center justify-center space-x-1">
                                <Upload className="w-3 h-3" />
                                <span>{uploadingWoId === wo.id ? 'Uploading...' : 'Upload Repair Proof Photo'}</span>
                              </span>
                            </label>
                          </div>
                        )}

                        {/* Status Shift Buttons */}
                        <div className="flex justify-between pt-1 gap-1">
                          {col !== 'Reported' && (
                            <button
                              onClick={() => handleStatusChange(wo.id, columns[columns.indexOf(col) - 1])}
                              className="text-[10px] text-slate-500 hover:text-slate-900 dark:hover:text-white underline"
                            >
                              ← Move Back
                            </button>
                          )}
                          {col !== 'Repaired' && (
                            <button
                              onClick={() => handleStatusChange(wo.id, columns[columns.indexOf(col) + 1])}
                              className="text-[10px] text-amber-600 font-semibold hover:underline ml-auto"
                            >
                              Advance →
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
