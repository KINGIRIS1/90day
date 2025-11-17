# Error Handling System - Hướng Dẫn Bảo Trì

## 📋 Tổng Quan

Hệ thống xử lý lỗi tập trung giúp dễ dàng thêm, sửa, và quản lý các loại lỗi API.

**Các file chính:**
- `python/error_handler.py` - Backend error handler (Python)
- `src/utils/errorHandler.js` - Frontend error handler (React)

---

## 🔧 Cách Thêm Lỗi Mới

### 1. Thêm vào Backend (Python)

Mở file `python/error_handler.py`, thêm vào dictionary `ERROR_CONFIGS`:

```python
ERROR_CONFIGS = {
    # ... existing errors ...
    
    "404": {  # Tên lỗi (HTTP status code hoặc custom name)
        "name": "Not Found",  # Tên hiển thị
        "threshold": 1,  # Số lần lỗi liên tiếp trước khi cảnh báo nghiêm trọng
        "retry": False,  # Có retry không?
        "retry_delay": 0,  # Thời gian chờ giữa các retry (seconds)
        "user_message": "API endpoint không tồn tại. Vui lòng cập nhật app.",
        "console_warning": "❌ 404 Not Found - API endpoint không tồn tại",
        "critical": True,  # Có phải critical error không?
        "should_stop": True  # Có nên dừng quét không?
    }
}
```

**Giải thích các field:**
- `name`: Tên lỗi cho developer
- `threshold`: Sau bao nhiêu lần lỗi thì show cảnh báo nghiêm trọng
- `retry`: `True` = tự động retry, `False` = không retry
- `retry_delay`: Base delay giữa các retry (sẽ có exponential backoff)
- `user_message`: Thông báo hiển thị cho người dùng (tiếng Việt)
- `console_warning`: Thông báo log trong console
- `critical`: `True` = lỗi nghiêm trọng, cần cảnh báo rõ ràng
- `should_stop`: `True` = dừng quét ngay, `False` = cho phép tiếp tục

### 2. Thêm vào Frontend (React)

Mở file `src/utils/errorHandler.js`, thêm vào object `ERROR_MESSAGES`:

```javascript
export const ERROR_MESSAGES = {
  // ... existing errors ...
  
  'CRITICAL_404_ERROR': {
    title: '❌ API Không Tồn Tại',
    message: 'API endpoint không tồn tại. Vui lòng cập nhật app.',
    shouldStop: true,
    severity: 'critical'
  }
};
```

**Giải thích các field:**
- `title`: Tiêu đề alert popup
- `message`: Nội dung thông báo
- `shouldStop`: `true` = dừng quét, `false` = cho phép tiếp tục
- `severity`: `'critical'`, `'error'`, `'warning'`, `'info'` (quyết định màu sắc)

---

## 📝 Ví Dụ: Thêm Lỗi "Request Too Large"

### Backend (Python)

```python
"413": {
    "name": "Request Too Large",
    "threshold": 1,
    "retry": False,
    "user_message": "File quá lớn. Vui lòng giảm batch size xuống 2-3 files.",
    "console_warning": "❌ 413 Request Too Large - Vượt quá giới hạn kích thước",
    "critical": False,
    "should_stop": False
}
```

### Frontend (React)

```javascript
'CRITICAL_413_ERROR': {
  title: '⚠️ File Quá Lớn',
  message: 'File quá lớn. Vui lòng giảm batch size xuống 2-3 files.',
  shouldStop: false,
  severity: 'warning'
}
```

---

## 🎯 Các Lỗi Hiện Tại

