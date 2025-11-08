# Hướng dẫn Paste Files Manually

## 🎯 Vì bạn không thể SCP, hãy paste manual!

Tôi đã tạo 3 files TXT với full content. Bạn chỉ cần:
1. Mở file TXT
2. Copy tất cả
3. Paste vào file tương ứng

---

## 📝 File 1: electron/preload.js

### Bước 1: Mở file
```
C:\your-path\desktop-app\FILE_1_preload.js.txt
```

### Bước 2: Select All (Ctrl+A) → Copy (Ctrl+C)

### Bước 3: Paste vào
```
C:\your-path\desktop-app\electron\preload.js
```

**Chi tiết:**
1. Mở Notepad++/VSCode
2. Open: `desktop-app\electron\preload.js`
3. Select All (Ctrl+A)
4. Delete
5. Paste content từ `FILE_1_preload.js.txt`
6. Save (Ctrl+S)

---

## 📝 File 2: electron/main.js

**⚠️ Quan trọng:** File main.js RẤT DÀI (500+ dòng)

Thay vì paste toàn bộ, chỉ cần **THÊM** đoạn code sau:

### Tìm dòng này trong main.js (khoảng line 176):
```javascript
ipcMain.handle('select-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'] },
      { name: 'PDFs', extensions: ['pdf'] }
    ]
  });
  return result.filePaths;
});
```

### THÊM đoạn code này NGAY SAU dòng trên:

```javascript
// Batch scanning - select CSV/Excel file
ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    title: options?.title || 'Select File',
    filters: options?.filters || []
  });
  return {
    success: !result.canceled,
    canceled: result.canceled,
    filePath: result.canceled ? null : result.filePaths[0]
  };
});

// Batch scanning - analyze CSV/Excel file
ipcMain.handle('analyze-batch-file', async (event, csvFilePath) => {
  const pyInfo = discoverPython();
  if (!pyInfo.ok) {
    return { success: false, error: 'Python not found' };
  }
  
  const batchScriptPath = isDev 
    ? path.join(__dirname, '../python/batch_scanner.py')
    : getPythonScriptPath('batch_scanner.py');
  
  return new Promise((resolve) => {
    const child = spawn(pyInfo.executable, [batchScriptPath, csvFilePath], {
      env: buildPythonEnv({}, pyInfo, path.dirname(batchScriptPath))
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          resolve({ success: false, error: `Failed to parse JSON: ${e.message}` });
        }
      } else {
        resolve({ success: false, error: stderr || `Process exited with code ${code}` });
      }
    });
    
    // Timeout after 30 seconds
    setTimeout(() => {
      try {
        child.kill();
      } catch {}
      resolve({ success: false, error: 'Analysis timeout' });
    }, 30000);
  });
});
```

---

## 📝 File 3: src/App.js

### Tìm dòng này (khoảng line 1-7):
```javascript
import React, { useState, useEffect } from 'react';
import './App.css';
import DesktopScanner from './components/DesktopScanner';
import Settings from './components/Settings';
import RulesManager from './components/RulesManager';
import CloudSettings from './components/CloudSettings';
```

### THÊM dòng này NGAY SAU:
```javascript
import BatchScanner from './components/BatchScanner';
```

### Sau đó, tìm section với buttons (khoảng line 188-210):
```javascript
              <button
                onClick={() => setActiveTab('rules')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'rules' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📋 Rules
              </button>
```

### THÊM button này TRƯỚC button "📋 Rules":
```javascript
              <button
                onClick={() => setActiveTab('batch')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'batch' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📋 Quét danh sách
              </button>
```

### Cuối cùng, tìm section render tabs (khoảng line 278-290):
```javascript
        {/* Rules tab - rendered after first visit, just hidden when not active */}
        {visitedTabs.has('rules') && (
          <div style={{ display: activeTab === 'rules' ? 'block' : 'none' }}>
            <RulesManager />
          </div>
        )}
```

### THÊM đoạn này TRƯỚC section "Rules tab":
```javascript
        {/* Batch Scanner tab - rendered after first visit, just hidden when not active */}
        {visitedTabs.has('batch') && (
          <div style={{ display: activeTab === 'batch' ? 'block' : 'none' }}>
            <BatchScanner />
          </div>
        )}
```

---

## ✅ Verify sau khi paste

```cmd
check-files.bat
```

Phải thấy:
```
✅ electron\preload.js - analyzeBatchFile found
✅ electron\main.js - IPC handler found
✅ src\App.js - BatchScanner imported
```

Sau đó:
```cmd
fix-api-error.bat
```

---

## 💡 Tips

- Dùng **VSCode** hoặc **Notepad++** để paste (không dùng Notepad thường)
- **Backup files cũ** trước khi paste
- **Save All** sau khi paste
- Kiểm tra kỹ **indentation** (dùng spaces, không dùng tabs)

---

## 🚨 Nếu quá phức tạp

**Option dễ nhất:** Tôi tạo file ZIP với 3 files đã sửa, bạn extract và overwrite!

Bạn muốn tôi tạo ZIP không?
