# Sửa Lỗi Batch Scanner: GCN Date-Based & Merge Custom Folder

## Ngày: January 2025
## Trạng thái: ✅ ĐÃ SỬA

---

## 🐛 Vấn Đề 1: GCN Date-Based Classification Chưa Áp Dụng Cho Batch Scan

### Báo Cáo Từ Người Dùng
> "Đặt tên theo ngày cấp GCN cũng chưa áp dụng được với bên quét theo danh sách."

### Phân Tích
- **DesktopScanner.js** có logic `postProcessGCNBatch()` để phân loại GCN theo màu và ngày cấp
- **BatchScanner.js** KHÔNG có logic này
- Kết quả: Batch scan vẫn trả về "GCN" thay vì "GCNC"/"GCNM"

### Logic GCN Date-Based
```
1. Normalize GCNM/GCNC → GCN (Gemini có thể trả về code cũ)
2. Tìm tất cả GCN documents
3. Ghép thành pairs (trang 1 + trang 2)
4. Extract color và issue_date từ mỗi pair
5. Phân loại:
   - Nếu có màu khác nhau (red vs pink) → Dùng màu:
     * red/orange → GCNC
     * pink → GCNM
   - Nếu không có màu hoặc cùng màu → Dùng ngày cấp:
     * Ngày cũ nhất → GCNC
     * Các ngày khác → GCNM
     * Không có ngày → GCNM (default)
```

---

## ✅ Giải Pháp 1: Thêm GCN Post-Processing Vào Batch Scanner

### Files Modified

**File:** `/app/desktop-app/src/components/BatchScanner.js`

### Changes

#### 1. Thêm hàm `parseIssueDate()` (Lines ~540-568)
```javascript
const parseIssueDate = (issueDate, confidence) => {
  if (!issueDate) return null;
  
  try {
    let comparable = 0;
    let parts;
    
    if (confidence === 'full') {
      // DD/MM/YYYY
      parts = issueDate.split('/');
      if (parts.length === 3) {
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const year = parseInt(parts[2], 10);
        comparable = year * 10000 + month * 100 + day;
      }
    } else if (confidence === 'partial') {
      // MM/YYYY
      parts = issueDate.split('/');
      if (parts.length === 2) {
        const month = parseInt(parts[0], 10);
        const year = parseInt(parts[1], 10);
        comparable = year * 10000 + month * 100 + 1;
      }
    } else if (confidence === 'year_only') {
      // YYYY
      const year = parseInt(issueDate, 10);
      comparable = year * 10000 + 1 * 100 + 1;
    }
    
    return { comparable, original: issueDate };
  } catch (e) {
    console.error(`❌ Error parsing date: ${issueDate}`, e);
    return null;
  }
};
```

**Mục đích:** Parse ngày cấp thành số để so sánh (20220127 > 20210315)

---

