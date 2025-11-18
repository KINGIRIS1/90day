import React, { useState, useRef } from 'react';
import { handleError, isCriticalError } from '../utils/errorHandler';

/**
 * Only GCN Scanner - Chế độ đặc biệt
 * - Quét và phân loại tất cả file
 * - GCN A3 (GCNC/GCNM) → Đặt tên theo GCN
 * - File khác → Đặt tên "GTLQ"
 * - Giữ nguyên thứ tự file
 */
function OnlyGCNScanner() {
  const [scanMode, setScanMode] = useState('folder'); // 'folder' or 'batch'
  const [usePreFilter, setUsePreFilter] = useState(false); // Pre-filter OFF by default
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [currentPhase, setCurrentPhase] = useState(''); // 'prefilter', 'scanning', 'complete'
  const [currentFile, setCurrentFile] = useState('');
  const [currentFolder, setCurrentFolder] = useState('');
  const [folderProgress, setFolderProgress] = useState({ current: 0, total: 0 });
  const [phaseStats, setPhaseStats] = useState({ passed: 0, skipped: 0, scanned: 0 });
  const [txtFilePath, setTxtFilePath] = useState('');
  const [isLoadingFolders, setIsLoadingFolders] = useState(false);
  const [folderList, setFolderList] = useState([]);
  const stopRef = useRef(false);

  // Load OCR engine config
  const [ocrEngine, setOcrEngine] = useState('gemini-flash-lite');

  React.useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const engine = await window.electronAPI.getConfig('ocrEngine');
      setOcrEngine(engine || 'gemini-flash-lite');
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  // Select folder
  const handleSelectFolder = async () => {
    try {
      // Check if API is available
      if (!window.electronAPI.getImagesInFolder) {
        alert('⚠️ Chức năng này cần cập nhật app.\n\nVui lòng:\n1. Save to GitHub\n2. Pull code mới\n3. Đóng app hoàn toàn\n4. Xóa cache: %APPDATA%\\Electron\n5. Chạy: yarn install\n6. Restart app');
        return;
      }

      const folderPath = await window.electronAPI.selectFolder();
      if (!folderPath) return;

      // Get all image files
      const imageFiles = await window.electronAPI.getImagesInFolder(folderPath);
      
      if (imageFiles.length === 0) {
        alert('Không tìm thấy file ảnh nào trong thư mục!');
        return;
      }

      setFiles(imageFiles);
      setResults([]);
      setTxtFilePath('');
      console.log(`📁 Selected folder: ${imageFiles.length} files`);
    } catch (err) {
      console.error('Error selecting folder:', err);
      alert('Lỗi chọn thư mục: ' + err.message);
    }
  };

  // Select txt file for batch mode
  const handleSelectTxtFile = async () => {
    try {
      // Check if API is available
      if (!window.electronAPI.getImagesInFolder) {
        alert('⚠️ Chức năng này cần cập nhật app.\n\nVui lòng:\n1. Save to GitHub\n2. Pull code mới\n3. Đóng app hoàn toàn\n4. Xóa cache: %APPDATA%\\Electron\n5. Chạy: yarn install\n6. Restart app');
        return;
      }

      const txtPath = await window.electronAPI.selectTxtFile();
      if (!txtPath) return;

      setTxtFilePath(txtPath);
      setFolderList([]);
      setFiles([]);
      setResults([]);
      
      console.log(`📋 Selected txt file: ${txtPath}`);
    } catch (err) {
      console.error('Error selecting txt file:', err);
      alert('Lỗi chọn file txt: ' + err.message);
    }
  };

  // Load folders from txt file
  const handleLoadFolders = async () => {
    if (!txtFilePath) {
      alert('Vui lòng chọn file txt trước!');
      return;
    }

    setIsLoadingFolders(true);
    
    try {
      // Read and validate folders from txt
      const validation = await window.electronAPI.validateBatchFolders(txtFilePath);
      
      if (!validation.success) {
        alert('Lỗi đọc file txt: ' + validation.error);
        setIsLoadingFolders(false);
        return;
      }

      setFolderList(validation.folders);

      // Collect all image files from all folders
      const allFiles = [];
      for (const folder of validation.folders) {
        const imageFiles = await window.electronAPI.getImagesInFolder(folder.path);
        allFiles.push(...imageFiles);
      }

      if (allFiles.length === 0) {
        alert('Không tìm thấy file ảnh nào trong các thư mục!');
        setIsLoadingFolders(false);
        return;
      }

      setFiles(allFiles);
      console.log(`✅ Loaded ${validation.folders.length} folders: ${allFiles.length} total files`);
    } catch (err) {
      console.error('Error loading folders:', err);
      alert('Lỗi tải thư mục: ' + err.message);
    } finally {
      setIsLoadingFolders(false);
    }
  };

  // Start scanning with pre-filter BY FOLDER
  const handleStartScan = async () => {
    if (files.length === 0) {
      alert('Vui lòng chọn thư mục trước!');
      return;
    }

    setIsScanning(true);
    setResults([]);
    setCurrentPhase('prefilter');
    setPhaseStats({ passed: 0, skipped: 0, scanned: 0 });
    stopRef.current = false;

    const allResults = [];

    try {
      // Check if pre-filter API is available
      const hasPreFilter = !!window.electronAPI.preFilterGCNFiles;

      // Group files by folder
      const folderGroups = {};
      files.forEach(filePath => {
        const folderPath = filePath.substring(0, filePath.lastIndexOf(/[/\\]/.exec(filePath)[0]));
        if (!folderGroups[folderPath]) {
          folderGroups[folderPath] = [];
        }
        folderGroups[folderPath].push(filePath);
      });

      const folderPaths = Object.keys(folderGroups);
      console.log(`📁 Processing ${folderPaths.length} folders...`);
      
      setFolderProgress({ current: 0, total: folderPaths.length });

      // Process each folder
      for (let folderIdx = 0; folderIdx < folderPaths.length; folderIdx++) {
        if (stopRef.current) {
          console.log('⏹️ Scan stopped by user');
          break;
        }

        const folderPath = folderPaths[folderIdx];
        const folderFiles = folderGroups[folderPath];
        const folderName = folderPath.split(/[/\\]/).pop() || 'root';

        setFolderProgress({ current: folderIdx + 1, total: folderPaths.length });
        setCurrentFolder(folderName);

        console.log(`\n📂 [${folderIdx + 1}/${folderPaths.length}] Processing folder: ${folderName}`);
        console.log(`   Files: ${folderFiles.length}`);

        // Phase 1: Pre-filter THIS FOLDER
        setCurrentPhase('prefilter');
        setCurrentFile(`Đang phân tích màu sắc thư mục ${folderName}...`);
        
        const preFilterStart = Date.now();
        const preFilterResults = hasPreFilter
          ? await window.electronAPI.preFilterGCNFiles(folderFiles)
          : { passed: folderFiles, skipped: [] };
        
        const preFilterTime = ((Date.now() - preFilterStart) / 1000).toFixed(1);
        
        const gcnCandidates = preFilterResults.passed || [];
        const skipped = preFilterResults.skipped || [];
        
        console.log(`   🎨 Pre-filter: ${gcnCandidates.length} GCN, ${skipped.length} skipped (${preFilterTime}s)`);
        
        // Add skipped files as GTLQ
        for (const filePath of skipped) {
          const fileName = filePath.split(/[/\\]/).pop();
          allResults.push({
            fileName,
            filePath,
            folderName,
            previewUrl: null,
            originalShortCode: 'SKIPPED',
            originalDocType: 'Bỏ qua (không phải GCN)',
            newShortCode: 'GTLQ',
            newDocType: 'Giấy tờ liên quan',
            confidence: 0,
            reasoning: 'Pre-filter: Không có màu GCN (red/pink)',
            metadata: {},
            success: true,
            preFiltered: true
          });
        }

        // Phase 2: AI scan GCN candidates OF THIS FOLDER
        if (gcnCandidates.length > 0) {
          setCurrentPhase('scanning');
          console.log(`   🤖 AI scanning ${gcnCandidates.length} GCN candidates...`);
          setProgress({ current: 0, total: gcnCandidates.length });

          for (let i = 0; i < gcnCandidates.length; i++) {
            if (stopRef.current) break;

            const filePath = gcnCandidates[i];
            const fileName = filePath.split(/[/\\]/).pop();

            setProgress({ current: i + 1, total: gcnCandidates.length });
            setCurrentFile(fileName);
            console.log(`      [${i + 1}/${gcnCandidates.length}] Scanning: ${fileName}`);

            try {
              const result = await window.electronAPI.processDocumentOffline(filePath);
              
              let previewUrl = null;
              try {
                if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(fileName)) {
                  previewUrl = await window.electronAPI.readImageDataUrl(filePath);
                }
              } catch (e) {
                console.warn('Failed to load preview:', fileName);
              }

              let newShortCode = 'GTLQ';
              let newDocType = 'Giấy tờ liên quan';
              
              const shortCode = result.short_code || result.classification || '';
              if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
                newShortCode = shortCode;
                newDocType = shortCode === 'GCNC' ? 'Giấy chứng nhận (Chung)' : 
                             shortCode === 'GCNM' ? 'Giấy chứng nhận (Mẫu)' : 
                             'Giấy chứng nhận';
              }

              allResults.push({
                fileName,
                filePath,
                folderName,
                previewUrl,
                originalShortCode: shortCode,
                originalDocType: result.doc_type || shortCode,
                newShortCode,
                newDocType,
                confidence: result.confidence || 0,
                reasoning: result.reasoning || '',
                metadata: result.metadata || {},
                success: true,
                preFiltered: false
              });

            } catch (err) {
              console.error(`Error processing ${fileName}:`, err);
              allResults.push({
                fileName,
                filePath,
                folderName,
                previewUrl: null,
                originalShortCode: 'ERROR',
                originalDocType: 'Lỗi',
                newShortCode: 'GTLQ',
                newDocType: 'Giấy tờ liên quan',
                confidence: 0,
                reasoning: `Lỗi: ${err.message}`,
                metadata: {},
                success: false,
                preFiltered: false
              });
            }

            setResults([...allResults]);
          }
        }

        console.log(`   ✅ Folder ${folderName} complete!`);
      }

      // Sort results to maintain original file order
      allResults.sort((a, b) => {
        const aIndex = files.indexOf(a.filePath);
        const bIndex = files.indexOf(b.filePath);
        return aIndex - bIndex;
      });

      setResults(allResults);
      setCurrentPhase('complete');
      setCurrentFile('');
      setCurrentFolder('');
      console.log('\n✅ All folders complete!');
      
      const finalGcnCount = allResults.filter(r => r.newShortCode !== 'GTLQ').length;
      const finalGtlqCount = allResults.filter(r => r.newShortCode === 'GTLQ').length;
      console.log(`📊 Final stats: ${finalGcnCount} GCN, ${finalGtlqCount} GTLQ`);
    } catch (err) {
      console.error('Scan error:', err);
      alert('Lỗi quét: ' + err.message);
      setCurrentPhase('');
    } finally {
      setIsScanning(false);
    }
  };

  // Stop scanning
  const handleStop = () => {
    stopRef.current = true;
  };

  // Merge PDFs
  const handleMerge = async () => {
    if (results.length === 0) {
      alert('Chưa có kết quả nào để gộp!');
      return;
    }

    try {
      // Prepare merge data - keep original order
      const mergeData = results.map(r => ({
        filePath: r.filePath,
        short_code: r.newShortCode,
        doc_type: r.newDocType
      }));

      console.log('📦 Merging PDFs with GCN filter...');
      console.log(`   Total files: ${mergeData.length}`);
      console.log(`   GCN files: ${mergeData.filter(f => f.short_code !== 'GTLQ').length}`);
      console.log(`   GTLQ files: ${mergeData.filter(f => f.short_code === 'GTLQ').length}`);

      const result = await window.electronAPI.mergeFolderPdfs(mergeData);

      if (result.success) {
        alert(`✅ Gộp PDF thành công!\n\nĐã tạo:\n${result.files.map(f => `- ${f}`).join('\n')}`);
      } else {
        alert('❌ Gộp PDF thất bại: ' + (result.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Merge error:', err);
      alert('Lỗi gộp PDF: ' + err.message);
    }
  };

  const gcnCount = results.filter(r => r.newShortCode !== 'GTLQ').length;
  const gtlqCount = results.filter(r => r.newShortCode === 'GTLQ').length;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📋 Only GCN - Chế độ đặc biệt
        </h1>
        <p className="text-gray-600">
          Quét và phân loại: GCN A3 → Đặt tên GCN | File khác → Đặt tên GTLQ (giữ nguyên thứ tự)
        </p>
      </div>

      {/* Mode Selection */}
      <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => {
              setScanMode('folder');
              setFiles([]);
              setResults([]);
              setTxtFilePath('');
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              scanMode === 'folder'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            📁 Quét thư mục
          </button>
          <button
            onClick={() => {
              setScanMode('batch');
              setFiles([]);
              setResults([]);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              scanMode === 'batch'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            📋 Quét theo danh sách
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          {scanMode === 'folder' 
            ? '💡 Quét tất cả file trong 1 thư mục' 
            : '💡 Quét nhiều thư mục từ file .txt (mỗi dòng 1 đường dẫn)'}
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div className="flex flex-wrap gap-3 items-center">
          {scanMode === 'folder' ? (
            <button
              onClick={handleSelectFolder}
              disabled={isScanning}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              📁 Chọn thư mục
            </button>
          ) : (
            <>
              <button
                onClick={handleSelectTxtFile}
                disabled={isScanning || isLoadingFolders}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📄 Chọn file .txt
              </button>
              {txtFilePath && (
                <>
                  <span className="text-sm text-gray-600">
                    {txtFilePath.split(/[/\\]/).pop()}
                  </span>
                  <button
                    onClick={handleLoadFolders}
                    disabled={isScanning || isLoadingFolders || !txtFilePath}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoadingFolders ? '⏳ Đang tìm...' : '🔍 Tìm kiếm thư mục'}
                  </button>
                </>
              )}
            </>
          )}

          <button
            onClick={handleStartScan}
            disabled={files.length === 0 || isScanning}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? '⏳ Đang quét...' : '▶️ Bắt đầu quét'}
          </button>

          {isScanning && (
            <button
              onClick={handleStop}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow-sm transition-colors"
            >
              ⏹️ Dừng
            </button>
          )}

          {results.length > 0 && !isScanning && (
            <button
              onClick={handleMerge}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium shadow-sm transition-colors"
            >
              📚 Gộp PDF (giữ nguyên thứ tự)
            </button>
          )}

          <div className="ml-auto text-sm text-gray-600">
            <span className="font-medium">Engine:</span> {ocrEngine}
          </div>
        </div>
      </div>

      {/* Progress - Detailed */}
      {isScanning && (
        <div className="mb-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-5 shadow-sm">
          {/* Folder Progress */}
          {folderProgress.total > 0 && (
            <div className="mb-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-purple-700 font-semibold">📁 Thư mục:</span>
                  <span className="text-purple-900 font-bold">{folderProgress.current} / {folderProgress.total}</span>
                </div>
                {currentFolder && (
                  <span className="text-sm text-purple-700 font-medium">{currentFolder}</span>
                )}
              </div>
              <div className="mt-2 w-full bg-purple-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${(folderProgress.current / folderProgress.total) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Phase indicator */}
          <div className="mb-4">
            <div className="flex items-center space-x-3">
              {currentPhase === 'prefilter' && (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-lg font-bold text-blue-900">🎨 Phase 1: Pre-filter (Lọc màu sắc)</span>
                </>
              )}
              {currentPhase === 'scanning' && (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
                  <span className="text-lg font-bold text-green-900">🤖 Phase 2: AI Scanning</span>
                </>
              )}
              {currentPhase === 'complete' && (
                <>
                  <span className="text-2xl">✅</span>
                  <span className="text-lg font-bold text-green-900">Hoàn thành!</span>
                </>
              )}
            </div>
          </div>

          {/* Phase 1 Stats */}
          {(currentPhase === 'prefilter' || currentPhase === 'scanning') && (
            <div className="mb-3 p-3 bg-white rounded-lg border border-blue-200">
              <div className="text-sm font-medium text-gray-700 mb-2">📊 Phase 1 - Kết quả lọc màu:</div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center">
                  <span className="text-green-600 font-semibold">🟢 GCN candidates:</span>
                  <span className="ml-2 font-bold text-green-700">{phaseStats.passed} files</span>
                </div>
                <div className="flex items-center">
                  <span className="text-gray-600 font-semibold">⏭️  Skipped:</span>
                  <span className="ml-2 font-bold text-gray-700">{phaseStats.skipped} files</span>
                </div>
              </div>
            </div>
          )}

          {/* Phase 2 Progress */}
          {currentPhase === 'scanning' && (
            <>
              <div className="mb-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-700">
                    🔍 Đang quét AI: {progress.current} / {progress.total}
                  </span>
                  <span className="text-sm font-bold text-green-700">
                    {progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-500 to-emerald-600 h-3 rounded-full transition-all duration-300 shadow-sm"
                    style={{ width: `${progress.total > 0 ? (progress.current / progress.total) * 100 : 0}%` }}
                  />
                </div>
              </div>

              {/* Current file */}
              {currentFile && (
                <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                  <span className="text-yellow-800 font-medium">📄 File hiện tại:</span>
                  <span className="ml-2 text-yellow-900 font-mono text-xs">{currentFile}</span>
                </div>
              )}

              {/* Time estimate */}
              {progress.current > 0 && progress.total > 0 && (
                <div className="mt-2 text-xs text-gray-600">
                  ⏱️ Ước tính: ~{Math.ceil((progress.total - progress.current) * 15)} giây còn lại
                </div>
              )}
            </>
          )}

          {/* Summary */}
          {currentPhase === 'complete' && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-sm font-medium text-green-800">
                🎉 Đã quét xong {progress.total} files!
              </div>
            </div>
          )}
        </div>
      )}

      {/* Folder List */}
      {folderList.length > 0 && files.length > 0 && !isScanning && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="font-semibold text-blue-900 mb-2">
            📁 {folderList.length} thư mục - {files.length} files
          </div>
          <div className="text-sm text-blue-700 max-h-32 overflow-y-auto">
            {folderList.map((folder, idx) => (
              <div key={idx} className="py-1">
                {idx + 1}. {folder.name} ({folder.path})
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      {results.length > 0 && (
        <div className="mb-4 grid grid-cols-3 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-gray-900">{results.length}</div>
            <div className="text-sm text-gray-600">Tổng số file</div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{gcnCount}</div>
            <div className="text-sm text-green-700">File GCN A3</div>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="text-2xl font-bold text-gray-600">{gtlqCount}</div>
            <div className="text-sm text-gray-700">File GTLQ</div>
          </div>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    #
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Thư mục
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Phân loại gốc
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    → Tên mới
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Preview
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.map((result, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3 text-sm text-gray-900">{idx + 1}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{result.folderName || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{result.fileName}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        result.originalShortCode === 'GCNC' || result.originalShortCode === 'GCNM' || result.originalShortCode === 'GCN'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {result.originalShortCode}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        result.newShortCode !== 'GTLQ'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {result.newShortCode}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {result.previewUrl && (
                        <img
                          src={result.previewUrl}
                          alt={result.fileName}
                          className="w-16 h-20 object-cover rounded border border-gray-300"
                        />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {files.length === 0 && !isScanning && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">
            {scanMode === 'folder' ? '📁' : '📋'}
          </div>
          <div className="text-xl font-medium text-gray-900 mb-2">
            {scanMode === 'folder' ? 'Chưa chọn thư mục' : 'Chưa chọn file .txt'}
          </div>
          <div className="text-gray-600">
            {scanMode === 'folder' 
              ? 'Nhấn "Chọn thư mục" để bắt đầu'
              : 'Nhấn "Chọn file .txt" để bắt đầu'}
          </div>
        </div>
      )}
    </div>
  );
}

export default OnlyGCNScanner;
