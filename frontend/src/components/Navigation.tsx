import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  AlertTriangle, 
  Kanban, 
  Settings as SettingsIcon, 
  Moon, 
  Sun, 
  ShieldCheck, 
  ShieldAlert,
  UserCheck,
  Building2
} from 'lucide-react';
import { Settings } from '../types';

interface TopBarProps {
  settings: Settings | null;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  userRole: 'citizen' | 'admin';
  setUserRole: (role: 'citizen' | 'admin') => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  settings,
  darkMode,
  setDarkMode,
  userRole,
  setUserRole
}) => {
  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center text-white font-bold text-lg shadow-sm">
          R
        </div>
        <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight">RoadSense</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 font-medium">
          {userRole === 'citizen' ? 'Citizen Incident Reporter' : 'Municipal Control Hub'}
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {/* Role Switcher Toggle */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
          <button
            onClick={() => setUserRole('citizen')}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              userRole === 'citizen'
                ? 'bg-amber-500 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Citizen Portal</span>
          </button>

          <button
            onClick={() => setUserRole('admin')}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              userRole === 'admin'
                ? 'bg-slate-900 dark:bg-slate-950 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>City Dept Hub</span>
          </button>
        </div>

        {/* Model Engine Status */}
        <div className="hidden sm:flex items-center space-x-2 text-xs font-medium px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
          {settings?.model_loaded ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span className="text-slate-700 dark:text-slate-300">YOLOv8 Engine Ready</span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              <ShieldAlert className="w-4 h-4 text-amber-500" />
              <span className="text-slate-700 dark:text-slate-300">YOLOv8 Fallback</span>
            </>
          )}
        </div>

        {/* Dark Mode */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Toggle Dark/Light Mode"
        >
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};

export const Sidebar: React.FC<{ activeTab: string; setActiveTab: (tab: string) => void; userRole: 'citizen' | 'admin' }> = ({
  activeTab,
  setActiveTab,
  userRole
}) => {
  const citizenItems = [
    { id: 'analyze', label: 'Report Defect / Dashcam', icon: UploadCloud },
    { id: 'dashboard', label: 'Public Road Health Map', icon: LayoutDashboard },
    { id: 'issues', label: 'My Reported Incidents', icon: AlertTriangle },
  ];

  const adminItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analyze', label: 'Analyze Footage', icon: UploadCloud },
    { id: 'issues', label: 'Incidents & Telemetry', icon: AlertTriangle },
    { id: 'workorders', label: 'Municipal Work Orders', icon: Kanban },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  const menuItems = userRole === 'citizen' ? citizenItems : adminItems;

  return (
    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between p-4 sticky top-14 h-[calc(100vh-3.5rem)] transition-colors">
      <nav className="space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
          {userRole === 'citizen' ? 'Citizen Navigation' : 'Municipal Operator Menu'}
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all ${
                isActive
                  ? 'bg-amber-500 text-white shadow-sm font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
        <p className="font-semibold text-slate-700 dark:text-slate-300 mb-0.5">
          {userRole === 'citizen' ? '🚘 Citizen Portal' : '🏛️ City Dept Node'}
        </p>
        <p>{userRole === 'citizen' ? 'Fast Action Pothole Dispatch' : 'Active Node: Sector 4 Response'}</p>
      </div>
    </aside>
  );
};
