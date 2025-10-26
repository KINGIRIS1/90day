# 🚀 HƯỚNG DẪN NHANH - ALL-IN-ONE INSTALLER

## TÓM TẮT 30 GIÂY

Đã tạo xong hệ thống all-in-one installer. Developer chỉ cần:
1. Cài NSIS trên Windows
2. Download 2 file installers
3. Chạy `build-allinone.bat`
4. Nhận file `90dayChonThanh-AllInOne-Setup.exe` (~235MB)

---

## CHUẨN BỊ (5 PHÚT)

### 1. Cài NSIS
```
Download: https://nsis.sourceforge.io/Download
File: nsis-3.09-setup.exe
Cài với default settings
```

### 2. Download Python Installer
```
Link: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
Lưu vào: desktop-app/installers/python-3.11.8-amd64.exe
Size: ~30 MB
```

### 3. Download Tesseract Installer
```
Link: https://github.com/UB-Mannheim/tesseract/wiki
File: tesseract-ocr-w64-setup-5.3.3.exe
Lưu vào: desktop-app/installers/tesseract-ocr-w64-setup-5.3.3.exe
Size: ~50 MB
```

---

## BUILD (10 PHÚT)

### Bước 1: Kiểm tra
```batch
cd desktop-app
check-prerequisites.bat
```

### Bước 2: Build
```batch
build-allinone.bat
```

Đợi 5-10 phút...

### Bước 3: Kết quả
```
✅ File: 90dayChonThanh-AllInOne-Setup.exe
✅ Size: ~235 MB
✅ Includes: Python + Tesseract + App
```

---

## TEST (15 PHÚT)

### Tạo VM
- Windows 10/11 fresh install
- KHÔNG cài Python
- KHÔNG cài Tesseract

### Test Installer
1. Copy `.exe` vào VM
2. Double-click
3. Follow wizard
4. Đợi 5-10 phút
5. Test app

### Kiểm tra
- [ ] App mở được
- [ ] Python installed: `python --version`
- [ ] Tesseract installed: `tesseract --version`
- [ ] OCR works
- [ ] Desktop shortcut works

---

## PHÂN PHỐI

### Tạo Package
```
90dayChonThanh-v1.0.0/
├── 90dayChonThanh-AllInOne-Setup.exe
├── CAI_DAT_NHANH.txt
└── HUONG_DAN_SU_DUNG_ALLINONE.md
```

### Upload
- Google Drive, Dropbox, hoặc File server
- Share link với users

---

## TÀI LIỆU CHI TIẾT

📖 **Đọc thêm:**
- `BUILD_ALLINONE.md` - Guide đầy đủ
- `ALLINONE_BUILD_CHECKLIST.md` - Checklist chi tiết
- `HUONG_DAN_TONG_HOP.md` - Hướng dẫn tiếng Việt đầy đủ

---

## TROUBLESHOOTING NHANH

**Lỗi: NSIS not found**
→ Cài NSIS từ link trên

**Lỗi: Python installer not found**
→ Download và đặt đúng folder `installers/`

**Lỗi: Tesseract installer not found**
→ Download và đặt đúng folder `installers/`

**Lỗi: yarn build failed**
→ `rm -rf node_modules && yarn install`

---

## CẤU TRÚC FOLDER

```
desktop-app/
├── installers/                              ← TẠO FOLDER NÀY
│   ├── python-3.11.8-amd64.exe             ← DOWNLOAD FILE NÀY
│   └── tesseract-ocr-w64-setup-5.3.3.exe   ← DOWNLOAD FILE NÀY
│
├── check-prerequisites.bat                  ← CHẠY TRƯỚC
├── build-allinone.bat                       ← CHẠY SAU
├── installer.nsi                            ← Auto-used
└── 90dayChonThanh-AllInOne-Setup.exe       ← OUTPUT
```

---

## USER WORKFLOW

User nhận được: `90dayChonThanh-AllInOne-Setup.exe`

User làm:
1. Double-click
2. Click Next, I Agree, Next
3. Đợi 5-10 phút
4. Done!

Không cần cài gì thêm. Tất cả tự động.

---

## STATUS

🟢 Scripts ready
🟢 Documentation ready
🟡 Pending: Windows build
🟡 Pending: VM testing

---

**Sẵn sàng build trên Windows! 🚀**
