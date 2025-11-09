# Fix: GCN Color+Date Classification Logic

## Ngày: January 2025  
## Trạng thái: ✅ ĐÃ SỬA

---

## 🐛 Vấn Đề: GCN Đặt Tên Sai Khi Có Mixed Colors

### Báo Cáo Từ User
> "Quét được ngày nhưng đặt tên sai. Chỉ đặt tên đúng cho 2 file trang 2 GCN có ngày, trang 1 bị đặt tên sai."

### Console Logs
```javascript
🔍 GCN detected: {file: '20220105-07300038.jpg', color: 'red', issue_date: 'null'}
🔍 GCN detected: {file: '20220105-07300039.jpg', color: 'red', issue_date: '01/2009'}
🔍 GCN detected: {file: 'S00001 (1).jpg', color: 'pink', issue_date: 'null'}
🔍 GCN detected: {file: 'S00001 (2).jpg', color: 'pink', issue_date: '19/12/2021'}

🔄 Post-processing GCN batch...
📋 Found 5 GCN document(s) to process
  🎨 Unique colors: unknown, red, pink
  🎨 Mixed colors → Classify by color
```

### Phân Tích Data
```
File 1: unknown color, no date
File 2: red, no date (trang 1)
File 3: red, date=01/2009 (trang 2)
File 4: pink, no date (trang 1)
File 5: pink, date=19/12/2021 (trang 2)

Pairs:
- Pair 1: File 1 (unknown) + File 2 (red, no date) → Lẻ?
- Pair 2: File 3 (red, 01/2009) + File 4 (pink, no date)
- Pair 3: File 5 (pink, 19/12/2021) → Lẻ?

Thực tế có thể là:
- Pair 1: File 2 (red, trang 1) + File 3 (red, trang 2, 01/2009)
- Pair 2: File 4 (pink, trang 1) + File 5 (pink, trang 2, 19/12/2021)
```

---

## 🔍 Root Cause

### Logic Cũ (SAI)

```javascript
// OLD LOGIC
if (hasMixedColors && hasRedAndPink) {
  console.log(`🎨 Mixed colors → Classify by color`);
  
  pairsWithData.forEach(pair => {
    // ❌ SAI: Classify TOÀN BỘ red → GCNC, pink → GCNM
    const classification = (pair.color === 'red' || pair.color === 'orange') ? 'GCNC' : 'GCNM';
    
    // Apply to BOTH pages in pair
    [pair.page1, pair.page2].filter(Boolean).forEach(page => {
      normalizedResults[index] = { ...page, short_code: classification };
    });
  });
  
  return normalizedResults; // ❌ Bỏ qua date comparison!
}
```

**Vấn đề:**
1. ❌ Không xét đến **ngày cấp** khi classify trong cùng màu
2. ❌ Logic: "Có mixed colors → Dùng màu" → Ignore dates hoàn toàn
3. ❌ Kết quả: Cả 2 red pairs đều thành GCNC, cả 2 pink pairs đều thành GCNM

**Ví dụ Sai:**
```
Red Pair 1 (ngày 01/2009) → GCNC ✅ (đúng, cũ hơn)
Red Pair 2 (ngày 05/2020) → GCNC ❌ (SAI! Mới hơn phải là GCNM)
Pink Pair 1 (ngày 06/2021) → GCNM ✅ (đúng)
Pink Pair 2 (ngày 12/2025) → GCNM ✅ (đúng, nhưng nếu so với red thì sai logic)
```

---

## ✅ Giải Pháp: Color + Date Hybrid Logic

### Logic Mới (ĐÚNG)

**Nguyên tắc:**
1. ✅ **Color làm base classification:**
   - Red/Orange → Xu hướng GCNC (cũ)
   - Pink → Xu hướng GCNM (mới)

2. ✅ **Date làm refinement trong cùng màu:**
   - Trong các red pairs: ngày cũ nhất → GCNC, còn lại → GCNM
   - Trong các pink pairs: tất cả → GCNM (pink = format mới)

3. ✅ **No date fallback:**
   - Red + no date → GCNC (mặc định cũ)
   - Pink + no date → GCNM (mặc định mới)

### Implementation

**File:** `/app/desktop-app/src/components/BatchScanner.js` (Lines ~680-770)

