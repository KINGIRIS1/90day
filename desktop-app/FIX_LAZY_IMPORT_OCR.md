# ✅ Fix: Lazy Import OCR Engines

## 🐛 Vấn đề

User chọn Google Cloud Vision nhưng bị lỗi:
```
Missing dependency: No module named 'pytesseract'
```

**Logs cho thấy:**
```
Spawning: python process_document.py ... google [API_KEY]  ← Đúng!
[Python stderr]: Missing dependency: No module named 'pytesseract'  ← Fail!
```

### Root Cause:

**process_document.py** import tất cả engines ngay đầu file:

```python
# Đầu file:
from ocr_engine_tesseract import OCREngine as TesseractEngine  ← Fail ở đây!
tesseract_engine = TesseractEngine()

# Chưa kịp chạy tới đây:
if ocr_engine_type == 'google':
    from ocr_engine_google import ocr_google_cloud_vision
```

**Vấn đề:**
- User chỉ muốn dùng Google Cloud Vision
- Không cần Tesseract dependencies
- Nhưng script fail ngay khi import Tesseract → Crash trước khi vào Google logic

---

## ✅ Giải pháp: Lazy Import

**Concept:** Chỉ import engine nào khi thực sự cần dùng

### Before (Eager Import):
```python
# Đầu file - Import TẤT CẢ
from ocr_engine_tesseract import OCREngine as TesseractEngine
from ocr_engine_vietocr import OCREngine as VietOCREngine  
from ocr_engine_easyocr import OCREngine as EasyOCREngine

tesseract_engine = TesseractEngine()  # Fail nếu thiếu pytesseract
vietocr_engine = VietOCREngine()  # Fail nếu thiếu vietocr
easyocr_engine = EasyOCREngine()  # Fail nếu thiếu easyocr

# Problem: Tất cả phải có dependencies dù không dùng
```

### After (Lazy Import):
```python
# Đầu file - KHÔNG import gì
tesseract_engine = None
vietocr_engine = None
easyocr_engine = None

# Trong process_document():
if ocr_engine_type == 'google':
    # Import Google engine (chỉ cần requests)
    from ocr_engine_google import ocr_google_cloud_vision
    text = ocr_google_cloud_vision(image, api_key)
    
elif ocr_engine_type == 'tesseract':
    # Chỉ khi cần Tesseract mới import
    if tesseract_engine is None:
        from ocr_engine_tesseract import OCREngine
        tesseract_engine = OCREngine()
    text = tesseract_engine.extract_text(image)
```

**Benefits:**
- ✅ Google Cloud Vision work mà không cần Tesseract
- ✅ Azure work mà không cần Tesseract
- ✅ Chỉ install dependencies cho engine thực sự dùng
- ✅ Faster startup (không load unused engines)

---

## 📦 Implementation Details

### 1. Removed Top-level Imports

**Before:**
```python
from ocr_engine_tesseract import OCREngine as TesseractEngine
from rule_classifier import RuleClassifier

tesseract_engine = TesseractEngine()  # Eager init

try:
    from ocr_engine_vietocr import OCREngine as VietOCREngine
    vietocr_engine = VietOCREngine()
except:
    vietocr_engine = None
```

**After:**
```python
from rule_classifier import RuleClassifier  # Only classifier

# Lazy init - start as None
tesseract_engine = None
vietocr_engine = None
easyocr_engine = None
```

---

### 2. Cloud OCR Engines (Already Lazy)

```python
if ocr_engine_type == 'google':
    # Import only when needed
    from ocr_engine_google import ocr_google_cloud_vision
    text, confidence, error = ocr_google_cloud_vision(file_path, api_key)

elif ocr_engine_type == 'azure':
    # Import only when needed
    from ocr_engine_azure import ocr_azure_computer_vision
    text, confidence, error = ocr_azure_computer_vision(file_path, api_key, endpoint)
```

**Benefits:**
- Google engine chỉ cần `requests` library
- Azure engine chỉ cần `requests` library
- Không cần pytesseract, vietocr, easyocr

---

### 3. Offline OCR Engines (Now Lazy)

```python
else:  # Offline engines
    global tesseract_engine, vietocr_engine, easyocr_engine
    
    if ocr_engine_type == 'tesseract':
        # Lazy load Tesseract
        if tesseract_engine is None:
            from ocr_engine_tesseract import OCREngine as TesseractEngine
            tesseract_engine = TesseractEngine()
        ocr_engine = tesseract_engine
        
    elif ocr_engine_type == 'vietocr':
        # Lazy load VietOCR
        if vietocr_engine is None:
            try:
                from ocr_engine_vietocr import OCREngine as VietOCREngine
                vietocr_engine = VietOCREngine()
            except Exception as e:
                # Fallback to Tesseract
                if tesseract_engine is None:
                    from ocr_engine_tesseract import OCREngine as TesseractEngine
                    tesseract_engine = TesseractEngine()
                ocr_engine = tesseract_engine
                
    # ... EasyOCR similar logic
```

