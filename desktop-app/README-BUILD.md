# 🏗️ Build Installer Guide - 90dayChonThanh Desktop v1.1.0

## 🎯 Quick Start

**Muốn build installer ngay? Chỉ 3 bước:**

```bash
# 1. Mở Command Prompt trong thư mục desktop-app
cd C:\path\to\desktop-app

# 2. Chạy build script
build-installer.bat

# 3. Chờ 5-10 phút → Done!
# File installer: dist\90dayChonThanh-Setup-1.1.0.exe
```

**Xem hướng dẫn chi tiết:** [`QUICK_START.md`](QUICK_START.md) (5 phút)

---

## 📚 Complete Documentation

| Document | Description | Read When |
|----------|-------------|-----------|
| **[QUICK_START.md](QUICK_START.md)** | ⚡ 5-minute quick start guide | **Start here!** |
| **[BUILD_README.md](BUILD_README.md)** | 📖 Complete build guide | Need full details |
| **[HUONG_DAN_BUILD_INSTALLER.md](HUONG_DAN_BUILD_INSTALLER.md)** | 🇻🇳 Vietnamese detailed guide | Vietnamese speakers |
| **[BUILD_SCRIPTS_INDEX.md](BUILD_SCRIPTS_INDEX.md)** | 📑 All scripts & docs index | Find specific script |
| **[BUILD_CHECKLIST.md](BUILD_CHECKLIST.md)** | ✅ Step-by-step checklist | Systematic build |

---

## 🚀 Build Scripts

### Primary Scripts

```bash
# Full build (first time)
build-installer.bat

# Quick rebuild (after changes)
quick-build.bat

# Test installer
test-installer.bat
```

### PowerShell Alternative

```powershell
# Full build with PowerShell (prettier output)
.\build-installer.ps1
```

---

## 📋 Prerequisites

Install these before building:

1. **Node.js** (>= v16) → https://nodejs.org/
2. **Yarn** → `npm install -g yarn`
3. **Python** (3.10-3.12) → https://www.python.org/
4. **NSIS** (recommended) → https://nsis.sourceforge.io/Download

**Check installation:**
```bash
node --version
yarn --version
python --version
makensis /VERSION
```

---

## 📦 Build Output

After successful build:

```
dist/
└── 90dayChonThanh-Setup-1.1.0.exe  (~150-250 MB)
```

**This is your installer file!** 🎉

---

## 🎬 Build Process Overview

```
Prerequisites Check
  ↓
Clean Python Vendor
  ↓
Install Dependencies (yarn install)
  ↓
Build React App (yarn build)
  ↓
Build Electron + Installer (yarn dist:win)
  ↓
Verify Output
  ↓
✅ Done! → dist\90dayChonThanh-Setup-1.1.0.exe
```

**Time:** ~5-10 minutes (full build), ~2-3 minutes (quick rebuild)

---

## ⚡ Quick Commands

### First Build
```bash
build-installer.bat
```

### Rebuild After Code Changes
```bash
quick-build.bat
```

### Test
```bash
test-installer.bat
```

### Manual Step-by-Step
```bash
# Clean Python vendor
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1

# Install dependencies
yarn install

# Build React
yarn build

# Build installer
yarn dist:win
```

---

## 🐛 Common Issues & Quick Fixes

### ❌ "Node.js not found"
```bash
# Install Node.js from https://nodejs.org/
# Then OPEN NEW Command Prompt and try again
```

### ❌ "Yarn not found"
```bash
npm install -g yarn
# Then OPEN NEW Command Prompt
```

### ❌ "NSIS not found"
```bash
# Download and install NSIS from https://nsis.sourceforge.io/Download
# Add to PATH
# OPEN NEW Command Prompt
```

### ❌ "EPERM: operation not permitted"
```bash
# Close app if running
rmdir /s /q dist
# Run build again
build-installer.bat
```

### ❌ Build stuck or very slow
```bash
# Clean build
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q build
yarn install
build-installer.bat
```

**More troubleshooting:** See `BUILD_README.md` → Troubleshooting section

---

## 🧪 Testing

### Quick Test
```bash
test-installer.bat
```

### Manual Test
1. Run: `dist\90dayChonThanh-Setup-1.1.0.exe`
2. Install the app
3. Test features:
   - File scanning ✓
   - OCR & classification ✓
   - Settings ✓
   - Export ✓

**Detailed test checklist:** See `BUILD_CHECKLIST.md`

---

## 📤 Distribution

After successful build and testing:

### Option 1: Google Drive
1. Upload `.exe` to Google Drive
2. Share → "Anyone with the link"
3. Send link to users

### Option 2: GitHub Release
1. Push code to GitHub
2. Create Release
3. Attach `.exe` file
4. Share release URL

### Option 3: Direct Download
- Upload to your website/hosting
- Share download link

---

## 💡 Best Practices

✅ **DO:**
- Read `QUICK_START.md` before first build
- Use `build-installer.bat` for full builds
- Use `quick-build.bat` for quick rebuilds
- Test before distributing
- Open NEW Command Prompt after installing tools

❌ **DON'T:**
- Use old Command Prompt after installing tools
- Build while app is running
- Skip error messages
- Distribute untested installer

---

## 📊 Build Checklist

- [ ] Prerequisites installed (Node, Yarn, Python, NSIS)
- [ ] All commands work (node, yarn, python, makensis)
- [ ] Run `build-installer.bat`
- [ ] Wait for completion (5-10 min)
- [ ] Verify: `dist\90dayChonThanh-Setup-1.1.0.exe` exists
- [ ] Size: ~150-250 MB
- [ ] Run `test-installer.bat`
- [ ] Test all features
- [ ] Ready to distribute! 🎉

**Detailed checklist:** See `BUILD_CHECKLIST.md`

---

## 🔗 More Resources

### Build Guides
- [QUICK_START.md](QUICK_START.md) - Start here! (5 min)
- [BUILD_README.md](BUILD_README.md) - Complete guide
- [HUONG_DAN_BUILD_INSTALLER.md](HUONG_DAN_BUILD_INSTALLER.md) - Vietnamese guide
- [BUILD_SCRIPTS_INDEX.md](BUILD_SCRIPTS_INDEX.md) - All scripts index

### Development
- [README.md](README.md) - Development guide
- [CHANGELOG.md](CHANGELOG.md) - Version history

### Features
- [CLASSIFICATION_RULES_EXPLAINED.md](CLASSIFICATION_RULES_EXPLAINED.md) - Classification logic
- [BYOK_FEATURE_GUIDE.md](BYOK_FEATURE_GUIDE.md) - BYOK feature

---

## 📞 Support

**Need help?**

1. Check [BUILD_README.md](BUILD_README.md) → Troubleshooting
2. Check [QUICK_START.md](QUICK_START.md) → Quick fixes
3. Email: contact@90daychonthanh.vn

---

## 📝 Version Info

- **App Version:** 1.1.0
- **Platform:** Windows x64
- **Installer Type:** NSIS one-click installer
- **Build Time:** ~5-10 minutes (full), ~2-3 minutes (quick)
- **Installer Size:** ~150-250 MB

---

## 🎉 Ready to Build?

**3 simple steps:**

```bash
# 1. Check prerequisites
node --version && yarn --version && python --version

# 2. Run build
build-installer.bat

# 3. Test
test-installer.bat

# Done! 🚀
```

**First time?** → Read [QUICK_START.md](QUICK_START.md) first (5 min)

**Happy Building!** 🏗️✨
