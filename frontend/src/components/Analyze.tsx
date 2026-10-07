import React, { useState, useEffect } from 'react';
import { Upload, Play, CheckCircle, MapPin, AlertCircle, Loader2 } from 'lucide-react';
import { Detection } from '../types';

interface AnalyzeProps {
  onNavigateToMap: () => void;
  onNavigateToWorkOrders: () => void;
}

export const Analyze: React.FC<AnalyzeProps> = ({ onNavigateToMap, onNavigateToWorkOrders }) => {
  const [file, setFile] = useState<File | null>(null);
  const [confThreshold, setConfThreshold] = useState<number>(0.25);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    let interval: any = null;
    if (isUploading) {
      interval = setInterval(async () => {
        try {
          const res = await fetch('/api/analyze/job-status');
          const data = await res.json();
          setJobStatus(data);
          if (data.completed) {
            setIsUploading(false);
            setSummary(data);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Job status check error', err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isUploading]);

  const handleStartAnalysis = async () => {
    if (!file) return;
    setIsUploading(true);
    setSummary(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('conf_threshold', confThreshold.toString());

    try {
      const res = await fetch('/api/analyze/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'completed') {
        setIsUploading(false);
        setSummary(data);
      }
    } catch (err) {
      console.error('Failed to launch analysis', err);
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Video & Footage Analysis</h2>
        <p className="text-xs text-slate-500">Run YOLOv8 object detection on dashcam video streams or single snapshots.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
              Upload Dashcam Footage
            </label>
            <div className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl p-6 text-center hover:border-amber-500/50 transition-colors cursor-pointer bg-slate-50/50 dark:bg-slate-950/50">
              <input
                type="file"
                accept="video/*,image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer space-y-2 block">
                <Upload className="w-8 h-8 mx-auto text-amber-500" />
                <p className="text-xs font-medium text-slate-700 dark:text-slate-300">
                  {file ? file.name : 'Click to upload video or image'}
                </p>
                <p className="text-[10px] text-slate-400">MP4, AVI, MOV, JPG, PNG (Max 200MB)</p>
              </label>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Confidence Threshold
              </label>
              <span className="text-xs font-bold text-amber-600 dark:text-amber-500">{(confThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="1.0"
              step="0.05"
              value={confThreshold}
              onChange={(e) => setConfThreshold(parseFloat(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>

          <button
            onClick={handleStartAnalysis}
            disabled={!file || isUploading}
            className={`w-full py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center space-x-2 transition-all shadow-sm ${
              !file || isUploading
                ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 cursor-not-allowed'
                : 'bg-amber-500 hover:bg-amber-600 text-white shadow-amber-500/20'
            }`}
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running Inference...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Start Video Analysis</span>
              </>
            )}
          </button>
        </div>

        {/* Live Preview / Status Column */}
        <div className="md:col-span-2 p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between min-h-[350px]">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Analysis Telemetry Preview</h3>
            
            {isUploading && jobStatus ? (
              <div className="space-y-4 my-8">
                <div className="flex items-center justify-between text-xs font-medium text-slate-700 dark:text-slate-300">
                  <span>Progress: {Math.round((jobStatus.progress || 0) * 100)}%</span>
                  <span>FPS: {jobStatus.fps || 0}</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-amber-500 transition-all duration-300"
                    style={{ width: `${(jobStatus.progress || 0) * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-slate-500 text-center">Detections identified: <span className="font-bold text-amber-600 dark:text-amber-500">{jobStatus.detections_count || 0}</span></p>
              </div>
            ) : summary ? (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-800 dark:text-emerald-300 space-y-3 my-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                  <span className="font-bold text-sm">Analysis Pipeline Complete</span>
                </div>
                <p className="text-xs">{summary.message || `Identified ${summary.detections_count || 0} road defect(s).`}</p>
                <div className="flex space-x-3 pt-2">
                  <button
                    onClick={onNavigateToMap}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-semibold flex items-center space-x-1 hover:bg-emerald-700"
                  >
                    <MapPin className="w-3.5 h-3.5" />
                    <span>View on Map</span>
                  </button>
                  <button
                    onClick={onNavigateToWorkOrders}
                    className="px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-slate-800 text-white text-xs font-semibold hover:bg-slate-800"
                  >
                    <span>Create Work Orders</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="border border-slate-100 dark:border-slate-800/80 rounded-xl bg-slate-50/50 dark:bg-slate-950/50 h-[240px] flex items-center justify-center text-slate-400 text-xs">
                Upload video or image footage to preview live inferences.
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Target Hardware: NVIDIA Jetson Orin Edge</span>
            <span>Estimated Severity: 2D Box Area Ratio</span>
          </div>
        </div>
      </div>
    </div>
  );
};