| Error Code | Tên | Threshold | Retry | Stop | Mô tả |
|------------|-----|-----------|-------|------|-------|
| 503 | Service Unavailable | 3 | ✅ | ✅ | Server quá tải |
| 500 | Internal Server Error | 3 | ✅ | ✅ | Lỗi server |
| 429 | Rate Limit | 2 | ✅ | ❌ | Vượt giới hạn API |
| 403 | Forbidden | 1 | ❌ | ✅ | API key không hợp lệ |
| 401 | Unauthorized | 1 | ❌ | ✅ | API key sai |
| 400 | Bad Request | 1 | ❌ | ❌ | Request không hợp lệ |
| network | Network Error | 3 | ✅ | ❌ | Lỗi mạng |
| timeout | Timeout | 2 | ✅ | ❌ | Request quá lâu |

---

## 🔄 Workflow Xử Lý Lỗi

```
API Call
   ↓
Error xảy ra
   ↓
error_handler.handle_error()
   ↓
Increment counter
   ↓
Check threshold
   ↓
   ├─→ < threshold: Retry (nếu retry=True)
   ├─→ >= threshold: Show warning
   └─→ >= threshold + critical: Stop & Alert
```

---

## 🧪 Testing Error Handler

### Test Backend

```bash
cd /app/desktop-app/python
python3 -c "
from error_handler import handle_error, handle_success

# Test 503 error
for i in range(4):
    result = handle_error('503')
    print(f'Lần {i+1}:', result)
    
# Test success (reset counter)
handle_success()
print('Counter reset!')
"
```

### Test Frontend

Mở Console trong app:

```javascript
import { handleError, isCriticalError } from './utils/errorHandler';

// Test critical 503 error
const error503 = {
  error: 'CRITICAL_503_ERROR',
  error_message: 'Test message',
  should_stop: true
};

handleError('TestComponent', error503, () => console.log('Stopped!'));
```

---

## 📊 Monitoring

### Xem log errors

```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log | grep "🚨"

# Frontend logs
# Mở DevTools Console trong app
```

### Reset error counters

Error counters tự động reset khi:
- API call thành công
- Restart app

---

## 🚀 Best Practices

1. **Luôn có thông báo tiếng Việt**: Người dùng cần hiểu rõ lỗi
2. **Threshold hợp lý**: 
   - Auth errors (401, 403): threshold = 1 (fail ngay)
   - Server errors (500, 503): threshold = 3 (retry vài lần)
3. **Retry delay phù hợp**:
   - Network errors: 10s
   - Rate limit: 60s (hoặc theo header Retry-After)
4. **Should stop khi cần**:
   - Auth errors: dừng ngay (không có ý nghĩa retry)
   - Server errors: dừng sau nhiều lần thất bại
   - Rate limit: cho phép tiếp tục (sau khi wait)

---

## 🔧 Troubleshooting

### Lỗi không được handle

**Triệu chứng**: App crash hoặc không hiển thị thông báo lỗi

**Giải pháp**:
1. Kiểm tra `ERROR_HANDLER_AVAILABLE` trong batch_processor.py
2. Kiểm tra import error_handler trong các component
3. Xem log để tìm error type

### Thông báo không đúng

**Triệu chứng**: Thông báo lỗi không match với lỗi thực tế

**Giải pháp**:
1. Check error type trong ERROR_CONFIGS (backend) và ERROR_MESSAGES (frontend)
2. Đảm bảo naming convention: `CRITICAL_{error_type}_ERROR`
3. Rebuild frontend: `yarn build`

---

## 📚 Tài Liệu Liên Quan

- [Python Requests Documentation](https://requests.readthedocs.io/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Gemini API Error Codes](https://ai.google.dev/api/rest/v1beta/troubleshooting)

---

## ✅ Checklist Khi Thêm Lỗi Mới

- [ ] Thêm vào `ERROR_CONFIGS` (backend)
- [ ] Thêm vào `ERROR_MESSAGES` (frontend)
- [ ] Test với mock error
- [ ] Verify thông báo tiếng Việt
- [ ] Verify retry logic (nếu có)
- [ ] Verify should_stop behavior
- [ ] Update bảng "Các Lỗi Hiện Tại" trong file này
- [ ] Rebuild frontend

---

**Cập nhật lần cuối**: 2024-11-17
**Version**: 1.0
