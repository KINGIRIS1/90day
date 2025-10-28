# 📦 BUILD CHECKLIST v1.1.0

## ✅ Prerequisites (Kiểm tra trước khi build)

### 1. Software Requirements
- [ ] **Node.js 16+** installed
  - Check: `node --version`
  - Download: https://nodejs.org/
  - ⚠️ IMPORTANT: Chọn "Add to PATH" khi cài đặt

- [ ] **Yarn** installed
  - Check: `yarn --version`
  - Install: `npm install -g yarn`

- [ ] **Python 3.8-3.11** installed
  - Check: `python --version` hoặc `py --version`
  - Download: https://www.python.org/
  - ⚠️ IMPORTANT: Tick "Add Python to PATH"

- [ ] **Git** installed (optional, for version control)
  - Check: `git --version`
  - Download: https://git-scm.com/

- [ ] **NSIS** installed (optional, for .exe installer)
  - Check: `makensis /VERSION`
  - Download: https://nsis.sourceforge.io/Download
  - Note: Electron-builder có thể tự động download

### 2. Disk Space
- [ ] At least **5GB free space** on C: drive
  - node_modules: ~500MB
  - Python packages: ~2GB
  - Build output: ~300MB

### 3. Internet Connection
- [ ] Stable internet for downloading dependencies

---

## 🚀 BUILD PROCESS

### Step 1: Open Command Prompt as Administrator
- Press `Win + X`
- Select "Command Prompt (Admin)" hoặc "PowerShell (Admin)"

### Step 2: Navigate to project folder
```cmd
cd C:\desktop-app
```
(Thay bằng đường dẫn thực tế)

### Step 3: Run build script
```cmd
build-installer.bat
```

### Step 4: Wait for build to complete
⏱️ Expected time: **10-20 minutes** (depending on internet speed)

Progress will show:
1. ✅ Checking prerequisites
2. ✅ Installing Node.js dependencies (2-5 mins)
3. ✅ Installing Python dependencies (5-10 mins)
4. ✅ Building React frontend (2-3 mins)
5. ✅ Building Electron App (1-2 mins)
6. ✅ Creating NSIS Installer (1 min)

---

## 📂 BUILD OUTPUT

### Success indicators:
- [ ] No RED error messages in console
- [ ] `dist\` folder created
- [ ] One of these exists:
  - `dist\90dayChonThanh Setup 1.1.0.exe` (Installer)
  - `dist\win-unpacked\90dayChonThanh.exe` (Portable)

### File sizes (approximate):
- **Installer (.exe)**: ~150-200MB
- **Portable (folder)**: ~250-300MB

---

## 🧪 POST-BUILD TESTING

### Test on BUILD machine:
1. [ ] Run installer: `dist\90dayChonThanh Setup 1.1.0.exe`
2. [ ] Install to default location: `C:\Program Files\90dayChonThanh`
3. [ ] Launch app from desktop shortcut
4. [ ] Test scan với 1 ảnh đơn giản
5. [ ] Check Settings → OCR Engine options
6. [ ] Check About → Version should show "1.1.0"

### Test on CLEAN Windows machine (recommended):
1. [ ] Copy installer to USB/cloud
2. [ ] Install on máy chưa có Python/Node.js
3. [ ] Verify app runs độc lập
4. [ ] Test full workflow:
   - Single scan
   - Batch scan (3-5 images)
   - PDF export
   - Settings changes

---

## 📤 DISTRIBUTION

### Package for users:
1. [ ] Create folder: `90dayChonThanh-v1.1.0-Windows`
2. [ ] Copy files:
   - `90dayChonThanh Setup 1.1.0.exe` (installer)
   - `HUONG_DAN_CAI_DAT_USER.md` (user guide)
   - `CHANGELOG-v1.1.0.md` (changelog)
   - `LICENSE.txt` (if any)

3. [ ] Compress to ZIP: `90dayChonThanh-v1.1.0-Windows.zip`

4. [ ] Upload to:
   - Google Drive (recommended)
   - OneDrive
   - Dropbox
   - Direct download server

5. [ ] Share link with users

---

## ⚠️ COMMON ISSUES & FIXES

### Issue 1: "Node.js not found"
**Fix:** 
- Restart Command Prompt after installing Node.js
- Check PATH: `echo %PATH%`
- Reinstall Node.js with "Add to PATH" option

### Issue 2: "Python not found"
**Fix:**
- Run: `py --version` hoặc `python --version`
- Check PATH: `where python`
- Reinstall Python 3.11 with "Add to PATH" option

### Issue 3: "yarn install" fails
**Fix:**
```cmd
npm cache clean --force
npm install -g yarn
yarn install
```

### Issue 4: "electron-builder" fails
**Fix:**
```cmd
yarn add electron-builder --dev
yarn electron-build
```

### Issue 5: Build completes but no installer
**Fix:**
- Check `dist\win-unpacked\` for portable version
- Install NSIS manually: https://nsis.sourceforge.io/Download
- Run build again

### Issue 6: Installer created but app won't start
**Fix:**
- Check antivirus (may block .exe)
- Run installer as Administrator
- Check Windows Event Viewer for errors

---

## 📊 BUILD LOG

**Date:** _____________
**Built by:** _____________
**Version:** 1.1.0
**Build time:** _______ minutes
**Output size:** _______ MB

**Tested on:**
- [ ] Windows 10
- [ ] Windows 11
- [ ] Clean machine (no Python/Node.js)

**Issues encountered:**
_____________________________________________
_____________________________________________

**Notes:**
_____________________________________________
_____________________________________________

---

## ✅ FINAL CHECKLIST

Before distribution:
- [ ] Installer tested on build machine ✓
- [ ] Installer tested on clean machine ✓
- [ ] All features working (scan, classify, export) ✓
- [ ] Version number correct (1.1.0) ✓
- [ ] User guide included ✓
- [ ] Changelog included ✓
- [ ] Upload complete ✓
- [ ] Download link shared ✓

---

**Build Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Notes:** This is v1.1.0 with Smart Crop, improved timeout (60s), and enhanced classification logic (88-92% accuracy offline).
