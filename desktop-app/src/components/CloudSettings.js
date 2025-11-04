import React, { useState, useEffect } from 'react';

function CloudSettings() {
  const [ocrEngine, setOcrEngine] = useState('offline-tesseract');
  const [googleKey, setGoogleKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [azureKey, setAzureKey] = useState('');
  const [azureEndpoint, setAzureEndpoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [testingKey, setTestingKey] = useState(null);
  const [showGoogleGuide, setShowGoogleGuide] = useState(false);
  const [showGeminiGuide, setShowGeminiGuide] = useState(false);
  const [showAzureGuide, setShowAzureGuide] = useState(false);
  
  // Image resize settings
  const [enableResize, setEnableResize] = useState(true);
  const [maxWidth, setMaxWidth] = useState(2000);
  const [maxHeight, setMaxHeight] = useState(2800);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const backendEngine = await window.electronAPI.getConfig('ocrEngine') || 'tesseract';
      
      // Map backend values to UI values
      const uiEngineMapping = {
        'tesseract': 'offline-tesseract',
        'easyocr': 'offline-easyocr',
        'vietocr': 'offline-vietocr',
        'google': 'google',
        'azure': 'azure',
        'gemini-flash': 'gemini-flash',
        'gemini-flash-lite': 'gemini-flash-lite'
      };
      
      const uiEngine = uiEngineMapping[backendEngine] || 'offline-tesseract';
      
      const google = await window.electronAPI.getApiKey('google') || '';
      const gemini = await window.electronAPI.getApiKey('gemini') || '';
      const azure = await window.electronAPI.getApiKey('azure') || '';
      const azureEp = await window.electronAPI.getApiKey('azureEndpoint') || '';
      
      // Load resize settings
      const resizeEnabled = await window.electronAPI.getConfig('enableResize');
      const resizeMaxWidth = await window.electronAPI.getConfig('maxWidth');
      const resizeMaxHeight = await window.electronAPI.getConfig('maxHeight');
      
      setOcrEngine(uiEngine);
      setGoogleKey(google);
      setGeminiKey(gemini);
      setAzureKey(azure);
      setAzureEndpoint(azureEp);
      
      // Set resize settings with defaults
      setEnableResize(resizeEnabled !== null ? resizeEnabled : true);
      setMaxWidth(resizeMaxWidth || 2000);
      setMaxHeight(resizeMaxHeight || 2800);
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      // Map UI values to backend values
      const engineMapping = {
        'offline-tesseract': 'tesseract',
        'offline-easyocr': 'easyocr',
        'offline-vietocr': 'vietocr',
        'google': 'google',
        'azure': 'azure',
        'gemini-flash': 'gemini-flash',
        'gemini-flash-lite': 'gemini-flash-lite'
      };
      
      const backendEngine = engineMapping[ocrEngine] || 'tesseract';
      
      // Save OCR engine preference
      await window.electronAPI.setConfig('ocrEngine', backendEngine);

      // Save API keys if provided
      if (ocrEngine === 'google' && googleKey.trim()) {
        await window.electronAPI.saveApiKey({ provider: 'google', apiKey: googleKey.trim() });
      }
      if ((ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-lite') && geminiKey.trim()) {
        await window.electronAPI.saveApiKey({ provider: 'gemini', apiKey: geminiKey.trim() });
      }
      if (ocrEngine === 'azure' && azureKey.trim() && azureEndpoint.trim()) {
        await window.electronAPI.saveApiKey({ provider: 'azure', apiKey: azureKey.trim() });
        await window.electronAPI.saveApiKey({ provider: 'azureEndpoint', apiKey: azureEndpoint.trim() });
      }
      
      // Save resize settings
      await window.electronAPI.setConfig('enableResize', enableResize);
      await window.electronAPI.setConfig('maxWidth', maxWidth);
      await window.electronAPI.setConfig('maxHeight', maxHeight);

      alert('✅ Đã lưu cài đặt thành công!');
    } catch (error) {
      alert('❌ Lỗi khi lưu: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTestKey = async (provider) => {
    setTestingKey(provider);
    try {
      let key, endpoint;
      
      if (provider === 'google') {
        key = googleKey;
      } else if (provider === 'gemini') {
        key = geminiKey;
      } else if (provider === 'azure') {
        key = azureKey;
        endpoint = azureEndpoint;
      }
      
      if (!key || !key.trim()) {
        alert('⚠️ Vui lòng nhập API key trước khi test!');
        return;
      }

      const result = await window.electronAPI.testApiKey({ provider, apiKey: key, endpoint });
      
      if (result.success) {
        alert(`✅ API key hợp lệ!\n\n${result.message || 'Test thành công'}`);
      } else {
        alert(`❌ API key không hợp lệ!\n\nLỗi: ${result.error}`);
      }
    } catch (error) {
      alert('❌ Lỗi khi test API key: ' + error.message);
    } finally {
      setTestingKey(null);
    }
  };

  const handleDeleteKey = async (provider) => {
    if (window.confirm(`⚠️ Xác nhận xóa ${provider.toUpperCase()} API key?`)) {
      try {
        await window.electronAPI.deleteApiKey(provider);
        
        if (provider === 'google') {
          setGoogleKey('');
        } else if (provider === 'gemini') {
          setGeminiKey('');
        } else if (provider === 'azure') {
          setAzureKey('');
          setAzureEndpoint('');
        }
        
        alert('✅ Đã xóa API key!');
      } catch (error) {
        alert('❌ Lỗi khi xóa: ' + error.message);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">⚙️ Cài đặt Cloud OCR</h1>
      <p className="text-gray-600 mb-6">Cấu hình OCR engine và API keys</p>

      {/* OCR Engine Selection */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">📡 Chọn OCR Engine</h2>
        
        <div className="space-y-3">
          {/* Offline Tesseract */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
            <input
              type="radio"
              name="ocrEngine"
              value="offline-tesseract"
              checked={ocrEngine === 'offline-tesseract'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium">⚡ Tesseract OCR (Offline)</div>
              <div className="text-sm text-gray-600 mt-1">
                • Miễn phí, không cần internet<br />
                • Accuracy: 75-85%<br />
                • Tốc độ: Trung bình<br />
                • Không cần API key
              </div>
            </div>
          </label>

          {/* Offline EasyOCR */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
            <input
              type="radio"
              name="ocrEngine"
              value="offline-easyocr"
              checked={ocrEngine === 'offline-easyocr'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium">⚡ EasyOCR (Offline)</div>
              <div className="text-sm text-gray-600 mt-1">
                • Miễn phí, không cần internet<br />
                • Accuracy: 88-92%<br />
                • Tốc độ: Trung bình (7-8s)<br />
                • Không cần API key
              </div>
            </div>
          </label>

          {/* Offline VietOCR */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
            <input
              type="radio"
              name="ocrEngine"
              value="offline-vietocr"
              checked={ocrEngine === 'offline-vietocr'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium">⚡ VietOCR (Offline) ⭐ Best for Vietnamese</div>
              <div className="text-sm text-gray-600 mt-1">
                • Miễn phí, không cần internet<br />
                • Accuracy: 90-95%<br />
                • Tốc độ: Nhanh (1-2s)<br />
                • Chuyên tiếng Việt, cần cài đặt riêng
              </div>
            </div>
          </label>

          {/* Google Cloud Vision */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition border-blue-200">
            <input
              type="radio"
              name="ocrEngine"
              value="google"
              checked={ocrEngine === 'google'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium">☁️ Google Cloud Vision (Cloud)</div>
              <div className="text-sm text-gray-600 mt-1">
                • <strong>Accuracy cao nhất: 90-95%</strong><br />
                • Tốc độ: Rất nhanh (1-2s)<br />
                • Free tier: 1,000 requests/tháng<br />
                • Sau đó: $1.50/1,000 requests<br />
                • ⚠️ Cần API key riêng của bạn
              </div>
            </div>
          </label>

          {/* Azure Vision */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-green-50 transition border-green-200">
            <input
              type="radio"
              name="ocrEngine"
              value="azure"
              checked={ocrEngine === 'azure'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium">☁️ Azure Computer Vision (Cloud)</div>
              <div className="text-sm text-gray-600 mt-1">
                • Accuracy: 92-96%<br />
                • Tốc độ: Rất nhanh (1-2s)<br />
                • Free tier: 5,000 requests/tháng<br />
                • Sau đó: $1.00/1,000 requests<br />
                • ⚠️ Cần API key + endpoint riêng của bạn
              </div>
            </div>
          </label>

          {/* Gemini Flash 2.5 - AI Classification */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-purple-50 transition border-purple-200">
            <input
              type="radio"
              name="ocrEngine"
              value="gemini-flash"
              checked={ocrEngine === 'gemini-flash'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium flex items-center gap-2">
                <span>🤖 Gemini 2.5 Flash (AI Classification)</span>
                <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded">ACCURACY CAO</span>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                • <strong>AI reasoning - Hiểu context</strong><br />
                • <strong>Accuracy: 93-97%</strong> (AI classification trực tiếp)<br />
                • Tốc độ: Rất nhanh (1-2s)<br />
                • Chi phí: $0.30/1M input + $2.50/1M output tokens<br />
                • Free tier: Có (monthly limits)<br />
                • ⚠️ Cần Google API key (BYOK)
              </div>
            </div>
          </label>

          {/* Gemini Flash 2.5 Lite - AI Classification (Faster & Cheaper) */}
          <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-green-50 transition border-green-200">
            <input
              type="radio"
              name="ocrEngine"
              value="gemini-flash-lite"
              checked={ocrEngine === 'gemini-flash-lite'}
              onChange={(e) => setOcrEngine(e.target.value)}
              className="mt-1 mr-3"
            />
            <div className="flex-1">
              <div className="font-medium flex items-center gap-2">
                <span>⚡ Gemini 2.5 Flash Lite (AI Classification)</span>
                <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">RẺ NHẤT - NHANH NHẤT</span>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                • <strong>AI reasoning - Hiểu context</strong><br />
                • Accuracy: 90-95% (vẫn tốt cho documents rõ ràng)<br />
                • <strong>Tốc độ: CỰC NHANH (0.5-1s) ⚡</strong><br />
                • <strong>Chi phí: $0.10/1M input + $0.40/1M output tokens</strong><br />
                • 💰 <strong>TIẾT KIỆM 3x input, 6.3x output so với Flash</strong><br />
                • Free tier: Có (monthly limits)<br />
                • ⚠️ Cần Google API key (BYOK)
              </div>
            </div>
          </label>
        </div>
      </div>

      {/* Google Cloud Vision Setup */}
      {ocrEngine === 'google' && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>🔑</span> Google Cloud Vision API Key
          </h2>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">API Key:</label>
            <input
              type="password"
              value={googleKey}
              onChange={(e) => setGoogleKey(e.target.value)}
              placeholder="AIzaSyD...your_google_api_key_here..."
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
          </div>

          <div className="flex gap-3 mb-4">
            <button
              onClick={() => handleTestKey('google')}
              disabled={testingKey === 'google'}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {testingKey === 'google' ? '⏳ Đang test...' : '🧪 Test API Key'}
            </button>
            {googleKey && (
              <button
                onClick={() => handleDeleteKey('google')}
                className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
              >
                🗑️ Xóa Key
              </button>
            )}
            <button
              onClick={() => setShowGoogleGuide(!showGoogleGuide)}
              className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200 transition"
            >
              {showGoogleGuide ? '▲ Ẩn hướng dẫn' : '▼ Xem hướng dẫn'}
            </button>
          </div>

          {showGoogleGuide && (
            <div className="bg-white rounded p-4 text-sm">
              <p className="font-medium mb-2">📖 Hướng dẫn lấy Google Cloud Vision API Key:</p>
              <ol className="list-decimal ml-5 space-y-2">
                <li>Truy cập <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Cloud Console</a></li>
                <li>Đăng nhập với Google account (hoặc tạo account mới)</li>
                <li>Tạo project mới: Click "Select a project" → "New Project"</li>
                <li>Enable Cloud Vision API:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Vào "APIs & Services" → "Library"</li>
                    <li>Tìm "Cloud Vision API"</li>
                    <li>Click "Enable"</li>
                  </ul>
                </li>
                <li>Tạo API key:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Vào "APIs & Services" → "Credentials"</li>
                    <li>Click "Create Credentials" → "API key"</li>
                    <li>Copy API key</li>
                  </ul>
                </li>
                <li>Paste API key vào ô trên</li>
                <li>Click "Test API Key" để verify</li>
              </ol>
              <p className="mt-3 text-gray-600">
                💡 <strong>Free tier:</strong> 1,000 requests/tháng miễn phí<br />
                💰 <strong>Sau đó:</strong> $1.50 per 1,000 requests
              </p>
            </div>
          )}
        </div>
      )}

      {/* Azure Vision Setup */}
      {ocrEngine === 'azure' && (
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>🔑</span> Azure Computer Vision API
          </h2>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">API Key:</label>
            <input
              type="password"
              value={azureKey}
              onChange={(e) => setAzureKey(e.target.value)}
              placeholder="your_azure_api_key_here..."
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Endpoint URL:</label>
            <input
              type="text"
              value={azureEndpoint}
              onChange={(e) => setAzureEndpoint(e.target.value)}
              placeholder="https://your-resource-name.cognitiveservices.azure.com/"
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
          </div>

          <div className="flex gap-3 mb-4">
            <button
              onClick={() => handleTestKey('azure')}
              disabled={testingKey === 'azure'}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition"
            >
              {testingKey === 'azure' ? '⏳ Đang test...' : '🧪 Test API Key'}
            </button>
            {azureKey && (
              <button
                onClick={() => handleDeleteKey('azure')}
                className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
              >
                🗑️ Xóa Key
              </button>
            )}
            <button
              onClick={() => setShowAzureGuide(!showAzureGuide)}
              className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200 transition"
            >
              {showAzureGuide ? '▲ Ẩn hướng dẫn' : '▼ Xem hướng dẫn'}
            </button>
          </div>

          {showAzureGuide && (
            <div className="bg-white rounded p-4 text-sm">
              <p className="font-medium mb-2">📖 Hướng dẫn lấy Azure Computer Vision API:</p>
              <ol className="list-decimal ml-5 space-y-2">
                <li>Truy cập <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Azure Portal</a></li>
                <li>Đăng nhập với Microsoft account (hoặc tạo account mới)</li>
                <li>Tạo Computer Vision resource:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Click "Create a resource"</li>
                    <li>Tìm "Computer Vision"</li>
                    <li>Click "Create"</li>
                    <li>Chọn subscription, resource group, region</li>
                    <li>Chọn pricing tier: "Free F0" (5,000 calls/month)</li>
                  </ul>
                </li>
                <li>Sau khi tạo xong, vào resource</li>
                <li>Copy API Key và Endpoint:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Vào "Keys and Endpoint"</li>
                    <li>Copy "KEY 1" hoặc "KEY 2"</li>
                    <li>Copy "Endpoint"</li>
                  </ul>
                </li>
                <li>Paste vào các ô trên</li>
                <li>Click "Test API Key" để verify</li>
              </ol>
              <p className="mt-3 text-gray-600">
                💡 <strong>Free tier:</strong> 5,000 requests/tháng miễn phí<br />
                💰 <strong>Sau đó:</strong> $1.00 per 1,000 requests
              </p>
            </div>
          )}
        </div>
      )}

      {/* Gemini Flash Setup */}
      {(ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-lite') && (
        <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>🤖</span> Gemini {ocrEngine === 'gemini-flash-lite' ? '2.5 Flash Lite' : '2.5 Flash'} API Key
            <span className={`text-white text-xs px-2 py-1 rounded ml-2 ${ocrEngine === 'gemini-flash-lite' ? 'bg-green-600' : 'bg-purple-600'}`}>
              {ocrEngine === 'gemini-flash-lite' ? 'RẺ NHẤT - NHANH NHẤT' : 'ACCURACY CAO'}
            </span>
          </h2>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Google API Key:</label>
            <input
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSyD...your_google_api_key_here..."
              className="w-full border rounded px-3 py-2 font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">
              💡 Dùng chung Google API key (cùng key với Google Cloud Vision)
            </p>
          </div>

          <div className="flex gap-3 mb-4">
            <button
              onClick={() => handleTestKey('gemini')}
              disabled={testingKey === 'gemini'}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 transition"
            >
              {testingKey === 'gemini' ? '⏳ Đang test...' : '🧪 Test API Key'}
            </button>
            {geminiKey && (
              <button
                onClick={() => handleDeleteKey('gemini')}
                className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
              >
                🗑️ Xóa Key
              </button>
            )}
            <button
              onClick={() => setShowGeminiGuide(!showGeminiGuide)}
              className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200 transition"
            >
              {showGeminiGuide ? '▲ Ẩn hướng dẫn' : '▼ Xem hướng dẫn'}
            </button>
          </div>

          {showGeminiGuide && (
            <div className="bg-white rounded p-4 text-sm">
              <h3 className="font-semibold mb-2">📖 Hướng dẫn lấy Google API Key:</h3>
              <ol className="list-decimal ml-5 space-y-2">
                <li>Truy cập <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Cloud Console</a></li>
                <li>Tạo project mới (nếu chưa có):
                  <ul className="list-disc ml-5 mt-1">
                    <li>Click "Select a project" → "New Project"</li>
                    <li>Tên: "Vietnamese-OCR-App"</li>
                  </ul>
                </li>
                <li>Enable Gemini API:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Vào: APIs & Services → Library</li>
                    <li>Search: "Generative Language API"</li>
                    <li>Click "Enable"</li>
                  </ul>
                </li>
                <li>Tạo API Key:
                  <ul className="list-disc ml-5 mt-1">
                    <li>Vào: APIs & Services → Credentials</li>
                    <li>Click "Create Credentials" → "API Key"</li>
                    <li>Copy key (dạng: AIzaSyABC...xyz123)</li>
                  </ul>
                </li>
                <li>Paste vào ô trên</li>
                <li>Click "Test API Key" để verify</li>
              </ol>
              <div className="mt-4 p-3 bg-purple-100 rounded">
                <p className="font-semibold mb-2">💰 Chi phí Gemini {ocrEngine === 'gemini-flash-lite' ? 'Flash Lite' : 'Flash'}:</p>
                {ocrEngine === 'gemini-flash-lite' ? (
                  <ul className="space-y-1 text-sm">
                    <li>✅ <strong>Free tier: 1,500 requests/ngày (45,000/tháng)</strong></li>
                    <li>💵 Input: $0.10 per 1M tokens | Output: $0.40 per 1M tokens</li>
                    <li>⚡ <strong>Tốc độ: 0.5-1s (NHANH NHẤT)</strong></li>
                    <li>🎯 Tiết kiệm 3x input, 6.3x output so với Flash thường</li>
                  </ul>
                ) : (
                  <ul className="space-y-1 text-sm">
                    <li>✅ <strong>Free tier: 1,500 requests/ngày (45,000/tháng)</strong></li>
                    <li>💵 Input: $0.30 per 1M tokens | Output: $2.50 per 1M tokens</li>
                    <li>🎯 <strong>Accuracy cao nhất: 93-97%</strong></li>
                    <li>⚡ Tốc độ: 1-2s</li>
                  </ul>
                )}
                
                <div className="mt-3 pt-3 border-t border-purple-200">
                  <p className="font-semibold text-sm mb-2">📊 Bảng so sánh chi phí 1 trang:</p>
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-purple-200">
                        <th className="text-left py-1">Kích thước ảnh</th>
                        <th className="text-right py-1">+ Resize</th>
                        <th className="text-right py-1">Không resize</th>
                        <th className="text-right py-1">Tiết kiệm</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ocrEngine === 'gemini-flash-lite' ? (
                        <>
                          <tr className="border-b border-purple-100">
                            <td className="py-1">2500x3500</td>
                            <td className="text-right font-semibold text-green-700">$0.00093</td>
                            <td className="text-right opacity-60">$0.00135</td>
                            <td className="text-right text-green-600">31%</td>
                          </tr>
                          <tr className="border-b border-purple-100 bg-purple-50">
                            <td className="py-1"><strong>3000x4000 ⭐</strong></td>
                            <td className="text-right font-bold text-green-700">$0.00089</td>
                            <td className="text-right opacity-60">$0.00178</td>
                            <td className="text-right font-semibold text-green-600">50%</td>
                          </tr>
                          <tr>
                            <td className="py-1">4000x5600</td>
                            <td className="text-right font-semibold text-green-700">$0.00093</td>
                            <td className="text-right opacity-60">$0.00320</td>
                            <td className="text-right text-green-600">71%</td>
                          </tr>
                        </>
                      ) : (
                        <>
                          <tr className="border-b border-purple-100">
                            <td className="py-1">2500x3500</td>
                            <td className="text-right font-semibold text-green-700">$0.0042</td>
                            <td className="text-right opacity-60">$0.0054</td>
                            <td className="text-right text-green-600">23%</td>
                          </tr>
                          <tr className="border-b border-purple-100 bg-purple-50">
                            <td className="py-1"><strong>3000x4000 ⭐</strong></td>
                            <td className="text-right font-bold text-green-700">$0.0041</td>
                            <td className="text-right opacity-60">$0.0067</td>
                            <td className="text-right font-semibold text-green-600">40%</td>
                          </tr>
                          <tr>
                            <td className="py-1">4000x5600</td>
                            <td className="text-right font-semibold text-green-700">$0.0042</td>
                            <td className="text-right opacity-60">$0.0109</td>
                            <td className="text-right text-green-600">62%</td>
                          </tr>
                        </>
                      )}
                    </tbody>
                  </table>
                  <p className="text-xs text-gray-600 mt-2">
                    ⭐ <strong>3000x4000</strong> = Kích thước scan điển hình (A4, 300 DPI)
                  </p>
                </div>
              </div>
              <div className="mt-3 p-3 bg-blue-50 rounded">
                <p className="font-semibold mb-2">🤖 Ưu điểm AI Classification:</p>
                <ul className="space-y-1 text-sm">
                  <li>✅ Hiểu context (quốc huy, layout, màu sắc)</li>
                  <li>✅ Không cần rules phức tạp</li>
                  <li>✅ Accuracy: 93-97%</li>
                  <li>✅ Direct classification từ image</li>
                  <li>✅ Returns reasoning (giải thích tại sao)</li>
                </ul>
                
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <p className="font-semibold text-sm mb-2">💼 Chi phí khối lượng lớn (scan 3000x4000):</p>
                  <div className="space-y-2">
                    {ocrEngine === 'gemini-flash-lite' ? (
                      <>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs">100 trang + resize:</span>
                          <span className="text-xs font-semibold text-green-700">~$0.089 (~89₫)</span>
                        </div>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs font-bold">1,000 trang + resize:</span>
                          <span className="text-xs font-bold text-green-700">~$0.89 (~890₫)</span>
                        </div>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs">10,000 trang + resize:</span>
                          <span className="text-xs font-semibold text-green-700">~$8.90 (~8,900₫)</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs">100 trang + resize:</span>
                          <span className="text-xs font-semibold text-green-700">~$0.41 (~410₫)</span>
                        </div>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs font-bold">1,000 trang + resize:</span>
                          <span className="text-xs font-bold text-green-700">~$4.10 (~4,100₫)</span>
                        </div>
                        <div className="flex justify-between p-2 bg-white rounded">
                          <span className="text-xs">10,000 trang + resize:</span>
                          <span className="text-xs font-semibold text-green-700">~$41 (~41,000₫)</span>
                        </div>
                      </>
                    )}
                    <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-xs">
                      <p className="font-semibold mb-1">💡 Free Tier Limits:</p>
                      <ul className="space-y-1 ml-3">
                        <li>• <strong>1,500 requests/ngày</strong> (reset 0:00 UTC = 7:00 AM VN)</li>
                        <li>• <strong>~60 requests/phút</strong> (rate limit)</li>
                        <li>• <strong>45,000 requests/tháng</strong> miễn phí!</li>
                      </ul>
                      <p className="mt-2 text-yellow-700">
                        ⚠️ Nếu vượt quota → Chuyển sang OCR Offline hoặc đợi reset!
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Image Resize Settings - Only for Gemini engines */}
      {(ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-lite') && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <span>💰</span> Tối ưu hóa chi phí Gemini
            <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">TIẾT KIỆM 50-70%</span>
          </h2>
          
          <div className="mb-4">
            <label className="flex items-center gap-3 p-4 bg-white rounded-lg border-2 cursor-pointer hover:bg-gray-50 transition">
              <input
                type="checkbox"
                checked={enableResize}
                onChange={(e) => setEnableResize(e.target.checked)}
                className="w-5 h-5"
              />
              <div>
                <div className="font-medium">🖼️ Tự động resize ảnh trước khi gửi lên Gemini API</div>
                <div className="text-sm text-gray-600 mt-1">
                  Giảm kích thước ảnh để tiết kiệm input tokens mà vẫn giữ độ chính xác OCR
                </div>
              </div>
            </label>
          </div>

          {enableResize && (
            <div className="bg-white rounded-lg p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    🔸 Chiều rộng tối đa (pixels):
                  </label>
                  <input
                    type="number"
                    value={maxWidth}
                    onChange={(e) => setMaxWidth(parseInt(e.target.value) || 2000)}
                    min="800"
                    max="4000"
                    step="100"
                    className="w-full border rounded px-3 py-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Khuyến nghị: 1500-2500 pixels
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    🔹 Chiều cao tối đa (pixels):
                  </label>
                  <input
                    type="number"
                    value={maxHeight}
                    onChange={(e) => setMaxHeight(parseInt(e.target.value) || 2800)}
                    min="1000"
                    max="5000"
                    step="100"
                    className="w-full border rounded px-3 py-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Khuyến nghị: 2000-3500 pixels
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 rounded p-3 text-sm">
                <p className="font-semibold mb-2">💡 Cách hoạt động:</p>
                <ul className="space-y-1">
                  <li>• Nếu ảnh nhỏ hơn {maxWidth}x{maxHeight} → Giữ nguyên kích thước</li>
                  <li>• Nếu ảnh lớn hơn → Tự động resize xuống (giữ tỷ lệ khung hình)</li>
                  <li>• Chất lượng JPEG: 85% (balance giữa size và quality)</li>
                  <li>• Ảnh scan thường: 2500x3500px → Resize thành: {maxWidth}x{Math.round(maxWidth * 3500/2500)}px</li>
                </ul>
              </div>

              <div className="bg-green-50 rounded p-3 text-sm">
                <p className="font-semibold mb-2">💰 DỰ TOÁN CHI PHÍ 1 TRANG (scan 3000x4000):</p>
                <div className="space-y-2">
                  {ocrEngine === 'gemini-flash' ? (
                    <>
                      <div className="flex justify-between items-center p-2 bg-white rounded">
                        <span>✅ Flash + Resize ({maxWidth}x{maxHeight}):</span>
                        <span className="font-bold text-green-700">$0.0041 (~4₫)</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-gray-100 rounded opacity-60">
                        <span>❌ Flash (không resize):</span>
                        <span className="font-medium">$0.0067 (~6.7₫)</span>
                      </div>
                      <div className="text-xs text-green-700 font-semibold ml-2">
                        → Tiết kiệm: ~40% ($0.0026/trang)
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between items-center p-2 bg-white rounded">
                        <span>✅ Flash Lite + Resize ({maxWidth}x{maxHeight}):</span>
                        <span className="font-bold text-green-700">$0.00096 (~0.96₫)</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-gray-100 rounded opacity-60">
                        <span>❌ Flash Lite (không resize):</span>
                        <span className="font-medium">$0.00191 (~1.9₫)</span>
                      </div>
                      <div className="text-xs text-green-700 font-semibold ml-2">
                        → Tiết kiệm: ~50% ($0.00095/trang)
                      </div>
                    </>
                  )}
                </div>
                <div className="mt-3 pt-2 border-t border-green-200">
                  <p className="text-xs text-gray-600">
                    📊 <strong>1,000 trang với resize:</strong><br/>
                    • Flash: ~$4.10 (tiết kiệm $2.67 so với không resize)<br/>
                    • Flash Lite: ~$0.96 (tiết kiệm $0.95 so với không resize) 🎉
                  </p>
                </div>
              </div>

              <div className="bg-yellow-50 rounded p-3 text-sm">
                <p className="font-semibold mb-1">⚠️ Lưu ý:</p>
                <p className="text-gray-700">
                  • Với documents rõ ràng, kích thước {maxWidth}x{maxHeight} đủ để OCR chính xác<br />
                  • Nếu documents mờ/nhòe, có thể tăng lên 2500x3500 hoặc tắt resize<br />
                  • Cài đặt này chỉ áp dụng cho Gemini Flash/Flash Lite
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Save Button */}
      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={loading}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
        >
          {loading ? '⏳ Đang lưu...' : '💾 Lưu cài đặt'}
        </button>
        <button
          onClick={() => window.history.back()}
          className="px-8 py-3 bg-gray-200 rounded-lg hover:bg-gray-300 transition font-medium"
        >
          ❌ Hủy
        </button>
      </div>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>ℹ️ Lưu ý:</strong><br />
          • API keys được lưu trữ an toàn (encrypted) trên máy của bạn<br />
          • Mỗi user nên dùng API key riêng để tận dụng free tier<br />
          • Offline OCR hoàn toàn miễn phí, không cần API key<br />
          • Cloud OCR có accuracy cao hơn nhưng cần internet
        </p>
      </div>
    </div>
  );
}

export default CloudSettings;
