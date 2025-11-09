import React, { useState, useEffect } from 'react';

function BatchScanner() {
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
  const [shouldStop, setShouldStop] = useState(false);
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

  // Load OCR engine from config on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const engine = await window.electronAPI.getConfig('ocrEngine');
        if (engine) setOcrEngine(engine);
      } catch (err) {
        console.error('Failed to load OCR engine config:', err);
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
      setDiscoveredFolders(result.folders);
      
      const validCount = result.folders.filter(f => f.valid).length;
      alert(`✅ Tìm thấy ${result.folders.length} thư mục\n\n- Hợp lệ: ${validCount}\n- Không hợp lệ: ${result.folders.length - validCount}\n\nVui lòng xem danh sách và bấm "Quét tất cả" để bắt đầu.`);
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
    setShouldStop(false);
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

    try {
      console.log('🚀 Starting batch scan...');
      console.log('📁 Selected folders:', selectedFolders.length);
      console.log('🔧 OCR Engine:', ocrEngine);

      // Scan each folder one by one (allows stopping)
      const allResults = [];
      const allErrors = [];
      const processedFolderPaths = [];

      for (let i = 0; i < selectedFolders.length; i++) {
        if (shouldStop) {
          console.log('⏸️ Scan stopped by user');
          break;
        }

        const folder = selectedFolders[i];
        console.log(`\n📂 [${i + 1}/${selectedFolders.length}] Scanning: ${folder.path}`);
        
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

        try {
          // Get image files in folder
          const imageFilesResult = await window.electronAPI.listFilesInFolder(folder.path);
          
          if (!imageFilesResult.success) {
            throw new Error(imageFilesResult.error || 'Failed to list files');
          }
          
          const validImages = imageFilesResult.files.filter(f => /\.(jpg|jpeg|png)$/i.test(f));
          
          console.log(`Found ${validImages.length} images in ${folder.name}`);
          
          // Scan each file and display immediately
          const folderResults = [];
          for (let j = 0; j < validImages.length; j++) {
            // Check shouldStop at start of each iteration
            if (shouldStop) {
              console.log('⏹️ Stopping at file:', j + 1);
              break;
            }

            const imagePath = validImages[j];
            const fileName = imagePath.split(/[/\\]/).pop();
            
            setProgress(prev => ({
              ...prev,
              processedFiles: j + 1,
              currentFile: fileName
            }));

            try {
              console.log(`  [${j + 1}/${validImages.length}] Processing: ${fileName}`);
              
              // Scan single file
              const fileResult = await window.electronAPI.processDocumentOffline(imagePath);
              
              if (fileResult.success) {
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
                  method: fileResult.method || 'offline_ocr'
                };

                folderResults.push(fileWithPreview);
                allResults.push({
                  original_path: imagePath,
                  short_code: fileResult.short_code || 'UNKNOWN',
                  doc_type: fileResult.doc_type || 'Unknown',
                  confidence: fileResult.confidence || 0,
                  folder: folder.path
                });

                // Add to fileResults and folder tab immediately (realtime display)
                setFileResults(prev => [...prev, fileWithPreview]);
                setFolderTabs(prev => prev.map(t => 
                  t.path === folder.path ? { ...t, files: [...t.files, fileWithPreview] } : t
                ));

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

          if (!shouldStop && folderResults.length > 0) {
            processedFolderPaths.push(folder.path);
            
            // Update folder tab to 'done'
            setFolderTabs(prev => prev.map(t => 
              t.path === folder.path ? { ...t, status: 'done', count: folderResults.length } : t
            ));
          }
        } catch (err) {
          console.error(`Error scanning ${folder.path}:`, err);
          allErrors.push({
            folder: folder.path,
            error: err.message
          });
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

      console.log('✅ Batch scan complete:', result);

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
        
        alert(`✅ Quét hoàn tất!\n\n📊 Thống kê:\n- Thư mục hợp lệ: ${result.valid_folders}/${result.total_folders}\n- Files xử lý: ${result.processed_files}/${result.total_files}\n- Lỗi: ${result.error_count}\n\n💡 Bạn có thể xem kết quả chi tiết và gộp PDF bên dưới.`);
      } else {
        alert(`❌ Lỗi: ${result.error}`);
      }
    } catch (err) {
      console.error('Batch scan error:', err);
      alert(`❌ Lỗi xử lý: ${err.message}`);
    } finally {
      setIsScanning(false);
      setShouldStop(false);
    }
  };

  // Stop scanning
  const handleStopScan = () => {
    setShouldStop(true);
    alert('⏸️ Đang dừng quét... Vui lòng đợi thư mục hiện tại hoàn tất.');
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

  // Apply sequential naming logic (UNKNOWN fallback)
  const applySequentialNaming = (result, lastType) => {
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
        // Merge only current folder
        allFilesToMerge = fileResults;
      }

      const payload = allFilesToMerge
        .filter(r => r.success && r.short_code)
        .map(r => ({ filePath: r.filePath, short_code: r.short_code }));

      if (payload.length === 0) {
        alert('Không có trang hợp lệ để gộp.');
        setMergeInProgress(false);
        return;
      }

      const mergeOptions = {
        autoSave: true,
        mergeMode: outputOption === 'same_folder' ? 'root' : 'new',
        mergeSuffix: mergeSuffix,
        parentFolder: null // Will be handled per folder
      };

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
        const folderMergeOptions = { ...mergeOptions, parentFolder: folder };
        const merged = await window.electronAPI.mergeByShortCode(items, folderMergeOptions);
        const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
        totalMerged += (merged || []).length;
        totalSuccess += okCount;
      }

      alert(`✅ Gộp PDF hoàn tất!\n\nThành công: ${totalSuccess}/${totalMerged} file PDF`);
    } catch (err) {
      console.error('Merge error:', err);
      alert(`❌ Lỗi khi gộp PDF: ${err.message}`);
    } finally {
      setMergeInProgress(false);
    }
  };

  // Inline short code editor component
  const InlineShortCodeEditor = ({ value, onChange }) => {
    const [editing, setEditing] = useState(false);
    const [tempValue, setTempValue] = useState(value);

    if (!editing) {
      return (
        <button
          onClick={() => { setEditing(true); setTempValue(value); }}
          className="text-xs text-blue-600 hover:underline"
        >
          ✏️ Sửa: {value}
        </button>
      );
    }

    return (
      <div className="flex gap-1">
        <input
          type="text"
          value={tempValue}
          onChange={(e) => setTempValue(e.target.value.toUpperCase())}
          className="flex-1 text-xs px-1 py-0.5 border rounded"
          autoFocus
        />
        <button
          onClick={() => { onChange(tempValue); setEditing(false); }}
          className="text-xs px-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          ✓
        </button>
        <button
          onClick={() => setEditing(false)}
          className="text-xs px-2 bg-gray-300 rounded hover:bg-gray-400"
        >
          ✕
        </button>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">📋 Quét theo danh sách</h2>
        <p className="text-gray-600 text-sm">
          Quét nhiều thư mục cùng lúc từ file TXT (mỗi dòng = đường dẫn thư mục)
        </p>
      </div>

      {/* Configuration Section */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Cấu hình</h3>

        {/* TXT File Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            1️⃣ Chọn file TXT danh sách thư mục
          </label>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSelectTxtFile}
              disabled={isLoadingFolders || isScanning}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              📄 Chọn file TXT
            </button>
            {txtFilePath && (
              <span className="text-sm text-gray-600" title={txtFilePath}>
                ✅ {getFileName(txtFilePath)}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            File TXT với mỗi dòng là đường dẫn đến 1 thư mục (ví dụ: C:\Documents\Folder1)
          </p>
        </div>

        {/* OCR Engine Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            2️⃣ OCR Engine (từ cài đặt)
          </label>
          <div className="px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700">
            🔧 <strong>{ocrEngine}</strong>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Để thay đổi OCR engine, vui lòng vào tab "⚙️ Cài đặt"
          </p>
        </div>

        {/* Note about merging */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <div className="font-semibold text-blue-900 mb-1">Về tính năng gộp PDF</div>
              <div className="text-sm text-blue-800">
                Sau khi quét, bạn sẽ thấy danh sách tất cả file đã quét. 
                Sử dụng nút <strong>"📚 Gộp PDF"</strong> để merge các ảnh cùng loại thành file PDF 
                và chọn nơi lưu (thư mục gốc, thư mục mới, hoặc thư mục tùy chọn).
              </div>
            </div>
          </div>
        </div>

        {/* Load Folders Button */}
        <div className="pt-4 border-t">
          <button
            onClick={handleLoadFolders}
            disabled={isLoadingFolders || !txtFilePath}
            className="w-full px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoadingFolders ? '⏳ Đang tìm thư mục...' : '🔍 Tìm kiếm thư mục'}
          </button>
        </div>
      </div>

      {/* Discovered Folders List */}
      {discoveredFolders.length > 0 && !isScanning && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              📂 Thư mục tìm thấy ({discoveredFolders.filter(f => f.selected && f.valid).length}/{discoveredFolders.filter(f => f.valid).length})
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => selectAllFolders(true)}
                className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                ✓ Chọn tất cả
              </button>
              <button
                onClick={() => selectAllFolders(false)}
                className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                ✕ Bỏ chọn tất cả
              </button>
            </div>
          </div>

          {/* Folder List */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {discoveredFolders.map((folder, idx) => (
              <div 
                key={idx}
                className={`p-4 border rounded-lg ${
                  folder.valid 
                    ? (folder.selected ? 'bg-blue-50 border-blue-300' : 'bg-white border-gray-200')
                    : 'bg-gray-50 border-gray-200 opacity-60'
                }`}
              >
                <div className="flex items-center gap-3">
                  {/* Checkbox */}
                  {folder.valid && (
                    <input
                      type="checkbox"
                      checked={folder.selected}
                      onChange={() => toggleFolderSelection(folder.path)}
                      className="w-5 h-5 text-blue-600"
                    />
                  )}
                  {!folder.valid && (
                    <div className="w-5 h-5 flex items-center justify-center text-red-500">
                      ✕
                    </div>
                  )}

                  {/* Folder Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 truncate" title={folder.name}>
                        {folder.name}
                      </span>
                      {folder.valid && (
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                          {folder.imageCount} ảnh
                        </span>
                      )}
                      {!folder.valid && (
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">
                          {folder.error}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 truncate mt-1" title={folder.path}>
                      {folder.path}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Scan Button */}
          <div className="mt-6 pt-4 border-t">
            <button
              onClick={handleStartScan}
              disabled={discoveredFolders.filter(f => f.selected && f.valid).length === 0}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              🚀 Quét {discoveredFolders.filter(f => f.selected && f.valid).length} thư mục
            </button>
          </div>
        </div>
      )}

      {/* Scanning Status */}
      {isScanning && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="font-medium text-blue-900">Đang xử lý batch scan...</span>
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

      {/* Folder Tabs - Only show after scanning */}
      {folderTabs.length > 0 && !isScanning && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">📂 Thư mục đã quét ({folderTabs.length})</h2>
            <button
              onClick={() => handleMerge(true)}
              disabled={mergeInProgress || isScanning}
              className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-300 transition-all shadow-sm font-medium"
            >
              {mergeInProgress ? '⏳ Đang gộp...' : '📚 Gộp tất cả thư mục'}
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex items-center gap-2 overflow-auto mb-4">
            {folderTabs.map((tab) => (
              <button 
                key={tab.path} 
                onClick={() => {
                  setActiveFolder(tab.path);
                  setFileResults(tab.files);
                }}
                title={`${tab.name} (${tab.count} files)`}
                className={`px-3 py-2 text-xs rounded-xl border flex items-center gap-2 min-w-[120px] max-w-[180px] ${
                  activeFolder === tab.path 
                    ? 'bg-blue-50 border-blue-300 text-blue-900 font-medium' 
                    : 'bg-white hover:bg-gray-50 border-gray-300'
                }`}
              >
                <span className="truncate flex-1">{tab.name} ({tab.count})</span>
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
        </div>
      )}

      {/* File Results Grid - Show files of active folder only */}
      {activeFolder && folderTabs.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          {folderTabs.map((tab) => (
            activeFolder === tab.path && (
              <div key={tab.path}>
                {/* Scanning indicator */}
                {tab.status === 'scanning' && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-xl border border-blue-200">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="animate-spin text-xl">⚙️</div>
                      <span className="text-sm text-blue-900 font-medium">
                        Đang quét thư mục "{tab.name}"... ({tab.files.length}/{tab.count})
                      </span>
                    </div>
                    <div className="w-full bg-blue-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(tab.files.length / tab.count) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    📁 {tab.name} - {tab.files.length} files
                  </h2>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Mật độ:</label>
                <select 
                  value={density} 
                  onChange={(e) => setDensity(e.target.value)} 
                  className="text-sm border rounded px-3 py-1.5"
                >
                  <option value="high">Cao (5)</option>
                  <option value="medium">TB (4)</option>
                  <option value="low">Thấp (3)</option>
                </select>
              </div>
              <button
                onClick={handleMerge}
                disabled={mergeInProgress || isScanning}
                className="px-5 py-2.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 transition-all shadow-sm font-medium"
              >
                {mergeInProgress ? '⏳ Đang gộp...' : '📚 Gộp PDF'}
              </button>
            </div>
          </div>

                {/* Grid */}
                <div className={`grid gap-4 ${gridColsClass}`}>
                  {tab.files.map((result, idx) => (
              <div key={idx} className="p-3 border rounded-lg bg-white hover:shadow-md transition-shadow">
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
                <div className="mt-2 text-xs text-gray-600">
                  Loại: {result.doc_type || 'N/A'} | Mã: <span className="text-blue-600 font-semibold">{result.short_code}</span>
                </div>

                    {/* Inline Editor */}
                    <div className="mt-2 p-2 bg-gray-50 border rounded">
                      <InlineShortCodeEditor 
                        value={result.short_code} 
                        onChange={(newCode) => {
                          setFolderTabs(prev => prev.map(t => {
                            if (t.path !== tab.path) return t;
                            const newFiles = [...t.files];
                            newFiles[idx] = { ...newFiles[idx], short_code: newCode };
                            return { ...t, files: newFiles };
                          }));
                        }} 
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
                ))}
              </div>
            </div>
          )
        ))}
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
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
          </div>

          {/* Note about merging */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
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
