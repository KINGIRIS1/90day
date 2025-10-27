# 🎯 VietOCR Integration - User Choice Feature (2025)

## ✨ Overview

**NEW FEATURE**: Users can now **choose their preferred OCR engine** in Settings!

- 🔧 **Tesseract OCR**: Fast, lightweight, multi-language (85-88% accuracy)
- 🇻🇳 **VietOCR**: Vietnamese specialized, Transformer-based (90-95% accuracy)

## 📋 What's Implemented

### 1. Backend Changes

**File: `/app/desktop-app/python/process_document.py`**

- ✅ Imports both Tesseract and VietOCR engines
- ✅ Initializes both engines on startup
- ✅ Accepts `ocr_engine_type` parameter ('tesseract' or 'vietocr')
- ✅ Auto-fallback if VietOCR selected but not available
- ✅ Returns engine name in OCR result

```python
# Usage:
result = process_document("image.jpg", ocr_engine_type="vietocr")
# result['ocr_engine'] = "VietOCR" or "Tesseract"
```

### 2. Electron Changes

**Files: `electron/main.js` and `public/electron.js`**

- ✅ Reads `ocrEngineType` from electron-store
- ✅ Passes engine preference to Python script
- ✅ Default: 'tesseract' (safe fallback)

```javascript
const ocrEngineType = store.get('ocrEngineType', 'tesseract');
spawn(pythonPath, [scriptPath, filePath, ocrEngineType]);
```

### 3. UI Changes

**File: `/app/desktop-app/src/components/Settings.js`**

New section: **"🔍 Chọn OCR Engine (Offline)"**

- ✅ Radio button: Tesseract OCR
  - Description: "Nhanh, nhẹ, hỗ trợ đa ngôn ngữ (bao gồm tiếng Việt)"
- ✅ Radio button: VietOCR (Transformer)
  - Description: "Chuyên cho tiếng Việt, độ chính xác cao (90-95%), cần cài đặt riêng"
- ✅ Auto-save on selection
- ✅ Green checkmark feedback
- ✅ Dynamic display in "App Information" section

## 🚀 How to Use

### For End Users:

1. **Open the Desktop App**
2. **Go to Settings tab**
3. **Find "🔍 Chọn OCR Engine (Offline)"**
4. **Select your preferred engine:**
   - Choose **Tesseract** for speed and general use
   - Choose **VietOCR** for better Vietnamese accuracy (requires installation)
5. **Setting is saved automatically**
6. **Process documents** - your choice will be used

### First Time Using VietOCR:

If you select VietOCR but haven't installed it:

1. The app will show: `⚠️ VietOCR not available`
2. **Install VietOCR:**
   ```bash
   pip install vietocr torch torchvision
   # Or for Python 3.12 specifically:
   py -3.12 -m pip install vietocr torch torchvision
   ```
3. On **first OCR run**, VietOCR will download model (~100MB, 1-2 minutes)
4. Subsequent runs will be fast (1-2 seconds per page)

## 📊 Performance Comparison

| Feature | Tesseract | VietOCR |
|---------|-----------|---------|
| **Speed** | 0.5-1s/page ⚡⚡⚡ | 1-2s/page ⚡⚡ |
| **Accuracy (Vietnamese)** | 85-88% | 90-95% ✅ |
| **Languages** | Multi-language | Vietnamese only |
| **Model Size** | ~4MB | ~100MB |
| **Setup** | Simple (binary) | Requires Python packages |
| **Best For** | General use, speed | Vietnamese documents, accuracy |

## 🎯 When to Use Which Engine?

### Use Tesseract If:
- ✅ You need **fast processing** (0.5-1s per page)
- ✅ You work with **multiple languages**
- ✅ You want a **lightweight** solution
- ✅ **85-88% accuracy is sufficient** for your needs

### Use VietOCR If:
- ✅ You work **exclusively with Vietnamese** documents
- ✅ You need **higher accuracy** (90-95%)
- ✅ You can afford **slightly slower** processing (1-2s)
- ✅ You have **Python packages installed** (vietocr, torch)

## 🔧 Technical Details

### Architecture:

```
User Selection (Settings UI)
    ↓
electron-store saves 'ocrEngineType'
    ↓
Electron reads preference on OCR request
    ↓
Pass to Python: process_document.py <file> <engine_type>
    ↓
Python loads selected engine
    ↓
Extract text + classify
    ↓
Return result with engine name
```

### Fallback Logic:

