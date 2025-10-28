import React, { useState, useEffect, useRef } from 'react';
import CompareResults from './CompareResults';
import InlineShortCodeEditor from './InlineShortCodeEditor';

const DesktopScanner = ({ initialFolder, onDisplayFolder, enginePref: enginePrefProp }) => {
  // Core selection and results
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  // Cloud & compare
  const [backendUrl, setBackendUrl] = useState('');
  const [compareMode, setCompareMode] = useState(false);
  const [comparisons, setComparisons] = useState([]);

  // UI helpers
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [lastKnownType, setLastKnownType] = useState(null);
  const [autoFallbackEnabled, setAutoFallbackEnabled] = useState(false);
  const [enginePref, setEnginePref] = useState(enginePrefProp || 'offline');

  // Grid density: low=3, medium=4, high=5
  const [density, setDensity] = useState('high');
  const gridColsClass = density === 'high'
    ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5'
    : density === 'low'
      ? 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3'
      : 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4';

  // Parent folder analysis + child tabs
  const [childMergeReport, setChildMergeReport] = useState([]); // lines of saved PDFs across tabs
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeOption, setMergeOption] = useState('root'); // 'root' or 'new'
  const [mergeSuffix, setMergeSuffix] = useState('_merged');

  const [parentFolder, setParentFolder] = useState(null);
  const [parentSummary, setParentSummary] = useState(null); // { subfolderCount, rootFileCount }
  const [childTabs, setChildTabs] = useState([]); // [{ name, path, count, status, results }]
  const [activeChild, setActiveChild] = useState(null);
  const [childScanImagesOnly, setChildScanImagesOnly] = useState(false);
  const stopRef = useRef(false);
  const [isPaused, setIsPaused] = useState(false); // Track pause state
  const [remainingFiles, setRemainingFiles] = useState([]); // Files left to process

  // Load config (guard electron)
  useEffect(() => { if (enginePrefProp) setEnginePref(enginePrefProp); }, [enginePrefProp]);

  useEffect(() => {
    const loadConfig = async () => {
      const api = window.electronAPI;
      if (!api) return;
      const url = await api.getBackendUrl();
      setBackendUrl(url || '');
      const enabled = await api.getConfig('autoFallbackEnabled');
      setAutoFallbackEnabled(!!enabled);
      const ep = await api.getConfig('enginePreference');
      setEnginePref(ep || 'offline');
    };
    try { loadConfig(); } catch {}
  }, []);

  // Auto process initialFolder
  useEffect(() => {
    const autoLoad = async () => {
      if (!initialFolder) return;
      if (!window.electronAPI) return;
      await analyzeAndLoadFolder(initialFolder);
      await handleProcessFiles(false);
    };
    autoLoad();
    // eslint-disable-next-line
  }, [initialFolder]);

  const analyzeAndLoadFolder = async (folderPath) => {
    // Analyze parent and create child tabs + show root files list
    setParentFolder(folderPath);

    // Try fast IPC analyze; if not available, fallback to manual listing
    let analyzed = false;
    try {
      if (window.electronAPI.analyzeParentFolder) {
        const analysis = await window.electronAPI.analyzeParentFolder(folderPath);
        if (analysis && analysis.success) {
          setParentSummary(analysis.summary);
          setChildTabs(analysis.subfolders.map(sf => ({ name: sf.name, path: sf.path, count: sf.fileCount, status: 'pending', results: [] })));
          setActiveChild(analysis.subfolders[0]?.path || null);
          analyzed = true;
        }
      }
    } catch (e) {
      // ignore, will fallback
    }

    if (!analyzed) {
      // Fallback: manual compute summary and child tabs
      try {
        const subs = await window.electronAPI.listSubfoldersInFolder(folderPath);
        const rootFiles = await window.electronAPI.listFilesInFolder(folderPath);
        if (subs && subs.success && rootFiles && rootFiles.success) {
          const subfolders = subs.folders || [];
          const childWithCounts = [];
          for (const sp of subfolders) {
            const lf = await window.electronAPI.listFilesInFolder(sp);
            const count = (lf && lf.success && lf.files) ? lf.files.length : 0;
            childWithCounts.push({ name: sp.split(/[\\\/]/).pop(), path: sp, count, status: 'pending', results: [] });
          }
          setParentSummary({ subfolderCount: childWithCounts.length, rootFileCount: rootFiles.files.length });
          setChildTabs(childWithCounts);
          setActiveChild(childWithCounts[0]?.path || null);
        } else {
          setParentSummary(null);
          setChildTabs([]);
          setActiveChild(null);
        }
      } catch (e) {
        setParentSummary(null);
        setChildTabs([]);
        setActiveChild(null);
      }
    }

    // Load root files list for optional batch processing
    try {
      if (!window.electronAPI) return;
    const res = await window.electronAPI.listFilesInFolder(folderPath);
      if (res && res.success) {
        const files = res.files.map(path => ({
          path,
          name: path.split(/[\\\/]/).pop(),
          processed: false,
          result: null
        }));
        setSelectedFiles(files);
        setResults([]);
      }
    } catch (e) {
      // ignore
    }
  };

  const handleSelectFiles = async () => {
    try {
      if (!window.electronAPI) return;
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
    }
  };

  const handleSelectFolder = async () => {
    try {
      const folderPath = await window.electronAPI.selectFolder();
      if (!folderPath) return;
      await analyzeAndLoadFolder(folderPath);
    } catch (error) {
      console.error('Error selecting folder:', error);
    }
  };

  const processOffline = async (file) => {
    try {
      const result = await window.electronAPI.processDocumentOffline(file.path);
      return result;
    } catch (error) {
      return { success: false, error: error.message, method: 'offline_failed' };
    }
  };

  const processCloudBoost = async (file) => {
    if (!backendUrl) {
      return { success: false, error: 'Chưa cấu hình Backend URL.', method: 'cloud_boost_failed', errorType: 'CONFIG' };
    }
    try {
      const result = await window.electronAPI.processDocumentCloud(file.path);
      return result;
    } catch (error) {
      return { success: false, error: error.message, method: 'cloud_boost_failed', errorType: 'OTHER' };
    }
  };

  const applySequentialNaming = (result, lastType) => {
    // Apply sequential naming if:
    // 1. Current result is UNKNOWN
    // 2. Low confidence (< 0.5) - might be a page without clear title
    // 3. No title detected (indicated by low confidence or missing title_text)
    // This mimics Cloud behavior: if page has no title, use previous short_code
    if (result.success && lastType) {
      const shouldUseSequential = 
        result.short_code === 'UNKNOWN' || 
        result.confidence < 0.5 ||
        (result.title_text && result.title_text.length < 10); // Very short/no title
      
      if (shouldUseSequential) {
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.6, lastType.confidence * 0.9), // Maintain reasonable confidence
          original_confidence: result.confidence,
          applied_sequential_logic: true,
          note: `Trang tiếp theo của ${lastType.short_code} (không có tiêu đề rõ ràng)`
        };
      }
    }
    return result;
  };

  // Progressive file processing (vừa quét vừa hiện)
  const handleProcessFiles = async (useCloudBoost = false, isResume = false) => {
    let filesToProcess = selectedFiles;
    if (!filesToProcess || filesToProcess.length === 0) {
      if (!window.electronAPI) return;
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
    setIsPaused(false); // Reset pause state
    
    // If resuming, use remaining files, otherwise start fresh
    if (!isResume) {
      setResults([]);
      setComparisons([]);
      setProgress({ current: 0, total: filesToProcess.length });
      setLastKnownType(null);
      setRemainingFiles(filesToProcess);
    } else {
      // Resume: use remaining files
      filesToProcess = remainingFiles;
      setProgress({ current: results.length, total: results.length + filesToProcess.length });
    }
    
    stopRef.current = false; // Reset stop flag

    const enginePref = await window.electronAPI.getConfig('enginePreference');

    const newResults = isResume ? [...results] : []; // Keep existing results if resuming
    let currentLastKnown = null;

    for (let i = 0; i < filesToProcess.length; i++) {
      // Check if user clicked stop
      if (stopRef.current) {
        console.log('❌ Scan stopped by user at file', i);
        setRemainingFiles(filesToProcess.slice(i));
        setIsPaused(true);
        setProcessing(false);
        return;
      }
      
      const file = filesToProcess[i];
      setProgress({ current: i + 1, total: filesToProcess.length });

      let result;
      const preferCloud = enginePref === 'cloud';
      if (preferCloud) {
        result = await processCloudBoost(file);
        
        // Check stop after async operation
        if (stopRef.current) {
          console.log('❌ Scan stopped after cloud boost at file', i);
          setRemainingFiles(filesToProcess.slice(i));
          setIsPaused(true);
          setProcessing(false);
          return;
        }
        
        if (!result.success && autoFallbackEnabled && ['TIMEOUT','UNAUTHORIZED','QUOTA','SERVER','NETWORK','CONFIG','OTHER'].includes(result.errorType || 'OTHER')) {
          const userConfirmed = window.confirm(`Cloud lỗi: ${result.error || result.errorType}. Chuyển sang Offline (Tesseract) cho "${file.name}"?`);
          if (userConfirmed) result = await processOffline(file);
        }
      } else {
        result = await processOffline(file);
      }
      
      // Check stop after processing
      if (stopRef.current) {
        console.log('❌ Scan stopped after processing at file', i);
        // Save remaining files for resume
        setRemainingFiles(filesToProcess.slice(i + 1));
        setIsPaused(true);
        setProcessing(false);
        return; // Exit early
      }

      const processedResult = applySequentialNaming(result, currentLastKnown);
      // Update lastKnown if this is a valid, confident result (not sequential)
      if (processedResult.success && 
          processedResult.short_code !== 'UNKNOWN' && 
          processedResult.confidence >= 0.5 &&
          !processedResult.applied_sequential_logic) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
      }

      // Build preview
      let previewUrl = null;
      try {
        const toFileUrl = (p) => (/^[A-Za-z]:\\\\/.test(p) ? 'file:///' + p.replace(/\\\\/g, '/') : 'file://' + p);
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(file.name)) {
          previewUrl = await window.electronAPI.readImageDataUrl(file.path);
          if (!previewUrl) previewUrl = toFileUrl(file.path);
        }
      } catch {}

      newResults.push({
        fileName: file.name,
        filePath: file.path,
        previewUrl,
        isPdf: /\.pdf$/i.test(file.name),
        ...processedResult
      });
      // incremental update
      setResults([...newResults]);
    }

    setProcessing(false);
  };

  // Scan one child folder incrementally
  const scanChildFolder = async (childPath) => {
    const idx = childTabs.findIndex(t => t.path === childPath);
    if (idx < 0) return;
    setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'scanning' } : t));

    const listing = await window.electronAPI.listFilesInFolder(childPath);
    if (!listing.success) {
      setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'pending' } : t));
      return;
    }

    let fileList = listing.files.map(p => ({ path: p, name: p.split(/[\\\/]/).pop() }));
    if (childScanImagesOnly) fileList = fileList.filter(f => /\.(png|jpg|jpeg|gif|bmp)$/i.test(f.name));

    const files = fileList;
    const childResults = [];
    stopRef.current = false;
    
    // Get engine preference from config (respect user settings)
    const enginePref = await window.electronAPI.getConfig('enginePreference');
    const preferCloud = enginePref === 'cloud';
    
    for (let i = 0; i < files.length; i++) {
      if (stopRef.current) {
        console.log('❌ Folder scan stopped at file', i, 'in', childPath);
        break;
      }
      const f = files[i];
      
      // Use engine preference (same as file scan)
      let r;
      if (preferCloud) {
        r = await processCloudBoost(f);
        
        // Check stop after async
        if (stopRef.current) {
          console.log('❌ Folder scan stopped after cloud at file', i);
          break;
        }
        
        if (!r.success && autoFallbackEnabled) {
          r = await processOffline(f);
        }
      } else {
        r = await processOffline(f);
      }
      
      // Check stop after processing
      if (stopRef.current) {
        console.log('❌ Folder scan stopped after processing at file', i);
        break;
      }
      
      let previewUrl = null;
      try {
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(f.name)) previewUrl = await window.electronAPI.readImageDataUrl(f.path);
      } catch {}
      childResults.push({ fileName: f.name, filePath: f.path, previewUrl, isPdf: /\.pdf$/i.test(f.name), ...r });
      setChildTabs(prev => prev.map((t, j) => j === idx ? { ...t, results: [...childResults] } : t));
    }

    setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'done' } : t));
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getMethodBadge = (method) => {
    if (method === 'offline_ocr') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">🔵 Offline OCR (FREE)</span>
      );
    }
    if (method === 'cloud_boost') {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">☁️ Cloud Boost</span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">⚠️ {method}</span>
    );
  };

  return (
    <div className="space-y-4">
      {/* File Selection */}
      <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
        <h2 className="text-base font-semibold text-gray-900 mb-3">Chọn tài liệu</h2>
        <div className="flex flex-wrap gap-2">
          <button onClick={handleSelectFiles} disabled={processing} className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm font-medium">
            <span>📁</span><span>Chọn file</span>
          </button>
          <button onClick={handleSelectFolder} disabled={processing} className="flex items-center space-x-2 px-4 py-2.5 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm font-medium">
            <span>📂</span><span>Chọn thư mục</span>
          </button>
          {selectedFiles.length > 0 && !processing && !isPaused && (
            <button onClick={() => handleProcessFiles()} className="flex items-center space-x-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md text-sm font-medium ml-auto">
              <span>🚀</span><span>Bắt đầu quét</span>
            </button>
          )}
          {isPaused && remainingFiles.length > 0 && (
            <button onClick={() => handleProcessFiles(false, true)} className="flex items-center space-x-2 px-4 py-2.5 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-all shadow-sm hover:shadow-md text-sm font-medium ml-auto animate-pulse">
              <span>▶️</span><span>Tiếp tục quét ({remainingFiles.length} files còn lại)</span>
            </button>
          )}
        </div>
        {selectedFiles.length > 0 && (
          <div className="mt-2"><span className="inline-flex items-center bg-gray-100 border border-gray-200 rounded-full px-2 py-1 text-xs text-gray-700"><span className="mr-1">📦</span>Đã chọn {selectedFiles.length} file</span></div>
        )}
        {parentFolder && parentSummary && (
          <div className="mt-2 text-xs text-gray-700">
            Thư mục: <span className="font-medium">{parentFolder}</span> •
            <span className="ml-2">{parentSummary.subfolderCount} thư mục con</span> •
            <span className="ml-2">{parentSummary.rootFileCount} file ở cấp gốc</span>
          </div>
        )}
      </div>

      {/* Processing Progress with Animation */}
      {processing && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="animate-spin text-2xl">⚙️</div>
              <span className="text-gray-700 font-medium">
                Đang xử lý... ({progress.current}/{selectedFiles.length})
              </span>
            </div>
            <button 
              onClick={() => { 
                stopRef.current = true; 
              }} 
              className="px-4 py-2 text-sm rounded-xl bg-orange-600 text-white hover:bg-orange-700 transition-all shadow-sm hover:shadow-md font-medium"
            >
              ⏸️ Tạm dừng
            </button>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out relative" style={{ width: `${(progress.current / selectedFiles.length) * 100}%` }}>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
            </div>
          </div>
        </div>
      )}

      {/* Results Grid */}
      {results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-900">Kết quả ({results.length})</h2>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2"><label className="text-xs text-gray-600">Mật độ:</label><select value={density} onChange={(e) => setDensity(e.target.value)} className="text-xs border rounded px-2 py-1"><option value="high">Cao (5)</option><option value="medium">TB (4)</option><option value="low">Thấp (3)</option></select></div>
              <button onClick={async () => {
                const payload = results.filter(r => r.success && r.short_code).map(r => ({ filePath: r.filePath, short_code: r.short_code }));
                if (payload.length === 0) { alert('Không có trang hợp lệ để gộp.'); return; }
                const merged = await window.electronAPI.mergeByShortCode(payload, { autoSave: true });
                const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
                alert(`Đã xử lý gộp theo short_code và lưu tự động. Thành công: ${okCount}/${(merged || []).length}.`);
              }} className="px-4 py-2.5 text-sm bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md font-medium">📚 Gộp PDF</button>
            </div>
          </div>
          <div className={`grid gap-3 ${gridColsClass}`}>
            {results.map((result, idx) => (
              <div key={idx} className="p-3 border rounded-lg bg-white">
                <div className="mb-2">
                  {result.previewUrl ? (
                    <img src={result.previewUrl} alt={result.fileName} className="w-full h-40 object-contain border rounded bg-gray-50" />
                  ) : (
                    <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">{result.isPdf ? 'PDF (không có preview)' : 'Không có preview'}</div>
                  )}
                </div>
                <div className="text-sm font-medium truncate" title={result.fileName}>{result.fileName}</div>
                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">{getMethodBadge(result.method)}<span className="ml-auto font-semibold">{(result.confidence * 100).toFixed(0)}%</span></div>
                <div className="mt-2 text-xs text-gray-600">Loại: {result.doc_type} | Mã: <span className="text-blue-600">{result.short_code}</span></div>
                <div className="mt-2 p-2 bg-gray-50 border rounded"><InlineShortCodeEditor value={result.short_code} onChange={(newCode) => { setResults(prev => prev.map((r, i) => i === idx ? { ...r, short_code: newCode } : r)); }} /></div>
                {result.previewUrl && (<button onClick={() => setSelectedPreview(result.previewUrl)} className="mt-2 w-full text-xs text-blue-600 hover:underline">Phóng to ảnh</button>)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Child tabs for parent folder scan */}
      {parentFolder && childTabs.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="flex items-center gap-2 overflow-auto">
            {childTabs.map((t) => (
              <button 
                key={t.path} 
                onClick={() => setActiveChild(t.path)} 
                title={`${t.name} (${t.count} files)`}
                className={`px-3 py-2 text-xs rounded-xl border flex items-center gap-2 min-w-[120px] max-w-[180px] ${activeChild === t.path ? 'bg-blue-50 border-blue-300 text-blue-900 font-medium' : 'bg-white hover:bg-gray-50 border-gray-300'}`}
              >
                <span className="truncate flex-1">{t.name} ({t.count})</span>
                {t.status === 'scanning' ? (
                  <span className="animate-spin flex-shrink-0">⚙️</span>
                ) : t.status === 'done' ? (
                  <span className="text-green-600 flex-shrink-0">✓</span>
                ) : (
                  <span className="text-gray-400 flex-shrink-0">○</span>
                )}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-2">
              <label className="text-xs text-gray-600 inline-flex items-center gap-1">
                <input type="checkbox" checked={childScanImagesOnly} onChange={(e) => setChildScanImagesOnly(e.target.checked)} />Bỏ qua PDF (chỉ quét ảnh)
              </label>
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-600">Mật độ:</label>
                <select value={density} onChange={(e) => setDensity(e.target.value)} className="text-xs border rounded px-2 py-1">
                  <option value="high">Cao (5 cột)</option>
                  <option value="medium">Trung bình (4 cột)</option>
                  <option value="low">Thấp (3 cột)</option>
                </select>
              </div>
              <button 
                onClick={() => { 
                  stopRef.current = true; 
                  setTimeout(() => (stopRef.current = false), 100);
                }} 
                className="px-4 py-2.5 text-xs rounded-xl bg-red-600 text-white hover:bg-red-700 transition-all shadow-sm hover:shadow-md font-medium"
              >
                ⏹️ Dừng quét
              </button>
              <button onClick={async () => { stopRef.current = false; for (const tab of childTabs) { if (stopRef.current) break; if (tab.status !== 'done') await scanChildFolder(tab.path); } }} className="px-4 py-2.5 text-xs rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-all shadow-sm hover:shadow-md font-medium">Quét tất cả thư mục con</button>
              <button
                onClick={() => setShowMergeModal(true)}
                className="px-4 py-2.5 text-xs rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 transition-all shadow-sm hover:shadow-md font-medium"
              >
                📚 Gộp tất cả tab con
              </button>
            </div>
          </div>
          <div className="mt-3">
            {childTabs.map((t) => (
              activeChild === t.path && (
                <div key={t.path}>
                  {/* Loading indicator for scanning tab */}
                  {t.status === 'scanning' && (
                    <div className="mb-3 p-3 bg-blue-50 rounded-xl border border-blue-200">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="animate-spin text-xl">⚙️</div>
                        <span className="text-sm text-blue-900 font-medium">
                          Đang quét thư mục "{t.name}"... ({(t.results || []).length}/{t.count})
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out relative" 
                          style={{ width: `${((t.results || []).length / t.count) * 100}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className={`grid gap-3 ${gridColsClass}`}>
                    {(t.results || []).map((r, idx) => (
                      <div key={idx} className="p-3 border rounded-lg bg-white">
                        <div className="mb-2">
                          {r.previewUrl ? (
                            <img src={r.previewUrl} alt={r.fileName} className="w-full h-40 object-contain border rounded bg-gray-50" />
                          ) : (
                            <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">{r.isPdf ? 'PDF (không có preview)' : 'Không có preview'}</div>
                          )}
                        </div>
                        <div className="text-sm font-medium truncate" title={r.fileName}>{r.fileName}</div>
                        <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                          {getMethodBadge(r.method)}
                          <span className="ml-auto font-semibold">{(r.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="mt-2 text-xs text-gray-600">Loại: {r.doc_type} | Mã: <span className="text-blue-600">{r.short_code}</span></div>
                        <div className="mt-2 p-2 bg-gray-50 border rounded">
                          <InlineShortCodeEditor
                            value={r.short_code}
                            onChange={(newCode) => {
                              setChildTabs(prev => prev.map((ct, j) => {
                                if (j !== childTabs.findIndex(x => x.path === t.path)) return ct;
                                const newRes = [...(ct.results || [])];
                                newRes[idx] = { ...newRes[idx], short_code: newCode };
                                return { ...ct, results: newRes };
                              }));
                            }}
                          />
                        </div>
                        {r.previewUrl && (
                          <button onClick={() => setSelectedPreview(r.previewUrl)} className="mt-2 w-full text-xs text-blue-600 hover:underline">Phóng to ảnh</button>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    {t.status !== 'done' && (
                      <button onClick={() => { stopRef.current = false; scanChildFolder(t.path); }} className="px-3 py-2 text-xs rounded-md bg-indigo-600 text-white hover:bg-indigo-700">Quét thư mục này</button>
                    )}
                    {(t.results && t.results.length > 0) && (
                      <button
                        onClick={async () => {
                          const payload = (t.results || [])
                            .filter(r => r.success && r.short_code)
                            .map(r => ({ filePath: r.filePath, short_code: r.short_code }));
                          if (payload.length === 0) { alert('Không có trang hợp lệ để gộp.'); return; }
                          const merged = await window.electronAPI.mergeByShortCode(payload, { autoSave: true });
                          const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
                          alert(`Đã gộp PDF theo short_code cho thư mục "${t.name}". Thành công: ${okCount}/${(merged || []).length}.`);
                        }}
                        className="px-3 py-2 text-xs rounded-md bg-emerald-600 text-white hover:bg-emerald-700"
                      >
                        📚 Gộp PDF theo short_code (tab này)
                      </button>
                    )}
                  </div>
                </div>
              )
            ))}
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
      {/* Merge report for all child tabs */}
      {childMergeReport.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-4">
          <div className="text-xs font-semibold text-green-800 mb-1">Đã lưu PDF:</div>
          <div className="max-h-28 overflow-auto text-[11px] text-green-900 space-y-1">
            {childMergeReport.map((ln, i) => (
              <div key={i} className="truncate" title={ln}>{ln}</div>
            ))}
          </div>
        </div>
      )}

      {/* Merge Modal */}
      {showMergeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Gộp tất cả thư mục con</h3>
            
            <div className="space-y-4">
              {/* Option 1: Gộp vào thư mục gốc */}
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="mergeOption"
                  value="root"
                  checked={mergeOption === 'root'}
                  onChange={(e) => setMergeOption(e.target.value)}
                  className="mt-1"
                />
                <div>
                  <div className="font-medium text-gray-900">Gộp vào thư mục gốc</div>
                  <div className="text-sm text-gray-600">PDF sẽ được lưu trực tiếp vào thư mục gốc</div>
                </div>
              </label>

              {/* Option 2: Tạo thư mục mới */}
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="mergeOption"
                  value="new"
                  checked={mergeOption === 'new'}
                  onChange={(e) => setMergeOption(e.target.value)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Tạo thư mục mới</div>
                  <div className="text-sm text-gray-600 mb-2">Tên thư mục = Thư mục gốc + ký tự tùy chọn</div>
                  {mergeOption === 'new' && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-700">Ký tự thêm vào:</span>
                      <input
                        type="text"
                        value={mergeSuffix}
                        onChange={(e) => setMergeSuffix(e.target.value)}
                        placeholder="_merged"
                        className="flex-1 px-2 py-1 text-sm border rounded"
                      />
                    </div>
                  )}
                  {mergeOption === 'new' && parentFolder && (
                    <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                      Ví dụ: <span className="font-mono">{parentFolder.split(/[\\\/]/).pop()}{mergeSuffix}</span>
                    </div>
                  )}
                </div>
              </label>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 mt-6">
              <button
                onClick={() => setShowMergeModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={async () => {
                  setShowMergeModal(false);
                  // Execute merge with selected options
                  const finalLines = [];
                  
                  // Pass merge options to backend
                  const mergeOptions = {
                    autoSave: true,
                    mergeMode: mergeOption, // 'root' or 'new'
                    mergeSuffix: mergeSuffix, // e.g., '_merged'
                    parentFolder: parentFolder
                  };
                  
                  // Merge each tab
                  for (const ct of childTabs) {
                    const payload = (ct.results || [])
                      .filter(r => r.success && r.short_code)
                      .map(r => ({ filePath: r.filePath, short_code: r.short_code }));
                    if (payload.length === 0) continue;
                    
                    const merged = await window.electronAPI.mergeByShortCode(payload, mergeOptions);
                    
                    (merged || []).forEach(m => {
                      if (m && m.success && m.path) {
                        finalLines.push(`✓ [${ct.name}] ${m.short_code}: ${m.path}`);
                      }
                    });
                  }
                  setChildMergeReport(finalLines);
                }}
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Bắt đầu gộp
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DesktopScanner;
