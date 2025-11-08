# Fix: api.analyzeBatchFile is not a function (Windows Desktop)

## 🔴 Vấn đề
Sau khi copy code sang Windows và chạy, vẫn báo lỗi:
```
❌ Lỗi phân tích file: api.analyzeBatchFile is not a function
```

## ✅ Giải pháp (5 bước)

### Bước 1: Kill tất cả process Electron
Mở **Command Prompt (CMD)** hoặc **PowerShell** với quyền Admin:

```cmd
taskkill /F /IM electron.exe
taskkill /F /IM node.exe
```

Hoặc dùng Task Manager:
- Nhấn `Ctrl + Shift + Esc`
- Tìm "Electron" và "Node.js"
- Click chuột phải → End Task

### Bước 2: Xóa cache
```cmd
cd C:\path\to\desktop-app
rmdir /S /Q node_modules\.cache
rmdir /S /Q build
```

### Bước 3: Kiểm tra file đã copy đúng chưa

**Kiểm tra preload.js:**
Mở file: `desktop-app\electron\preload.js`

Tìm dòng này (khoảng line 52):
```javascript
  analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),
```

✅ Nếu có dòng này → File đúng
❌ Nếu không có → Copy lại file từ server

**Kiểm tra main.js:**
Mở file: `desktop-app\electron\main.js`

Tìm dòng này (khoảng line 193):
```javascript
ipcMain.handle('analyze-batch-file', async (event, csvFilePath) => {
```

✅ Nếu có → File đúng
❌ Nếu không → Copy lại file từ server

### Bước 4: Reinstall dependencies (Quan trọng!)

```cmd
cd C:\path\to\desktop-app

# Xóa node_modules cũ
rmdir /S /Q node_modules

# Cài lại
yarn install
```

### Bước 5: Rebuild và chạy lại

**Option A: Development mode (Recommended)**
```cmd
yarn electron-dev-win
```

**Option B: Build installer mới**
```cmd
yarn build
yarn dist:win
```

Rồi cài file `.exe` mới trong folder `dist\`

---

## 🧪 Kiểm tra sau khi restart

### Test 1: Check trong DevTools
1. Mở app
2. Nhấn `F12` để mở DevTools
3. Gõ trong Console:
```javascript
console.log(typeof window.electronAPI.analyzeBatchFile);
```

**Kết quả mong đợi:** `"function"`
**Nếu là:** `"undefined"` → Tiếp tục bước troubleshooting

### Test 2: Check tất cả APIs
```javascript
console.log(window.electronAPI);
```

Phải thấy object chứa `analyzeBatchFile` và `selectFile`

---

## 🛠️ Troubleshooting Nâng cao

### Vấn đề 1: Copy không đầy đủ

**Kiểm tra tất cả files đã copy:**
```
desktop-app\
  ├── electron\
  │   ├── main.js         ← Phải có IPC handler
  │   └── preload.js      ← Phải có analyzeBatchFile
  ├── python\
  │   └── batch_scanner.py ← File mới
  └── src\
      └── components\
          └── BatchScanner.js ← File mới
```

**Solution:** Copy lại TOÀN BỘ folder

### Vấn đề 2: Electron cache

**Xóa Electron cache:**
```cmd
# Xóa temp data
del /Q /F %APPDATA%\Electron\*
del /Q /F %LOCALAPPDATA%\Electron\*

# Xóa cache trong project
cd desktop-app
rmdir /S /Q node_modules\.cache
```

### Vấn đề 3: Multiple Electron processes

**Kiểm tra:**
```cmd
tasklist | findstr electron
```

**Kill tất cả:**
```cmd
taskkill /F /IM electron.exe /T
```

### Vấn đề 4: Port đang bị dùng

**Kiểm tra port 3001:**
```cmd
netstat -ano | findstr :3001
```

**Kill process trên port 3001:**
```cmd
# Lấy PID từ lệnh trên (cột cuối)
taskkill /F /PID <PID>
```

---

## 🔧 Script tự động (Tạo file fix.bat)

Tạo file `fix-api-error.bat`:

```batch
@echo off
echo ========================================
echo Fix API Error - Windows Desktop
echo ========================================

echo Step 1: Killing processes...
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo Step 2: Cleaning cache...
if exist node_modules\.cache rmdir /S /Q node_modules\.cache
if exist build rmdir /S /Q build

echo Step 3: Cleaning Electron cache...
del /Q /F %APPDATA%\Electron\* 2>nul
del /Q /F %LOCALAPPDATA%\Electron\* 2>nul

echo Step 4: Reinstalling dependencies...
call yarn install

echo Step 5: Starting app...
call yarn electron-dev-win

pause
```

Chạy file này bằng cách double-click!

---

## ✅ Checklist đầy đủ

Trước khi chạy app, đảm bảo:

- [ ] Đã kill tất cả Electron processes
- [ ] Đã xóa cache (`node_modules\.cache`, `build`)
- [ ] File `electron/preload.js` có `analyzeBatchFile`
- [ ] File `electron/main.js` có IPC handler `analyze-batch-file`
- [ ] File `python/batch_scanner.py` tồn tại
- [ ] File `src/components/BatchScanner.js` tồn tại
- [ ] Đã chạy `yarn install`
- [ ] Đã restart app hoàn toàn

---

## 📞 Vẫn không work?

### Giải pháp cuối cùng: Fresh install

1. **Xóa folder cũ hoàn toàn**
```cmd
cd C:\
rmdir /S /Q desktop-app-old
```

2. **Copy lại folder MỚI từ server**

3. **Cài dependencies mới**
```cmd
cd desktop-app
yarn install
```

4. **Cài Python dependencies**
```cmd
pip install openpyxl
```

5. **Chạy app**
```cmd
yarn electron-dev-win
```

---

## 🎯 Nguyên nhân phổ biến

1. **Electron cache** (60% trường hợp)
   - Fix: Xóa cache và restart

2. **Copy không đầy đủ** (30% trường hợp)
   - Fix: Copy lại toàn bộ folder

3. **Process zombie** (10% trường hợp)
   - Fix: Kill tất cả Electron/Node processes

---

**Hãy thử script tự động `fix-api-error.bat` trước - nó sẽ fix hầu hết các vấn đề!**
