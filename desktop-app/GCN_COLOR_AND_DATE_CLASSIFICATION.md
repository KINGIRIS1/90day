# GCN Color and Date Based Classification

## Tổng quan

Update logic phân loại GCN với **2 priorities**:
1. **Priority 1: Màu sắc** (red/orange = GCNC, pink = GCNM)
2. **Priority 2: Ngày cấp** (fallback nếu không detect màu)

## 3 Loại GCN

### 1. GCNC (Cũ - Đỏ/Cam)
- **Màu**: Đỏ hoặc cam
- **Format**: A3, 2 trang
- **Ngày cấp**: Trang 2 (inner page)
- **Example**: SỐ AQ 227162

### 2. GCNM (Mới - Hồng A3)
- **Màu**: Hồng
- **Format**: A3, 2 trang
- **Ngày cấp**: Trang 2 (inner page)
- **Example**: DK 700320

### 3. GCNM (Mới nhất - Hồng A4)
- **Màu**: Hồng nhạt
- **Format**: A4, 2 trang (nhỏ hơn)
- **Ngày cấp**: **Trang 1** (bottom)
- **Example**: AA 01085158

## Logic Phân Loại

### Priority 1: Màu Sắc (Highest)

```javascript
if (color === 'red' || color === 'orange') {
  return 'GCNC'; // Cũ
} else if (color === 'pink') {
  return 'GCNM'; // Mới
}
```

### Priority 2: Ngày Cấp (Fallback)

Nếu không detect được màu:

```javascript
if (only_1_pair) {
  return 'GCNM'; // Default mới
} else {
  // Sort by date
  oldest_date → 'GCNC'
  newer_dates → 'GCNM'
}
```

## Scan Order

**Cả A3 và A4 đều scan 2 trang**:
- Trang 1 → Trang 2 (Pair 1)
- Trang 1 → Trang 2 (Pair 2)
- ...

**Mixed batch**: Có thể có cả A3 và A4 trong cùng 1 batch

## Gemini Extraction

### Fields Extracted:

1. **color** (string): "red", "orange", "pink", "unknown"
   - Detect màu nền của giấy
   - Red/orange = GCNC (cũ)
   - Pink = GCNM (mới)

2. **issue_date** (string): "DD/MM/YYYY", "MM/YYYY", "YYYY", null
   - A3: Thường ở trang 2
   - A4: Thường ở trang 1 (bottom)
   - Flexible format nếu mờ

3. **issue_date_confidence** (string): "full", "partial", "year_only", "not_found"

### Example Response:

```json
{
  "short_code": "GCN",
  "color": "red",
  "issue_date": "27/10/2021",
  "issue_date_confidence": "full",
  "confidence": 0.95,
  "reasoning": "Giấy chứng nhận màu đỏ/cam (cũ), ngày cấp 27/10/2021"
}
```

## Frontend Logic

### Step 1: Pairing

```javascript
pairs = [
  { page1: doc0, page2: doc1 },
  { page1: doc2, page2: doc3 },
  ...
]
```

### Step 2: Extract Data

```javascript
for each pair:
  color = page1.color || page2.color
  issue_date = page1.issue_date || page2.issue_date
```

### Step 3: Classify by Color

```javascript
if (color === 'red' || color === 'orange'):
  classification = 'GCNC'
elif (color === 'pink'):
  classification = 'GCNM'
```

### Step 4: Fallback to Date

```javascript
if (no color detected):
  if (only 1 pair):
    classification = 'GCNM' (default)
  else:
    sort pairs by date
    oldest → 'GCNC'
    others → 'GCNM'
```

### Step 5: Apply to Both Pages

```javascript
for each page in pair:
  page.short_code = classification
```

## Changes Summary

### Backend (Python)

**`ocr_engine_gemini_flash.py`**:
- Updated prompts to extract `color` field
- Added color detection instructions (red/orange vs pink)
- Updated examples with color field

