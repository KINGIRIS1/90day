# 🔧 Quick Fix: PaddleOCR Installation Issues

## ❌ Error: "Could not find a version that satisfies the requirement paddlepaddle>=3.0.0"

### ✅ Solution 1: Install without version constraint (Recommended)

```bash
cd desktop-app/python
python -m pip install paddleocr
```

PaddleOCR will automatically install the compatible PaddlePaddle version.

---

### ✅ Solution 2: Manual installation step-by-step

```bash
# Step 1: Install PaddlePaddle (CPU version)
python -m pip install paddlepaddle -i https://pypi.org/simple

# Step 2: Install PaddleOCR
python -m pip install paddleocr

# Step 3: Install other dependencies
python -m pip install Pillow opencv-python-headless pytesseract

# Step 4: Verify
python -c "from paddleocr import PaddleOCR; print('✅ Success!')"
```

---

### ✅ Solution 3: Use Tesseract instead (Faster setup)

If PaddleOCR installation fails, app will automatically use Tesseract:

**Windows:**
1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install with Vietnamese language pack
3. Install Python wrapper:
   ```bash
   pip install pytesseract
   ```

**Accuracy:**
- PaddleOCR: 90-95% (best)
- Tesseract: 85-88% (good)

---

## 🔍 Check Python Version

PaddlePaddle requires Python 3.9-3.12:

```bash
python --version
```

If your Python version is outside this range, download compatible version from python.org

---

## 🔄 Re-run Installation

After applying fixes:

```bash
cd desktop-app
install.bat
```

---

## ✅ Verification

Test if PaddleOCR is working:

```bash
python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='vi'); print('✅ PaddleOCR working!')"
```

Expected: "✅ PaddleOCR working!" (may take 1-2 minutes on first run for model download)

---

## 📞 Still Having Issues?

The app has **automatic fallback** - it will use Tesseract if PaddleOCR is not available.

Both work fine:
- ✅ With PaddleOCR: 90-95% accuracy
- ✅ With Tesseract: 85-88% accuracy

Choose what works for your system!
