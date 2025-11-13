import React, { useState, useEffect, useRef } from 'react';
import CompareResults from './CompareResults';
import InlineShortCodeEditor from './InlineShortCodeEditor';
import QuotaWarning from './QuotaWarning';
import ResumeDialog from './ResumeDialog';

const DesktopScanner = ({ initialFolder, onDisplayFolder, onSwitchTab, disableResumeCheck = false }) => {
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
  
  // Pagination to prevent memory overflow
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 10; // EMERGENCY: Ultra-safe limit (10 items)
  const [previewsEnabled, setPreviewsEnabled] = useState(false); // DEFAULT OFF to prevent crashes
  
  // Memory cleanup when changing pages
  useEffect(() => {
    // Force garbage collection hint (not guaranteed but helps)
    if (window.gc) {
      console.log('🗑️ Triggering garbage collection');
      window.gc();
    }
  }, [currentPage]);

  // Parent folder analysis + child tabs
  const [childMergeReport, setChildMergeReport] = useState([]); // lines of saved PDFs across tabs
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeOption, setMergeOption] = useState('root'); // 'root' or 'new'
  const [mergeSuffix, setMergeSuffix] = useState('_merged');
  const [activeChildForMerge, setActiveChildForMerge] = useState(null);
  
  // File scan merge modal
  const [showFileMergeModal, setShowFileMergeModal] = useState(false);
  const [fileOutputOption, setFileOutputOption] = useState('same_folder'); // 'same_folder', 'new_folder', 'custom_folder'
  const [fileMergeSuffix, setFileMergeSuffix] = useState('_merged');
  const [fileOutputFolder, setFileOutputFolder] = useState(null);
  const [fileMergeInProgress, setFileMergeInProgress] = useState(false);

  const [parentFolder, setParentFolder] = useState(null);
  const [parentSummary, setParentSummary] = useState(null); // { subfolderCount, rootFileCount }
  const [childTabs, setChildTabs] = useState([]); // [{ name, path, count, status, results }]
  const [activeChild, setActiveChild] = useState(null);
  const [childScanImagesOnly, setChildScanImagesOnly] = useState(false);
  const [isFolderPaused, setIsFolderPaused] = useState(false); // Track folder pause state
  const [duplicateChildFolders, setDuplicateChildFolders] = useState([]); // Track duplicate folder names: [{name, paths: [path1, path2]}]
  const [remainingTabs, setRemainingTabs] = useState([]); // Tabs left to scan
  const [tabPreviewsLoaded, setTabPreviewsLoaded] = useState(new Set()); // Track which tabs have previews loaded
  const [isLoadingPreviews, setIsLoadingPreviews] = useState(false); // Track preview loading state
  const [previewLoadMode, setPreviewLoadMode] = useState('gcn-only'); // 'none', 'gcn-only', 'all'
  const [isLoadingTabs, setIsLoadingTabs] = useState(false); // Track progressive tab loading
  const [tabLoadProgress, setTabLoadProgress] = useState({ current: 0, total: 0 }); // Progress for tab loading
  const [isEditingResultId, setIsEditingResultId] = useState(null); // Track which result is being edited (prevent update conflicts)
  const stopRef = useRef(false);
  const [isPaused, setIsPaused] = useState(false); // Track pause state
  const [remainingFiles, setRemainingFiles] = useState([]); // Files left to process
  
  // Quota error handling
  const [quotaError, setQuotaError] = useState(null);
  
  // Rate limit control - delay between requests (ms)
  const [requestDelay, setRequestDelay] = useState(1200); // Default 1.2s, loaded from config
  const [postProcessingStatus, setPostProcessingStatus] = useState(null); // Show post-processing notification
  
  // Batch processing mode
  const [batchMode, setBatchMode] = useState('sequential'); // 'sequential', 'fixed', 'smart'
  const [activeBatchMode, setActiveBatchMode] = useState(null); // Track active batch mode during scan
  
  // GCN sorting preference
  const [sortGCNToTop, setSortGCNToTop] = useState(true); // User preference: sort GCN to top after scan
  
  // Auto-save & Resume
  const [showResumeDialog, setShowResumeDialog] = useState(false);
  const [incompleteScans, setIncompleteScans] = useState([]);
  const [currentScanId, setCurrentScanId] = useState(null);
  
  // Timer states
  const [timers, setTimers] = useState({
    scanStartTime: null,
    scanEndTime: null,
    scanElapsedSeconds: 0,
    fileTimings: [], // [{fileName, startTime, endTime, durationMs, engineType}]
    folderTimings: [], // [{folderName, startTime, endTime, durationMs, fileCount}]
  });
  const [elapsedTime, setElapsedTime] = useState(0); // Live elapsed time in seconds
  const timerIntervalRef = useRef(null);

  // Helper: Sort results with GCN (GCNC, GCNM) on top
  const sortResultsWithGCNOnTop = (results) => {
    if (!results || results.length === 0) return results;
    
    const gcnResults = [];
    const otherResults = [];
    
    results.forEach(result => {
      const shortCode = result.short_code || result.classification || '';
      if (shortCode === 'GCNC' || shortCode === 'GCNM') {
        gcnResults.push(result);
      } else {
        otherResults.push(result);
      }
    });
    
    // GCN first (GCNC then GCNM), then others
    const sortedGCN = gcnResults.sort((a, b) => {
      const aCode = a.short_code || a.classification || '';
      const bCode = b.short_code || b.classification || '';
      if (aCode === 'GCNC' && bCode === 'GCNM') return -1;
      if (aCode === 'GCNM' && bCode === 'GCNC') return 1;
      return 0;
    });
    
    return [...sortedGCN, ...otherResults];
  };

  // Live timer effect - update elapsed time every second
  useEffect(() => {
    if (processing && timers.scanStartTime) {
      timerIntervalRef.current = setInterval(() => {
        const now = Date.now();
        const elapsedMs = now - timers.scanStartTime;
        setElapsedTime(Math.floor(elapsedMs / 1000)); // Convert to seconds
      }, 1000);
    } else {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
    }
    
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, [processing, timers.scanStartTime]);
  
  // Auto-save when childTabs change (folders complete) - IMMEDIATE SAVE
  useEffect(() => {
    const autoSave = async () => {
      const doneFolders = childTabs.filter(t => t.status === 'done');
      const allDone = childTabs.length > 0 && childTabs.every(t => t.status === 'done');
      
      if (childTabs.length > 0 && doneFolders.length > 0 && !allDone && window.electronAPI?.saveScanState) {
        let scanId = currentScanId;
        if (!scanId) {
          scanId = `folder_scan_${Date.now()}`;
          setCurrentScanId(scanId);
        }
        
        await window.electronAPI.saveScanState({
          scanId: scanId,
          type: 'folder_scan',
          status: 'incomplete',
          parentFolder: parentFolder,
          // Strip previewUrl to reduce size
          childTabs: childTabs.map(t => ({
            ...t,
            results: t.results?.map(r => ({ ...r, previewUrl: null })) || []
          })),
          activeChild: activeChild,
          progress: {
            current: doneFolders.length,
            total: childTabs.length
          },
          engine: currentOcrEngine,
          batchMode: batchMode,
          timestamp: Date.now()
        });
        
        console.log(`💾 Auto-saved immediately: ${doneFolders.length}/${childTabs.length} folders done`);
      }
    };
    autoSave(); // Execute immediately (no debounce)
  }, [childTabs, currentScanId, parentFolder, activeChild, currentOcrEngine, batchMode]);
  
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
      
      // Load request delay from config
      const savedDelay = await api.getConfig('requestDelay');
      if (savedDelay !== undefined && savedDelay !== null) {
        setRequestDelay(parseInt(savedDelay));
        console.log(`⏱️ Loaded request delay: ${savedDelay}ms`);
      }
      
      // Load batch mode from config
      const savedBatchMode = await api.getConfig('batchMode');
      if (savedBatchMode) {
        setBatchMode(savedBatchMode);
        console.log(`📦 Loaded batch mode: ${savedBatchMode}`);
      }
      
      // Load GCN sort preference from config
      const savedSortGCN = await api.getConfig('sortGCNToTop');
      if (savedSortGCN !== undefined && savedSortGCN !== null) {
        setSortGCNToTop(savedSortGCN);
        console.log(`📊 Loaded GCN sort preference: ${savedSortGCN}`);
      }
      
      console.log('🔍 Current OCR Engine:', engine);
      
      // Check for incomplete scans (only for main scanner tab, not folder tabs)
      if (!disableResumeCheck) {
        const incompleteResult = await api.getIncompleteScans();
        if (incompleteResult.success && incompleteResult.scans.length > 0) {
          // Filter to only show folder_scan and file_scan (not batch_scan)
          const scannerScans = incompleteResult.scans.filter(s => 
            s.type === 'folder_scan' || s.type === 'file_scan'
          );
          if (scannerScans.length > 0) {
            console.log(`🔄 Found ${scannerScans.length} incomplete scanner scan(s)`);
            setIncompleteScans(scannerScans);
            setShowResumeDialog(true);
          }
        }
      }
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

  // Load previews on-demand when switching active child tab
  useEffect(() => {
    const loadPreviewsForActiveTab = async () => {
      if (!activeChild || !window.electronAPI) return;
      
      // Skip if preview mode is 'none'
      if (previewLoadMode === 'none') {
        console.log(`🚫 Preview mode is 'none' - skipping preview load`);
        setTabPreviewsLoaded(prev => new Set([...prev, activeChild]));
        return;
      }
      
      // Check if previews for this tab are already loaded
      if (tabPreviewsLoaded.has(activeChild)) {
        console.log(`✅ Previews already loaded for tab: ${activeChild}`);
        return;
      }
      
      const activeTabIndex = childTabs.findIndex(t => t.path === activeChild);
      if (activeTabIndex === -1) return;
      
      const activeTabData = childTabs[activeTabIndex];
      if (!activeTabData.results || activeTabData.results.length === 0) return;
      
      // Determine which results need preview loading based on mode
      const shouldLoadPreview = (result) => {
        if (!result.filePath || !/\.(png|jpg|jpeg|gif|bmp)$/i.test(result.fileName)) return false;
        if (result.previewUrl) return false; // Already has preview
        
        // Mode: 'gcn-only' - only load GCN documents
        if (previewLoadMode === 'gcn-only') {
          const shortCode = result.short_code || result.classification || '';
          return shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN';
        }
        
        // Mode: 'all' - load all
        return true;
      };
      
      const needsLoading = activeTabData.results.some(shouldLoadPreview);
      
      if (!needsLoading) {
        // Mark as loaded even if no previews needed
        setTabPreviewsLoaded(prev => new Set([...prev, activeChild]));
        console.log(`ℹ️ No previews to load for tab (mode: ${previewLoadMode})`);
        return;
      }
      
      const modeLabel = previewLoadMode === 'gcn-only' ? '(chỉ GCN)' : '(tất cả)';
      console.log(`🖼️ Loading previews for tab: ${activeTabData.name} ${modeLabel}...`);
      setIsLoadingPreviews(true);
      
      try {
        let loadedCount = 0;
        // Load previews for this tab's results
        const updatedResults = await Promise.all(
          activeTabData.results.map(async (result) => {
            // Check if should load preview for this result
            if (!shouldLoadPreview(result)) {
              return result;
            }
            
            try {
              const previewUrl = await window.electronAPI.readImageDataUrl(result.filePath);
              if (previewUrl) loadedCount++;
              return { ...result, previewUrl: previewUrl || null };
            } catch (err) {
              console.warn(`⚠️ Failed to load preview for: ${result.fileName}`);
              return result;
            }
          })
        );
        
        // Update only the active tab's results
        setChildTabs(prev => prev.map((tab, idx) => 
          idx === activeTabIndex ? { ...tab, results: updatedResults } : tab
        ));
        
        // Mark this tab as having loaded previews
        setTabPreviewsLoaded(prev => new Set([...prev, activeChild]));
        
        console.log(`✅ Loaded ${loadedCount} previews for tab: ${activeTabData.name} ${modeLabel}`);
      } catch (error) {
        console.error(`❌ Error loading previews:`, error);
      } finally {
        setIsLoadingPreviews(false);
      }
    };
    
    loadPreviewsForActiveTab();
  }, [activeChild, childTabs, previewLoadMode]);

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
      // Rule 1: UNKNOWN → always use lastKnown
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
      
      // Rule 2: No title boost (no title or rejected title) → use lastKnown
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
      
      // Rule 3: Title not at top (middle/bottom) + low confidence → likely continuation
      if (result.title_position && result.title_position !== 'top' && result.confidence < 0.85) {
        console.log(`🔄 Sequential: Title at ${result.title_position} + low confidence (${formatConfidence(result.confidence)}%) → Override ${result.short_code} to ${lastType.short_code}`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.70, lastType.confidence * 0.90),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của ${lastType.short_code} (title at ${result.title_position}, confidence ${formatConfidence(result.confidence)}%)`
        };
      }
      
      // Rule 4: Different doc type but low confidence → might be continuation
      if (result.short_code !== lastType.short_code && result.confidence < 0.80) {
        console.log(`🔄 Sequential: Different doc (${result.short_code} vs ${lastType.short_code}) + low confidence (${formatConfidence(result.confidence)}%) → Override to ${lastType.short_code}`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.70, lastType.confidence * 0.88),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của ${lastType.short_code} (detected as ${result.short_code} with low confidence)`
        };
      }
      
      // Rule 5: Special case - GCN + HSKT (common mistake for GCN page 2 with map/diagram)
      if ((lastType.short_code === 'GCN' || lastType.short_code === 'GCNM' || lastType.short_code === 'GCNC') 
          && result.short_code === 'HSKT') {
        console.log(`🔄 Sequential: GCN page 2 detected as HSKT (sơ đồ thửa đất) → Override to ${lastType.short_code}`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.75, lastType.confidence * 0.92),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của ${lastType.short_code} (trang 2 có sơ đồ thửa đất, nhầm với HSKT)`
        };
      }
      
      // Rule 6: Special case - PCT + DDKBD (common mistake for PCT page 2 with "ĐĂNG KÝ BIẾN ĐỘNG" section)
      if (lastType.short_code === 'PCT' && result.short_code === 'DDKBD') {
        console.log(`🔄 Sequential: PCT page 2 detected as DDKBD (section "ĐĂNG KÝ BIẾN ĐỘNG") → Override to PCT`);
        return {
          ...result,
          doc_type: lastType.doc_type,
          short_code: lastType.short_code,
          confidence: Math.max(0.75, lastType.confidence * 0.92),
          original_confidence: result.confidence,
          original_short_code: result.short_code,
          applied_sequential_logic: true,
          note: `📄 Trang tiếp theo của PCT (trang 2 có section "ĐĂNG KÝ BIẾN ĐỘNG", nhầm với DDKBD)`
        };
      }
      
      // No sequential applied - this is a new document
      if (result.title_boost_applied && result.confidence >= 0.80) {
        console.log(`✅ No sequential: Title accepted by classifier → New document ${result.short_code} (confidence: ${formatConfidence(result.confidence)}%)`);
      }
    }
    return result;
  };

  // Handle resume scan from saved state
  const handleResumeScan = async (scan, previewMode = 'gcn-only') => {
    try {
      // Auto-switch to scanner tab if needed
      if (onSwitchTab) {
        onSwitchTab('scanner');
      }
      
      console.log(`🔄 Resuming scan: ${scan.scanId} (preview mode: ${previewMode})`);
      
      // Set preview load mode based on user selection
      setPreviewLoadMode(previewMode);
      
      // Load scan data
      const loadResult = await window.electronAPI.loadScanState(scan.scanId);
      if (!loadResult.success) {
        console.error('❌ Load scan state failed:', loadResult.error);
        alert(`❌ Không thể load scan data.\n\nLỗi: ${loadResult.error || 'Unknown error'}\n\nDữ liệu có thể bị corrupt. Hãy xóa scan này và quét lại.`);
        return;
      }
      
      const scanData = loadResult.data;
      
      // Validate scan data structure
      if (!scanData || !scanData.type) {
        console.error('❌ Invalid scan data structure:', scanData);
        alert('❌ Dữ liệu scan không hợp lệ. Vui lòng xóa và quét lại.');
        await window.electronAPI.deleteScanState(scan.scanId);
        setShowResumeDialog(false);
        return;
      }
      
      // Restore state based on scan type
      if (scanData.type === 'folder_scan') {
        // Restore folder scan state WITH RESULTS
        const restoredTabs = scanData.childTabs || [];
        
        // Validate childTabs structure
        if (!Array.isArray(restoredTabs)) {
          console.error('❌ Invalid childTabs structure:', restoredTabs);
          alert('❌ Dữ liệu thư mục không hợp lệ. Vui lòng xóa và quét lại.');
          await window.electronAPI.deleteScanState(scan.scanId);
          setShowResumeDialog(false);
          return;
        }
        
        // ASYNC TAB LOADING: Load tabs in background without blocking UI
        console.log(`🔄 Async loading: Will load ${restoredTabs.length} tabs in background...`);
        
        // Validate tabs array
        const validRestoredTabs = restoredTabs.filter(tab => tab && tab.path && tab.name);
        if (validRestoredTabs.length === 0) {
          console.error('❌ No valid tabs after loading');
          alert('❌ Không có dữ liệu hợp lệ để khôi phục. Vui lòng xóa và quét lại.');
          await window.electronAPI.deleteScanState(scan.scanId);
          setShowResumeDialog(false);
          return;
        }
        
        // Setup initial state
        setParentFolder(scanData.parentFolder || null);
        setCurrentScanId(scan.scanId);
        setActiveTab('folders');
        setTabPreviewsLoaded(new Set());
        
        // Initialize with empty tabs first (just structure, no results)
        const initialTabs = validRestoredTabs.map(tab => ({
          name: tab.name,
          path: tab.path,
          count: tab.count || 0,
          status: 'loading', // Tab is being loaded
          results: []
        }));
        setChildTabs(initialTabs);
        
        // CLOSE DIALOG IMMEDIATELY - don't block user
        setShowResumeDialog(false);
        
        console.log(`📂 Dialog closed. Loading ${initialTabs.length} tabs in background...`);
        
        // Start async loading in background (non-blocking)
        (async () => {
          setIsLoadingTabs(true);
          setTabLoadProgress({ current: 0, total: validRestoredTabs.length });
          
          let loadedCount = 0;
          let errorCount = 0;
          
          for (let i = 0; i < validRestoredTabs.length; i++) {
            const tab = validRestoredTabs[i];
            
            try {
              // Update progress
              setTabLoadProgress({ current: i + 1, total: validRestoredTabs.length });
              
              // Small delay for UI responsiveness (non-blocking)
              await new Promise(resolve => setTimeout(resolve, 50));
              
              console.log(`📥 Loading tab ${i + 1}/${validRestoredTabs.length}: ${tab.name} (${tab.results?.length || 0} files)...`);
              
              // Load this tab's data (without previews)
              const loadedTab = {
                ...tab,
                results: (tab.results || []).map(r => ({
                  ...r,
                  previewUrl: null // Will be lazy-loaded on demand
                }))
              };
              
              // Update state with this tab's data - THIS TAB IS NOW USABLE
              setChildTabs(prev => prev.map((t, idx) => 
                idx === i ? loadedTab : t
              ));
              
              loadedCount++;
              console.log(`✅ Tab ${i + 1}/${validRestoredTabs.length} ready: ${tab.name} (${tab.results?.length || 0} files)`);
              
              // Set active to first completed folder
              if (i === 0 && tab.status === 'done') {
                setActiveChild(tab.path);
                console.log(`📂 Set active to first tab: ${tab.name}`);
              }
              
            } catch (error) {
              errorCount++;
              console.error(`❌ Error loading tab ${i + 1}: ${tab.name}`, error);
              
              // Mark tab as error but continue with others
              setChildTabs(prev => prev.map((t, idx) => 
                idx === i ? { ...t, status: 'error', error: error.message } : t
              ));
            }
          }
          
          // Loading complete
          setIsLoadingTabs(false);
          setTabLoadProgress({ current: 0, total: 0 });
          
          console.log(`✅ Background loading complete: ${loadedCount}/${validRestoredTabs.length} tabs loaded${errorCount > 0 ? `, ${errorCount} errors` : ''}`);
        })(); // IIFE - runs in background
        
        // Check if there are pending tabs to continue scanning
        const pendingFolders = validRestoredTabs.filter(t => t.status === 'pending');
        if (pendingFolders.length > 0) {
          console.log(`🚀 Will auto-resume ${pendingFolders.length} pending folders after loading`);
          setRemainingTabs(pendingFolders);
          // Trigger continue scan after tabs are loaded
          setTimeout(() => {
            setProcessing(true);
            scanAllChildFolders(true); // Resume folder scan
          }, 1000); // Wait for first few tabs to load
        }
        
      } else if (scanData.type === 'file_scan') {
        // Restore file scan state
        const savedResults = scanData.results || [];
        
        // Validate results structure
        if (!Array.isArray(savedResults)) {
          console.error('❌ Invalid results structure:', savedResults);
          alert('❌ Dữ liệu file không hợp lệ. Vui lòng xóa và quét lại.');
          await window.electronAPI.deleteScanState(scan.scanId);
          setShowResumeDialog(false);
          return;
        }
        
        // DO NOT load preview URLs on resume - set to null for lazy loading
        // For file scan, previews are less critical as user can see them immediately
        const validResults = savedResults
          .filter(r => r !== null && r !== undefined)
          .map(r => ({ ...r, previewUrl: null })); // Will be lazy-loaded if needed
        
        if (validResults.length === 0 && savedResults.length > 0) {
          console.error('❌ No valid results after loading');
          alert('❌ Không có dữ liệu hợp lệ để khôi phục. Vui lòng xóa và quét lại.');
          await window.electronAPI.deleteScanState(scan.scanId);
          setShowResumeDialog(false);
          return;
        }
        
        console.log(`🔄 Resume: ${validResults.length} files loaded (previews will be lazy-loaded if needed)`);
        
        setResults(validResults);
        setSelectedFiles(scanData.selectedFiles || []);
        setLastKnownType(scanData.lastKnownType);
        setRemainingFiles(scanData.remainingFiles || []);
        setProgress(scanData.progress || {current: 0, total: 0});
        setCurrentScanId(scan.scanId);
        setActiveTab('files'); // Switch to files tab
        
        // CLOSE DIALOG IMMEDIATELY - don't block user
        setShowResumeDialog(false);
        
        // Auto-trigger continue scan if there are remaining files
        const remainingCount = (scanData.remainingFiles || []).length;
        if (remainingCount > 0) {
          console.log(`🚀 Auto-resuming: ${remainingCount} remaining files`);
          // Trigger continue scan after a short delay to ensure UI is ready
          setTimeout(() => {
            setProcessing(true);
            handleProcessFiles(false, true); // (useCloudBoost=false, isResume=true)
          }, 500);
        } else {
          alert(`✅ Đã khôi phục tất cả ${validResults.length} files (đã scan xong).`);
        }
      }
      
      // Note: setShowResumeDialog(false) is called in both folder_scan and file_scan flows above
      
    } catch (error) {
      console.error('❌ Resume scan error:', error);
      console.error('Error stack:', error.stack);
      
      // Try to delete corrupt scan state
      try {
        await window.electronAPI.deleteScanState(scan.scanId);
        console.log('🗑️ Deleted corrupt scan state');
      } catch (deleteErr) {
        console.error('Failed to delete scan state:', deleteErr);
      }
      
      alert(`❌ Lỗi khi khôi phục scan.\n\nLỗi: ${error.message}\n\nDữ liệu có thể bị corrupt. Đã xóa scan state. Vui lòng quét lại.`);
      setShowResumeDialog(false);
      
      // Reload to refresh state
      window.location.reload();
    }
  };

  // Handle dismiss resume dialog
  const handleDismissResume = async (scanId) => {
    try {
      if (scanId === 'all') {
        // Delete all incomplete scans
        for (const scan of incompleteScans) {
          await window.electronAPI.deleteScanState(scan.scanId);
        }
        console.log(`🗑️ Deleted all ${incompleteScans.length} incomplete scans`);
      } else {
        // Delete specific scan
        await window.electronAPI.deleteScanState(scanId);
        console.log(`🗑️ Deleted scan: ${scanId}`);
      }
      
      setShowResumeDialog(false);
      setIncompleteScans([]);
    } catch (error) {
      console.error('Delete scan error:', error);
    }
  };

  // Post-process GCN documents after batch completion
  const postProcessGCNBatch = (results) => {
    try {
      console.log('🔄 Post-processing GCN batch (DATE-BASED classification)...');
      
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
    
      // STEP 2: Find all GCN documents
      const allGcnDocs = normalizedResults.filter(r => r.short_code === 'GCN');
      
      if (allGcnDocs.length === 0) {
        console.log('✅ No GCN documents found in batch');
        return normalizedResults;
      }
      
      console.log(`📋 Found ${allGcnDocs.length} GCN document(s) to process`);
      
      // Check if results came from batch processing
      const isBatchMode = allGcnDocs.length > 0 && allGcnDocs[0].method && allGcnDocs[0].method.includes('batch');
      
      if (isBatchMode) {
        console.log(`📦 Batch mode detected - Using AI grouping for GCN classification`);
        console.log(`   (AI already grouped pages into documents, no need to pair)`);
        
        // In batch mode, AI already grouped GCN pages
        // Each unique metadata = 1 GCN document
        // Just classify each group based on its metadata
        
        const gcnGroups = new Map();
        
        allGcnDocs.forEach((doc, idx) => {
          const meta = doc.metadata || {};
          const color = meta.color || 'unknown';
          const issueDate = meta.issue_date || null;
          const issueDateConf = meta.issue_date_confidence || null;
          
          // Use unique key: color + issueDate
          const groupKey = `${color}_${issueDate || 'null'}`;
          
          if (!gcnGroups.has(groupKey)) {
            gcnGroups.set(groupKey, {
              files: [],
              color: color,
              issueDate: issueDate,
              issueDateConfidence: issueDateConf,
              parsedDate: parseIssueDate(issueDate, issueDateConf)
            });
          }
          
          gcnGroups.get(groupKey).files.push(doc);
        });
      
      console.log(`📋 Found ${gcnGroups.size} unique GCN document(s) (by metadata)`);
      
      const groupsArray = Array.from(gcnGroups.values());
      
      // Log each group
      groupsArray.forEach((group, idx) => {
        console.log(`  📄 GCN ${idx + 1}: ${group.files.length} pages`);
        console.log(`     🎨 color = ${group.color}`);
        console.log(`     📅 issue_date = ${group.issueDate || 'null'} (${group.issueDateConfidence || 'N/A'})`);
      });
      
      // Classify by color first, then date
      console.log('\n📊 Classifying GCN documents...');
      
      const colors = groupsArray.map(g => g.color).filter(c => c && c !== 'unknown');
      const uniqueColors = [...new Set(colors)];
      const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
      
      console.log(`  🎨 Unique colors: ${uniqueColors.join(', ') || 'none'}`);
      
      if (hasRedAndPink) {
        // Different colors → classify by color
        console.log(`  🎨 Mixed colors → Classify by color`);
        groupsArray.forEach(group => {
          const classification = (group.color === 'red' || group.color === 'orange') ? 'GCNC' : 'GCNM';
          group.files.forEach(file => {
            const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
            if (idx >= 0) {
              normalizedResults[idx].short_code = classification;
              normalizedResults[idx].doc_type = classification;
              console.log(`  ✅ ${file.fileName}: ${group.color} → ${classification}`);
            }
          });
        });
      } else {
        // Same color or no color → classify by date
        console.log(`  📅 Same/no color → Classify by date`);
        
        const groupsWithDate = groupsArray.filter(g => g.parsedDate && g.parsedDate.comparable > 0);
        const groupsWithoutDate = groupsArray.filter(g => !g.parsedDate || g.parsedDate.comparable === 0);
        
        if (groupsWithDate.length >= 2) {
          // Sort by date
          groupsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
          
          console.log('\n📊 Sorted by date:');
          groupsWithDate.forEach((group, idx) => {
            console.log(`  ${idx + 1}. ${group.issueDate} (color: ${group.color})`);
          });
          
          // Oldest = GCNC, others = GCNM
          groupsWithDate.forEach((group, idx) => {
            const classification = (idx === 0) ? 'GCNC' : 'GCNM';
            group.files.forEach(file => {
              const resIdx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (resIdx >= 0) {
                normalizedResults[resIdx].short_code = classification;
                normalizedResults[resIdx].doc_type = classification;
                console.log(`  ✅ ${file.fileName}: ${group.issueDate} → ${classification}`);
              }
            });
          });
          
          // Groups without date → default GCNM
          if (groupsWithoutDate.length > 0) {
            console.log(`  ⚠️ ${groupsWithoutDate.length} group(s) without date → Default GCNM`);
            groupsWithoutDate.forEach(group => {
              group.files.forEach(file => {
                const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
                if (idx >= 0) {
                  normalizedResults[idx].short_code = 'GCNM';
                  normalizedResults[idx].doc_type = 'GCNM';
                  console.log(`  ✅ ${file.fileName}: No date → GCNM (default)`);
                }
              });
            });
          }
        } else if (groupsWithDate.length === 1 && groupsWithoutDate.length === 0) {
          // Only 1 group with date, no other groups → classify as GCNC
          console.log(`  ⚠️ Only 1 GCN group with date → GCNC (only document)`);
          groupsWithDate[0].files.forEach(file => {
            const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
            if (idx >= 0) {
              normalizedResults[idx].short_code = 'GCNC';
              normalizedResults[idx].doc_type = 'GCNC';
              console.log(`  ✅ ${file.fileName}: ${groupsWithDate[0].issueDate} → GCNC (only)`);
            }
          });
        } else if (groupsWithDate.length === 1 && groupsWithoutDate.length > 0) {
          // 1 with date + others without date → First = GCNC, rest = GCNM
          console.log(`  📊 Mixed: 1 with date, ${groupsWithoutDate.length} without → First GCNC, rest GCNM`);
          
          // Group with date = GCNC
          groupsWithDate[0].files.forEach(file => {
            const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
            if (idx >= 0) {
              normalizedResults[idx].short_code = 'GCNC';
              normalizedResults[idx].doc_type = 'GCNC';
              console.log(`  ✅ ${file.fileName}: ${groupsWithDate[0].issueDate} → GCNC (has date)`);
            }
          });
          
          // Other groups without date → GCNM
          groupsWithoutDate.forEach(group => {
            group.files.forEach(file => {
              const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (idx >= 0) {
                normalizedResults[idx].short_code = 'GCNM';
                normalizedResults[idx].doc_type = 'GCNM';
                console.log(`  ✅ ${file.fileName}: No date → GCNM`);
              }
            });
          });
        } else {
          // No dates at all → Fallback to file order (first group = GCNC, rest = GCNM)
          console.log(`  ⚠️ No dates for comparison → Fallback to file order`);
          
          if (groupsArray.length === 1) {
            // Only 1 group → GCNC (assume it's the older one)
            console.log(`  📄 Only 1 GCN group → GCNC (default oldest)`);
            groupsArray[0].files.forEach(file => {
              const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (idx >= 0) {
                normalizedResults[idx].short_code = 'GCNC';
                normalizedResults[idx].doc_type = 'GCNC';
                console.log(`  ✅ ${file.fileName}: Single group → GCNC (default)`);
              }
            });
          } else {
            // Multiple groups → First = GCNC, rest = GCNM (based on file order)
            console.log(`  📊 Multiple groups without dates → First GCNC, rest GCNM (by file order)`);
            groupsArray.forEach((group, groupIdx) => {
              const classification = (groupIdx === 0) ? 'GCNC' : 'GCNM';
              group.files.forEach(file => {
                const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
                if (idx >= 0) {
                  normalizedResults[idx].short_code = classification;
                  normalizedResults[idx].doc_type = classification;
                  console.log(`  ✅ ${file.fileName}: Group ${groupIdx + 1} → ${classification} (file order)`);
                }
              });
            });
          }
        }
      }
      
      console.log('✅ GCN post-processing complete (batch mode, AI-grouped)');
      return normalizedResults;
      
    } else {
      console.log(`📄 Single-file mode detected - Using manual pairing (2 files per GCN)`);
      
      // OLD PAIRING LOGIC for single-file mode
      
      const pairs = [];
      for (let i = 0; i < allGcnDocs.length; i += 2) {
        const page1 = allGcnDocs[i];
        const page2 = allGcnDocs[i + 1];
        
        if (page1 && page2) {
          pairs.push({ page1, page2, pairIndex: i / 2 });
          console.log(`📄 Pair ${i/2 + 1}: ${page1.fileName} (trang 1) + ${page2.fileName} (trang 2)`);
        } else if (page1) {
          // Lẻ page (chỉ có trang 1, không có trang 2)
          pairs.push({ page1, page2: null, pairIndex: i / 2 });
          console.log(`📄 Pair ${i/2 + 1}: ${page1.fileName} (trang 1 only, no pair)`);
        }
      }
      
      console.log(`📋 Total pairs: ${pairs.length}`);
    
    /* ============================================
     * COMMENTED OUT: OLD LOGIC (certificate_number based)
     * ============================================
     * 
     * // Separate GCNs with and without certificate numbers
     * const gcnDocs = allGcnDocs.filter(r => r.certificate_number && r.certificate_number.trim() !== '');
     * const gcnWithoutCert = allGcnDocs.filter(r => !r.certificate_number || r.certificate_number.trim() === '');
     * 
     * console.log(`  📋 With certificate number: ${gcnDocs.length}`);
     * console.log(`  📋 Without certificate number: ${gcnWithoutCert.length}`);
     * 
     * // Group by prefix - ONLY accept valid GCN certificate numbers:
     * // 1. [2 letters][6 numbers]: DE 334187 (old, red)
     * // 2. [2 letters][8 numbers]: AA 01085158 (new, pink)
     * // 3. [4 letters][6 numbers]: S6AB 227162 (OCR error → GCNC)
     * // 
     * // ⚠️ IGNORE 5-digit numbers (e.g., CS 09068, CN.03126)
     * // → These are "Số vào sổ cấp GCN", NOT real certificate numbers!
     * const grouped = {};
     * const unrecognizedCerts = []; // Track unrecognized/invalid formats
     * 
     * gcnDocs.forEach((doc, originalIndex) => {
     *   const certNumber = doc.certificate_number.trim();
     *   
     *   // Try to match VALID certificate patterns
     *   let match = null;
     *   let prefix = null;
     *   let number = null;
     *   
     *   // Pattern 1: [2-4 letters][space/dot][6 or 8 digits ONLY]
     *   match = certNumber.match(/^([A-Z]{2,4})[\s.]*(\d{6}|\d{8})$/i);
     *   
     *   if (match) {
     *     prefix = match[1].toUpperCase();
     *     number = match[2];
     *   } else {
     *     // Pattern 2: [6 or 8 digits only] (no prefix)
     *     match = certNumber.match(/^(\d{6}|\d{8})$/);
     *     if (match) {
     *       prefix = 'NO_PREFIX';
     *       number = match[1];
     *       console.log(`⚠️ Certificate with no prefix: ${certNumber} → Default GCNC`);
     *     } else {
     *       // Invalid format - identify what type
     *       const digitMatch = certNumber.match(/\d+/);
     *       const digitCount = digitMatch ? digitMatch[0].length : 0;
     *       
     *       let reason = 'unknown format';
     *       if (digitCount === 5) {
     *         reason = 'likely "số vào sổ" (5 digits)';
     *       } else if (digitCount >= 10) {
     *         reason = 'likely "mã vạch/barcode" (10+ digits)';
     *       } else if (digitCount < 6) {
     *         reason = 'too short (< 6 digits)';
     *       } else {
     *         reason = 'invalid format';
     *       }
     *       
     *       console.log(`⚠️ Invalid certificate format (${reason}): ${certNumber} → Ignored`);
     *       unrecognizedCerts.push({ ...doc, _invalidReason: reason });
     *       return; // Skip to next document
     *     }
     *   }
     *   
     *   const digitCount = number.length;
     *   const letterCount = prefix === 'NO_PREFIX' ? 0 : prefix.length;
     *   const isOcrError = letterCount === 4; // 4 letters = OCR error
     *   const hasNoPrefix = prefix === 'NO_PREFIX';
     *   
     *   if (!grouped[prefix]) {
     *     grouped[prefix] = [];
     *   }
     *   
     *   grouped[prefix].push({...}); ... rest of old logic
     * ============================================
     * END OF COMMENTED OUT CODE
     * ============================================ */
      
      // NEW LOGIC: Extract color and issue dates from pairs
      const pairsWithData = pairs.map(pair => {
        // Try to get color from metadata (batch mode) or direct fields (single-file mode)
        const color = pair.page1?.metadata?.color || pair.page1?.color || 
                      pair.page2?.metadata?.color || pair.page2?.color || null;
        
        // Try to get issue_date from metadata (batch mode) or direct fields (single-file mode)
        const issueDate = pair.page1?.metadata?.issue_date || pair.page1?.issue_date || 
                          pair.page2?.metadata?.issue_date || pair.page2?.issue_date || null;
        const issueDateConfidence = pair.page1?.metadata?.issue_date_confidence || pair.page1?.issue_date_confidence || 
                                     pair.page2?.metadata?.issue_date_confidence || pair.page2?.issue_date_confidence || null;
        
        console.log(`  🎨 Pair ${pair.pairIndex + 1}: color = ${color || 'unknown'}`);
        console.log(`  📅 Pair ${pair.pairIndex + 1}: issue_date = ${issueDate || 'null'} (${issueDateConfidence || 'N/A'})`);
        
        return {
          ...pair,
          color,
          issueDate,
          issueDateConfidence,
          parsedDate: parseIssueDate(issueDate, issueDateConfidence)
        };
      });
      
      // Classification logic: Priority 1 = Color (if different), Priority 2 = Date
      console.log('\n📊 Classifying GCN pairs...');
      
      // Check if there are different colors in batch
      const colors = pairsWithData.map(p => p.color).filter(Boolean);
      const uniqueColors = [...new Set(colors)];
      const hasMixedColors = uniqueColors.length > 1;
      const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
      
      console.log(`  🎨 Unique colors detected: ${uniqueColors.join(', ') || 'none'}`);
      console.log(`  🎨 Mixed colors (red vs pink)? ${hasMixedColors && hasRedAndPink ? 'Yes' : 'No'}`);
      
      // Step 1: Only classify by color if there are DIFFERENT colors (red vs pink)
      const pairsClassifiedByColor = [];
      const pairsNeedDateComparison = [];
      
      if (hasMixedColors && hasRedAndPink) {
        // Mixed colors (red vs pink) → use color to classify
        console.log(`  🎨 Mixed colors detected → Classify by color`);
        
        pairsWithData.forEach(pair => {
          if (pair.color === 'red' || pair.color === 'orange') {
            // Red/orange → GCNC
            const classification = 'GCNC';
            const colorName = 'đỏ/cam (cũ)';
            const note = `Màu ${colorName} → ${classification}`;
            
            console.log(`  🎨 Pair ${pair.pairIndex + 1}: Màu ${pair.color} → ${classification}`);
            
            [pair.page1, pair.page2].filter(Boolean).forEach(page => {
              const index = normalizedResults.indexOf(page);
              normalizedResults[index] = {
                ...page,
                short_code: classification,
                reasoning: `${page.reasoning || 'GCN'} - ${note}`,
                gcn_classification_note: `📌 ${note} (phân loại theo màu)`
              };
            });
            
            pairsClassifiedByColor.push(pair);
          } else if (pair.color === 'pink') {
            // Pink → GCNM
            const classification = 'GCNM';
            const colorName = 'hồng (mới)';
            const note = `Màu ${colorName} → ${classification}`;
            
            console.log(`  🎨 Pair ${pair.pairIndex + 1}: Màu ${pair.color} → ${classification}`);
            
            [pair.page1, pair.page2].filter(Boolean).forEach(page => {
              const index = normalizedResults.indexOf(page);
              normalizedResults[index] = {
                ...page,
                short_code: classification,
                reasoning: `${page.reasoning || 'GCN'} - ${note}`,
                gcn_classification_note: `📌 ${note} (phân loại theo màu)`
              };
            });
            
            pairsClassifiedByColor.push(pair);
          } else {
            // No color or unknown → need date comparison
            pairsNeedDateComparison.push(pair);
          }
        });
      } else {
        // All same color or no color → need date comparison
        console.log(`  📅 All same color or no color → Classify by date`);
        pairsNeedDateComparison.push(...pairsWithData);
      }
      
      // Step 2: Classify remaining pairs by date
      if (pairsNeedDateComparison.length > 0) {
        console.log('\n📅 Classifying remaining pairs by date...');
        console.log(`  📊 ${pairsNeedDateComparison.length} pair(s) need date comparison`);
        
        if (pairsNeedDateComparison.length === 1) {
          // Only 1 pair → default GCNM
          console.log('📄 Only 1 pair → Default GCNM');
          const pair = pairsNeedDateComparison[0];
          const classification = 'GCNM';
          const dateStr = pair.issueDate || 'không có ngày cấp';
          const colorStr = pair.color ? `màu ${pair.color}` : 'không detect màu';
          const note = `${colorStr}, chỉ 1 GCN → GCNM (mặc định)`;
          
          [pair.page1, pair.page2].filter(Boolean).forEach(page => {
            const index = normalizedResults.indexOf(page);
            normalizedResults[index] = {
              ...page,
              short_code: classification,
              reasoning: `${page.reasoning || 'GCN'} - ${note}`,
              gcn_classification_note: `📌 ${note} (ngày cấp: ${dateStr})`
            };
          });
        } else {
          // Multiple pairs → sort by date
          const sortedPairs = [...pairsNeedDateComparison].sort((a, b) => {
            if (!a.parsedDate && !b.parsedDate) return 0;
            if (!a.parsedDate) return 1;
            if (!b.parsedDate) return -1;
            return a.parsedDate.comparable - b.parsedDate.comparable;
          });
          
          console.log('\n📊 Sorted pairs by date:');
          sortedPairs.forEach((pair, idx) => {
            const dateStr = pair.issueDate || 'null';
            const colorStr = pair.color || 'unknown';
            console.log(`  ${idx + 1}. Pair ${pair.pairIndex + 1}: ${dateStr} (color: ${colorStr})`);
          });
          
          // Classify: oldest = GCNC, others = GCNM
          sortedPairs.forEach((pair, idx) => {
            const isOldest = (idx === 0 && pair.parsedDate !== null);
            const classification = isOldest ? 'GCNC' : 'GCNM';
            const dateStr = pair.issueDate || 'không có ngày cấp';
            const colorStr = pair.color ? `màu ${pair.color}` : 'không detect màu';
            const note = isOldest 
              ? `${colorStr}, ngày cấp sớm nhất: ${dateStr} → GCNC (cũ)` 
              : pair.parsedDate 
                ? `${colorStr}, ngày cấp muộn hơn: ${dateStr} → GCNM (mới)`
                : `${colorStr}, không có ngày cấp → GCNM (mặc định)`;
            
            console.log(`  ✅ Pair ${pair.pairIndex + 1}: ${dateStr} → ${classification}`);
            
            [pair.page1, pair.page2].filter(Boolean).forEach(page => {
              const index = normalizedResults.indexOf(page);
              normalizedResults[index] = {
                ...page,
                short_code: classification,
                reasoning: `${page.reasoning || 'GCN'} - ${note}`,
                gcn_classification_note: `📌 ${note} (phân loại theo ngày)`
              };
            });
          });
        }
      
      } // End of else (single-file mode)
      
      } // End of if-else (batch vs single-file mode)
      
      console.log('✅ GCN post-processing complete (date-based)');
      return normalizedResults;
      
    } catch (error) {
      console.error('❌ Error in GCN post-processing:', error);
      console.error('Stack trace:', error.stack);
      // Return original results if processing fails
      return results;
    }
  };
  
  // Helper function to parse issue date for comparison
  const parseIssueDate = (issueDate, confidence) => {
    if (!issueDate) return null;
    
    try {
      let comparable = 0;
      let parts;
      
      if (confidence === 'full') {
        // DD/MM/YYYY
        parts = issueDate.split('/');
        if (parts.length === 3) {
          const day = parseInt(parts[0], 10);
          const month = parseInt(parts[1], 10);
          const year = parseInt(parts[2], 10);
          comparable = year * 10000 + month * 100 + day;
        }
      } else if (confidence === 'partial') {
        // MM/YYYY
        parts = issueDate.split('/');
        if (parts.length === 2) {
          const month = parseInt(parts[0], 10);
          const year = parseInt(parts[1], 10);
          comparable = year * 10000 + month * 100 + 1; // Assume day 1
        }
      } else if (confidence === 'year_only') {
        // YYYY
        const year = parseInt(issueDate, 10);
        comparable = year * 10000 + 1 * 100 + 1; // Assume Jan 1
      }
      
      return { comparable, original: issueDate };
    } catch (e) {
      console.error(`❌ Error parsing date: ${issueDate}`, e);
      return null;
    }
  };

  // Batch processing using Python batch_processor.py
  const handleProcessFilesBatch = async (filesToProcess, mode) => {
    const modeNames = {
      'fixed': '📦 Gom Cố Định 5 Files',
      'smart': '🧠 Gom Thông Minh'
    };
    
    console.log(`\n${'='*80}`);
    console.log(`🚀 BATCH PROCESSING START`);
    console.log(`   Mode: ${modeNames[mode] || mode}`);
    console.log(`   Files: ${filesToProcess.length}`);
    console.log(`   Engine: ${currentOcrEngine}`);
    console.log(`${'='*80}`);
    
    if (!window.electronAPI) {
      console.error('❌ Electron API not available');
      return null;
    }
    
    try {
      // Filter ONLY image files (skip PDFs)
      const imageFiles = filesToProcess.filter(f => 
        /\.(png|jpg|jpeg|gif|bmp)$/i.test(f.path || f.name || f)
      );
      
      if (imageFiles.length === 0) {
        console.error('❌ No image files found (all PDFs or unsupported)');
        return null;
      }
      
      if (imageFiles.length < filesToProcess.length) {
        const skipped = filesToProcess.length - imageFiles.length;
        console.log(`⏭️ Skipped ${skipped} PDF/unsupported files, processing ${imageFiles.length} images`);
      }
      
      // Get image paths only
      const imagePaths = imageFiles.map(f => f.path || f);
      
      // Call batch processor via IPC
      const batchResult = await window.electronAPI.batchProcessDocuments({
        mode: mode,
        imagePaths: imagePaths,
        ocrEngine: currentOcrEngine
      });
      
      if (!batchResult.success) {
        console.error('❌ Batch processing failed:', batchResult.error);
        return null;
      }
      
      console.log(`✅ Batch processing complete: ${batchResult.results.length} results`);
      
      // Map batch results back to our format
      const mappedResults = [];
      for (const batchItem of batchResult.results) {
        const fileName = batchItem.file_name;
        const filePath = batchItem.file_path;
        
        // Generate preview URL
        let previewUrl = null;
        try {
          const toFileUrl = (p) => (/^[A-Za-z]:\\\\/.test(p) ? 'file:///' + p.replace(/\\\\/g, '/') : 'file://' + p);
          if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(fileName)) {
            previewUrl = await window.electronAPI.readImageDataUrl(filePath);
            if (!previewUrl) previewUrl = toFileUrl(filePath);
          }
        } catch (e) {
          console.error(`Error generating preview for ${fileName}:`, e);
        }
        
        mappedResults.push({
          fileName: fileName,
          filePath: filePath,
          previewUrl: previewUrl,
          isPdf: /\.pdf$/i.test(fileName),
          success: true,
          short_code: batchItem.short_code || 'UNKNOWN',
          confidence: batchItem.confidence || 0.5,
          doc_type: batchItem.short_code || 'UNKNOWN', // Alias
          method: `batch_${mode}`,
          reasoning: batchItem.reasoning || '',
          metadata: batchItem.metadata || {},
          batch_num: batchItem.batch_num,
          // Timing - batch doesn't have per-file timing yet
          startTime: null,
          endTime: null,
          durationMs: null,
          durationSeconds: null
        });
      }
      
      console.log(`✅ Mapped ${mappedResults.length} batch results to UI format`);
      return mappedResults;
      
    } catch (error) {
      console.error('❌ Batch processing error:', error);
      return null;
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
    
    // Initialize timer (only for new scan, not resume)
    if (!isResume) {
      const scanStartTime = Date.now();
      setTimers({
        scanStartTime: scanStartTime,
        scanEndTime: null,
        scanElapsedSeconds: 0,
        fileTimings: [],
        folderTimings: []
      });
      setElapsedTime(0);
      console.log('⏱️ File scan timer started:', new Date(scanStartTime).toLocaleTimeString());
    }
    
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

    // 🚀 CHECK IF BATCH PROCESSING SHOULD BE USED
    const isGeminiEngine = ['gemini-flash', 'gemini-flash-lite', 'gemini-flash-hybrid'].includes(currentOcrEngine);
    const shouldUseBatch = (
      !isResume && // Not resuming
      isGeminiEngine && // Gemini engine
      (batchMode === 'fixed' || batchMode === 'smart') && // Batch mode enabled
      filesToProcess.length >= 3 // At least 3 files (batch makes sense)
    );
    
    if (shouldUseBatch) {
      console.log(`\n${'='*80}`);
      console.log(`🚀 BATCH MODE DETECTED: Using batch processing for ${filesToProcess.length} files`);
      console.log(`   Mode: ${batchMode}`);
      console.log(`   Engine: ${currentOcrEngine}`);
      console.log(`${'='*80}\n`);
      
      setProgress({ current: 0, total: filesToProcess.length });
      setActiveBatchMode(batchMode); // Set active batch mode for UI indicator
      
      // Use batch processing
      const batchResults = await handleProcessFilesBatch(filesToProcess, batchMode);
      
      if (batchResults && batchResults.length > 0) {
        console.log(`✅ Batch processing returned ${batchResults.length} results`);
        
        // Post-process GCN documents
        const processedResults = postProcessGCNBatch(batchResults);
        
        // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
        const finalResults = sortGCNToTop ? sortResultsWithGCNOnTop(processedResults) : processedResults;
        if (sortGCNToTop) {
          console.log(`📊 Sorted results: ${finalResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
        }
        
        // Update results
        setResults(finalResults);
        setProgress({ current: finalResults.length, total: filesToProcess.length });
        
        // Auto-disable previews if too many files to prevent crashes
        if (finalResults.length > 30 && previewsEnabled) {
          console.warn(`⚠️ Auto-disabling previews: ${finalResults.length} files (>30) to prevent memory overflow`);
          setPreviewsEnabled(false);
          alert('⚠️ Preview đã được tắt tự động\n\n' + 
                `Lý do: ${finalResults.length} files (>30)\n\n` +
                'Để tránh crash, bạn có thể:\n' +
                '1. Giữ preview OFF (khuyến nghị)\n' +
                '2. Bật lại preview (rủi ro cao)');
        }
        
        // End timer
        if (timers.scanStartTime) {
          const scanEndTime = Date.now();
          const scanElapsedMs = scanEndTime - timers.scanStartTime;
          const scanElapsedSeconds = Math.floor(scanElapsedMs / 1000);
          const avgTimePerFile = (scanElapsedMs / filesToProcess.length / 1000).toFixed(2);
          
          const modeNames = {
            'fixed': '📦 Gom Cố Định 5 Files',
            'smart': '🧠 Gom Thông Minh'
          };
          
          console.log(`\n${'='*80}`);
          console.log(`✅ BATCH SCAN COMPLETE`);
          console.log(`   Mode: ${modeNames[batchMode] || batchMode}`);
          console.log(`   Files: ${filesToProcess.length}`);
          console.log(`   Total time: ${scanElapsedSeconds}s (${(scanElapsedMs / 1000 / 60).toFixed(2)} minutes)`);
          console.log(`   Avg per file: ${avgTimePerFile}s`);
          console.log(`   Performance: ⚡ ${batchMode === 'fixed' ? '3-5x faster' : '6-9x faster'} than sequential`);
          console.log(`   Cost savings: 💰 ${batchMode === 'fixed' ? '~80%' : '~90%'}`);
          console.log(`${'='*80}\n`);
          
          setTimers(prev => ({
            ...prev,
            scanEndTime: scanEndTime,
            scanElapsedSeconds: scanElapsedSeconds,
            fileTimings: []
          }));
        }
        
        setProcessing(false);
        setActiveBatchMode(null); // Reset batch mode indicator
        return;
      } else {
        // Batch failed - show clear notification
        const errorMsg = batchResults?.error || 'Unknown error';
        console.error('⚠️ BATCH PROCESSING FAILED:', errorMsg);
        console.warn('🔄 FALLBACK: Switching to sequential processing...');
        
        // Show user notification about fallback
        if (window.confirm(
          `⚠️ BATCH PROCESSING GẶP LỖI!\n\n` +
          `Lỗi: ${errorMsg}\n\n` +
          `App sẽ tự động chuyển sang quét TUẦN TỰ (từng trang một).\n\n` +
          `⏱️ Thời gian sẽ lâu hơn (15s/trang thay vì 2s/trang batch)\n\n` +
          `Bạn có muốn:\n` +
          `• OK = Tiếp tục quét tuần tự\n` +
          `• Cancel = Dừng lại, thử lại sau`
        )) {
          console.log('✅ User confirmed fallback to sequential');
          setActiveBatchMode(null);
          // Fall through to sequential processing
        } else {
          console.log('❌ User cancelled scan');
          setProcessing(false);
          setActiveBatchMode(null);
          return;
        }
      }
    }

    // SEQUENTIAL PROCESSING (Original logic)
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
      const fileStartTime = Date.now();
      setProgress({ current: i + 1, total: filesToProcess.length });
      
      console.log(`  ⏱️ File timer started: ${file.name}`);

      let result = await processOffline(file);
      const fileEndTime = Date.now();
      const fileDurationMs = fileEndTime - fileStartTime;
      
      console.log(`  ✅ File completed in ${(fileDurationMs / 1000).toFixed(2)}s`);
      
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
        // Timing data
        startTime: fileStartTime,
        endTime: fileEndTime,
        durationMs: fileDurationMs,
        durationSeconds: (fileDurationMs / 1000).toFixed(2),
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
    
    const processedResults = postProcessGCNBatch(newResults);
    
    console.log('======================================================================');
    console.log('✅ POST-PROCESSING COMPLETE - UPDATING UI');
    console.log('======================================================================');
    
    // Update notification
    if (gcnCount > 0) {
      const gcncCount = processedResults.filter(r => r.short_code === 'GCNC').length;
      const gcnmCount = processedResults.filter(r => r.short_code === 'GCNM').length;
      setPostProcessingStatus(`✅ Hoàn tất: ${gcncCount} GCNC, ${gcnmCount} GCNM`);
      
      // Clear after 5 seconds
      setTimeout(() => setPostProcessingStatus(null), 5000);
    }
    
    // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
    const finalResults = sortGCNToTop ? sortResultsWithGCNOnTop(processedResults) : processedResults;
    if (sortGCNToTop) {
      console.log(`📊 Sorted results: ${finalResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
    }
    
    // Force UI update
    setResults([...finalResults]);
    
    // End timer
    if (!isResume && timers.scanStartTime) {
      const scanEndTime = Date.now();
      const scanElapsedMs = scanEndTime - timers.scanStartTime;
      const scanElapsedSeconds = Math.floor(scanElapsedMs / 1000);
      
      console.log(`⏱️ File scan timer ended: ${new Date(scanEndTime).toLocaleTimeString()}`);
      console.log(`⏱️ Total scan time: ${scanElapsedSeconds}s (${(scanElapsedMs / 1000 / 60).toFixed(2)} minutes)`);
      
      setTimers(prev => ({
        ...prev,
        scanEndTime: scanEndTime,
        scanElapsedSeconds: scanElapsedSeconds
      }));
      
      // Save file timings
      const fileTimings = finalResults.map(r => ({
        fileName: r.fileName,
        startTime: r.startTime,
        endTime: r.endTime,
        durationMs: r.durationMs,
        engineType: currentOcrEngine,
        method: r.method || 'offline_ocr'
      })).filter(t => t.startTime && t.endTime);
      
      setTimers(prev => ({
        ...prev,
        fileTimings: fileTimings
      }));
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
    if (childScanImagesOnly) fileList = fileList.filter(f => (/\.(png|jpg|jpeg|gif|bmp)$/i).test(f.name));

    const files = fileList;
    const childResults = [];
    stopRef.current = false;
    
    // 🚀 CHECK IF BATCH PROCESSING SHOULD BE USED (same logic as File Scan)
    const isGeminiEngine = ['gemini-flash', 'gemini-flash-lite', 'gemini-flash-hybrid'].includes(currentOcrEngine);
    const shouldUseBatch = (
      isGeminiEngine && // Gemini engine
      (batchMode === 'fixed' || batchMode === 'smart') && // Batch mode enabled
      files.length >= 3 // At least 3 files
    );
    
    if (shouldUseBatch) {
      console.log(`\n${'='*80}`);
      console.log(`🚀 FOLDER BATCH MODE DETECTED: Using batch for ${files.length} files in ${childPath}`);
      console.log(`   Mode: ${batchMode}`);
      console.log(`   Engine: ${currentOcrEngine}`);
      console.log(`${'='*80}\n`);
      
      // Use batch processing
      const batchResults = await handleProcessFilesBatch(files, batchMode);
      
      if (batchResults && batchResults.length > 0) {
        console.log(`✅ Folder batch complete: ${batchResults.length} results`);
        
        // Post-process GCN documents
        const processedResults = postProcessGCNBatch(batchResults);
        
        // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
        const finalChildResults = sortGCNToTop ? sortResultsWithGCNOnTop(processedResults) : processedResults;
        if (sortGCNToTop) {
          console.log(`📊 Sorted folder results: ${finalChildResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
        }
        
        setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'done', results: finalChildResults } : t));
        return;
      } else {
        const errorMsg = batchResults?.error || 'Batch returned no results';
        console.error(`⚠️ FOLDER BATCH FAILED for ${childPath}:`, errorMsg);
        console.warn('🔄 FALLBACK: Switching to sequential for this folder...');
        
        // Don't ask user for folder scan (too many prompts), just fallback silently with clear log
        console.log(`📋 Folder will be scanned sequentially (file by file)`);
        // Fall through to sequential processing
      }
    }
    
    // SEQUENTIAL PROCESSING (Original logic)
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
      
      // DO NOT load preview immediately - will be lazy-loaded on-demand
      // This prevents memory overflow when scanning folders with many images
      childResults.push({ 
        fileName: f.name, 
        filePath: f.path, 
        previewUrl: null, // Will be lazy-loaded when user switches to this tab
        isPdf: /\.pdf$/i.test(f.name), 
        ...processedResult 
      });
      
      // IMPORTANT: Skip update if user is editing a result in this tab
      // This prevents input from jumping/resetting while user is typing
      const isEditingThisTab = isEditingResultId && isEditingResultId.startsWith(childTabs[idx]?.path);
      if (!isEditingThisTab) {
        setChildTabs(prev => prev.map((t, j) => j === idx ? { ...t, results: [...childResults] } : t));
      } else {
        console.log(`⏸️ Skipping tab update (user is editing)`);
      }
    }

    // Post-process GCN documents for this child folder
    console.log(`🔄 Child folder scan complete (${childPath}), post-processing GCN documents...`);
    const finalChildResults = postProcessGCNBatch(childResults);
    
    // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
    const sortedResults = sortGCNToTop ? sortResultsWithGCNOnTop(finalChildResults) : finalChildResults;
    if (sortGCNToTop) {
      console.log(`📊 Sorted results: ${sortedResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
    }
    
    setChildTabs(prev => prev.map((t, i) => i === idx ? { ...t, status: 'done', results: sortedResults } : t));
    
    // 💾 MANUAL SAVE after folder complete (before next folder starts)
    if (window.electronAPI?.saveScanState) {
      // Get current state for save
      const currentChildTabs = childTabs.map((t, i) => 
        i === idx ? { ...t, status: 'done', results: finalChildResults } : t
      );
      
      const doneFolders = currentChildTabs.filter(t => t.status === 'done');
      const scanId = currentScanId || `scan_${Date.now()}`;
      
      await window.electronAPI.saveScanState({
        type: 'folder_scan',
        status: 'incomplete',
        parentFolder: parentFolder,
        childTabs: currentChildTabs,
        activeChild: activeChild,
        progress: {
          current: doneFolders.length,
          total: currentChildTabs.length
        },
        engine: currentOcrEngine,
        batchMode: batchMode,
        timestamp: Date.now()
      });
      
      if (!currentScanId) setCurrentScanId(scanId);
      console.log(`💾 Manual save after folder complete: ${doneFolders.length}/${currentChildTabs.length} folders done`);
    }
  };

  // Scan all child folders with pause support
  const scanAllChildFolders = async (isResume = false) => {
    stopRef.current = false;
    setIsFolderPaused(false);
    
    // Initialize timer (only for new scan, not resume)
    if (!isResume) {
      const scanStartTime = Date.now();
      setTimers({
        scanStartTime: scanStartTime,
        scanEndTime: null,
        scanElapsedSeconds: 0,
        fileTimings: [],
        folderTimings: []
      });
      setElapsedTime(0);
      console.log('⏱️ Folder scan timer started:', new Date(scanStartTime).toLocaleTimeString());
    }
    
    let tabsToScan = isResume ? remainingTabs : childTabs.filter(t => t.status !== 'done');
    
    for (const tab of tabsToScan) {
      if (stopRef.current) {
        console.log('❌ Folder scan stopped');
        const remainingIndex = tabsToScan.indexOf(tab);
        setRemainingTabs(tabsToScan.slice(remainingIndex));
        setIsFolderPaused(true);
        return;
      }
      
      const folderStartTime = Date.now();
      console.log(`⏱️ Folder timer started: ${tab.name}`);
      
      await scanChildFolder(tab.path);
      
      const folderEndTime = Date.now();
      const folderDurationMs = folderEndTime - folderStartTime;
      console.log(`✅ Folder "${tab.name}" completed in ${(folderDurationMs / 1000).toFixed(2)}s`);
      
      // Save folder timing
      setTimers(prev => ({
        ...prev,
        folderTimings: [...prev.folderTimings, {
          folderName: tab.name,
          folderPath: tab.path,
          startTime: folderStartTime,
          endTime: folderEndTime,
          durationMs: folderDurationMs,
          fileCount: tab.count || 0
        }]
      }));
    }
    
    // End timer
    if (!isResume && timers.scanStartTime) {
      const scanEndTime = Date.now();
      const scanElapsedMs = scanEndTime - timers.scanStartTime;
      const scanElapsedSeconds = Math.floor(scanElapsedMs / 1000);
      
      console.log(`⏱️ Folder scan timer ended: ${new Date(scanEndTime).toLocaleTimeString()}`);
      console.log(`⏱️ Total folder scan time: ${scanElapsedSeconds}s (${(scanElapsedMs / 1000 / 60).toFixed(2)} minutes)`);
      
      setTimers(prev => ({
        ...prev,
        scanEndTime: scanEndTime,
        scanElapsedSeconds: scanElapsedSeconds
      }));
    }
    
    // 🎉 MARK SCAN COMPLETE
    if (currentScanId && window.electronAPI?.markScanComplete) {
      await window.electronAPI.markScanComplete(currentScanId);
      setCurrentScanId(null);
      console.log(`✅ Marked scan complete`);
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

  // Execute file scan merge (similar to BatchScanner)
  const executeFileMerge = async () => {
    console.log('🚀 executeFileMerge called:', { fileOutputOption, fileMergeSuffix, fileOutputFolder });
    
    setShowFileMergeModal(false);
    setFileMergeInProgress(true);

    try {
      const payload = results
        .filter(r => r.success && r.short_code)
        .map(r => ({ filePath: r.filePath, short_code: r.short_code }));

      if (payload.length === 0) {
        alert('Không có trang hợp lệ để gộp.');
        setFileMergeInProgress(false);
        return;
      }

      // Group files by folder
      const folderGroups = {};
      payload.forEach(item => {
        const result = results.find(r => r.filePath === item.filePath);
        const folder = result?.folder || '';
        if (!folderGroups[folder]) {
          folderGroups[folder] = [];
        }
        folderGroups[folder].push(item);
      });

      let totalMerged = 0;
      let totalSuccess = 0;

      // Merge each folder separately
      for (const [folder, items] of Object.entries(folderGroups)) {
        const mergeOptions = {
          autoSave: true,
          mergeMode: fileOutputOption === 'same_folder' ? 'root' : (fileOutputOption === 'new_folder' ? 'new' : 'custom'),
          mergeSuffix: fileMergeSuffix || '_merged',
          parentFolder: folder,
          customOutputFolder: fileOutputOption === 'custom_folder' ? fileOutputFolder : null
        };
        
        console.log('Merge options:', mergeOptions);
        console.log('Items to merge:', items.length, 'files');
        
        try {
          const merged = await window.electronAPI.mergeByShortCode(items, mergeOptions);
          console.log('Merge result:', merged);
          const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
          totalMerged += (merged || []).length;
          totalSuccess += okCount;
        } catch (mergeErr) {
          console.error('❌ Merge failed for folder:', folder, mergeErr);
          alert(`❌ Lỗi merge folder ${folder}:\n${mergeErr.message}`);
        }
      }

      alert(`✅ Gộp PDF hoàn tất!\n\nThành công: ${totalSuccess}/${totalMerged} file PDF`);
    } catch (err) {
      console.error('Merge error:', err);
      alert(`❌ Lỗi khi gộp PDF: ${err.message}`);
    } finally {
      setFileMergeInProgress(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Resume Dialog */}
      {showResumeDialog && (
        <ResumeDialog
          scans={incompleteScans}
          onResume={handleResumeScan}
          onDismiss={handleDismissResume}
        />
      )}
      
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
            
            {/* Request Delay Info (Read-only) */}
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-700">
                    ⏱️ Delay giữa các request:
                  </label>
                  <div className="text-xs text-gray-600 mt-1">
                    💡 Chỉnh delay trong <strong>Settings</strong> để tránh Rate Limit
                  </div>
                </div>
                <span className="text-sm font-bold text-blue-700">
                  {requestDelay}ms
                </span>
              </div>
            </div>
            
            {/* GCN Sort Toggle */}
            <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-700">
                    📊 Sắp xếp GCN lên đầu sau khi quét
                  </label>
                  <div className="text-xs text-gray-600 mt-1">
                    💡 GCN (GCNC, GCNM) sẽ được hiển thị đầu tiên để dễ kiểm tra
                  </div>
                </div>
                <button
                  onClick={async () => {
                    const newValue = !sortGCNToTop;
                    setSortGCNToTop(newValue);
                    await window.electronAPI.setConfig('sortGCNToTop', newValue);
                    console.log(`📊 GCN sort preference updated: ${newValue}`);
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    sortGCNToTop 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                  }`}
                >
                  {sortGCNToTop ? '✅ BẬT' : '❌ TẮT'}
                </button>
              </div>
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
              <div>
                <span className="text-gray-700 font-medium">
                  Đang xử lý... ({progress.current}/{selectedFiles.length})
                </span>
                {/* Batch Mode Indicator */}
                {activeBatchMode && activeBatchMode !== 'sequential' && (
                  <div className="flex items-center gap-2 mt-1">
                    {activeBatchMode === 'fixed' && (
                      <span className="inline-flex items-center gap-1 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-medium">
                        <span>📦</span> Batch Mode: Gom 5 Files
                      </span>
                    )}
                    {activeBatchMode === 'smart' && (
                      <span className="inline-flex items-center gap-1 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                        <span>🧠</span> Batch Mode: Gom Thông Minh
                      </span>
                    )}
                    <span className="text-xs text-gray-500">
                      (⚡ Nhanh hơn 3-9 lần)
                    </span>
                  </div>
                )}
                {(!activeBatchMode || activeBatchMode === 'sequential') && (
                  <div className="flex items-center gap-2 mt-1">
                    <span className="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                      <span>🔄</span> Tuần Tự (File by File)
                    </span>
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              {/* Live Timer */}
              {timers.scanStartTime && (
                <div className="flex items-center gap-2 bg-orange-50 px-4 py-2 rounded-lg border border-orange-200">
                  <span className="text-lg">⏱️</span>
                  <div className="text-right">
                    <div className="text-xs text-orange-600 font-medium">Thời gian</div>
                    <div className="text-sm font-bold text-orange-900">
                      {Math.floor(elapsedTime / 60)}:{String(elapsedTime % 60).padStart(2, '0')}
                    </div>
                  </div>
                </div>
              )}
              <button 
                onClick={() => { 
                  stopRef.current = true; 
                }} 
                className="px-4 py-2 text-sm rounded-xl bg-orange-600 text-white hover:bg-orange-700 transition-all shadow-sm hover:shadow-md font-medium"
              >
                ⏸️ Tạm dừng
              </button>
            </div>
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
      {/* Performance Stats - File Scan */}
      {activeTab === 'files' && results.length > 0 && timers.scanElapsedSeconds > 0 && (
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span className="text-xl">⏱️</span>
            <span>Thống kê hiệu năng</span>
            {/* Batch Mode Badge in Stats */}
            {results[0]?.method?.includes('batch') && (
              <span className={`ml-2 inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full font-medium ${
                results[0].method.includes('fixed') 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-green-100 text-green-800'
              }`}>
                {results[0].method.includes('fixed') ? '📦 Batch: Gom 5 Files' : '🧠 Batch: Gom Thông Minh'}
              </span>
            )}
            {!results[0]?.method?.includes('batch') && (
              <span className="ml-2 inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                🔄 Tuần Tự
              </span>
            )}
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-white p-3 rounded border border-orange-200">
              <div className="text-xs text-gray-600 mb-1">Tổng thời gian</div>
              <div className="text-lg font-bold text-orange-600">
                {Math.floor(timers.scanElapsedSeconds / 60)}:{String(timers.scanElapsedSeconds % 60).padStart(2, '0')}
              </div>
            </div>
            
            <div className="bg-white p-3 rounded border border-orange-200">
              <div className="text-xs text-gray-600 mb-1">TB mỗi file</div>
              <div className="text-lg font-bold text-blue-600">
                {(timers.scanElapsedSeconds / results.length).toFixed(2)}s
              </div>
            </div>
            
            <div className="bg-white p-3 rounded border border-orange-200">
              <div className="text-xs text-gray-600 mb-1">Engine</div>
              <div className="text-sm font-bold text-gray-700">
                {currentOcrEngine === 'gemini-flash-hybrid' ? '🔄 Hybrid' : currentOcrEngine === 'gemini-flash' ? '🤖 Flash' : currentOcrEngine === 'gemini-flash-lite' ? '⚡ Lite' : currentOcrEngine}
              </div>
            </div>
            
            <div className="bg-white p-3 rounded border border-orange-200">
              <div className="text-xs text-gray-600 mb-1">Tổng files</div>
              <div className="text-lg font-bold text-purple-600">
                {results.length}
              </div>
            </div>
          </div>
          
          {/* Performance Gain Message for Batch Mode */}
          {results[0]?.method?.includes('batch') && (
            <div className="mt-3 bg-green-50 border border-green-300 rounded p-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">⚡</span>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-green-900 mb-1">
                    Batch Processing Performance
                  </div>
                  <div className="text-xs text-green-800">
                    {results[0].method.includes('fixed') && (
                      <>
                        • Nhanh hơn <strong>3-5x</strong> so với tuần tự<br/>
                        • Tiết kiệm <strong>~80%</strong> chi phí API<br/>
                        • Accuracy: <strong>95%+</strong> (context-aware)
                      </>
                    )}
                    {results[0].method.includes('smart') && (
                      <>
                        • Nhanh hơn <strong>6-9x</strong> so với tuần tự<br/>
                        • Tiết kiệm <strong>~90%</strong> chi phí API<br/>
                        • Accuracy: <strong>97%+</strong> (full document context)
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'files' && results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-900">Kết quả ({results.length})</h2>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2"><label className="text-xs text-gray-600">Mật độ:</label><select value={density} onChange={(e) => setDensity(e.target.value)} className="text-xs border rounded px-2 py-1"><option value="high">Cao (5)</option><option value="medium">TB (4)</option><option value="low">Thấp (3)</option></select></div>
              <button onClick={() => {
                if (results.filter(r => r.success && r.short_code).length === 0) {
                  alert('Không có trang hợp lệ để gộp.');
                  return;
                }
                setShowFileMergeModal(true);
              }} disabled={fileMergeInProgress} className="px-4 py-2.5 text-sm bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md font-medium disabled:bg-gray-300">
                {fileMergeInProgress ? '⏳ Đang gộp...' : '📚 Gộp PDF'}
              </button>
            </div>
          </div>
          {/* Memory warning banner */}
          {results.length > 50 && (
            <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 rounded-lg">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <div className="font-bold text-red-900 mb-1">CẢNH BÁO: RỦI RO CRASH CAO!</div>
                  <div className="text-sm text-red-800">
                    • Bạn có <strong>{results.length} files</strong> - rất nhiều!<br/>
                    • Preview đã tắt để tránh crash<br/>
                    • Khuyến nghị: <strong>KHÔNG bật preview</strong> với số lượng này<br/>
                    • Nếu app crash, giảm số files xuống &lt;30
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Pagination controls */}
          {results.length > ITEMS_PER_PAGE && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="text-sm text-gray-700">
                  ⚠️ Hiển thị {Math.min(currentPage * ITEMS_PER_PAGE, results.length)}/{results.length} files (giới hạn {ITEMS_PER_PAGE}/trang)
                </div>
                <button
                  onClick={() => setPreviewsEnabled(!previewsEnabled)}
                  className={`px-3 py-1 text-xs rounded font-medium ${previewsEnabled ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-700'}`}
                  title={previewsEnabled ? 'Click để tắt preview (tiết kiệm RAM)' : 'Click để bật preview'}
                >
                  {previewsEnabled ? '🖼️ Preview ON' : '🖼️ Preview OFF'}
                </button>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  ← Trước
                </button>
                <span className="text-sm text-gray-600">
                  Trang {currentPage}/{Math.ceil(results.length / ITEMS_PER_PAGE)}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(Math.ceil(results.length / ITEMS_PER_PAGE), p + 1))}
                  disabled={currentPage >= Math.ceil(results.length / ITEMS_PER_PAGE)}
                  className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  Sau →
                </button>
              </div>
            </div>
          )}
          
          <div className={`grid gap-3 ${gridColsClass}`}>
            {results
              .slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)
              .map((result, idx) => (
              <div key={idx} className="p-3 border rounded-lg bg-white">
                <div className="mb-2">
                  {previewsEnabled && result.previewUrl ? (
                    <img src={result.previewUrl} alt={result.fileName} className="w-full h-40 object-contain border rounded bg-gray-50" />
                  ) : !previewsEnabled ? (
                    <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">
                      🖼️ Preview disabled<br/>(tiết kiệm RAM)
                    </div>
                  ) : (
                    <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">{result.isPdf ? 'PDF (không có preview)' : 'Không có preview'}</div>
                  )}
                </div>
                <div className="text-sm font-medium truncate" title={result.fileName}>{result.fileName}</div>
                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">{getMethodBadge(result.method)}<span className="ml-auto font-semibold">{formatConfidence(result.confidence)}%</span></div>
                <div className="mt-2 text-xs text-gray-600">Loại: {result.doc_type} | Mã: <span className="text-blue-600">{result.short_code}</span></div>
                {/* Timing Info */}
                {result.durationSeconds && (
                  <div className="mt-1 text-xs text-orange-600 flex items-center gap-1">
                    <span>⏱️</span>
                    <span className="font-medium">{result.durationSeconds}s</span>
                  </div>
                )}
                <div className="mt-2 p-2 bg-gray-50 border rounded"><InlineShortCodeEditor value={result.short_code} onChange={(newCode) => { setResults(prev => prev.map((r, i) => i === idx ? { ...r, short_code: newCode } : r)); }} /></div>
                
                {/* Action Buttons */}
                <div className="mt-2 flex gap-2">
                  {result.previewUrl && (
                    <button
                      onClick={() => setSelectedPreview(result.previewUrl)}
                      className="flex-1 text-xs text-blue-600 hover:bg-blue-50 py-1 px-2 rounded border border-blue-200"
                    >
                      🔍 Phóng to
                    </button>
                  )}
                  <button
                    onClick={() => {
                      if (window.confirm(`Xóa file "${result.fileName}"?`)) {
                        setResults(prev => prev.filter((_, i) => i !== idx));
                      }
                    }}
                    className="flex-1 text-xs text-red-600 hover:bg-red-50 py-1 px-2 rounded border border-red-200"
                  >
                    🗑️ Xóa
                  </button>
                </div>
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
            
            {/* GCN Sort Toggle */}
            <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-700">
                    📊 Sắp xếp GCN lên đầu sau khi quét
                  </label>
                  <div className="text-xs text-gray-600 mt-1">
                    💡 GCN (GCNC, GCNM) sẽ được hiển thị đầu tiên để dễ kiểm tra
                  </div>
                </div>
                <button
                  onClick={async () => {
                    const newValue = !sortGCNToTop;
                    setSortGCNToTop(newValue);
                    await window.electronAPI.setConfig('sortGCNToTop', newValue);
                    console.log(`📊 GCN sort preference updated: ${newValue}`);
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    sortGCNToTop 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                  }`}
                >
                  {sortGCNToTop ? '✅ BẬT' : '❌ TẮT'}
                </button>
              </div>
            </div>
            
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
          
          {/* Progressive Tab Loading Indicator */}
          {isLoadingTabs && tabLoadProgress.total > 0 && (
            <div className="mb-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-300 shadow-sm">
              <div className="flex items-center space-x-3 mb-3">
                <div className="animate-spin text-2xl">⏳</div>
                <div className="flex-1">
                  <div className="text-sm text-blue-900 font-bold">
                    Đang khôi phục dữ liệu... ({tabLoadProgress.current}/{tabLoadProgress.total} thư mục)
                  </div>
                  <div className="text-xs text-blue-700 mt-1">
                    Load dần từng thư mục để tránh quá tải RAM
                  </div>
                </div>
              </div>
              {/* Progress bar */}
              <div className="w-full bg-blue-200 rounded-full h-3 overflow-hidden shadow-inner">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-300 ease-out relative shadow-md" 
                  style={{ width: `${(tabLoadProgress.current / tabLoadProgress.total) * 100}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-40 animate-pulse"></div>
                </div>
              </div>
            </div>
          )}
          
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
                className={`px-3 py-2 text-xs rounded-xl border flex items-center gap-2 min-w-[120px] max-w-[180px] relative ${activeChild === t.path ? 'bg-blue-50 border-blue-300 text-blue-900 font-medium' : 'bg-white hover:bg-gray-50 border-gray-300'}`}
              >
                {/* UNKNOWN badge */}
                {(() => {
                  const unknownCount = (t.results || []).filter(r => r.short_code === 'UNKNOWN').length;
                  if (unknownCount > 0 && t.status === 'done') {
                    return (
                      <span 
                        className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg border-2 border-white"
                        title={`${unknownCount} file(s) UNKNOWN`}
                      >
                        {unknownCount}
                      </span>
                    );
                  }
                  return null;
                })()}
                
                <span className="truncate flex-1">{t.name} ({t.count})</span>
                {t.status === 'error' ? (
                  <span className="text-red-600 flex-shrink-0" title={t.error}>⚠️</span>
                ) : t.status === 'loading' ? (
                  <span className="animate-pulse flex-shrink-0">⏳</span>
                ) : t.status === 'scanning' ? (
                  <span className="animate-spin flex-shrink-0">⚙️</span>
                ) : t.status === 'done' ? (
                  <span className="text-green-600 flex-shrink-0">✓</span>
                ) : (
                  <span className="text-gray-400 flex-shrink-0">○</span>
                )}
              </button>
            ))}
          </div>
          
          {/* Tab content - LAZY RENDER: Only render active tab */}
          <div className="mt-3">
            {(() => {
              const activeTab = childTabs.find(t => t.path === activeChild);
              if (!activeTab) return null;
              const t = activeTab;
              return (
                <div key={t.path}>
                  {/* UNKNOWN Files Counter */}
                  {(() => {
                    const unknownCount = (t.results || []).filter(r => r.short_code === 'UNKNOWN').length;
                    if (unknownCount > 0) {
                      return (
                        <div className="mb-3 p-3 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border-2 border-red-300">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <span className="text-2xl">⚠️</span>
                              <div>
                                <div className="text-sm text-red-900 font-bold">
                                  {unknownCount} file{unknownCount > 1 ? 's' : ''} chưa phân loại (UNKNOWN)
                                </div>
                                <div className="text-xs text-red-700 mt-0.5">
                                  Cần xem xét và đặt lại mã phân loại cho các file này
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-red-800 bg-red-100 px-3 py-1 rounded-full font-mono font-bold">
                              <span>❌</span>
                              <span>{unknownCount}/{(t.results || []).length}</span>
                            </div>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}
                  
                  {/* Preview Mode Info */}
                  {previewLoadMode !== 'all' && (
                    <div className="mb-3 p-2 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg border border-cyan-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm">
                            {previewLoadMode === 'none' ? '🚫' : '⭐'}
                          </span>
                          <span className="text-xs font-medium text-cyan-900">
                            {previewLoadMode === 'none' 
                              ? 'Chế độ: Không hiển thị ảnh (tiết kiệm RAM)'
                              : 'Chế độ: Chỉ hiển thị ảnh GCN (tiết kiệm RAM)'}
                          </span>
                        </div>
                        <button
                          onClick={() => setPreviewLoadMode(previewLoadMode === 'none' ? 'gcn-only' : previewLoadMode === 'gcn-only' ? 'all' : 'none')}
                          className="text-xs bg-cyan-600 hover:bg-cyan-700 text-white px-2 py-1 rounded"
                          title="Nhấn để thay đổi chế độ"
                        >
                          Đổi chế độ
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Manual Load Preview Button */}
                  {t.status === 'done' && !tabPreviewsLoaded.has(activeChild) && (
                    <div className="mb-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-xl">🖼️</span>
                          <div>
                            <div className="text-sm text-green-900 font-medium">Preview chưa được load</div>
                            <div className="text-xs text-green-700 mt-0.5">
                              Nhấn nút để load preview images cho tab này
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            // Trigger lazy loading by marking tab as active
                            setTabPreviewsLoaded(prev => {
                              const newSet = new Set(prev);
                              newSet.delete(activeChild); // Remove to trigger reload
                              return newSet;
                            });
                            // Force re-trigger useEffect
                            setTimeout(() => {
                              setActiveChild(null);
                              setTimeout(() => setActiveChild(t.path), 10);
                            }, 10);
                          }}
                          disabled={isLoadingPreviews}
                          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm transition-all shadow-md hover:shadow-lg"
                        >
                          {isLoadingPreviews ? (
                            <>
                              <span className="animate-spin">⏳</span>
                              <span>Đang load...</span>
                            </>
                          ) : (
                            <>
                              <span>📥</span>
                              <span>Load Preview</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Error indicator for failed tab */}
                  {t.status === 'error' && (
                    <div className="mb-3 p-3 bg-red-50 rounded-xl border border-red-200">
                      <div className="flex items-center space-x-3">
                        <span className="text-xl">⚠️</span>
                        <div>
                          <div className="text-sm text-red-900 font-medium">Lỗi khi load thư mục "{t.name}"</div>
                          <div className="text-xs text-red-700 mt-1">
                            {t.error || 'Không thể load dữ liệu'} - Tab này bị bỏ qua
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Loading indicator for preview loading */}
                  {isLoadingPreviews && (
                    <div className="mb-3 p-2 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin text-sm">⏳</div>
                        <span className="text-xs text-purple-900 font-medium">
                          Đang tải preview images{previewLoadMode === 'gcn-only' ? ' (chỉ GCN)' : ''}...
                        </span>
                      </div>
                    </div>
                  )}
                  
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
                  
                  {/* Rescan folder button + Merge button */}
                  {t.status === 'done' && (t.results || []).length > 0 && (
                    <div className="mb-3 p-3 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl border border-orange-200">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">
                            📂 {t.name} - {(t.results || []).length} files
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            Nếu bạn phát hiện nhiều file bị lỗi. Hãy sử dụng tính năng quét lại thư mục này để sửa
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              setActiveChildForMerge(t);
                              setShowMergeModal(true);
                            }}
                            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors"
                          >
                            📚 Gộp thư mục này
                          </button>
                          <button
                            onClick={async () => {
                              if (window.confirm(`Quét lại thư mục "${t.name}"?\n\nTất cả kết quả cũ sẽ bị xóa và quét lại từ đầu.`)) {
                                const idx = childTabs.findIndex(x => x.path === t.path);
                                if (idx >= 0) {
                                  // Reset status and results
                                  setChildTabs(prev => prev.map((ct, i) => 
                                    i === idx ? { ...ct, status: 'pending', results: [] } : ct
                                  ));
                                  // Rescan this folder
                                  await scanChildFolder(idx);
                                }
                              }
                            }}
                            className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors"
                          >
                            🔄 Quét lại thư mục này
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Pagination for folder results */}
                  {(t.results || []).length > ITEMS_PER_PAGE && (
                    <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center justify-between text-xs">
                      <div className="text-gray-700">
                        ⚠️ {Math.min(currentPage * ITEMS_PER_PAGE, (t.results || []).length)}/{(t.results || []).length} files (giới hạn {ITEMS_PER_PAGE}/trang)
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          className="px-2 py-1 bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
                        >
                          ←
                        </button>
                        <span className="text-gray-600">
                          {currentPage}/{Math.ceil((t.results || []).length / ITEMS_PER_PAGE)}
                        </span>
                        <button
                          onClick={() => setCurrentPage(p => Math.min(Math.ceil((t.results || []).length / ITEMS_PER_PAGE), p + 1))}
                          disabled={currentPage >= Math.ceil((t.results || []).length / ITEMS_PER_PAGE)}
                          className="px-2 py-1 bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
                        >
                          →
                        </button>
                      </div>
                    </div>
                  )}
                  
                  <div className={`grid gap-3 ${gridColsClass}`}>
                    {(t.results || [])
                      .slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)
                      .map((r, idx) => (
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
                            onEditStart={() => setIsEditingResultId(`${t.path}-${idx}`)}
                            onEditEnd={() => setIsEditingResultId(null)}
                          />
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="mt-2 flex gap-2">
                          {r.previewUrl && (
                            <button
                              onClick={() => setSelectedPreview(r.previewUrl)}
                              className="flex-1 text-xs text-blue-600 hover:bg-blue-50 py-1 px-2 rounded border border-blue-200"
                            >
                              🔍 Phóng to
                            </button>
                          )}
                          <button
                            onClick={() => {
                              if (window.confirm(`Xóa file "${r.fileName}"?`)) {
                                setChildTabs(prev => prev.map((ct, j) => {
                                  if (j !== childTabs.findIndex(x => x.path === t.path)) return ct;
                                  const newRes = [...(ct.results || [])];
                                  newRes.splice(idx, 1);
                                  return { ...ct, results: newRes };
                                }));
                              }
                            }}
                            className="flex-1 text-xs text-red-600 hover:bg-red-50 py-1 px-2 rounded border border-red-200"
                          >
                            🗑️ Xóa
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}
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

      {/* Folder Scan Merge Modal */}
      {showMergeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📚 {activeChildForMerge ? `Gộp thư mục "${activeChildForMerge.name}"` : 'Gộp tất cả thư mục con'}
            </h3>
            
            {/* Output Location */}
            <div className="space-y-3 mb-4">
              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="mergeOption"
                    value="root"
                    checked={mergeOption === 'root'}
                    onChange={(e) => setMergeOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📁 Lưu trong thư mục gốc</span>
                </div>
                <p className="text-xs text-gray-500 ml-6">PDF sẽ được lưu trực tiếp vào thư mục gốc của mỗi subfolder</p>
              </label>

              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="mergeOption"
                    value="new"
                    checked={mergeOption === 'new'}
                    onChange={(e) => setMergeOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📂 Tạo thư mục mới trong mỗi subfolder</span>
                </div>
                <p className="text-xs text-gray-500 ml-6">Tạo subfolder "_merged" hoặc tùy chỉnh trong mỗi thư mục con</p>
              </label>

              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="mergeOption"
                    value="custom"
                    checked={mergeOption === 'custom'}
                    onChange={(e) => setMergeOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📍 Chọn thư mục tùy chỉnh</span>
                </div>
                {mergeOption === 'custom' && (
                  <div className="ml-6 mt-2">
                    <button
                      onClick={async () => {
                        const folder = await window.electronAPI.selectFolder();
                        if (folder) setFileOutputFolder(folder);
                      }}
                      className="px-3 py-1.5 text-xs bg-gray-100 rounded hover:bg-gray-200 border"
                    >
                      {fileOutputFolder ? `✅ ${fileOutputFolder}` : 'Chọn thư mục...'}
                    </button>
                  </div>
                )}
              </label>
            </div>

            {/* Merge Suffix */}
            {mergeOption === 'new' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tên thư mục con (suffix):
                </label>
                <input
                  type="text"
                  value={mergeSuffix}
                  onChange={(e) => setMergeSuffix(e.target.value)}
                  placeholder="_merged"
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
                {parentFolder && (
                  <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    Ví dụ: <span className="font-mono">{parentFolder.split(/[\\\/]/).pop()}{mergeSuffix}</span>
                  </div>
                )}
              </div>
            )}

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
                  
                  const tabsToMerge = activeChildForMerge ? [activeChildForMerge] : childTabs;
                  let totalMerged = 0;
                  let totalSuccess = 0;
                  
                  // Merge each folder separately (like BatchScanner)
                  for (const ct of tabsToMerge) {
                    const payload = (ct.results || [])
                      .filter(r => r.success && r.short_code)
                      .map(r => ({ filePath: r.filePath, short_code: r.short_code }));
                    if (payload.length === 0) continue;
                    
                    // Each folder has its own parentFolder (ct.path)
                    const mergeOptions = {
                      autoSave: true,
                      mergeMode: mergeOption,
                      mergeSuffix: mergeSuffix || '_merged',
                      parentFolder: ct.path, // Use subfolder path as parent
                      customOutputFolder: mergeOption === 'custom' ? fileOutputFolder : null
                    };
                    
                    console.log(`📚 Merge folder ${ct.name}:`, mergeOptions);
                    
                    try {
                      const merged = await window.electronAPI.mergeByShortCode(payload, mergeOptions);
                      console.log(`✅ Merged folder ${ct.name}:`, merged);
                      const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
                      totalMerged += (merged || []).length;
                      totalSuccess += okCount;
                      
                      (merged || []).forEach(m => {
                        if (m && m.success && m.path) {
                          finalLines.push(`✓ [${ct.name}] ${m.short_code}: ${m.path}`);
                        }
                      });
                    } catch (mergeErr) {
                      console.error(`❌ Merge failed for ${ct.name}:`, mergeErr);
                      finalLines.push(`✗ [${ct.name}] Lỗi: ${mergeErr.message}`);
                    }
                  }
                  
                  setChildMergeReport(finalLines);
                  setActiveChildForMerge(null);
                  
                  alert(`✅ Gộp PDF hoàn tất!\n\nThành công: ${totalSuccess}/${totalMerged} file PDF`);
                }}
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-all shadow-sm font-medium"
              >
                Bắt đầu gộp
              </button>
            </div>
          </div>
        </div>
      )}

      {/* File Scan Merge Modal */}
      {showFileMergeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Tùy chọn gộp PDF</h3>
            
            {/* Output Location */}
            <div className="space-y-3 mb-4">
              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="fileOutputOption"
                    value="same_folder"
                    checked={fileOutputOption === 'same_folder'}
                    onChange={(e) => setFileOutputOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📁 Lưu trong thư mục gốc của file</span>
                </div>
                <p className="text-xs text-gray-500 ml-6">PDF sẽ được lưu cùng thư mục với ảnh gốc</p>
              </label>

              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="fileOutputOption"
                    value="new_folder"
                    checked={fileOutputOption === 'new_folder'}
                    onChange={(e) => setFileOutputOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📂 Tạo thư mục mới trong thư mục gốc</span>
                </div>
                <p className="text-xs text-gray-500 ml-6">Tạo subfolder "_merged" hoặc tùy chỉnh</p>
              </label>

              <label className="block">
                <div className="flex items-center gap-2 mb-2">
                  <input
                    type="radio"
                    name="fileOutputOption"
                    value="custom_folder"
                    checked={fileOutputOption === 'custom_folder'}
                    onChange={(e) => setFileOutputOption(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">📍 Chọn thư mục tùy chỉnh</span>
                </div>
                {fileOutputOption === 'custom_folder' && (
                  <div className="ml-6 mt-2">
                    <button
                      onClick={async () => {
                        const folder = await window.electronAPI.selectFolder();
                        if (folder) setFileOutputFolder(folder);
                      }}
                      className="px-3 py-1.5 text-xs bg-gray-100 rounded hover:bg-gray-200 border"
                    >
                      {fileOutputFolder ? `✅ ${fileOutputFolder}` : 'Chọn thư mục...'}
                    </button>
                  </div>
                )}
              </label>
            </div>

            {/* Merge Suffix */}
            {fileOutputOption === 'new_folder' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tên thư mục con (suffix):
                </label>
                <input
                  type="text"
                  value={fileMergeSuffix}
                  onChange={(e) => setFileMergeSuffix(e.target.value)}
                  placeholder="_merged"
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center gap-3 mt-6">
              <button
                onClick={() => setShowFileMergeModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={executeFileMerge}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-sm font-medium"
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
