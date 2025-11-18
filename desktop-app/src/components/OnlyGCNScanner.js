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
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
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
      console.log(`📁 Selected folder: ${imageFiles.length} files`);
    } catch (err) {
      console.error('Error selecting folder:', err);
      alert('Lỗi chọn thư mục: ' + err.message);
    }
  };

  // Start scanning with pre-filter
  const handleStartScan = async () => {
    if (files.length === 0) {
      alert('Vui lòng chọn thư mục trước!');
      return;
    }

    setIsScanning(true);
    setResults([]);
    stopRef.current = false;

    const newResults = [];

    try {
      // Phase 1: Pre-filter by color (fast, free, local)
      console.log('🎨 Phase 1: Pre-filtering by color...');
      const preFilterStart = Date.now();
      
      const preFilterResults = await window.electronAPI.preFilterGCNFiles(files);
      const preFilterTime = ((Date.now() - preFilterStart) / 1000).toFixed(1);
      
      const gcnCandidates = preFilterResults.passed || [];
      const skipped = preFilterResults.skipped || [];
      
      console.log(`✅ Pre-filter complete in ${preFilterTime}s:`);
      console.log(`   🟢 GCN candidates: ${gcnCandidates.length} files`);
      console.log(`   ⏭️  Skipped: ${skipped.length} files`);
      
      // Add skipped files to results as GTLQ without scanning
      for (const filePath of skipped) {
        const fileName = filePath.split(/[/\\]/).pop();
        newResults.push({
          fileName,
          filePath,
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

      // Phase 2: AI scan only GCN candidates
      console.log(`\n🤖 Phase 2: AI scanning ${gcnCandidates.length} GCN candidates...`);
      setProgress({ current: 0, total: gcnCandidates.length });

      for (let i = 0; i < gcnCandidates.length; i++) {
        if (stopRef.current) {
          console.log('⏹️ Scan stopped by user');
          break;
        }

        const filePath = gcnCandidates[i];
        const fileName = filePath.split(/[/\\]/).pop();

        setProgress({ current: i + 1, total: gcnCandidates.length });
        console.log(`[${i + 1}/${gcnCandidates.length}] AI Scanning: ${fileName}`);

        try {
          // Scan file
          const result = await window.electronAPI.processDocumentOffline(filePath);
          
          // Generate preview
          let previewUrl = null;
          try {
            if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(fileName)) {
              previewUrl = await window.electronAPI.readImageDataUrl(filePath);
            }
          } catch (e) {
            console.warn('Failed to load preview:', fileName);
          }

          // Determine new name based on classification
          let newShortCode = 'GTLQ';
          let newDocType = 'Giấy tờ liên quan';
          
          // Check if it's GCN A3 (GCNC or GCNM)
          const shortCode = result.short_code || result.classification || '';
          if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
            newShortCode = shortCode;
            newDocType = shortCode === 'GCNC' ? 'Giấy chứng nhận (Chung)' : 
                         shortCode === 'GCNM' ? 'Giấy chứng nhận (Mẫu)' : 
                         'Giấy chứng nhận';
          }

          newResults.push({
            fileName,
            filePath,
            previewUrl,
            originalShortCode: shortCode,
            originalDocType: result.doc_type || shortCode,
            newShortCode,
            newDocType,
            confidence: result.confidence || 0,
            reasoning: result.reasoning || '',
            metadata: result.metadata || {},
            success: true
          });

        } catch (err) {
          console.error(`Error processing ${fileName}:`, err);
          newResults.push({
            fileName,
            filePath,
            previewUrl: null,
            originalShortCode: 'ERROR',
            originalDocType: 'Lỗi',
            newShortCode: 'GTLQ',
            newDocType: 'Giấy tờ liên quan',
            confidence: 0,
            reasoning: `Lỗi: ${err.message}`,
            metadata: {},
            success: false
          });
        }

        setResults([...newResults]);
      }

      console.log('✅ Scan complete!');
    } catch (err) {
      console.error('Scan error:', err);
      alert('Lỗi quét: ' + err.message);
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

      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div className="flex flex-wrap gap-3 items-center">
          <button
            onClick={handleSelectFolder}
            disabled={isScanning}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            📁 Chọn thư mục
          </button>

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

      {/* Progress */}
      {isScanning && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Đang quét: {progress.current} / {progress.total}
            </span>
            <span className="text-sm text-blue-700">
              {Math.round((progress.current / progress.total) * 100)}%
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${(progress.current / progress.total) * 100}%` }}
            />
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
          <div className="text-6xl mb-4">📁</div>
          <div className="text-xl font-medium text-gray-900 mb-2">
            Chưa chọn thư mục
          </div>
          <div className="text-gray-600">
            Nhấn "Chọn thư mục" để bắt đầu
          </div>
        </div>
      )}
    </div>
  );
}

export default OnlyGCNScanner;
