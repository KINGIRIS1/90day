# Debug: Merge Custom Folder Không Hoạt Động

## Ngày: January 2025
## Trạng thái: 🔍 DEBUGGING

---

## 🐛 Vấn Đề

### Báo Cáo Từ User
> "Kiểm tra lại tính năng gộp vào thư mục chỉ định vẫn không được. Hình như app không tạo được thư mục trong thư mục khác."

### Console Logs (Renderer Process)
```javascript
Merge options: {
  autoSave: true, 
  mergeMode: 'custom', 
  mergeSuffix: '_merged', 
  parentFolder: '\\\\SERVERNAS\\Luutru\\2022\\1-2022\\5-01\\MINH HUNG\\16-384', 
  customOutputFolder: 'D:\\APP'
}
```

**Vấn đề:** KHÔNG có logs từ main.js (Electron main process)!

---

## 🔍 Phân Tích

### Có 3 Khả Năng

#### 1. IPC Handler Không Được Gọi
- BatchScanner gọi `window.electronAPI.mergeByShortCode()`
- Nhưng main.js handler KHÔNG chạy
- Có thể do:
  - IPC channel name sai
  - preload.js không expose API đúng
  - Electron context isolation issues

#### 2. Handler Chạy Nhưng Error Bị Nuốt
- Handler chạy
- Error xảy ra khi tạo folder
- Error không được log ra console
- Promise rejection không được handle

#### 3. Permission Issues
- Handler chạy OK
- `fs.mkdirSync()` fail do permissions
- Windows UAC block
- Drive D: có read-only?

---

## ✅ Fixes Applied

### Fix 1: Thêm Extensive Logging

**File:** `/app/desktop-app/electron/main.js` (Lines ~627-745)

#### Log đầu handler:
```javascript
ipcMain.handle('merge-by-short-code', async (event, items, options = {}) => {
  console.log('='.repeat(80));
  console.log('🚀 MERGE HANDLER CALLED IN MAIN.JS');
  console.log('📦 Items count:', items.length);
  console.log('⚙️ Options:', JSON.stringify(options, null, 2));
  console.log('='.repeat(80));
  // ...
});
```

**Mục đích:** Verify handler có được gọi không

---

#### Log groups:
```javascript
console.log('📊 Groups created:', Object.keys(groups).join(', '));
console.log('📊 Group details:', Object.entries(groups).map(([k, v]) => `${k}: ${v.length} files`).join(', '));
```

**Mục đích:** Verify items được group đúng chưa

---

#### Log custom folder creation:
```javascript
console.log(`📁 Attempting to create custom folder:`);
console.log(`   customOutputFolder: ${options.customOutputFolder}`);
console.log(`   childBaseName: ${childBaseName}`);
console.log(`   targetDir: ${targetDir}`);

// Check if custom folder exists
if (!fs.existsSync(options.customOutputFolder)) {
  console.error(`❌ Custom output folder does not exist: ${options.customOutputFolder}`);
  throw new Error(`Custom output folder does not exist: ${options.customOutputFolder}`);
}

// Check write permission
try {
  fs.accessSync(options.customOutputFolder, fs.constants.W_OK);
  console.log(`✅ Write permission OK for: ${options.customOutputFolder}`);
} catch (permErr) {
  console.error(`❌ No write permission for: ${options.customOutputFolder}`);
  throw new Error(`No write permission for custom folder: ${options.customOutputFolder}`);
}

// Create subfolder
fs.mkdirSync(targetDir, { recursive: true });
console.log(`✅ Subfolder created successfully: ${targetDir}`);
```

**Mục đích:** Debug từng step của folder creation

---

#### Log file writing:
```javascript
try {
  fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
  console.log(`✅ PDF written successfully: ${outputPath}`);
  results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true, autoSaved: true });
} catch (writeErr) {
  console.error(`❌ Failed to write PDF: ${writeErr.message}`);
  throw new Error(`Cannot write PDF to: ${outputPath} - ${writeErr.message}`);
}
```

**Mục đích:** Verify file được ghi thành công

---

#### Log cuối handler:
```javascript
console.log('='.repeat(80));
console.log('✅ MERGE HANDLER COMPLETED');
console.log('📊 Results:', results.map(r => `${r.short_code}: ${r.success ? '✅' : '❌'}`).join(', '));
console.log('='.repeat(80));

return results;
```

