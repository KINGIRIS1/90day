# 🚀 Hướng Dẫn Build Installer One-Click

## Thông Tin App
- **Tên**: 90dayChonThanh
- **Công ty**: Nguyen Thin Trung
- **Version**: 1.1.0
- **Platform**: Windows x64
- **Installer**: NSIS (All-in-one)

---

## 📋 Yêu Cầu Trước Khi Build

### 1. **Node.js & Yarn**
```bash
# Kiểm tra đã cài chưa
node --version   # Cần >= v16
yarn --version   # Cần >= 1.22
```
**Tải về:**
- Node.js: https://nodejs.org/ (LTS version)
- Yarn: `npm install -g yarn`

---

### 2. **NSIS (Nullsoft Scriptable Install System)**
```bash
# Kiểm tra đã cài chưa
makensis /VERSION
```
**Tải về:**
- NSIS: https://nsis.sourceforge.io/Download
- Tải file: **nsis-3.xx-setup.exe**
- Cài đặt và đảm bảo NSIS có trong PATH

**Kiểm tra PATH:**
```powershell
# Mở PowerShell và chạy:
$env:PATH -split ';' | Select-String "NSIS"
```

---

### 3. **Python 3.10 - 3.12**
```bash
# Kiểm tra đã cài chưa
python --version   # hoặc
py --version
```
**Yêu cầu:**
- Python version: **3.10, 3.11 hoặc 3.12**
- Python phải có trong PATH
- Đề xuất dùng `py launcher` (tự động cài khi cài Python)

**Tải về:**
- Python: https://www.python.org/downloads/
- Chọn "Add Python to PATH" khi cài

**Cài thư viện cần thiết:**
```bash
pip install Pillow requests
```

---

## 🛠️ Các Bước Build

### **Bước 1: Chuẩn Bị Project**

```bash
# Di chuyển vào thư mục project
cd C:\desktop-app

# Cài dependencies
yarn install
```

**Output mong đợi:**
```
✔ Done in 45.32s
```

---

### **Bước 2: Clean Python Vendor**

**Lý do:** Xóa các thư viện Python cũ trong local để tránh conflict

```powershell
# Chạy script clean (PowerShell)
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1
```

**Hoặc thủ công:**
```powershell
Remove-Item -Recurse -Force .\python\Lib -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\python\PIL -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\python\requests -ErrorAction SilentlyContinue
```

---

### **Bước 3: Build React App**

```bash
yarn build
```

**Output mong đợi:**
```
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  152.45 KB  build/static/js/main.xxxxxxxx.js
  ...
```

**Kiểm tra:** Thư mục `build/` đã được tạo

---

### **Bước 4: Build Windows Installer**

```bash
yarn dist:win
```

**Quá trình build:**
```
• electron-builder  version=24.x.x
• loaded configuration  file=package.json
• description is missed in the package.json  appPackageFile=C:\desktop-app\package.json
• author is missed in the package.json  appPackageFile=C:\desktop-app\package.json
• writing effective config  file=dist\builder-effective-config.yaml
• packaging       platform=win32 arch=x64 electron=28.x.x appOutDir=dist\win-unpacked
• building        target=nsis file=dist\90dayChonThanh Setup 1.1.0.exe archs=x64 oneClick=true perMachine=false
• building block map  blockMapFile=dist\90dayChonThanh Setup 1.1.0.exe.blockmap
```

**Thời gian:** ~2-5 phút (tùy máy)

---

### **Bước 5: Kiểm Tra Installer**

**File installer được tạo:**
```
C:\desktop-app\dist\90dayChonThanh Setup 1.1.0.exe
```

**Kích thước:** ~150-250 MB

**Các file khác trong dist/:**
- `90dayChonThanh Setup 1.1.0.exe` ← **Installer chính**
- `90dayChonThanh Setup 1.1.0.exe.blockmap` ← Metadata
- `win-unpacked/` ← Unpacked version (test)
- `builder-effective-config.yaml` ← Build config

---

## ✅ Test Installer

### **Test 1: Cài Đặt**

1. **Double-click** file `90dayChonThanh Setup 1.1.0.exe`
2. Installer sẽ tự động cài đặt vào:
   ```
   C:\Users\[TÊN_BẠN]\AppData\Local\Programs\90dayChonThanh\
   ```
3. Desktop shortcut sẽ được tạo (nếu có config)
4. Start Menu shortcut được tạo

---

### **Test 2: Chạy App**

```bash
# Chạy từ shortcut hoặc:
"%LocalAppData%\Programs\90dayChonThanh\90dayChonThanh.exe"
```

**Kiểm tra:**
- ✅ App mở được
- ✅ UI hiển thị đúng
- ✅ Quét file hoạt động
- ✅ Python OCR hoạt động
- ✅ Settings lưu được

---

### **Test 3: Chạy Với Logs (Debug)**

```powershell
# Set logging
set ELECTRON_ENABLE_LOGGING=1

# Chạy với logs
"%LocalAppData%\Programs\90dayChonThanh\90dayChonThanh.exe" --enable-logging
```

**Logs sẽ hiển thị trong console**

---

## 🐛 Xử Lý Lỗi Thường Gặp

### **Lỗi 1: "NSIS not found"**

**Lỗi:**
```
Error: NSIS not found
```

**Giải pháp:**
1. Cài NSIS: https://nsis.sourceforge.io/Download
2. Thêm NSIS vào PATH:
   ```powershell
   # Thêm vào System Environment Variables:
   C:\Program Files (x86)\NSIS
   ```