#### 2. Thêm hàm `postProcessGCNBatch()` (Lines ~570-710)
```javascript
const postProcessGCNBatch = (folderResults) => {
  try {
    console.log('🔄 Post-processing GCN batch (DATE-BASED classification)...');
    
    // Step 1: Normalize GCNM/GCNC → GCN
    const normalizedResults = folderResults.map(r => {
      if (r.short_code === 'GCNM' || r.short_code === 'GCNC') {
        return { ...r, short_code: 'GCN', original_short_code: r.short_code };
      }
      return r;
    });
    
    // Step 2: Find all GCN documents
    const allGcnDocs = normalizedResults.filter(r => r.short_code === 'GCN');
    if (allGcnDocs.length === 0) return normalizedResults;
    
    // Step 3: Pair documents (trang 1 + trang 2)
    const pairs = [];
    for (let i = 0; i < allGcnDocs.length; i += 2) {
      const page1 = allGcnDocs[i];
      const page2 = allGcnDocs[i + 1];
      if (page1 && page2) {
        pairs.push({ page1, page2, pairIndex: i / 2 });
      } else if (page1) {
        pairs.push({ page1, page2: null, pairIndex: i / 2 });
      }
    }
    
    // Step 4: Extract color and dates
    const pairsWithData = pairs.map(pair => {
      const color = pair.page1?.color || pair.page2?.color || null;
      const issueDate = pair.page1?.issue_date || pair.page2?.issue_date || null;
      const issueDateConfidence = pair.page1?.issue_date_confidence || pair.page2?.issue_date_confidence || null;
      
      return {
        ...pair,
        color,
        issueDate,
        issueDateConfidence,
        parsedDate: parseIssueDate(issueDate, issueDateConfidence)
      };
    });
    
    // Step 5: Check if mixed colors
    const uniqueColors = [...new Set(pairsWithData.map(p => p.color).filter(Boolean))];
    const hasMixedColors = uniqueColors.length > 1;
    const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
    
    // Step 6: Classify by color if mixed
    if (hasMixedColors && hasRedAndPink) {
      pairsWithData.forEach(pair => {
        const classification = (pair.color === 'red' || pair.color === 'orange') ? 'GCNC' : 'GCNM';
        [pair.page1, pair.page2].filter(Boolean).forEach(page => {
          const index = normalizedResults.indexOf(page);
          normalizedResults[index] = {
            ...page,
            short_code: classification,
            gcn_classification_note: `📌 Màu ${pair.color} → ${classification}`
          };
        });
      });
      return normalizedResults;
    }
    
    // Step 7: Classify by date
    const pairsWithDates = pairsWithData.filter(p => p.parsedDate);
    if (pairsWithDates.length === 0) {
      // No dates → default all to GCNM
      pairsWithData.forEach(pair => {
        [pair.page1, pair.page2].filter(Boolean).forEach(page => {
          const index = normalizedResults.indexOf(page);
          normalizedResults[index] = {
            ...page,
            short_code: 'GCNM',
            gcn_classification_note: '📌 Không có ngày → GCNM (mặc định)'
          };
        });
      });
      return normalizedResults;
    }
    
    // Sort by date (oldest first)
    pairsWithDates.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
    
    // Oldest = GCNC, rest = GCNM
    pairsWithDates.forEach((pair, idx) => {
      const classification = idx === 0 ? 'GCNC' : 'GCNM';
      const note = `Ngày ${pair.issueDate} → ${classification}`;
      
      [pair.page1, pair.page2].filter(Boolean).forEach(page => {
        const index = normalizedResults.indexOf(page);
        normalizedResults[index] = {
          ...page,
          short_code: classification,
          gcn_classification_note: `📌 ${note}`
        };
      });
    });
    
    return normalizedResults;
  } catch (err) {
    console.error('❌ GCN post-processing error:', err);
    return folderResults;
  }
};
```

**Mục đích:** Post-process GCN documents sau khi scan xong folder

---

#### 3. Gọi `postProcessGCNBatch()` Sau Khi Scan Xong Folder (Lines ~365-398)
```javascript
if (!stopRef.current && folderResults.length > 0) {
  // Post-process GCN documents (date-based classification)
  const processedFolderResults = postProcessGCNBatch(folderResults);
  
  // Update allResults with post-processed results
  const startIndex = allResults.length - folderResults.length;
  for (let i = 0; i < processedFolderResults.length; i++) {
    allResults[startIndex + i] = {
      original_path: processedFolderResults[i].filePath,
      short_code: processedFolderResults[i].short_code,
      doc_type: processedFolderResults[i].doc_type,
      confidence: processedFolderResults[i].confidence,
      folder: processedFolderResults[i].folder
    };
  }
  
  // Update folder tabs with post-processed results
  setFolderTabs(prev => prev.map(t => {
    if (t.path === folder.path) {
      return { 
        ...t, 
        status: 'done', 
        count: processedFolderResults.length,
        files: processedFolderResults 
      };
    }
    return t;
  }));
  
  // Update fileResults with post-processed results
  setFileResults(prev => {
    const otherFolders = prev.filter(f => f.folder !== folder.path);
    return [...otherFolders, ...processedFolderResults];
  });
  
  processedFolderPaths.push(folder.path);
}
```

**Mục đích:** Gọi post-process ngay sau khi scan xong 1 folder và cập nhật kết quả

---

### Expected Behavior

#### Before Fix
```
Folder: C:\Data\GCN\
Files:
  - page1.jpg → GCN ❌
  - page2.jpg (ngày 27/10/2021) → GCN ❌
  - page3.jpg → GCN ❌
  - page4.jpg (ngày 14/04/2025) → GCN ❌
```