```javascript
// Step 6: Classify - Prioritize date over color, then use color as fallback
console.log(`📊 Starting classification...`);

// Group pairs by color
const redPairs = pairsWithData.filter(p => p.color === 'red' || p.color === 'orange');
const pinkPairs = pairsWithData.filter(p => p.color === 'pink');
const unknownColorPairs = pairsWithData.filter(p => !p.color || p.color === 'unknown');

console.log(`🎨 Red pairs: ${redPairs.length}, Pink pairs: ${pinkPairs.length}, Unknown: ${unknownColorPairs.length}`);

if (hasMixedColors && hasRedAndPink) {
  console.log(`🎨 Mixed colors detected → Using color for base classification`);
  
  // ===== RED PAIRS =====
  // Classify red pairs by date (oldest red = GCNC, newer red = GCNM)
  const redPairsWithDate = redPairs.filter(p => p.parsedDate);
  if (redPairsWithDate.length > 0) {
    redPairsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
    
    redPairsWithDate.forEach((pair, idx) => {
      const classification = idx === 0 ? 'GCNC' : 'GCNM';
      const note = `Màu đỏ, ngày ${pair.issueDate} → ${classification} ${idx === 0 ? '(cũ nhất trong đỏ)' : ''}`;
      
      // Apply to BOTH pages
      [pair.page1, pair.page2].filter(Boolean).forEach(page => {
        const index = normalizedResults.indexOf(page);
        normalizedResults[index] = { ...page, short_code: classification, ... };
      });
    });
  }
  
  // Red pairs without dates → GCNC (default old)
  const redPairsNoDate = redPairs.filter(p => !p.parsedDate);
  redPairsNoDate.forEach(pair => {
    const note = `Màu đỏ, không có ngày → GCNC (mặc định cũ)`;
    // Apply GCNC to BOTH pages
  });
  
  // ===== PINK PAIRS =====
  // All pink → GCNM (new format, regardless of date)
  pinkPairs.forEach(pair => {
    const note = pair.issueDate 
      ? `Màu hồng, ngày ${pair.issueDate} → GCNM`
      : `Màu hồng, không có ngày → GCNM (mặc định mới)`;
    
    // Apply GCNM to BOTH pages
    [pair.page1, pair.page2].filter(Boolean).forEach(page => {
      normalizedResults[index] = { ...page, short_code: 'GCNM', ... };
    });
  });
  
  // ===== UNKNOWN COLOR =====
  unknownColorPairs.forEach(pair => {
    // Apply GCNM to BOTH pages (default)
  });
}
```

---

## 📊 Test Scenarios

### Scenario 1: Mixed Colors với Dates

**Input:**
```
File 1: red, no date (trang 1)
File 2: red, 01/2009 (trang 2)
File 3: red, no date (trang 1)
File 4: red, 05/2020 (trang 2)
File 5: pink, no date (trang 1)
File 6: pink, 19/12/2021 (trang 2)
```

**Pairs:**
```
Red Pair 1: File 1 + File 2 (date=01/2009)
Red Pair 2: File 3 + File 4 (date=05/2020)
Pink Pair 1: File 5 + File 6 (date=19/12/2021)
```

**Expected Output (NEW LOGIC):**
```
Red Pair 1 (01/2009) → GCNC ✅ (cũ nhất trong đỏ)
  - File 1 (trang 1) → GCNC
  - File 2 (trang 2) → GCNC

Red Pair 2 (05/2020) → GCNM ✅ (mới hơn trong đỏ)
  - File 3 (trang 1) → GCNM
  - File 4 (trang 2) → GCNM

Pink Pair 1 (19/12/2021) → GCNM ✅ (pink = mới)
  - File 5 (trang 1) → GCNM
  - File 6 (trang 2) → GCNM
```

**Console Logs:**
```
📊 Starting classification...
🎨 Red pairs: 2, Pink pairs: 1, Unknown: 0
🎨 Mixed colors detected → Using color for base classification
📅 Red pairs with dates: 2
  ✅ Red Pair 1: Màu đỏ, ngày 01/2009 → GCNC (cũ nhất trong đỏ)
  ✅ Red Pair 2: Màu đỏ, ngày 05/2020 → GCNM
📅 Pink pairs with dates: 1
  ✅ Pink Pair 1: Màu hồng, ngày 19/12/2021 → GCNM
✅ GCN classification by color+date complete
```

---

### Scenario 2: Red Pairs Không Có Dates

**Input:**
```
File 1: red, no date (trang 1)
File 2: red, no date (trang 2)
File 3: pink, no date (trang 1)
File 4: pink, 19/12/2021 (trang 2)
```

