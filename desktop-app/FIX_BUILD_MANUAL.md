# 🔧 DEBUG BUILD SIZE - MANUAL STEPS

## Vấn đề: Build vẫn chỉ 82MB

Electron-builder preset `react-cra` đang override config và exclude node_modules.

## ✅ GIẢI PHÁP:

### CÁCH 1: Dùng script build-full.bat (Khuyến nghị)

```cmd
build-full.bat
```

Script này sẽ build với config explicit, bypass preset.

---

### CÁCH 2: Kiểm tra xem node_modules có trong asar không

```cmd
npx asar list dist\win-unpacked\resources\app.asar > asar-contents.txt
notepad asar-contents.txt
```

Tìm từ "node_modules" trong file. 

- **Nếu KHÔNG có** → Config không work, dùng Cách 3
- **Nếu CÓ** → Có thể do compression, thử Cách 4

---

### CÁCH 3: Build không dùng asar (Workaround)

**Bước 1:** Sửa `package.json`, thêm:

```json
"build": {
  "asar": false,
  ...
}
```

**Bước 2:** Build lại:
```cmd
yarn build
npx electron-builder --win --x64
```

Khi `asar: false`, tất cả files sẽ ở dạng unpacked → Size sẽ đúng.

**Note:** App vẫn chạy bình thường, chỉ khác là files không nén trong .asar

---

### CÁCH 4: Copy package.json mới hoàn toàn

**Bước 1:** Backup package.json cũ:
```cmd
copy package.json package.json.backup
```

**Bước 2:** Copy file mới từ đây:
- File: `package-fixed.json`
- Đổi tên thành `package.json`

**Bước 3:** Clean install:
```cmd
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q build
yarn cache clean
yarn install
```

**Bước 4:** Build:
```cmd
yarn build
npx electron-builder --win --x64
```

---

### CÁCH 5: Build với electron-builder config file riêng

**Bước 1:** Tạo file `electron-builder.yml`:

```yaml
appId: com.90daychonhanh.app
productName: 90dayChonThanh
extends: null

files:
  - build/**/*
  - public/electron.js
  - public/preload.js
  - python/**/*
  - node_modules/**/*
  - package.json

asarUnpack:
  - python/**/*
  - node_modules/electron-store/**/*

extraResources:
  - from: python
    to: python
    filter:
      - "**/*"

directories:
  buildResources: assets
  output: dist

win:
  target:
    - nsis
  icon: assets/icon.png

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
```

**Bước 2:** Build với config file:
```cmd
yarn build
npx electron-builder --win --x64 --config electron-builder.yml
```

---

## 🔍 DEBUG: Kiểm tra chi tiết

### 1. Kiểm tra app.asar size
```cmd
dir dist\win-unpacked\resources\app.asar
```

Nên là: **~80-90 MB**

Nếu chỉ **~3-5 MB** → node_modules KHÔNG có trong asar

### 2. List files trong asar
```cmd
npx asar list dist\win-unpacked\resources\app.asar | findstr /c:"node_modules" /c:"package.json" /c:"python"
```

Phải thấy:
- `/node_modules`
- `/node_modules/@dnd-kit`
- `/node_modules/axios`
- ... (nhiều packages)

### 3. Kiểm tra tổng size unpacked
```cmd
dir dist\win-unpacked
```

Folder size nên: **~300-400 MB**

### 4. Check build log
Khi build, xem log có dòng:
```
• files          build/**/* public/electron.js public/preload.js python/**/* node_modules/**/* package.json
```

Nếu KHÔNG thấy `node_modules/**/*` → Config không được apply

---

## 🐛 Nếu vẫn không work

### Option A: Build portable (không dùng installer)

```cmd
yarn build
npx electron-builder --win --x64 --dir
```

File app ở: `dist\win-unpacked\90daychonhanh-desktop.exe`

Copy toàn bộ folder `win-unpacked` để distribute → App vẫn chạy bình thường.

### Option B: Dùng asar: false

Thêm vào `package.json`:
```json
"build": {
  "asar": false,
  ...
}
```

Build lại. App sẽ lớn hơn nhưng đảm bảo đầy đủ files.

### Option C: Kiểm tra .gitignore / .npmignore

Có thể electron-builder đang đọc `.gitignore` và skip node_modules.

Tạo file `.npmignore` với nội dung:
```
# Don't ignore anything for electron-builder
```

---

## 📊 So sánh sizes

| Component | Expected | Your Build | Status |
|-----------|----------|------------|--------|
| Installer .exe | 150-200 MB | 82 MB | ❌ |
| app.asar | 80-90 MB | ??? MB | ❓ |
| win-unpacked | 300-400 MB | ??? MB | ❓ |

Check từng component để tìm vấn đề.

---

## 💡 Lý do phổ biến

1. **Preset react-cra**: Override config và exclude node_modules
   - Fix: Thêm `"extends": null`

2. **.gitignore**: node_modules bị ignore
   - Fix: Tạo `.npmignore` hoặc dùng `asar: false`

3. **Cache**: Build cũ còn lại
   - Fix: Xóa `dist`, `build`, `node_modules`, build lại

4. **electron-builder version**: Version cũ có bug
   - Fix: Update: `yarn add -D electron-builder@latest`

---

## ✅ Checklist cuối cùng

Trước khi build, đảm bảo:

- [ ] `package.json` có `"extends": null` trong build config
- [ ] `package.json` có `"node_modules/**/*"` trong files
- [ ] Đã xóa `dist/` và `build/`
- [ ] Đã chạy `yarn cache clean`
- [ ] Đã chạy `yarn install` lại
- [ ] Build React thành công (`yarn build`)
- [ ] Folder `node_modules` có đầy đủ packages

---

**Nếu thử hết các cách trên vẫn không được, hãy build với `asar: false` và distribute folder `win-unpacked` trực tiếp.**
