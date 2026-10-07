import React, { useState, useEffect } from 'react';
import { Settings as SettingsType } from '../types';
import { ShieldCheck, ShieldAlert, Trash2, Database, MapPin } from 'lucide-react';

interface SettingsProps {
  settings: SettingsType | null;
  onSettingsUpdated: () => void;
}

export const SettingsView: React.FC<SettingsProps> = ({ settings, onSettingsUpdated }) => {
  const [modelPath, setModelPath] = useState(settings?.model_path || 'models/best.pt');
  const [conf, setConf] = useState(settings?.default_conf || 0.25);
  const [inputSize, setInputSize] = useState(settings?.input_size || 640);
  const [gpsMode, setGpsMode] = useState(settings?.gps_mode || 'Simulated');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  useEffect(() => {
    if (settings) {
      setModelPath(settings.model_path);
      setConf(settings.default_conf);
      setInputSize(settings.input_size);
      setGpsMode(settings.gps_mode);
    }
  }, [settings]);

  const handleSaveSettings = async () => {
    try {
      await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_path: modelPath,
          default_conf: conf,
          input_size: inputSize,
          gps_mode: gpsMode
        })
      });
      onSettingsUpdated();
    } catch (err) {
      console.error('Failed to save settings', err);
    }
  };

  const handleClearData = async () => {
    try {
      await fetch('/api/data/clear', { method: 'DELETE' });
      setShowClearConfirm(false);
      onSettingsUpdated();
    } catch (err) {
      console.error('Failed to clear data', err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Platform Settings</h2>
        <p className="text-xs text-slate-500">Configure YOLOv8 model inference engine, telemetry GPS sources, and database options.</p>
      </div>

      {/* Model Engine Configuration */}
      <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
          <span>YOLOv8 Inference Engine</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Model Weights Path</label>
            <input
              type="text"
              value={modelPath}
              onChange={(e) => setModelPath(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-xs font-mono text-slate-900 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Input Dimension (Pixels)</label>
            <input
              type="number"
              value={inputSize}
              onChange={(e) => setInputSize(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-xs text-slate-900 dark:text-white"
            />
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            {settings?.model_loaded ? (
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-amber-500" />
            )}
            <span className="text-slate-700 dark:text-slate-300 font-medium">
              {settings?.model_loaded ? 'Model file verified and loaded.' : 'Using standard YOLOv8 fallback weights (best.pt not found).'}
            </span>
          </div>
        </div>
      </div>

      {/* GPS Source Configuration */}
      <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
          <MapPin className="w-4 h-4 text-amber-500" />
          <span>Telemetry & GPS Source</span>
        </h3>

        <div className="space-y-3">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="radio"
              name="gps"
              value="Simulated"
              checked={gpsMode === 'Simulated'}
              onChange={() => setGpsMode('Simulated')}
              className="text-amber-500 focus:ring-amber-500"
            />
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
              Demo Simulation Mode (Appends visible "Simulated GPS" tag to detections)
            </span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="radio"
              name="gps"
              value="Custom CSV"
              checked={gpsMode === 'Custom CSV'}
              onChange={() => setGpsMode('Custom CSV')}
              className="text-amber-500 focus:ring-amber-500"
            />
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
              Real Hardware Telemetry Log (Upload CSV override with timestamp, lat, lon)
            </span>
          </label>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveSettings}
          className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs shadow-sm transition-all"
        >
          Save Platform Settings
        </button>
      </div>

      {/* Database Management */}
      <div className="p-5 rounded-xl border border-rose-200 dark:border-rose-900/30 bg-rose-500/5 space-y-4 mt-8">
        <h3 className="text-sm font-semibold text-rose-600 dark:text-rose-400 flex items-center space-x-2">
          <Database className="w-4 h-4" />
          <span>Clear Database Records</span>
        </h3>
        <p className="text-xs text-slate-500">Permanently remove all recorded detections and work order logs.</p>
        
        {showClearConfirm ? (
          <div className="flex items-center space-x-3 pt-2">
            <button
              onClick={handleClearData}
              className="px-3.5 py-1.5 rounded-lg bg-rose-600 text-white text-xs font-semibold hover:bg-rose-700"
            >
              Yes, Clear All Data
            </button>
            <button
              onClick={() => setShowClearConfirm(false)}
              className="px-3.5 py-1.5 rounded-lg bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowClearConfirm(true)}
            className="px-4 py-2 rounded-xl bg-rose-500/10 text-rose-600 border border-rose-500/20 text-xs font-semibold hover:bg-rose-500/20 transition-all"
          >
            Clear Demo Data
          </button>
        )}
      </div>
    </div>
  );
};
