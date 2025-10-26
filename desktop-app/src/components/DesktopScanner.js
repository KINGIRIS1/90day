import React, { useState, useRef } from 'react';
import axios from 'axios';
import CompareResults from './CompareResults';

const RenameInline = ({ oldPath, currentName, onRenamed }) => {
  const [editing, setEditing] = useState(false);
  const [baseName, setBaseName] = useState(currentName.replace(/\.[^/.]+$/, ''));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const onSave = async () => {
    setSaving(true);
    setError('');
    try {
  const [orderingOpen, setOrderingOpen] = useState(false);
  const [orderByShortCode, setOrderByShortCode] = useState({}); // { SHORT: [filePath,...] }

      const res = await window.electronAPI.renameFile(oldPath, baseName);
      if (res.success) {
        const newPathParts = res.newPath.split(/[\\\/]/);
        const newName = newPathParts[newPathParts.length - 1];
        onRenamed(newName, res.newPath);
        setEditing(false);
      } else {
        setError(res.error || 'Đổi tên thất bại');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-2 p-2 border rounded bg-gray-50">
      {!editing ? (
        <button
          onClick={() => setEditing(true)}
          className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
        >
          ✏️ Chỉnh sửa tên
        </button>
      ) : (
        <div className="flex items-center space-x-2">
          <input
            className="px-2 py-1 text-sm border rounded flex-1"
            value={baseName}
            onChange={(e) => setBaseName(e.target.value)}
          />
          <button
            disabled={saving}
            onClick={onSave}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Lưu
          </button>
          <button
            disabled={saving}
            onClick={() => { setEditing(false); setBaseName(currentName.replace(/\.[^/.]+$/, '')); setError(''); }}
            className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
          >
            Hủy
          </button>
        </div>
      )}
      {error && <div className="text-xs text-red-600 mt-1">{error}</div>}
    </div>
  );
};

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
  const [selectedPreview, setSelectedPreview] = useState(null);

  const [lastKnownType, setLastKnownType] = useState(null); // Track last known doc type
  const [autoFallbackEnabled, setAutoFallbackEnabled] = useState(false);
  const [confirmFallbackOpen, setConfirmFallbackOpen] = useState(false);
  const fallbackDecisionRef = useRef(null);

  
  // Load backend URL from config
  React.useEffect(() => {
    const loadConfig = async () => {
    (async () => {
      const enabled = await window.electronAPI.getConfig('autoFallbackEnabled');
      setAutoFallbackEnabled(!!enabled);
    })();
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
      // Build group-by-short_code order map
      if (processedResult.success && processedResult.short_code) {
        setOrderByShortCode(prev => {
          const arr = prev[processedResult.short_code] ? [...prev[processedResult.short_code]] : [];
          arr.push(file.path);
          return { ...prev, [processedResult.short_code]: arr };
        });
      }

        method: 'cloud_boost_failed',
        errorType: 'CONFIG'
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
        method: 'cloud_boost_failed',
        errorType: 'OTHER'
      };
    }
  };

  const applySequentialNaming = (result, lastType) => {
    /**
     * Sequential naming logic:
     * - If result is UNKNOWN/low confidence AND we have a last known type
     * - Use the last known type (continuation of previous document)
     * - Otherwise, use the detected type and update last known
     */
    
    if (result.success && 
        (result.short_code === 'UNKNOWN' || result.confidence < 0.3) && 
        lastType) {
      // Apply last known type
      return {
        ...result,
        doc_type: lastType.doc_type,
        short_code: lastType.short_code,
        confidence: lastType.confidence * 0.9, // Slightly reduce confidence
        original_confidence: result.confidence,
        applied_sequential_logic: true,
        note: `Trang tiếp theo của ${lastType.short_code}`
      };
    }
    
    // Return as-is (will become new last known type if valid)
    return result;
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
    setLastKnownType(null); // Reset at start of new batch

    const newResults = [];
    let currentLastKnown = null;

      // If using Cloud and it failed with common cloud errors, optionally prompt fallback
      if (useCloudBoost && (!result.success) && ['TIMEOUT','UNAUTHORIZED','QUOTA','SERVER','NETWORK','CONFIG','OTHER'].includes(result.errorType || 'OTHER')) {
        if (autoFallbackEnabled) {
      // Build preview for image/pdf
      const displayName = file.name;

      let previewUrl = null;
      try {
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(file.name)) {
          // For local files, Electron renderer can show via file:// path
          previewUrl = `file://${file.path}`;
        } else if (/\.pdf$/i.test(file.name)) {
          // Simple icon/label for PDF; previewing PDF inline would require extra libs
          previewUrl = null; // Keep null, show generic PDF badge
        }
      } catch {}

          // Show confirm dialog if user requested confirmation (C)
          const doConfirm = true; // UI choice C requires a dialog
          if (doConfirm) {
            const userConfirmed = await new Promise((resolve) => {
              const message = `Cloud lỗi: ${result.error || result.errorType}. Bạn có muốn chuyển sang Offline (Tesseract) cho file "${file.name}" không?`;
              const ok = window.confirm(message);
              resolve(ok);
            });
            if (userConfirmed) {
              const offlineResult = await processOffline(file);
              result = offlineResult;
            }
          }
        }
      }

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      setProgress({ current: i + 1, total: selectedFiles.length });

      let result;
      if (useCloudBoost) {
        result = await processCloudBoost(file);
      } else {
        result = await processOffline(file);
      }

      // Apply sequential naming logic
      const processedResult = applySequentialNaming(result, currentLastKnown);
      
      // Update last known type if this result is valid (not UNKNOWN)
      if (processedResult.success && 
          processedResult.short_code !== 'UNKNOWN' && 
          processedResult.confidence >= 0.3) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
        setLastKnownType(currentLastKnown);
      }

      newResults.push({
        fileName: displayName,
        filePath: file.path,
        previewUrl,
        isPdf: /\.pdf$/i.test(displayName),
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
            <div className="mt-2 text-xs text-gray-500">
              Gợi ý: Click vào ảnh để phóng to xem chi tiết.
            </div>

      return;
    }

    setProcessing(true);
    setResults([]);
    setComparisons([]);
    setCompareMode(true);
    setProgress({ current: 0, total: selectedFiles.length * 2 }); // x2 vì chạy cả 2 modes
    setLastKnownType(null); // Reset

    const newComparisons = [];
    let offlineLastKnown = null;
    let cloudLastKnown = null;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      
      // Process Offline
      setProgress({ current: i * 2 + 1, total: selectedFiles.length * 2 });
      let offlineResult = await processOffline(file);
      offlineResult = applySequentialNaming(offlineResult, offlineLastKnown);
      
      // Update offline last known
      if (offlineResult.success && 
          offlineResult.short_code !== 'UNKNOWN' && 
          offlineResult.confidence >= 0.3) {
        offlineLastKnown = {
          doc_type: offlineResult.doc_type,
          short_code: offlineResult.short_code,
          confidence: offlineResult.confidence
        };
      }
      
      // Process Cloud Boost
      setProgress({ current: i * 2 + 2, total: selectedFiles.length * 2 });
      let cloudResult = await processCloudBoost(file);
      cloudResult = applySequentialNaming(cloudResult, cloudLastKnown);
      
      // Update cloud last known
      if (cloudResult.success && 
          cloudResult.short_code !== 'UNKNOWN' && 
          cloudResult.confidence >= 0.3) {
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
            {/* Process Folder Now toggle */}
            {selectedFiles.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 border rounded">
                <label className="inline-flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    onChange={async (e) => {
                      if (e.target.checked) {
                        await handleProcessFiles(false);
                      }
                    }}
                  />
                  <span>Tự động xử lý ngay sau khi chọn thư mục (Process Folder Now)</span>
                </label>
              </div>
            )}
          {/* Open ordering panel */}
          {results.length > 0 && (
            <div className="mb-2 flex items-center gap-2">
              <button
                onClick={() => setOrderingOpen(true)}
                className="px-3 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                🧩 Sắp xếp thứ tự thủ công (drag‑drop)
              </button>
            </div>
          )}


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
          {/* Merge PDF by short_code */}
          {results.length > 0 && (
            <div className="mb-4">
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
          )}

            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span>📁</span>
            <span>Chọn file</span>
                        {/* Zoomable preview */}
                        {result.previewUrl && (
                          <button
                            onClick={() => setSelectedPreview(result.previewUrl)}
                            className="mt-1 text-xs text-blue-600 hover:underline"
                          >
                            Phóng to ảnh
                          </button>
                        )}

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
                  {autoFallbackEnabled && (
                    <p className="text-xs text-purple-700 mt-2">
                      Auto‑fallback: BẬT (sẽ hỏi xác nhận nếu Cloud lỗi)
                    </p>
                  )}

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
                    {/* Preview + rename */}
                    <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 items-start">
                      <div className="md:col-span-1">
                        {result.previewUrl ? (
                          <img src={result.previewUrl} alt={result.fileName} className="w-full max-h-48 object-contain border rounded" />
                        ) : (
                          <div className="w-full h-48 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">
                            {result.isPdf ? 'PDF (không có preview)' : 'Không có preview'}
                          </div>
                        )}
                      </div>
                      <div className="md:col-span-2 space-y-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-600 text-sm">Tên file:</span>
                          <span className="text-sm font-medium break-all">{result.fileName}</span>
                        </div>
                        <RenameInline oldPath={result.filePath} currentName={result.fileName} onRenamed={(newName, newPath)=>{
                          // Update state after rename
                          setResults(prev => prev.map((r, idx2)=> idx2===idx ? { ...r, fileName: newName, filePath: newPath } : r));
                          setSelectedFiles(prev => prev.map((f)=> f.path===result.filePath ? { ...f, name: newName, path: newPath } : f));
                        }} />
                      </div>
                    </div>

                  {!backendUrl && (
      {/* Preview Modal */}
      {selectedPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="relative bg-white p-2 rounded shadow-lg max-w-5xl max-h-[90vh]">
            <button
              onClick={() => setSelectedPreview(null)}
              className="absolute -top-10 right-0 text-white text-2xl"
            >
              ✕
            </button>
            <img src={selectedPreview} alt="preview" className="max-w-[90vw] max-h-[85vh] object-contain" />
          </div>
        </div>
      )}

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

                    {/* OCR Debug View - Collapsible */}
                    {result.original_text && (
                      <details className="mt-3">
                        <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-blue-600 flex items-center">
                          <span className="mr-2">🔍</span>
                          <span>Xem text OCR đã đọc được (Debug)</span>
                        </summary>
                        <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
                          {/* Full Text */}
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">📄 Text đầy đủ:</p>
                            <div className="p-2 bg-white border rounded text-xs text-gray-800 max-h-32 overflow-y-auto">
                              {result.original_text || '(Không có text)'}
                            </div>
                          </div>
                          
                          {/* Title Text */}
                          {result.title_text && (
                            <div>
                              <p className="text-xs font-semibold text-gray-700 mb-1">🎯 Text tiêu đề (chữ to):</p>
                              <div className="p-2 bg-yellow-50 border border-yellow-300 rounded text-xs text-gray-800">
                                {result.title_text}
                              </div>
                            </div>
                          )}
                          
                          {/* Reasoning */}
                          {result.reasoning && (
                            <div>
                              <p className="text-xs font-semibold text-gray-700 mb-1">💡 Lý do phân loại:</p>
                              <div className="p-2 bg-blue-50 border border-blue-300 rounded text-xs text-gray-800">
                                {result.reasoning}
                              </div>
                            </div>
                          )}

                          {/* Font Height Info */}
                          {result.avg_font_height && (
                            <div className="flex items-center text-xs text-gray-600">
                              <span className="mr-2">📏</span>
                              <span>Chiều cao font trung bình: {result.avg_font_height}px</span>
                            </div>
                          )}

                          {/* Title Boost Indicator */}
                          {result.title_boost_applied && (
                            <div className="flex items-center text-xs text-green-700">
                              <span className="mr-2">⭐</span>
                              <span>Title boost đã được áp dụng (+20% confidence)</span>
                            </div>
                          )}
                        </div>
                      </details>
                    )}

                    {result.applied_sequential_logic && (
                      <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-xs text-blue-800 flex items-center">
                          <span className="mr-1">📄</span>
                          <span><strong>Trang tiếp theo:</strong> Tự động nhận dạng là {result.short_code} (kế thừa từ trang trước)</span>
                        </p>
                      </div>
                    )}

                    {result.recommend_cloud_boost && !result.applied_sequential_logic && (
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

      {/* Comparison Results */}
      {comparisons.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            ⚖️ So Sánh Kết Quả ({comparisons.length} tài liệu)
          </h2>
          <div className="space-y-4">
            {comparisons.map((comparison, idx) => (
              <CompareResults
                key={idx}
                offlineResult={comparison.offline}
                cloudResult={comparison.cloud}
                fileName={comparison.fileName}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DesktopScanner;
