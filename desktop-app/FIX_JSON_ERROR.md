# 🔴 SỬA LỖI PACKAGE.JSON - JSON SYNTAX ERROR

## ❌ Lỗi hiện tại:
```
SyntaxError: Expected ',' or '}' after property value in JSON at position 1459 (line 50 column 5)
```

## ✅ GIẢI PHÁP:

### CÁCH 1: Copy file đúng từ đây (KHUYẾN NGHỊ)

**Bước 1:** Mở file này trên máy Windows:
```
desktop-app\package.json.CORRECT
```

**Bước 2:** Copy TOÀN BỘ nội dung

**Bước 3:** Mở file:
```
desktop-app\package.json
```

**Bước 4:** Xóa hết, paste nội dung mới vào

**Bước 5:** Save file (Ctrl+S)

---

### CÁCH 2: Download file mới

Nếu bạn không thấy file `package.json.CORRECT`, copy nội dung này:

```json
{
  "name": "90daychonhanh-desktop",
  "version": "1.1.0",
  "description": "Desktop app for land document scanning with offline OCR and optional cloud boost - v1.1.0 with Smart Crop & Improved Classification",
  "main": "public/electron.js",
  "homepage": ".",
  "scripts": {
    "start": "set PORT=3001 && react-scripts start",
    "build": "react-scripts build",
    "electron": "electron .",
    "electron-dev": "concurrently \"set PORT=3001 && yarn start\" \"wait-on http://localhost:3001 && electron .\"",
    "electron-dev-win": "concurrently \"set PORT=3001 && set BROWSER=none && yarn start\" \"wait-on http://localhost:3001 && electron .\"",
    "electron-pack": "yarn build && electron-builder --dir",
    "electron-build": "yarn build && electron-builder",
    "postinstall": "electron-builder install-app-deps"
  },
  "build": {
    "appId": "com.90daychonhanh.app",
    "productName": "90dayChonThanh",
    "files": [
      "build/**/*",
      "public/electron.js",
      "public/preload.js",
      "python/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "asarUnpack": [
      "python/**/*",
      "node_modules/electron-store/**/*"
    ],
    "extraResources": [
      {
        "from": "python",
        "to": "python",
        "filter": ["**/*"]
      }
    ],
    "directories": {
      "buildResources": "assets",
      "output": "dist"
    },
    "win": {
      "target": [
        "nsis"
      ],
      "icon": "assets/icon.png",
      "sign": null,
      "signingHashAlgorithms": null
    },
    "mac": {
      "target": [
        "dmg"
      ],
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": [
        "AppImage"
      ],
      "icon": "assets/icon.png",
      "category": "Utility"
    }
  },
  "dependencies": {
    "@dnd-kit/core": "^6.3.1",
    "@dnd-kit/sortable": "^10.0.0",
    "@dnd-kit/utilities": "^3.2.2",
    "axios": "^1.12.2",
    "date-fns": "^2.29.3",
    "electron-store": "^8.1.0",
    "form-data": "^4.0.4",
    "lucide-react": "latest",
    "pdf-lib": "^1.17.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "tailwindcss": "^3.4.1"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.14",
    "concurrently": "^8.2.2",
    "cross-env": "^10.1.0",
    "electron": "^28.0.0",
    "electron-builder": "^24.9.1",
    "postcss": "^8.4.21",
    "react-scripts": "5.0.1",
    "wait-on": "^7.2.0"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

**Lưu ý:** 
- ✅ Đảm bảo copy TOÀN BỘ từ `{` đầu tiên đến `}` cuối cùng
- ✅ Không thêm/bớt ký tự nào
- ✅ Save file với encoding UTF-8

---

## 🧪 KIỂM TRA FILE ĐÚNG

Sau khi sửa xong, chạy:
```cmd
yarn --version
```

Nếu không lỗi = Package.json đúng!

---

## 🚀 BUILD LẠI

```cmd
cd desktop-app
rmdir /s /q dist
rmdir /s /q build
yarn install
yarn build
npx electron-builder --win --x64
```

---

## ⚠️ LƯU Ý

**Lỗi thường gặp khi sửa JSON:**
1. ❌ Thiếu dấu phẩy `,` giữa các properties
2. ❌ Dấu phẩy thừa `,` ở cuối object/array
3. ❌ Quote không đúng (phải dùng `"` không dùng `'`)
4. ❌ Comment trong JSON (JSON không hỗ trợ comment)

**Cách tránh lỗi:**
- ✅ Dùng editor có JSON validation (VS Code, Notepad++)
- ✅ Copy/paste file đúng thay vì sửa tay
- ✅ Dùng online JSON validator: https://jsonlint.com/

---

## 📝 ĐIỂM KHÁC BIỆT SO VỚI FILE CŨ

File mới có thêm:
```json
"files": [
  ...
  "node_modules/**/*",  ← THÊM MỚI
  "package.json"        ← THÊM MỚI
],
"asarUnpack": [         ← THÊM MỚI (toàn bộ section)
  "python/**/*",
  "node_modules/electron-store/**/*"
]
```

Đây là lý do tại sao build cũ chỉ có 84MB!

---

**✅ Sau khi sửa xong, build sẽ ra file ~180-200MB!**
