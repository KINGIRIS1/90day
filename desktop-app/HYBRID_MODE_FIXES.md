# Hybrid Mode Fixes

## 🐛 Vấn Đề Được Báo Cáo

1. **Python process exited with code 1** khi chạy `gemini-flash-hybrid`
2. **Chức năng resize settings bị mất** khi chọn hybrid mode

---

## ✅ Các Fix Đã Thực Hiện

### 1. **CloudSettings.js - Thêm Hybrid vào Resize Settings**

**Vấn đề**: Resize settings CHỈ hiển thị khi chọn `gemini-flash` hoặc `gemini-flash-lite`, KHÔNG có `gemini-flash-hybrid`.

**Fix**: Line 783
```javascript
// OLD
{(ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-lite') && (

// NEW
{(ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-hybrid' || ocrEngine === 'gemini-flash-lite') && (
```

**Kết quả**: Resize settings giờ hiển thị cho cả 3 modes: Flash, Hybrid, Lite

---

### 2. **electron/main.js - Thêm Hybrid vào API Key Validation (3 chỗ)**

**Vấn đề**: Electron main.js KHÔNG có logic xử lý `gemini-flash-hybrid` → không load API key → Python script fail.

**Fix 1** - Line 266 (Folder Scan):
```javascript
// OLD
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-lite') {

// NEW
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite') {
```

**Fix 2** - Line 363 (Batch Scan):
```javascript
// OLD
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-lite') {

// NEW
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite') {
```

**Fix 3** - Line 550 (Single File Scan):
```javascript
// OLD
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-lite') {

// NEW
} else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite') {
```

**Kết quả**: 
- Hybrid mode giờ load API key đúng cách
- Python script nhận được API key qua args
- Process không còn exit với code 1

---

### 3. **public/electron.js - Sync với main.js**

**Action**: Copy `electron/main.js` → `public/electron.js` để sync changes.

```bash
cp /app/desktop-app/electron/main.js /app/desktop-app/public/electron.js
```

**Kết quả**: Production build sẽ có cùng logic với dev build.

---

## 🧪 Cách Test

### Test 1: Resize Settings Hiển Thị
1. Mở app → Settings → Cloud OCR
2. Chọn: "🔄 Gemini Hybrid (Two-Tier)"
3. ✅ **Kiểm tra**: Section "💰 Tối ưu hóa chi phí Gemini" phải hiển thị
4. ✅ **Kiểm tra**: Checkbox "Tự động resize ảnh" phải có
5. ✅ **Kiểm tra**: Input fields cho Max Width/Height phải có

### Test 2: API Key Loading
1. Đảm bảo đã nhập Gemini API key
2. Chọn Hybrid mode
3. Save settings
4. Scan 1 ảnh
5. ✅ **Kiểm tra**: Console không có lỗi "API key not configured"
6. ✅ **Kiểm tra**: Console hiển thị: "🔄 TWO-TIER HYBRID ENGINE STARTED"

### Test 3: Hybrid Mode Hoạt Động
1. Scan document dễ (HDCQ)
   - ✅ Kỳ vọng: Tier 1 only
   - ✅ Console: "✅ TIER 1 ACCEPTED - No escalation needed"

2. Scan GCN document
   - ✅ Kỳ vọng: Tier 2 escalated (complex type)
   - ✅ Console: "⚠️ ESCALATION TRIGGER: Complex document type"

---

## 📝 Checklist Verification

- ✅ CloudSettings.js: Hybrid trong resize conditional
- ✅ electron/main.js: Hybrid trong API key check (3 chỗ)
- ✅ public/electron.js: Synced với main.js
- ✅ Import test: `python3 -c "from ocr_engine_gemini_flash_hybrid import ..."` → OK
- ✅ Backward compatible: Flash & Flash Lite vẫn hoạt động bình thường

---

## 🎯 Root Cause Analysis

**Nguyên nhân chính**: Khi implement Two-Tier Hybrid, tôi đã:
- ✅ Tạo Python engine mới (OK)
- ✅ Update process_document.py (OK)
- ✅ Update CloudSettings.js radio options + engine mappings (OK)
- ❌ **QUÊN** thêm hybrid vào resize settings conditional
- ❌ **QUÊN** thêm hybrid vào main.js API key validation (3 chỗ)

→ Dẫn đến:
1. Resize settings không hiển thị
2. API key không được load
3. Python script không nhận được API key
4. Process exit với code 1

---

## 💡 Lesson Learned

Khi thêm một OCR engine type mới, cần check TẤT CẢ các điều kiện sau:

### Frontend (CloudSettings.js):
- ✅ Radio option
- ✅ Engine mapping (UI ↔ Backend)
- ✅ API key save logic
- ✅ Setup section conditional
- ✅ **Resize settings conditional** ← QUAN TRỌNG
- ✅ Cost comparison section

### Electron (main.js):
- ✅ **API key validation** (folder scan)
- ✅ **API key validation** (batch scan)
- ✅ **API key validation** (single file scan)
- ✅ Sync với public/electron.js

### Backend (process_document.py):
- ✅ Engine type handling
- ✅ Import engine module
- ✅ Call engine function
- ✅ Return format

### Python Engine:
- ✅ Create new engine file
- ✅ Implement classification logic
- ✅ CLI interface for testing

---

## 🚀 Status

✅ **Tất cả fixes đã hoàn tất**
✅ **Sẵn sàng test lại**

User có thể:
1. Restart app (nếu đang chạy)
2. Chọn Hybrid mode
3. Scan documents
4. Verify resize settings hiển thị
5. Verify Hybrid mode hoạt động đúng

---

**Date**: 2025-01-XX  
**Status**: ✅ Fixed & Ready for Testing
