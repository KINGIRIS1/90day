# ✅ All-in-One Installer Build Checklist

Quick reference checklist for building the all-in-one installer.

---

## 📋 Pre-Build Checklist

### System Requirements

- [ ] Windows 10/11 (64-bit)
- [ ] Node.js 16+ installed
- [ ] Yarn installed
- [ ] Python 3.x installed (for testing)
- [ ] Git (optional, for version control)

### Required Software

- [ ] **NSIS Installed**
  - Download: https://nsis.sourceforge.io/Download
  - Install location: `C:\Program Files (x86)\NSIS\`
  - Verify: `makensis.exe` exists

### Required Files

- [ ] **Python Installer Downloaded**
  - File: `python-3.11.8-amd64.exe`
  - Size: ~30 MB
  - URL: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
  - Location: `desktop-app/installers/`

- [ ] **Tesseract Installer Downloaded**
  - File: `tesseract-ocr-w64-setup-5.3.3.exe`
  - Size: ~50 MB
  - URL: https://github.com/UB-Mannheim/tesseract/wiki
  - Location: `desktop-app/installers/`

### Project Files

- [ ] `installer.nsi` exists and configured
- [ ] `build-allinone.bat` exists
- [ ] `LICENSE.txt` exists (or will be auto-created)
- [ ] `assets/icon.ico` exists (or use default)

---

## 🛠️ Build Process Checklist

### Step 1: Prepare Environment

```batch
cd desktop-app
```

- [ ] Navigate to desktop-app directory
- [ ] Open command prompt as Administrator (recommended)

### Step 2: Verify Prerequisites

```batch
# Check NSIS
dir "C:\Program Files (x86)\NSIS\makensis.exe"

# Check installers
dir installers\python-3.11.8-amd64.exe
dir installers\tesseract-ocr-w64-setup-5.3.3.exe

# Check Node & Yarn
node --version
yarn --version
```

- [ ] NSIS found
- [ ] Python installer found
- [ ] Tesseract installer found
- [ ] Node.js working
- [ ] Yarn working

### Step 3: Install Dependencies

```batch
yarn install
```

- [ ] All npm packages installed
- [ ] No error messages

### Step 4: Run Build Script

```batch
build-allinone.bat
```

**Script will:**
- [ ] Check NSIS installation
- [ ] Verify Python installer
- [ ] Verify Tesseract installer
- [ ] Build React app (`yarn build`)
- [ ] Build Electron app (`yarn electron-pack`)
- [ ] Create NSIS installer

**Expected output:**
```
[1/5] Checking NSIS... [OK]
[2/5] Checking Python installer... [OK]
[3/5] Checking Tesseract installer... [OK]
[4/5] Building Electron app... [OK]
[5/5] Building NSIS installer... [OK]