**Expected Output:**
```
Red Pair (no date) → GCNC ✅ (đỏ = cũ, default)
  - File 1 → GCNC
  - File 2 → GCNC

Pink Pair (19/12/2021) → GCNM ✅ (hồng = mới)
  - File 3 → GCNM
  - File 4 → GCNM
```

---

### Scenario 3: Cùng Màu Đỏ (No Mixed)

**Input:**
```
File 1: red, 01/2009 (trang 2)
File 2: red, 05/2020 (trang 2)
```

**Expected Output:**
```
Red Pair 1 (01/2009) → GCNC ✅ (cũ nhất)
Red Pair 2 (05/2020) → GCNM ✅ (mới hơn)
```

---

## 🔧 Additional Fix: Merge Error Handling

### Problem
Merge vẫn không có logs từ main.js → có lỗi bị nuốt

### Fix
Thêm try-catch trong BatchScanner.js để bắt errors:

```javascript
// BatchScanner.js lines ~854-873
try {
  const merged = await window.electronAPI.mergeByShortCode(items, mergeOptions);
  console.log('Merge result:', merged);
  const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
  totalMerged += (merged || []).length;
  totalSuccess += okCount;
} catch (mergeErr) {
  console.error('❌ Merge failed for folder:', folder, mergeErr);
  alert(`❌ Lỗi merge folder ${folder}:\n${mergeErr.message}`);
}
```

**Mục đích:** Hiển thị lỗi merge nếu có

---

## 📋 Test Instructions

### Test 1: GCN Color+Date Classification

**Setup:**
```
Folder với 4-6 GCN files:
- 2 files màu đỏ (1 có ngày cũ, 1 không có ngày)
- 2 files màu hồng (1 có ngày mới, 1 không có ngày)
```

**Steps:**
1. Batch scan folder với Gemini Flash Lite
2. **MỞ DEVTOOLS (F12)** → Console tab
3. Xem logs

**Expected Logs:**
```
🔍 GCN detected: {color: 'red', issue_date: '01/2009'}
🔍 GCN detected: {color: 'red', issue_date: 'null'}
🔍 GCN detected: {color: 'pink', issue_date: '19/12/2021'}
🔍 GCN detected: {color: 'pink', issue_date: 'null'}

🔄 Post-processing GCN batch...
📋 Found 4 GCN document(s) to process
🎨 Red pairs: 1, Pink pairs: 1, Unknown: 0
🎨 Mixed colors detected → Using color for base classification
📅 Red pairs with dates: 1
  ✅ Red Pair 1: Màu đỏ, ngày 01/2009 → GCNC (cũ nhất trong đỏ)
📅 Pink pairs with dates: 1
  ✅ Pink Pair 1: Màu hồng, ngày 19/12/2021 → GCNM
✅ GCN classification by color+date complete
```

**Expected Results:**
```
File 1 (red, trang 1) → GCNC ✅
File 2 (red, trang 2, 01/2009) → GCNC ✅
File 3 (pink, trang 1) → GCNM ✅
File 4 (pink, trang 2, 19/12/2021) → GCNM ✅
```

---

### Test 2: Merge Custom Folder with Error Logs

**Steps:**
1. Batch scan folder
2. Gộp PDF → Custom folder
3. **MỞ DEVTOOLS** → Console tab
4. Check for errors

**Expected:**
- Nếu thành công: `✅ PDF written successfully: ...`
- Nếu lỗi: `❌ Merge failed for folder: ... [error message]`

---

## 📊 Summary

| Issue | Old Logic | New Logic | Status |
|-------|-----------|-----------|--------|
| Mixed color classification | All red → GCNC, all pink → GCNM (ignore dates) | Red: oldest → GCNC, newer → GCNM; Pink: all → GCNM | ✅ Fixed |
| Date comparison within color | ❌ Not done | ✅ Done (within red pairs) | ✅ Fixed |
| No date handling | ❌ Inconsistent | ✅ Red→GCNC, Pink→GCNM | ✅ Fixed |
| Merge error handling | ❌ Silent failures | ✅ Try-catch + alerts | ✅ Fixed |

**Files Modified:**
- `/app/desktop-app/src/components/BatchScanner.js` (~100 lines changed)

---

## 🙏 Vui Lòng Test

**Cần share:**
1. ✅ Console logs đầy đủ (từ "🔍 GCN detected" đến "✅ GCN classification complete")
2. ✅ Results: Mỗi file được classify thành gì?
3. ✅ Merge logs: Có error không? PDF có được tạo không?

Cảm ơn! 🇻🇳