**Mục đích:** Verify handler hoàn thành và trả về kết quả

---

### Fix 2: Permission Checks

**Checks trước khi tạo folder:**

1. **Check folder exists:**
   ```javascript
   if (!fs.existsSync(options.customOutputFolder)) {
     throw new Error(`Custom output folder does not exist`);
   }
   ```

2. **Check write permission:**
   ```javascript
   fs.accessSync(options.customOutputFolder, fs.constants.W_OK);
   ```

3. **Try create subfolder:**
   ```javascript
   fs.mkdirSync(targetDir, { recursive: true });
   ```

**Mục đích:** Catch errors sớm với messages rõ ràng

---

### Fix 3: Enhanced Error Logging

```javascript
catch (err) {
  console.error('❌ Merge error for', shortCode, ':', err.message);
  console.error('   Stack:', err.stack);
  results.push({ short_code: shortCode, error: err.message, success: false });
}
```

**Mục đích:** Log full error stack để debug

---

## 📋 Testing Instructions (QUAN TRỌNG!)

### Step 1: Open Electron DevTools

**Windows:**
1. Mở app
2. Press `Ctrl + Shift + I` để mở DevTools
3. Chọn tab **Console**
4. Keep DevTools open!

**Note:** DevTools của Electron main process KHÁC với renderer process!

---

### Step 2: Check Current Console

**Verify console đang xem:**
- **Renderer Console:** Logs từ React (BatchScanner.js)
- **Main Console:** Logs từ Electron (main.js)

**To view Main Console:**
1. In DevTools, click dropdown ở top (có thể thấy "top" hoặc "Electron")
2. Chọn "Electron" hoặc "main"
3. Hoặc: Check terminal nơi app được run (nếu run từ `npm start`)

---

### Step 3: Perform Merge

**Steps:**
1. Batch scan 1 folder
2. Click "Gộp PDF"
3. Select "Sao chép vào thư mục khác"
4. Choose: `D:\APP\` (hoặc folder khác)
5. Click "Gộp PDF"
6. **WATCH CONSOLE CAREFULLY**

---

### Step 4: Analyze Logs

#### Scenario A: Handler Được Gọi ✅

**Expected logs (Main Console):**
```
================================================================================
🚀 MERGE HANDLER CALLED IN MAIN.JS
📦 Items count: 15
⚙️ Options: {
  "autoSave": true,
  "mergeMode": "custom",
  "mergeSuffix": "_merged",
  "parentFolder": "\\\\SERVERNAS\\Luutru\\2022\\1-2022\\5-01\\MINH HUNG\\16-384",
  "customOutputFolder": "D:\\APP"
}
================================================================================
📊 Groups created: HDCQ, GCNM, DKTC
📊 Group details: HDCQ: 5 files, GCNM: 8 files, DKTC: 2 files

📂 Merge processing for HDCQ:
   childFolder: \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   parentFolder (from options): \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   mergeMode: custom
   customOutputFolder: D:\APP
   Files to merge: 5
   📁 Attempting to create custom folder:
      customOutputFolder: D:\APP
      childBaseName: 16-384
      targetDir: D:\APP\16-384
   ✅ Write permission OK for: D:\APP
   ✅ Subfolder created successfully: D:\APP\16-384
   🎯 Final output path: D:\APP\16-384\HDCQ.pdf
   ✅ PDF written successfully: D:\APP\16-384\HDCQ.pdf

[... repeat for GCNM, DKTC ...]

================================================================================
✅ MERGE HANDLER COMPLETED
📊 Results: HDCQ: ✅, GCNM: ✅, DKTC: ✅
================================================================================
```

**Action:** Merge thành công! Check `D:\APP\16-384\` để verify files.

---

#### Scenario B: Handler KHÔNG Được Gọi ❌

**Observed:**
- Renderer logs: `🚀 executeMerge called`, `Merge options: {...}`
- **NHƯNG KHÔNG CÓ logs từ main.js!**

**Possible causes:**
1. IPC channel name mismatch
2. preload.js không expose API
3. Context isolation issues

**Debug steps:**
1. Check `preload.js` có `mergeByShortCode` không?
2. Check `window.electronAPI` có tồn tại không?
3. Try add log trong `preload.js`:
   ```javascript
   mergeByShortCode: (items, options) => {
     console.log('📡 preload.js: mergeByShortCode called');
     return ipcRenderer.invoke('merge-by-short-code', items, options);
   }
   ```

---

#### Scenario C: Error Khi Tạo Folder ❌

**Observed logs:**
```
🚀 MERGE HANDLER CALLED IN MAIN.JS
📦 Items count: 15
...
📁 Attempting to create custom folder:
   customOutputFolder: D:\APP
   childBaseName: 16-384
   targetDir: D:\APP\16-384
