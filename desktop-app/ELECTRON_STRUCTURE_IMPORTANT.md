# 🚨 QUAN TRỌNG - Electron Structure

## ⚠️ LUÔN NHỚ KHI THÊM API MỚI

### ❌ SAI - Folder KHÔNG được load:
```
electron/
  ├── main.js        ← Không được load! (backup only)
  └── preload.js     ← Không được load! (backup only)
```

### ✅ ĐÚNG - Folder THỰC SỰ được dùng:
```
public/
  ├── electron.js    ← Main process (ĐƯỢC LOAD)
  └── preload.js     ← Preload script (ĐƯỢC LOAD) ⭐⭐⭐
```

---

## 📋 Quy trình thêm API mới:

### Bước 1: Thêm vào `public/preload.js`
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  // ... existing APIs ...
  
  // New API HERE ⭐
  yourNewAPI: (params) => ipcRenderer.invoke('your-new-api', params),
});
```

### Bước 2: Thêm handler vào `electron/main.js`
```javascript
ipcMain.handle('your-new-api', async (event, params) => {
  // Implementation here
  return result;
});
```

### Bước 3: (Optional) Sync sang `electron/preload.js`
Để consistency, nhưng file này KHÔNG được load!

---

## 🔍 Cách verify:

### Check xem Electron load file nào:
```javascript
// Trong public/electron.js
const mainWindow = new BrowserWindow({
  webPreferences: {
    preload: path.join(__dirname, 'preload.js') // ← Đây!
  }
});
```

**`__dirname` = `public/`** → Load `public/preload.js`

---

## 🐛 Lỗi phổ biến:

### Lỗi: `window.electronAPI.newAPI is not a function`

**Nguyên nhân:**
- ❌ Thêm vào `electron/preload.js` (sai folder!)
- ✅ Phải thêm vào `public/preload.js`

**Cách fix:**
1. Copy API từ `electron/preload.js`
2. Paste vào `public/preload.js`
3. Kill Electron processes
4. Xóa cache: `%APPDATA%\Electron`
5. Restart app

---

## 📝 Checklist khi thêm API:

- [ ] Thêm vào `public/preload.js` (QUAN TRỌNG!)
- [ ] Thêm handler vào `electron/main.js`
- [ ] Sync sang `electron/preload.js` (optional, để consistency)
- [ ] Build: `yarn build`
- [ ] Test: Verify trong Console (F12)

---

## 🎯 Các API đã thêm (lịch sử):

### 2024-11 - BatchScanner APIs
- `validateBatchFolders`
- `scanSingleFolder`
- `processBatchScan`
- `batchProcessDocuments`

**✅ Đã thêm vào:** `public/preload.js`

### 2024-11 - OnlyGCN APIs
- `getImagesInFolder`
- `preFilterGCNFiles`
- `mergeFolderPdfs`

**❌ Lần đầu thêm SAI:** `electron/preload.js` → Lỗi undefined
**✅ Đã fix:** Thêm vào `public/preload.js` → OK

---

## 💡 Nguyên tắc vàng:

1. **`public/` là nguồn chân lý** (source of truth)
2. **`electron/` chỉ là backup** (không được load)
3. **Luôn thêm API vào `public/preload.js` TRƯỚC**
4. **Verify bằng Console trước khi ship**

---

## 🔧 Quick fix script:

Nếu gặp lỗi API undefined:

```powershell
# Kill & clear cache
Stop-Process -Name "node", "electron" -Force
Remove-Item -Recurse -Force "$env:APPDATA\Electron"

# Restart
yarn electron-dev-win
```

---

**Ghi nhớ:** Mọi thay đổi về APIs phải vào `public/preload.js`!

**Last updated:** 2024-11-17
**Reason:** Lỗi OnlyGCN APIs undefined vì thêm sai folder
