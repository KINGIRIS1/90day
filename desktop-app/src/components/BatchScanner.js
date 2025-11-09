import React, { useState, useEffect } from 'react';

const BatchScanner = () => {
  // State
  const [csvFile, setCsvFile] = useState(null);
  const [batchAnalysis, setBatchAnalysis] = useState(null);
  const [outputMode, setOutputMode] = useState('rename'); // 'rename', 'copy_by_type', 'copy_to_folder'
  const [outputFolder, setOutputFolder] = useState('');
  const [processing, setProcessing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, currentFolder: '' });
  const [results, setResults] = useState([]);
  const [logs, setLogs] = useState([]);
  const [pendingItems, setPendingItems] = useState([]); // Items left to process

  // Load saved output mode
  useEffect(() => {
    const loadConfig = async () => {
      const api = window.electronAPI;
      if (!api) return;
      
      const savedMode = await api.getConfig('batchOutputMode');
      if (savedMode) setOutputMode(savedMode);
    };
    loadConfig();
  }, []);

  // Save output mode when changed
  const handleOutputModeChange = async (mode) => {
    setOutputMode(mode);
    const api = window.electronAPI;
    if (api) {
      await api.setConfig('batchOutputMode', mode);
    }
  };

  const handleSelectCsvFile = async () => {
    const api = window.electronAPI;
    if (!api) {
      addLog('❌ Electron API not available', 'error');
      return;
    }

    // Check if analyzeBatchFile API exists
    if (!api.analyzeBatchFile) {
      addLog('❌ analyzeBatchFile API not found. App needs restart.', 'error');
      return;
    }

    try {
      // Use native file input
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.csv,.xlsx,.xls';
      input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
          const filePath = file.path || file.name;
          setCsvFile(filePath);
          addLog(`✅ Đã chọn file: ${filePath}`, 'success');
          
          // In Electron, file.path should always exist
          if (file.path) {
            await analyzeBatch(file.path);
          } else {
            addLog('❌ Không thể đọc đường dẫn file. Vui lòng thử lại.', 'error');
          }
        }
      };
      input.click();
    } catch (error) {
      addLog(`❌ Lỗi chọn file: ${error.message}`, 'error');
    }
  };

  const analyzeBatch = async (filePath) => {
    const api = window.electronAPI;
    if (!api) return;

    addLog('🔍 Đang phân tích file...', 'info');
    setBatchAnalysis(null);

    try {
      const result = await api.analyzeBatchFile(filePath);
      
      if (result.success) {
        setBatchAnalysis(result);
        addLog(`✅ Phân tích hoàn tất: ${result.valid_folders}/${result.total_folders} thư mục hợp lệ, ${result.total_images} ảnh`, 'success');
        
        // Show warnings for invalid folders
        if (result.invalid_folders > 0) {
          result.folders.forEach(folder => {
            if (!folder.valid) {
              addLog(`⚠️ Thư mục không hợp lệ: ${folder.path} - ${folder.error}`, 'warning');
            }
          });
        }
      } else {
        addLog(`❌ Lỗi phân tích: ${result.error}`, 'error');
      }
    } catch (error) {
      addLog(`❌ Lỗi phân tích file: ${error.message}`, 'error');
    }
  };

  const handleSelectOutputFolder = async () => {
    const api = window.electronAPI;
    if (!api) return;

    try {
      const result = await api.selectFolder({
        title: 'Chọn thư mục lưu kết quả'
      });

      if (result.success && result.folderPath) {
        setOutputFolder(result.folderPath);
        addLog(`✅ Thư mục output: ${result.folderPath}`, 'success');
      }
    } catch (error) {
      addLog(`❌ Lỗi chọn thư mục: ${error.message}`, 'error');
    }
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
    if (isPaused) {
      addLog('▶️ Tiếp tục quét...', 'info');
    } else {
      addLog('⏸️ Đã tạm dừng', 'warning');
    }
  };

  const handleStop = () => {
    setProcessing(false);
    setIsPaused(false);
    addLog('⏹️ Đã dừng quét batch', 'warning');
  };

  const handleStartBatchScan = async () => {
    if (!batchAnalysis || batchAnalysis.valid_folders === 0) {
      addLog('❌ Không có thư mục hợp lệ để quét', 'error');
      return;
    }

    if (outputMode === 'copy_to_folder' && !outputFolder) {
      addLog('❌ Vui lòng chọn thư mục đích', 'error');
      return;
    }

    const api = window.electronAPI;
    if (!api) return;

    setProcessing(true);
    setIsPaused(false);
    setResults([]);
    setProgress({ current: 0, total: batchAnalysis.total_images, currentFolder: '' });
    addLog('🚀 Bắt đầu quét batch...', 'info');

    try {
      // Process each valid folder
      let currentImageCount = 0;

      for (const folder of batchAnalysis.folders) {
        if (!processing) break; // Stop if processing was set to false
        
        if (!folder.valid || folder.image_count === 0) {
          continue;
        }

        setProgress(prev => ({ ...prev, currentFolder: folder.path }));
        addLog(`📁 Đang quét: ${folder.path} (${folder.image_count} ảnh)`, 'info');

        // Process images in this folder
        for (let i = 0; i < folder.images.length; i++) {
          // Check if paused
          while (isPaused && processing) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }
          
          // Check if stopped
          if (!processing) break;
          
          const imagePath = folder.images[i];
          currentImageCount++;
          
          setProgress({
            current: currentImageCount,
            total: batchAnalysis.total_images,
            currentFolder: folder.path
          });

          try {
            // Process single image using offline OCR
            const result = await api.processDocumentOffline(imagePath);
            
            if (result.success) {
              const shortCode = result.short_code || 'UNKNOWN';
              let outputPath = imagePath;
              let fileProcessed = false;
              
              // Handle output based on mode
              if (outputMode === 'rename') {
                // Rename in place
                try {
                  const renameResult = await api.renameFile(imagePath, shortCode);
                  if (renameResult.success) {
                    outputPath = renameResult.newPath;
                    fileProcessed = true;
                  }
                } catch (e) {
                  addLog(`⚠️ Không thể đổi tên ${getFileName(imagePath)}: ${e.message}`, 'warning');
                }
              } else if (outputMode === 'copy_by_type' || outputMode === 'copy_to_folder') {
                // For now, just rename in place since we need to implement copy functions
                // TODO: Implement proper copy functionality in Electron IPC
                addLog(`⚠️ Chế độ copy chưa được implement đầy đủ. Tạm thời dùng rename.`, 'warning');
                try {
                  const renameResult = await api.renameFile(imagePath, shortCode);
                  if (renameResult.success) {
                    outputPath = renameResult.newPath;
                    fileProcessed = true;
                  }
                } catch (e) {
                  addLog(`⚠️ Không thể đổi tên ${getFileName(imagePath)}: ${e.message}`, 'warning');
                }
              }

              setResults(prev => [...prev, {
                originalPath: imagePath,
                outputPath,
                shortCode: shortCode,
                confidence: result.confidence || 0,
                success: true,
                processed: fileProcessed
              }]);
              
              if (fileProcessed) {
                addLog(`✅ ${getFileName(imagePath)} → ${shortCode}`, 'success');
              }
            } else {
              addLog(`❌ Lỗi xử lý ${getFileName(imagePath)}: ${result.error || 'Unknown error'}`, 'error');
              setResults(prev => [...prev, {
                originalPath: imagePath,
                error: result.error || 'Unknown error',
                success: false
              }]);
            }
          } catch (error) {
            addLog(`❌ Lỗi xử lý ${getFileName(imagePath)}: ${error.message}`, 'error');
            setResults(prev => [...prev, {
              originalPath: imagePath,
              error: error.message,
              success: false
            }]);
          }
        }

        addLog(`✅ Hoàn thành thư mục: ${folder.path}`, 'success');
      }

      addLog(`🎉 Hoàn thành batch scan! Đã xử lý ${currentImageCount} ảnh`, 'success');
    } catch (error) {
      addLog(`❌ Lỗi batch scan: ${error.message}`, 'error');
    } finally {
      setProcessing(false);
    }
  };

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString('vi-VN');
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const getFileName = (fullPath) => {
    return fullPath.split(/[/\\]/).pop();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">📋 Quét theo danh sách</h2>
        <p className="text-sm text-gray-600 mb-6">
          Upload file CSV hoặc Excel chứa danh sách đường dẫn thư mục để quét hàng loạt
        </p>

        {/* Step 1: Select CSV/Excel File */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Bước 1: Chọn file CSV/Excel</h3>
          <div className="flex items-center gap-3">
            <button
              onClick={handleSelectCsvFile}
              disabled={processing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              📂 Chọn file
            </button>
            {csvFile && (
              <span className="text-sm text-gray-700">
                {csvFile.split(/[/\\]/).pop()}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            File CSV/Excel phải có cột chứa đường dẫn thư mục (ví dụ: "folder_path", "path", "đường dẫn")
          </p>
        </div>

        {/* Batch Analysis Summary */}
        {batchAnalysis && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold mb-2">📊 Phân tích batch</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Tổng thư mục:</p>
                <p className="text-xl font-bold text-gray-900">{batchAnalysis.total_folders}</p>
              </div>
              <div>
                <p className="text-gray-600">Thư mục hợp lệ:</p>
                <p className="text-xl font-bold text-green-600">{batchAnalysis.valid_folders}</p>
              </div>
              <div>
                <p className="text-gray-600">Thư mục lỗi:</p>
                <p className="text-xl font-bold text-red-600">{batchAnalysis.invalid_folders}</p>
              </div>
              <div>
                <p className="text-gray-600">Tổng ảnh:</p>
                <p className="text-xl font-bold text-blue-600">{batchAnalysis.total_images}</p>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Select Output Mode */}
        {batchAnalysis && batchAnalysis.valid_folders > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Bước 2: Chọn chế độ lưu kết quả</h3>
            <div className="space-y-3">
              <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="outputMode"
                  value="rename"
                  checked={outputMode === 'rename'}
                  onChange={(e) => handleOutputModeChange(e.target.value)}
                  disabled={processing}
                  className="mt-1"
                />
                <div>
                  <p className="font-medium">Đổi tên tại chỗ</p>
                  <p className="text-sm text-gray-600">File sẽ được đổi tên ngay tại thư mục gốc</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="outputMode"
                  value="copy_by_type"
                  checked={outputMode === 'copy_by_type'}
                  onChange={(e) => handleOutputModeChange(e.target.value)}
                  disabled={processing}
                  className="mt-1"
                />
                <div>
                  <p className="font-medium">Copy theo loại tài liệu</p>
                  <p className="text-sm text-gray-600">Tạo thư mục con theo loại tài liệu (GCN, HDCQ, ...)</p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="outputMode"
                  value="copy_to_folder"
                  checked={outputMode === 'copy_to_folder'}
                  onChange={(e) => handleOutputModeChange(e.target.value)}
                  disabled={processing}
                  className="mt-1"
                />
                <div className="flex-1">
                  <p className="font-medium">Lưu vào thư mục khác</p>
                  <p className="text-sm text-gray-600 mb-2">Copy tất cả file vào 1 thư mục do bạn chọn</p>
                  {outputMode === 'copy_to_folder' && (
                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={handleSelectOutputFolder}
                        disabled={processing}
                        className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 disabled:opacity-50"
                      >
                        Chọn thư mục
                      </button>
                      {outputFolder && (
                        <span className="text-xs text-gray-600">{outputFolder}</span>
                      )}
                    </div>
                  )}
                </div>
              </label>
            </div>
          </div>
        )}

        {/* Step 3: Start Processing */}
        {batchAnalysis && batchAnalysis.valid_folders > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Bước 3: Bắt đầu quét</h3>
            <div className="flex items-center gap-3">
              <button
                onClick={handleStartBatchScan}
                disabled={processing || (outputMode === 'copy_to_folder' && !outputFolder)}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {processing ? '⏳ Đang xử lý...' : '🚀 Bắt đầu quét batch'}
              </button>
              
              {processing && (
                <>
                  <button
                    onClick={handlePauseResume}
                    className="px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-medium"
                  >
                    {isPaused ? '▶️ Tiếp tục' : '⏸️ Tạm dừng'}
                  </button>
                  <button
                    onClick={handleStop}
                    className="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                  >
                    ⏹️ Dừng
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Progress */}
        {processing && (
          <div className={`mb-6 p-4 rounded-lg border ${isPaused ? 'bg-orange-50 border-orange-200' : 'bg-yellow-50 border-yellow-200'}`}>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">{isPaused ? '⏸️ Đã tạm dừng' : '⏳ Tiến độ'}</h3>
              {isPaused && (
                <span className="text-sm text-orange-600 font-medium">Nhấn "Tiếp tục" để chạy lại</span>
              )}
            </div>
            <div className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span>Đã xử lý: {progress.current} / {progress.total} ảnh</span>
                <span>{Math.round((progress.current / progress.total) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${isPaused ? 'bg-orange-600' : 'bg-green-600'}`}
                  style={{ width: `${(progress.current / progress.total) * 100}%` }}
                />
              </div>
            </div>
            {progress.currentFolder && (
              <p className="text-sm text-gray-600 truncate">
                📁 {progress.currentFolder}
              </p>
            )}
          </div>
        )}

        {/* Logs */}
        <div className="mt-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold">📋 Nhật ký</h3>
            {logs.length > 0 && (
              <button
                onClick={clearLogs}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
              >
                Xóa log
              </button>
            )}
          </div>
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <p className="text-gray-500">Chưa có log...</p>
            ) : (
              logs.map((log, idx) => (
                <div
                  key={idx}
                  className={`mb-1 ${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    'text-gray-300'
                  }`}
                >
                  <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Results Summary */}
        {results.length > 0 && !processing && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="text-lg font-semibold mb-2">✅ Kết quả</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Thành công:</p>
                <p className="text-xl font-bold text-green-600">
                  {results.filter(r => r.success).length}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Lỗi:</p>
                <p className="text-xl font-bold text-red-600">
                  {results.filter(r => !r.success).length}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchScanner;
