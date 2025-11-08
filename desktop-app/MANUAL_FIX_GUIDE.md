# Manual Fix Guide - Copy 3 Files từ Server

## 🎯 Vấn đề
Bạn đã copy folder **CŨ** từ server. Cần update **3 files** để có code mới.

## ✅ Giải pháp: Copy 3 files từ server

### Files cần copy:

| # | File trên Server | Copy đến Local |
|---|------------------|----------------|
| 1 | `/app/desktop-app/electron/preload.js` | `desktop-app\electron\preload.js` |
| 2 | `/app/desktop-app/electron/main.js` | `desktop-app\electron\main.js` |
| 3 | `/app/desktop-app/src/App.js` | `desktop-app\src\App.js` |

---

## 📋 Hướng dẫn từng bước

### Option 1: Dùng FileZilla / WinSCP (GUI)

**Bước 1: Connect to server**
- Mở FileZilla hoặc WinSCP
- Connect đến server Linux của bạn

**Bước 2: Navigate to folder**
- Server side: `/app/desktop-app/`
- Local side: `C:\your-path\desktop-app\`

**Bước 3: Copy files**
1. **preload.js:**
   - Server: `/app/desktop-app/electron/preload.js`
   - Local: `desktop-app\electron\preload.js`
   - Click chuột phải → Download (overwrite)

2. **main.js:**
   - Server: `/app/desktop-app/electron/main.js`
   - Local: `desktop-app\electron\main.js`
   - Click chuột phải → Download (overwrite)

3. **App.js:**
   - Server: `/app/desktop-app/src/App.js`
   - Local: `desktop-app\src\App.js`
   - Click chuột phải → Download (overwrite)

**Bước 4: Verify**
- Chạy `check-files.bat`
- Phải thấy tất cả ✅

---

### Option 2: Dùng Command Line (SSH/SCP)

**Từ Windows PowerShell:**

```powershell
# Navigate to your desktop-app folder
cd C:\your-path\desktop-app

# Copy preload.js
scp user@server:/app/desktop-app/electron/preload.js electron\

# Copy main.js
scp user@server:/app/desktop-app/electron/main.js electron\

# Copy App.js
scp user@server:/app/desktop-app/src/App.js src\
```

**Verify:**
```cmd
check-files.bat
```

---

### Option 3: Copy toàn bộ folder (Chậm nhưng chắc chắn)

```powershell
# Backup folder cũ
Rename-Item desktop-app desktop-app-old

# Copy toàn bộ folder mới từ server
scp -r user@server:/app/desktop-app C:\your-path\

# Install dependencies
cd desktop-app
yarn install
```

---

## 🔍 Verify sau khi copy

### Bước 1: Run check-files.bat
```cmd
check-files.bat
```

**Kết quả mong đợi:**
```
✅ electron\preload.js - analyzeBatchFile found
✅ electron\main.js - IPC handler found
✅ python\batch_scanner.py - exists
✅ src\components\BatchScanner.js - exists
✅ src\App.js - BatchScanner imported

========================================
✅ All files are correct!
========================================
```

### Bước 2: Clean cache và restart
```cmd
fix-api-error.bat
```

### Bước 3: Test trong app
1. App mở
2. Nhấn `F12`
3. Console:
```javascript
console.log(typeof window.electronAPI.analyzeBatchFile);
// Result: "function" ✅
```

---

## 🚨 Nếu không có quyền access server

### Option: Tạo files mới manually

Nếu bạn không thể access server, tôi có thể cung cấp **full content** của 3 files để bạn tự tạo.

**Nhưng cách này dễ sai → Recommend: Copy từ server**

---

## 📞 Quick Command Reference

### Check if files are updated
```cmd
# Check preload.js
findstr "analyzeBatchFile" electron\preload.js

# Check main.js
findstr "analyze-batch-file" electron\main.js

# Check App.js
findstr "BatchScanner" src\App.js
```

### Backup before overwrite
```cmd
copy electron\preload.js electron\preload.js.backup
copy electron\main.js electron\main.js.backup
copy src\App.js src\App.js.backup
```

### Restore from backup if needed
```cmd
copy electron\preload.js.backup electron\preload.js
copy electron\main.js.backup electron\main.js
copy src\App.js.backup src\App.js
```

---

## ✅ Checklist

- [ ] Connected to server
- [ ] Downloaded `electron/preload.js`
- [ ] Downloaded `electron/main.js`
- [ ] Downloaded `src/App.js`
- [ ] Ran `check-files.bat` → All ✅
- [ ] Ran `fix-api-error.bat`
- [ ] App opened successfully
- [ ] Tested API in DevTools → `"function"`
- [ ] Clicked "Chọn file" → No error

---

## 🎯 Expected Results

**Before copy:**
```
❌ electron\preload.js - analyzeBatchFile NOT found
❌ electron\main.js - IPC handler NOT found
❌ src\App.js - BatchScanner NOT imported
```

**After copy:**
```
✅ electron\preload.js - analyzeBatchFile found
✅ electron\main.js - IPC handler found
✅ src\App.js - BatchScanner imported
```

---

**Copy 3 files → Run check-files.bat → Run fix-api-error.bat → Done! ✅**
