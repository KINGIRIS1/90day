import React, { useState, useRef } from 'react';
import axios from 'axios';
import CompareResults from './CompareResults';

const DesktopScanner = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [backendUrl, setBackendUrl] = useState('');
  const [compareMode, setCompareMode] = useState(false);
  const [comparisons, setComparisons] = useState([]);
  
  // Load backend URL from config
  React.useEffect(() => {
    const loadConfig = async () => {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url || '');
    };
    loadConfig();
  }, []);

  const handleSelectFiles = async () => {
    try {
      const filePaths = await window.electronAPI.selectFiles();
      if (filePaths && filePaths.length > 0) {
        const files = filePaths.map(path => ({
          path,
          name: path.split(/[\\/]/).pop(),
          processed: false,
          result: null
        }));
        setSelectedFiles(files);
        setResults([]);
      }
    } catch (error) {
      console.error('Error selecting files:', error);
      alert('Lỗi khi chọn file: ' + error.message);
    }
  };

  const handleSelectFolder = async () => {
    try {
      const folderPath = await window.electronAPI.selectFolder();
      if (folderPath) {
        alert('Tính năng quét thư mục đang được phát triển. Hiện tại vui lòng chọn từng file.');
      }
    } catch (error) {
      console.error('Error selecting folder:', error);
    }
  };

  const processOffline = async (file) => {
    try {
      const result = await window.electronAPI.processDocumentOffline(file.path);
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message,
        method: 'offline_failed'
      };
    }
  };

  const processCloudBoost = async (file) => {
    if (!backendUrl) {
      return {
        success: false,
        error: 'Chưa cấu hình Backend URL. Vui lòng vào phần Cài đặt.',
        method: 'cloud_boost_failed'
      };
    }

    try {
      // Call Electron IPC to process with cloud
      const result = await window.electronAPI.processDocumentCloud(file.path);
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message,
        method: 'cloud_boost_failed'
      };
    }
  };

  const handleProcessFiles = async (useCloudBoost = false) => {
    if (selectedFiles.length === 0) {
      alert('Vui lòng chọn file trước!');
      return;
    }

    setProcessing(true);
    setResults([]);
    setComparisons([]);
    setProgress({ current: 0, total: selectedFiles.length });

    const newResults = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      setProgress({ current: i + 1, total: selectedFiles.length });

      let result;
      if (useCloudBoost) {
        result = await processCloudBoost(file);
      } else {
        result = await processOffline(file);
      }

      newResults.push({
        fileName: file.name,
        filePath: file.path,
        ...result
      });
    }

    setResults(newResults);
    setProcessing(false);
  };

  const handleTestBoth = async () => {
    if (selectedFiles.length === 0) {
      alert('Vui lòng chọn file trước!');
      return;
    }

    if (!backendUrl) {
      alert('Vui lòng cấu hình Backend URL trong Cài đặt trước!');
      return;
    }

    setProcessing(true);
    setResults([]);
    setComparisons([]);
    setCompareMode(true);
    setProgress({ current: 0, total: selectedFiles.length * 2 }); // x2 vì chạy cả 2 modes

    const newComparisons = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      // Process Offline
      setProgress({ current: i * 2 + 1, total: selectedFiles.length * 2 });
      const offlineResult = await processOffline(file);
      
      // Process Cloud Boost
      setProgress({ current: i * 2 + 2, total: selectedFiles.length * 2 });
      const cloudResult = await processCloudBoost(file);
      
      newComparisons.push({
        fileName: file.name,
        filePath: file.path,
        offline: offlineResult,
        cloud: cloudResult
      });
    }

    setComparisons(newComparisons);
    setProcessing(false);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getMethodBadge = (method) => {
    if (method === 'offline_ocr') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          🔵 Offline OCR (FREE)
        </span>
      );
    }
    if (method === 'cloud_boost') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          ☁️ Cloud Boost
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        ⚠️ {method}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* File Selection */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Chọn tài liệu</h2>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleSelectFiles}
            disabled={processing}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span>📁</span>
            <span>Chọn file</span>
          </button>
          <button
            onClick={handleSelectFolder}
            disabled={processing}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span>📂</span>
            <span>Chọn thư mục</span>
          </button>
        </div>

        {selectedFiles.length > 0 && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">
              Đã chọn <span className="font-semibold">{selectedFiles.length}</span> file
            </p>
            <div className="max-h-32 overflow-y-auto space-y-1">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="text-xs text-gray-500 truncate">
                  {file.name}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Processing Options */}
      {selectedFiles.length > 0 && !processing && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Chọn phương thức xử lý</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Offline OCR Option */}
            <button
              onClick={() => handleProcessFiles(false)}
              className="p-6 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-left group"
            >
              <div className="flex items-start space-x-3">
                <div className="text-3xl">🔵</div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Offline OCR + Rules
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Xử lý hoàn toàn offline, không tốn chi phí
                  </p>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center text-green-600">
                      <span className="mr-1">✓</span>
                      <span>Độ chính xác: 85-88%</span>
                    </div>
                    <div className="flex items-center text-green-600">
                      <span className="mr-1">✓</span>
                      <span>Hoàn toàn miễn phí</span>
                    </div>
                    <div className="flex items-center text-green-600">
                      <span className="mr-1">✓</span>
                      <span>Bảo mật: Dữ liệu ở local</span>
                    </div>
                  </div>
                </div>
              </div>
            </button>

            {/* Cloud Boost Option */}
            <button
              onClick={() => handleProcessFiles(true)}
              disabled={!backendUrl}
              className="p-6 border-2 border-purple-200 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all text-left group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-start space-x-3">
                <div className="text-3xl">☁️</div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Cloud Boost (GPT-4)
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Sử dụng AI để độ chính xác cao hơn
                  </p>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center text-purple-600">
                      <span className="mr-1">✓</span>
                      <span>Độ chính xác: 93%+</span>
                    </div>
                    <div className="flex items-center text-orange-600">
                      <span className="mr-1">⚠</span>
                      <span>Có phí (theo API usage)</span>
                    </div>
                    <div className="flex items-center text-orange-600">
                      <span className="mr-1">⚠</span>
                      <span>Cần kết nối internet</span>
                    </div>
                  </div>
                  {!backendUrl && (
                    <p className="text-xs text-red-600 mt-2">
                      Cần cấu hình Backend URL trong Cài đặt
                    </p>
                  )}
                </div>
              </div>
            </button>
          </div>

          {/* Test Both Button */}
          {backendUrl && (
            <div className="mt-4">
              <button
                onClick={handleTestBoth}
                className="w-full p-4 border-2 border-green-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all"
              >
                <div className="flex items-center justify-center space-x-3">
                  <span className="text-2xl">⚖️</span>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">
                      So Sánh Cả Hai Phương Pháp
                    </h3>
                    <p className="text-sm text-gray-600">
                      Test cả Offline và Cloud Boost để so sánh kết quả
                    </p>
                  </div>
                </div>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Processing Progress */}
      {processing && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="processing-indicator">⚙️</div>
            <span className="text-gray-700 font-medium">
              Đang xử lý... ({progress.current}/{progress.total})
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${(progress.current / progress.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Kết quả ({results.length} tài liệu)
          </h2>
          <div className="space-y-4">
            {results.map((result, idx) => (
              <div
                key={idx}
                className="result-card p-4 border rounded-lg"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-1">
                      {result.fileName}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {getMethodBadge(result.method)}
                      {result.accuracy_estimate && (
                        <span className="text-xs text-gray-500">
                          {result.accuracy_estimate}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {result.success ? (
                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-600">Độ tin cậy:</span>
                        <span className="text-sm font-medium">
                          {(result.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full confidence-bar ${getConfidenceColor(result.confidence)}`}
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Loại tài liệu:</span>
                        <p className="font-medium text-gray-900">{result.doc_type}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Mã rút gọn:</span>
                        <p className="font-medium text-blue-600">{result.short_code}</p>
                      </div>
                    </div>

                    {result.recommend_cloud_boost && (
                      <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p className="text-sm text-yellow-800">
                          💡 Độ tin cậy thấp. Khuyến nghị sử dụng <strong>Cloud Boost</strong> để độ chính xác cao hơn.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">
                      ❌ Lỗi: {result.error}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DesktopScanner;
