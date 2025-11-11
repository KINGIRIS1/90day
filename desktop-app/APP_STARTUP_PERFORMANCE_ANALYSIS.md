# 🐌 App Startup Performance Analysis

## ⚠️ Vấn đề: Load app khi mở lại rất chậm

### Phân tích các nguyên nhân có thể:

---

## 1. ✅ PreviewUrl đã được strip (GOOD)

**Code hiện tại:**
```javascript
// DesktopScanner.js line 123-127
childTabs: childTabs.map(t => ({
  ...t,
  results: t.results?.map(r => ({ ...r, previewUrl: null })) || []
}))

// BatchScanner.js line 100-106
folderTabs: folderTabs.map(t => ({
  ...t,
  files: t.files?.map(f => ({ ...f, previewUrl: null })) || []
}))
```

**✅ Kết luận:** PreviewUrl KHÔNG được lưu vào config.json → Không phải nguyên nhân chính

---

## 2. ❌ Config.json có thể vẫn lớn do nhiều scans

**Kịch bản:**
```
User scan 100 folders trong 1 tuần
→ scanHistory có 100 entries
→ Mỗi entry có 50-200 files metadata
→ Total: 5,000-20,000 file records
→ config.json size: 5-20 MB

Electron-store load toàn bộ vào memory → CHẬM
```

**Auto-cleanup hiện tại:**
```javascript
// main.js line 1038-1073
// Chỉ cleanup scans > 7 ngày khi gọi get-incomplete-scans
// NHƯNG nếu user không scan mới → không cleanup → config.json vẫn lớn
```

---

## 3. ⚠️ Electron app startup overhead

### Các bước khi mở app:

```
1. Electron process launch (200-500ms)
2. Load config.json (10-100ms depending on size)
3. Create BrowserWindow (100-300ms)
4. Load React app (500-1500ms)
   ├── Parse & execute JavaScript bundles
   ├── Initialize React components
   ├── Load settings from config
   └── Check for incomplete scans
5. Ready to use

Total: 810-2400ms (0.8-2.4 seconds) NORMAL
```

**Nếu chậm hơn 3-5 seconds → VẤN ĐỀ**

---

## 4. 🔍 Các nguyên nhân có thể làm chậm:

### A. Config.json quá lớn
**Dấu hiệu:**
- File > 10 MB
- Có nhiều incomplete scans (> 50)
- Lưu quá nhiều metadata không cần thiết

**Check:**
```bash
# Windows
cd %APPDATA%\90dayChonThanh
dir config.json

# macOS/Linux
ls -lh ~/Library/Application\ Support/90dayChonThanh/config.json
```

