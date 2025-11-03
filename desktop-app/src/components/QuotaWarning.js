import React from 'react';

function QuotaWarning({ error }) {
  if (!error || !error.includes('QUÁ GIỚI HẠN')) return null;

  const isRateLimit = error.includes('Rate Limit');
  const isQuotaExhausted = error.includes('hết quota') || error.includes('RESOURCE_EXHAUSTED');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">⚠️</span>
            <div>
              <h2 className="text-2xl font-bold text-red-600">
                {isRateLimit ? 'Rate Limit Exceeded' : 'Hết Quota Free Tier'}
              </h2>
              <p className="text-gray-600">Gemini API đã vượt quá giới hạn</p>
            </div>
          </div>

          {/* Error Details */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-red-800 whitespace-pre-wrap">{error}</p>
          </div>

          {/* Solutions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <span>💡</span> Giải pháp khắc phục:
            </h3>

            {isRateLimit ? (
              // Rate Limit Solutions
              <div className="space-y-3">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">🕐 Đợi và thử lại</h4>
                  <p className="text-sm text-gray-700">
                    Gemini có giới hạn requests per minute (RPM). Đợi 1-2 phút rồi thử lại.
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">📉 Giảm tốc độ scan</h4>
                  <p className="text-sm text-gray-700">
                    • Scan từng trang thay vì batch<br/>
                    • Đợi 1-2 giây giữa mỗi lần scan<br/>
                    • Tránh scan quá nhiều trang cùng lúc
                  </p>
                </div>
              </div>
            ) : (
              // Quota Exhausted Solutions
              <div className="space-y-3">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">⏰ Đợi đến ngày mai</h4>
                  <p className="text-sm text-gray-700">
                    Free tier: <strong>1,500 requests/ngày</strong><br/>
                    Quota reset vào <strong>0:00 AM UTC</strong> (7:00 AM Việt Nam)
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">💳 Upgrade lên Paid Tier</h4>
                  <p className="text-sm text-gray-700 mb-2">
                    Không giới hạn requests với chi phí rất thấp:
                  </p>
                  <ul className="text-sm space-y-1 ml-4">
                    <li>• Flash Lite: ~$0.89/1,000 trang</li>
                    <li>• Flash: ~$4.10/1,000 trang</li>
                  </ul>
                  <a
                    href="https://aistudio.google.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                  >
                    🔗 Mở Google AI Studio
                  </a>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">🆕 Tạo API key mới</h4>
                  <p className="text-sm text-gray-700">
                    Tạo Gmail mới → Tạo API key mới → 1,500 requests miễn phí nữa!
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">⚡ Dùng OCR Offline tạm thời</h4>
                  <p className="text-sm text-gray-700 mb-2">
                    Chuyển sang OCR offline trong Settings:
                  </p>
                  <ul className="text-sm space-y-1 ml-4">
                    <li>• <strong>VietOCR</strong>: 90-95% accuracy (tốt nhất)</li>
                    <li>• <strong>EasyOCR</strong>: 88-92% accuracy</li>
                    <li>• <strong>Tesseract</strong>: 75-85% accuracy</li>
                    <li>• 🎉 <strong>Hoàn toàn miễn phí, không giới hạn!</strong></li>
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Quota Info */}
          <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold mb-2">📊 Thông tin Quota</h4>
            <div className="text-sm space-y-1">
              <p>• <strong>Free Tier:</strong> 1,500 requests/ngày</p>
              <p>• <strong>Rate Limit:</strong> ~60 requests/phút (RPM)</p>
              <p>• <strong>Reset:</strong> Hàng ngày vào 0:00 UTC</p>
              <p>• <strong>Check quota:</strong> <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google AI Studio → Usage</a></p>
            </div>
          </div>

          {/* Close Button */}
          <div className="mt-6 flex justify-end">
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition font-medium"
            >
              Đã hiểu
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuotaWarning;
