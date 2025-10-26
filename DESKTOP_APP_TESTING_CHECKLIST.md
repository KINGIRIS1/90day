# Desktop App - Testing Checklist

## ✅ Pre-Testing Setup

### Environment Check
- [ ] Node.js version >= 16
  ```bash
  node --version
  ```
- [ ] Yarn installed
  ```bash
  yarn --version
  ```
- [ ] Python version >= 3.8
  ```bash
  python3 --version
  ```

### Installation
- [ ] JavaScript dependencies installed
  ```bash
  cd /app/desktop-app
  yarn install
  ```
- [ ] Python dependencies installed
  ```bash
  cd /app/desktop-app/python
  pip3 install -r requirements.txt
  ```
  **Expected time:** 5-10 minutes (PaddleOCR is large)

---

## 🧪 Phase 1: Python Engine Tests

### Test 1: Standalone Python Script
```bash
cd /app/desktop-app/python
python3 process_document.py /path/to/test-image.jpg
```

**Expected output:**
```json
{
  "success": true,
  "method": "offline_ocr",
  "original_text": "...",
  "doc_type": "Giấy chứng nhận quyền sử dụng đất",
  "confidence": 0.85,
  "short_code": "GCNQSD",
  "reasoning": "...",
  "recommend_cloud_boost": false,
  "accuracy_estimate": "85-88%"
}
```

**Test cases:**
- [ ] Test with valid Vietnamese land document image
- [ ] Test with invalid image (should return error)
- [ ] Test with non-existent file (should return error)
- [ ] Check processing time (should be 2-5 seconds)
- [ ] Verify confidence threshold logic (< 0.7 recommends cloud boost)

### Test 2: Import Validation
```bash
cd /app/desktop-app/python
python3 -c "from ocr_engine import OCREngine; from rule_classifier import RuleClassifier; print('OK')"
```
- [ ] No import errors
- [ ] No PaddleOCR initialization errors

---

## 🖥️ Phase 2: Electron App Tests

### Test 3: Development Mode Startup
```bash
cd /app/desktop-app
yarn electron-dev
```

**Expected behavior:**
- [ ] React dev server starts on port 3000
- [ ] Electron window opens automatically
- [ ] Window size: 1400x900
- [ ] No console errors in terminal
- [ ] DevTools open by default (development mode)

### Test 4: UI Rendering
**Visual checks:**
- [ ] Header displays "Document Scanner"
- [ ] Tab navigation: "📄 Quét tài liệu" and "⚙️ Cài đặt"
- [ ] Scanner tab active by default
- [ ] Two buttons visible: "📁 Chọn file" and "📂 Chọn thư mục"
- [ ] Tailwind CSS loaded (proper styling)
- [ ] No broken layouts

### Test 5: Tab Navigation
- [ ] Click "⚙️ Cài đặt" → Settings page shows
- [ ] Click "📄 Quét tài liệu" → Scanner page shows
- [ ] Active tab has white background
- [ ] Inactive tab has gray text

---

## 📁 Phase 3: File Selection Tests

### Test 6: Select Files Dialog
**Actions:**
1. Click "📁 Chọn file"
2. Native file dialog opens
3. Select 1-3 image files (.jpg, .png)
4. Click "Open"

**Expected:**
- [ ] File dialog appears (native OS dialog)
- [ ] Can filter by image types
- [ ] Can select multiple files
- [ ] Selected files show below buttons
- [ ] File names display correctly (Vietnamese characters if any)
- [ ] Shows count: "Đã chọn X file"

### Test 7: Select Folder Dialog
**Actions:**
1. Click "📂 Chọn thư mục"
2. Folder dialog opens

**Expected:**
- [ ] Folder dialog appears
- [ ] Alert shows: "Tính năng quét thư mục đang được phát triển"
  (Feature under development message)

---

## 🔵 Phase 4: Offline OCR Tests

