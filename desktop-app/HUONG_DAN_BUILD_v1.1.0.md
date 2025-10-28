# 🛠️ HƯỚNG DẪN BUILD INSTALLER v1.1.0

## 🎯 MỤC TIÊU
Build Windows installer (.exe) cho 90dayChonThanh Desktop App v1.1.0

---

## 📋 CHUẨN BỊ (15-30 phút)

### 1. Cài đặt Node.js
1. Download: https://nodejs.org/ (chọn LTS version)
2. Chạy installer
3. ⚠️ **QUAN TRỌNG:** Tick ✅ "Add to PATH"
4. Khởi động lại Command Prompt
5. Kiểm tra: `node --version` (should show v16.x.x or higher)

### 2. Cài đặt Yarn (nếu chưa có)
```cmd
npm install -g yarn
```
Kiểm tra: `yarn --version`

### 3. Kiểm tra Python (đã cài rồi)
```cmd
python --version
```
hoặc
```cmd
py --version
```
Should show: Python 3.11.x ✅

### 4. Cài NSIS (Optional - để tạo .exe installer)
- Download: https://nsis.sourceforge.io/Download
- Chạy installer mặc định
- Kiểm tra: `makensis /VERSION`
- **Note:** Electron-builder có thể tự download nếu cần

---

## 🚀 CÁCH BUILD (10-20 phút)

### PHƯƠNG PHÁP 1: Dùng Script Tự Động (Khuyên dùng ⭐)

#### Bước 1: Mở Command Prompt as Administrator
- Nhấn `Win + X`
- Chọn "Command Prompt (Admin)"

#### Bước 2: Vào thư mục project
```cmd
cd C:\desktop-app
```
(Thay bằng đường dẫn thực tế)

#### Bước 3: Chạy build script
```cmd
build-installer.bat
```

#### Bước 4: Đợi build hoàn thành
⏱️ **Dự kiến:** 10-20 phút

**Quá trình:**
```
[1/6] Checking prerequisites...        (30 seconds)
[2/6] Installing Node.js dependencies... (2-5 minutes)
[3/6] Installing Python dependencies...  (5-10 minutes)
[4/6] Building React frontend...         (2-3 minutes)
[5/6] Building Electron App...           (1-2 minutes)
[6/6] Creating NSIS Installer...         (1 minute)
```

#### Bước 5: Kiểm tra kết quả
```cmd
dir dist\*.exe
```

**Thành công nếu thấy:**
- `dist\90dayChonThanh Setup 1.1.0.exe` (Installer)

---

### PHƯƠNG PHÁP 2: Build Từng Bước (Manual)

#### Step 1: Cài dependencies
```cmd
cd C:\desktop-app
yarn install
```

#### Step 2: Cài Python packages
```cmd
cd python
python -m pip install -r requirements.txt
cd ..
```

#### Step 3: Build React frontend
```cmd
yarn build
```

#### Step 4: Build Electron app + installer
```cmd
yarn electron-build
```

**Output:** `dist\90dayChonThanh Setup 1.1.0.exe`

---

## 📂 OUTPUT FILES

### Sau khi build xong, kiểm tra folder `dist\`:

```
dist/
├── 90dayChonThanh Setup 1.1.0.exe    (Installer - ~150-200MB)
├── win-unpacked/                      (Portable version)
│   └── 90dayChonThanh.exe
└── builder-effective-config.yaml     (Build config)
```

### File sizes:
- **Installer:** ~150-200MB (nén)
- **Portable:** ~250-300MB (giải nén)
- **After install:** ~500MB (bao gồm Python + packages)

---

## 🧪 TEST INSTALLER

### Test 1: Trên máy build (Quick test)
```cmd
dist\90dayChonThanh Setup 1.1.0.exe
```

**Checklist:**
- [ ] Installer chạy được
- [ ] Install thành công vào `C:\Program Files\90dayChonThanh`
- [ ] Desktop shortcut được tạo
- [ ] App khởi động được
- [ ] Scan 1 ảnh test
- [ ] Version hiển thị "1.1.0"

### Test 2: Trên máy sạch (Recommended ⭐)
1. Copy installer sang USB hoặc upload lên Drive
2. Test trên máy Windows **CHƯA CÓ** Python/Node.js
3. Install và test đầy đủ:
   - Single scan
   - Batch scan (5 ảnh)
   - Different OCR engines (Tesseract, EasyOCR)
   - PDF export
   - Settings

---

## 📤 PACKAGE VÀ CHIA SẺ

