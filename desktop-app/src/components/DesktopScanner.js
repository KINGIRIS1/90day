import React, { useState, useRef, useEffect } from 'react';
import CompareResults from './CompareResults';
import InlineShortCodeEditor from './InlineShortCodeEditor';

//
/* Drag-drop removed per user request
const DraggableItem = ({ id, label }) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });
  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
  };
  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes} className={`p-2 border rounded bg-white text-xs ${isDragging ? 'opacity-70' : ''}`}>
      {label}
    </div>
  );
};

const SortableList = ({ items, labels, onReorder }) => {
  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={({ active, over }) => {
      if (!over || active.id === over.id) return;
      const oldIndex = items.indexOf(active.id);
      const newIndex = items.indexOf(over.id);
      onReorder(arrayMove(items, oldIndex, newIndex));
    }}>
      <SortableContext items={items} strategy={verticalListSortingStrategy}>
        <div className="space-y-2">
          {items.map((id) => (
            <DraggableItem key={id} id={id} label={labels[id] || id} />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
};

const ManualOrderPanel = ({ onClose, orderByShortCode, results, onApply, onMerge, onMergeAll }) => {
  // Build labels map from results (filePath -> display label)
  const labels = {};
  results.forEach(r => { labels[r.filePath] = r.fileName; });
  const [localMap, setLocalMap] = useState(orderByShortCode || {});

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white w-[900px] max-h-[90vh] overflow-auto rounded shadow-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">Sắp xếp thứ tự trang theo short_code</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="space-y-6">
          {Object.keys(localMap).length === 0 && (
            <div className="text-sm text-gray-500">Chưa có nhóm short_code nào. Hãy chạy nhận dạng trước.</div>
          )}

          {Object.entries(localMap).map(([shortCode, paths]) => (
            <div key={shortCode} className="border rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium text-gray-800">Nhóm: {shortCode} ({paths.length} trang)</div>
                <div className="space-x-2 text-sm">
                  <button
                    onClick={() => onMerge(shortCode, paths)}
                    className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Gộp nhóm này (auto save)
                  </button>
                </div>
              </div>
              <SortableList
                items={paths}
                labels={labels}
                onReorder={(newOrder) => {
                  setLocalMap(prev => ({ ...prev, [shortCode]: newOrder }));
                }}
              />
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between mt-4">
          <div className="text-xs text-gray-500">Kéo‑thả để thay đổi thứ tự trang trong từng nhóm.</div>
          <div className="space-x-2">
            <button
              onClick={() => onApply(localMap)}
              className="px-3 py-2 bg-gray-200 rounded hover:bg-gray-300"
            >
              Áp dụng thứ tự
            </button>
            <button
              onClick={() => onMergeAll(localMap)}
              className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Gộp tất cả nhóm (auto save)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const RenameInline = ({ oldPath, currentName, onRenamed }) => {
  const [editing, setEditing] = useState(false);
  const [baseName, setBaseName] = useState(currentName.replace(/\.[^/.]+$/, ''));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const onSave = async () => {
    setSaving(true);
    setError('');
    try {
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

const DesktopScanner = ({ initialFolder, onDisplayFolder }) => {
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
  const [orderingOpen, setOrderingOpen] = useState(false);
  const [orderByShortCode, setOrderByShortCode] = useState({}); // { SHORT: [filePath,...] }

  // Load backend URL and settings from config
  useEffect(() => {
    const loadConfig = async () => {
      const url = await window.electronAPI.getBackendUrl();
      setBackendUrl(url || '');
      const enabled = await window.electronAPI.getConfig('autoFallbackEnabled');
      setAutoFallbackEnabled(!!enabled);
    };
    loadConfig();
  // Auto load and process when initialFolder is provided
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
  }, [initialFolder]);

  }, []);

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
    const groupMap = {}; // short_code -> [filePath,...]

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      setProgress({ current: i + 1, total: selectedFiles.length });

      let result;
      if (useCloudBoost) {
        result = await processCloudBoost(file);
        // Fallback if cloud failed and setting enabled
        if (!result.success && autoFallbackEnabled && ['TIMEOUT','UNAUTHORIZED','QUOTA','SERVER','NETWORK','CONFIG','OTHER'].includes(result.errorType || 'OTHER')) {
          const userConfirmed = window.confirm(`Cloud lỗi: ${result.error || result.errorType}. Bạn có muốn chuyển sang Offline (Tesseract) cho file "${file.name}" không?`);
          if (userConfirmed) {
            result = await processOffline(file);
          }
        }
      } else {
        result = await processOffline(file);
      }

      // Apply sequential naming logic
      const processedResult = applySequentialNaming(result, currentLastKnown);

      // Update last known type if valid
      if (processedResult.success && processedResult.short_code !== 'UNKNOWN' && processedResult.confidence >= 0.3) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
      }

      // Build preview for image/pdf
      const displayName = file.name;
      let previewUrl = null;
      try {
        const toFileUrl = (p) => {
          if (/^[A-Za-z]:\\/.test(p)) {
            return 'file:///' + p.replace(/\\/g, '/');
          }
          return 'file://' + p;
        };
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(file.name)) {
          // Try data URL to avoid file protocol/security issues
          previewUrl = await window.electronAPI.readImageDataUrl(file.path);
          if (!previewUrl) {
            previewUrl = toFileUrl(file.path);
          }
        } else if (/\.pdf$/i.test(file.name)) {
          previewUrl = null;
        }
      } catch {}

      // Build order map
      if (processedResult.success && processedResult.short_code) {
        const sc = processedResult.short_code;
        if (!groupMap[sc]) groupMap[sc] = [];
        groupMap[sc].push(file.path);
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
    setOrderByShortCode(groupMap);
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

      // Offline
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

      // Cloud
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
            onClick={async () => {
              const folderPath = await window.electronAPI.selectFolder();
              if (folderPath) {
                if (onDisplayFolder) onDisplayFolder(folderPath);
                else await handleSelectFolder();
              }
            }}
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

        {/* Process Folder Now toggle */}
        {selectedFiles.length > 0 && (
          <div className="mt-3 p-3 bg-gray-50 border rounded">
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
                  {autoFallbackEnabled && (
                    <p className="text-xs text-purple-700 mt-2">
                      Auto‑fallback: BẬT (sẽ hỏi xác nhận nếu Cloud lỗi)
                    </p>
                  )}
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

      {/* Merge and Ordering Controls */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">Kết quả ({results.length} tài liệu)</h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setOrderingOpen(true)}
                className="px-3 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                🧩 Sắp xếp thứ tự thủ công (drag‑drop)
              </button>
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

          <div className="space-y-4">
            {/* Grid view for results */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
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
                    <div><span className="text-gray-500">Loại:</span> {result.doc_type}</div>
                    <div><span className="text-gray-500">Mã:</span> <span className="text-blue-600">{result.short_code}</span></div>
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
        </div>
      )}

      {/* Preview Modal */}
      {selectedPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="relative bg-white p-2 rounded shadow-lg max-w-5xl max-h-[90vh]">
            <button onClick={() => setSelectedPreview(null)} className="absolute -top-10 right-0 text-white text-2xl">✕</button>
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