**`process_document.py`**:
- Added `color` field to response
- Passes to frontend for classification

### Frontend (JavaScript)

**`DesktopScanner.js`**:
- Updated `postProcessGCNBatch()`:
  - Extract color from both pages
  - Priority 1: Classify by color
  - Priority 2: Classify by date (fallback)
  - Extract issue_date from both pages (A3 = page2, A4 = page1)

## Test Cases

### Case 1: Batch with Color Detection

**Input:**
```
Pair 1: color = "red", issue_date = "27/10/2021"
Pair 2: color = "pink", issue_date = "14/04/2025"
```

**Output:**
```
Pair 1 → GCNC (màu đỏ)
Pair 2 → GCNM (màu hồng)
```

### Case 2: Batch without Color (Date Fallback)

**Input:**
```
Pair 1: color = null, issue_date = "01/01/2012"
Pair 2: color = null, issue_date = "02/01/2013"
```

**Output:**
```
Pair 1 → GCNC (ngày sớm nhất)
Pair 2 → GCNM (ngày muộn hơn)
```

### Case 3: Mixed (Some with Color, Some without)

**Input:**
```
Pair 1: color = "red", issue_date = "27/10/2021"
Pair 2: color = null, issue_date = "01/01/2012"
Pair 3: color = "pink", issue_date = "14/04/2025"
```

**Output:**
```
Pair 1 → GCNC (màu đỏ)
Pair 2 → GCNC (không màu, ngày sớm nhất trong nhóm không màu)
Pair 3 → GCNM (màu hồng)
```

### Case 4: A4 Format (Issue Date on Page 1)

**Input:**
```
Pair 1 (A4):
  page1: issue_date = "14/04/2025", color = "pink"
  page2: issue_date = null
```

**Output:**
```
Pair 1 → GCNM (màu hồng, ngày cấp trang 1)
```

## Files Modified

1. `/app/desktop-app/python/ocr_engine_gemini_flash.py`
   - Updated prompts with color detection
   - Updated extraction code
   - Updated examples

2. `/app/desktop-app/python/process_document.py`
   - Added `color` field to response

3. `/app/desktop-app/src/components/DesktopScanner.js`
   - Updated `postProcessGCNBatch()` with priority-based logic
   - Extract color and issue_date from both pages
   - Classify by color first, then date

4. `/app/desktop-app/GCN_COLOR_AND_DATE_CLASSIFICATION.md`
   - This documentation

## Testing

### Backend Testing
```bash
cd /app/desktop-app
python3 test_gcn_date_classification.py
```

### Manual Testing
1. Scan batch with mixed GCN types (red, pink, A3, A4)
2. Check console logs for color detection
3. Verify classification results

### Expected Console Logs
```
🔄 Post-processing GCN batch (DATE-BASED classification)...
📋 Found 6 GCN document(s) to process
📄 Pair 1: file1.jpg (trang 1) + file2.jpg (trang 2)
  🎨 Pair 1: color = red
  📅 Pair 1: issue_date = 27/10/2021 (full)
📄 Pair 2: file3.jpg (trang 1) + file4.jpg (trang 2)
  🎨 Pair 2: color = pink
  📅 Pair 2: issue_date = 14/04/2025 (full)
📊 Classifying GCN pairs...
  🎨 2 pair(s) with color detected
  ⚪ 0 pair(s) without color → will use date
  🎨 Pair 1: Màu red → GCNC
  🎨 Pair 2: Màu pink → GCNM
✅ GCN post-processing complete (date-based)
```

## Rollback

Nếu cần quay lại logic cũ:
1. Revert changes in `ocr_engine_gemini_flash.py`
2. Revert changes in `process_document.py`
3. Revert changes in `DesktopScanner.js`

---

**Version**: 2.0
**Date**: 2025-01-XX
**Status**: ✅ Implemented (chưa test)