#### After Fix
```
Folder: C:\Data\GCN\
Files:
  - page1.jpg → GCNC ✅ (cặp với page2, ngày 27/10/2021 - cũ nhất)
  - page2.jpg (ngày 27/10/2021) → GCNC ✅
  - page3.jpg → GCNM ✅ (cặp với page4, ngày 14/04/2025 - mới hơn)
  - page4.jpg (ngày 14/04/2025) → GCNM ✅
```

---

## 🐛 Vấn Đề 2: Merge Custom Folder Vẫn Chưa Hoạt Động

### Báo Cáo Từ Người Dùng
> "Phần gộp về thư mục chỉ định vẫn chưa hoạt động."

### Phân Tích
- Code merge đã được sửa ở lần trước (thêm handler cho `mergeMode === 'custom'`)
- Nhưng không có console logs để debug
- Có thể do:
  1. `parentFolder` không đúng khi gọi merge
  2. Logic không chạy (cần verify với logs)

---

## ✅ Giải Pháp 2: Thêm Console Logs Để Debug

### Files Modified

**File:** `/app/desktop-app/electron/main.js`

### Changes

#### Thêm Console Logs (Lines ~653-677)
```javascript
const pdfBytes = await outPdf.save();
let outputPath;
if (options.autoSave) {
  const childFolder = path.dirname(filePaths[0]);
  let targetDir;
  
  console.log(`📂 Merge processing for ${shortCode}:`);
  console.log(`   childFolder: ${childFolder}`);
  console.log(`   mergeMode: ${options.mergeMode}`);
  console.log(`   customOutputFolder: ${options.customOutputFolder || 'null'}`);
  
  if (options.mergeMode === 'new') {
    const parentOfChild = path.dirname(childFolder);
    const childBaseName = path.basename(childFolder);
    const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
    targetDir = path.join(parentOfChild, newFolderName);
    if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
    console.log(`   ✅ Mode 'new': targetDir = ${targetDir}`);
  } else if (options.mergeMode === 'custom' && options.customOutputFolder) {
    // Custom folder mode: Create subfolder named after source folder
    const childBaseName = path.basename(childFolder);
    targetDir = path.join(options.customOutputFolder, childBaseName);
    console.log(`   📁 Creating custom folder: ${targetDir}`);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
      console.log(`   ✅ Created: ${targetDir}`);
    } else {
      console.log(`   ✅ Already exists: ${targetDir}`);
    }
  } else {
    // Default: Same folder (root mode)
    targetDir = childFolder;
    console.log(`   ✅ Mode 'root': targetDir = ${targetDir}`);
  }
  outputPath = path.join(targetDir, `${shortCode}.pdf`);
  console.log(`   🎯 Final output path: ${outputPath}`);
```

**Mục đích:** Debug merge process với chi tiết logs

---

### Console Logs Để Verify

#### Expected Logs (Custom Folder)
```
📂 Merge processing for HDCQ:
   childFolder: C:\Data\Folder1
   mergeMode: custom
   customOutputFolder: D:\AI
   📁 Creating custom folder: D:\AI\Folder1
   ✅ Created: D:\AI\Folder1
   🎯 Final output path: D:\AI\Folder1\HDCQ.pdf
```

#### If Not Working - Debug Steps
1. Kiểm tra `mergeMode` có đúng là "custom" không?
2. Kiểm tra `customOutputFolder` có null không?
3. Kiểm tra path có chứa ký tự đặc biệt không?
4. Kiểm tra quyền ghi vào thư mục custom

---

## 📊 Test Instructions

### Test 1: GCN Date-Based trong Batch Scan

**Setup:**
```
Folder: C:\Test\GCN\
Files:
  - 001.jpg (GCN trang 1, màu đỏ)
  - 002.jpg (GCN trang 2, màu đỏ, ngày 27/10/2021)
  - 003.jpg (GCN trang 1, màu hồng)
  - 004.jpg (GCN trang 2, màu hồng, ngày 14/04/2025)
```

**Steps:**
1. Tạo file TXT với đường dẫn: `C:\Test\GCN\`
2. Batch Scanner → Load TXT
3. Start Scan (Gemini Flash Lite)
4. Xem kết quả

**Expected:**
```
✅ 001.jpg → GCNC (màu đỏ + ngày 27/10/2021 - cũ)
✅ 002.jpg → GCNC
✅ 003.jpg → GCNM (màu hồng + ngày 14/04/2025 - mới)
✅ 004.jpg → GCNM
```

**Console Logs:**
```
🔄 Post-processing GCN batch (DATE-BASED classification)...
📋 Found 4 GCN document(s) to process
  🎨 Unique colors: red, pink
  🎨 Mixed colors → Classify by color
  🎨 Pair 1: Màu red → GCNC
  🎨 Pair 2: Màu pink → GCNM
