import React, { useState, useEffect } from 'react';
import CompareResults from './CompareResults';
import InlineShortCodeEditor from './InlineShortCodeEditor';

const DesktopScanner = ({ initialFolder, onDisplayFolder }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [backendUrl, setBackendUrl] = useState('');
  const [compareMode, setCompareMode] = useState(false);
  const [comparisons, setComparisons] = useState([]);
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [lastKnownType, setLastKnownType] = useState(null);
  const [autoFallbackEnabled, setAutoFallbackEnabled] = useState(false);

  // Grid density: low=3, medium=4, high=5 (default high per demo)
  const [density, setDensity] = useState('high');
  const gridColsClass = density === 'high'
    ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5'
    : density === 'low'
    ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3'
    : 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4';

  // Load backend URL and settings from config
  useEffect(() => {
    const loadConfig = async () => {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url || '');
      const enabled = await window.electronAPI.getConfig('autoFallbackEnabled');
      setAutoFallbackEnabled(!!enabled);
    };
    loadConfig();
  }, []);

  // Auto load and process when initialFolder is provided (for folder tabs)
  useEffect(() => {
    const autoLoad = async () => {
      if (initialFolder) {
        const res = await window.electronAPI.listFilesInFolder(initialFolder);
        if (res.success) {
          const files = res.files.map(path => ({
            path,
            name: path.split(/[\\\/]/).pop(),
            processed: false,
            result: null
          }));
          setSelectedFiles(files);
          await handleProcessFiles(false);
        }
      }
    };
    autoLoad();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialFolder]);

  const handleSelectFiles = async () => {
    try {
      const filePaths = await window.electronAPI.selectFiles();
      if (filePaths && filePaths.length > 0) {
        const files = filePaths.map(path => ({
          path,
          name: path.split(/[\\\/]/).pop(),
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

  const loadFolderLocally = async (folderPath) => {
    const res = await window.electronAPI.listFilesInFolder(folderPath);
    if (res.success) {
      const files = res.files.map(path => ({
        path,
        name: path.split(/[\\\/]/).pop(),
        processed: false,
        result: null
      }));
      setSelectedFiles(files);
      setResults([]);
    } else {
      alert('Không đọc được thư mục: ' + res.error);
    }
  };

  const handleSelectFolder = async () => {
    try {
      const folderPath = await window.electronAPI.selectFolder();
      if (folderPath) {
        if (onDisplayFolder) {
          onDisplayFolder(folderPath);
        } else {
          await loadFolderLocally(folderPath);
        }
      }
    } catch (error) {
      console.error('Error selecting folder:', error);
      alert('Lỗi khi chọn thư mục: ' + error.message);
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
        method: 'cloud_boost_failed',
        errorType: 'CONFIG'
      };
    }

    try {
      const result = await window.electronAPI.processDocumentCloud(file.path);
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message,
        method: 'cloud_boost_failed',
        errorType: 'OTHER'
      };
    }
  };

  const applySequentialNaming = (result, lastType) => {
    if (result.success && (result.short_code === 'UNKNOWN' || result.confidence < 0.3) && lastType) {
      return {
        ...result,
        doc_type: lastType.doc_type,
        short_code: lastType.short_code,
        confidence: lastType.confidence * 0.9,
        original_confidence: result.confidence,
        applied_sequential_logic: true,
        note: `Trang tiếp theo của ${lastType.short_code}`
      };
    }
    return result;
  };

  const handleProcessFiles = async (useCloudBoost = false) => {
    let filesToProcess = selectedFiles;
    if (!filesToProcess || filesToProcess.length === 0) {
      const filePaths = await window.electronAPI.selectFiles();
      if (filePaths && filePaths.length > 0) {
        filesToProcess = filePaths.map(path => ({
          path,
          name: path.split(/[\\\/]/).pop(),
          processed: false,
          result: null
        }));
        setSelectedFiles(filesToProcess);
      } else {
        return;
      }
    }

    setProcessing(true);
    setResults([]);
    setComparisons([]);
    setProgress({ current: 0, total: filesToProcess.length });
    setLastKnownType(null);

    const newResults = [];
    let currentLastKnown = null;

    for (let i = 0; i < filesToProcess.length; i++) {
      const file = filesToProcess[i];
      setProgress({ current: i + 1, total: filesToProcess.length });

      let result;
      if (useCloudBoost) {
        result = await processCloudBoost(file);
        if (!result.success && autoFallbackEnabled && ['TIMEOUT','UNAUTHORIZED','QUOTA','SERVER','NETWORK','CONFIG','OTHER'].includes(result.errorType || 'OTHER')) {
          const userConfirmed = window.confirm(`Cloud lỗi: ${result.error || result.errorType}. Bạn có muốn chuyển sang Offline (Tesseract) cho file "${file.name}" không?`);
          if (userConfirmed) {
            result = await processOffline(file);
          }
        }
      } else {
        result = await processOffline(file);
      }

      const processedResult = applySequentialNaming(result, currentLastKnown);

      if (processedResult.success && processedResult.short_code !== 'UNKNOWN' && processedResult.confidence >= 0.3) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
      }

      // Build preview (prefer data URL for Windows)
      let previewUrl = null;
      try {
        const toFileUrl = (p) => {
          if (/^[A-Za-z]:\\\\/.test(p)) {
            return 'file:///' + p.replace(/\\\\/g, '/');
          }
          return 'file://' + p;
        };
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(file.name)) {
          previewUrl = await window.electronAPI.readImageDataUrl(file.path);
          if (!previewUrl) previewUrl = toFileUrl(file.path);
        } else if (/\.pdf$/i.test(file.name)) {
          previewUrl = null;
        }
      } catch {}

      newResults.push({
        fileName: file.name,
        filePath: file.path,
        previewUrl,
        isPdf: /\.pdf$/i.test(file.name),
        ...processedResult
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
    setProgress({ current: 0, total: selectedFiles.length * 2 });
    setLastKnownType(null);

    const newComparisons = [];
    let offlineLastKnown = null;
    let cloudLastKnown = null;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];

      setProgress({ current: i * 2 + 1, total: selectedFiles.length * 2 });
      let offlineResult = await processOffline(file);
      offlineResult = applySequentialNaming(offlineResult, offlineLastKnown);
      if (offlineResult.success && offlineResult.short_code !== 'UNKNOWN' && offlineResult.confidence >= 0.3) {
        offlineLastKnown = {
          doc_type: offlineResult.doc_type,
          short_code: offlineResult.short_code,
          confidence: offlineResult.confidence
        };
      }

      setProgress({ current: i * 2 + 2, total: selectedFiles.length * 2 });
      let cloudResult = await processCloudBoost(file);
      cloudResult = applySequentialNaming(cloudResult, cloudLastKnown);
      if (cloudResult.success && cloudResult.short_code !== 'UNKNOWN' && cloudResult.confidence >= 0.3) {
        cloudLastKnown = {
          doc_type: cloudResult.doc_type,
          short_code: cloudResult.short_code,
          confidence: cloudResult.confidence
        };
      }

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
          <button
            onClick={async () => {
              const folderPaths = await window.electronAPI.selectFolders();
              if (folderPaths && folderPaths.length) {
                folderPaths.forEach(fp => onDisplayFolder && onDisplayFolder(fp));
              }
            }}
            disabled={processing}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span>🗂️</span>
            <span>Chọn nhiều thư mục</span>
          </button>
        </div>
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
                  <h3 className="font-semibold text-gray-900 mb-1">Offline OCR + Rules</h3>
                  <p className="text-sm text-gray-600 mb-2">Xử lý hoàn toàn offline, không tốn chi phí</p>
                  {autoFallbackEnabled && (
                    <p className="text-xs text-purple-700 mt-2">Auto‑fallback: BẬT (sẽ hỏi xác nhận nếu Cloud lỗi)</p>
                  )}
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
                  <h3 className="font-semibold text-gray-900 mb-1">Cloud Boost (GPT-4)</h3>
                  <p className="text-sm text-gray-600 mb-2">Sử dụng AI để độ chính xác cao hơn</p>
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
                    <p className="text-xs text-red-600 mt-2">Cần cấu hình Backend URL trong Cài đặt</p>
                  )}
                </div>
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Processing Progress */}
      {processing && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="processing-indicator">⚙️</div>
            <span className="text-gray-700 font-medium">Đang xử lý... ({progress.current}/{progress.total})</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${(progress.current / progress.total) * 100}%` }} />
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold text-gray-900">Kết quả ({results.length} tài liệu)</h2>
            <div className="flex items-center gap-3">
              {/* Density switch */}
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-600">Mật độ:</label>
                <select value={density} onChange={(e) => setDensity(e.target.value)} className="text-xs border rounded px-2 py-1">
                  <option value="high">Cao (5 cột)</option>
                  <option value="medium">Trung bình (4 cột)</option>
                  <option value="low">Thấp (3 cột)</option>
                </select>
              </div>

              <button
                onClick={async () => {
                  const payload = results
                    .filter(r => r.success && r.short_code)
                    .map(r => ({ filePath: r.filePath, short_code: r.short_code }));
                  if (payload.length === 0) {
                    alert('Không có trang hợp lệ để gộp.');
                    return;
                  }
                  const merged = await window.electronAPI.mergeByShortCode(payload, { autoSave: true });
                  const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
                  alert(`Đã xử lý gộp theo short_code và lưu tự động. Thành công: ${okCount}/${(merged || []).length}.`);
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                📚 Gộp thành PDF theo short_code (toàn batch)
              </button>
            </div>
          </div>

          {/* Grid view */}
          <div className={`grid gap-3 ${gridColsClass}`}>
            {results.map((result, idx) => (
              <div key={idx} className="p-3 border rounded-lg bg-white">
                <div className="mb-2">
                  {result.previewUrl ? (
                    <img src={result.previewUrl} alt={result.fileName} className="w-full h-40 object-contain border rounded bg-gray-50" />
                  ) : (
                    <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">
                      {result.isPdf ? 'PDF (không có preview)' : 'Không có preview'}
                    </div>
                  )}
                </div>
                <div className="text-sm font-medium truncate" title={result.fileName}>{result.fileName}</div>
                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                  {getMethodBadge(result.method)}
                  <span className="ml-auto font-semibold">{(result.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  <div>Loại: {result.doc_type} | Mã: <span className="text-blue-600">{result.short_code}</span></div>
                </div>

                {/* Inline short_code rename (not filesystem) */}
                <div className="mt-2 p-2 bg-gray-50 border rounded">
                  <InlineShortCodeEditor
                    value={result.short_code}
                    onChange={(newCode) => {
                      setResults(prev => prev.map((r, i) => i === idx ? { ...r, short_code: newCode } : r));
                    }}
                  />
                </div>

                {result.previewUrl && (
                  <button onClick={() => setSelectedPreview(result.previewUrl)} className="mt-2 w-full text-xs text-blue-600 hover:underline">
                    Phóng to ảnh
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {selectedPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="relative bg-white p-2 rounded shadow-lg max-w-5xl max-h-[90vh]">
            <button onClick={() => setSelectedPreview(null)} className="absolute -top-10 right-0 text-white text-2xl">✕</button>
        {selectedFiles.length > 0 && (
          <div className="mt-3">
            <div className="inline-flex items-center bg-gray-100 border border-gray-200 rounded-full px-3 py-1 text-xs text-gray-700">
              <span className="mr-1">📦</span>
              <span>Đã chọn {selectedFiles.length} file</span>
            </div>
            <details className="mt-2 text-xs text-gray-600">
              <summary className="cursor-pointer select-none text-gray-700 hover:text-gray-900">Xem danh sách</summary>
              <div className="mt-1 max-h-28 overflow-auto bg-white border rounded p-2">
                {selectedFiles.map((f, i) => (
                  <div key={i} className="truncate">• {f.name}</div>
                ))}
              </div>
            </details>
          </div>
        )}

            <img src={selectedPreview} alt="preview" className="max-w-[90vw] max-h-[85vh] object-contain" />
          </div>
        </div>
      )}

      {/* Comparison Results */}
      {comparisons.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">⚖️ So Sánh Kết Quả ({comparisons.length} tài liệu)</h2>
          <div className="space-y-4">
            {comparisons.map((comparison, idx) => (
              <CompareResults key={idx} offlineResult={comparison.offline} cloudResult={comparison.cloud} fileName={comparison.fileName} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DesktopScanner;
