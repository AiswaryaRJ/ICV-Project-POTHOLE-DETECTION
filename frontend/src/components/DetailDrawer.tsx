import React from 'react';
import { X, MapPin, Calendar, Shield, AlertTriangle, Truck } from 'lucide-react';
import { Detection } from '../types';

interface DetailDrawerProps {
  detection: Detection | null;
  onClose: () => void;
  onCreateWorkOrder: (det: Detection) => void;
}

export const DetailDrawer: React.FC<DetailDrawerProps> = ({ detection, onClose, onCreateWorkOrder }) => {
  if (!detection) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-xl z-50 flex flex-col justify-between p-6 overflow-y-auto">
      <div className="space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white text-base">{detection.code}</h3>
            <span className="text-xs text-slate-400">Pothole Defect Incident</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Snapshot Image */}
        <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 h-48 flex items-center justify-center">
          {detection.snapshot_path ? (
            <img src={detection.snapshot_path} alt={detection.code} className="w-full h-full object-cover" />
          ) : (
            <div className="text-xs text-slate-400 flex flex-col items-center space-y-1">
              <AlertTriangle className="w-6 h-6 text-amber-500" />
              <span>Cropped snapshot preview</span>
            </div>
          )}
        </div>

        {/* Status Badges */}
        <div className="flex items-center justify-between">
          <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
            detection.severity === 'High' ? 'bg-rose-500/10 text-rose-600' :
            detection.severity === 'Medium' ? 'bg-amber-500/10 text-amber-600' : 'bg-emerald-500/10 text-emerald-600'
          }`}>
            {detection.severity} Severity (Estimated)
          </span>

          {detection.is_simulated_gps && (
            <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 text-[10px] font-semibold">
              Simulated GPS
            </span>
          )}
        </div>

        {/* Details Grid */}
        <div className="space-y-3 text-xs divide-y divide-slate-100 dark:divide-slate-800">
          <div className="pt-2 flex justify-between">
            <span className="text-slate-500">Confidence Rating</span>
            <span className="font-semibold text-slate-900 dark:text-white">{(detection.confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="pt-2 flex justify-between">
            <span className="text-slate-500">Latitude / Longitude</span>
            <span className="font-mono text-slate-900 dark:text-white">{detection.lat.toFixed(5)}, {detection.lon.toFixed(5)}</span>
          </div>
          <div className="pt-2 flex justify-between">
            <span className="text-slate-500">Logged Timestamp</span>
            <span className="text-slate-900 dark:text-white">{new Date(detection.timestamp).toLocaleString()}</span>
          </div>
          <div className="pt-2 flex justify-between">
            <span className="text-slate-500">Dispatch Status</span>
            <span className="font-semibold text-amber-600 dark:text-amber-500">{detection.status}</span>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2">
        <button
          onClick={() => onCreateWorkOrder(detection)}
          className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-sm transition-all"
        >
          <Truck className="w-4 h-4" />
          <span>Create Repair Work Order</span>
        </button>
      </div>
    </div>
  );
};
