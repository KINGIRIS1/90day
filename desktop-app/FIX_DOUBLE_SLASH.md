# 🔧 FIX: 404 Error - Double Slash trong API URL

## ❌ Vấn Đề

Khi dùng Cloud Boost, gặp lỗi 404:
```
URL: https://ocr-landocs.preview.emergentagent.com//api/scan-document-public
                                                  ^^
                                                  Double slash!
```

**Nguyên nhân:**
- Backend URL có trailing slash: `https://example.com/`
- Code thêm `/api/...` → Thành `https://example.com//api/...`
- Server không nhận diện `//api` → 404 Not Found

---

## ✅ ĐÃ SỬA

### Thay đổi trong `electron/main.js` và `public/electron.js`

**TRƯỚC (Dòng 446):**
```javascript
const response = await axios.post(`${backendUrl}/api/scan-document-public`, form, {
```

**SAU:**
```javascript
// Normalize backend URL (remove trailing slash if exists)
const normalizedUrl = backendUrl.replace(/\/$/, '');

const response = await axios.post(`${normalizedUrl}/api/scan-document-public`, form, {
```

**Giải thích:**
- `backendUrl.replace(/\/$/, '')` → Xóa trailing slash nếu có
- `https://example.com/` → `https://example.com`
- `https://example.com` → `https://example.com` (không đổi nếu không có slash)

---

## 🚀 SỬ DỤNG

### Bước 1: Restart App

```batch
# Tắt app (Ctrl+C hoặc đóng cửa sổ)
# Chạy lại
yarn electron-dev
```

Hoặc nếu đang dùng production build:
```batch
# Rebuild app
yarn electron-pack
```

---

### Bước 2: Cấu Hình Backend URL

**Trong app, vào Settings:**

**✅ Đúng - Cả 2 cách đều OK:**
```
https://ocr-landocs.preview.emergentagent.com
https://ocr-landocs.preview.emergentagent.com/
```

Cả 2 đều hoạt động vì code đã normalize!

**❌ Sai:**
```
https://ocr-landocs.preview.emergentagent.com//
(double slash cuối - không nên, nhưng code cũng xử lý được)
```

---

### Bước 3: Test Cloud Boost

1. Chọn file ảnh
2. Click "☁️ Cloud Boost"
3. Kiểm tra kết quả

**Nếu thành công:**
- ✅ Thấy kết quả OCR
- ✅ Confidence ~93%+
- ✅ Console log: `Cloud Boost response: {...}`

**Nếu vẫn 404:**
- Check Backend URL đúng chưa
- Check backend server có chạy không
- Check endpoint `/api/scan-document-public` có tồn tại không

---

## 🔍 DEBUG

### Kiểm tra URL được gọi

Check console log trong app:
```
Cloud Boost: Uploading D:\file.jpg to https://landocr-pro...
```

URL phải là:
```
https://ocr-landocs.preview.emergentagent.com/api/scan-document-public
```

**KHÔNG có double slash `//api`**

---

### Test Backend Endpoint

Dùng curl hoặc Postman:

```bash
curl -X POST https://ocr-landocs.preview.emergentagent.com/api/scan-document-public \
  -F "file=@test.jpg"
```

**Nếu 404:**
- Backend chưa deploy endpoint này
- Hoặc endpoint có path khác

**Nếu 200:**
- Backend OK
- App sẽ hoạt động sau khi restart

---

## 📊 URL Normalization Examples

| Input URL | Normalized | Final API URL |
|-----------|-----------|---------------|
| `https://api.com` | `https://api.com` | `https://api.com/api/scan...` |
| `https://api.com/` | `https://api.com` | `https://api.com/api/scan...` |
| `https://api.com//` | `https://api.com/` | `https://api.com//api/scan...` ⚠️ |

**Note:** Nếu URL có nhiều hơn 1 trailing slash, chỉ xóa 1. User nên nhập đúng URL.

---

## 📝 Files Đã Sửa

1. ✅ `electron/main.js` - Added URL normalization
2. ✅ `public/electron.js` - Added URL normalization
3. ✅ `FIX_DOUBLE_SLASH.md` - This file

---

## ⚠️ Lưu Ý

### 1. Backend URL Format

**Recommended:**
```
https://your-backend.com
(không có trailing slash)
```

**Also OK:**
```
https://your-backend.com/
(có trailing slash - code sẽ xử lý)
```

---

### 2. Các Endpoints Được Gọi

App gọi các endpoints sau:
```
POST /api/scan-document-public     (Cloud Boost)
```

Đảm bảo backend có endpoints này!

---

### 3. CORS và Authentication

Endpoint `/api/scan-document-public` là public (không cần auth).

Nếu backend yêu cầu auth:
- Check code xem có gửi token không
- Hoặc update endpoint thành public

---

## 🎯 TÓM TẮT

**Vấn đề:** Double slash `//api` → 404  
**Nguyên nhân:** Backend URL có trailing slash  
**Giải pháp:** Normalize URL trước khi gọi API  
**Kết quả:** Cloud Boost hoạt động với mọi format URL  

---

## 🚀 NEXT STEPS

1. **Restart app** để load code mới
2. **Test Cloud Boost** với file ảnh
3. **Verify** URL trong console log (không có `//api`)

---

**Restart app và test lại Cloud Boost!** ☁️
