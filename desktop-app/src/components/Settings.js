import React, { useState, useEffect } from 'react';

const RequestDelaySetting = () => {
  const [delay, setDelay] = useState(1200); // Default 1.2s
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      const savedDelay = await window.electronAPI.getConfig('requestDelay');
      if (savedDelay !== undefined && savedDelay !== null) {
        setDelay(parseInt(savedDelay));
      }
    })();
  }, []);

  const handleChange = async (newDelay) => {
    setDelay(newDelay);
    await window.electronAPI.setConfig('requestDelay', newDelay);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const requestsPerMinute = Math.floor(60000 / (delay + 1000));

  return (
    <div className="space-y-3">
      <div>
        <div className="font-medium text-gray-900 mb-1">⏱️ Delay giữa các request (tránh Rate Limit)</div>
        <div className="text-sm text-gray-500 mb-3">
          Điều chỉnh delay để tránh vượt giới hạn API (60 requests/phút).
          <br />
          <span className="text-xs text-orange-600">
            ⚠️ Lưu ý: Flash Lite có rate limit thấp hơn Flash, nên dùng delay cao hơn.
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-700">Delay hiện tại:</span>
        <span className="text-sm font-bold text-blue-700">
          {delay}ms = ~{requestsPerMinute} requests/phút
        </span>
      </div>
      
      <input
        type="range"
        min="0"
        max="3000"
        step="100"
        value={delay}
        onChange={(e) => handleChange(parseInt(e.target.value))}
        className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
      />
      
      <div className="flex justify-between text-xs text-gray-500">
        <span>0ms (nhanh nhất)</span>
        <span>1500ms (khuyến nghị)</span>
        <span>3000ms (an toàn nhất)</span>
      </div>
      
      {/* Presets */}
      <div className="flex gap-2 mt-3">
        <button
          onClick={() => handleChange(800)}
          className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-lg"
        >
          Flash (800ms)
        </button>
        <button
          onClick={() => handleChange(1500)}
          className="px-3 py-1 text-xs bg-blue-100 hover:bg-blue-200 rounded-lg"
        >
          Flash Lite (1500ms)
        </button>
        <button
          onClick={() => handleChange(2500)}
          className="px-3 py-1 text-xs bg-green-100 hover:bg-green-200 rounded-lg"
        >
          An toàn (2500ms)
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
  const [ocrEngine, setOcrEngine] = useState('Tesseract OCR');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url || '');
      
      // Load OCR engine from new unified config
      const engineType = await window.electronAPI.getConfig('ocrEngine') || 
                         await window.electronAPI.getConfig('ocrEngineType') || 
                         'tesseract';
      
      const engineMap = {
        'tesseract': 'Tesseract OCR',
        'easyocr': 'EasyOCR',
        'vietocr': 'VietOCR (Transformer)',
        'google': 'Google Cloud Vision',
        'azure': 'Azure Computer Vision'
      };
      
      setOcrEngine(engineMap[engineType] || 'Tesseract OCR');
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

      {/* Request Delay Setting */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Cài đặt Rate Limit
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          <strong>Quan trọng:</strong> Điều chỉnh delay giữa các request để tránh vượt giới hạn API.
          <br />
          Flash Lite có rate limit thấp hơn Flash, khuyến nghị dùng delay cao hơn.
        </p>
        <RequestDelaySetting />
      </div>

      {/* App Information */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">
          Thông tin App
        </h2>
        
        <div className="space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Nền tảng:</span>
            <span className="font-medium text-gray-900">Windows Desktop (Electron)</span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Công ty:</span>
            <span className="font-medium text-gray-900">Nguyen Thin Trung</span>
          </div>
          <div className="flex justify-between py-2 border-b">
            <span className="text-gray-600">Version:</span>
            <span className="font-medium text-gray-900">1.1.0</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-600">OCR Engine:</span>
            <span className="font-medium text-gray-900">{ocrEngine}</span>
          </div>
        </div>
      </div>

      {/* Developer Information */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b">
          👨‍💻 Người Phát Triển
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-2xl font-bold shadow-md">
              NT
            </div>
            <div className="flex-1">
              <h3 className="text-base font-semibold text-gray-900">Nguyen Thin Trung</h3>
              <p className="text-sm text-gray-600 mt-1">Software Developer</p>
              <p className="text-xs text-gray-500 mt-2">
                Phần mềm được phát triển để hỗ trợ số hóa tài liệu đất đai Việt Nam, 
                sử dụng công nghệ AI và OCR tiên tiến.
              </p>
            </div>
          </div>
          
          <div className="pt-3 border-t space-y-2">
            <div className="flex items-center text-sm">
              <span className="text-gray-600 w-24">📧 Email:</span>
              <span className="text-blue-600 font-medium">contact@90daychonthanh.vn</span>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-gray-600 w-24">🌐 Website:</span>
              <span className="text-blue-600 font-medium">www.90daychonthanh.vn</span>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-gray-600 w-24">📱 Hotline:</span>
              <span className="text-gray-900 font-medium">1900-xxxx</span>
            </div>
          </div>
          
          <div className="pt-3 border-t">
            <p className="text-xs text-gray-500 leading-relaxed">
              <strong className="text-gray-700">Lưu ý:</strong> Phần mềm này được bảo vệ bởi luật sở hữu trí tuệ. 
              Nghiêm cấm sao chép, phân phối hoặc sử dụng cho mục đích thương mại 
              mà không có sự cho phép bằng văn bản từ tác giả.
            </p>
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
            <strong>1. OCR Engine:</strong> Chọn công cụ OCR phù hợp:
          </p>
          <ul className="ml-6 space-y-1 list-disc">
            <li><strong>Tesseract:</strong> Nhanh nhất (0.5-1s), đa ngôn ngữ, phù hợp cho bulk processing</li>
            <li><strong>VietOCR:</strong> Cân bằng (1-2s), chuyên tiếng Việt, accuracy 90-95%</li>
            <li><strong>EasyOCR:</strong> Chính xác nhất (7-8s), tốt cho documents quan trọng, accuracy 90-92%</li>
          </ul>
          <p className="mt-3">
            <strong>2. Offline OCR (Mặc định):</strong> Xử lý hoàn toàn trên máy tính của bạn,
            không cần internet, miễn phí.
          </p>
          <p>
            <strong>3. Cloud Boost:</strong> Sử dụng GPT-4 để độ chính xác cao hơn (93%+),
            cần kết nối internet và có phí sử dụng API.
          </p>
          <p className="mt-3 pt-3 border-t border-blue-200">
            <strong>💡 Gợi ý:</strong> Dùng EasyOCR hoặc VietOCR cho daily use, nếu độ tin cậy thấp
            thì dùng Cloud Boost cho các file cực kỳ quan trọng.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Settings;
