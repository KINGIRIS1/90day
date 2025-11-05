# 📑 Build Scripts & Documentation Index

## 🎯 Mục Đích
Tài liệu này tổng hợp tất cả build scripts và documentation để build installer cho 90dayChonThanh Desktop App v1.1.0.

---

## 🚀 Quick Start (Recommended)

**Lần đầu build? Bắt đầu tại đây:**

1. **Đọc:** [`QUICK_START.md`](QUICK_START.md) - 5 phút quick start guide
2. **Chạy:** `build-installer.bat` - One-click build script
3. **Test:** `test-installer.bat` - Test installer sau khi build

---

## 📜 Build Scripts

### 🟢 Primary Build Scripts (Recommended)

| Script | Mô tả | Khi nào dùng |
|--------|-------|--------------|
| **`build-installer.bat`** | Full build với prerequisites check | ✅ Build lần đầu<br>✅ Build đầy đủ<br>✅ Kiểm tra hệ thống |
| **`build-installer.ps1`** | PowerShell version của build-installer.bat | ✅ Nếu thích PowerShell<br>✅ UI đẹp hơn |
| **`quick-build.bat`** | Fast rebuild (2-3 phút) | ✅ Rebuild sau khi đã build 1 lần<br>✅ Chỉ sửa code |
| **`test-installer.bat`** | Test installer sau khi build | ✅ Verify installer<br>✅ Quick test |

### 🔵 Alternative Build Scripts

| Script | Mô tả | Notes |
|--------|-------|-------|
| `build-full.bat` | Full build alternative | Tương tự build-installer.bat |
| `build-windows.bat` | Windows-specific build | Simplified version |
| `build-windows.ps1` | PowerShell Windows build | PowerShell version |
| `build.bat` | Legacy build script | Older version |

### 🟡 Specialized Build Scripts

| Script | Mô tả | Use Case |
|--------|-------|----------|
| `build-allinone.bat` | All-in-one installer build | Creates single .exe with everything |
| `build-electron-only.bat` | Build Electron app only | No installer, just app folder |
| `build-with-pythonpath-fix.bat` | Build with Python path fixes | If Python path issues |
| `quick-fix-rebuild.bat` | Quick fix and rebuild | After small fixes |

### 🧪 Test Scripts

| Script | Mô tả |
|--------|-------|
| `test-installer.bat` | Test installer file |
| `test-improvements.bat` | Test app improvements |
| `test-menu.bat` | Test menu system |

---

## 📚 Documentation Files

### 🟢 Start Here

| File | Mô tả | Đọc khi nào |
|------|-------|------------|
| **[`QUICK_START.md`](QUICK_START.md)** | 5-phút quick start | ✅ LẦN ĐẦU BUILD |
| **[`BUILD_README.md`](BUILD_README.md)** | Hướng dẫn chi tiết đầy đủ | ✅ Cần hiểu rõ build process |
| **[`HUONG_DAN_BUILD_INSTALLER.md`](HUONG_DAN_BUILD_INSTALLER.md)** | Hướng dẫn tiếng Việt chi tiết | ✅ Hướng dẫn từ A-Z |

### 🔵 Reference Guides

| File | Mô tả |
|------|-------|
| `BUILD_CHECKLIST.md` | Checklist từng bước |
| `BUILD_STATUS.md` | Build status và progress |
| `BUILD_WINDOWS_GUIDE.md` | Windows-specific guide |
| `BUILD_FIX_COMPLETE.md` | Build fixes documentation |

### 🟡 Specialized Docs

| File | Topic |
|------|-------|
| `BUILD_ALLINONE.md` | All-in-one installer guide |
| `ALLINONE_BUILD_CHECKLIST.md` | All-in-one checklist |
| `AUTO_VARIANTS_GUIDE.md` | Auto variants guide |
| `BYOK_FEATURE_GUIDE.md` | Bring Your Own Key feature |
| `BYOK_IMPLEMENTATION_SUMMARY.md` | BYOK implementation |
| `BYOK_INSTALLATION_GUIDE.md` | BYOK installation |

### 🟣 Feature & Change Docs

| File | Topic |
|------|-------|
| `CHANGELOG.md` | All changes log |
| `CHANGELOG-v1.1.0.md` | Version 1.1.0 changes |
| `CLASSIFICATION_RULES_EXPLAINED.md` | Document classification rules |
| `CLOUD_OCR_CROP_OPTIMIZATION.md` | OCR optimization |

