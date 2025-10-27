# 🔧 FIX: Port 3000 Vẫn Bị Chiếm

## ❌ Vấn Đề

Dù đã đổi port nhưng React Scripts vẫn cố chạy port 3000:
```
Something is already running on port 3000.
```

---

## ✅ GIẢI PHÁP (Chọn 1)

### Giải pháp 1: Dùng Script Mới (RECOMMENDED)

```batch
cd desktop-app
start-dev.bat
```

Script này tự động set PORT=3001 và chạy app.

---

### Giải pháp 2: Kill Process Port 3000

**Tìm process đang dùng port 3000:**
```batch
netstat -ano | findstr :3000
```

**Output ví dụ:**
```
TCP    0.0.0.0:3000    0.0.0.0:0    LISTENING    12345
```

**Kill process (12345 là PID):**
```batch
taskkill /PID 12345 /F
```

Sau đó chạy lại:
```batch
yarn electron-dev
```

---

### Giải pháp 3: Tắt App Khác Trên Port 3000

Tìm app nào đang dùng port 3000:
- Có thể là React app khác
- Có thể là Node server
- Check Task Manager

Tắt app đó, rồi chạy lại.

---

### Giải pháp 4: Dùng Port Khác (3002)

Nếu cả 3000 và 3001 đều bận:

**Sửa `.env.local`:**
```env
PORT=3002
BROWSER=none
```

**Sửa `package.json`:**
```json
"electron-dev": "... wait-on http://localhost:3002 ..."
```

**Sửa `electron/main.js` và `public/electron.js`:**
```javascript
? 'http://localhost:3002'
```

---

## 🔍 DEBUG

### Kiểm tra .env được load chưa

Thêm vào đầu `package.json` scripts để test:
```batch
echo %PORT%
```

Nếu không hiện 3001 → .env chưa được đọc

---

### Kiểm tra React Scripts config

```batch
cd desktop-app
yarn start
```

Check console output:
- Nếu "Compiled successfully! Local: http://localhost:3001" → OK
- Nếu vẫn 3000 → Cần fix config

---

## 📝 Files Đã Tạo/Sửa

### 1. `.env` (đã có)
```env
BROWSER=none
PORT=3001
```

### 2. `.env.local` (MỚI - Priority cao hơn)
```env
PORT=3001
BROWSER=none
```

### 3. `package.json` (đã sửa)
```json
"start": "set PORT=3001 && react-scripts start",
"electron-dev": "concurrently \"set PORT=3001 && yarn start\" ...",
"electron-dev-win": "concurrently \"set PORT=3001 && set BROWSER=none && yarn start\" ..."
```

### 4. `start-dev.bat` (MỚI)
```batch
set PORT=3001
set BROWSER=none
yarn electron-dev-win
```

---

## 🎯 CÁCH CHẠY KHUYẾN NGHỊ

### Windows:

```batch
cd C:\desktop-app
start-dev.bat
```

Hoặc:

```batch
cd C:\desktop-app
set PORT=3001 && yarn electron-dev-win
```

### Verify port:

Sau khi chạy, check console:
```
Local:            http://localhost:3001
```

Nếu thấy 3001 → Thành công!

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Clear Cache

Nếu vẫn lỗi, clear cache:
```batch
# Xóa node_modules
rmdir /s /q node_modules
yarn install

# Xóa build cache
rmdir /s /q build
rmdir /s /q .cache
```

### 2. Restart Terminal

Đóng Command Prompt và mở lại (để load .env mới)

### 3. Check Multiple Ports

```batch
# Check port 3000
netstat -ano | findstr :3000

# Check port 3001
netstat -ano | findstr :3001
```

Cả 2 phải trống hoặc chỉ 3001 có process của app mình.

---

## 🚀 WORKFLOW HOÀN CHỈNH

### Bước 1: Tắt tất cả apps đang chạy

```batch
# Tắt các terminal/command prompt đang chạy
# Hoặc kill processes
taskkill /F /IM node.exe
```

### Bước 2: Clean workspace

```batch
cd desktop-app
rmdir /s /q node_modules
yarn install
```

### Bước 3: Chạy app

```batch
start-dev.bat
```

### Bước 4: Verify

Check console output có "http://localhost:3001" không.

---

## 💡 Quick Fix Commands

```batch
# Kill all node processes
taskkill /F /IM node.exe

# Check ports
netstat -ano | findstr :3000
netstat -ano | findstr :3001

# Run app with explicit port
set PORT=3001 && yarn electron-dev-win

# Or use script
start-dev.bat
```

---

## 📞 Nếu Vẫn Không Được

Báo cho tôi:
1. Output của: `netstat -ano | findstr :3000`
2. Output của: `echo %PORT%`
3. Output của: `yarn start` (chạy riêng)

Tôi sẽ debug thêm!

---

**Thử `start-dev.bat` ngay!** 🚀
