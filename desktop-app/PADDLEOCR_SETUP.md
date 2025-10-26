# 🚀 PaddleOCR Installation Guide - Desktop App

## ✨ Tại Sao Dùng PaddleOCR?

**PaddleOCR** cung cấp độ chính xác cao nhất cho tiếng Việt:

| OCR Engine | Accuracy | Cost | Offline |
|-----------|----------|------|---------|
| **PaddleOCR** | **90-95%** ✅ | FREE | ✅ |
| Tesseract | 85-88% | FREE | ✅ |
| GPT-4 Vision | 93%+ | $$$ | ❌ |

**Cải thiện: +7% accuracy so với Tesseract, miễn phí!**

---

## 📦 Installation

### Windows (Recommended)

#### Option A: Automatic Installation (Khuyến nghị)

```bash
cd desktop-app
install.bat
```

Script sẽ tự động:
- Cài đặt Python dependencies
- Download PaddleOCR models
- Setup Vietnamese language model

#### Option B: Manual Installation

1. **Install Python 3.9-3.12 (64-bit)**
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH"

2. **Install PaddlePaddle**
   ```bash
   python -m pip install paddlepaddle
   ```

3. **Install PaddleOCR**
   ```bash
   pip install paddleocr
   ```

4. **Install other dependencies**
   ```bash
   cd desktop-app/python
   pip install -r requirements-windows.txt
   ```

5. **Test installation**
   ```bash
   python ocr_engine_paddleocr.py test_image.jpg
   ```

---

### Mac/Linux

```bash
# Install PaddlePaddle
pip install paddlepaddle

# Install PaddleOCR
pip install paddleocr

# Install dependencies
cd desktop-app/python
pip install -r requirements.txt

# Test
python ocr_engine_paddleocr.py test_image.jpg
```

---

## 🔧 Troubleshooting

### ❌ "No module named 'paddleocr'"

```bash
pip install paddleocr paddlepaddle
```

### ❌ "ImportError: cannot import name PaddleOCR"

Reinstall with latest version:
```bash
pip uninstall paddleocr paddlepaddle -y
pip install paddleocr --upgrade
```

### ❌ Model download fails

Models are downloaded automatically on first run. If download fails:

1. Check internet connection
2. Retry - models are cached after first download
3. Manual download from: https://github.com/PaddlePaddle/PaddleOCR

### ❌ Slow performance

PaddleOCR uses CPU by default. For GPU acceleration:

```bash
# NVIDIA GPU (Windows/Linux)
pip uninstall paddlepaddle -y
pip install paddlepaddle-gpu
```

---

## 🎯 Verification

Run test to verify installation:

```bash
cd desktop-app/python
python -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR installed successfully')"
```

Expected output:
```
✅ PaddleOCR installed successfully
```

---

## 📊 Usage in Desktop App

Desktop app automatically detects and uses the best available OCR:

1. **PaddleOCR** (if installed) - 90-95% accuracy
2. **Tesseract** (fallback) - 85-88% accuracy  
3. **EasyOCR** (alternative) - 87-90% accuracy

Priority order ensures best performance!

---

## 🔄 Switching OCR Engines

Desktop app chooses OCR engine automatically, but you can force specific engine:

### Force PaddleOCR:
Rename or delete `ocr_engine_tesseract.py`

### Force Tesseract:
Uninstall PaddleOCR:
```bash
pip uninstall paddleocr paddlepaddle -y
```

---

## 💡 Performance Tips

### 1. First Run is Slower
- Models download automatically (~100MB)
- Subsequent runs are fast (models cached)

### 2. Optimize Accuracy
Already optimized in code:
- ✅ Scans top 40% of document (where title is)
- ✅ Font height detection (2x boost for titles)
- ✅ Vietnamese language model

### 3. Speed vs Accuracy
Current settings prioritize accuracy. For faster processing:
- Reduce image size before OCR
- Skip font height detection

---

## 📚 References

- PaddleOCR GitHub: https://github.com/PaddlePaddle/PaddleOCR
- Vietnamese OCR: https://github.com/bmd1905/vietnamese-ocr
- Installation Guide: https://paddlepaddle.github.io/PaddleOCR/

---

## ✅ Success Indicators

After installation, desktop app will show:

```
✅ PaddleOCR Vietnamese model loaded successfully
Accuracy estimate: 90-95%
```

Instead of:

```
Using Tesseract OCR
Accuracy estimate: 85-88%
```

---

## 🆘 Support

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Verify Python version (3.9-3.12)
3. Ensure 64-bit Python installation
4. Try reinstalling dependencies

For persistent issues, desktop app will automatically fallback to Tesseract.
