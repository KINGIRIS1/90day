# 🪟 Hướng Dẫn Chạy Desktop App trên Windows

## ✅ Đã Fix Xong!

Desktop app đã được cập nhật để hỗ trợ Windows.

---

## 🚀 Cách Chạy

### **Cách 1: Dùng lệnh cross-platform (khuyến nghị)**

```cmd
cd c:\desktop-app
yarn electron-dev
```

### **Cách 2: Dùng lệnh Windows-specific**

```cmd
cd c:\desktop-app
yarn electron-dev-win
```

---

## 📦 Python OCR Setup (Chọn 1 trong 3)

### **✅ Option 1: Tesseract (Nhẹ nhất - Khuyến nghị)**

1. **Tải Tesseract:**
   - Link: https://github.com/UB-Mannheim/tesseract/wiki
   - File: `tesseract-ocr-w64-setup-5.x.x.exe`
   - **Quan trọng:** Chọn "Vietnamese" trong Additional Language Data

2. **Cài Python packages:**
   ```cmd
   cd c:\desktop-app\python
   pip install pytesseract pillow --user
   ```

3. **Test:**
   ```cmd
   python -c "import pytesseract; print('OK')"
   ```

**Ưu điểm:**
- ✅ Siêu nhẹ (chỉ ~100MB)
- ✅ Không cần Visual Studio Build Tools
- ✅ Cài nhanh (3-5 phút)
- ✅ Accuracy: ~80-85%

---

### **Option 2: EasyOCR với Anaconda**

1. **Cài Anaconda:** https://www.anaconda.com/download

2. **Mở Anaconda Prompt:**
   ```cmd
   conda create -n desktop-ocr python=3.10 -y
   conda activate desktop-ocr
   conda install numpy pillow -y
   pip install opencv-python-headless easyocr
   ```

3. **Chạy app trong Anaconda Prompt:**
   ```cmd
   cd c:\desktop-app
   yarn electron-dev
   ```

**Ưu điểm:**
- ✅ Accuracy cao hơn (~85-90%)
- ✅ Không cần Build Tools
- ❌ Nặng hơn (~2GB với PyTorch)

---

### **Option 3: Chỉ dùng Cloud Boost**

Không cần cài Python, chỉ dùng Cloud Boost mode:
- App sẽ gọi backend API
- Cần config Backend URL trong Settings
- Không có offline mode

---

## 🎯 **Recommended Flow**

```cmd
# 1. Cài Tesseract từ .exe installer
#    Link: https://github.com/UB-Mannheim/tesseract/wiki
#    ✅ Nhớ chọn Vietnamese language

# 2. Cài Python packages
cd c:\desktop-app\python
pip install pytesseract pillow --user

# 3. Về thư mục gốc
cd c:\desktop-app

# 4. Chạy app
yarn electron-dev
```

---

## ❓ Troubleshooting

### **Lỗi: Port 3000 đã bị dùng**

```cmd
# Tìm process đang dùng port 3000
netstat -ano | findstr :3000

# Kill process
taskkill /PID <PID_NUMBER> /F
```

### **Lỗi: Tesseract not found**

Mở file `c:\desktop-app\python\ocr_engine_tesseract.py`, uncomment dòng:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Hoặc thêm Tesseract vào PATH:
- System Properties → Environment Variables
- Edit PATH → Add: `C:\Program Files\Tesseract-OCR`

### **Lỗi: JavaScript packages thiếu**

```cmd
cd c:\desktop-app
yarn install
```

---

## ✅ Checklist Hoàn Chỉnh

- [ ] ✅ Node.js đã cài (check: `node --version`)
- [ ] ✅ Yarn đã cài (check: `yarn --version`)
- [ ] ✅ Python đã cài (check: `python --version`)
- [ ] ✅ Tesseract đã cài + Vietnamese language
- [ ] ✅ Python packages: `pip install pytesseract pillow`
- [ ] ✅ JavaScript packages: `yarn install`
- [ ] ✅ Chạy: `yarn electron-dev`

---

## 🎉 Khi Thành Công

Bạn sẽ thấy:
1. Terminal: "Compiled successfully!"
2. Cửa sổ Electron mở ra
3. Giao diện: "Document Scanner" với 2 tabs
4. Click "📁 Chọn file" → Chọn ảnh → Click "🔵 Offline OCR"
5. Kết quả hiện ra sau 2-5 giây!

---

## 📊 So Sánh 3 Options

| Tiêu chí | Tesseract | EasyOCR | Cloud Only |
|----------|-----------|---------|------------|
| **Cài đặt** | ⭐⭐⭐⭐⭐ Dễ | ⭐⭐⭐ TB | ⭐⭐⭐⭐⭐ Rất dễ |
| **Dung lượng** | ~100MB | ~2GB | 0 |
| **Accuracy** | 80-85% | 85-90% | 93%+ |
| **Offline** | ✅ | ✅ | ❌ |
| **Tốc độ** | Nhanh | Trung bình | Phụ thuộc mạng |

---

**Khuyến nghị: Dùng Tesseract cho đơn giản nhất!** 🚀
