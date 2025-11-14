import React, { useState, useEffect, useRef } from 'react';
import ResumeDialog from './ResumeDialog';
import InlineShortCodeEditor from './InlineShortCodeEditor';
import ActionButtonGroup from './ActionButtonGroup';
import { getDocumentHighlight, getRowHighlight, getDocumentBadge } from '../utils/documentHighlight';

function BatchScanner({ onSwitchTab }) {
  // State
  const [txtFilePath, setTxtFilePath] = useState(null);
  const [ocrEngine, setOcrEngine] = useState('tesseract');
  const [outputOption, setOutputOption] = useState('same_folder');
  const [mergeSuffix, setMergeSuffix] = useState('_merged');
  const [outputFolder, setOutputFolder] = useState(null);
  
  // New workflow states
  const [isLoadingFolders, setIsLoadingFolders] = useState(false);
  const [discoveredFolders, setDiscoveredFolders] = useState([]); // [{path, name, imageCount, valid, selected}]
  const [isScanning, setIsScanning] = useState(false);
  const stopRef = useRef(false); // Use ref for stop button (mutable across renders)
  const [progress, setProgress] = useState({ 
    currentFolder: '',
    currentFile: '',
    processedFiles: 0,
    totalFiles: 0,
    processedFolders: 0,
    totalFolders: 0
  });
  const [scanResults, setScanResults] = useState(null); // Scan statistics
  const [fileResults, setFileResults] = useState([]); // Individual file results with preview
  const [errors, setErrors] = useState([]);
  const [skippedFolders, setSkippedFolders] = useState([]);
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeInProgress, setMergeInProgress] = useState(false);
  const [density, setDensity] = useState('medium');
  const [selectedPreview, setSelectedPreview] = useState(null);
  
  // Folder tabs state
  const [folderTabs, setFolderTabs] = useState([]); // [{path, name, count, status, files: []}]
  const [activeFolder, setActiveFolder] = useState(null);
  const [isMergeAll, setIsMergeAll] = useState(false); // Track if merging all folders
  const [lastKnownType, setLastKnownType] = useState(null); // For sequential naming (UNKNOWN fallback)
  const [duplicateFolders, setDuplicateFolders] = useState([]); // Track duplicate folder names: [{name, paths: [path1, path2]}]
  
  // Batch processing mode
  const [batchMode, setBatchMode] = useState('sequential'); // 'sequential', 'fixed', 'smart'
  
  // GCN sorting preference
  const [sortGCNToTop, setSortGCNToTop] = useState(true); // User preference: sort GCN to top after scan
  
  // Auto-save preference
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true); // User preference: auto-save scan state
  
  // Auto-save & Resume
  const [showResumeDialog, setShowResumeDialog] = useState(false);
  const [incompleteScans, setIncompleteScans] = useState([]);
  const [currentScanId, setCurrentScanId] = useState(null);
  const [foldersPreviewsLoaded, setFoldersPreviewsLoaded] = useState(new Set()); // Track which folders have previews loaded
  const [loadingPreviewFor, setLoadingPreviewFor] = useState(null); // Track which folder is loading previews
  const [isEditingFileId, setIsEditingFileId] = useState(null); // Track which file is being edited (prevent update conflicts)
  
  // Timer states
  const [timers, setTimers] = useState({
    batchStartTime: null,
    batchEndTime: null,
    batchElapsedSeconds: 0,
    fileTimings: [], // [{fileName, startTime, endTime, durationMs, engineType}]
    folderTimings: [], // [{folderName, startTime, endTime, durationMs, fileCount}]
  });
  const [elapsedTime, setElapsedTime] = useState(0); // Live elapsed time in seconds
  const timerIntervalRef = useRef(null);

  // Live timer effect - update elapsed time every second
  useEffect(() => {
    if (isScanning && timers.batchStartTime) {
      timerIntervalRef.current = setInterval(() => {
        const now = Date.now();
        const elapsedMs = now - timers.batchStartTime;
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
  }, [isScanning, timers.batchStartTime]);
  
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
  
  // Auto-save when folderTabs change (folders complete) - IMMEDIATE SAVE
  useEffect(() => {
    const autoSave = async () => {
      // Skip if auto-save is disabled
      if (!autoSaveEnabled) {
        console.log('💾 Auto-save disabled, skipping...');
        return;
      }
      
      const doneFolders = folderTabs.filter(t => t.status === 'done');
      const allDone = folderTabs.length > 0 && folderTabs.every(t => t.status === 'done');
      
      if (folderTabs.length > 0 && doneFolders.length > 0 && !allDone && window.electronAPI?.saveScanState) {
        let scanId = currentScanId;
        if (!scanId) {
          scanId = `batch_scan_${Date.now()}`;
          setCurrentScanId(scanId);
        }
        
        await window.electronAPI.saveScanState({
          scanId: scanId,
          type: 'batch_scan',
          status: 'incomplete',
          // Strip previewUrl to reduce size
          folderTabs: folderTabs.map(t => ({
            ...t,
            files: t.files?.map(f => ({ ...f, previewUrl: null })) || []
          })),
          discoveredFolders: discoveredFolders,
          fileResults: fileResults.map(r => ({ ...r, previewUrl: null })),
          txtFilePath: txtFilePath,
          progress: {
            current: doneFolders.length,
            total: folderTabs.length
          },
          engine: ocrEngine,
          batchMode: batchMode,
          timestamp: Date.now()
        });
        
        console.log(`💾 Auto-saved immediately: ${doneFolders.length}/${folderTabs.length} folders done`);
      }
    };
    autoSave(); // Execute immediately (no debounce)
  }, [folderTabs, currentScanId, discoveredFolders, fileResults, txtFilePath, ocrEngine, batchMode, autoSaveEnabled]);
  
  // Load OCR engine from config on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const engine = await window.electronAPI.getConfig('ocrEngine');
        if (engine) setOcrEngine(engine);
        
        // Load batch mode
        const savedBatchMode = await window.electronAPI.getConfig('batchMode');
        if (savedBatchMode) {
          setBatchMode(savedBatchMode);
          console.log(`📦 Loaded batch mode: ${savedBatchMode}`);
        }
        
        // Load GCN sort preference
        const savedSortGCN = await window.electronAPI.getConfig('sortGCNToTop');
        if (savedSortGCN !== undefined && savedSortGCN !== null) {
          setSortGCNToTop(savedSortGCN);
          console.log(`📊 Loaded GCN sort preference: ${savedSortGCN}`);
        }
        
        // Load auto-save preference
        const savedAutoSave = await window.electronAPI.getConfig('autoSaveEnabled');
        if (savedAutoSave !== undefined && savedAutoSave !== null) {
          setAutoSaveEnabled(savedAutoSave);
          console.log(`💾 Loaded auto-save preference: ${savedAutoSave}`);
        }
        
        // Check for incomplete scans
        const incompleteResult = await window.electronAPI.getIncompleteScans();
        if (incompleteResult.success && incompleteResult.scans.length > 0) {
          const batchScans = incompleteResult.scans.filter(s => s.type === 'batch_scan');
          if (batchScans.length > 0) {
            console.log(`🔄 Found ${batchScans.length} incomplete batch scan(s)`);
            setIncompleteScans(batchScans);
            setShowResumeDialog(true);
          }
        }
      } catch (err) {
        console.error('Failed to load config:', err);
      }
    };
    loadConfig();

    // Listen for progress updates
    const handleProgress = (data) => {
      const logText = String(data);
      
      // Parse folder progress: "📂 [1/3] Processing: C:\Folder1"
      const folderMatch = logText.match(/📂\s*\[(\d+)\/(\d+)\]\s*Processing:\s*(.+)/);
      if (folderMatch) {
        const folderPath = folderMatch[3].trim();
        const folderName = folderPath.split(/[/\\]/).pop() || folderPath;
        
        setProgress(prev => ({
          ...prev,
          processedFolders: parseInt(folderMatch[1]),
          totalFolders: parseInt(folderMatch[2]),
          currentFolder: folderPath
        }));

        // Update or create folder tab with 'scanning' status
        setFolderTabs(prev => {
          const existing = prev.find(t => t.path === folderPath);
          if (existing) {
            return prev.map(t => 
              t.path === folderPath ? { ...t, status: 'scanning' } : t
            );
          } else {
            return [...prev, {
              path: folderPath,
              name: folderName,
              count: 0,
              status: 'scanning',
              files: []
            }];
          }
        });
      }

      // Parse file progress: "   [1/10] Processing: image001.jpg"
      const fileMatch = logText.match(/\s*\[(\d+)\/(\d+)\]\s*Processing:\s*(.+)/);
      if (fileMatch) {
        setProgress(prev => ({
          ...prev,
          processedFiles: parseInt(fileMatch[1]),
          totalFiles: parseInt(fileMatch[2]),
          currentFile: fileMatch[3].trim()
        }));
      }

      // Parse found files: "🖼️  Found 10 image file(s)"
      const foundMatch = logText.match(/Found\s+(\d+)\s+image/);
      if (foundMatch) {
        const count = parseInt(foundMatch[1]);
        setProgress(prev => ({
          ...prev,
          totalFiles: count
        }));

        // Update current folder tab count
        setFolderTabs(prev => 
          prev.map(t => 
            t.path === progress.currentFolder ? { ...t, count } : t
          )
        );
      }
    };

    if (window.electronAPI && window.electronAPI.onBatchScanProgress) {
      window.electronAPI.onBatchScanProgress(handleProgress);
    }

    return () => {
      // Cleanup listener if needed
    };
  }, []);

  // Handle TXT file selection
  const handleSelectTxtFile = async () => {
    try {
      const filePath = await window.electronAPI.selectTxtFile();
      if (filePath) {
        setTxtFilePath(filePath);
        // Reset results when new file is selected
        setScanResults(null);
        setFileResults([]);
        setErrors([]);
        setSkippedFolders([]);
      }
    } catch (err) {
      alert(`Lỗi chọn file: ${err.message}`);
    }
  };

  // Handle output folder selection
  const handleSelectOutputFolder = async () => {
    try {
      const folderPath = await window.electronAPI.selectFolder();
      if (folderPath) {
        setOutputFolder(folderPath);
      }
    } catch (err) {
      alert(`Lỗi chọn thư mục: ${err.message}`);
    }
  };

  // Step 1: Load and validate folders from TXT
  const handleLoadFolders = async () => {
    if (!txtFilePath) {
      alert('Vui lòng chọn file TXT trước!');
      return;
    }

    setIsLoadingFolders(true);
    setDiscoveredFolders([]);

    try {
      console.log('📄 Loading folders from TXT:', txtFilePath);
      
      // Call IPC to read and validate folders
      const result = await window.electronAPI.validateBatchFolders(txtFilePath);
      
      if (!result.success) {
        alert(`❌ Lỗi: ${result.error}`);
        return;
      }

      console.log('✅ Discovered folders:', result.folders);
      
      // Detect duplicate folder names
      const folderNameMap = new Map();
      const duplicates = [];
      
      result.folders.forEach(folder => {
        if (!folderNameMap.has(folder.name)) {
          folderNameMap.set(folder.name, []);
        }
        folderNameMap.get(folder.name).push(folder.path);
      });
      
      // Find duplicates
      folderNameMap.forEach((paths, name) => {
        if (paths.length > 1) {
          duplicates.push({ name, paths });
          console.warn(`⚠️ Duplicate folder name detected: "${name}" at ${paths.length} locations`);
        }
      });
      
      // Filter: Keep only first occurrence of each folder name
      const seenNames = new Set();
      const filteredFolders = result.folders.filter(folder => {
        if (seenNames.has(folder.name)) {
          console.log(`🚫 Skipping duplicate folder: ${folder.path} (name: "${folder.name}")`);
          return false;
        }
        seenNames.add(folder.name);
        return true;
      });
      
      setDiscoveredFolders(filteredFolders);
      setDuplicateFolders(duplicates);
      
      const validCount = filteredFolders.filter(f => f.valid).length;
      
      let alertMsg = `✅ Tìm thấy ${result.folders.length} thư mục\n\n- Hợp lệ: ${validCount}\n- Không hợp lệ: ${filteredFolders.length - validCount}`;
      
      if (duplicates.length > 0) {
        alertMsg += `\n\n⚠️ CẢNH BÁO: Phát hiện ${duplicates.length} thư mục trùng tên!`;
        alertMsg += `\n(Chỉ thư mục đầu tiên sẽ được quét)`;
      }
      
      alertMsg += `\n\nVui lòng xem danh sách và bấm "Quét tất cả" để bắt đầu.`;
      
      alert(alertMsg);
    } catch (err) {
      console.error('Load folders error:', err);
      alert(`❌ Lỗi đọc file TXT: ${err.message}`);
    } finally {
      setIsLoadingFolders(false);
    }
  };

  // Step 2: Start scanning selected folders
  const handleStartScan = async () => {
    const selectedFolders = discoveredFolders.filter(f => f.selected && f.valid);
    
    if (selectedFolders.length === 0) {
      alert('Vui lòng chọn ít nhất 1 thư mục hợp lệ để quét!');
      return;
    }

    setIsScanning(true);
    stopRef.current = false;
    
    // Check if this is a resume (có folderTabs với status done)
    const isResume = folderTabs.length > 0 && folderTabs.some(t => t.status === 'done');
    
    if (!isResume) {
      // Fresh scan - reset everything
      setProgress({ 
        currentFolder: '',
        currentFile: '',
        processedFiles: 0,
        totalFiles: 0,
        processedFolders: 0,
        totalFolders: selectedFolders.length
      });
      setScanResults(null);
      setFileResults([]);
      setErrors([]);
      setSkippedFolders([]);
      setFolderTabs([]);
      setActiveFolder(null);
      
      // Initialize timer
      const batchStartTime = Date.now();
      setTimers({
        batchStartTime: batchStartTime,
        batchEndTime: null,
        batchElapsedSeconds: 0,
        fileTimings: [],
        folderTimings: []
      });
      setElapsedTime(0);
      
      console.log('⏱️ Batch timer started:', new Date(batchStartTime).toLocaleTimeString());
    } else {
      // Resume scan - keep existing data
      console.log('🔄 Resuming batch scan - keeping existing results');
      
      const doneFolders = folderTabs.filter(t => t.status === 'done');
      console.log(`📂 Resuming with ${doneFolders.length} folders already done`);
      
      // Update progress for resume
      setProgress(prev => ({
        ...prev,
        processedFolders: doneFolders.length,
        totalFolders: selectedFolders.length
      }));
    }

    try {
      console.log('🚀 Starting batch scan...');
      console.log('📁 Selected folders:', selectedFolders.length);
      console.log('🔧 OCR Engine:', ocrEngine);

      // Scan each folder one by one (allows stopping)
      const allResults = [];
      const allErrors = [];
      const processedFolderPaths = [];

      for (let i = 0; i < selectedFolders.length; i++) {
        if (stopRef.current) {
          console.log('⏸️ Scan stopped by user');
          break;
        }

        const folder = selectedFolders[i];
        
        // 🔄 SKIP if folder already done (resume scenario)
        const existingFolder = folderTabs.find(t => t.path === folder.path);
        if (existingFolder && existingFolder.status === 'done') {
          console.log(`⏭️ Skipping folder (already done): ${folder.name}`);
          continue;
        }
        
        const folderStartTime = Date.now();
        console.log(`\n📂 [${i + 1}/${selectedFolders.length}] Scanning: ${folder.path}`);
        console.log(`⏱️ Folder timer started: ${new Date(folderStartTime).toLocaleTimeString()}`);
        
        setProgress(prev => ({
          ...prev,
          processedFolders: i,
          totalFolders: selectedFolders.length,
          currentFolder: folder.path,
          processedFiles: 0,
          totalFiles: folder.imageCount
        }));

        // Update folder tab status to 'scanning'
        setFolderTabs(prev => {
          const existing = prev.find(t => t.path === folder.path);
          if (existing) {
            return prev.map(t => t.path === folder.path ? { ...t, status: 'scanning' } : t);
          } else {
            return [...prev, {
              path: folder.path,
              name: folder.name,
              count: folder.imageCount,
              status: 'scanning',
              files: []
            }];
          }
        });

        // Set active folder to show files as they're scanned
        setActiveFolder(folder.path);
        
        // Use local variable for lastKnownType in loop (not state!)
        let currentLastKnown = null;

        try {
          // Get image files in folder
          const imageFilesResult = await window.electronAPI.listFilesInFolder(folder.path);
          
          if (!imageFilesResult.success) {
            throw new Error(imageFilesResult.error || 'Failed to list files');
          }
          
          const validImages = imageFilesResult.files.filter(f => /\.(jpg|jpeg|png)$/i.test(f));
          
          console.log(`Found ${validImages.length} images in ${folder.name}`);
          
          // Initialize folderResults array
          const folderResults = [];
          
          // 🚀 CHECK IF BATCH PROCESSING SHOULD BE USED
          const isGeminiEngine = ['gemini-flash', 'gemini-flash-lite', 'gemini-flash-hybrid', 'gemini-flash-text'].includes(ocrEngine);
          const shouldUseBatch = (
            isGeminiEngine && // Gemini engine (including Tesseract+Text)
            (batchMode === 'fixed' || batchMode === 'smart') &&
            validImages.length >= 3
          );
          
          if (shouldUseBatch) {
            console.log(`\n🚀 BATCH MODE for folder: ${folder.name}`);
            console.log(`   Files: ${validImages.length}, Mode: ${batchMode}`);
            
            // Use batch processing for this folder
            const batchResults = await processFolderBatch(validImages, batchMode, ocrEngine);
            
            if (batchResults && batchResults.length > 0) {
              console.log(`✅ Folder batch success: ${batchResults.length} files`);
              
              // Add all batch results
              batchResults.forEach(result => {
                allResults.push(result);
                setFileResults(prev => [...prev, result]);
              });
              
              folderResults.push(...batchResults);
              
              // Update progress
              setProgress(prev => ({
                ...prev,
                processedFiles: prev.processedFiles + batchResults.length,
                currentFile: ''
              }));
              
              // Update folder timing
              const folderEndTime = Date.now();
              const folderDurationMs = folderEndTime - folderStartTime;
              console.log(`✅ Folder "${folder.name}" completed in ${(folderDurationMs / 1000).toFixed(2)}s (BATCH MODE)`);
              
              setTimers(prev => ({
                ...prev,
                folderTimings: [...prev.folderTimings, {
                  folderName: folder.name,
                  startTime: folderStartTime,
                  endTime: folderEndTime,
                  durationMs: folderDurationMs,
                  fileCount: batchResults.length,
                  mode: `batch_${batchMode}`
                }]
              }));
              
              // Post-process GCN documents for this folder
              console.log(`🔄 Post-processing GCN for folder: ${folder.name}`);
              const processedFolderResults = postProcessGCNBatch(folderResults);
              
              // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
              const sortedResults = sortGCNToTop ? sortResultsWithGCNOnTop(processedFolderResults) : processedFolderResults;
              if (sortGCNToTop) {
                console.log(`📊 Sorted results: ${sortedResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
              }
              
              // Update folder tab status to 'done' with results
              setFolderTabs(prev => prev.map(t => 
                t.path === folder.path 
                  ? { ...t, status: 'done', files: sortedResults }
                  : t
              ));
              
              // Update fileResults with post-processed
              setFileResults(prev => {
                const otherFolders = prev.filter(f => f.folder !== folder.path);
                return [...otherFolders, ...processedFolderResults];
              });
              
              processedFolderPaths.push(folder.path);
              
              // Continue to next folder (skip sequential loop)
              continue;
            } else {
              const errorMsg = batchResults?.error || 'Batch returned no results';
              console.error(`⚠️ BATCH FAILED for folder ${folder.name}:`, errorMsg);
              console.warn('🔄 FALLBACK: Switching to sequential processing for this folder...');
              console.log(`📋 Files in this folder will be scanned one by one (slower but reliable)`);
              
              // For batch scan, don't prompt user (too many prompts across folders)
              // Just fallback silently with clear logs
              // Fall through to sequential
            }
          }
          
          // SEQUENTIAL PROCESSING (Original logic)
          // Scan each file and display immediately
          for (let j = 0; j < validImages.length; j++) {
            // Check stopRef at start of each iteration
            if (stopRef.current) {
              console.log('⏹️ Stopping at file:', j + 1);
              break;
            }

            const imagePath = validImages[j];
            const fileName = imagePath.split(/[/\\]/).pop();
            const fileStartTime = Date.now();
            
            setProgress(prev => ({
              ...prev,
              processedFiles: j + 1,
              currentFile: fileName
            }));

            try {
              console.log(`  [${j + 1}/${validImages.length}] Processing: ${fileName}`);
              console.log(`  ⏱️ File timer started: ${new Date(fileStartTime).toLocaleTimeString()}`);
              
              // Scan single file
              let fileResult = await window.electronAPI.processDocumentOffline(imagePath);
              const fileEndTime = Date.now();
              const fileDurationMs = fileEndTime - fileStartTime;
              
              console.log(`  ✅ File completed in ${(fileDurationMs / 1000).toFixed(2)}s`);
              
              // Debug: Log GCN fields if present
              if (fileResult.short_code === 'GCN' || fileResult.short_code === 'GCNM' || fileResult.short_code === 'GCNC') {
                console.log(`  🔍 GCN detected:`, {
                  file: fileName,
                  short_code: fileResult.short_code,
                  color: fileResult.color || 'null',
                  issue_date: fileResult.issue_date || 'null',
                  issue_date_confidence: fileResult.issue_date_confidence || 'null'
                });
              }
              
              // Apply sequential naming if UNKNOWN (use local variable, not state!)
              fileResult = applySequentialNaming(fileResult, currentLastKnown);
              
              if (fileResult.success) {
                // Update LOCAL currentLastKnown if not UNKNOWN (synchronous update!)
                if (fileResult.short_code !== 'UNKNOWN') {
                  currentLastKnown = {
                    short_code: fileResult.short_code,
                    doc_type: fileResult.doc_type,
                    confidence: fileResult.confidence
                  };
                  // Also update state for UI display (optional)
                  setLastKnownType(currentLastKnown);
                }
                // Load preview
                let previewUrl = null;
                try {
                  previewUrl = await window.electronAPI.readImageDataUrl(imagePath);
                } catch (err) {
                  console.warn('Failed to load preview:', err);
                }

                const fileWithPreview = {
                  filePath: imagePath,
                  fileName: fileName,
                  short_code: fileResult.short_code || 'UNKNOWN',
                  doc_type: fileResult.doc_type || 'Unknown',
                  confidence: fileResult.confidence || 0,
                  folder: folder.path,
                  previewUrl: previewUrl,
                  success: true,
                  method: fileResult.method || 'offline_ocr',
                  // GCN fields for post-processing
                  color: fileResult.color || null,
                  issue_date: fileResult.issue_date || null,
                  issue_date_confidence: fileResult.issue_date_confidence || null,
                  // Timing data
                  startTime: fileStartTime,
                  endTime: fileEndTime,
                  durationMs: fileDurationMs,
                  durationSeconds: (fileDurationMs / 1000).toFixed(2)
                };

                folderResults.push(fileWithPreview);
                
                // Save file timing
                setTimers(prev => ({
                  ...prev,
                  fileTimings: [...prev.fileTimings, {
                    fileName: fileName,
                    folderName: folder.name,
                    startTime: fileStartTime,
                    endTime: fileEndTime,
                    durationMs: fileDurationMs,
                    engineType: ocrEngine,
                    method: fileResult.method || 'offline_ocr'
                  }]
                }));
                allResults.push({
                  original_path: imagePath,
                  short_code: fileResult.short_code || 'UNKNOWN',
                  doc_type: fileResult.doc_type || 'Unknown',
                  confidence: fileResult.confidence || 0,
                  folder: folder.path
                });

                // Add to fileResults and folder tab immediately (realtime display)
                setFileResults(prev => [...prev, fileWithPreview]);
                
                // IMPORTANT: Skip update if user is editing a file in this folder
                // This prevents input from jumping/resetting while user is typing
                const isEditingThisFolder = isEditingFileId && isEditingFileId.startsWith(folder.path);
                if (!isEditingThisFolder) {
                  setFolderTabs(prev => prev.map(t => 
                    t.path === folder.path ? { ...t, files: [...t.files, fileWithPreview] } : t
                  ));
                } else {
                  console.log(`⏸️ Skipping folder tab update (user is editing)`);
                }

                console.log(`  ✅ ${fileResult.short_code} - ${Math.round(fileResult.confidence * 100)}%`);
              } else {
                allErrors.push({
                  file: imagePath,
                  error: fileResult.error || 'Unknown error'
                });
              }
            } catch (err) {
              console.error(`  ❌ Error processing ${fileName}:`, err);
              allErrors.push({
                file: imagePath,
                error: err.message
              });
            }
          }

          if (!stopRef.current && folderResults.length > 0) {
            // Post-process GCN documents (date-based classification)
            const processedFolderResults = postProcessGCNBatch(folderResults);
            
            // Sort results: GCN (GCNC, GCNM) on top for easy review (if enabled)
            const sortedResults = sortGCNToTop ? sortResultsWithGCNOnTop(processedFolderResults) : processedFolderResults;
            if (sortGCNToTop) {
              console.log(`📊 Sorted results: ${sortedResults.filter(r => r.short_code === 'GCNC' || r.short_code === 'GCNM').length} GCN documents moved to top`);
            }
            
            // Update allResults with post-processed results
            const startIndex = allResults.length - folderResults.length;
            for (let i = 0; i < sortedResults.length; i++) {
              allResults[startIndex + i] = {
                original_path: sortedResults[i].filePath,
                short_code: sortedResults[i].short_code,
                doc_type: sortedResults[i].doc_type,
                confidence: sortedResults[i].confidence,
                folder: sortedResults[i].folder
              };
            }
            
            // Update folder tabs with sorted results
            setFolderTabs(prev => prev.map(t => {
              if (t.path === folder.path) {
                return { 
                  ...t, 
                  status: 'done', 
                  count: sortedResults.length,
                  files: sortedResults 
                };
              }
              return t;
            }));
            
            // Update fileResults with post-processed results
            setFileResults(prev => {
              const otherFolders = prev.filter(f => f.folder !== folder.path);
              return [...otherFolders, ...processedFolderResults];
            });
            
            processedFolderPaths.push(folder.path);
          }
          
          // Save folder timing
          const folderEndTime = Date.now();
          const folderDurationMs = folderEndTime - folderStartTime;
          console.log(`\n✅ Folder "${folder.name}" completed in ${(folderDurationMs / 1000).toFixed(2)}s (${folderResults.length} files)`);
          
          setTimers(prev => ({
            ...prev,
            folderTimings: [...prev.folderTimings, {
              folderName: folder.name,
              folderPath: folder.path,
              startTime: folderStartTime,
              endTime: folderEndTime,
              durationMs: folderDurationMs,
              fileCount: folderResults.length,
              avgTimePerFile: folderResults.length > 0 ? (folderDurationMs / folderResults.length).toFixed(0) : 0
            }]
          }));
        } catch (err) {
          console.error(`Error scanning ${folder.path}:`, err);
          allErrors.push({
            folder: folder.path,
            error: err.message
          });
          
          // Still save folder timing even if error
          const folderEndTime = Date.now();
          const folderDurationMs = folderEndTime - folderStartTime;
          setTimers(prev => ({
            ...prev,
            folderTimings: [...prev.folderTimings, {
              folderName: folder.name,
              folderPath: folder.path,
              startTime: folderStartTime,
              endTime: folderEndTime,
              durationMs: folderDurationMs,
              fileCount: 0,
              error: true
            }]
          }));
        }
      }

      // Aggregate results
      const result = {
        success: true,
        total_folders: selectedFolders.length,
        valid_folders: processedFolderPaths.length,
        skipped_folders_count: allErrors.length,
        total_files: allResults.length,
        processed_files: allResults.length,
        error_count: allErrors.length,
        skipped_folders: allErrors,
        errors: allErrors,
        results: allResults
      };

      // End batch timer
      const batchEndTime = Date.now();
      const batchElapsedMs = timers.batchStartTime ? (batchEndTime - timers.batchStartTime) : 0;
      const batchElapsedSeconds = Math.floor(batchElapsedMs / 1000);
      
      console.log('✅ Batch scan complete:', result);
      if (timers.batchStartTime) {
        console.log(`⏱️ Total batch time: ${batchElapsedSeconds}s (${(batchElapsedMs / 1000 / 60).toFixed(2)} minutes)`);
      }
      
      setTimers(prev => ({
        ...prev,
        batchEndTime: batchEndTime,
        batchElapsedSeconds: batchElapsedSeconds
      }));

      if (result.success) {
        setScanResults(result);
        setSkippedFolders(result.skipped_folders || []);
        setErrors(result.errors || []);
        
        // Group results by folder
        const folderMap = {};
        for (const item of (result.results || [])) {
          if (!folderMap[item.folder]) {
            folderMap[item.folder] = [];
          }
          folderMap[item.folder].push(item);
        }

        // Create folder tabs
        const tabs = [];
        for (const [folderPath, items] of Object.entries(folderMap)) {
          const folderName = folderPath.split(/[/\\]/).pop() || folderPath;
          
          // Load preview for all files in this folder
          const filesWithPreview = await Promise.all(
            items.map(async (item) => {
              try {
                const previewUrl = await window.electronAPI.readImageDataUrl(item.original_path);
                return {
                  filePath: item.original_path,
                  fileName: item.original_path.split(/[/\\]/).pop(),
                  short_code: item.short_code,
                  doc_type: item.doc_type,
                  confidence: item.confidence,
                  folder: item.folder,
                  previewUrl: previewUrl,
                  success: true,
                  method: 'offline_ocr'
                };
              } catch (err) {
                return {
                  filePath: item.original_path,
                  fileName: item.original_path.split(/[/\\]/).pop(),
                  short_code: item.short_code,
                  doc_type: item.doc_type,
                  confidence: item.confidence,
                  folder: item.folder,
                  previewUrl: null,
                  success: true,
                  method: 'offline_ocr'
                };
              }
            })
          );

          tabs.push({
            path: folderPath,
            name: folderName,
            count: items.length,
            status: 'done',
            files: filesWithPreview
          });
        }

        setFolderTabs(tabs);
        
        // Set first folder as active
        if (tabs.length > 0) {
          setActiveFolder(tabs[0].path);
          setFileResults(tabs[0].files);
        }
        
        let completeMsg = `✅ Quét hoàn tất!\n\n📊 Thống kê:\n- Thư mục hợp lệ: ${result.valid_folders}/${result.total_folders}\n- Files xử lý: ${result.processed_files}/${result.total_files}\n- Lỗi: ${result.error_count}`;
        
        // Add duplicate folder warning
        if (duplicateFolders.length > 0) {
          completeMsg += `\n\n⚠️ CẢNH BÁO THƯ MỤC TRÙNG TÊN:`;
          completeMsg += `\n${duplicateFolders.length} thư mục trùng tên đã BỊ BỎ QUA:`;
          duplicateFolders.forEach(dup => {
            completeMsg += `\n\n📁 "${dup.name}":`;
            completeMsg += `\n  ✅ Đã quét: ${dup.paths[0]}`;
            for (let i = 1; i < dup.paths.length; i++) {
              completeMsg += `\n  ❌ Bỏ qua: ${dup.paths[i]}`;
            }
          });
        }
        
        completeMsg += `\n\n💡 Bạn có thể xem kết quả chi tiết và gộp PDF bên dưới.`;
        
        alert(completeMsg);
      } else {
        alert(`❌ Lỗi: ${result.error}`);
      }
    } catch (err) {
      console.error('Batch scan error:', err);
      alert(`❌ Lỗi xử lý: ${err.message}`);
    } finally {
      // 🎉 MARK SCAN COMPLETE (nếu không bị stop giữa chừng)
      if (!stopRef.current && currentScanId && window.electronAPI?.markScanComplete) {
        await window.electronAPI.markScanComplete(currentScanId);
        setCurrentScanId(null);
        console.log(`✅ Marked batch scan complete`);
      }
      
      setIsScanning(false);
      stopRef.current = false;
    }
  };

  // Stop scanning
  const handleStopScan = () => {
    stopRef.current = true;
    alert('⏸️ Đang dừng quét... Vui lòng đợi file hiện tại hoàn tất.');
  };

  // Toggle folder selection
  const toggleFolderSelection = (folderPath) => {
    setDiscoveredFolders(prev => prev.map(f => 
      f.path === folderPath ? { ...f, selected: !f.selected } : f
    ));
  };

  // Select/Deselect all
  const selectAllFolders = (select = true) => {
    setDiscoveredFolders(prev => prev.map(f => 
      f.valid ? { ...f, selected: select } : f
    ));
  };

  // Get filename from path
  const getFileName = (filePath) => {
    if (!filePath) return '';
    const parts = filePath.split(/[/\\]/);
    return parts[parts.length - 1];
  };

  // Format confidence percentage
  const formatConfidence = (conf) => {
    if (typeof conf !== 'number') return 0;
    return Math.round(conf * 100);
  };

  // Load previews for a specific folder
  const handleLoadPreviewsForFolder = async (folderPath) => {
    if (!folderPath || !window.electronAPI) return;
    
    // Check if already loaded
    if (foldersPreviewsLoaded.has(folderPath)) {
      console.log(`✅ Previews already loaded for: ${folderPath}`);
      return;
    }
    
    const folderTab = folderTabs.find(t => t.path === folderPath);
    if (!folderTab || !folderTab.files || folderTab.files.length === 0) return;
    
    console.log(`🖼️ Loading previews for folder: ${folderTab.name}...`);
    setLoadingPreviewFor(folderPath);
    
    try {
      let loadedCount = 0;
      const filesWithPreviews = await Promise.all(
        folderTab.files.map(async (file) => {
          if (!file.filePath || file.previewUrl) return file; // Skip if no path or already has preview
          
          try {
            const previewUrl = await window.electronAPI.getBase64Image(file.filePath);
            if (previewUrl) loadedCount++;
            return { ...file, previewUrl };
          } catch (err) {
            console.warn(`⚠️ Failed to load preview: ${file.fileName}`);
            return file;
          }
        })
      );
      
      // Update folder with loaded previews
      setFolderTabs(prev => prev.map(tab =>
        tab.path === folderPath ? { ...tab, files: filesWithPreviews } : tab
      ));
      
      // Mark as loaded
      setFoldersPreviewsLoaded(prev => new Set([...prev, folderPath]));
      
      console.log(`✅ Loaded ${loadedCount} previews for: ${folderTab.name}`);
    } catch (error) {
      console.error(`❌ Error loading previews:`, error);
      alert(`Lỗi khi load preview: ${error.message}`);
    } finally {
      setLoadingPreviewFor(null);
    }
  };

  // Handle resume scan from saved state
  const handleResumeScan = async (scan, previewMode = 'gcn-only') => {
    try {
      console.log(`🔄 Resuming batch scan: ${scan.scanId} (preview mode: ${previewMode})`);
      
      // Auto-switch to batch tab if needed
      if (onSwitchTab) {
        onSwitchTab('batch');
      }
      
      const loadResult = await window.electronAPI.loadScanState(scan.scanId);
      if (!loadResult.success) {
        alert('❌ Không thể load scan data');
        return;
      }
      
      const scanData = loadResult.data;
      
      // DO NOT load preview URLs on resume - set to null for lazy loading
      // This prevents memory overflow and speeds up resume
      const foldersWithoutPreviews = (scanData.folderTabs || []).map(folder => ({
        ...folder,
        files: (folder.files || []).map(file => ({
          ...file,
          previewUrl: null // Will be lazy-loaded if needed
        }))
      }));
      
      const fileResultsWithoutPreviews = (scanData.fileResults || []).map(file => ({
        ...file,
        previewUrl: null // Will be lazy-loaded if needed
      }));
      
      console.log(`🔄 Resume: Previews will NOT be loaded (lazy load on-demand)`);
      
      // Restore batch scan state
      setFolderTabs(foldersWithoutPreviews);
      setDiscoveredFolders(scanData.discoveredFolders || []);
      setFileResults(fileResultsWithoutPreviews);
      setTxtFilePath(scanData.txtFilePath || null);
      setCurrentScanId(scan.scanId);
      
      // CLOSE DIALOG IMMEDIATELY - don't block user
      setShowResumeDialog(false);
      
      // Set active to first completed folder to show results
      const firstDone = scanData.folderTabs?.find(t => t.status === 'done');
      if (firstDone) {
        setActiveFolder(firstDone.path);
      }
      
      // Count completed
      const completedFolders = scanData.folderTabs?.filter(t => t.status === 'done') || [];
      const totalFolders = scanData.folderTabs?.length || 0;
      const totalFiles = scanData.fileResults?.length || 0;
      
      console.log(`✅ Restored ${completedFolders.length}/${totalFolders} folders`);
      console.log(`✅ Restored ${totalFiles} files`);
      
      // Auto-trigger continue scan
      const pendingFolders = foldersWithoutPreviews.filter(f => f.status === 'pending');
      if (pendingFolders.length > 0) {
        console.log(`🚀 Auto-resuming: ${pendingFolders.length} pending folders`);
        // Trigger continue scan after a short delay to ensure UI is ready
        setTimeout(() => {
          setIsScanning(true);
          handleProcessBatchFiles(true); // Resume = true
        }, 500);
      } else {
        alert(`✅ Đã khôi phục tất cả ${totalFolders} folders (đã scan xong).\n\nPreview images sẽ được load on-demand khi cần.`);
      }
      
    } catch (error) {
      console.error('Resume scan error:', error);
      alert(`❌ Lỗi: ${error.message}`);
    }
  };

  // Handle dismiss resume dialog
  const handleDismissResume = async (scanId) => {
    try {
      if (scanId === 'all') {
        for (const scan of incompleteScans) {
          await window.electronAPI.deleteScanState(scan.scanId);
        }
        console.log(`🗑️ Deleted all ${incompleteScans.length} incomplete scans`);
      } else {
        await window.electronAPI.deleteScanState(scanId);
        console.log(`🗑️ Deleted scan: ${scanId}`);
      }
      
      setShowResumeDialog(false);
      setIncompleteScans([]);
    } catch (error) {
      console.error('Delete scan error:', error);
    }
  };

  // Apply sequential naming logic (UNKNOWN fallback)
  const applySequentialNaming = (result, lastType) => {
    console.log('🔍 applySequentialNaming:', { 
      short_code: result.short_code, 
      lastType: lastType ? lastType.short_code : 'null' 
    });
    
    if (result.success && lastType) {
      // Rule: UNKNOWN → always use lastKnown
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
    }
    return result;
  };

  // Parse issue date from GCN for comparison
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

  // Batch processing helper for folder
  const processFolderBatch = async (imagePaths, mode, engineType) => {
    console.log(`\n${'='*80}`);
    console.log(`🚀 FOLDER BATCH PROCESSING: ${imagePaths.length} files`);
    console.log(`   Mode: ${mode}`);
    console.log(`   Engine: ${engineType}`);
    console.log(`${'='*80}\n`);
    
    if (!window.electronAPI) {
      console.error('❌ Electron API not available');
      return null;
    }
    
    // Filter ONLY image files (skip PDFs)
    const imageOnly = imagePaths.filter(path => 
      /\.(jpg|jpeg|png|gif|bmp)$/i.test(path)
    );
    
    if (imageOnly.length === 0) {
      console.error('❌ No image files found (all PDFs)');
      return null;
    }
    
    if (imageOnly.length < imagePaths.length) {
      console.log(`⏭️ Skipped ${imagePaths.length - imageOnly.length} PDF files, processing ${imageOnly.length} images`);
    }
    
    try {
      // Call batch processor via IPC
      const batchResult = await window.electronAPI.batchProcessDocuments({
        mode: mode,
        imagePaths: imageOnly,  // Use filtered images only
        ocrEngine: engineType
      });
      
      if (!batchResult.success) {
        console.error('❌ Folder batch failed:', batchResult.error);
        return null;
      }
      
      console.log(`✅ Folder batch complete: ${batchResult.results.length} results`);
      
      // DEBUG: Log first result structure
      if (batchResult.results.length > 0) {
        console.log(`🔍 DEBUG - First batch result:`, batchResult.results[0]);
      }
      
      // Map batch results to BatchScanner format
      const mappedResults = [];
      for (const batchItem of batchResult.results) {
        const fileName = batchItem.file_name;
        const filePath = batchItem.file_path;
        
        // DEBUG: Log item structure
        console.log(`🔍 Mapping item: fileName=${fileName}, filePath=${filePath ? 'OK' : 'UNDEFINED'}`);
        
        // Validate filePath
        if (!filePath) {
          console.error(`⚠️ Missing file_path for item:`, batchItem);
          continue;
        }
        
        // Get folder path from file path
        const folderPath = filePath.substring(0, filePath.lastIndexOf(/[/\\]/.test(filePath) ? (filePath.includes('/') ? '/' : '\\') : '/'));
        
        // Generate preview (with validation)
        let previewUrl = null;
        try {
          if (filePath && typeof filePath === 'string') {
            previewUrl = await window.electronAPI.readImageDataUrl(filePath);
          }
        } catch (e) {
          console.error(`Preview error for ${fileName}:`, e);
        }
        
        mappedResults.push({
          filePath: filePath,
          fileName: fileName,
          short_code: batchItem.short_code || 'UNKNOWN',
          doc_type: batchItem.short_code || 'UNKNOWN',
          confidence: batchItem.confidence || 0.5,
          folder: folderPath,
          previewUrl: previewUrl,
          success: true,
          method: `batch_${mode}`,
          metadata: batchItem.metadata || {},
          // GCN fields
          color: batchItem.metadata?.color || null,
          issue_date: batchItem.metadata?.issue_date || null,
          issue_date_confidence: batchItem.metadata?.issue_date_confidence || null,
          // Additional fields for BatchScanner compatibility
          original_path: filePath,  // Add this for folderMap compatibility
          // Timing
          startTime: null,
          endTime: null,
          durationMs: null
        });
      }
      
      return mappedResults;
      
    } catch (error) {
      console.error('❌ Folder batch error:', error);
      return null;
    }
  };

  // Post-process GCN batch (DATE-BASED classification)
  const postProcessGCNBatch = (folderResults) => {
    try {
      console.log('🔄 Post-processing GCN batch (DATE-BASED classification)...');
      
      // Step 1: Normalize GCNM/GCNC → GCN
      const normalizedResults = folderResults.map(r => {
        if (r.short_code === 'GCNM' || r.short_code === 'GCNC') {
          console.log(`🔄 Converting ${r.short_code} → GCN for file: ${r.fileName}`);
          return { ...r, short_code: 'GCN', original_short_code: r.short_code };
        }
        return r;
      });
      
      // Step 2: Find all GCN documents
      const allGcnDocs = normalizedResults.filter(r => r.short_code === 'GCN');
      
      if (allGcnDocs.length === 0) {
        console.log('✅ No GCN documents found');
        return normalizedResults;
      }
      
      console.log(`📋 Found ${allGcnDocs.length} GCN document(s) to process`);
      
      // Check if results came from batch processing
      const isBatchMode = allGcnDocs.length > 0 && allGcnDocs[0].method && allGcnDocs[0].method.includes('batch');
      
      if (isBatchMode) {
        console.log(`📦 Batch mode - Using AI grouping (same as DesktopScanner)`);
        
        // Group by metadata (color + issue_date)
        const gcnGroups = new Map();
        
        allGcnDocs.forEach(doc => {
          const meta = doc.metadata || {};
          const color = meta.color || doc.color || 'unknown';
          const issueDate = meta.issue_date || doc.issue_date || null;
          const issueDateConf = meta.issue_date_confidence || doc.issue_date_confidence || null;
          
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
        
        console.log(`📋 Found ${gcnGroups.size} unique GCN document(s)`);
        
        const groupsArray = Array.from(gcnGroups.values());
        
        // Classify by color or date
        const colors = groupsArray.map(g => g.color).filter(c => c && c !== 'unknown');
        const uniqueColors = [...new Set(colors)];
        const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
        
        if (hasRedAndPink) {
          console.log(`  🎨 Mixed colors → Classify by color`);
          groupsArray.forEach(group => {
            const classification = (group.color === 'red' || group.color === 'orange') ? 'GCNC' : 'GCNM';
            group.files.forEach(file => {
              const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (idx >= 0) {
                normalizedResults[idx].short_code = classification;
                normalizedResults[idx].doc_type = classification;
              }
            });
          });
        } else {
          console.log(`  📅 Same color → Classify by date`);
          const groupsWithDate = groupsArray.filter(g => g.parsedDate && g.parsedDate.comparable > 0);
          
          if (groupsWithDate.length >= 2) {
            groupsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
            console.log(`📊 Sorted: Oldest = GCNC, others = GCNM`);
            
            groupsWithDate.forEach((group, idx) => {
              const classification = (idx === 0) ? 'GCNC' : 'GCNM';
              group.files.forEach(file => {
                const resIdx = normalizedResults.findIndex(r => r.fileName === file.fileName);
                if (resIdx >= 0) {
                  normalizedResults[resIdx].short_code = classification;
                  normalizedResults[resIdx].doc_type = classification;
                }
              });
            });
          } else {
            // Fallback: Not enough dates → Use file order
            console.log(`  ⚠️ Not enough dates → Fallback to file order`);
            
            if (groupsArray.length === 1) {
              console.log(`  📄 Only 1 GCN group → GCNC (default oldest)`);
              groupsArray[0].files.forEach(file => {
                const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
                if (idx >= 0) {
                  normalizedResults[idx].short_code = 'GCNC';
                  normalizedResults[idx].doc_type = 'GCNC';
                }
              });
            } else {
              console.log(`  📊 Multiple groups → First GCNC, rest GCNM (by file order)`);
              groupsArray.forEach((group, groupIdx) => {
                const classification = (groupIdx === 0) ? 'GCNC' : 'GCNM';
                group.files.forEach(file => {
                  const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
                  if (idx >= 0) {
                    normalizedResults[idx].short_code = classification;
                    normalizedResults[idx].doc_type = classification;
                  }
                });
              });
            }
          }
        }
        
        console.log('✅ GCN post-processing complete (batch mode)');
        return normalizedResults;
        
      } else {
        console.log(`📄 Single-file mode - Using pairing logic`);
        
        // OLD PAIRING LOGIC (keep for single-file mode)
      
      // Step 3: Group by color first, then pair within same color
      console.log(`  🎨 Grouping GCN documents by color...`);
      
      const colorGroups = {
        red: [],
        pink: [],
        unknown: []
      };
      
      allGcnDocs.forEach(doc => {
        if (doc.color === 'red' || doc.color === 'orange') {
          colorGroups.red.push(doc);
        } else if (doc.color === 'pink') {
          colorGroups.pink.push(doc);
        } else {
          colorGroups.unknown.push(doc);
        }
      });
      
      console.log(`  📊 Color groups: Red=${colorGroups.red.length}, Pink=${colorGroups.pink.length}, Unknown=${colorGroups.unknown.length}`);
      
      // Step 4: Pair within each color group
      const pairs = [];
      let pairIndex = 0;
      
      ['red', 'pink', 'unknown'].forEach(colorKey => {
        const group = colorGroups[colorKey];
        for (let i = 0; i < group.length; i += 2) {
          const page1 = group[i];
          const page2 = group[i + 1];
          
          if (page1 && page2) {
            pairs.push({ 
              page1, 
              page2, 
              pairIndex: pairIndex++,
              colorGroup: colorKey 
            });
            console.log(`    ➡️ Pair ${pairIndex}: [${page1.fileName}] + [${page2.fileName}] (${colorKey})`);
          } else if (page1) {
            pairs.push({ 
              page1, 
              page2: null, 
              pairIndex: pairIndex++,
              colorGroup: colorKey 
            });
            console.log(`    ➡️ Pair ${pairIndex}: [${page1.fileName}] (single, ${colorKey})`);
          }
        }
      });
      
      // Step 5: Extract color and dates from each pair
      const pairsWithData = pairs.map(pair => {
        // Color already determined by grouping
        const color = pair.colorGroup === 'red' ? 'red' : (pair.colorGroup === 'pink' ? 'pink' : 'unknown');
        
        // Extract date from either page (prefer page2, then page1)
        const issueDate = pair.page2?.issue_date || pair.page1?.issue_date || null;
        const issueDateConfidence = pair.page2?.issue_date_confidence || pair.page1?.issue_date_confidence || null;
        
        const pairData = {
          ...pair,
          color,
          issueDate,
          issueDateConfidence,
          parsedDate: parseIssueDate(issueDate, issueDateConfidence)
        };
        
        console.log(`    📅 Pair ${pair.pairIndex + 1} (${color}): date=${issueDate || 'null'}, confidence=${issueDateConfidence || 'null'}`);
        
        return pairData;
      });
      
      // Step 5: Check if mixed colors (red vs pink)
      const colors = pairsWithData.map(p => p.color).filter(Boolean);
      const uniqueColors = [...new Set(colors)];
      const hasMixedColors = uniqueColors.length > 1;
      const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
      
      console.log(`  🎨 Unique colors: ${uniqueColors.join(', ') || 'none'}`);
      
      // Step 6: Classify - Prioritize date over color, then use color as fallback
      console.log(`  📊 Starting classification...`);
      
      // Group pairs by color
      const redPairs = pairsWithData.filter(p => p.color === 'red' || p.color === 'orange');
      const pinkPairs = pairsWithData.filter(p => p.color === 'pink');
      const unknownColorPairs = pairsWithData.filter(p => !p.color || p.color === 'unknown');
      
      console.log(`  🎨 Red pairs: ${redPairs.length}, Pink pairs: ${pinkPairs.length}, Unknown: ${unknownColorPairs.length}`);
      
      // If mixed colors (red vs pink), use color-based classification
      if (hasMixedColors && hasRedAndPink) {
        console.log(`  🎨 Mixed colors detected → Using color for base classification`);
        
        // Classify red pairs by date (oldest red = GCNC, newer red = GCNM)
        const redPairsWithDate = redPairs.filter(p => p.parsedDate);
        if (redPairsWithDate.length > 0) {
          redPairsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
          console.log(`  📅 Red pairs with dates: ${redPairsWithDate.length}`);
          
          redPairsWithDate.forEach((pair, idx) => {
            const classification = idx === 0 ? 'GCNC' : 'GCNM';
            const note = `Màu đỏ, ngày ${pair.issueDate} → ${classification} ${idx === 0 ? '(cũ nhất trong đỏ)' : ''}`;
            
            console.log(`    ✅ Red Pair ${idx + 1}: ${note}`);
            
            [pair.page1, pair.page2].filter(Boolean).forEach(page => {
              const index = normalizedResults.indexOf(page);
              normalizedResults[index] = {
                ...page,
                short_code: classification,
                reasoning: `${page.reasoning || 'GCN'} - ${note}`,
                gcn_classification_note: `📌 ${note}`
              };
            });
          });
        }
        
        // All red pairs without dates → GCNC (default old)
        const redPairsNoDate = redPairs.filter(p => !p.parsedDate);
        redPairsNoDate.forEach(pair => {
          const note = `Màu đỏ, không có ngày → GCNC (mặc định cũ)`;
          [pair.page1, pair.page2].filter(Boolean).forEach(page => {
            const index = normalizedResults.indexOf(page);
            normalizedResults[index] = {
              ...page,
              short_code: 'GCNC',
              reasoning: `${page.reasoning || 'GCN'} - ${note}`,
              gcn_classification_note: `📌 ${note}`
            };
          });
        });
        
        // Classify pink pairs by date (oldest pink = could be GCNC, but likely GCNM)
        const pinkPairsWithDate = pinkPairs.filter(p => p.parsedDate);
        if (pinkPairsWithDate.length > 0) {
          pinkPairsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
          console.log(`  📅 Pink pairs with dates: ${pinkPairsWithDate.length}`);
          
          pinkPairsWithDate.forEach((pair, idx) => {
            // All pink → GCNM (new format)
            const classification = 'GCNM';
            const note = `Màu hồng, ngày ${pair.issueDate} → ${classification}`;
            
            console.log(`    ✅ Pink Pair ${idx + 1}: ${note}`);
            
            [pair.page1, pair.page2].filter(Boolean).forEach(page => {
              const index = normalizedResults.indexOf(page);
              normalizedResults[index] = {
                ...page,
                short_code: classification,
                reasoning: `${page.reasoning || 'GCN'} - ${note}`,
                gcn_classification_note: `📌 ${note}`
              };
            });
          });
        }
        
        // All pink pairs without dates → GCNM (default new)
        const pinkPairsNoDate = pinkPairs.filter(p => !p.parsedDate);
        pinkPairsNoDate.forEach(pair => {
          const note = `Màu hồng, không có ngày → GCNM (mặc định mới)`;
          [pair.page1, pair.page2].filter(Boolean).forEach(page => {
            const index = normalizedResults.indexOf(page);
            normalizedResults[index] = {
              ...page,
              short_code: 'GCNM',
              reasoning: `${page.reasoning || 'GCN'} - ${note}`,
              gcn_classification_note: `📌 ${note}`
            };
          });
        });
        
        // Unknown color → default GCNM
        unknownColorPairs.forEach(pair => {
          const note = `Không xác định màu → GCNM (mặc định)`;
          [pair.page1, pair.page2].filter(Boolean).forEach(page => {
            const index = normalizedResults.indexOf(page);
            normalizedResults[index] = {
              ...page,
              short_code: 'GCNM',
              reasoning: `${page.reasoning || 'GCN'} - ${note}`,
              gcn_classification_note: `📌 ${note}`
            };
          });
        });
        
        console.log('✅ GCN classification by color+date complete');
        return normalizedResults;
      }
      
      // Step 7: Classify by date (oldest = GCNC, newer = GCNM)
      const pairsWithDates = pairsWithData.filter(p => p.parsedDate);
      
      if (pairsWithDates.length === 0) {
        console.log('  ⚠️ No dates found → Default all to GCNM');
        pairsWithData.forEach(pair => {
          [pair.page1, pair.page2].filter(Boolean).forEach(page => {
            const index = normalizedResults.indexOf(page);
            normalizedResults[index] = {
              ...page,
              short_code: 'GCNM',
              reasoning: `${page.reasoning || 'GCN'} - Không tìm thấy ngày → GCNM (mặc định)`,
              gcn_classification_note: '📌 Không có ngày cấp → GCNM (mặc định)'
            };
          });
        });
        return normalizedResults;
      }
      
      // Sort by date
      pairsWithDates.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
      
      console.log('  📊 Sorted by date:');
      pairsWithDates.forEach((pair, idx) => {
        console.log(`    ${idx + 1}. ${pair.issueDate} (${pair.issueDateConfidence})`);
      });
      
      // Oldest = GCNC, rest = GCNM
      pairsWithDates.forEach((pair, idx) => {
        const classification = idx === 0 ? 'GCNC' : 'GCNM';
        const note = `Ngày cấp ${pair.issueDate} → ${classification} ${idx === 0 ? '(cũ nhất)' : ''}`;
        
        console.log(`  ✅ ${note}`);
        
        [pair.page1, pair.page2].filter(Boolean).forEach(page => {
          const index = normalizedResults.indexOf(page);
          normalizedResults[index] = {
            ...page,
            short_code: classification,
            reasoning: `${page.reasoning || 'GCN'} - ${note}`,
            gcn_classification_note: `📌 ${note}`
          };
        });
      });
      
      // Handle pairs without dates (default GCNM)
      const pairsWithoutDates = pairsWithData.filter(p => !p.parsedDate);
      pairsWithoutDates.forEach(pair => {
        [pair.page1, pair.page2].filter(Boolean).forEach(page => {
          const index = normalizedResults.indexOf(page);
          if (normalizedResults[index].short_code === 'GCN') {
            normalizedResults[index] = {
              ...page,
              short_code: 'GCNM',
              reasoning: `${page.reasoning || 'GCN'} - Không tìm thấy ngày → GCNM`,
              gcn_classification_note: '📌 Không có ngày → GCNM (mặc định)'
            };
          }
        });
      });
      
      } // End of else (single-file mode)
      
      console.log('✅ GCN post-processing complete');
      return normalizedResults;
      
    } catch (err) {
      console.error('❌ GCN post-processing error:', err);
      return folderResults; // Return original if error
    }
  };

  // Get method badge - check OCR engine type
  const getMethodBadge = (method) => {
    // Check if using cloud OCR engines
    const isCloudEngine = ocrEngine.includes('gemini') || ocrEngine.includes('google') || ocrEngine.includes('azure');
    
    if (method === 'cloud_boost' || isCloudEngine) {
      return <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full">☁️ Cloud</span>;
    }
    return <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">💻 Offline</span>;
  };

  // Grid columns based on density
  const gridColsClass = density === 'high' ? 'grid-cols-5' : density === 'medium' ? 'grid-cols-4' : 'grid-cols-3';

  // Handle merge PDFs (show modal)
  const handleMerge = (mergeAll = false) => {
    if (mergeAll) {
      // Check if there are any files across all folders
      const totalFiles = folderTabs.reduce((sum, tab) => sum + tab.files.length, 0);
      if (totalFiles === 0) {
        alert('Không có file nào để gộp PDF!');
        return;
      }
    } else {
      // Check current folder
      if (fileResults.length === 0) {
        alert('Không có file nào trong thư mục hiện tại để gộp PDF!');
        return;
      }
    }
    setIsMergeAll(mergeAll);
    setShowMergeModal(true);
  };

  // Execute merge with selected options
  const executeMerge = async (mergeAll = false) => {
    console.log('🚀 executeMerge called:', { mergeAll, outputOption, mergeSuffix, outputFolder });
    
    setShowMergeModal(false);
    setMergeInProgress(true);

    try {
      // Determine which files to merge
      let allFilesToMerge = [];
      if (mergeAll) {
        // Merge all files from all folders
        folderTabs.forEach(tab => {
          allFilesToMerge = allFilesToMerge.concat(tab.files);
        });
      } else {
        // Merge only current active folder
        const currentTab = folderTabs.find(t => t.path === activeFolder);
        if (currentTab) {
          allFilesToMerge = currentTab.files;
        }
      }

      const payload = allFilesToMerge
        .filter(r => r.success && r.short_code)
        .map(r => ({ filePath: r.filePath, short_code: r.short_code }));

      if (payload.length === 0) {
        alert('Không có trang hợp lệ để gộp.');
        setMergeInProgress(false);
        return;
      }

      // Group files by folder
      const folderGroups = {};
      payload.forEach(item => {
        const result = allFilesToMerge.find(r => r.filePath === item.filePath);
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
          mergeMode: outputOption === 'same_folder' ? 'root' : (outputOption === 'new_folder' ? 'new' : 'custom'),
          mergeSuffix: mergeSuffix || '_merged',
          parentFolder: folder,
          customOutputFolder: outputOption === 'custom_folder' ? outputFolder : null
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
      setMergeInProgress(false);
    }
  };

  // Inline editor component is imported from separate file (InlineShortCodeEditor.js)
  // with full autocomplete support - no need to redefine here

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
      
      {/* COMPACT TOP BAR - 1 line */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
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
              {sortGCNToTop ? '✅ Đang BẬT' : '❌ Đang TẮT'}
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Title */}
          <div className="flex-shrink-0">
            <h2 className="text-lg font-bold text-gray-900">📋 Quét danh sách</h2>
          </div>
          
          {/* File TXT Input */}
          <div className="flex items-center gap-2 flex-1">
            <button 
              onClick={handleSelectTxtFile}
              disabled={isLoadingFolders || isScanning}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors font-medium"
            >
              📄 Chọn TXT
            </button>
            {txtFilePath && (
              <span className="text-sm text-gray-600 truncate" title={txtFilePath}>
                ✅ {getFileName(txtFilePath)}
              </span>
            )}
          </div>
          
          {/* OCR Engine */}
          <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg border flex-shrink-0">
            <span className="text-xs text-gray-500">OCR:</span>
            <span className="text-sm font-medium text-gray-900">{ocrEngine}</span>
          </div>
          
          {/* Search Button */}
          <button 
            onClick={handleLoadFolders}
            disabled={isLoadingFolders || !txtFilePath}
            className="px-5 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:bg-gray-300 transition-colors font-medium shadow-sm flex-shrink-0"
          >
            {isLoadingFolders ? '⏳ Đang tìm...' : '🔍 Tìm kiếm thư mục'}
          </button>
        </div>
      </div>

      {/* Duplicate Folders Warning */}
      {duplicateFolders.length > 0 && !isScanning && (
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div className="flex-1">
              <div className="font-semibold text-yellow-900 mb-2">
                Phát hiện {duplicateFolders.length} thư mục trùng tên
              </div>
              <div className="text-sm text-yellow-800 space-y-2">
                {duplicateFolders.map((dup, idx) => (
                  <div key={idx} className="bg-yellow-100 rounded p-2">
                    <div className="font-medium">📁 "{dup.name}"</div>
                    <div className="text-xs mt-1 space-y-1">
                      <div className="text-green-700">✅ Sẽ quét: {dup.paths[0]}</div>
                      {dup.paths.slice(1).map((path, i) => (
                        <div key={i} className="text-red-700">❌ Bỏ qua: {path}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-xs text-yellow-700 mt-2">
                💡 Chỉ thư mục đầu tiên sẽ được quét. Các thư mục trùng tên khác sẽ bị bỏ qua.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DISCOVERED FOLDERS - Compact Table Style */}
      {discoveredFolders.length > 0 && !isScanning && (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">
              📂 Thư mục tìm thấy ({discoveredFolders.filter(f => f.selected && f.valid).length}/{discoveredFolders.filter(f => f.valid).length})
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => selectAllFolders(true)}
                className="text-xs px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
              >
                ✓ Chọn tất cả
              </button>
              <button
                onClick={() => selectAllFolders(false)}
                className="text-xs px-3 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
              >
                ✕ Bỏ chọn
              </button>
              <button
                onClick={handleStartScan}
                disabled={discoveredFolders.filter(f => f.selected && f.valid).length === 0}
                className="px-4 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:bg-gray-300 font-medium"
              >
                🚀 Quét {discoveredFolders.filter(f => f.selected && f.valid).length} thư mục
              </button>
            </div>
          </div>
          
          {/* Table style list */}
          <div className="divide-y max-h-96 overflow-y-auto">
            {discoveredFolders.map((folder, idx) => (
              <div 
                key={idx}
                className={`px-4 py-3 flex items-center gap-3 ${
                  folder.valid 
                    ? (folder.selected ? 'bg-blue-50 hover:bg-blue-100' : 'hover:bg-gray-50')
                    : 'opacity-60'
                }`}
              >
                {/* Checkbox */}
                {folder.valid && (
                  <input
                    type="checkbox"
                    checked={folder.selected}
                    onChange={() => toggleFolderSelection(folder.path)}
                    className="w-4 h-4 text-blue-600"
                  />
                )}
                {!folder.valid && (
                  <div className="w-4 h-4 flex items-center justify-center text-red-500 text-sm">✕</div>
                )}

                {/* Folder Info - Name and path on SAME LINE */}
                <div className="flex-1 min-w-0 flex items-center gap-2">
                  <span className="font-medium text-sm text-gray-900 flex-shrink-0">{folder.name}</span>
                  <span className="text-xs text-gray-400">•</span>
                  <span className="text-xs text-gray-500 truncate" title={folder.path}>{folder.path}</span>
                </div>

                {/* Badge */}
                {folder.valid && (
                  <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full font-medium flex-shrink-0">
                    {folder.imageCount} ảnh
                  </span>
                )}
                {!folder.valid && (
                  <span className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-full font-medium flex-shrink-0">
                    {folder.error}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress bar moved to folder tabs section */}
      {/* Scanning Status - REMOVED, show in tabs instead */}
      {false && isScanning && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="font-medium text-blue-900">Đang xử lý batch scan...</span>
            </div>
            {/* Live Timer */}
            <div className="flex items-center gap-2 bg-blue-100 px-4 py-2 rounded-lg">
              <span className="text-2xl">⏱️</span>
              <div className="text-right">
                <div className="text-xs text-blue-600 font-medium">Thời gian đã quét</div>
                <div className="text-lg font-bold text-blue-900">
                  {Math.floor(elapsedTime / 60)}:{String(elapsedTime % 60).padStart(2, '0')}
                </div>
              </div>
            </div>
          </div>

          {/* Folder Progress */}
          {progress.totalFolders > 0 && (
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-blue-800 font-medium">📂 Thư mục: {progress.processedFolders}/{progress.totalFolders}</span>
                <span className="text-blue-600">{Math.round((progress.processedFolders / progress.totalFolders) * 100)}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.processedFolders / progress.totalFolders) * 100}%` }}
                ></div>
              </div>
              {progress.currentFolder && (
                <div className="text-xs text-blue-700 mt-2 truncate" title={progress.currentFolder}>
                  ➜ {progress.currentFolder}
                </div>
              )}
            </div>
          )}

          {/* File Progress */}
          {progress.totalFiles > 0 && (
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-blue-800 font-medium">🖼️ Files trong thư mục: {progress.processedFiles}/{progress.totalFiles}</span>
                <span className="text-blue-600">{Math.round((progress.processedFiles / progress.totalFiles) * 100)}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.processedFiles / progress.totalFiles) * 100}%` }}
                ></div>
              </div>
              {progress.currentFile && (
                <div className="text-xs text-blue-700 mt-2">
                  ➜ {progress.currentFile}
                </div>
              )}
            </div>
          )}

          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-blue-700">
              Vui lòng đợi. Quá trình này có thể mất vài phút tùy thuộc vào số lượng file.
            </p>
            <button
              onClick={handleStopScan}
              disabled={shouldStop}
              className="px-5 py-2.5 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-300 transition-colors font-medium"
            >
              {shouldStop ? '⏸️ Đang dừng...' : '⏹️ Dừng quét'}
            </button>
          </div>
        </div>
      )}

      {/* Folder Tabs - Show during and after scanning (TABS NGANG giống DesktopScanner) */}
      {folderTabs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          {/* Header with Stop/Merge All buttons */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">📂 Thư mục ({folderTabs.length})</h2>
            <div className="flex gap-2">
              {isScanning && (
                <button
                  onClick={handleStopScan}
                  className="px-4 py-2 text-sm bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium"
                >
                  ⏹️ Dừng quét
                </button>
              )}
              {!isScanning && folderTabs.some(t => t.files.length > 0) && (
                <button
                  onClick={() => handleMerge(true)}
                  disabled={mergeInProgress}
                  className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-300 transition-all shadow-sm font-medium"
                >
                  {mergeInProgress ? '⏳ Đang gộp...' : '📚 Gộp tất cả thư mục'}
                </button>
              )}
            </div>
          </div>

          {/* Tabs ngang (horizontal tabs) */}
          <div className="flex items-center gap-2 overflow-auto mb-4">
            {folderTabs.map((tab) => (
              <button 
                key={tab.path} 
                onClick={() => setActiveFolder(tab.path)}
                title={`${tab.name} (${tab.files.length} files)`}
                className={`px-3 py-2 text-xs rounded-xl border flex items-center gap-2 min-w-[120px] max-w-[180px] relative ${
                  activeFolder === tab.path 
                    ? 'bg-blue-50 border-blue-300 text-blue-900 font-medium' 
                    : 'bg-white hover:bg-gray-50 border-gray-300'
                }`}
              >
                {/* UNKNOWN badge */}
                {(() => {
                  const unknownCount = (tab.files || []).filter(f => f.short_code === 'UNKNOWN').length;
                  if (unknownCount > 0 && tab.status === 'done') {
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
                
                <span className="truncate flex-1">{tab.name} ({tab.files.length})</span>
                {tab.status === 'scanning' ? (
                  <span className="animate-spin flex-shrink-0">⚙️</span>
                ) : tab.status === 'done' ? (
                  <span className="text-green-600 flex-shrink-0">✓</span>
                ) : (
                  <span className="text-gray-400 flex-shrink-0">○</span>
                )}
              </button>
            ))}
          </div>

          {/* Progress bar cho tab đang scan */}
          {folderTabs.find(t => t.path === activeFolder && t.status === 'scanning') && (
            <div className="mb-4 p-3 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-blue-700">
                  Đang quét... {folderTabs.find(t => t.path === activeFolder).files.length}/{folderTabs.find(t => t.path === activeFolder).count}
                </span>
                <span className="text-blue-600">
                  {Math.round((folderTabs.find(t => t.path === activeFolder).files.length / folderTabs.find(t => t.path === activeFolder).count) * 100)}%
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ 
                    width: `${(folderTabs.find(t => t.path === activeFolder).files.length / folderTabs.find(t => t.path === activeFolder).count) * 100}%` 
                  }}
                ></div>
              </div>
              {progress.currentFile && (
                <div className="text-xs text-blue-600 mt-1">➜ {progress.currentFile}</div>
              )}
            </div>
          )}

          {/* UNKNOWN Files Counter for active folder */}
          {(() => {
            const activeTab = folderTabs.find(t => t.path === activeFolder);
            if (activeTab && activeTab.status === 'done') {
              const unknownCount = (activeTab.files || []).filter(f => f.short_code === 'UNKNOWN').length;
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
                        <span>{unknownCount}/{(activeTab.files || []).length}</span>
                      </div>
                    </div>
                  </div>
                );
              }
            }
            return null;
          })()}

          {/* Manual Load Preview Button for active folder */}
          {activeFolder && folderTabs.find(t => t.path === activeFolder && t.status === 'done') && !foldersPreviewsLoaded.has(activeFolder) && (
            <div className="mb-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">🖼️</span>
                  <div>
                    <div className="text-sm text-green-900 font-medium">Preview chưa được load</div>
                    <div className="text-xs text-green-700 mt-0.5">
                      Nhấn nút để load preview images cho thư mục này
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleLoadPreviewsForFolder(activeFolder)}
                  disabled={loadingPreviewFor === activeFolder}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm transition-all shadow-md hover:shadow-lg"
                >
                  {loadingPreviewFor === activeFolder ? (
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

          {/* Files grid cho tab active */}
          {activeFolder && folderTabs.find(t => t.path === activeFolder && t.files.length > 0) && (
            <div>
              <div className="flex items-center justify-between mb-3 p-3 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg border border-indigo-200">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-900">
                    📂 {folderTabs.find(t => t.path === activeFolder).name}
                  </span>
                  <span className="text-xs text-gray-600">
                    ({folderTabs.find(t => t.path === activeFolder).files.length} files)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {folderTabs.find(t => t.path === activeFolder && t.status === 'done') && !isScanning && (
                    <button
                      onClick={() => handleMerge(false)}
                      disabled={mergeInProgress}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors disabled:bg-gray-300"
                    >
                      {mergeInProgress ? '⏳ Đang gộp...' : '📚 Gộp thư mục này'}
                    </button>
                  )}
                  <select 
                    value={density} 
                    onChange={(e) => setDensity(e.target.value)} 
                    className="text-xs border rounded px-2 py-1 bg-white"
                  >
                    <option value="high">Mật độ cao (5)</option>
                    <option value="medium">Trung bình (4)</option>
                    <option value="low">Thấp (3)</option>
                  </select>
                </div>
              </div>

              {/* Action buttons - TOP */}
              {folderTabs.find(t => t.path === activeFolder)?.files?.length > 0 && (
                <ActionButtonGroup
                  onNext={() => {
                    const idx = folderTabs.findIndex(t => t.path === activeFolder);
                    if (idx < folderTabs.length - 1) {
                      setActiveFolder(folderTabs[idx + 1].path);
                    }
                  }}
                  onBack={() => {
                    const idx = folderTabs.findIndex(t => t.path === activeFolder);
                    if (idx > 0) {
                      setActiveFolder(folderTabs[idx - 1].path);
                    }
                  }}
                  hasNext={folderTabs.findIndex(t => t.path === activeFolder) < folderTabs.length - 1}
                  hasBack={folderTabs.findIndex(t => t.path === activeFolder) > 0}
                  position="top"
                />
              )}
              
              {/* Grid */}
              <div className={`grid gap-4 ${gridColsClass}`}>
                {folderTabs.find(t => t.path === activeFolder).files.map((result, idx) => {
                  const currentTab = folderTabs.find(t => t.path === activeFolder);
                  const highlight = getDocumentHighlight(result.short_code, currentTab.name);
                  const rowClass = getRowHighlight(result.short_code, currentTab.name);
                  return (
              <div key={idx} className={`p-3 rounded-lg ${highlight.bgClass} ${highlight.borderClass} ${rowClass} hover:shadow-md transition-shadow`}>
                {/* Preview Image */}
                <div className="mb-3">
                  {result.previewUrl ? (
                    <img 
                      src={result.previewUrl} 
                      alt={result.fileName} 
                      className="w-full h-40 object-contain border rounded bg-gray-50"
                    />
                  ) : (
                    <div className="w-full h-40 flex items-center justify-center border rounded text-xs text-gray-500 bg-gray-50">
                      Không có preview
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="text-sm font-medium truncate" title={result.fileName}>
                  {result.fileName}
                </div>
                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                  {getMethodBadge(result.method)}
                  <span className="ml-auto font-semibold">{formatConfidence(result.confidence)}%</span>
                </div>
                <div className="mt-2 text-xs text-gray-600 flex items-center gap-2">
                  <span>Loại: {result.doc_type || 'N/A'} | Mã: <span className="text-blue-600 font-semibold">{result.short_code}</span></span>
                  {getDocumentBadge(result.short_code, currentTab.name)}
                </div>
                {/* Timing Info */}
                {result.durationSeconds && (
                  <div className="mt-1 text-xs text-orange-600 flex items-center gap-1">
                    <span>⏱️</span>
                    <span className="font-medium">{result.durationSeconds}s</span>
                  </div>
                )}

                      {/* Inline Editor */}
                      <div className="mt-2 p-2 bg-gray-50 border rounded">
                        <InlineShortCodeEditor 
                          value={result.short_code} 
                          onChange={(newCode) => {
                            setFolderTabs(prev => prev.map(t => {
                              if (t.path !== activeFolder) return t;
                              const newFiles = [...t.files];
                              newFiles[idx] = { ...newFiles[idx], short_code: newCode };
                              return { ...t, files: newFiles };
                            }));
                          }}
                          onEditStart={() => setIsEditingFileId(`${activeFolder}-${idx}`)}
                          onEditEnd={() => setIsEditingFileId(null)}
                        />
                      </div>

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
                    </div>

                    {/* Folder Info */}
                    <div className="mt-2 text-xs text-gray-500 truncate" title={result.folder}>
                      📂 {getFileName(result.folder)}
                    </div>
                  </div>
                );
                })}
              </div>
              
              {/* Action buttons - BOTTOM */}
              {folderTabs.find(t => t.path === activeFolder)?.files?.length > 0 && (
                <ActionButtonGroup
                  onNext={() => {
                    const idx = folderTabs.findIndex(t => t.path === activeFolder);
                    if (idx < folderTabs.length - 1) {
                      setActiveFolder(folderTabs[idx + 1].path);
                    }
                  }}
                  onBack={() => {
                    const idx = folderTabs.findIndex(t => t.path === activeFolder);
                    if (idx > 0) {
                      setActiveFolder(folderTabs[idx - 1].path);
                    }
                  }}
                  hasNext={folderTabs.findIndex(t => t.path === activeFolder) < folderTabs.length - 1}
                  hasBack={folderTabs.findIndex(t => t.path === activeFolder) > 0}
                  position="bottom"
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Preview Modal */}
      {selectedPreview && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedPreview(null)}
        >
          <div className="max-w-6xl max-h-full">
            <img 
              src={selectedPreview} 
              alt="Preview" 
              className="max-w-full max-h-screen object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          <button
            onClick={() => setSelectedPreview(null)}
            className="absolute top-4 right-4 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-100"
          >
            ✕ Đóng
          </button>
        </div>
      )}

      {/* Merge Modal */}
      {showMergeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              📚 {isMergeAll ? 'Gộp PDF tất cả thư mục' : 'Gộp PDF thư mục hiện tại'}
            </h3>
            
            <p className="text-sm text-gray-600 mb-4">
              {isMergeAll 
                ? `Gộp PDF cho ${folderTabs.length} thư mục. Chọn cách lưu file PDF:`
                : 'Chọn cách lưu file PDF sau khi gộp:'
              }
            </p>

            <div className="space-y-3">
              {/* Option 1: Same Folder */}
              <label className="flex items-start space-x-3 cursor-pointer p-3 border rounded-lg hover:bg-gray-50">
                <input
                  type="radio"
                  name="mergeOutput"
                  value="same_folder"
                  checked={outputOption === 'same_folder'}
                  onChange={(e) => setOutputOption(e.target.value)}
                  className="mt-1"
                />
                <div>
                  <div className="font-medium text-gray-900">Gộp vào thư mục gốc</div>
                  <div className="text-sm text-gray-600">PDF sẽ được lưu trực tiếp vào thư mục gốc của mỗi folder</div>
                </div>
              </label>

              {/* Option 2: New Folder */}
              <label className="flex items-start space-x-3 cursor-pointer p-3 border rounded-lg hover:bg-gray-50">
                <input
                  type="radio"
                  name="mergeOutput"
                  value="new_folder"
                  checked={outputOption === 'new_folder'}
                  onChange={(e) => setOutputOption(e.target.value)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Tạo thư mục mới</div>
                  <div className="text-sm text-gray-600 mb-2">Tên thư mục = Thư mục gốc + ký tự tùy chọn</div>
                  {outputOption === 'new_folder' && (
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-sm text-gray-700">Ký tự thêm vào:</span>
                      <input
                        type="text"
                        value={mergeSuffix}
                        onChange={(e) => setMergeSuffix(e.target.value)}
                        placeholder="_merged"
                        className="flex-1 px-3 py-1.5 text-sm border rounded"
                      />
                    </div>
                  )}
                </div>
              </label>

              {/* Option 3: Custom Folder */}
              <label className="flex items-start space-x-3 cursor-pointer p-3 border rounded-lg hover:bg-gray-50">
                <input
                  type="radio"
                  name="mergeOutput"
                  value="custom_folder"
                  checked={outputOption === 'custom_folder'}
                  onChange={(e) => setOutputOption(e.target.value)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Lưu vào thư mục chỉ định</div>
                  <div className="text-sm text-gray-600 mb-2">Chọn thư mục để lưu tất cả PDF</div>
                  {outputOption === 'custom_folder' && (
                    <button
                      onClick={handleSelectOutputFolder}
                      className="mt-2 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      📁 Chọn thư mục
                    </button>
                  )}
                  {outputOption === 'custom_folder' && outputFolder && (
                    <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                      ✅ {getFileName(outputFolder)}
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
                onClick={() => executeMerge(isMergeAll)}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                {isMergeAll ? 'Gộp tất cả thư mục' : 'Gộp thư mục hiện tại'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Scan Statistics Summary */}
      {scanResults && !isScanning && (
        <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Thống kê tổng quan</h3>

          {/* Statistics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{scanResults.total_folders}</div>
              <div className="text-sm text-gray-600">Tổng thư mục</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{scanResults.valid_folders}</div>
              <div className="text-sm text-gray-600">Thư mục hợp lệ</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{scanResults.processed_files}/{scanResults.total_files}</div>
              <div className="text-sm text-gray-600">Files xử lý</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{scanResults.error_count}</div>
              <div className="text-sm text-gray-600">Lỗi</div>
            </div>
            {/* Timer Stats */}
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {Math.floor(timers.batchElapsedSeconds / 60)}:{String(timers.batchElapsedSeconds % 60).padStart(2, '0')}
              </div>
              <div className="text-sm text-gray-600">⏱️ Tổng thời gian</div>
              {scanResults.processed_files > 0 && (
                <div className="text-xs text-orange-500 mt-1">
                  ~{(timers.batchElapsedSeconds / scanResults.processed_files).toFixed(1)}s/file
                </div>
              )}
            </div>
          </div>

          {/* Performance Stats */}
          {timers.fileTimings.length > 0 && (
            <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-4 mt-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">⏱️</span>
                <span>Thống kê hiệu năng - {ocrEngine === 'gemini-flash-hybrid' ? '🔄 Gemini Hybrid' : ocrEngine === 'gemini-flash' ? '🤖 Gemini Flash' : ocrEngine === 'gemini-flash-lite' ? '⚡ Gemini Flash Lite' : ocrEngine}</span>
              </h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white p-3 rounded border border-orange-200">
                  <div className="text-xs text-gray-600 mb-1">Tổng thời gian</div>
                  <div className="text-lg font-bold text-orange-600">
                    {Math.floor(timers.batchElapsedSeconds / 60)}:{String(timers.batchElapsedSeconds % 60).padStart(2, '0')}
                  </div>
                </div>
                
                <div className="bg-white p-3 rounded border border-orange-200">
                  <div className="text-xs text-gray-600 mb-1">TB mỗi file</div>
                  <div className="text-lg font-bold text-blue-600">
                    {timers.fileTimings.length > 0 
                      ? (timers.fileTimings.reduce((sum, f) => sum + f.durationMs, 0) / timers.fileTimings.length / 1000).toFixed(2) 
                      : '0.00'}s
                  </div>
                </div>
                
                <div className="bg-white p-3 rounded border border-orange-200">
                  <div className="text-xs text-gray-600 mb-1">Nhanh nhất</div>
                  <div className="text-lg font-bold text-green-600">
                    {timers.fileTimings.length > 0 
                      ? (Math.min(...timers.fileTimings.map(f => f.durationMs)) / 1000).toFixed(2) 
                      : '0.00'}s
                  </div>
                </div>
                
                <div className="bg-white p-3 rounded border border-orange-200">
                  <div className="text-xs text-gray-600 mb-1">Chậm nhất</div>
                  <div className="text-lg font-bold text-red-600">
                    {timers.fileTimings.length > 0 
                      ? (Math.max(...timers.fileTimings.map(f => f.durationMs)) / 1000).toFixed(2) 
                      : '0.00'}s
                  </div>
                </div>
              </div>
              
              {/* Speed Rating */}
              {timers.fileTimings.length > 0 && (
                <div className="mt-3 text-xs text-gray-700">
                  📊 Tốc độ: {(() => {
                    const avgTime = timers.fileTimings.reduce((sum, f) => sum + f.durationMs, 0) / timers.fileTimings.length / 1000;
                    if (avgTime < 2) return '🚀 Rất nhanh (< 2s/file)';
                    if (avgTime < 5) return '⚡ Nhanh (2-5s/file)';
                    if (avgTime < 10) return '✅ Trung bình (5-10s/file)';
                    return '🐢 Chậm (> 10s/file)';
                  })()}
                </div>
              )}
            </div>
          )}
          
          {/* Note about merging */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
            <div className="flex items-center gap-2 text-blue-900">
              <span className="text-xl">💡</span>
              <span className="font-medium">Gộp PDF từ các file đã quét bằng nút "📚 Gộp PDF" ở trên</span>
            </div>
          </div>

          {/* Skipped Folders */}
          {skippedFolders.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-900 mb-3">⚠️ Thư mục bị bỏ qua ({skippedFolders.length})</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {skippedFolders.map((item, idx) => (
                  <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm">
                    <div className="font-medium text-gray-900">{item.folder}</div>
                    <div className="text-yellow-700 mt-1">➜ {item.reason}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Errors */}
          {errors.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-900 mb-3">❌ Lỗi xử lý ({errors.length})</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {errors.map((item, idx) => (
                  <div key={idx} className="bg-red-50 border border-red-200 rounded p-3 text-sm">
                    <div className="font-medium text-gray-900">{item.file}</div>
                    <div className="text-red-700 mt-1">➜ {item.error}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Success Message */}
          {scanResults.processed_files > 0 && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <div>
                  <div className="font-semibold text-green-900">Quét hoàn tất!</div>
                  <div className="text-sm text-green-700 mt-1">
                    Đã xử lý thành công {scanResults.processed_files} file từ {scanResults.valid_folders} thư mục.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">📖 Hướng dẫn</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">1.</span>
            <span>Tạo file TXT với mỗi dòng là đường dẫn đến 1 thư mục (ví dụ: C:\Documents\Folder1)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">2.</span>
            <span>Chọn file TXT bằng nút "Chọn file TXT"</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">3.</span>
            <span>Chọn chế độ output: đổi tên tại chỗ, copy theo loại, hoặc copy tất cả</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">4.</span>
            <span>Nếu chọn copy, chọn thư mục đích</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">5.</span>
            <span>Nhấn "Bắt đầu quét" và đợi kết quả</span>
          </li>
        </ul>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            <strong>Lưu ý:</strong> Chỉ quét file ảnh JPG, JPEG, PNG trong thư mục gốc (không quét sub-folder).
            Thư mục không tồn tại hoặc không có ảnh sẽ bị bỏ qua.
          </p>
        </div>
      </div>
    </div>
  );
}

export default BatchScanner;
