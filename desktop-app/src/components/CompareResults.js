import React, { useState } from 'react';

const CompareResults = ({ offlineResult, cloudResult, fileName }) => {
  const [showComparison, setShowComparison] = useState(true);

  if (!offlineResult || !cloudResult) return null;
  if (!showComparison) return null;

  const getConfidenceDiff = () => {
    const diff = (cloudResult.confidence - offlineResult.confidence) * 100;
    return diff.toFixed(1);
  };

  const isSameType = offlineResult.short_code === cloudResult.short_code;

  return (
    <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg relative">
      <button
        onClick={() => setShowComparison(false)}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
      >
        ✕
      </button>

      <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
        <span className="text-xl mr-2">⚖️</span>
        So sánh kết quả: {fileName}
      </h4>

      <div className="grid grid-cols-2 gap-4">
        {/* Offline Result */}
        <div className="bg-white p-3 rounded border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-2xl">🔵</span>
            <div>
              <div className="font-semibold text-sm">Offline OCR</div>
              <div className="text-xs text-gray-500">FREE, Nhanh</div>
            </div>
          </div>
          <div className="space-y-1 text-sm">
            <div>
              <span className="text-gray-600">Loại:</span>
              <p className="font-medium">{offlineResult.short_code}</p>
            </div>
            <div>
              <span className="text-gray-600">Độ tin cậy:</span>
              <p className="font-medium">{(offlineResult.confidence * 100).toFixed(0)}%</p>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {offlineResult.accuracy_estimate}
            </div>
            
            {/* OCR Text Debug */}
            {offlineResult.original_text && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-blue-600 hover:underline">
                  🔍 Xem text OCR
                </summary>
                <div className="mt-1 p-2 bg-gray-50 border rounded text-xs max-h-24 overflow-y-auto">
                  {offlineResult.original_text}
                </div>
              </details>
            )}
          </div>
        </div>

        {/* Cloud Boost Result */}
        <div className="bg-white p-3 rounded border border-purple-200">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-2xl">☁️</span>
            <div>
              <div className="font-semibold text-sm">Cloud Boost</div>
              <div className="text-xs text-gray-500">GPT-4, Chính xác</div>
            </div>
          </div>
          <div className="space-y-1 text-sm">
            <div>
              <span className="text-gray-600">Loại:</span>
              <p className="font-medium">{cloudResult.short_code}</p>
            </div>
            <div>
              <span className="text-gray-600">Độ tin cậy:</span>
              <p className="font-medium">{(cloudResult.confidence * 100).toFixed(0)}%</p>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {cloudResult.accuracy_estimate}
            </div>
            
            {/* GPT Analysis Debug */}
            {cloudResult.reasoning && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-purple-600 hover:underline">
                  💡 Phân tích GPT-4
                </summary>
                <div className="mt-1 p-2 bg-gray-50 border rounded text-xs max-h-24 overflow-y-auto">
                  {cloudResult.reasoning}
                </div>
              </details>
            )}
          </div>
        </div>
      </div>

      {/* Analysis */}
      <div className="mt-3 p-3 bg-white rounded border">
        <div className="text-sm">
          {isSameType ? (
            <div className="flex items-start space-x-2">
              <span className="text-green-600 text-xl">✓</span>
              <div>
                <p className="font-semibold text-green-700">Kết quả khớp nhau</p>
                <p className="text-gray-600 text-xs mt-1">
                  Cả 2 phương pháp đều nhận diện là <strong>{offlineResult.short_code}</strong>.
                  Cloud Boost tăng độ tin cậy thêm <strong>{getConfidenceDiff()}%</strong>.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-start space-x-2">
              <span className="text-orange-600 text-xl">⚠</span>
              <div>
                <p className="font-semibold text-orange-700">Kết quả khác nhau</p>
                <p className="text-gray-600 text-xs mt-1">
                  Offline: <strong>{offlineResult.short_code}</strong> ({(offlineResult.confidence * 100).toFixed(0)}%)
                  {' → '}
                  Cloud: <strong>{cloudResult.short_code}</strong> ({(cloudResult.confidence * 100).toFixed(0)}%)
                </p>
                <p className="text-purple-700 font-medium text-xs mt-2">
                  💡 Cloud Boost có độ chính xác cao hơn (93%+)
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Cost Info */}
      <div className="mt-2 text-xs text-gray-500 text-center">
        Offline: $0.00 | Cloud Boost: ~$0.01-0.02/ảnh
      </div>
    </div>
  );
};

export default CompareResults;
