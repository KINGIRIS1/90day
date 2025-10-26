import React, { useState, useEffect } from 'react';
import './App.css';
import DesktopScanner from './components/DesktopScanner';
import Settings from './components/Settings';

// Folder tree picker component
const FolderPicker = ({ baseFolder, onConfirm }) => {
  const [open, setOpen] = useState(false);
  const [tree, setTree] = useState(null);
  const [checked, setChecked] = useState({}); // path -> boolean

  const loadTree = async () => {
    if (!baseFolder) return;
    const res = await window.electronAPI.listFolderTree(baseFolder);
    if (res.success) setTree(res.tree);
  };

  useEffect(() => { setOpen(false); setTree(null); setChecked({}); }, [baseFolder]);

  const toggle = (p) => setChecked(prev => ({ ...prev, [p]: !prev[p] }));

  const collectSelected = (node, acc = []) => {
    if (!node) return acc;
    if (checked[node.path]) acc.push(node.path);
    if (node.children) node.children.forEach(c => collectSelected(c, acc));
    return acc;
  };

  const renderNode = (node, level = 0) => {
    if (!node) return null;
    return (
      <div key={node.path} style={{ marginLeft: level * 12 }} className="mb-1">
        <label className="inline-flex items-center gap-2 text-sm">
          <input type="checkbox" checked={!!checked[node.path]} onChange={() => toggle(node.path)} />
          <span title={node.path}>📁 {node.name}</span>
        </label>
        {node.children && node.children.map(child => renderNode(child, level + 1))}
      </div>
    );
  };

  if (!baseFolder) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => { setOpen(!open); if (!tree) loadTree(); }}
        className="px-3 py-2 rounded-md text-sm bg-gray-100 hover:bg-gray-200"
      >
        {open ? 'Ẩn chọn thư mục con' : 'Chọn thư mục con...'}
      </button>
      {open && (
        <div className="mt-2 p-3 border rounded bg-white max-h-80 overflow-auto">
          <div className="text-sm text-gray-600 mb-2">Thư mục gốc: {baseFolder}</div>
          {tree ? renderNode(tree) : <div className="text-sm text-gray-500">Đang tải cây thư mục...</div>}
          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={() => {
                const selected = collectSelected(tree, []);
                onConfirm(selected);
              }}
              className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Thêm vào tab
            </button>
            <button onClick={() => setOpen(false)} className="px-3 py-2 bg-gray-200 rounded text-sm hover:bg-gray-300">Đóng</button>
          </div>
        </div>
      )}
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('scanner');
  const [folders, setFolders] = useState([]); // multi-folder tabs
  const [isElectron, setIsElectron] = useState(false);
  const [enginePref, setEnginePref] = useState('offline'); // 'offline' | 'cloud'

  useEffect(() => {
    // Check if running in Electron or demo mode
    const params = new URLSearchParams(window.location.search);
    const isDemo = params.get('demo') === '1';
    if (isDemo) {
      setIsElectron(true); // enable UI for design demo
      return;
    }
    setIsElectron(window.electronAPI?.isElectron || false);
  }, []);
  useEffect(() => {
    const loadPref = async () => {
      if (!window.electronAPI) return;
      const ep = await window.electronAPI.getConfig('enginePreference');
      setEnginePref(ep || 'offline');
    };
    loadPref();
  }, []);


  const basename = (p) => {
    if (!p) return '';
    const parts = p.split(/[/\\]/);
    return parts[parts.length - 1] || p;
  };

  const addFolderTab = (folderPath) => {
    setFolders(prev => {
      if (prev.includes(folderPath)) return prev;
      const next = [...prev, folderPath];
      setActiveTab(`folder-${next.length - 1}`);
      return next;
    });
  };

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
        <div className="max-w-7xl mx-auto px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src="/brand-icon.png" alt="90dayChonThanh" className="w-8 h-8 rounded-lg object-cover" />
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
                  activeTab === 'scanner' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📄 Quét tài liệu
              </button>
              {folders.map((f, idx) => (
                <div key={idx} className="flex items-center">
                  <button
                    onClick={() => setActiveTab(`folder-${idx}`)}
                    className={`px-3 py-2 rounded-l-md text-sm font-medium transition-colors ${
                      activeTab === `folder-${idx}` ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                    }`}
                    title={f}
                  >
                    📁 {basename(f)}
                  </button>
                  <button
                    onClick={() => {
                      setFolders(prev => prev.filter((_, i) => i !== idx));
                      // Adjust activeTab if removing current tab
                      if (activeTab === `folder-${idx}`) setActiveTab('scanner');
                    }}
                    className={`px-2 py-2 rounded-r-md text-sm ${activeTab === `folder-${idx}` ? 'bg-white' : 'bg-gray-100 hover:bg-gray-200'}`}
                    title="Đóng tab"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                onClick={() => setActiveTab('settings')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'settings' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ⚙️ Cài đặt
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Optional controls for folder tabs */}
      <div className="max-w-7xl mx-auto px-4">
        {activeTab.startsWith('folder-') && (
          <div className="mt-2 flex items-center gap-2">
            <button
              onClick={async () => {
                const idx = parseInt(activeTab.replace('folder-', ''), 10);
                const base = folders[idx];
                if (!base) return;
                const res = await window.electronAPI.listSubfoldersInFolder(base);
                if (res.success && res.folders?.length) {
                  const toAdd = res.folders.filter(fp => !folders.includes(fp));
                  if (toAdd.length) setFolders(prev => [...prev, ...toAdd]);
                }
              }}
              className="px-3 py-2 rounded-md text-sm bg-gray-200 hover:bg-gray-300"
            >
              ➕ Thêm thư mục con (cấp 1)
            </button>
            <FolderPicker
              baseFolder={folders[parseInt(activeTab.replace('folder-', ''), 10)]}
              onConfirm={(selected) => {
                const toAdd = selected.filter(fp => !folders.includes(fp));
                if (toAdd.length) setFolders(prev => [...prev, ...toAdd]);
              }}
            />
          </div>
        )}
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'scanner' && (
          <DesktopScanner
            onDisplayFolder={(folderPath) => addFolderTab(folderPath)}
          />
        )}
        {folders.map((f, idx) => (
          activeTab === `folder-${idx}` && (
            <DesktopScanner
              key={f}
              initialFolder={f}
              onDisplayFolder={(folderPath) => addFolderTab(folderPath)}
            />
          )
        ))}
        {activeTab === 'settings' && <Settings />}
      </main>
    </div>
  );
}

export default App;
