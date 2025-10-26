# 🎁 Hướng Dẫn Cài Đặt - 90dayChonThanh Desktop

## 📦 Bạn nhận được gì?

Sau khi build option 3, bạn có **2 files**:
1. `90dayChonThanh-Setup-1.0.0.exe` (~150MB) - **INSTALLER**
2. `90dayChonThanh-Portable-Win.zip` (~220MB) - **PORTABLE**

---

## 🚀 Cách 1: Cài Đặt Bằng Installer (KHUYẾN NGHỊ)

### Dành cho: User thông thường

### Bước 1: Chuẩn bị (BẮT BUỘC)

**A. Cài Python 3.8+**
1. Download từ: https://www.python.org/downloads/
2. Chạy installer
3. ✅ **QUAN TRỌNG:** Tick "Add Python to PATH"
   ```
   ☑ Add Python 3.x to PATH
   ```
4. Click "Install Now"
5. Đợi cài xong

**Verify:**
```batch
# Mở Command Prompt (CMD), gõ:
python --version
# Phải hiện: Python 3.x.x
```

**B. Cài Python libraries**
```batch
# Mở CMD, gõ:
pip install pytesseract Pillow
```

**C. Cài Tesseract OCR**
1. Download từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Chọn: `tesseract-ocr-w64-setup-5.3.3.exe` (hoặc mới hơn)
3. Khi cài:
   - ✅ Tick "Vietnamese language pack"
   - ✅ Tick "Add to PATH"
4. Install

**Verify:**
```batch
tesseract --version
# Phải hiện: tesseract 5.x.x
```

---

### Bước 2: Cài App

1. Double click file: `90dayChonThanh-Setup-1.0.0.exe`
2. Nếu Windows hiện cảnh báo:
   - Click "More info"
   - Click "Run anyway"
3. Follow hướng dẫn:
   - Next → Next → Install
4. Đợi cài đặt hoàn tất
5. Click "Finish"

---

### Bước 3: Chạy App

**Desktop icon:**
- Double click icon "90dayChonThanh" trên desktop

**Start Menu:**
- Start → All Apps → 90dayChonThanh

**First run:**
- App có thể mất vài giây để khởi động
- Splash screen sẽ hiện ra
- Sau đó main window mở ra

---

### Bước 4: Test App

1. Click tab "Scanner"
2. Click "Quét Offline"
3. Chọn 1 ảnh tài liệu
4. Xem kết quả

**Nếu lỗi "Python not found":**
- Quay lại Bước 1A, cài Python
- Restart app

**Nếu lỗi "Tesseract not found":**
- Quay lại Bước 1C, cài Tesseract
- Restart app

---

## 🎒 Cách 2: Dùng Portable Version

### Dành cho: Power users, USB, không muốn install

### Bước 1: Giải nén

1. Right click file: `90dayChonThanh-Portable-Win.zip`
2. Extract All → Chọn folder → Extract
3. Vào folder vừa giải nén

### Bước 2: Chuẩn bị (GIỐNG Cách 1)

**Vẫn cần:**
- ✅ Python 3.8+ (Add to PATH)
- ✅ `pip install pytesseract Pillow`
- ✅ Tesseract OCR

**Không thể skip bước này!**

### Bước 3: Chạy App

1. Vào folder: `90dayChonThanh-Portable-Win\`
2. Double click: `90dayChonThanh.exe`
3. App mở ra

**Ưu điểm:**
- Có thể copy sang USB
- Chạy trên bất kỳ máy nào (có Python + Tesseract)
- Không modify registry

**Nhược điểm:**
- Không có Desktop icon
- Không có Start Menu entry
- Phải cài Python + Tesseract trên mỗi máy

---

## 🔍 Troubleshooting

### Lỗi: "Python is not recognized"

**Nguyên nhân:** Python chưa cài hoặc chưa add to PATH

**Giải pháp:**
1. Cài Python từ python.org
2. Khi cài, tick "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

**Nếu vẫn lỗi:**
```batch
# Thêm Python vào PATH thủ công:
1. Control Panel → System → Advanced system settings
2. Environment Variables
3. System variables → Path → Edit
4. New → Paste: C:\Python311\
5. New → Paste: C:\Python311\Scripts\
6. OK → OK → OK
7. Restart CMD
```

---

### Lỗi: "Tesseract is not recognized"

**Giải pháp:**
```batch
# Thêm Tesseract vào PATH:
1. Environment Variables (như trên)
2. Path → Edit → New
3. Paste: C:\Program Files\Tesseract-OCR\
4. OK → OK
5. Restart CMD
```

---

### Lỗi: "No module named 'pytesseract'"

**Giải pháp:**
```batch
pip install pytesseract Pillow
```

**Nếu vẫn lỗi:**
```batch
# Verify pip:
pip --version

