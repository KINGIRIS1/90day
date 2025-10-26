import React, { useState, useEffect } from 'react';
import './App.css';
import DesktopScanner from './components/DesktopScanner';
import Settings from './components/Settings';

function App() {
import { useMemo } from 'react';

  const [activeTab, setActiveTab] = useState('scanner');
  const [folders, setFolders] = useState([]); // multi-folder tabs

  const [isElectron, setIsElectron] = useState(false);

  useEffect(() => {
    // Check if running in Electron
    setIsElectron(window.electronAPI?.isElectron || false);
  }, []);

  if (!isElectron) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">⚠️ Lỗi</h1>
          <p className="text-gray-700 mb-4">
            Ứng dụng này chỉ chạy được trong môi trường Electron Desktop.
          </p>
          <p className="text-sm text-gray-500">
            Vui lòng sử dụng file thực thi (.exe, .dmg, .AppImage) để chạy ứng dụng.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src="/brand-icon.png" alt="90dayChonThanh" className="w-10 h-10 rounded-lg object-cover" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">90dayChonThanh</h1>
                <p className="text-xs text-gray-500">Desktop App - Offline First</p>
              </div>
            </div>
            
            {/* Tab Navigation */}
            <nav className="flex space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('scanner')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'scanner'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📄 Quét tài liệu
              </button>
              {folders.map((f, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveTab(`folder-${idx}`)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === `folder-${idx}`
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  title={f}
                >
                  📁 {idx+1}
                </button>
              ))}
              <button
                onClick={() => setActiveTab('settings')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'settings'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ⚙️ Cài đặt
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'scanner' && (
          <DesktopScanner
            onDisplayFolder={(folderPath) => {
              setFolders(prev => prev.includes(folderPath) ? prev : [...prev, folderPath]);
              setActiveTab(`folder-${folders.length}`);
            }}
          />
        )}
        {folders.map((f, idx) => (
          activeTab === `folder-${idx}` && (
            <DesktopScanner key={f}
              initialFolder={f}
              onDisplayFolder={(folderPath) => {
                setFolders(prev => prev.includes(folderPath) ? prev : [...prev, folderPath]);
                setActiveTab(`folder-${folders.length}`);
              }}
            />
          )
        ))}
        {activeTab === 'settings' && <Settings />}
      </main>
    </div>
  );
}

export default App;
