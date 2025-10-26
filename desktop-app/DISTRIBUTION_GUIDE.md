# 📦 Hướng Dẫn Cài Đặt & Phân Phối

## 🎯 Mục tiêu

Cài đặt app **90dayChonThanh** trên các máy khác một cách **ĐƠN GIẢN NHẤT**, không cần kiến thức lập trình.

---

## 🚀 Phương án 1: Cài đặt từ File Setup (KHUYẾN NGHỊ)

### Cho người dùng cuối (End Users)

#### Windows

**Bước 1: Download file installer**
- File: `90dayChonThanh-Setup-1.0.0.exe` (~150MB)
- Double click file → Next → Next → Install

**Bước 2: Cài đặt Tesseract OCR**
1. Download từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Chọn phiên bản mới nhất (ví dụ: `tesseract-ocr-w64-setup-5.3.3.exe`)
3. Khi cài đặt, **NHỚ CHỌN "Vietnamese language pack"**
4. Tick vào checkbox "Add to PATH"

**Bước 3: Chạy app**
- Desktop icon: "90dayChonThanh"
- Hoặc Start Menu → 90dayChonThanh

**Xong! ✅**

---

#### macOS

**Bước 1: Download file installer**
- File: `90dayChonThanh-1.0.0.dmg` (~120MB)
- Double click → Drag app vào Applications folder

**Bước 2: Cài đặt Tesseract**
```bash
# Mở Terminal, chạy lệnh:
brew install tesseract tesseract-lang
```

**Bước 3: Chạy app**
- Applications → 90dayChonThanh
- Lần đầu có thể cần: Right click → Open (do unsigned app)

**Xong! ✅**

---

#### Linux

**Bước 1: Download file**
- File: `90dayChonThanh-1.0.0.AppImage` (~130MB)
- Hoặc: `90dayChonThanh-1.0.0.deb` (Ubuntu/Debian)

**Bước 2: Cài đặt Tesseract**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-vie python3

# Fedora
sudo dnf install tesseract tesseract-langpack-vie python3

# Arch
sudo pacman -S tesseract tesseract-data-vie python
```

**Bước 3: Chạy app**
```bash
# AppImage
chmod +x 90dayChonThanh-1.0.0.AppImage
./90dayChonThanh-1.0.0.AppImage

# hoặc .deb
sudo dpkg -i 90dayChonThanh-1.0.0.deb
```

**Xong! ✅**

---

## 🏗️ Phương án 2: Build từ Source (Cho Dev)

### Requirements

- Node.js 16+ và Yarn
- Python 3.8+
- Git

### Build Steps

```bash
# 1. Clone repo (hoặc copy folder desktop-app)
cd desktop-app

# 2. Install dependencies
yarn install

# 3. Build React app
yarn build

# 4. Build installer cho platform hiện tại
yarn electron-build

# Output:
# - Windows: dist/90dayChonThanh Setup 1.0.0.exe
# - macOS: dist/90dayChonThanh-1.0.0.dmg
# - Linux: dist/90dayChonThanh-1.0.0.AppImage
```

### Build cho nhiều platforms (trên máy dev)

```bash
# Build tất cả (cần tools cho mỗi platform)
yarn electron-build --win --mac --linux

# Chỉ Windows
yarn electron-build --win

# Chỉ macOS
yarn electron-build --mac

# Chỉ Linux
yarn electron-build --linux
```

---

## 📁 Phương án 3: Portable Version (Không cần install)

### Tạo Portable Package

```bash
# Build unpacked version
yarn electron-pack

# Output: dist/win-unpacked/ (hoặc mac, linux)
```

### Phân phối Portable

**Bước 1:** Zip folder `win-unpacked` → `90dayChonThanh-Portable.zip`

**Bước 2:** User giải nén và chạy:
- Windows: `90dayChonThanh.exe`
- macOS: `90dayChonThanh.app`
- Linux: `90dayChonThanh`

**Lưu ý:** Vẫn cần cài Tesseract riêng.

---

## 🎁 Phương án 4: All-in-One Package (EASIEST)

### Bao gồm cả Tesseract trong installer

#### Windows - Tạo Custom Installer với NSIS

**File: `installer.nsi`**
```nsis
; Include Tesseract installer
Section "Install Tesseract OCR"
  File "tesseract-installer.exe"
  ExecWait "$INSTDIR\tesseract-installer.exe /S /L vie"
  Delete "$INSTDIR\tesseract-installer.exe"
