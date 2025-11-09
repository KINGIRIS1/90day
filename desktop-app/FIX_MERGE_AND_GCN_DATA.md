# Fix: Merge Custom Folder & GCN Data Missing

## Ngày: January 2025
## Trạng thái: ✅ ĐÃ SỬA

---

## 🐛 Vấn Đề 1: Merge Custom Folder Vẫn Không Hoạt Động

### Console Logs Từ User
```javascript
🚀 executeMerge called: {
  mergeAll: false, 
  outputOption: 'custom_folder', 
  mergeSuffix: '_merged', 
  outputFolder: 'C:\\Users\\nguye\\OneDrive\\Máy tính\\AI'
}

Merge options: {
  autoSave: true, 
  mergeMode: 'custom', 
  mergeSuffix: '_merged', 
  parentFolder: '\\\\SERVERNAS\\Luutru\\2022\\1-2022\\5-01\\MINH HUNG\\16-384', 
  customOutputFolder: 'C:\\Users\\nguye\\OneDrive\\Máy tính\\AI'
}

// Không có logs từ main.js! ❌
```

### Root Cause
**Vấn đề:** Console logs từ `main.js` KHÔNG xuất hiện!

**Phân tích:**
1. BatchScanner.js GỬI đúng options (mergeMode: 'custom', customOutputFolder: '...')
2. NHƯNG main.js KHÔNG log gì cả
3. → main.js không dùng `options.parentFolder`!

**Code cũ (main.js line 653):**
```javascript
const childFolder = path.dirname(filePaths[0]); // ❌ Lấy từ filePath, không dùng options!
```

**Vấn đề:**
- BatchScanner gửi `parentFolder` trong options
- main.js KHÔNG đọc `options.parentFolder`
- main.js chỉ dùng `path.dirname(filePaths[0])`
- Với network path (`\\SERVERNAS\...`), `path.dirname()` có thể trả về path sai!

---

## ✅ Fix 1: Dùng `options.parentFolder` Trong main.js

### File: `/app/desktop-app/electron/main.js`

### Changes (Lines ~653-703)

#### Before:
```javascript
const childFolder = path.dirname(filePaths[0]);
```

#### After:
```javascript
// Use parentFolder from options if provided, otherwise get from filePath
const childFolder = options.parentFolder || path.dirname(filePaths[0]);

console.log(`📂 Merge processing for ${shortCode}:`);
console.log(`   childFolder: ${childFolder}`);
console.log(`   parentFolder (from options): ${options.parentFolder || 'null'}`);
console.log(`   mergeMode: ${options.mergeMode}`);
console.log(`   customOutputFolder: ${options.customOutputFolder || 'null'}`);
console.log(`   Files to merge: ${filePaths.length}`);
```

**Điểm mới:**
- ✅ Ưu tiên dùng `options.parentFolder` (từ BatchScanner)
- ✅ Fallback về `path.dirname(filePaths[0])` nếu không có
- ✅ Log cả 2 giá trị để debug

---

#### Enhanced Error Handling

```javascript
else if (options.mergeMode === 'custom' && options.customOutputFolder) {
  const childBaseName = path.basename(childFolder);
  targetDir = path.join(options.customOutputFolder, childBaseName);
  console.log(`   📁 Creating custom folder: ${targetDir}`);
  
  try {
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
      console.log(`   ✅ Created: ${targetDir}`);
    } else {
      console.log(`   ✅ Already exists: ${targetDir}`);
    }
  } catch (mkdirErr) {
    console.error(`   ❌ Failed to create directory: ${mkdirErr.message}`);
    throw new Error(`Cannot create output directory: ${targetDir}`);
  }
}
```

**Điểm mới:**
- ✅ Try-catch cho `fs.mkdirSync()`
- ✅ Throw error rõ ràng nếu không tạo được folder

---

#### Enhanced File Writing

```javascript
try {
  fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
  console.log(`   ✅ PDF written successfully: ${outputPath}`);
  results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true, autoSaved: true });
} catch (writeErr) {
  console.error(`   ❌ Failed to write PDF: ${writeErr.message}`);
  throw new Error(`Cannot write PDF to: ${outputPath} - ${writeErr.message}`);
}
```

**Điểm mới:**
- ✅ Try-catch cho `fs.writeFileSync()`
- ✅ Log success khi ghi file thành công
- ✅ Throw error rõ ràng nếu không ghi được

---

### Expected Console Logs (Sau khi fix)