# Reinstall:
python -m pip install --upgrade pip
pip install pytesseract Pillow
```

---

### App không mở

**Check:**
1. Python installed? `python --version`
2. Tesseract installed? `tesseract --version`
3. Dependencies installed? `pip list | findstr pytesseract`

**Nếu tất cả OK nhưng vẫn lỗi:**
1. Right click app → Properties → Compatibility
2. Tick "Run as administrator"
3. Try again

---

## 📋 Checklist Trước Khi Phân Phối

### Cho Developer (người build app)

- [ ] Build app với option 3
- [ ] Có 2 files: .exe và .zip
- [ ] Test installer trên máy clean
- [ ] Test portable trên máy clean
- [ ] Chuẩn bị file hướng dẫn này
- [ ] List requirements rõ ràng

### Package gửi cho User

**Minimum:**
```
📁 90dayChonThanh-Package/
├── 90dayChonThanh-Setup-1.0.0.exe
└── HUONG_DAN_CAI_DAT.txt (file này)
```

**Complete:**
```
📁 90dayChonThanh-Complete-Package/
├── 90dayChonThanh-Setup-1.0.0.exe
├── 90dayChonThanh-Portable-Win.zip
├── HUONG_DAN_CAI_DAT.txt
├── REQUIREMENTS.txt
└── Links/
    ├── Python-Download-Link.txt
    └── Tesseract-Download-Link.txt
```

---

## 📝 Requirements Summary

**PHẢI CÓ:**
1. ✅ Windows 10 hoặc mới hơn
2. ✅ Python 3.8+ (Add to PATH)
3. ✅ pytesseract, Pillow (pip install)
4. ✅ Tesseract OCR binary (Add to PATH)
5. ✅ ~500MB disk space

**OPTIONAL:**
- Internet (cho Cloud Boost feature)
- 4GB+ RAM (recommended)

---

## 🎯 Quick Start (Tóm tắt)

### Cài Đặt Đầy Đủ (15 phút)

```
1. Cài Python → Tick "Add to PATH"
   python --version ✓

2. pip install pytesseract Pillow
   pip list | findstr pytesseract ✓

3. Cài Tesseract → Tick Vietnamese
   tesseract --version ✓

4. Chạy: 90dayChonThanh-Setup-1.0.0.exe
   Next → Install ✓

5. Desktop icon → Open app ✓

6. Tab Scanner → Quét Offline → Test ✓
```

**Done! 🎉**

---

## 🆘 Support

**Nếu gặp vấn đề:**

1. **Check logs:**
   ```
   C:\Users\<tên user>\AppData\Roaming\90dayChonThanh\logs\
   ```

2. **Common issues:**
   - Python not found → Cài Python + Add PATH
   - Tesseract not found → Cài Tesseract + Add PATH
   - Module not found → pip install pytesseract Pillow

3. **Contact:**
   - Email: support@example.com
   - Attach: Error message + Log file

---

## 📱 Video Hướng Dẫn (Optional)

**Có thể tạo video ngắn:**
1. Cài Python (2 phút)
2. Cài Tesseract (1 phút)
3. Cài App (1 phút)
4. Demo sử dụng (2 phút)

**Total: 6 phút** → Very helpful cho non-tech users!

---

**🎊 Chúc bạn sử dụng app vui vẻ!**

Version: 1.0.0
Last Updated: 2025-01-27
