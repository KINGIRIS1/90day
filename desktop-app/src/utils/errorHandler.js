/**
 * Centralized Error Handler for Frontend
 * Xử lý và hiển thị thông báo lỗi thân thiện cho người dùng
 */

// ============================================================================
// ERROR CONFIGURATION - Dễ dàng thêm/sửa lỗi ở đây
// ============================================================================

export const ERROR_MESSAGES = {
  // Backend errors (từ Python)
  'CRITICAL_503_ERROR': {
    title: '🚨 Server Không Ổn Định',
    message: 'Hiện tại server không ổn định. Đề nghị tạm dừng quét để tránh hỏng Key. Xin cảm ơn.',
    shouldStop: true,
    severity: 'critical'
  },
  'CRITICAL_500_ERROR': {
    title: '🚨 Server Gặp Sự Cố',
    message: 'Server đang gặp sự cố nội bộ. Đề nghị thử lại sau vài phút.',
    shouldStop: true,
    severity: 'critical'
  },
  'CRITICAL_429_ERROR': {
    title: '⚠️ Vượt Quá Giới Hạn',
    message: 'Đã vượt quá giới hạn API request. Vui lòng đợi 1-2 phút rồi thử lại.',
    shouldStop: false,
    severity: 'warning'
  },
  'CRITICAL_403_ERROR': {
    title: '❌ API Key Không Hợp Lệ',
    message: 'API Key không hợp lệ hoặc hết quota. Vui lòng kiểm tra lại API Key trong Settings.',
    shouldStop: true,
    severity: 'critical'
  },
  'CRITICAL_401_ERROR': {
    title: '❌ Xác Thực Thất Bại',
    message: 'API Key không hợp lệ. Vui lòng kiểm tra lại API Key trong Settings.',
    shouldStop: true,
    severity: 'critical'
  },
  'CRITICAL_400_ERROR': {
    title: '⚠️ Request Không Hợp Lệ',
    message: 'Request không hợp lệ. Có thể ảnh đầu vào bị lỗi hoặc quá lớn.',
    shouldStop: false,
    severity: 'warning'
  },
  'CRITICAL_network_ERROR': {
    title: '🌐 Lỗi Kết Nối',
    message: 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối internet.',
    shouldStop: false,
    severity: 'warning'
  },
  'CRITICAL_timeout_ERROR': {
    title: '⏱️ Request Timeout',
    message: 'Request timeout. File có thể quá lớn hoặc mạng chậm. Thử giảm batch size hoặc kiểm tra kết nối.',
    shouldStop: false,
    severity: 'warning'
  }
};

// ============================================================================
// ERROR HANDLER
// ============================================================================

/**
 * Kiểm tra xem error có phải là critical error từ backend không
 * @param {Object} errorResult - Result object từ backend
 * @returns {boolean}
 */
export function isCriticalError(errorResult) {
  if (!errorResult) return false;
  
  // Check for critical error patterns
  const errorType = errorResult.error || '';
  return errorType.startsWith('CRITICAL_') || errorResult.should_stop === true;
}

/**
 * Lấy error message config từ error type
 * @param {string} errorType - Error type từ backend
 * @returns {Object} Error config
 */
export function getErrorConfig(errorType) {
  return ERROR_MESSAGES[errorType] || {
    title: '❌ Lỗi Không Xác Định',
    message: `Đã xảy ra lỗi: ${errorType}. Vui lòng thử lại hoặc liên hệ support.`,
    shouldStop: false,
    severity: 'error'
  };
}

/**
 * Hiển thị error alert cho người dùng
 * @param {Object} errorResult - Result object từ backend
 * @returns {boolean} - true nếu nên dừng quét
 */
export function showErrorAlert(errorResult) {
  if (!errorResult) return false;
  
  const errorType = errorResult.error || 'UNKNOWN';
  const config = getErrorConfig(errorType);
  
  // Use custom message if provided
  const message = errorResult.error_message || config.message;
  const errorCount = errorResult.error_count ? `\n\nSố lần lỗi: ${errorResult.error_count}` : '';
  
  // Build alert message
  const alertMessage = `${config.title}\n\n${message}${errorCount}${
    config.shouldStop ? '\n\nĐã tự động dừng quét.' : ''
  }`;
  
  // Show alert
  alert(alertMessage);
  
  return config.shouldStop || errorResult.should_stop === true;
}

/**
 * Log error to console với format đẹp
 * @param {string} context - Context (e.g., 'BatchScanner', 'DesktopScanner')
 * @param {Object} errorResult - Result object từ backend
 */
export function logError(context, errorResult) {
  const errorType = errorResult?.error || 'UNKNOWN';
  const config = getErrorConfig(errorType);
  
  console.group(`🔴 [${context}] ${config.title}`);
  console.error('Error Type:', errorType);
  console.error('Message:', errorResult?.error_message || config.message);
  console.error('Should Stop:', config.shouldStop);
  console.error('Error Count:', errorResult?.error_count || 'N/A');
  console.error('Full Error:', errorResult);
  console.groupEnd();
}

/**
 * Xử lý error tổng hợp: log + alert + return action
 * @param {string} context - Context
 * @param {Object} errorResult - Result object từ backend
 * @param {Function} setIsScanning - setState function để dừng quét
 * @returns {boolean} - true nếu đã xử lý xong, false nếu cần xử lý thêm
 */
export function handleError(context, errorResult, setIsScanning) {
  if (!isCriticalError(errorResult)) {
    return false; // Not a critical error, let caller handle
  }
  
  // Log error
  logError(context, errorResult);
  
  // Show alert and check if should stop
  const shouldStop = showErrorAlert(errorResult);
  
  // Stop scanning if needed
  if (shouldStop && setIsScanning) {
    setIsScanning(false);
  }
  
  return shouldStop;
}

/**
 * Format error message cho UI display (không phải alert)
 * @param {Object} errorResult - Result object từ backend
 * @returns {string} - HTML-safe error message
 */
export function formatErrorMessage(errorResult) {
  const errorType = errorResult?.error || 'UNKNOWN';
  const config = getErrorConfig(errorType);
  const message = errorResult?.error_message || config.message;
  
  return `${config.title}: ${message}`;
}

// ============================================================================
// UTILITIES
// ============================================================================

/**
 * Get severity color for UI
 * @param {string} errorType 
 * @returns {string} Tailwind color class
 */
export function getSeverityColor(errorType) {
  const config = getErrorConfig(errorType);
  const severityColors = {
    'critical': 'text-red-600 bg-red-50 border-red-200',
    'error': 'text-red-500 bg-red-50 border-red-200',
    'warning': 'text-yellow-600 bg-yellow-50 border-yellow-200',
    'info': 'text-blue-600 bg-blue-50 border-blue-200'
  };
  return severityColors[config.severity] || severityColors['error'];
}

/**
 * Export all for convenience
 */
export default {
  isCriticalError,
  getErrorConfig,
  showErrorAlert,
  logError,
  handleError,
  formatErrorMessage,
  getSeverityColor
};