```javascript
🚀 executeMerge called: {mergeAll: false, outputOption: 'custom_folder', ...}
Merge options: {autoSave: true, mergeMode: 'custom', customOutputFolder: 'C:\\Users\\nguye\\OneDrive\\Máy tính\\AI', ...}

📂 Merge processing for HDCQ:
   childFolder: \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   parentFolder (from options): \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   mergeMode: custom
   customOutputFolder: C:\Users\nguye\OneDrive\Máy tính\AI
   Files to merge: 3
   📁 Creating custom folder: C:\Users\nguye\OneDrive\Máy tính\AI\16-384
   ✅ Created: C:\Users\nguye\OneDrive\Máy tính\AI\16-384
   🎯 Final output path: C:\Users\nguye\OneDrive\Máy tính\AI\16-384\HDCQ.pdf
   ✅ PDF written successfully: C:\Users\nguye\OneDrive\Máy tính\AI\16-384\HDCQ.pdf

📂 Merge processing for GCNM:
   childFolder: \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   parentFolder (from options): \\SERVERNAS\Luutru\2022\1-2022\5-01\MINH HUNG\16-384
   mergeMode: custom
   customOutputFolder: C:\Users\nguye\OneDrive\Máy tính\AI
   Files to merge: 2
   ✅ Already exists: C:\Users\nguye\OneDrive\Máy tính\AI\16-384
   🎯 Final output path: C:\Users\nguye\OneDrive\Máy tính\AI\16-384\GCNM.pdf
   ✅ PDF written successfully: C:\Users\nguye\OneDrive\Máy tính\AI\16-384\GCNM.pdf
```

---

## 🐛 Vấn Đề 2: GCN Không Tìm Thấy Color và Date

### Console Logs Từ User
```javascript
🔄 Post-processing GCN batch (DATE-BASED classification)...
📋 Found 4 GCN document(s) to process
  🎨 Unique colors: none
  ⚠️ No dates found → Default all to GCNM
```

### Root Cause
**Vấn đề:** `postProcessGCNBatch()` không tìm thấy `color` và `issue_date`!

**Phân tích:**
```javascript
// BatchScanner.js line 322-332 (OLD)
const fileWithPreview = {
  filePath: imagePath,
  fileName: fileName,
  short_code: fileResult.short_code || 'UNKNOWN',
  doc_type: fileResult.doc_type || 'Unknown',
  confidence: fileResult.confidence || 0,
  // ❌ THIẾU: color, issue_date, issue_date_confidence
};
```

**Gemini trả về:**
```javascript
fileResult = {
  short_code: 'GCN',
  confidence: 0.95,
  color: 'pink',               // ✅ Có
  issue_date: '14/04/2025',    // ✅ Có
  issue_date_confidence: 'full' // ✅ Có
};
```

**NHƯNG:** BatchScanner KHÔNG copy 3 fields này vào `fileWithPreview`!

→ `postProcessGCNBatch()` nhận object không có `color`, `issue_date`
→ Không phân loại được → Default all to GCNM

---

## ✅ Fix 2: Copy GCN Fields Vào fileWithPreview

### File: `/app/desktop-app/src/components/BatchScanner.js`

### Changes (Lines ~322-334)

#### Before:
```javascript
const fileWithPreview = {
  filePath: imagePath,
  fileName: fileName,
  short_code: fileResult.short_code || 'UNKNOWN',
  doc_type: fileResult.doc_type || 'Unknown',
  confidence: fileResult.confidence || 0,
  folder: folder.path,
  previewUrl: previewUrl,
  success: true,
  method: fileResult.method || 'offline_ocr'
  // ❌ THIẾU GCN fields
};
```

#### After:
```javascript
const fileWithPreview = {
  filePath: imagePath,
  fileName: fileName,
  short_code: fileResult.short_code || 'UNKNOWN',
  doc_type: fileResult.doc_type || 'Unknown',
  confidence: fileResult.confidence || 0,
  folder: folder.path,
  previewUrl: previewUrl,
  success: true,
  method: fileResult.method || 'offline_ocr',
  // ✅ GCN fields for post-processing
  color: fileResult.color || null,
  issue_date: fileResult.issue_date || null,
  issue_date_confidence: fileResult.issue_date_confidence || null
};
```

**Điểm mới:**
- ✅ Copy `color` từ Gemini response
- ✅ Copy `issue_date` từ Gemini response
- ✅ Copy `issue_date_confidence` từ Gemini response

---

### Add Debug Logs (Lines ~297-308)

```javascript
// Scan single file
let fileResult = await window.electronAPI.processDocumentOffline(imagePath);

// Debug: Log GCN fields if present
if (fileResult.short_code === 'GCN' || fileResult.short_code === 'GCNM' || fileResult.short_code === 'GCNC') {
  console.log(`  🔍 GCN detected:`, {
    file: fileName,
    short_code: fileResult.short_code,
    color: fileResult.color || 'null',
    issue_date: fileResult.issue_date || 'null',
    issue_date_confidence: fileResult.issue_date_confidence || 'null'
  });
}

// Apply sequential naming...
```

**Mục đích:** Verify xem Gemini có trả về `color` và `issue_date` không

---

### Expected Console Logs (Sau khi fix)