❌ Custom output folder does not exist: D:\APP
```

**Cause:** Folder `D:\APP` không tồn tại!

**Solution:** Tạo folder `D:\APP` trước, hoặc chọn folder khác tồn tại.

---

**Observed logs:**
```
📁 Attempting to create custom folder:
   ...
❌ No write permission for: D:\APP
```

**Cause:** Không có quyền ghi vào `D:\APP`!

**Solution:**
1. Check folder properties → Security tab
2. Ensure current user có "Write" permission
3. Try chọn folder khác (ví dụ: `C:\Users\[YourName]\Desktop\`)

---

**Observed logs:**
```
📁 Creating subfolder: D:\APP\16-384
❌ Failed to create directory: [Error details]
   Error code: EACCES
   Error message: permission denied
```

**Cause:** Windows UAC hoặc folder read-only

**Solution:**
1. Run app as Administrator
2. Check folder không bị read-only
3. Try khác drive (C: thay vì D:)

---

#### Scenario D: Error Khi Ghi File ❌

**Observed logs:**
```
✅ Subfolder created successfully: D:\APP\16-384
🎯 Final output path: D:\APP\16-384\HDCQ.pdf
❌ Failed to write PDF: [Error details]
```

**Cause:** Có thể do:
- Disk full
- Antivirus block
- File đang được mở bởi app khác

**Solution:**
1. Check disk space
2. Temporarily disable antivirus
3. Close apps có thể đang lock file

---

## 🔧 Workarounds

### Workaround 1: Test với Path Đơn Giản

Thay vì:
```
Custom folder: D:\APP\
```

Thử:
```
Custom folder: C:\Temp\
```

Hoặc:
```
Custom folder: C:\Users\[YourName]\Desktop\TestMerge\
```

**Mục đích:** Verify vấn đề có phải do path phức tạp không

---

### Workaround 2: Check Drive D: Permissions

```powershell
# PowerShell: Check if D:\APP exists and writable
Test-Path "D:\APP"
# Should return True

# Try create file
New-Item -Path "D:\APP\test.txt" -ItemType File -Value "test"
# If error → permission issue
```

---

### Workaround 3: Run App as Administrator

1. Right-click app icon
2. "Run as administrator"
3. Try merge again

**Note:** Chỉ temporary, không phải solution lâu dài

---

## 📊 Expected File Structure (Sau khi merge thành công)

```
D:\APP\
  └── 16-384\              ← Subfolder tên giống source folder
      ├── HDCQ.pdf         ← Merged PDF
      ├── GCNM.pdf
      ├── DKTC.pdf
      └── HSKT.pdf
```

**Verify:**
1. `D:\APP\16-384\` folder được tạo? ✅
2. PDF files có bên trong? ✅
3. Mở PDF để verify nội dung? ✅

---

## 🙏 Information Needed

**Vui lòng share:**

1. **Full console logs** (BOTH Renderer AND Main):
   - Copy/paste hoặc screenshot
   - From "🚀 executeMerge called" đến end

2. **Error messages** (nếu có):
   - "Custom folder does not exist"?
   - "No write permission"?
   - "Failed to create directory"?
   - Error code?

3. **File system state:**
   - `D:\APP` có tồn tại không?
   - Bạn có quyền ghi vào `D:\APP` không?
   - Try tạo file thủ công trong `D:\APP` → OK?

4. **App run mode:**
   - Run từ installer?
   - Run từ `npm start`?
   - Run as Administrator?

---

## 💡 Quick Test

**Test minimal case:**
```
1. Tạo folder: C:\TestMerge\
2. Batch scan 1 folder nhỏ (5-10 files)
3. Merge → Custom folder → C:\TestMerge\
4. Check console logs
5. Check C:\TestMerge\ có folder con không?
```

**Nếu test này pass:**
→ Vấn đề là với `D:\APP` path
→ Try different drive/folder

**Nếu test này fail:**
→ Vấn đề là logic merge
→ Share full logs để debug tiếp

---

Cảm ơn! 🇻🇳
