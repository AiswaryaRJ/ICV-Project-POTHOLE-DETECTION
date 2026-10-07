import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertCircle, CheckCircle2, Clock, Truck, ChevronRight, Eye, MapPin, Image as ImageIcon } from 'lucide-react';
import { Detection, DashboardStats } from '../types';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const createCustomMarker = (severity: string) => {
  const color = severity === 'High' ? '#ef4444' : severity === 'Medium' ? '#f59e0b' : '#10b981';
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.4);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });
};

interface DashboardProps {
  onSelectDetection: (det: Detection) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectDetection }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [resStats, resDets, resChart] = await Promise.all([
        fetch('/api/stats'),
        fetch('/api/detections'),
        fetch('/api/detections/chart')
      ]);
      setStats(await resStats.json());
      setDetections(await resDets.json());
      setChartData(await resChart.json());
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  const centerLat = detections.length > 0 ? detections[0].lat : 37.7749;
  const centerLon = detections.length > 0 ? detections[0].lon : -122.4194;

  return (
    <div className="space-y-6">
      {/* City Dept Header Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 text-white border border-slate-700 shadow-md flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold">🏛️ City Road Operations Dashboard</h2>
          <p className="text-xs text-slate-300 mt-0.5">Real-time citizen defect reports, geospatial verification & dispatch status.</p>
        </div>
        <div className="text-right">
          <span className="text-[11px] bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1 rounded-full font-bold">
            Live Field Telemetry Sync
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Open Incidents</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{loading ? '-' : stats?.open_issues}</p>
          </div>
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-500">
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">High Severity</p>
            <p className="text-2xl font-bold text-rose-600 dark:text-rose-500 mt-1">{loading ? '-' : stats?.high_severity}</p>
          </div>
          <div className="p-3 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-500">
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Dispatched Crews</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-500 mt-1">{loading ? '-' : stats?.dispatched}</p>
          </div>
          <div className="p-3 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-500">
            <Truck className="w-5 h-5" />
          </div>
        </div>

        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Repaired This Week</p>
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-500 mt-1">{loading ? '-' : stats?.repaired_this_week}</p>
          </div>
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-500">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main Map & Frequency Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Map */}
        <div className="lg:col-span-2 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col h-[420px]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-amber-500" />
              <span>City Incident Map & Geotag Verification</span>
            </h3>
            <div className="flex items-center space-x-3 text-xs">
              <span className="flex items-center space-x-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span><span className="text-slate-500">Low</span></span>
              <span className="flex items-center space-x-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span><span className="text-slate-500">Medium</span></span>
              <span className="flex items-center space-x-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span><span className="text-slate-500">High</span></span>
            </div>
          </div>
          <div className="flex-1 w-full rounded-lg overflow-hidden border border-slate-100 dark:border-slate-800">
            <MapContainer center={[centerLat, centerLon]} zoom={13} style={{ width: '100%', height: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {detections.map((det) => (
                <Marker
                  key={det.id}
                  position={[det.lat, det.lon]}
                  icon={createCustomMarker(det.severity)}
                >
                  <Popup>
                    <div className="p-2 text-xs space-y-2 min-w-[180px]">
                      <div className="flex items-center justify-between border-b pb-1">
                        <p className="font-bold text-slate-900">{det.code}</p>
                        <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-700 font-semibold">{det.severity}</span>
                      </div>
                      {det.snapshot_path && (
                        <img src={det.snapshot_path} alt={det.code} className="w-full h-24 object-cover rounded border" />
                      )}
                      <p className="text-slate-600 font-mono text-[10px]">📍 {det.lat.toFixed(5)}, {det.lon.toFixed(5)}</p>
                      <button
                        onClick={() => onSelectDetection(det)}
                        className="w-full mt-1 bg-amber-500 text-white font-bold py-1 px-2 rounded text-[11px] hover:bg-amber-600 flex items-center justify-center space-x-1"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Review Visual & Details</span>
                      </button>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>

        {/* Detections over time chart */}
        <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between h-[420px]">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">Defect Rate & Frequency</h3>
            <p className="text-xs text-slate-500">Trends of citizen & dashcam reports over time</p>
          </div>
          <div className="h-[300px] w-full mt-4">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }} />
                  <Area type="monotone" dataKey="High" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="Medium" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="Low" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No telemetry chart data available.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Incident Review Table with Visual Snapshots & Map Links */}
      <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Incident Review & Inspection Table</h3>
            <p className="text-xs text-slate-500">Review cropped defect snapshots and spatial coordinates before dispatch.</p>
          </div>
          <span className="text-xs text-slate-500 font-semibold">{detections.length} recorded</span>
        </div>

        {detections.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-xs">
            No incidents reported yet. Upload dashcam footage or submit a citizen report to populate data.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-600 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-950 text-slate-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-4 py-2.5">Visual Snapshot</th>
                  <th className="px-4 py-2.5">Incident ID</th>
                  <th className="px-4 py-2.5">Reported Time</th>
                  <th className="px-4 py-2.5">GPS Location</th>
                  <th className="px-4 py-2.5">Confidence</th>
                  <th className="px-4 py-2.5">Severity</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 text-right">Review Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {detections.slice(0, 8).map((det) => (
                  <tr key={det.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-2">
                      {det.snapshot_path ? (
                        <div className="relative group cursor-pointer" onClick={() => onSelectDetection(det)}>
                          <img src={det.snapshot_path} alt={det.code} className="w-14 h-10 object-cover rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm group-hover:opacity-80" />
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 rounded-lg flex items-center justify-center text-white transition-opacity">
                            <Eye className="w-3.5 h-3.5" />
                          </div>
                        </div>
                      ) : (
                        <div className="w-14 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center text-slate-400">
                          <ImageIcon className="w-4 h-4" />
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-900 dark:text-white">{det.code}</td>
                    <td className="px-4 py-3">{new Date(det.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3 font-mono">
                      <span className="inline-flex items-center space-x-1 text-slate-700 dark:text-slate-300">
                        <MapPin className="w-3 h-3 text-amber-500" />
                        <span>{det.lat.toFixed(4)}, {det.lon.toFixed(4)}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3">{(det.confidence * 100).toFixed(0)}%</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full font-medium text-[11px] ${
                        det.severity === 'High' ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400' :
                        det.severity === 'Medium' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' :
                        'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                      }`}>
                        {det.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">
                      <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {det.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => onSelectDetection(det)}
                        className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-500 hover:bg-amber-500/20 font-semibold text-[11px] inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect Review</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