### Bước 1: Tạo package
1. Tạo folder: `90dayChonThanh-v1.1.0-Windows`
2. Copy vào:
   ```
   90dayChonThanh-v1.1.0-Windows/
   ├── 90dayChonThanh Setup 1.1.0.exe
   ├── HUONG_DAN_CAI_DAT_USER.md
   ├── CHANGELOG-v1.1.0.md
   └── LICENSE.txt (if any)
   ```

3. Nén thành ZIP: `90dayChonThanh-v1.1.0-Windows.zip`

### Bước 2: Upload
**Recommended:** Google Drive
1. Upload ZIP file
2. Tạo shareable link
3. Test download

**Alternatives:**
- OneDrive
- Dropbox
- WeTransfer
- Direct server

### Bước 3: Share
Gửi link kèm:
- Version: 1.1.0
- OS: Windows 10/11 64-bit
- Size: ~XXX MB
- What's new: Smart Crop, 60s timeout, improved classification

---

## ⚠️ TROUBLESHOOTING

### ❌ Error: "Node.js not found"
**Fix:**
1. Cài lại Node.js từ https://nodejs.org/
2. ✅ Tick "Add to PATH"
3. Restart Command Prompt
4. Test: `node --version`

### ❌ Error: "yarn: command not found"
**Fix:**
```cmd
npm install -g yarn
```

### ❌ Error: "Python not found"
**Fix:**
1. Check: `python --version` và `py --version`
2. Nếu không có: Cài lại Python 3.11
3. ✅ Tick "Add Python to PATH"

### ❌ Error: "Cannot find module '@babel/...'"
**Fix:**
```cmd
rd /s /q node_modules
yarn install
```

### ❌ Error: "electron-builder: command not found"
**Fix:**
```cmd
yarn add electron-builder --dev
```

### ❌ Build completes nhưng KHÔNG có installer
**Possible causes:**
1. NSIS không cài → Install NSIS manually
2. Chỉ có portable version → Check `dist\win-unpacked\`
3. Build failed midway → Xem logs chi tiết

**Fix:**
```cmd
REM Clean build
rd /s /q dist build
yarn build
yarn electron-build
```

### ❌ Installer tạo được nhưng app không chạy
**Fix:**
1. Run installer as Administrator
2. Disable antivirus temporarily
3. Check Windows Event Viewer:
   - `Win + X` → Event Viewer
   - Windows Logs → Application
   - Look for 90dayChonThanh errors

### ❌ "Out of memory" during build
**Fix:**
1. Close other apps
2. Increase Node.js memory:
```cmd
set NODE_OPTIONS=--max_old_space_size=4096
yarn electron-build
```

---

## 💡 TIPS & BEST PRACTICES

### ✅ DO:
- Build trên máy có internet ổn định
- Khởi động lại CMD sau khi cài tools mới
- Test installer trên máy sạch
- Backup installer sau khi build xong
- Ghi log build time và issues

### ❌ DON'T:
- Đừng ngắt mạng giữa chừng
- Đừng close terminal khi đang build
- Đừng modify files trong lúc build
- Đừng dùng Windows 7 (not supported)

### 🚀 Performance Tips:
- Dùng SSD (nhanh hơn HDD rất nhiều)
- Close antivirus tạm thời (tăng tốc)
- Có ít nhất 8GB RAM
- Internet >= 10Mbps

---

## 📊 BUILD TIME ESTIMATE

| Component | Time | Note |
|-----------|------|------|
| Prerequisites check | 30s | |
| Node dependencies | 2-5 min | First time longer |
| Python packages | 5-10 min | EasyOCR là lớn nhất |
| React build | 2-3 min | |
| Electron build | 1-2 min | |
| NSIS installer | 1 min | |
| **TOTAL** | **10-20 min** | Tùy máy và mạng |

---

## 📞 CẦN HỖ TRỢ?

**Stuck?** Gửi:
1. Screenshot error message
2. Build logs (copy toàn bộ output)
3. Máy specs (Windows version, RAM, CPU)
4. Bước nào bị lỗi

**Files cần tham khảo:**
- `BUILD_CHECKLIST_v1.1.0.md` - Checklist chi tiết
- `CHANGELOG-v1.1.0.md` - Những gì thay đổi
- `TEST_GUIDE_v1.1.0.md` - Hướng dẫn test

---

## ✅ COMPLETED CHECKLIST

- [ ] Node.js installed
- [ ] Yarn installed
- [ ] Python verified
- [ ] NSIS installed (optional)
- [ ] Build script executed
- [ ] Installer created in `dist\`
- [ ] Tested on build machine
- [ ] Tested on clean machine
- [ ] Packaged for distribution
- [ ] Uploaded to cloud
- [ ] Link shared

---

**🎉 Chúc build thành công!**

Build Date: _____________
Built by: _____________
Issues encountered: _____________