### B. React app bundle lớn
**Dấu hiệu:**
- build/static/js/*.js > 5 MB total
- Chưa minify/optimize production build

### C. Python environment discovery chậm
**Dấu hiệu:**
- discoverPython() takes > 1s
- Windows "py launcher" probe multiple versions

### D. Electron DevTools auto-open (nếu dev mode)
```javascript
// main.js line 45
if (isDev) mainWindow.webContents.openDevTools(); // Chậm 500ms-1s
```

### E. Network check hoặc API calls khi startup
**Dấu hiệu:**
- App đợi network response
- Cloud OCR API key validation at startup

---

## 📊 Performance Benchmarks

### Normal Startup Times:

| Stage | Time | Total |
|-------|------|-------|
| Electron launch | 200ms | 200ms |
| Load config.json (< 1MB) | 10ms | 210ms |
| Create window | 150ms | 360ms |
| Load React (dev) | 1500ms | 1860ms |
| Load React (prod) | 500ms | 860ms |
| **Total (dev)** | - | **~2s** ✅ |
| **Total (prod)** | - | **~1s** ✅ |

### Slow Startup (VẤN ĐỀ):

| Scenario | Additional Time | Total |
|----------|----------------|-------|
| Config.json 20MB | +200ms | 2.2s |
| Config.json 100MB | +1000ms | 3s |
| Python discovery slow | +1000ms | 3s |
| Dev mode + DevTools | +1000ms | 3s |
| **Worst case** | +3000ms | **5s** ❌ |

---

## 🔧 Giải pháp tối ưu

### **Solution 1: Aggressive Auto-cleanup** ⭐ (Recommended)

**Hiện tại:** Cleanup scans > 7 ngày **khi gọi get-incomplete-scans**
**Vấn đề:** Nếu user không scan mới → không cleanup

**Giải pháp:** Cleanup **khi app startup** (trong main.js)

```javascript
// main.js - Add after app.whenReady()
app.whenReady().then(() => {
  // Auto-cleanup old scans on startup
  cleanupOldScans();
  
  createWindow();
  app.on('activate', () => { ... });
});

function cleanupOldScans() {
  try {
    const scanHistory = store.get('scanHistory', {});
    const now = Date.now();
    const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
    
    let cleaned = 0;
    for (const [scanId, scanData] of Object.entries(scanHistory)) {
      if (scanData.timestamp < sevenDaysAgo) {
        delete scanHistory[scanId];
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      store.set('scanHistory', scanHistory);
      console.log(`🗑️ Startup cleanup: Removed ${cleaned} old scans`);
    }
  } catch (e) {
    console.error('Cleanup error:', e);
  }
}
```

**Lợi ích:**
- ✅ Config.json luôn nhỏ (< 1 MB)
- ✅ Không cần user action
- ✅ Chạy nhanh (10-50ms)

---

### **Solution 2: Limit scanHistory size**

**Giới hạn tối đa 20 scans gần nhất:**

```javascript
// main.js - Modify save-scan-state handler
ipcMain.handle('save-scan-state', (event, scanData) => {
  try {
    const scanHistory = store.get('scanHistory', {});
    
    // Add new scan
    scanHistory[scanData.scanId] = scanData;
    
    // Limit to 20 most recent scans
    const entries = Object.entries(scanHistory)
      .sort((a, b) => b[1].timestamp - a[1].timestamp)
      .slice(0, 20); // Keep only 20 newest
    
    const limitedHistory = Object.fromEntries(entries);
    store.set('scanHistory', limitedHistory);
    
    console.log(`💾 Saved scan, total: ${entries.length}`);
    return { success: true, scanId: scanData.scanId };
  } catch (e) {
    console.error('Save error:', e);
    return { success: false, error: e.message };
  }
});
```

**Lợi ích:**
- ✅ Config.json không bao giờ quá lớn
- ✅ Performance ổn định
- ✅ Đủ history cho user (20 scans)

---

### **Solution 3: Separate storage cho scanHistory**

**Thay vì lưu trong config.json → Dùng separate file:**

```javascript
// main.js
const Store = require('electron-store');
const store = new Store(); // Config: settings, apiKeys
const scanStore = new Store({ name: 'scan-history' }); // Separate: scans

// Use scanStore thay vì store
ipcMain.handle('save-scan-state', (event, scanData) => {
  scanStore.set(`scans.${scanData.scanId}`, scanData); // Separate file
});
```

**Lợi ích:**
- ✅ Config.json luôn nhỏ (chỉ settings)
- ✅ scan-history.json load riêng (không ảnh hưởng startup)
- ✅ Có thể clear scan history mà không mất settings

---

### **Solution 4: Lazy load incomplete scans**

**Thay vì check ngay khi startup → Delay 2-3 seconds:**

```javascript
// DesktopScanner.js & BatchScanner.js
useEffect(() => {
  // Delay check for incomplete scans (don't block UI)
  const timer = setTimeout(async () => {
    const incompleteResult = await window.electronAPI.getIncompleteScans();
    if (incompleteResult.success && incompleteResult.scans.length > 0) {
      setIncompleteScans(incompleteResult.scans);
      setShowResumeDialog(true);
    }
  }, 2000); // Delay 2s
  
  return () => clearTimeout(timer);
}, []);
```

**Lợi ích:**
- ✅ App UI load nhanh (không đợi scan history)
- ✅ ResumeDialog xuất hiện sau 2s (không ảnh hưởng UX)

---

### **Solution 5: Production build optimization**

**Đảm bảo app đang chạy production build:**

```bash
# Build production
cd /app/desktop-app
npm run build

# Electron package
npm run electron-build
```

**Check DevTools:**
```javascript
// main.js line 45
if (isDev) mainWindow.webContents.openDevTools(); // ❌ Disable for production
```

---

## 🎯 Recommended Implementation Plan

### **Phase 1: Quick Wins** (5-10 minutes)

1. ✅ **Aggressive auto-cleanup** (Solution 1)
   - Add cleanupOldScans() to app.whenReady()
   - Remove scans > 7 days on startup

2. ✅ **Limit scanHistory** (Solution 2)
   - Keep only 20 most recent scans
   - Prevent config.json from growing

**Expected result:** Config.json < 1 MB → Startup ~1-2s ✅

---

### **Phase 2: If still slow** (30 minutes)

3. ✅ **Separate storage** (Solution 3)
   - Move scanHistory to separate file
   - Config.json only for settings

4. ✅ **Lazy load** (Solution 4)
   - Delay incomplete scan check by 2s
   - UI load immediately

**Expected result:** Startup < 1s ✅

---

### **Phase 3: Advanced** (if needed)

5. ✅ **Python discovery cache**
   - Cache Python path to avoid re-discovery
   
6. ✅ **React bundle optimization**
   - Code splitting
   - Lazy load heavy components

---

## 📊 Expected Performance Improvements

### Before optimization:
```
Config.json: 20 MB (100 scans × 200KB)
Startup time: 4-5 seconds ❌
User experience: Frustrating
```

### After Phase 1:
```
Config.json: < 1 MB (20 scans × 50KB)
Startup time: 1-2 seconds ✅
User experience: Acceptable
```

### After Phase 2:
```
Config.json: < 100 KB (settings only)
scan-history.json: < 1 MB (lazy loaded)
Startup time: < 1 second ✅
User experience: Excellent
```

---

## 🔍 Debug Commands

### Check config.json size:

**Windows:**
```cmd
cd %APPDATA%\90dayChonThanh
dir config.json
type config.json | find /c "scanId"
```

**macOS/Linux:**
```bash
cd ~/Library/Application\ Support/90dayChonThanh
ls -lh config.json
cat config.json | grep -c "scanId"
```

### Measure startup time:

**Add to main.js:**
```javascript
const startupTime = Date.now();

app.whenReady().then(() => {
  const elapsed = Date.now() - startupTime;
  console.log(`⏱️ App startup time: ${elapsed}ms`);
  
  createWindow();
});
```

---

## 🎯 Action Plan

**Bạn muốn tôi implement Solution nào?**

1. **Solution 1 + 2** (Recommended) ⭐
   - Aggressive cleanup + Limit 20 scans
   - Quick & effective
   - Estimated time: 5 minutes

2. **Solution 3** (If still slow)
   - Separate storage
   - Estimated time: 15 minutes

3. **All solutions** (Complete optimization)
   - Maximum performance
   - Estimated time: 30 minutes

**Hoặc tôi có thể:**
- Debug config.json size của bạn (nếu bạn share được)
- Measure actual startup time với logs
- Test từng solution step-by-step

Bạn muốn làm gì tiếp theo? 🚀
