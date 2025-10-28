# ✅ FIX BUILD ERROR - Node.js modules in React

## ❌ **LỖI:**

```
Module not found: Error: Can't resolve 'path' in 'C:\desktop-app\src\components'
Module not found: Error: Can't resolve 'fs' in ...
```

**Nguyên nhân:**
- React component (browser) không thể dùng `require('path')`, `require('fs')`
- Đây là Node.js modules, chỉ chạy trong backend

---

## ✅ **GIẢI PHÁP:**

### **1. Di chuyển logic sang Electron backend**

**Trước (React - ❌ SAI):**
```javascript
// Trong DesktopScanner.js
const path = require('path'); // ❌ Browser không có 'path'
const fs = require('fs');     // ❌ Browser không có 'fs'

let targetFolder = parentFolder;
if (mergeOption === 'new') {
  const newFolderName = path.basename(parentFolder) + mergeSuffix;
  targetFolder = path.join(path.dirname(parentFolder), newFolderName);
  fs.mkdirSync(targetFolder, { recursive: true });
}
```

**Sau (React - ✅ ĐÚNG):**
```javascript
// Trong DesktopScanner.js
// Chỉ truyền options xuống backend
const mergeOptions = {
  autoSave: true,
  mergeMode: mergeOption,    // 'root' or 'new'
  mergeSuffix: mergeSuffix,  // '_merged'
  parentFolder: parentFolder
};

const merged = await window.electronAPI.mergeByShortCode(payload, mergeOptions);
```

---

### **2. Xử lý logic trong Electron backend**

**File:** `electron/main.js` & `public/electron.js`

```javascript
// IPC Handler: merge-by-short-code
ipcMain.handle('merge-by-short-code', async (event, items, options = {}) => {
  // ...
  
  let targetDir;
  
  if (options.mergeMode === 'new' && options.parentFolder) {
    // Tạo thư mục mới: parentFolder + suffix
    const parentDir = path.dirname(options.parentFolder);
    const baseName = path.basename(options.parentFolder);
    const newFolderName = baseName + (options.mergeSuffix || '_merged');
    targetDir = path.join(parentDir, newFolderName);
    
    // Create folder
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
  } else if (options.mergeMode === 'root' && options.parentFolder) {
    // Gộp vào thư mục gốc
    targetDir = options.parentFolder;
  } else {
    // Default: folder của file đầu tiên
    targetDir = path.dirname(filePaths[0]);
  }
  
  // Save PDF to targetDir
  outputPath = path.join(targetDir, `${shortCode}.pdf`);
  // ...
});
```

---

### **3. Giữ lại preview folder name (không dùng path)**

**React có thể dùng string manipulation:**

```javascript
// ✅ OK trong browser
const folderName = parentFolder.split(/[\\\/]/).pop();
const preview = folderName + mergeSuffix; // "FolderName_merged"
```

---

## 📝 **FILES ĐÃ SỬA:**

### 1. `/app/desktop-app/src/components/DesktopScanner.js`
- ✅ Xóa `require('path')` và `require('fs')`
- ✅ Truyền mergeOptions xuống backend
- ✅ Dùng `.split()` thay vì `path.basename()`

### 2. `/app/desktop-app/electron/main.js`
- ✅ Thêm logic xử lý `mergeMode` và `mergeSuffix`
- ✅ Tạo folder mới nếu `mergeMode === 'new'`
- ✅ Gộp vào root nếu `mergeMode === 'root'`

### 3. `/app/desktop-app/public/electron.js`
- ✅ Mirror changes từ main.js

---

## 🧪 **TEST BUILD:**

```powershell
cd C:\desktop-app

# Clean
Remove-Item -Recurse -Force node_modules/.cache, build

# Build
npm run build
```

**Expected:** ✅ Build thành công, không có lỗi module

---

## 🎯 **KEY TAKEAWAY:**

| Module | Browser (React) | Node.js (Electron) |
|--------|----------------|--------------------|
| **path** | ❌ Không có | ✅ Có |
| **fs** | ❌ Không có | ✅ Có |
| **String methods** | ✅ Có | ✅ Có |

**Rule:**
- Browser: Chỉ logic UI, string manipulation
- Electron IPC: File system, path operations

---

## ✅ **STATUS:**

- ✅ Xóa Node.js modules khỏi React
- ✅ Di chuyển logic sang Electron backend
- ✅ Linting passed
- ✅ Ready to build

---

**Date:** 2025-01-28
**Fixed by:** AI Assistant
