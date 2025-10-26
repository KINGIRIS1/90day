import React, { useState, useEffect } from 'react';

const EnginePreferenceSetting = ({ enginePref: propPref, onChangeEnginePref }) => {
  const [engine, setEngine] = useState('offline'); // 'offline' | 'cloud'
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      const val = await window.electronAPI.getConfig('enginePreference');
      setEngine(val || 'offline');
    })();
  }, []);

  const save = async (val) => {
    setEngine(val);
    await window.electronAPI.setConfig('enginePreference', val);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <label className="inline-flex items-center gap-2 text-sm">
          <input type="radio" name="enginePref" checked={engine === 'offline'} onChange={() => save('offline')} />
          Offline (Tesseract)
        </label>
        <label className="inline-flex items-center gap-2 text-sm">
          <input type="radio" name="enginePref" checked={engine === 'cloud'} onChange={() => save('cloud')} />
          Cloud (GPT‑4)
        </label>
      </div>
      {saved && <div className="text-xs text-green-700">✓ Đã lưu</div>}
    </div>
  );
};


const AutoFallbackSetting = () => {
  const [enabled, setEnabled] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      const val = await window.electronAPI.getConfig('autoFallbackEnabled');
      setEnabled(!!val);
    })();
  }, []);

  const toggle = async () => {
    const newVal = !enabled;
    setEnabled(newVal);
    await window.electronAPI.setConfig('autoFallbackEnabled', newVal);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium text-gray-900">Auto‑fallback to Offline</div>
          <div className="text-sm text-gray-500">Khi Cloud lỗi/hết hạn mức sẽ chuyển sang Tesseract offline</div>
        </div>
        <button
          onClick={toggle}
          className={`px-4 py-2 rounded-lg text-sm ${enabled ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}
        >
          {enabled ? 'Đang BẬT' : 'Đang TẮT'}
        </button>
      </div>
      {saved && (
        <div className="text-xs text-green-700">✓ Đã lưu</div>
      )}
    </div>
  );
};

const Settings = () => {
  const [backendUrl, setBackendUrl] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url || '');
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async () => {
    try {
      await window.electronAPI.setBackendUrl(backendUrl);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Lỗi khi lưu cài đặt: ' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Backend URL Configuration */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Cấu hình Cloud Boost
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Backend URL (cho Cloud Boost)
            </label>
            <input
              type="text"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              placeholder="https://your-backend-url.com/api"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">
              URL của backend server để sử dụng tính năng Cloud Boost (GPT-4)
            </p>
          </div>

          <button
            onClick={handleSave}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            💾 Lưu cài đặt
          </button>

          {saved && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                ✓ Đã lưu cài đặt thành công!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Engine preference setting */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tuỳ chọn Engine toàn cục</h2>
        <EnginePreferenceSetting />
      </div>

      {/* Auto-fallback setting */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Tuỳ chọn Auto‑fallback</h2>
        <AutoFallbackSetting />
      </div>

      {/* App Information */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Thông tin ứng dụng
        </h2>
        
        <div className="space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Phiên bản:</span>
            <span className="font-medium text-gray-900">1.0.0</span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Nền tảng:</span>
            <span className="font-medium text-gray-900">
              {window.electronAPI?.platform || 'Unknown'}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">OCR Engine:</span>
            <span className="font-medium text-gray-900">PaddleOCR 2.7</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-600">Cloud Boost:</span>
            <span className="font-medium text-gray-900">
              {backendUrl ? '✓ Đã cấu hình' : '✗ Chưa cấu hình'}
            </span>
          </div>
        </div>
      </div>

      {/* Usage Guide */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">
          📖 Hướng dẫn sử dụng
        </h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>1. Offline OCR (Mặc định):</strong> Xử lý hoàn toàn trên máy tính của bạn,
            không cần internet, miễn phí, độ chính xác 85-88%.
          </p>
          <p>
            <strong>2. Cloud Boost:</strong> Sử dụng GPT-4 để độ chính xác cao hơn (93%+),
            cần kết nối internet và có phí sử dụng API.
          </p>
          <p className="mt-3 pt-3 border-t border-blue-200">
            <strong>💡 Gợi ý:</strong> Dùng Offline OCR trước, nếu độ tin cậy thấp
            thì dùng Cloud Boost cho các file quan trọng.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Settings;
