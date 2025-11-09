import React, { useState, useEffect } from 'react';

function BatchScanner() {
  // State
  const [txtFilePath, setTxtFilePath] = useState(null);
  const [ocrEngine, setOcrEngine] = useState('tesseract');
  const [outputOption, setOutputOption] = useState('same_folder');
  const [mergeSuffix, setMergeSuffix] = useState('_merged');
  const [outputFolder, setOutputFolder] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [currentFolder, setCurrentFolder] = useState('');
  const [scanResults, setScanResults] = useState(null); // Scan statistics
  const [fileResults, setFileResults] = useState([]); // Individual file results with preview
  const [errors, setErrors] = useState([]);
  const [skippedFolders, setSkippedFolders] = useState([]);
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeInProgress, setMergeInProgress] = useState(false);
  const [density, setDensity] = useState('medium');

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
  }, []);

  // Handle TXT file selection
  const handleSelectTxtFile = async () => {
    try {
      const filePath = await window.electronAPI.selectTxtFile();
      if (filePath) {
        setTxtFilePath(filePath);
        // Reset results when new file is selected
        setResults(null);
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

  // Handle batch scan start
  const handleStartScan = async () => {
    if (!txtFilePath) {
      alert('Vui lòng chọn file TXT trước!');
      return;
    }

    if (outputOption === 'custom_folder' && !outputFolder) {
      alert('Vui lòng chọn thư mục đích!');
      return;
    }
    
    if (outputOption === 'new_folder' && !mergeSuffix) {
      alert('Vui lòng nhập suffix cho thư mục mới!');
      return;
    }

    setIsProcessing(true);
    setProgress({ current: 0, total: 0 });
    setCurrentFolder('');
    setScanResults(null);
    setFileResults([]);
    setErrors([]);
    setSkippedFolders([]);

    try {
      console.log('🚀 Starting batch scan...');
      console.log('📄 TXT file:', txtFilePath);
      console.log('🔧 OCR Engine:', ocrEngine);
      console.log('📤 Output Option:', outputOption);
      console.log('📝 Merge Suffix:', mergeSuffix);
      console.log('📁 Output Folder:', outputFolder);

      const result = await window.electronAPI.processBatchScan(
        txtFilePath,
        outputOption,
        mergeSuffix,
        outputFolder
      );

      console.log('✅ Batch scan result:', result);

      if (result.success) {
        setResults(result);
        setSkippedFolders(result.skipped_folders || []);
        setErrors(result.errors || []);
        alert(`✅ Quét hoàn tất!\n\n📊 Thống kê:\n- Thư mục hợp lệ: ${result.valid_folders}/${result.total_folders}\n- Files xử lý: ${result.processed_files}/${result.total_files}\n- PDFs đã tạo: ${result.merged_pdfs_count || 0}\n- Lỗi: ${result.error_count}`);
      } else {
        alert(`❌ Lỗi: ${result.error}`);
      }
    } catch (err) {
      console.error('Batch scan error:', err);
      alert(`❌ Lỗi xử lý: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Get filename from path
  const getFileName = (filePath) => {
    if (!filePath) return '';
    const parts = filePath.split(/[/\\]/);
    return parts[parts.length - 1];
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
              disabled={isProcessing}
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

        {/* Output Option Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            3️⃣ Chọn chế độ output
          </label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="outputOption"
                value="same_folder"
                checked={outputOption === 'same_folder'}
                onChange={(e) => setOutputOption(e.target.value)}
                disabled={isProcessing}
                className="text-blue-600"
              />
              <div>
                <div className="font-medium text-gray-900">Lưu trong thư mục gốc</div>
                <div className="text-xs text-gray-500">Merge ảnh cùng loại thành PDF, lưu trong thư mục gốc (HDCQ.pdf, GCNM.pdf)</div>
              </div>
            </label>

            <label className="flex items-center gap-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="outputOption"
                value="new_folder"
                checked={outputOption === 'new_folder'}
                onChange={(e) => setOutputOption(e.target.value)}
                disabled={isProcessing}
                className="text-blue-600"
              />
              <div>
                <div className="font-medium text-gray-900">Lưu trong thư mục mới (có suffix)</div>
                <div className="text-xs text-gray-500">Tạo thư mục mới bên cạnh với suffix, merge PDF vào đó (Folder1_merged/HDCQ.pdf)</div>
              </div>
            </label>

            <label className="flex items-center gap-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="outputOption"
                value="custom_folder"
                checked={outputOption === 'custom_folder'}
                onChange={(e) => setOutputOption(e.target.value)}
                disabled={isProcessing}
                className="text-blue-600"
              />
              <div>
                <div className="font-medium text-gray-900">Lưu trong thư mục chỉ định</div>
                <div className="text-xs text-gray-500">Merge PDF, lưu trong thư mục chỉ định, tổ chức theo tên thư mục gốc (Output/Folder1/HDCQ.pdf)</div>
              </div>
            </label>
          </div>
        </div>

        {/* Merge Suffix Input (only for new_folder mode) */}
        {outputOption === 'new_folder' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              4️⃣ Nhập suffix cho thư mục mới
            </label>
            <input
              type="text"
              value={mergeSuffix}
              onChange={(e) => setMergeSuffix(e.target.value)}
              disabled={isProcessing}
              placeholder="Ví dụ: _merged, _output, _pdf"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Ví dụ: Folder1 → Folder1{mergeSuffix}
            </p>
          </div>
        )}

        {/* Output Folder Selection (only for custom_folder mode) */}
        {outputOption === 'custom_folder' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              5️⃣ Chọn thư mục đích
            </label>
            <div className="flex items-center gap-3">
              <button
                onClick={handleSelectOutputFolder}
                disabled={isProcessing}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                📁 Chọn thư mục đích
              </button>
              {outputFolder && (
                <span className="text-sm text-gray-600" title={outputFolder}>
                  ✅ {getFileName(outputFolder)}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Start Button */}
        <div className="pt-4 border-t">
          <button
            onClick={handleStartScan}
            disabled={isProcessing || !txtFilePath}
            className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? '⏳ Đang xử lý...' : '🚀 Bắt đầu quét'}
          </button>
        </div>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="font-medium text-blue-900">Đang xử lý batch scan...</span>
          </div>
          <p className="text-sm text-blue-700">
            Vui lòng đợi. Quá trình này có thể mất vài phút tùy thuộc vào số lượng file.
          </p>
        </div>
      )}

      {/* Results Summary */}
      {results && !isProcessing && (
        <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Kết quả</h3>

          {/* Statistics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{results.total_folders}</div>
              <div className="text-sm text-gray-600">Tổng thư mục</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{results.valid_folders}</div>
              <div className="text-sm text-gray-600">Thư mục hợp lệ</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{results.processed_files}/{results.total_files}</div>
              <div className="text-sm text-gray-600">Files xử lý</div>
            </div>
            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-indigo-600">{results.merged_pdfs_count || 0}</div>
              <div className="text-sm text-gray-600">PDFs đã tạo</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{results.error_count}</div>
              <div className="text-sm text-gray-600">Lỗi</div>
            </div>
          </div>

          {/* Merged PDFs List */}
          {results.merged_pdfs && results.merged_pdfs.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-gray-900 mb-3">📚 PDFs đã tạo ({results.merged_pdfs.length})</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {results.merged_pdfs.map((item, idx) => (
                  <div key={idx} className="bg-indigo-50 border border-indigo-200 rounded p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-gray-900">{item.short_code}.pdf</div>
                      <div className="text-xs text-indigo-700">{item.count} ảnh</div>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">{item.path}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

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
          {results.processed_files > 0 && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✅</span>
                <div>
                  <div className="font-semibold text-green-900">Quét hoàn tất!</div>
                  <div className="text-sm text-green-700 mt-1">
                    Đã xử lý thành công {results.processed_files} file từ {results.valid_folders} thư mục.
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