**Benefits:**
- Tesseract chỉ load khi user chọn Tesseract
- VietOCR chỉ load khi user chọn VietOCR
- EasyOCR chỉ load khi user chọn EasyOCR

---

## 🔄 Flow Comparison

### Before (Fail):
```
User: Chọn Google Cloud Vision
  ↓
App: python process_document.py ... google [API_KEY]
  ↓
Python: from ocr_engine_tesseract import ...  ← FAIL!
  ↓
Error: No module named 'pytesseract'
  ↓
❌ Google Cloud Vision không chạy được
```

### After (Success):
```
User: Chọn Google Cloud Vision
  ↓
App: python process_document.py ... google [API_KEY]
  ↓
Python: Check ocr_engine_type == 'google'
  ↓
Python: from ocr_engine_google import ...  ← Only this!
  ↓
Python: Call Google Cloud Vision API
  ↓
✅ Success! Không cần pytesseract
```

---

## 📊 Dependency Requirements

### Cloud OCR Engines:
```python
# Google Cloud Vision
Required: requests

# Azure Computer Vision
Required: requests

# Both work without:
- pytesseract ✅
- vietocr ✅
- easyocr ✅
```

### Offline OCR Engines:
```python
# Tesseract
Required: pytesseract, Pillow, tesseract binary

# VietOCR
Required: vietocr, torch, torchvision

# EasyOCR
Required: easyocr, torch, torchvision
```

**User chỉ cần install engine họ dùng! 🎯**

---

## 🧪 Testing Scenarios

### Scenario 1: Cloud Only User
```bash
# User chỉ install requests
pip install requests

# Chọn Google Cloud Vision
→ ✅ Works perfectly
→ No need for pytesseract, vietocr, easyocr
```

### Scenario 2: Mixed User
```bash
# User install requests + tesseract
pip install requests pytesseract pillow

# Switch between:
→ ✅ Google Cloud Vision (uses requests)
→ ✅ Tesseract (uses pytesseract)
→ ✅ VietOCR fails gracefully, fallback to Tesseract
```

### Scenario 3: Offline Only User
```bash
# User install tesseract only
pip install pytesseract pillow

# Try Google Cloud Vision without API key
→ ✅ Clear error: "API key required"
→ ✅ Can switch to Tesseract
```

---

## 🎯 Key Benefits

### For Users:
1. **Minimal dependencies** - Chỉ cài engine dùng
2. **Faster startup** - Không load unused engines
3. **Cloud works independently** - Không cần offline dependencies

### For Developers:
1. **Clean architecture** - Each engine isolated
2. **Easy to add engines** - Just add lazy load logic
3. **Better error handling** - Per-engine errors, not global crash

### For Deployment:
1. **Smaller packages** - Bundle only needed engines
2. **Flexible configs** - Users choose dependencies
3. **Cloud-first option** - Deploy without heavy ML libs

---

## 📂 Files Modified

1. `/desktop-app/python/process_document.py`
   - Removed top-level OCR engine imports
   - Added lazy loading for Tesseract
   - Added lazy loading for VietOCR
   - Added lazy loading for EasyOCR
   - Google/Azure already lazy (import inside if-block)

2. `/desktop-app/FIX_LAZY_IMPORT_OCR.md` (this file)

---

## ✅ Verification Checklist

### Google Cloud Vision:
- [ ] User không có pytesseract installed
- [ ] Chọn Google Cloud Vision
- [ ] Enter API key
- [ ] Scan document
- [ ] ✅ Should work without pytesseract error

### Azure Computer Vision:
- [ ] User không có pytesseract installed
- [ ] Chọn Azure Computer Vision
- [ ] Enter API key + endpoint
- [ ] Scan document
- [ ] ✅ Should work without pytesseract error

### Tesseract (with dependencies):
- [ ] Install pytesseract
- [ ] Chọn Tesseract
- [ ] Scan document
- [ ] ✅ Should work

### Graceful Degradation:
- [ ] Chọn VietOCR (not installed)
- [ ] Should fallback to Tesseract
- [ ] Or show clear error if Tesseract also missing

---

**Status:** ✅ Lazy Loading Complete  
**Impact:** High - Enables cloud-only users  
**Test Now:** Google Cloud Vision without Tesseract dependencies