---

## 🎬 Build Workflow

### For First-Time Builders

```
1. Read QUICK_START.md (5 min)
   ↓
2. Check prerequisites
   ↓
3. Run: build-installer.bat
   ↓
4. Wait 5-10 minutes
   ↓
5. Run: test-installer.bat
   ↓
6. Done! → dist\90dayChonThanh-Setup-1.1.0.exe
```

### For Regular Rebuilds

```
1. Make code changes
   ↓
2. Run: quick-build.bat
   ↓
3. Wait 2-3 minutes
   ↓
4. Test installer
   ↓
5. Done!
```

---

## 📋 Prerequisites

**Trước khi build, cần cài:**

1. **Node.js** (>= v16) - https://nodejs.org/
2. **Yarn** (>= 1.22) - `npm install -g yarn`
3. **Python** (3.10-3.12) - https://www.python.org/
4. **NSIS** (recommended) - https://nsis.sourceforge.io/Download

**Kiểm tra:**
```bash
node --version
yarn --version
python --version
makensis /VERSION
```

---

## ⚡ Quick Commands

### Full Build
```bash
build-installer.bat
```

### Quick Rebuild
```bash
quick-build.bat
```

### Test
```bash
test-installer.bat
```

### Manual Build
```bash
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1
yarn install
yarn build
yarn dist:win
```

---

## 🎯 Recommended Path

**🆕 Lần đầu build?**
1. `QUICK_START.md` → Đọc quick start
2. `build-installer.bat` → Chạy build
3. `test-installer.bat` → Test

**🔄 Đã build rồi, muốn rebuild?**
1. `quick-build.bat` → Fast rebuild

**📚 Muốn hiểu chi tiết?**
1. `BUILD_README.md` → Chi tiết đầy đủ
2. `HUONG_DAN_BUILD_INSTALLER.md` → Hướng dẫn tiếng Việt

**🐛 Gặp lỗi?**
1. `BUILD_README.md` → Phần Troubleshooting
2. `BUILD_FIX_COMPLETE.md` → Build fixes

---

## 📊 Build Output

**Expected output:**
```
dist/
├── 90dayChonThanh-Setup-1.1.0.exe  (~150-250 MB) ← INSTALLER CHÍNH
├── 90dayChonThanh-Setup-1.1.0.exe.blockmap
├── win-unpacked/                    ← Portable version
│   └── 90dayChonThanh.exe
└── builder-effective-config.yaml
```

---

## 🆘 Help & Support

**Nếu gặp vấn đề:**

1. **Check documentation:**
   - `QUICK_START.md` - Quick fixes
   - `BUILD_README.md` - Troubleshooting section
   - `HUONG_DAN_BUILD_INSTALLER.md` - Xử lý lỗi

2. **Common fixes:**
   ```bash
   # Mở lại Command Prompt sau khi cài tools
   # Xóa và build lại
   rmdir /s /q node_modules
   rmdir /s /q dist
   rmdir /s /q build
   yarn install
   build-installer.bat
   ```

3. **Contact:**
   - Email: contact@90daychonthanh.vn

---

## 🏆 Best Practices

✅ **DO:**
- Đọc `QUICK_START.md` trước khi build lần đầu
- Dùng `build-installer.bat` cho full build
- Dùng `quick-build.bat` cho rebuild
- Test installer trước khi phân phối
- Mở Command Prompt mới sau khi cài tools

❌ **DON'T:**
- Dùng Command Prompt cũ sau khi cài tools
- Build khi app đang chạy
- Bỏ qua error messages
- Phân phối installer chưa test

---

## 📝 Notes

- **Version:** 1.1.0
- **Platform:** Windows x64
- **Installer Type:** NSIS one-click installer
- **Expected Build Time:** 5-10 minutes (full), 2-3 minutes (quick)
- **Expected Installer Size:** ~150-250 MB

---

## 🔗 Quick Links

- [QUICK_START.md](QUICK_START.md) - 5 phút bắt đầu
- [BUILD_README.md](BUILD_README.md) - Hướng dẫn đầy đủ
- [HUONG_DAN_BUILD_INSTALLER.md](HUONG_DAN_BUILD_INSTALLER.md) - Hướng dẫn tiếng Việt
- [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md) - Checklist chi tiết

---

**🚀 Happy Building!**

*Last Updated: 2025*
