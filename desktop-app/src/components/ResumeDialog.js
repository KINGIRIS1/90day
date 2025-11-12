import React, { useState } from 'react';

function ResumeDialog({ scans, onResume, onDismiss }) {
  const [previewMode, setPreviewMode] = useState('gcn-only'); // 'none', 'gcn-only', 'all'
  
  if (!scans || scans.length === 0) return null;

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${Math.floor(diffHours / 24)} ngày trước`;
  };

  const getScanTypeLabel = (type) => {
    const labels = {
      'file_scan': '📄 File Scan',
      'folder_scan': '📁 Folder Scan',
      'batch_scan': '📋 Batch Scan'
    };
    return labels[type] || type;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-3xl">🔄</span>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Tiếp Tục Scan?</h2>
            <p className="text-sm text-gray-600">Phát hiện scan chưa hoàn thành từ lần trước</p>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {scans.map((scan) => (
            <div 
              key={scan.scanId}
              className="border-2 border-blue-300 rounded-xl p-4 bg-blue-50 hover:bg-blue-100 transition"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 flex items-center gap-2">
                    {getScanTypeLabel(scan.type)}
                    <span className="text-xs bg-orange-500 text-white px-2 py-1 rounded">Chưa xong</span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {formatTime(scan.timestamp)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                <div className="bg-white rounded p-2">
                  <div className="text-gray-600">Tiến độ</div>
                  <div className="font-bold text-blue-600">
                    {scan.progress?.current || 0} / {scan.progress?.total || 0}
                  </div>
                </div>
                <div className="bg-white rounded p-2">
                  <div className="text-gray-600">Files đã scan</div>
                  <div className="font-bold text-green-600">
                    {scan.results?.length || 0} files
                  </div>
                </div>
              </div>

              {scan.currentFolder && (
                <div className="text-xs text-gray-600 bg-white rounded p-2 truncate" title={scan.currentFolder}>
                  📁 {scan.currentFolder}
                </div>
              )}

              {/* Preview Loading Options */}
              <div className="mt-3 mb-3 bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs font-semibold text-gray-700 mb-2">🖼️ Hiển thị ảnh preview:</div>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                    <input
                      type="radio"
                      name={`preview-${scan.scanId}`}
                      value="none"
                      checked={previewMode === 'none'}
                      onChange={(e) => setPreviewMode(e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div>
                      <div className="text-sm font-medium text-gray-900">🚀 Không load ảnh</div>
                      <div className="text-xs text-gray-600">Nhanh nhất, tiết kiệm RAM tối đa</div>
                    </div>
                  </label>
                  
                  <label className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded border-2 border-green-300 bg-green-50">
                    <input
                      type="radio"
                      name={`preview-${scan.scanId}`}
                      value="gcn-only"
                      checked={previewMode === 'gcn-only'}
                      onChange={(e) => setPreviewMode(e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div>
                      <div className="text-sm font-medium text-green-900">
                        ⭐ Chỉ load ảnh GCN <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">Khuyến nghị</span>
                      </div>
                      <div className="text-xs text-green-700">Cân bằng - chỉ load tài liệu quan trọng</div>
                    </div>
                  </label>
                  
                  <label className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                    <input
                      type="radio"
                      name={`preview-${scan.scanId}`}
                      value="all"
                      checked={previewMode === 'all'}
                      onChange={(e) => setPreviewMode(e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div>
                      <div className="text-sm font-medium text-gray-900">📸 Load tất cả ảnh</div>
                      <div className="text-xs text-gray-600">Đầy đủ nhất (có thể chậm nếu nhiều ảnh)</div>
                    </div>
                  </label>
                </div>
              </div>

              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => onResume(scan, previewMode)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  ▶️ Tiếp Tục Scan
                </button>
                <button
                  onClick={() => onDismiss(scan.scanId)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                >
                  🗑️ Xóa
                </button>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={() => onDismiss('all')}
          className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition font-medium"
        >
          ❌ Bỏ Qua Tất Cả & Bắt Đầu Mới
        </button>

        <div className="mt-4 text-xs text-gray-500 bg-yellow-50 border border-yellow-200 rounded p-3">
          💡 <strong>Lưu ý:</strong> Scan history tự động xóa sau 7 ngày. Tiếp tục scan sẽ load lại kết quả đã quét và chỉ scan files còn lại.
        </div>
      </div>
    </div>
  );
}

export default ResumeDialog;