3. Restart terminal và chạy lại

---

### **Lỗi 2: "Python not found"**

**Lỗi:**
```
Error: spawn python ENOENT
```

**Giải pháp:**
1. Cài Python 3.10-3.12
2. Kiểm tra PATH:
   ```bash
   python --version
   ```
3. Nếu không có, thêm vào PATH:
   ```
   C:\Users\[USER]\AppData\Local\Programs\Python\Python312\
   C:\Users\[USER]\AppData\Local\Programs\Python\Python312\Scripts\
   ```

---

### **Lỗi 3: "ImportError: PIL._imaging"**

**Lỗi:**
```python
ImportError: DLL load failed while importing _imaging: The specified module could not be found.
```

**Giải pháp:**
1. Clean local python:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1
   ```
2. Cài Pillow trong system Python:
   ```bash
   pip install Pillow
   ```
3. Build lại:
   ```bash
   yarn dist:win
   ```

---

### **Lỗi 4: "EPERM: operation not permitted"**

**Lỗi:**
```
Error: EPERM: operation not permitted, unlink 'dist\...'
```

**Giải pháp:**
1. Đóng app nếu đang chạy
2. Xóa thư mục `dist/`:
   ```bash
   rmdir /s /q dist
   ```
3. Build lại

---

### **Lỗi 5: "Out of memory"**

**Lỗi:**
```
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed
```

**Giải pháp:**
1. Tăng memory cho Node.js:
   ```bash
   set NODE_OPTIONS=--max_old_space_size=4096
   yarn dist:win
   ```
2. Hoặc close các app khác để giải phóng RAM

---

## 📦 Tùy Chỉnh Installer

### **Thay Đổi Icon**

File: `assets/icon.ico`

**Yêu cầu:**
- Format: .ico
- Size: 256x256 recommended
- Có thể dùng tool convert: https://convertio.co/png-ico/

---

### **Thay Đổi Banner/Sidebar**

Chưa có config sẵn, có thể thêm trong `package.json`:

```json
"win": {
  "target": "nsis",
  "icon": "assets/icon.ico"
}
```

---

### **Custom NSIS Script**

File: `assets/installer.nsh`

**Ví dụ thêm custom page:**
```nsis
!macro customHeader
  !insertmacro MUI_PAGE_WELCOME
!macroend
```

---

## 🚀 Build Script Nhanh (One Command)

Tạo file `build.bat`:

```batch
@echo off
echo ========================================
echo  BUILD 90dayChonThanh INSTALLER
echo ========================================
echo.

echo [1/4] Cleaning Python vendor...
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1

echo.
echo [2/4] Installing dependencies...
call yarn install

echo.
echo [3/4] Building React app...
call yarn build

echo.
echo [4/4] Building Windows installer...
call yarn dist:win

echo.
echo ========================================
echo  BUILD COMPLETE!
echo ========================================
echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
pause
```

**Sử dụng:**
```bash
build.bat
```

---

## 📤 Phân Phối Installer

### **Option 1: Direct Download**
- Upload file .exe lên Google Drive / Dropbox / OneDrive
- Share link cho user

### **Option 2: Website**
- Upload lên website hosting
- Link download: `https://your-site.com/downloads/90dayChonThanh-Setup-1.1.0.exe`

### **Option 3: GitHub Releases**
- Push code lên GitHub
- Tạo Release với file .exe đính kèm
- User download từ Releases page

---

## 🔒 Code Signing (Tùy Chọn)

**Tại sao cần:**
- Windows SmartScreen sẽ không cảnh báo
- User tin tưởng hơn
- Professional hơn

**Yêu cầu:**
- Code signing certificate (~$100-300/year)
- Từ: DigiCert, Sectigo, GlobalSign

**Config trong package.json:**
```json
"win": {
  "certificateFile": "certs/cert.pfx",
  "certificatePassword": "YOUR_PASSWORD",
  "signDlls": true
}
```

---

## 📊 Checklist Build

- [ ] Node.js & Yarn đã cài
- [ ] NSIS đã cài và trong PATH
- [ ] Python 3.10-3.12 đã cài
- [ ] Pillow và requests đã cài trong system Python
- [ ] `yarn install` thành công
- [ ] Clean Python vendor (chạy script)
- [ ] `yarn build` thành công
- [ ] `yarn dist:win` thành công
- [ ] File .exe được tạo trong `dist/`
- [ ] Test cài đặt trên máy sạch
- [ ] Test tất cả features hoạt động

---

## 🎯 Tổng Kết

**Lệnh build nhanh nhất:**
```bash
cd C:\desktop-app
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1
yarn install
yarn build
yarn dist:win
```

**Kết quả:**
```
C:\desktop-app\dist\90dayChonThanh Setup 1.1.0.exe
```

**Size:** ~150-250 MB
**Type:** NSIS one-click installer
**Target:** Windows x64

---

## 📞 Support

**Nếu gặp vấn đề:**
1. Kiểm tra logs trong console
2. Đảm bảo tất cả prerequisites đã cài
3. Thử clean build:
   ```bash
   rmdir /s /q node_modules
   rmdir /s /q dist
   rmdir /s /q build
   yarn install
   yarn dist:win
   ```

**Contact:**
- Email: contact@90daychonthanh.vn
- Website: www.90daychonthanh.vn

---

**Version**: 1.1.0
**Last Updated**: 2025
**Platform**: Windows x64