BUILD COMPLETE!
Output file: 90dayChonThanh-AllInOne-Setup.exe
```

### Step 5: Verify Output

- [ ] File exists: `90dayChonThanh-AllInOne-Setup.exe`
- [ ] File size: ~235 MB (varies)
- [ ] No error messages in console

---

## 🧪 Testing Checklist

### Pre-Release Testing

- [ ] **Test on Clean VM**
  - [ ] Create Windows VM (VirtualBox, VMware, Hyper-V)
  - [ ] Fresh Windows 10/11 install
  - [ ] No Python installed
  - [ ] No Tesseract installed

- [ ] **Run Installer**
  - [ ] Copy `.exe` to VM
  - [ ] Run as Administrator
  - [ ] No errors during installation
  - [ ] All components installed silently

- [ ] **Verify Installation**
  - [ ] Desktop shortcut created
  - [ ] Start menu entry exists
  - [ ] Python installed: `python --version`
  - [ ] Tesseract installed: `tesseract --version`
  - [ ] App launches successfully

- [ ] **Test App Functionality**
  - [ ] App opens without errors
  - [ ] Offline OCR works
  - [ ] File picker works
  - [ ] Folder picker works
  - [ ] Results display correctly
  - [ ] Save functionality works

- [ ] **Test OCR Quality**
  - [ ] Test with 5-10 Vietnamese documents
  - [ ] Verify classification accuracy
  - [ ] Check text extraction quality
  - [ ] Verify short codes generated correctly

- [ ] **Test Rules Manager**
  - [ ] Rules tab accessible
  - [ ] Can view existing rules
  - [ ] Can add new rule
  - [ ] Can edit rule
  - [ ] Can delete rule
  - [ ] Can export rules
  - [ ] Can import rules

- [ ] **Test Uninstaller**
  - [ ] Uninstall from Control Panel
  - [ ] App removed successfully
  - [ ] Shortcuts removed
  - [ ] Python/Tesseract remain (expected)

---

## 📦 Distribution Checklist

### Prepare Distribution Package

- [ ] **Create Distribution Folder**
  ```
  90dayChonThanh-v1.0.0/
  ├── 90dayChonThanh-AllInOne-Setup.exe
  ├── README.txt
  └── HUONG_DAN_CAI_DAT.txt
  ```

- [ ] **Create README.txt** (Simple instructions)
  ```
  90dayChonThanh Desktop App v1.0.0
  
  Installation:
  1. Run: 90dayChonThanh-AllInOne-Setup.exe
  2. Wait 5-10 minutes
  3. Done! Desktop icon will appear
  
  Includes:
  - Python 3.11
  - Tesseract OCR (Vietnamese)
  - 90dayChonThanh App
  ```

- [ ] **Create Vietnamese Guide** (HUONG_DAN_CAI_DAT.txt)

### Upload & Share

- [ ] **Choose distribution method:**
  - [ ] Google Drive / Dropbox
  - [ ] Company file server
  - [ ] WeTransfer / File sharing service
  - [ ] Direct USB drive
  - [ ] Company intranet

- [ ] **Create download link**
- [ ] **Test download link**
- [ ] **Verify file integrity after download**

### Documentation

- [ ] **Update changelog**
- [ ] **Document known issues**
- [ ] **Create release notes**
- [ ] **Update version number**

---

## 🐛 Troubleshooting Checklist

### Build Errors

**Error: "NSIS not found"**
- [ ] Install NSIS from official website
- [ ] Restart command prompt
- [ ] Check installation path

**Error: "Python installer not found"**
- [ ] Download Python installer
- [ ] Place in `installers/` folder
- [ ] Check exact filename matches

**Error: "Tesseract installer not found"**
- [ ] Download Tesseract installer
- [ ] Place in `installers/` folder
- [ ] Rename to exact filename

**Error: "yarn build failed"**
- [ ] Delete `node_modules/`
- [ ] Run `yarn install` again
- [ ] Check for dependency conflicts

**Error: "electron-pack failed"**
- [ ] Check `package.json` configuration
- [ ] Verify `electron-builder` installed
- [ ] Check disk space

### Runtime Errors

**Error: "Python not found" after install**
- [ ] Restart computer
- [ ] Check PATH environment variable
- [ ] Reinstall app

**Error: "Tesseract not found" after install**
- [ ] Check `C:\Program Files\Tesseract-OCR\`
- [ ] Manually add to PATH
- [ ] Reinstall Tesseract

**Error: "OCR not working"**
- [ ] Verify image format (JPG, PNG)
- [ ] Check image quality
- [ ] Test with sample image
- [ ] Check error logs

---

## 📊 Performance Checklist

### Installer Performance

- [ ] Install time: 5-10 minutes
- [ ] File size: 230-250 MB
- [ ] Disk space required: 500 MB+
- [ ] Memory usage during install: < 1 GB
- [ ] No crashes during install

### App Performance

- [ ] App startup: < 3 seconds
- [ ] OCR processing: 1-2 seconds per image (offline)
- [ ] Memory usage: < 500 MB
- [ ] CPU usage: < 50% during processing
- [ ] Responsive UI (no freezing)

---

## 🔄 Update Checklist

### For Future Updates

When updating to new version:

- [ ] Update version in `package.json`
- [ ] Update version in `installer.nsi`
- [ ] Update changelog
- [ ] Test new features
- [ ] Rebuild installer
- [ ] Test on clean VM
- [ ] Document changes
- [ ] Update user guide

### Version Compatibility

- [ ] Backward compatible with old rules
- [ ] Settings migrate automatically
- [ ] Data preserved during update
- [ ] Can uninstall old version first

---

## 📝 Sign-Off Checklist

Before releasing to users:

- [ ] All tests passed
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] User guide updated
- [ ] Support channels ready
- [ ] Backup plan ready
- [ ] Rollback plan documented

### Final Approval

- [ ] Developer sign-off
- [ ] QA sign-off
- [ ] Product owner sign-off
- [ ] Ready for distribution

---

## 🎯 Quick Start (TL;DR)

For experienced developers:

```batch
# 1. Prepare
cd desktop-app
mkdir installers

# 2. Download
# - python-3.11.8-amd64.exe → installers/
# - tesseract-ocr-w64-setup-5.3.3.exe → installers/

# 3. Build
build-allinone.bat

# 4. Test
# Run on clean VM

# 5. Distribute
# Upload and share
```

---

## 📞 Support

If stuck:
1. Check BUILD_ALLINONE.md for details
2. Review error messages
3. Test prerequisites
4. Ask for help

---

**Last Updated:** 2024
**Maintainer:** Development Team
**Version:** 1.0.0
