import React, { useState, useEffect } from 'react';
import { TopBar, Sidebar } from './components/Navigation';
import { Dashboard } from './components/Dashboard';
import { Analyze } from './components/Analyze';
import { Issues } from './components/Issues';
import { WorkOrders } from './components/WorkOrders';
import { SettingsView } from './components/SettingsView';
import { DetailDrawer } from './components/DetailDrawer';
import { Detection, Settings } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('analyze');
  const [userRole, setUserRole] = useState<'citizen' | 'admin'>('citizen');
  const [darkMode, setDarkMode] = useState<boolean>(true);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/settings');
      setSettings(await res.json());
    } catch (err) {
      console.error('Failed to load settings', err);
    }
  };

  const handleRoleChange = (role: 'citizen' | 'admin') => {
    setUserRole(role);
    if (role === 'citizen') {
      setActiveTab('analyze');
    } else {
      setActiveTab('dashboard');
    }
  };

  const handleCreateWorkOrder = async (det: Detection) => {
    try {
      await fetch('/api/work-orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ detection_id: det.id })
      });
      setSelectedDetection(null);
      setActiveTab('workorders');
    } catch (err) {
      console.error('Failed to create work order', err);
    }
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
        <TopBar
          settings={settings}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          userRole={userRole}
          setUserRole={handleRoleChange}
        />

        <div className="flex">
          <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} userRole={userRole} />

          <main className="flex-1 p-6 overflow-x-hidden">
            {activeTab === 'dashboard' && (
              <Dashboard onSelectDetection={(det) => setSelectedDetection(det)} />
            )}
            {activeTab === 'analyze' && (
              <Analyze
                onNavigateToMap={() => setActiveTab('dashboard')}
                onNavigateToWorkOrders={() => setActiveTab('workorders')}
              />
            )}
            {activeTab === 'issues' && (
              <Issues onSelectDetection={(det) => setSelectedDetection(det)} />
            )}
            {activeTab === 'workorders' && <WorkOrders />}
            {activeTab === 'settings' && (
              <SettingsView settings={settings} onSettingsUpdated={fetchSettings} />
            )}
          </main>
        </div>

        {/* Drawer Slideout */}
        <DetailDrawer
          detection={selectedDetection}
          onClose={() => setSelectedDetection(null)}
          onCreateWorkOrder={handleCreateWorkOrder}
        />
      </div>
    </div>
  );
}

export default App;
