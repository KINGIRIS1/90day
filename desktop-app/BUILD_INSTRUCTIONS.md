# 🚀 Hướng dẫn Build One-Click Installer

## ✅ Yêu cầu hệ thống

- **Windows 10/11** (để build Windows installer)
- **Node.js** v16 hoặc mới hơn
- **Yarn** (hoặc npm)
- **Python 3.9+** đã cài đặt
- **Git** (để clone/pull code)

---

## 📦 Các bước Build

### 1. Clone hoặc Pull code mới nhất

```bash
# Nếu chưa có code
git clone <your-repo-url>

# Hoặc pull code mới nhất
cd desktop-app
git pull origin main
```

### 2. Cài đặt dependencies

```bash
cd desktop-app
yarn install
# hoặc: npm install
```

### 3. Build One-Click Installer cho Windows

```bash
yarn dist:win
# hoặc: npm run dist:win
```

**Lưu ý:** Build sẽ mất khoảng 2-5 phút tùy vào cấu hình máy.

### 4. Lấy file installer

Sau khi build xong, file installer sẽ nằm ở:

```
desktop-app/dist/90dayChonThanh-Setup-1.1.0.exe
```

---

## 🎯 Các script build có sẵn

| Script | Mô tả |
|--------|-------|
| `yarn dist:win` | Build Windows installer (one-click NSIS) |
| `yarn electron-build` | Build cho tất cả platforms |
| `yarn electron-pack` | Build portable (không cần cài đặt) |

---

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "wine is required"

**Nguyên nhân:** Đang build trên Linux/Mac cho Windows.

**Giải pháp:** Build trên máy Windows, hoặc cài đặt wine:

```bash
# Ubuntu/Debian
sudo apt-get install wine64

# macOS
brew install wine-stable
```

### Lỗi: "electron-builder not found"

**Giải pháp:**

```bash
yarn add --dev electron-builder
# hoặc: npm install --save-dev electron-builder
```

### Lỗi: "Python not found"

**Giải pháp:** Cài đặt Python 3.9+ từ [python.org](https://www.python.org/downloads/)

---

## 📋 Cấu hình Build

Build config trong `package.json`:

```json
{
  "build": {
    "appId": "com.90daychonhanh.app",
    "productName": "90dayChonThanh",
    "nsis": {
      "oneClick": true,           // One-click installer
      "perMachine": false,        // Install cho user hiện tại
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

---

## 🎨 Customization

### Thay đổi icon

1. Thêm file icon vào thư mục `assets/`
2. Update trong `package.json`:

```json
"win": {
  "icon": "assets/your-icon.png"
}
```

### Thay đổi tên file installer

Update trong `package.json`:

```json
"win": {
  "artifactName": "YourAppName-Setup-${version}.exe"
}
```

---

## 📊 Kích thước file

- **Installer:** ~150-200 MB
- **Installed:** ~250-300 MB
- **Bao gồm:** Electron runtime, React app, Python runtime, OCR libraries

---

## 🚀 Deploy

Sau khi có file `.exe`, bạn có thể:

1. **Chia sẻ trực tiếp** cho người dùng
2. **Upload lên GitHub Releases**
3. **Host trên website** của bạn
4. **Upload lên Google Drive / Dropbox**

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:

- Console logs khi build
- File `dist/builder-debug.yml`
- Docs: https://www.electron.build/

---

**Version:** 1.1.0  
**Last Updated:** 14/11/2024
