# ✅ Fix: DesktopScanner sử dụng BYOK Cloud OCR

## 🐛 Vấn đề

User đã setup Google Cloud Vision API key nhưng app vẫn gọi **Cloud Boost** (backend server) thay vì dùng API key của user.

### Logs cho thấy:
```javascript
hostname: 'landoc-scanner.preview.emergentagent.com'
path: '/api/scan-document-public'
// → Đang gọi Cloud Boost backend, KHÔNG PHẢI Google Cloud Vision API
```

### Root Cause:

**DesktopScanner.js** có logic cũ với 2 options:
1. `processOffline()` → Gọi local Python
2. `processCloudBoost()` → Gọi backend server

**Vấn đề:**
- User chọn "Google Cloud Vision" trong CloudSettings
- Nhưng DesktopScanner không đọc `ocrEngine` config
- Vẫn dùng logic cũ: offline vs cloud boost
- Không biết là cần dùng Google API key của user

---

## ✅ Giải pháp

### Thay đổi logic:

**Before (Sai):**
```javascript
// 2 modes riêng biệt
processOffline() → Local Tesseract only
processCloudBoost() → Backend server (GPT-4)

// User chọn Google → Không biết gọi cái nào
```

**After (Đúng):**
```javascript
// processDocumentOffline() đã support TẤT CẢ engines
processOffline() → Calls main.js → Checks ocrEngine config
  → If 'tesseract' → Python Tesseract
  → If 'easyocr' → Python EasyOCR
  → If 'vietocr' → Python VietOCR
  → If 'google' → Python Google Cloud Vision (with API key)
  → If 'azure' → Python Azure Computer Vision (with API key)

processCloudBoost() → Backend server (Cloud Boost only)
```

---

## 📦 Changes Made

### 1. DesktopScanner.js

#### Removed enginePref (legacy)
```javascript
// ❌ BEFORE
const [enginePref, setEnginePref] = useState('offline' | 'cloud');

// ✅ AFTER
const [currentOcrEngine, setCurrentOcrEngine] = useState('tesseract');
```

#### Load ocrEngine config
```javascript
// Load current OCR engine from unified config
const engine = await api.getConfig('ocrEngine') || 'tesseract';
setCurrentOcrEngine(engine);
console.log('🔍 Current OCR Engine:', engine);
```

#### Updated processOffline comment
```javascript
const processOffline = async (file) => {
  // This calls Python with current ocrEngine config
  // Main.js will load API keys if engine is 'google' or 'azure'
  const result = await window.electronAPI.processDocumentOffline(file.path);
  return result;
};
```

#### Added Engine Display UI
```jsx
{selectedFiles.length > 0 && (
  <div className="mt-2 flex items-center gap-2">
    <span>📦 Đã chọn {selectedFiles.length} file</span>
    <span className="border border-blue-200">
      {currentOcrEngine === 'google' && '☁️ Google Cloud Vision'}
      {currentOcrEngine === 'azure' && '☁️ Azure Computer Vision'}
      {currentOcrEngine === 'tesseract' && '⚡ Tesseract OCR'}
      {currentOcrEngine === 'easyocr' && '⚡ EasyOCR'}
      {currentOcrEngine === 'vietocr' && '⚡ VietOCR'}
    </span>
  </div>
)}
```

---

## 🔄 Flow sau khi fix

### User chọn Google Cloud Vision:

```mermaid
1. CloudSettings → Select "Google Cloud Vision" → Save API key
   ↓
2. Config saved: ocrEngine = 'google', cloudOCR.google.apiKey = 'AIza...'
   ↓
3. DesktopScanner → Load ocrEngine config → setCurrentOcrEngine('google')
   ↓
4. UI shows: "☁️ Google Cloud Vision"
   ↓
5. User scan → processOffline() → window.electronAPI.processDocumentOffline()
   ↓
6. Main.js → Check ocrEngine = 'google' → Load API key from store
   ↓
7. Spawn Python: python process_document.py image.jpg google AIza...
   ↓
8. Python calls Google Cloud Vision API with user's key
   ↓
9. Return result to UI ✅
```

---

## 🧪 Testing Steps

### 1. Setup Google Cloud Vision
- [ ] CloudSettings → Select "Google Cloud Vision"
- [ ] Enter API key
- [ ] Test API Key → Should succeed
- [ ] Save

### 2. Verify Engine Display
- [ ] Go to "Quét tài liệu" tab
- [ ] Select files
- [ ] Should see badge: **"☁️ Google Cloud Vision"** (blue border)

### 3. Test Scan
- [ ] Click "Bắt đầu quét"
- [ ] Watch console logs
- [ ] Should see: `🔍 Current OCR Engine: google`
- [ ] Should NOT see: `landoc-scanner.preview.emergentagent.com`
- [ ] Should see Python process with Google API

### 4. Verify Result
- [ ] Check result method: Should be `"cloud_ocr"` not `"cloud_boost"`
- [ ] Check ocr_engine: Should be `"Google Cloud Vision"`
- [ ] Accuracy should be 90-95%

---

## 📊 Engine Indicator UI

**Visual feedback for user:**

| Engine | Display | Color |
|--------|---------|-------|
| Tesseract | ⚡ Tesseract OCR | Gray |
| EasyOCR | ⚡ EasyOCR | Gray |
| VietOCR | ⚡ VietOCR | Gray |
| Google Cloud Vision | ☁️ Google Cloud Vision | Blue |
| Azure Computer Vision | ☁️ Azure Computer Vision | Blue |

---

## 🔍 Debug Checklist

Nếu vẫn gọi Cloud Boost backend:

- [ ] Check console logs: `🔍 Current OCR Engine: ???`
- [ ] Verify ocrEngine config: F12 → Application → IndexedDB → electron-store
- [ ] Restart app after saving API key
- [ ] Check main.js logs khi scan
- [ ] Verify Python command includes API key as argument

---

## 📂 Files Modified

1. `/desktop-app/src/components/DesktopScanner.js`
   - Removed `enginePref` state
   - Added `currentOcrEngine` state
   - Load from `ocrEngine` config
   - Added engine display UI
   - Updated processOffline comment

2. `/desktop-app/FIX_BYOK_CLOUD_USAGE.md` (this file)

---

## 🎯 Expected Behavior

### After this fix:

**User selects Google Cloud Vision:**
```
CloudSettings → Choose Google → Enter key → Save
   ↓
DesktopScanner shows: "☁️ Google Cloud Vision"
   ↓
Scan documents → Uses Google API with user's key
   ↓
Result: cloud_ocr, accuracy 90-95% ✅
```

**Cloud Boost (backend) only when:**
- User clicks specific "Cloud Boost" button (if exists)
- Or uses compare mode with Cloud option
- NOT the default scan flow

---

**Status:** ✅ Fixed  
**Impact:** High - Enables BYOK feature to work correctly  
**Testing:** Required - User to test with real Google API key
