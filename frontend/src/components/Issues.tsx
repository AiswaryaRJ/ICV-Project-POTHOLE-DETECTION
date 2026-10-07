import React, { useState, useEffect } from 'react';
import { Search, Download, Filter, CheckSquare, XCircle, Truck, ChevronRight } from 'lucide-react';
import { Detection } from '../types';

interface IssuesProps {
  onSelectDetection: (det: Detection) => void;
}

export const Issues: React.FC<IssuesProps> = ({ onSelectDetection }) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDetections();
  }, [search, statusFilter, severityFilter]);

  const fetchDetections = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'All') params.append('status', statusFilter);
      if (severityFilter !== 'All') params.append('severity', severityFilter);
      if (search) params.append('search', search);

      const res = await fetch(`/api/detections?${params.toString()}`);
      setDetections(await res.json());
    } catch (err) {
      console.error('Failed to fetch issues', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(detections.map(d => d.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleSelect = (id: number) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]);
  };

  const handleBulkDispatch = async () => {
    if (selectedIds.length === 0) return;
    try {
      await fetch('/api/detections/bulk-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: selectedIds, status: 'Dispatched' })
      });
      setSelectedIds([]);
      fetchDetections();
    } catch (err) {
      console.error('Bulk update error', err);
    }
  };

  const handleExportCSV = () => {
    window.open('/api/detections/export/csv', '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Road Defect Incidents</h2>
          <p className="text-xs text-slate-500">Filter, inspect, and bulk dispatch geotagged pothole records.</p>
        </div>

        <div className="flex items-center space-x-3">
          {selectedIds.length > 0 && (
            <button
              onClick={handleBulkDispatch}
              className="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-sm transition-all"
            >
              <Truck className="w-3.5 h-3.5" />
              <span>Bulk Dispatch ({selectedIds.length})</span>
            </button>
          )}
          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-xs flex items-center space-x-1.5 shadow-sm transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search ID or defect..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-slate-900 dark:text-white text-xs focus:outline-none focus:border-amber-500"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-slate-700 dark:text-slate-300 text-xs focus:outline-none focus:border-amber-500"
          >
            <option value="All">All Severities</option>
            <option value="Low">Low Severity</option>
            <option value="Medium">Medium Severity</option>
            <option value="High">High Severity</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 text-slate-700 dark:text-slate-300 text-xs focus:outline-none focus:border-amber-500"
          >
            <option value="All">All Statuses</option>
            <option value="Reported">Reported</option>
            <option value="Dispatched">Dispatched</option>
            <option value="In progress">In progress</option>
            <option value="Repaired">Repaired</option>
          </select>
        </div>
      </div>

      {/* Issues Table */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-x-auto">
        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading detection records...</div>
        ) : detections.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">
            No matching pothole issues found.
          </div>
        ) : (
          <table className="w-full text-xs text-left text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-slate-950 text-slate-500 uppercase tracking-wider text-[10px] sticky top-0">
              <tr>
                <th className="p-3 w-8">
                  <input
                    type="checkbox"
                    checked={selectedIds.length === detections.length && detections.length > 0}
                    onChange={handleSelectAll}
                    className="rounded text-amber-500 focus:ring-amber-500"
                  />
                </th>
                <th className="p-3">ID</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Coordinates</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Estimated Severity</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {detections.map((det) => (
                <tr key={det.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                  <td className="p-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(det.id)}
                      onChange={() => handleToggleSelect(det.id)}
                      className="rounded text-amber-500 focus:ring-amber-500"
                    />
                  </td>
                  <td className="p-3 font-semibold text-slate-900 dark:text-white">{det.code}</td>
                  <td className="p-3">{new Date(det.timestamp).toLocaleString()}</td>
                  <td className="p-3 font-mono">{det.lat.toFixed(4)}, {det.lon.toFixed(4)}</td>
                  <td className="p-3">{(det.confidence * 100).toFixed(0)}%</td>
                  <td className="p-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full font-medium text-[11px] ${
                      det.severity === 'High' ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400' :
                      det.severity === 'Medium' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' :
                      'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                    }`}>
                      {det.severity}
                    </span>
                  </td>
                  <td className="p-3 font-medium">
                    <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {det.status}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => onSelectDetection(det)}
                      className="inline-flex items-center space-x-1 text-amber-600 dark:text-amber-500 hover:underline font-semibold"
                    >
                      <span>Drawer</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
