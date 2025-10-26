# 🚀 Hướng Dẫn Cài Đặt Nhanh

## Cho Người Dùng (Windows)

### Bước 1: Download

Tải 2 files sau:

1. **App installer:** `90dayChonThanh-Setup-1.0.0.exe` (~150MB)
2. **Tesseract OCR:** [Download tại đây](https://github.com/UB-Mannheim/tesseract/wiki)

### Bước 2: Cài Tesseract

1. Chạy file `tesseract-ocr-w64-setup-xxx.exe`
2. **QUAN TRỌNG:** Tick vào "Vietnamese language pack"
3. Next → Next → Install
4. ✅ Xong!

### Bước 3: Cài App

1. Chạy `90dayChonThanh-Setup-1.0.0.exe`
2. Next → Next → Install
3. ✅ Xong!

### Bước 4: Chạy App

- Desktop: Double click icon "90dayChonThanh"
- Hoặc: Start Menu → 90dayChonThanh

---

## 💻 Cho Developer/IT

### Build từ Source

```bash
# 1. Requirements
- Node.js 16+
- Yarn
- Python 3.8+

# 2. Clone/Copy folder desktop-app
cd desktop-app

# 3. Install dependencies
yarn install

# 4. Build
# Windows:
build.bat

# macOS/Linux:
./build.sh

# 5. Output
# dist/90dayChonThanh-Setup-1.0.0.exe
```

### Deploy tới nhiều máy

**Cách 1: Manual**
1. Copy file .exe lên network share
2. User chạy setup từ đó

**Cách 2: Silent Install**
```batch
REM Cài đặt im lặng (không popup)
90dayChonThanh-Setup-1.0.0.exe /S

REM Uninstall
"%ProgramFiles%\90dayChonThanh\Uninstall.exe" /S
```

**Cách 3: Group Policy (Windows Domain)**
1. Copy .exe vào SYSVOL
2. Create GPO → Software Installation
3. Assign to computers/users

---

## 🔧 Xử Lý Lỗi

### Lỗi: "Python not found"

**Giải pháp:**
1. Cài Python từ python.org
2. Tick "Add Python to PATH"
3. Restart app

### Lỗi: "Tesseract not found"

**Giải pháp:**
1. Cài Tesseract (xem Bước 2 ở trên)
2. Verify: Mở CMD, gõ `tesseract --version`
3. Nếu vẫn lỗi: Thêm Tesseract vào PATH

**Thêm vào PATH:**
```
Control Panel → System → Advanced → Environment Variables
→ Path → Edit → New
→ Thêm: C:\Program Files\Tesseract-OCR
→ OK
```

### Lỗi: "Cloud Boost không hoạt động"

**Giải pháp:**
1. Kiểm tra internet
2. Mở Settings → Kiểm tra Backend URL
3. Default: backend server cần running

---

## 📦 Files Cần Distribute

**Minimum (cho user):**
- `90dayChonThanh-Setup-1.0.0.exe` (installer)
- Link tải Tesseract
- File hướng dẫn này

**Portable version (không cần install):**
- `90dayChonThanh-Portable-Win.zip`
- Giải nén → Chạy `90dayChonThanh.exe`
- Vẫn cần Tesseract

**Complete package (all-in-one):**
- Tạo folder chứa:
  - App installer
  - Tesseract installer
  - Hướng dẫn (README.txt)
  - Auto-install script (optional)

---

## 🌐 Distribution Channels

### Option 1: Google Drive
```
1. Upload installer lên Drive
2. Set quyền "Anyone with link can view"
3. Share link cho users
```

### Option 2: GitHub Releases
```
1. Create new release on GitHub
2. Upload installers as assets
3. Users download từ Releases page
```

### Option 3: Website
```
1. Host file trên web server
2. Tạo download page
3. Link: yourwebsite.com/downloads
```

### Option 4: USB/Network Share
```
1. Copy installer vào USB/network folder
2. Users copy và chạy
3. Good cho offline deployment
```

---

## ✅ Pre-Distribution Checklist

**Trước khi phân phối:**

- [ ] Test installer trên Windows clean (VM hoặc máy mới)
- [ ] Verify app mở được
- [ ] Test quét offline (cần có Tesseract)
- [ ] Test quét cloud (nếu có backend)
- [ ] Test Rules Manager
- [ ] Check file size hợp lý (~150MB)
- [ ] Tạo SHA256 checksum cho installer
- [ ] Prepare user guide (file này)

**Checksum (cho security):**
```bash
# Windows (PowerShell)
Get-FileHash 90dayChonThanh-Setup-1.0.0.exe -Algorithm SHA256

# Linux/Mac
shasum -a 256 90dayChonThanh-Setup-1.0.0.exe
```

---

## 📱 Support

**User gặp vấn đề?**

1. Check logs:
   - Windows: `%APPDATA%\90dayChonThanh\logs\`
   - Copy file log mới nhất

2. Common issues:
   - Tesseract not found → Cài Tesseract
   - Python not found → Cài Python
   - Cloud không work → Check internet + backend

3. Report bug:
   - Describe issue
   - Attach log file
   - Screenshot (if UI issue)

---

## 🎉 That's It!

**User chỉ cần:**
1. Cài Tesseract (1 lần)
2. Cài App (1 lần)
3. Chạy và dùng!

**Developer chỉ cần:**
1. Run `build.bat` (Windows) hoặc `build.sh` (Mac/Linux)
2. Upload file trong `dist/` folder
3. Share link với users!

---

**💡 Tip:** Tạo folder "90dayChonThanh-Package" chứa:
- Installer
- Tesseract link
- README (file này)
- ZIP thành 1 file → Easy distribution!