### Test 8: Offline Processing - Happy Path
**Setup:** Select 1 Vietnamese land document image

**Actions:**
1. Click "Offline OCR + Rules" (blue card)

**Expected:**
- [ ] Processing indicator appears: "⚙️ Đang xử lý... (1/1)"
- [ ] Progress bar animates (0% → 100%)
- [ ] Processing time: 2-5 seconds per image
- [ ] Result card appears with:
  - [ ] File name
  - [ ] 🔵 "Offline OCR (FREE)" badge
  - [ ] "85-88%" accuracy estimate
  - [ ] Confidence percentage (e.g., "85%")
  - [ ] Colored confidence bar (green if >80%, yellow if >60%, red otherwise)
  - [ ] "Loại tài liệu" field
  - [ ] "Mã rút gọn" field

### Test 9: Offline Processing - Low Confidence
**Setup:** Select image with low confidence (< 70%)

**Expected:**
- [ ] Result shows < 70% confidence
- [ ] Yellow warning box appears:
  "💡 Độ tin cậy thấp. Khuyến nghị sử dụng Cloud Boost..."
- [ ] `recommend_cloud_boost: true` in result

### Test 10: Offline Processing - Error Cases
**Test cases:**
- [ ] Select non-image file → Error message
- [ ] Select corrupted image → Error message
- [ ] Error displays in red box with ❌ icon

### Test 11: Batch Offline Processing
**Setup:** Select 3-5 images

**Expected:**
- [ ] Progress shows: "(1/5)", "(2/5)", etc.
- [ ] Progress bar updates incrementally
- [ ] All results display after completion
- [ ] Results maintain order
- [ ] Each result has independent badge and confidence

---

## ☁️ Phase 5: Cloud Boost Tests

### Test 12: Cloud Boost - No Backend URL
**Actions:**
1. Don't configure backend URL
2. Select file
3. Click "Cloud Boost (GPT-4)" (purple card)

**Expected:**
- [ ] Purple card shows "Cần cấu hình Backend URL trong Cài đặt"
- [ ] Button is disabled (opacity 50%)
- [ ] Cannot click

### Test 13: Settings - Backend URL Configuration
**Actions:**
1. Go to "⚙️ Cài đặt" tab
2. Enter backend URL: `https://example.com/api`
3. Click "💾 Lưu cài đặt"

**Expected:**
- [ ] Input field accepts URL
- [ ] Green success message: "✓ Đã lưu cài đặt thành công!"
- [ ] Message auto-hides after 3 seconds
- [ ] Settings persist after app restart

### Test 14: Cloud Boost - With Backend URL
**Setup:** Configure backend URL in settings

**Actions:**
1. Go back to Scanner tab
2. Select file
3. Click "Cloud Boost (GPT-4)"

**Expected:**
- [ ] Purple card is now enabled
- [ ] Processing starts
- [ ] Currently shows: "Lỗi: Cloud Boost đang được phát triển"
  (This is expected - feature marked for Phase 3)

---

## ⚙️ Phase 6: Settings Tests

### Test 15: Settings Page Elements
**Expected elements:**
- [ ] "Cấu hình Cloud Boost" section
- [ ] Backend URL input field
- [ ] "💾 Lưu cài đặt" button
- [ ] "Thông tin ứng dụng" section showing:
  - [ ] Phiên bản: 1.0.0
  - [ ] Nền tảng: (Windows/Darwin/Linux)
  - [ ] OCR Engine: PaddleOCR 2.7
  - [ ] Cloud Boost status
- [ ] "📖 Hướng dẫn sử dụng" guide box (blue)

### Test 16: Settings Persistence
**Actions:**
1. Configure backend URL
2. Save
3. Close app completely
4. Reopen app
5. Check settings

**Expected:**
- [ ] Backend URL still present
- [ ] electron-store working correctly

---

## 🎨 Phase 7: UI/UX Tests

### Test 17: Responsive Design
**Actions:** Resize window (minimize, maximize, custom size)