SectionEnd
```

#### macOS - Bundle với Homebrew script

**File: `post-install.sh`**
```bash
#!/bin/bash
# Check if Tesseract installed
if ! command -v tesseract &> /dev/null; then
  echo "Installing Tesseract..."
  brew install tesseract tesseract-lang
fi
```

---

## 📝 Checklist cho Developer

### Trước khi Build

- [ ] Update version trong `package.json`
- [ ] Test app thoroughly (offline + cloud modes)
- [ ] Verify Python scripts work with bundled Python
- [ ] Check icon files exist:
  - `assets/icon.png` (Windows/Linux)
  - `assets/icon.icns` (macOS)
- [ ] Update CHANGELOG.md

### Build Process

- [ ] Run `yarn build` (build React)
- [ ] Run `yarn electron-build` (package app)
- [ ] Test installer trên máy clean (không có dependencies)
- [ ] Verify app runs without errors
- [ ] Test Tesseract integration

### Distribution

- [ ] Upload installer files lên server/GitHub Releases
- [ ] Tạo hướng dẫn cài đặt cho user (README)
- [ ] Share download links
- [ ] Provide checksums (SHA256) cho security

---

## 🔧 Troubleshooting

### App không chạy

**Windows:**
```
Error: Python not found
→ Solution: Cài Python 3.8+ từ python.org
          Tick "Add Python to PATH"
```

**macOS:**
```
Error: App is damaged and can't be opened
→ Solution: xattr -cr /Applications/90dayChonThanh.app
```

### Tesseract không hoạt động

```
Error: Tesseract not found
→ Solution: Cài Tesseract theo hướng dẫn ở trên
          Verify: tesseract --version
```

### Cloud Boost không hoạt động

```
Error: Network error
→ Solution: Kiểm tra internet connection
          Kiểm tra Backend URL trong Settings
```

---

## 📊 File Sizes (Estimated)

| Platform | Installer | Unpacked |
|----------|-----------|----------|
| Windows  | ~150MB    | ~220MB   |
| macOS    | ~120MB    | ~180MB   |
| Linux    | ~130MB    | ~200MB   |

**Lưu ý:** Size lớn vì bao gồm:
- Electron framework (~100MB)
- Node modules (~50MB)
- Python scripts + dependencies (~30MB)
- React build (~20MB)

---

## 🚢 Auto-Update (Optional - Advanced)

Để app tự động update, cần setup:

1. **Update server** (GitHub Releases hoặc custom)
2. **electron-updater** trong code
3. **Signed builds** (code signing certificate)

Tham khảo: https://www.electron.build/auto-update

---

## 💡 Tips cho Easy Distribution

### 1. Google Drive / Dropbox
```
Upload installer → Share link → User download & install
Pros: Đơn giản nhất
Cons: Cần reupload khi có version mới
```

### 2. GitHub Releases
```
Create release → Upload installers → Users download from Releases page
Pros: Free, có version history
Cons: Cần GitHub account
```

### 3. Website
```
Host installer trên website riêng
Pros: Professional, easy to find
Cons: Cần hosting
```

---

## ✅ Recommended Workflow

**Cho người dùng thông thường:**
1. Download installer file
2. Cài Tesseract OCR
3. Chạy app
4. Done!

**Cho IT Admin (deploy nhiều máy):**
1. Build All-in-One installer (bao gồm Tesseract)
2. Deploy qua network share hoặc GPO
3. Silent install: `Setup.exe /S`

---

## 📞 Support

**Nếu gặp lỗi khi cài đặt:**
1. Check `TROUBLESHOOTING.md`
2. Check logs: 
   - Windows: `%APPDATA%\90dayChonThanh\logs\`
   - macOS: `~/Library/Logs/90dayChonThanh/`
   - Linux: `~/.config/90dayChonThanh/logs/`

---

**🎉 Happy Distributing!**
