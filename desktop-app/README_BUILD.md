# 🚀 Quick Build Guide

## Cách nhanh nhất (Windows)

1. **Mở Command Prompt** tại thư mục `desktop-app`
2. **Chạy lệnh:**
   ```bash
   QUICK_BUILD.bat
   ```
3. **Đợi 2-5 phút**
4. **Lấy file:** `dist\90dayChonThanh-Setup-1.1.0.exe`

---

## Hoặc build thủ công

```bash
# Bước 1: Cài dependencies
yarn install

# Bước 2: Build installer
yarn dist:win
```

---

## ⚡ One-Click Installer Features

- ✅ **One-click installation** - Không cần tùy chọn
- ✅ **Desktop shortcut** - Tự động tạo shortcut
- ✅ **Start menu** - Thêm vào Start Menu
- ✅ **Auto-update ready** - Sẵn sàng cho tính năng tự động cập nhật
- ✅ **Uninstaller** - Có sẵn chương trình gỡ cài đặt

---

## 📦 Output Files

Sau khi build, bạn sẽ có:

```
dist/
  ├── 90dayChonThanh-Setup-1.1.0.exe  ← File installer (chia sẻ cho users)
  ├── win-unpacked/                   ← Portable version (không cần cài)
  └── builder-debug.yml               ← Log file (để debug nếu có lỗi)
```

---

## 🎯 Version Info

- **Current Version:** 1.1.0
- **Build Type:** NSIS One-Click Installer
- **Target Platform:** Windows 10/11 (x64)
- **File Size:** ~150-200 MB

---

## 🔧 Troubleshooting

**Lỗi "yarn not found":**
```bash
npm install -g yarn
```

**Lỗi "electron-builder not found":**
```bash
yarn add --dev electron-builder
```

**Build bị fail:**
- Xem file `dist/builder-debug.yml` để biết lỗi chi tiết
- Đọc `BUILD_INSTRUCTIONS.md` để biết cách xử lý

---

**📖 Hướng dẫn đầy đủ:** Xem `BUILD_INSTRUCTIONS.md`