**Expected:**
- [ ] Layout adjusts properly
- [ ] No horizontal scroll
- [ ] Buttons remain accessible
- [ ] Text doesn't overflow

### Test 18: Animations
**Checks:**
- [ ] Processing indicator pulses
- [ ] Confidence bar animates smoothly
- [ ] Result cards have hover effect (slight lift)
- [ ] Progress bar fills smoothly

### Test 19: Vietnamese Text Rendering
**Checks:**
- [ ] All Vietnamese characters display correctly
- [ ] No encoding issues
- [ ] Diacritics (dấu) render properly
- [ ] Font rendering is clear

---

## 🏗️ Phase 8: Build Tests

### Test 20: Production Build
```bash
cd /app/desktop-app
yarn build
```

**Expected:**
- [ ] Build completes without errors
- [ ] `/build` directory created
- [ ] Optimized React bundle
- [ ] File size reasonable (< 5MB)

### Test 21: Electron Package
```bash
yarn electron-build
```

**Expected:**
- [ ] Packaging completes
- [ ] `/dist` directory created
- [ ] Platform-specific installer:
  - Windows: `.exe` file
  - macOS: `.dmg` file
  - Linux: `.AppImage` file
- [ ] Python files included in package
- [ ] App size reasonable (50-150MB including Python)

### Test 22: Production App Launch
**Actions:**
1. Install from `/dist` package
2. Launch app

**Expected:**
- [ ] App starts without errors
- [ ] No DevTools open (production mode)
- [ ] All features work same as dev mode
- [ ] Performance is good (not slower)

---

## 🔒 Phase 9: Security Tests

### Test 23: Electron Security
**Checks:**
- [ ] `contextIsolation: true` in webPreferences
- [ ] `nodeIntegration: false`
- [ ] No direct Node.js access in renderer
- [ ] All IPC calls go through preload.js

### Test 24: File System Access
**Checks:**
- [ ] Renderer cannot directly access file system
- [ ] Only main process reads files
- [ ] File dialogs use Electron's secure API

---

## 🐛 Phase 10: Error Handling Tests

### Test 25: Python Process Errors
**Simulate:** Kill Python dependencies

**Expected:**
- [ ] Graceful error message
- [ ] No app crash
- [ ] User-friendly error display

### Test 26: Network Errors (Cloud Boost)
**Simulate:** Wrong backend URL

**Expected:**
- [ ] Network error caught
- [ ] Error message displayed
- [ ] App remains functional

### Test 27: Edge Cases
**Test cases:**
- [ ] Empty file selection → No action
- [ ] Very large image (> 10MB) → Process or timeout gracefully
- [ ] Special characters in file name → Handle correctly
- [ ] Concurrent processing attempts → Queue properly

---

## 📊 Phase 11: Performance Tests

### Test 28: Processing Speed
**Metrics to track:**
- [ ] Single image: 2-5 seconds (offline)
- [ ] 10 images: < 1 minute (offline)
- [ ] Memory usage stable (no leaks)
- [ ] CPU usage reasonable

### Test 29: App Responsiveness
**Checks:**
- [ ] UI doesn't freeze during processing
- [ ] Progress updates smoothly
- [ ] Can still interact with other tabs

---

## 📝 Test Results Summary

### Passing Tests: _____ / _____

### Critical Issues Found:
1. 
2. 
3. 

### Non-Critical Issues:
1. 
2. 
3. 

### Performance Notes:
- Processing speed: 
- Memory usage: 
- App size: 

### Recommendations:
1. 
2. 
3. 

---

## 🚀 Ready for Release Checklist

- [ ] All Phase 1-8 tests passing
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Performance acceptable
- [ ] User testing completed
- [ ] Build tested on target platforms
- [ ] Installation instructions verified

---

**Tested by:** _________________
**Date:** _________________
**Environment:** _________________
**Notes:** 
```
```