```javascript
[1/4] Processing: file001.jpg
  🔍 GCN detected: {
    file: 'file001.jpg',
    short_code: 'GCN',
    color: 'red',
    issue_date: 'null',
    issue_date_confidence: 'null'
  }
  ✅ GCN - 95%

[2/4] Processing: file002.jpg
  🔍 GCN detected: {
    file: 'file002.jpg',
    short_code: 'GCN',
    color: 'red',
    issue_date: '27/10/2021',
    issue_date_confidence: 'full'
  }
  ✅ GCN - 95%

[3/4] Processing: file003.jpg
  🔍 GCN detected: {
    file: 'file003.jpg',
    short_code: 'GCN',
    color: 'pink',
    issue_date: 'null',
    issue_date_confidence: 'null'
  }
  ✅ GCN - 96%

[4/4] Processing: file004.jpg
  🔍 GCN detected: {
    file: 'file004.jpg',
    short_code: 'GCN',
    color: 'pink',
    issue_date: '14/04/2025',
    issue_date_confidence: 'full'
  }
  ✅ GCN - 96%

🔄 Post-processing GCN batch (DATE-BASED classification)...
📋 Found 4 GCN document(s) to process
  🎨 Unique colors: red, pink
  🎨 Mixed colors → Classify by color
  🎨 Pair 1: Màu red → GCNC
  🎨 Pair 2: Màu pink → GCNM
✅ GCN post-processing complete
```

---

## 📋 Test Instructions

### Test 1: Merge Custom Folder (QUAN TRỌNG!)

**Steps:**
1. Batch scan 1 folder với network path: `\\SERVERNAS\...\Folder1\`
2. Click "Gộp PDF" → "Sao chép vào thư mục khác"
3. Chọn: `C:\Users\nguye\OneDrive\Máy tính\AI\`
4. **MỞ DEVTOOLS (F12)** → Console tab
5. Click "Gộp PDF"

**Expected Console Logs:**
```
📂 Merge processing for HDCQ:
   childFolder: \\SERVERNAS\...\Folder1
   parentFolder (from options): \\SERVERNAS\...\Folder1
   mergeMode: custom
   customOutputFolder: C:\Users\nguye\OneDrive\Máy tính\AI
   Files to merge: 3
   📁 Creating custom folder: C:\Users\nguye\OneDrive\Máy tính\AI\Folder1
   ✅ Created: C:\Users\nguye\OneDrive\Máy tính\AI\Folder1
   🎯 Final output path: C:\Users\nguye\OneDrive\Máy tính\AI\Folder1\HDCQ.pdf
   ✅ PDF written successfully: C:\Users\nguye\OneDrive\Máy tính\AI\Folder1\HDCQ.pdf
```

**Expected File System:**
```
C:\Users\nguye\OneDrive\Máy tính\AI\
  └── Folder1\
      ├── HDCQ.pdf ✅
      ├── GCNM.pdf ✅
      └── DKTC.pdf ✅
```

**Nếu vẫn lỗi:**
- Share full console logs (copy/paste hoặc screenshot)
- Check error messages (❌ Failed to...)
- Check quyền ghi vào `C:\Users\nguye\OneDrive\Máy tính\AI\`

---

### Test 2: GCN Color & Date Detection

**Steps:**
1. Scan folder với 4 file GCN (2 màu đỏ, 2 màu hồng)
2. **MỞ DEVTOOLS (F12)** → Console tab
3. Xem logs khi scan

**Expected Console Logs:**
```
  🔍 GCN detected: {color: 'red', issue_date: '27/10/2021', ...}
  🔍 GCN detected: {color: 'red', issue_date: 'null', ...}
  🔍 GCN detected: {color: 'pink', issue_date: '14/04/2025', ...}
  🔍 GCN detected: {color: 'pink', issue_date: 'null', ...}

🔄 Post-processing GCN batch...
  🎨 Unique colors: red, pink
  🎨 Mixed colors → Classify by color
```

**Nếu vẫn "🎨 Unique colors: none":**
- Gemini KHÔNG detect được màu
- → Có thể do ảnh không rõ
- → Hoặc Gemini Lite không đủ mạnh
- → Thử Gemini Flash (full) hoặc check ảnh

---

## 📊 Summary

| Issue | Fix | Status |
|-------|-----|--------|
| Merge custom folder không hoạt động | Dùng `options.parentFolder` trong main.js | ✅ Fixed |
| GCN không có color/date | Copy GCN fields vào fileWithPreview | ✅ Fixed |
| Không có debug logs | Thêm console logs chi tiết | ✅ Added |

**Files Modified:**
- `/app/desktop-app/electron/main.js` (lines ~653-703)
- `/app/desktop-app/src/components/BatchScanner.js` (lines ~297-334)

**Total Changes:** ~50 lines

---

## 🙏 Vui Lòng Test & Share Logs

**Cần:**
1. Console logs (copy/paste hoặc screenshot) cho cả 2 tests
2. File system results (PDF có được tạo đúng chỗ không?)
3. GCN classification results (GCNC/GCNM có đúng không?)

Cảm ơn! 🇻🇳