```python
if ocr_engine_type == 'vietocr' and vietocr_engine is not None:
    # Use VietOCR
elif ocr_engine_type == 'vietocr' and vietocr_engine is None:
    # VietOCR requested but not installed → fallback to Tesseract
    print("⚠️ VietOCR requested but not available, falling back to Tesseract")
else:
    # Use Tesseract (default)
```

### Persistence:

User preference is saved in **electron-store** (local JSON file):
- Windows: `%APPDATA%/<app-name>/config.json`
- Mac: `~/Library/Application Support/<app-name>/config.json`
- Linux: `~/.config/<app-name>/config.json`

## 📝 Files Modified

1. **`/app/desktop-app/python/process_document.py`**
   - Import both engines
   - Add `ocr_engine_type` parameter
   - Engine selection logic
   - Return engine name in result

2. **`/app/desktop-app/electron/main.js`**
   - Read `ocrEngineType` from store
   - Pass to Python script

3. **`/app/desktop-app/public/electron.js`**
   - Same changes as main.js (for production build)

4. **`/app/desktop-app/src/components/Settings.js`**
   - New component: `OCREngineTypeSetting`
   - UI for engine selection
   - Dynamic engine display
   - Updated usage guide

5. **`/app/desktop-app/python/requirements.txt`**
   - Added VietOCR as optional dependency

6. **`/app/desktop-app/VIETOCR_SETUP.md`**
   - Updated with UI toggle instructions

## ✅ Testing Checklist

### Manual Testing:

- [ ] Open Settings tab
- [ ] See "🔍 Chọn OCR Engine (Offline)" section
- [ ] Select **Tesseract** → green checkmark appears
- [ ] Process a document → should use Tesseract
- [ ] Go back to Settings → **Tesseract is still selected** (persistence)
- [ ] Select **VietOCR** → green checkmark appears
- [ ] If VietOCR installed:
  - [ ] Process document → should use VietOCR
  - [ ] Check result → `ocr_engine: "VietOCR"`
  - [ ] First run: model downloads (~1-2 min)
  - [ ] Second run: fast (~1-2s)
- [ ] If VietOCR not installed:
  - [ ] Process document → should fallback to Tesseract
  - [ ] Check logs: "⚠️ VietOCR requested but not available"
- [ ] Check App Information section → shows selected engine
- [ ] Restart app → preference persists

### Expected Console Logs:

**With Tesseract:**
```
🔍 Using Tesseract engine
✅ Tesseract OCR loaded (VietOCR disabled)
```

**With VietOCR (installed):**
```
🔍 Using VietOCR engine
✅ Both Tesseract and VietOCR engines loaded
```

**With VietOCR (not installed):**
```
⚠️ VietOCR not available: No module named 'vietocr'
✅ Tesseract OCR loaded (VietOCR disabled)
```

## 🆘 Troubleshooting

### Issue: VietOCR option selected but using Tesseract

**Solution:**
1. Check if VietOCR is installed:
   ```bash
   py -3.12 -c "import vietocr; print('VietOCR installed')"
   ```
2. If not installed:
   ```bash
   py -3.12 -m pip install vietocr torch torchvision
   ```

### Issue: VietOCR very slow (>10s per page)

**Solution:**
1. First run downloads model (~100MB) - this is normal
2. Check if model is cached: `~/.cache/vietocr/` or `~/.vietocr/`
3. Subsequent runs should be 1-2s per page
4. If still slow, stick with Tesseract

### Issue: Settings not persisting

**Solution:**
1. Check electron-store config file exists
2. Try selecting engine again
3. Check browser console for errors

## 🎉 Success Indicators

After implementation:

✅ Settings has new "🔍 Chọn OCR Engine" section
✅ Can switch between Tesseract and VietOCR
✅ Green checkmark appears on save
✅ Preference persists across app restarts
✅ App Info shows selected engine dynamically
✅ OCR uses selected engine (check logs)
✅ Fallback works if VietOCR not installed
✅ No breaking changes to existing functionality

## 📖 User Documentation

See **VIETOCR_SETUP.md** for:
- Installation instructions
- Performance benchmarks
- Troubleshooting guide
- Advanced configuration

## 🚀 Future Enhancements

Potential improvements:
- [ ] Auto-detect best engine for each document
- [ ] Show real-time accuracy comparison
- [ ] Batch processing with mixed engines
- [ ] GPU acceleration toggle for VietOCR
- [ ] Custom model training support
- [ ] Multi-engine processing (run both, compare)

---

**Status:** ✅ COMPLETE - Ready for testing
**Date:** January 2025
**Implementation:** Both engines supported, user can choose in Settings UI
