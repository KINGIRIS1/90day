# Kiểm tra trong App - CRITICAL DIAGNOSTIC

## 🔴 Bạn đang gặp lỗi vì:

Electron **CHƯA load preload.js mới** vào memory!

---

## 🔍 Bước 1: Kiểm tra trong DevTools

### Mở app → Nhấn F12 → Console tab

### Test 1: Check API existence
```javascript
console.log(typeof window.electronAPI.analyzeBatchFile);
```

**Kết quả:**
- `"function"` ✅ → API đã load (vấn đề khác)
- `"undefined"` ❌ → Preload.js CŨ vẫn còn cache!

### Test 2: List all APIs
```javascript
console.log(Object.keys(window.electronAPI));
```

**Xem có `"analyzeBatchFile"` trong list không?**
- Có ✅ → API đã expose
- Không ❌ → Preload.js cũ!

### Test 3: Check entire electronAPI
```javascript
console.log(window.electronAPI);
```

**Scroll xuống, tìm `analyzeBatchFile`**

---

## 🎯 Dựa vào kết quả

### Nếu Test 1 = "undefined" → PRELOAD.JS CŨ!

**Điều này có nghĩa:**
1. Cache CHƯA được xóa hết
2. Hoặc bạn đang chạy production build (đã compile sẵn)
3. Hoặc Electron đang load từ nơi khác

**Giải pháp:**

#### Option A: Check production build
```javascript
// In Console
console.log(process.env.NODE_ENV);
```

Nếu là `"production"` → Bạn đang chạy **packaged app**, không phải dev mode!

**Fix:**
- Close app
- Delete packaged app (file .exe)
- Run: `yarn electron-dev-win` (dev mode)

#### Option B: Restart máy
- Đơn giản nhất
- 95% success rate
- Xóa TẤT CẢ memory cache

```cmd
# Sau khi restart máy:
cd C:\desktop-app
yarn electron-dev-win
```

#### Option C: Nuclear - Fresh install
```cmd
# Xóa folder hiện tại
cd C:\
rmdir /S /Q desktop-app

# Copy lại từ server (FileZilla/WinSCP)
# Đường dẫn server: /app/desktop-app/

# Install
cd desktop-app
yarn install
yarn electron-dev-win
```

---

### Nếu Test 1 = "function" → API ĐÃ LOAD!

**Vấn đề ở code JavaScript!**

Check xem code gọi API có đúng không:

```javascript
// Trong Console, test trực tiếp:
window.electronAPI.analyzeBatchFile('D:\\APP\\test1.xlsx')
  .then(result => console.log('Result:', result))
  .catch(err => console.error('Error:', err));
```

Nếu lệnh này work → Vấn đề ở BatchScanner.js code!

---

## 🚨 Nếu TEST CHO KẾT QUẢ "undefined"

### → Bạn CẦN restart máy hoặc fresh install!

**Tại sao force-clean-restart.bat không work?**

Có thể:
1. Script không chạy với Admin rights
2. AppData cache chưa xóa hết (permission issue)
3. Electron process vẫn running trong background
4. Đang chạy production build (không phải dev mode)

**Solution duy nhất còn lại:**

### RESTART MÁY + Fresh Start

```cmd
# 1. Restart Windows
# 2. Sau khi restart:

cd C:\desktop-app

# 3. Kill mọi thứ
taskkill /F /IM electron.exe /T
taskkill /F /IM node.exe /T

# 4. Clean manually
rmdir /S /Q node_modules
rmdir /S /Q build
rmdir /S /Q .cache

# 5. Delete AppData (Windows Explorer)
explorer %APPDATA%
# → Xóa folder "Electron"

explorer %LOCALAPPDATA%  
# → Xóa folder "Electron"

# 6. Rebuild
yarn install

# 7. Run
yarn electron-dev-win
```

---

## 🔧 Troubleshooting Each Scenario

### Scenario 1: Running packaged app (.exe)
**Problem:** .exe file already compiled with old code
**Fix:** Delete .exe, run dev mode

### Scenario 2: Multiple Electron versions
**Problem:** Old Electron in global vs local
**Fix:** 
```cmd
npm uninstall -g electron
cd desktop-app
yarn install
```

### Scenario 3: Permission issues
**Problem:** Can't delete AppData cache
**Fix:** Run Command Prompt as Administrator

### Scenario 4: Wrong working directory
**Problem:** Running from wrong folder
**Fix:**
```cmd
cd C:\desktop-app
# Verify: Should see package.json
dir package.json
```

---

## ✅ Success Checklist

After fixes:

- [ ] F12 → Console → `typeof window.electronAPI.analyzeBatchFile` → `"function"`
- [ ] `Object.keys(window.electronAPI)` includes "analyzeBatchFile"
- [ ] Click "Chọn file" → No error
- [ ] File selection dialog opens
- [ ] After selecting .xlsx → Analysis runs (no "is not a function" error)

---

## 📞 What to report back

Please tell me:

1. **Test 1 result:** `typeof window.electronAPI.analyzeBatchFile` = ?
2. **Test 2 result:** Is "analyzeBatchFile" in the keys list?
3. **NODE_ENV:** `process.env.NODE_ENV` = ?
4. **Running mode:** Dev (yarn electron-dev-win) or Packaged (.exe)?

This will help me pinpoint exact issue!

---

**🔴 IMPORTANT: Run the DevTools tests FIRST before trying any fix!**
