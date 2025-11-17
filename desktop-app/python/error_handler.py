#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized Error Handler
Quản lý tập trung các loại lỗi API và thông báo cho người dùng
"""

import sys
import json

# ============================================================================
# ERROR CONFIGURATION - Dễ dàng thêm/sửa lỗi ở đây
# ============================================================================

ERROR_CONFIGS = {
    # HTTP Status Code Errors
    "503": {
        "name": "Service Unavailable",
        "threshold": 3,  # Số lần lỗi liên tiếp trước khi cảnh báo nghiêm trọng
        "retry": True,
        "retry_delay": 10,  # seconds
        "user_message": "Hiện tại server không ổn định. Đề nghị tạm dừng quét để tránh hỏng Key. Xin cảm ơn.",
        "console_warning": "⚠️ 503 Service Unavailable - Server đang quá tải hoặc bảo trì",
        "critical": True,
        "should_stop": True
    },
    "500": {
        "name": "Internal Server Error",
        "threshold": 3,
        "retry": True,
        "retry_delay": 10,
        "user_message": "Server đang gặp sự cố nội bộ. Đề nghị thử lại sau vài phút.",
        "console_warning": "⚠️ 500 Internal Server Error - Lỗi server",
        "critical": True,
        "should_stop": True
    },
    "429": {
        "name": "Rate Limit Exceeded",
        "threshold": 2,
        "retry": True,
        "retry_delay": 60,  # Longer delay for rate limits
        "user_message": "Đã vượt quá giới hạn API request. Vui lòng đợi 1-2 phút rồi thử lại.",
        "console_warning": "⚠️ 429 Rate Limit - Vượt quá giới hạn request",
        "critical": False,
        "should_stop": False
    },
    "403": {
        "name": "Forbidden - Invalid API Key",
        "threshold": 1,  # Don't retry, stop immediately
        "retry": False,
        "user_message": "API Key không hợp lệ hoặc hết quota. Vui lòng kiểm tra lại API Key trong Settings.",
        "console_warning": "❌ 403 Forbidden - API Key không hợp lệ hoặc hết quota",
        "critical": True,
        "should_stop": True
    },
    "401": {
        "name": "Unauthorized - Invalid API Key",
        "threshold": 1,
        "retry": False,
        "user_message": "API Key không hợp lệ. Vui lòng kiểm tra lại API Key trong Settings.",
        "console_warning": "❌ 401 Unauthorized - API Key sai",
        "critical": True,
        "should_stop": True
    },
    "400": {
        "name": "Bad Request",
        "threshold": 1,
        "retry": False,
        "user_message": "Request không hợp lệ. Có thể ảnh đầu vào bị lỗi hoặc quá lớn.",
        "console_warning": "❌ 400 Bad Request - Request không hợp lệ",
        "critical": False,
        "should_stop": False
    },
    "network": {
        "name": "Network Error",
        "threshold": 3,
        "retry": True,
        "retry_delay": 10,
        "user_message": "Không thể kết nối đến server. Vui lòng kiểm tra kết nối internet.",
        "console_warning": "⚠️ Network Error - Lỗi kết nối mạng",
        "critical": False,
        "should_stop": False
    },
    "timeout": {
        "name": "Request Timeout",
        "threshold": 2,
        "retry": True,
        "retry_delay": 15,
        "user_message": "Request timeout. File có thể quá lớn hoặc mạng chậm.",
        "console_warning": "⚠️ Timeout - Request quá lâu",
        "critical": False,
        "should_stop": False
    }
}

# ============================================================================
# ERROR COUNTER - Track số lần lỗi của từng loại
# ============================================================================

_error_counters = {}

def reset_error_counter(error_type):
    """Reset counter cho một loại lỗi cụ thể"""
    global _error_counters
    if error_type in _error_counters:
        _error_counters[error_type] = 0

def reset_all_counters():
    """Reset tất cả counters"""
    global _error_counters
    _error_counters = {}

def increment_error_counter(error_type):
    """Tăng counter cho một loại lỗi"""
    global _error_counters
    if error_type not in _error_counters:
        _error_counters[error_type] = 0
    _error_counters[error_type] += 1
    return _error_counters[error_type]

def get_error_count(error_type):
    """Lấy số lần lỗi hiện tại"""
    return _error_counters.get(error_type, 0)

# ============================================================================
# ERROR HANDLER
# ============================================================================

def handle_error(error_type, error_obj=None, context=None):
    """
    Xử lý lỗi tập trung
    
    Args:
        error_type: Loại lỗi (503, 500, 429, 403, 401, 400, network, timeout)
        error_obj: Exception object (optional)
        context: Thông tin thêm (batch_size, file_name, etc.)
    
    Returns:
        dict: {
            "should_retry": bool,
            "should_stop": bool,
            "wait_time": int (seconds),
            "error_count": int,
            "is_critical": bool,
            "user_message": str,
            "error_response": dict (for frontend)
        }
    """
    error_type = str(error_type)
    
    # Get config
    config = ERROR_CONFIGS.get(error_type)
    if not config:
        # Unknown error - use generic handling
        config = {
            "name": f"Unknown Error ({error_type})",
            "threshold": 1,
            "retry": False,
            "user_message": f"Lỗi không xác định: {error_type}. Vui lòng liên hệ support.",
            "console_warning": f"❌ Unknown Error: {error_type}",
            "critical": False,
            "should_stop": False
        }
    
    # Increment counter
    error_count = increment_error_counter(error_type)
    
    # Calculate wait time (exponential backoff)
    retry_delay = config.get("retry_delay", 10)
    wait_time = retry_delay * (2 ** min(error_count - 1, 3))  # Cap at 2^3
    
    # Check if reached threshold
    is_critical = error_count >= config.get("threshold", 1)
    should_stop = is_critical and config.get("should_stop", False)
    should_retry = config.get("retry", False) and not should_stop
    
    # Print console warning
    print(f"\n{config['console_warning']}", file=sys.stderr)
    print(f"Số lần lỗi liên tiếp: {error_count}/{config.get('threshold', 1)}", file=sys.stderr)
    
    if context:
        print(f"Context: {context}", file=sys.stderr)
    
    if error_obj:
        print(f"Error detail: {error_obj}", file=sys.stderr)
    
    # Print critical warning if threshold reached
    if is_critical and config.get("critical", False):
        print(f"\n{'🚨' * 15}", file=sys.stderr)
        print(f"🚨 CẢNH BÁO NGHIÊM TRỌNG - {config['name']} 🚨", file=sys.stderr)
        print(f"Đã gặp {error_count} lỗi liên tiếp!", file=sys.stderr)
        print(f"{config['user_message']}", file=sys.stderr)
        print(f"{'🚨' * 15}\n", file=sys.stderr)
    
    # Prepare error response for frontend
    error_response = None
    if should_stop:
        error_response = {
            "error": f"CRITICAL_{error_type}_ERROR",
            "error_message": config["user_message"],
            "error_count": error_count,
            "error_type": error_type,
            "should_stop": True
        }
    
    return {
        "should_retry": should_retry,
        "should_stop": should_stop,
        "wait_time": wait_time,
        "error_count": error_count,
        "is_critical": is_critical,
        "user_message": config["user_message"],
        "error_response": error_response
    }

def get_error_type_from_status(status_code):
    """Convert HTTP status code to error type string"""
    return str(status_code)

def print_error_response(error_response):
    """Print error response to stdout for frontend to parse"""
    if error_response:
        print(json.dumps(error_response))

# ============================================================================
# SUCCESS HANDLER
# ============================================================================

def handle_success():
    """Reset all error counters on successful API call"""
    reset_all_counters()

# ============================================================================
# UTILITIES
# ============================================================================

def get_retry_suggestion(error_type):
    """Get user-friendly retry suggestion"""
    config = ERROR_CONFIGS.get(str(error_type))
    if not config:
        return ""
    
    if not config.get("retry", False):
        return "💡 Không nên retry - vui lòng kiểm tra cấu hình hoặc liên hệ support."
    
    wait = config.get("retry_delay", 10)
    return f"💡 Sẽ tự động retry sau {wait}s..."

def get_all_error_types():
    """Get list of all supported error types"""
    return list(ERROR_CONFIGS.keys())
