import React from 'react';

/**
 * Reusable action button group for all scan modes
 * Includes: Next/Back tabs, Merge folder, Load preview
 */
const ActionButtonGroup = ({
  // Navigation
  onNext,
  onBack,
  hasNext = false,
  hasBack = false,
  
  // Merge
  onMerge,
  showMerge = false,
  mergeLabel = "📚 Gộp thư mục này",
  
  // Load preview
  onLoadPreview,
  showLoadPreview = false,
  
  // Rescan
  onRescan,
  showRescan = false,
  
  // Additional buttons
  children,
  
  // Style
  position = "top", // "top" or "bottom"
  className = ""
}) => {
  return (
    <div className={`flex flex-wrap gap-2 items-center ${position === 'bottom' ? 'mt-4' : 'mb-4'} ${className}`}>
      {/* Navigation buttons */}
      {(hasBack || hasNext) && (
        <div className="flex gap-1">
          <button
            onClick={onBack}
            disabled={!hasBack}
            className="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg font-medium shadow-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Tab trước (Ctrl+←)"
          >
            ⏮ Back
          </button>
          <button
            onClick={onNext}
            disabled={!hasNext}
            className="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg font-medium shadow-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Tab sau (Ctrl+→)"
          >
            Next ⏭
          </button>
        </div>
      )}
      
      {/* Merge button */}
      {showMerge && (
        <button
          onClick={onMerge}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors"
          title="Gộp PDF theo loại tài liệu"
        >
          {mergeLabel}
        </button>
      )}
      
      {/* Load preview button */}
      {showLoadPreview && (
        <button
          onClick={onLoadPreview}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors"
          title="Xem trước tất cả file"
        >
          🖼️ Load Preview
        </button>
      )}
      
      {/* Rescan button */}
      {showRescan && (
        <button
          onClick={onRescan}
          className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg font-medium shadow-sm transition-colors"
          title="Quét lại từ đầu"
        >
          🔄 Quét lại
        </button>
      )}
      
      {/* Additional custom buttons */}
      {children}
    </div>
  );
};

export default ActionButtonGroup;