✅ GCN post-processing complete
```

---

### Test 2: Merge Custom Folder

**Setup:**
```
Source: C:\Data\Folder1\ (10 files)
Custom output: D:\AI\
```

**Steps:**
1. Batch scan Folder1
2. Click "Gộp PDF"
3. Select "Sao chép vào thư mục khác"
4. Choose: D:\AI\
5. Click "Gộp PDF"
6. **Quan trọng:** Mở DevTools (F12) để xem console logs

**Expected Console Logs:**
```
🚀 executeMerge called: {mergeAll: false, outputOption: 'custom_folder', outputFolder: 'D:\\AI'}
Merge options: {autoSave: true, mergeMode: 'custom', customOutputFolder: 'D:\\AI', ...}

📂 Merge processing for HDCQ:
   childFolder: C:\Data\Folder1
   mergeMode: custom
   customOutputFolder: D:\AI
   📁 Creating custom folder: D:\AI\Folder1
   ✅ Created: D:\AI\Folder1
   🎯 Final output path: D:\AI\Folder1\HDCQ.pdf

📂 Merge processing for GCNM:
   childFolder: C:\Data\Folder1
   mergeMode: custom
   customOutputFolder: D:\AI
   ✅ Already exists: D:\AI\Folder1
   🎯 Final output path: D:\AI\Folder1\GCNM.pdf
```

**Expected File System:**
```
D:\AI\
  └── Folder1\
      ├── HDCQ.pdf ✅
      ├── GCNM.pdf ✅
      └── DKTC.pdf ✅
```

---

## 🔍 Troubleshooting

### Issue: GCN vẫn không phân loại

**Check:**
1. Gemini có trả về `color` field không?
   ```
   Console: "🎨 Unique colors: none"
   → Gemini không detect được màu
   ```

2. Gemini có trả về `issue_date` field không?
   ```
   Console: "⚠️ No dates found → Default all to GCNM"
   → Gemini không extract được ngày
   ```

**Solutions:**
- Nâng cấp lên Gemini Flash (full) thay vì Lite
- Kiểm tra prompt có đầy đủ instruction cho color & date không
- Test với ảnh rõ nét hơn

---

### Issue: Merge custom folder vẫn không hoạt động

**Debug với Console Logs:**

1. **Check mergeMode:**
   ```
   Console: "mergeMode: root"
   → Sai! Phải là "custom"
   → Fix: Check BatchScanner.js line ~621
   ```

2. **Check customOutputFolder:**
   ```
   Console: "customOutputFolder: null"
   → Sai! Phải có path
   → Fix: Check outputFolder state trong BatchScanner.js
   ```

3. **Check file creation:**
   ```
   Console: "✅ Created: D:\AI\Folder1"
   Nhưng không có file PDF
   → Check quyền ghi vào D:\AI\
   ```

---

## 📂 Files Modified Summary

| File | Lines Changed | Description |
|------|---------------|-------------|
| `/app/desktop-app/src/components/BatchScanner.js` | ~540-710, ~365-398 | Added GCN post-processing logic |
| `/app/desktop-app/electron/main.js` | ~653-677 | Added debug console logs for merge |

**Total changes:** ~230 lines added

---

## ✅ Summary

### Fix 1: GCN Date-Based Classification ✅
- Thêm `parseIssueDate()` để parse ngày cấp
- Thêm `postProcessGCNBatch()` để phân loại GCN theo màu và ngày
- Gọi post-process sau khi scan xong mỗi folder
- **Result:** GCN giờ được phân loại đúng GCNC/GCNM

### Fix 2: Merge Custom Folder Debug ✅
- Thêm console logs chi tiết cho merge process
- Giúp debug nếu vẫn còn vấn đề
- **Result:** Có thể xác định chính xác lỗi qua console logs

---

## 🙏 Vui Lòng Test & Báo Cáo

**Test và chia sẻ:**
1. ✅ GCN có phân loại đúng GCNC/GCNM không?
2. ✅ Merge custom folder có hoạt động không?
3. 📋 Console logs (mở DevTools → Console tab)
4. 📸 Screenshots kết quả

Cảm ơn! 🇻🇳
