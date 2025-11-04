import React, { useState, useEffect, useRef } from 'react';
import CompareResults from './CompareResults';
import InlineShortCodeEditor from './InlineShortCodeEditor';
import QuotaWarning from './QuotaWarning';

const DesktopScanner = ({ initialFolder, onDisplayFolder }) => {
  // Tab state - Main navigation
  const [activeTab, setActiveTab] = useState('files'); // 'files' or 'folders'
  
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
  const [currentOcrEngine, setCurrentOcrEngine] = useState('tesseract'); // Current OCR engine from config

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
  const [activeChildForMerge, setActiveChildForMerge] = useState(null);

  const [parentFolder, setParentFolder] = useState(null);
  const [parentSummary, setParentSummary] = useState(null); // { subfolderCount, rootFileCount }
  const [childTabs, setChildTabs] = useState([]); // [{ name, path, count, status, results }]
  const [activeChild, setActiveChild] = useState(null);
  const [childScanImagesOnly, setChildScanImagesOnly] = useState(false);
  const [isFolderPaused, setIsFolderPaused] = useState(false); // Track folder pause state
  const [remainingTabs, setRemainingTabs] = useState([]); // Tabs left to scan
  const stopRef = useRef(false);
  const [isPaused, setIsPaused] = useState(false); // Track pause state
  const [remainingFiles, setRemainingFiles] = useState([]); // Files left to process
  
  // Quota error handling
  const [quotaError, setQuotaError] = useState(null);
  
  // Rate limit control - delay between requests (ms)
  const [requestDelay, setRequestDelay] = useState(1200); // Default 1.2s = 50 requests/min
  const [postProcessingStatus, setPostProcessingStatus] = useState(null); // Show post-processing notification

  // Load config (guard electron)
  useEffect(() => {
    const loadConfig = async () => {
      const api = window.electronAPI;
      if (!api) return;
      
      // Load backend URL and auto-fallback
      const url = await api.getBackendUrl();
      setBackendUrl(url || '');
      const enabled = await api.getConfig('autoFallbackEnabled');
      setAutoFallbackEnabled(!!enabled);
      
      // Load current OCR engine from unified config
      const engine = await api.getConfig('ocrEngine') || 'tesseract';
      setCurrentOcrEngine(engine);
      
      console.log('🔍 Current OCR Engine:', engine);
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
      
      // Check for quota/rate limit errors
      if (result && result.error && typeof result.error === 'string') {
        if (result.error.includes('QUÁ GIỚI HẠN') || 
            result.error_code === 'RATE_LIMIT_EXCEEDED' ||
            result.error_code === 'INVALID_API_KEY') {
          setQuotaError(result.error);
          setProcessing(false);
          return { success: false, error: result.error, method: 'quota_exceeded' };
        }
      }
      
      return result;
    } catch (error) {
      return { success: false, error: error.message, method: 'offline_failed' };
    }
  };

  // Helper function to safely format confidence percentage
  const formatConfidence = (confidence) => {
    if (confidence === null || confidence === undefined || isNaN(confidence)) {
      return '0';
    }
    const conf = parseFloat(confidence);
    if (isNaN(conf) || conf < 0 || conf > 1) {
      return '0';
    }
    return (conf * 100).toFixed(0);
  };

  const applySequentialNaming = (result, lastType) => {
    if (result.success && lastType) {
      if (result.short_code === 'UNKNOWN') {
        console.log(`🔄 Sequential: UNKNOWN → ${lastType.short_code}`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.75, lastType.confidence * 0.95),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của ${lastType.short_code} (không nhận dạng được)`
        };
      }
      if (!result.title_boost_applied) {
        const reason = result.title_extracted_via_pattern 
          ? "title rejected by classifier (uppercase < 70% or low similarity)"
          : "no title extracted";
        
        console.log(`🔄 Sequential: ${reason} (confidence ${formatConfidence(result.confidence)}%, classified as ${result.short_code}) → Override to ${lastType.short_code}`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.70, lastType.confidence * 0.92),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của ${lastType.short_code} (${reason})`
        };
      }
      if (result.title_boost_applied) {
        console.log(`✅ No sequential: Title accepted by classifier → New document ${result.short_code} (confidence: ${formatConfidence(result.confidence)}%)`);
      }
    }
    return result;
  };

  // Post-process GCN documents after batch completion
  const postProcessGCNBatch = (results) => {
    try {
      console.log('🔄 Post-processing GCN batch...');
      
      // STEP 1: Convert any old GCNM/GCNC to GCN (Gemini sometimes still returns old codes)
      const normalizedResults = results.map(r => {
        if (r.short_code === 'GCNM' || r.short_code === 'GCNC') {
          console.log(`🔄 Converting ${r.short_code} → GCN for file: ${r.fileName}`);
          return {
            ...r,
            short_code: 'GCN',
            original_short_code: r.short_code,
            reasoning: `${r.reasoning || ''} (Normalized from ${r.short_code} to GCN for batch processing)`
          };
        }
        return r;
      });
    
    // STEP 2: Find all GCN documents with certificate numbers
    const gcnDocs = normalizedResults.filter(r => 
      r.short_code === 'GCN' && 
      r.certificate_number && 
      r.certificate_number.trim() !== ''
    );
    
    if (gcnDocs.length === 0) {
      console.log('✅ No GCN documents found in batch');
      return normalizedResults;
    }
    
    console.log(`📋 Found ${gcnDocs.length} GCN document(s) to process`);
    
    // Group by prefix (first 2 letters of certificate number)
    const grouped = {};
    gcnDocs.forEach((doc, originalIndex) => {
      const certNumber = doc.certificate_number.trim();
      const match = certNumber.match(/^([A-Z]{2})\s*(\d{6})$/i);
      
      if (match) {
        const prefix = match[1].toUpperCase();
        const number = match[2];
        
        if (!grouped[prefix]) {
          grouped[prefix] = [];
        }
        
        grouped[prefix].push({
          ...doc,
          _originalIndex: normalizedResults.indexOf(doc),
          _certPrefix: prefix,
          _certNumber: parseInt(number, 10)
        });
      }
    });
    
    console.log(`📊 Grouped into ${Object.keys(grouped).length} prefix(es):`, Object.keys(grouped));
    
    // Process each group
    const updatedResults = [...normalizedResults];
    
    Object.entries(grouped).forEach(([prefix, docs]) => {
      if (docs.length === 1) {
        // Only 1 GCN with this prefix - classify as GCNC (default to old)
        console.log(`📄 ${prefix}: Only 1 document, defaulting to GCNC`);
        const doc = docs[0];
        updatedResults[doc._originalIndex] = {
          ...doc,
          short_code: 'GCNC',
          reasoning: `${doc.reasoning || 'GCN'} - Single certificate in batch (default: old format)`,
          gcn_classification_note: '📌 Single GCN in batch → GCNC (default)'
        };
      } else {
        // Multiple GCNs - sort by certificate number
        const sorted = [...docs].sort((a, b) => a._certNumber - b._certNumber);
        
        console.log(`📊 ${prefix}: ${sorted.length} documents, sorting...`);
        sorted.forEach((doc, idx) => {
          console.log(`  ${idx + 1}. ${prefix} ${String(doc._certNumber).padStart(6, '0')} (index: ${doc._originalIndex})`);
        });
        
        // Smallest number = GCNC (old), others = GCNM (new)
        sorted.forEach((doc, idx) => {
          const isOldest = (idx === 0);
          const classification = isOldest ? 'GCNC' : 'GCNM';
          const note = isOldest 
            ? `📌 Smallest number in batch → GCNC (old format)`
            : `📌 Larger than ${prefix} ${String(sorted[0]._certNumber).padStart(6, '0')} → GCNM (new format)`;
          
          console.log(`  ✅ ${prefix} ${String(doc._certNumber).padStart(6, '0')} → ${classification} ${isOldest ? '(oldest)' : '(newer)'}`);
          
          updatedResults[doc._originalIndex] = {
            ...doc,
            short_code: classification,
            reasoning: `${doc.reasoning || 'GCN'} - Certificate ${doc.certificate_number} (${isOldest ? 'oldest' : 'newer'} in batch)`,
            gcn_classification_note: note
          };
        });
      }
    });
    
    console.log('✅ GCN post-processing complete');
    return updatedResults;
    } catch (error) {
      console.error('❌ Error in GCN post-processing:', error);
      console.error('Stack trace:', error.stack);
      // Return original results if processing fails
      return results;
    }
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
    setIsPaused(false);
    
    if (!isResume) {
      setResults([]);
      setComparisons([]);
      setProgress({ current: 0, total: filesToProcess.length });
      setLastKnownType(null);
      setRemainingFiles(filesToProcess);
    } else {
      filesToProcess = remainingFiles;
      setProgress({ current: results.length, total: results.length + filesToProcess.length });
    }
    
    stopRef.current = false;

    const newResults = isResume ? [...results] : [];
    let currentLastKnown = null;

    for (let i = 0; i < filesToProcess.length; i++) {
      if (stopRef.current) {
        console.log('❌ Scan stopped by user at file', i);
        setRemainingFiles(filesToProcess.slice(i));
        setIsPaused(true);
        setProcessing(false);
        return;
      }
      
      const file = filesToProcess[i];
      setProgress({ current: i + 1, total: filesToProcess.length });

      let result = await processOffline(file);
      
      // 🔧 ADD DELAY: Tránh vượt Rate Limit (60 requests/phút)
      // User configurable delay để tránh rate limit
      if (i < filesToProcess.length - 1) { // Không delay ở file cuối
        await new Promise(resolve => setTimeout(resolve, requestDelay));
      }
      
      if (stopRef.current) {
        console.log('❌ Scan stopped after processing at file', i);
        setRemainingFiles(filesToProcess.slice(i));
        setIsPaused(true);
        setProcessing(false);
        return;
      }
      
      if (stopRef.current) {
        console.log('❌ Scan stopped after processing at file', i);
        setRemainingFiles(filesToProcess.slice(i + 1));
        setIsPaused(true);
        setProcessing(false);
        return;
      }

      const processedResult = applySequentialNaming(result, currentLastKnown);
      if (processedResult.success && 
          processedResult.short_code !== 'UNKNOWN' && 
          processedResult.confidence >= 0.7 &&
          !processedResult.applied_sequential_logic) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
        console.log(`📌 Updated lastKnown: ${processedResult.short_code} (${formatConfidence(processedResult.confidence)}%)`);
      }

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
      setResults([...newResults]);
    }

    // Post-process GCN documents after batch completion
    console.log('======================================================================');
    console.log('🔄 BATCH SCAN COMPLETE - POST-PROCESSING GCN DOCUMENTS');
    console.log('======================================================================');
    console.log(`📊 Total files scanned: ${newResults.length}`);
    const gcnCount = newResults.filter(r => r.short_code === 'GCN' || r.short_code === 'GCNM' || r.short_code === 'GCNC').length;
    console.log(`📋 GCN/GCNM/GCNC files found: ${gcnCount}`);
    
    // Show notification
    if (gcnCount > 0) {
      setPostProcessingStatus(`🔄 Đang phân loại ${gcnCount} GCN documents...`);
    }
    
    const finalResults = postProcessGCNBatch(newResults);
    
    console.log('======================================================================');
    console.log('✅ POST-PROCESSING COMPLETE - UPDATING UI');
    console.log('======================================================================');
    
    // Update notification
    if (gcnCount > 0) {
      const gcncCount = finalResults.filter(r => r.short_code === 'GCNC').length;
      const gcnmCount = finalResults.filter(r => r.short_code === 'GCNM').length;
      setPostProcessingStatus(`✅ Hoàn tất: ${gcncCount} GCNC, ${gcnmCount} GCNM`);
      
      // Clear after 5 seconds
      setTimeout(() => setPostProcessingStatus(null), 5000);
    }
    
    // Force UI update
    setResults([...finalResults]);

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
    if (childScanImagesOnly) fileList = fileList.filter(f => (/\.(png|jpg|jpeg|gif|bmp)$/i).test(f.name));

    const files = fileList;
    const childResults = [];
    stopRef.current = false;
    
    let currentLastKnown = null;
    
    for (let i = 0; i < files.length; i++) {
      if (stopRef.current) {
        console.log('❌ Folder scan stopped at file', i, 'in', childPath);
        break;
      }
      const f = files[i];
      
      let r = await processOffline(f);
      
      if (stopRef.current) {
        console.log('❌ Folder scan stopped after processing at file', i);
        break;
      }
      
      if (stopRef.current) {
        console.log('❌ Folder scan stopped after processing at file', i);
        break;
      }
      
      const processedResult = applySequentialNaming(r, currentLastKnown);
      if (processedResult.success && 
          processedResult.short_code !== 'UNKNOWN' && 
          processedResult.confidence >= 0.7 &&
          !processedResult.applied_sequential_logic) {
        currentLastKnown = {
          doc_type: processedResult.doc_type,
          short_code: processedResult.short_code,
          confidence: processedResult.confidence
        };
        console.log(`📌 Updated lastKnown (folder): ${processedResult.short_code} (${formatConfidence(processedResult.confidence)}%)`);
      }
      
      let previewUrl = null;
      try {
        if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(f.name)) previewUrl = await window.electronAPI.readImageDataUrl(f.path);
      } catch {}
      childResults.push({ fileName: f.name, filePath: f.path, previewUrl, isPdf: /\.pdf$/i.test(f.name), ...processedResult });
      setChildTabs(prev => prev.map((t, j) => j === idx ? { ...t, results: [...childResults] } : t));
    }

    // Post-process GCN documents for this child folder
    console.log(`🔄 Child folder scan complete (${childPath}), post-processing GCN documents...`);
    const finalChildResults = postProcessGCNBatch(childResults);
    setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'done', results: finalChildResults } : t));
  };

  // Scan all child folders with pause support
  const scanAllChildFolders = async (isResume = false) => {
    stopRef.current = false;
    setIsFolderPaused(false);
    
    let tabsToScan = isResume ? remainingTabs : childTabs.filter(t => t.status !== 'done');
    
    for (const tab of tabsToScan) {
      if (stopRef.current) {
        console.log('❌ Folder scan stopped');
        const remainingIndex = tabsToScan.indexOf(tab);
        setRemainingTabs(tabsToScan.slice(remainingIndex));
        setIsFolderPaused(true);
        return;
      }
      await scanChildFolder(tab.path);
    }
    
    setRemainingTabs([]);
    setIsFolderPaused(false);
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
      {/* Quota Warning Modal */}
      {quotaError && <QuotaWarning error={quotaError} />}
      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex">
          <button
            onClick={() => setActiveTab('files')}
            className={`flex-1 px-6 py-4 text-sm font-semibold transition-all ${
              activeTab === 'files'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            📄 Quét File
          </button>
          <button
            onClick={() => setActiveTab('folders')}
            className={`flex-1 px-6 py-4 text-sm font-semibold transition-all ${
              activeTab === 'folders'
                ? 'bg-green-600 text-white'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            📂 Quét Thư Mục
          </button>
        </div>
      </div>

      {/* FILE SCAN TAB */}
      {activeTab === 'files' && (
        <>
          {/* File Selection */}
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h2 className="text-base font-semibold text-gray-900 mb-3">Quét File</h2>
            
            {/* Rate Limit Control */}
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  ⏱️ Delay giữa các request (tránh Rate Limit):
                </label>
                <span className="text-sm font-bold text-blue-700">
                  {requestDelay}ms = ~{Math.floor(60000 / (requestDelay + 1000))} requests/phút
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="3000"
                step="100"
                value={requestDelay}
                onChange={(e) => setRequestDelay(parseInt(e.target.value))}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
                disabled={processing}
              />
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>0ms (60/phút ⚠️)</span>
                <span>1000ms (30/phút ✅)</span>
                <span>2000ms (20/phút 🐢)</span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                💡 <strong>Khuyến nghị:</strong> 1200ms (~50/phút) để tránh vượt limit 60 requests/phút
              </p>
            </div>
            
            <div className="flex flex-wrap gap-2">
              <button onClick={handleSelectFiles} disabled={processing} className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm font-medium">
                <span>📁</span><span>Chọn file</span>
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
              <div className="mt-2 flex items-center gap-2">
                <span className="inline-flex items-center bg-gray-100 border border-gray-200 rounded-full px-2 py-1 text-xs text-gray-700">
                  <span className="mr-1">📦</span>Đã chọn {selectedFiles.length} file
                </span>
                <span className="inline-flex items-center border border-blue-200 rounded-full px-2 py-1 text-xs">
                  {currentOcrEngine === 'google' && <span className="text-blue-700">☁️ Google Cloud Vision</span>}
                  {currentOcrEngine === 'azure' && <span className="text-blue-700">☁️ Azure Computer Vision</span>}
                  {currentOcrEngine === 'tesseract' && <span className="text-gray-700">⚡ Tesseract OCR</span>}
                  {currentOcrEngine === 'easyocr' && <span className="text-gray-700">⚡ EasyOCR</span>}
                  {currentOcrEngine === 'vietocr' && <span className="text-gray-700">⚡ VietOCR</span>}
                </span>
              </div>
            )}
          </div>
        </>
      )}

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

      {/* GCN Post-Processing Status */}
      {postProcessingStatus && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl shadow-sm p-4 border-2 border-green-200 animate-pulse">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">
              {postProcessingStatus.startsWith('✅') ? '✅' : '🔄'}
            </div>
            <span className="text-gray-800 font-semibold text-lg">
              {postProcessingStatus}
            </span>
          </div>
        </div>
      )}

      {/* Paused State - File Scan */}
      {activeTab === 'files' && isPaused && remainingFiles.length > 0 && (
        <div className="bg-orange-50 rounded-xl shadow-sm p-4 border border-orange-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">⏸️</span>
              <div>
                <div className="text-orange-900 font-medium">Đã tạm dừng</div>
                <div className="text-sm text-orange-700">
                  Đã quét: {results.length} files • Còn lại: {remainingFiles.length} files
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Grid - File Scan */}
      {activeTab === 'files' && results.length > 0 && (
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
                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">{getMethodBadge(result.method)}<span className="ml-auto font-semibold">{formatConfidence(result.confidence)}%</span></div>
                <div className="mt-2 text-xs text-gray-600">Loại: {result.doc_type} | Mã: <span className="text-blue-600">{result.short_code}</span></div>
                {typeof result.estimated_cost_usd === 'number' && (
                  <div className="mt-1 text-[11px] text-emerald-700">
                    Ước tính: ${result.estimated_cost_usd.toFixed(6)} {result.usage ? `(in ${result.usage.input_tokens || 0}, out ${result.usage.output_tokens || 0})` : ''}
                    {result.resize_info && result.resize_info.resized && (
                      <span className="ml-2 text-green-600" title={`Resized: ${result.resize_info.original_size} → ${result.resize_info.final_size}`}>
                        📉 -{result.resize_info.reduction_percent}%
                      </span>
                    )}
                  </div>
                )}
                <div className="mt-2 p-2 bg-gray-50 border rounded"><InlineShortCodeEditor value={result.short_code} onChange={(newCode) => { setResults(prev => prev.map((r, i) => i === idx ? { ...r, short_code: newCode } : r)); }} /></div>
                {result.previewUrl && (<button onClick={() => setSelectedPreview(result.previewUrl)} className="mt-2 w-full text-xs text-blue-600 hover:underline">Phóng to ảnh</button>)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FOLDER SCAN TAB */}
      {activeTab === 'folders' && (
        <>
          {/* Folder Selection */}
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h2 className="text-base font-semibold text-gray-900 mb-3">Quét Thư Mục</h2>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleSelectFolder} disabled={processing || childTabs.some(t => t.status === 'scanning')} className="flex items-center space-x-2 px-4 py-2.5 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm font-medium">
                <span>📂</span><span>Chọn thư mục</span>
              </button>
            </div>
            {parentFolder && parentSummary && (
              <div className="mt-2 text-xs text-gray-700">
                Thư mục: <span className="font-medium">{parentFolder}</span> •
                <span className="ml-2">{parentSummary.subfolderCount} thư mục con</span> •
                <span className="ml-2">{parentSummary.rootFileCount} file ở cấp gốc</span>
              </div>
            )}
          </div>
        </>
      )}

      {/* Child tabs for parent folder scan */}
      {activeTab === 'folders' && parentFolder && childTabs.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          {/* Control buttons - MOVED TO TOP */}
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-900">Quét thư mục con</h2>
            <div className="flex items-center gap-2">
              {/* Density control */}
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-600">Mật độ:</label>
                <select value={density} onChange={(e) => setDensity(e.target.value)} className="text-xs border rounded-lg px-2 py-1">
                  <option value="high">Cao (5)</option>
                  <option value="medium">TB (4)</option>
                  <option value="low">Thấp (3)</option>
                </select>
              </div>
              
              <label className="text-xs text-gray-600 inline-flex items-center gap-1">
                <input type="checkbox" checked={childScanImagesOnly} onChange={(e) => setChildScanImagesOnly(e.target.checked)} />
                Bỏ qua PDF
              </label>
              
              {/* Resume button if paused */}
              {isFolderPaused && remainingTabs.length > 0 && (
                <button 
                  onClick={() => scanAllChildFolders(true)}
                  className="px-4 py-2.5 text-xs rounded-xl bg-green-600 text-white hover:bg-green-700 transition-all shadow-sm hover:shadow-md font-medium animate-pulse"
                >
                  ▶️ Tiếp tục ({remainingTabs.length} thư mục)
                </button>
              )}
              
              {/* Stop/Scan All buttons */}
              {!isFolderPaused && (
                <>
                  <button 
                    onClick={() => { 
                      stopRef.current = true;
                    }} 
                    className="px-4 py-2.5 text-xs rounded-xl bg-orange-600 text-white hover:bg-orange-700 transition-all shadow-sm hover:shadow-md font-medium"
                  >
                    ⏸️ Tạm dừng
                  </button>
                  <button 
                    onClick={() => scanAllChildFolders(false)} 
                    className="px-4 py-2.5 text-xs rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-all shadow-sm hover:shadow-md font-medium"
                  >
                    Quét tất cả thư mục con
                  </button>
                </>
              )}
              
              <button
                onClick={() => setShowMergeModal(true)}
                className="px-4 py-2.5 text-xs rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 transition-all shadow-sm hover:shadow-md font-medium"
              >
                📚 Gộp tất cả tab con
              </button>
            </div>
          </div>
          
          {/* Paused indicator for folder scan */}
          {isFolderPaused && remainingTabs.length > 0 && (
            <div className="mb-3 p-3 bg-orange-50 rounded-xl border border-orange-200">
              <div className="flex items-center space-x-3">
                <span className="text-xl">⏸️</span>
                <div>
                  <div className="text-sm text-orange-900 font-medium">Đã tạm dừng quét thư mục</div>
                  <div className="text-xs text-orange-700">
                    Đã quét: {childTabs.filter(t => t.status === 'done').length} thư mục • Còn lại: {remainingTabs.length} thư mục
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Tabs */}
          <div className="flex items-center gap-2 overflow-auto mb-3">
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
          </div>
          
          {/* Tab content */}
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
                          <span className="ml-auto font-semibold">{formatConfidence(r.confidence)}%</span>
                        </div>
                        <div className="mt-2 text-xs text-gray-600">Loại: {r.doc_type} | Mã: <span className="text-blue-600">{r.short_code}</span></div>
                        {typeof r.estimated_cost_usd === 'number' && (
                          <div className="mt-1 text-[11px] text-emerald-700">
                            Ước tính: ${r.estimated_cost_usd.toFixed(6)} {r.usage ? `(in ${r.usage.input_tokens || 0}, out ${r.usage.output_tokens || 0})` : ''}
                            {r.resize_info && r.resize_info.resized && (
                              <span className="ml-2 text-green-600" title={`Resized: ${r.resize_info.original_size} → ${r.resize_info.final_size}`}>
                                📉 -{r.resize_info.reduction_percent}%
                              </span>
                            )}
                          </div>
                        )}
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
                      <button onClick={() => { stopRef.current = false; scanChildFolder(t.path); }} className="px-3 py-2 text-xs rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition-all shadow-sm font-medium">Quét thư mục này</button>
                    )}
                    {(t.results && t.results.length > 0) && (
                      <button
                        onClick={() => {
                          setActiveChildForMerge(t);
                          setShowMergeModal(true);
                        }}
                        className="px-3 py-2 text-xs rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 transition-all shadow-sm font-medium"
                      >
                        📚 Gộp thư mục này
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
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📚 {activeChildForMerge ? `Gộp thư mục "${activeChildForMerge.name}"` : 'Gộp tất cả thư mục con'}
            </h3>
            
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
                  const finalLines = [];
                  const mergeOptions = {
                    autoSave: true,
                    mergeMode: mergeOption,
                    mergeSuffix: mergeSuffix,
                    parentFolder: parentFolder
                  };
                  const tabsToMerge = activeChildForMerge ? [activeChildForMerge] : childTabs;
                  for (const ct of tabsToMerge) {
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
                  setActiveChildForMerge(null);
                }}
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-all shadow-sm font-medium"
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
