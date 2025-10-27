# 🔄 ĐỔI PORT TỪ 3000 → 3001

## ✅ ĐÃ THAY ĐỔI

Port React development server đã được đổi từ **3000** → **3001**

**Lý do:** Port 3000 đang được sử dụng bởi app khác

---

## 📝 Files Đã Sửa

### 1. `.env`
```env
BROWSER=none
PORT=3001         ← MỚI THÊM
```

### 2. `package.json`
```json
"electron-dev": "... wait-on http://localhost:3001 ..."
"electron-dev-win": "... wait-on http://localhost:3001 ..."
```

### 3. `electron/main.js`
```javascript
const startUrl = isDev 
  ? 'http://localhost:3001'    // ← Đổi từ 3000
  : `file://${...}`;
```

### 4. `public/electron.js`
```javascript
const startUrl = isDev 
  ? 'http://localhost:3001'    // ← Đổi từ 3000
  : `file://${...}`;
```

---

## 🚀 SỬ DỤNG

### Development Mode

**Chạy app:**
```batch
cd desktop-app
yarn electron-dev
```

**App sẽ:**
- React chạy trên: `http://localhost:3001`
- Electron tự động connect port 3001
- Hot reload hoạt động bình thường

---

### Production Build

**Build không bị ảnh hưởng:**
```batch
yarn build
yarn electron-build
```

Port chỉ ảnh hưởng development mode.

---

## 🔧 ĐỔI SANG PORT KHÁC

Nếu muốn đổi sang port khác (ví dụ 3002):

### Bước 1: Sửa `.env`
```env
PORT=3002
```

### Bước 2: Sửa `package.json`
```json
"electron-dev": "... wait-on http://localhost:3002 ..."
"electron-dev-win": "... wait-on http://localhost:3002 ..."
```

### Bước 3: Sửa `electron/main.js` và `public/electron.js`
```javascript
const startUrl = isDev 
  ? 'http://localhost:3002'
  : `file://${...}`;
```

---

## 📊 Port Hiện Tại

| Service | Port | Môi trường |
|---------|------|-----------|
| React Dev Server | **3001** | Development |
| Electron App | N/A | All |
| Production Build | N/A | Không dùng port |

---

## ⚠️ Lưu Ý

### 1. Khởi động lại sau khi đổi

Nếu app đang chạy:
```batch
# Tắt app (Ctrl+C)
# Chạy lại
yarn electron-dev
```

### 2. Cache browser

Nếu gặp lỗi sau khi đổi port:
```batch
# Clear Electron cache
rm -rf %APPDATA%\90dayChonThanh\
# Hoặc
del /s /q %APPDATA%\90dayChonThanh\
```

### 3. Port đã được sử dụng

Nếu port 3001 cũng bị chiếm:
```
Error: Something is already running on port 3001
```

**Fix:** Đổi sang port khác (3002, 3003, etc.) theo hướng dẫn trên

---

## ✅ KIỂM TRA

### Test port đang dùng

```batch
# Windows
netstat -ano | findstr :3001

# Nếu có kết quả → Port đang được dùng
# Nếu trống → Port available
```

### Test app

1. Chạy: `yarn electron-dev`
2. Check console: 
   ```
   Compiled successfully!
   You can now view 90daychonhanh-desktop in the browser.
   Local: http://localhost:3001
   ```
3. Electron window mở
4. App hoạt động bình thường

---

## 🎯 TÓM TẮT

**Vấn đề:** Port 3000 bị chiếm  
**Giải pháp:** Đổi sang port 3001  
**Files sửa:** .env, package.json, electron/main.js, public/electron.js  
**Cách dùng:** `yarn electron-dev` (không thay đổi)  

---

**Port 3001 đã ready! Chạy `yarn electron-dev` để test!** 🚀
