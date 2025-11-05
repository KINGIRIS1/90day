# GCN Date-Based Classification

## Tổng quan

Thay đổi logic phân loại GCN (Giấy chứng nhận quyền sử dụng đất) từ **dựa trên số chứng nhận** sang **dựa trên ngày cấp**.

## Lý do thay đổi

User yêu cầu sử dụng **ngày cấp GCN** để phân loại GCNC (cũ) và GCNM (mới) thay vì dựa vào số chứng nhận.

## Logic mới

### 1. Scan theo thứ tự cặp (Pairing)

```
Trang 1 → Trang 2 (Cặp 1)
Trang 1 → Trang 2 (Cặp 2)
...
```

- **Trang 1** (index chẵn: 0, 2, 4...): Không có ngày cấp hoặc có thể có
- **Trang 2** (index lẻ: 1, 3, 5...): Có **ngày cấp** (issue_date)

### 2. Extract ngày cấp từ Gemini

Gemini 2.5 Flash/Flash Lite sẽ extract `issue_date` với các format:

- **Đầy đủ**: `DD/MM/YYYY` (ví dụ: "01/01/2012")
- **Một phần**: `MM/YYYY` (ví dụ: "02/2012") - nếu chữ ngày mờ
- **Chỉ năm**: `YYYY` (ví dụ: "2012") - nếu chỉ đọc được năm

Confidence levels:
- `"full"`: Đọc được đầy đủ DD/MM/YYYY
- `"partial"`: Chỉ đọc được MM/YYYY
- `"year_only"`: Chỉ đọc được YYYY
- `"not_found"`: Không tìm thấy (có thể trang 1)

### 3. So sánh ngày cấp giữa các cặp

**Logic comparison:**

```javascript
if (pairs.length === 1) {
  // Chỉ có 1 cặp → Mặc định GCNM
  classification = 'GCNM';
} else {
  // Nhiều cặp → So sánh ngày
  sortPairsByDate();
  
  for each pair:
    if (isOldest && hasDate) {
      classification = 'GCNC'; // Ngày sớm nhất = cũ
    } else {
      classification = 'GCNM'; // Ngày muộn hơn hoặc không có = mới
    }
}
```

**Format comparison:**

- **Full date** (DD/MM/YYYY): So sánh ngày/tháng/năm
- **Partial** (MM/YYYY): So sánh tháng/năm (assume ngày = 1)
- **Year only** (YYYY): So sánh năm (assume tháng = 1, ngày = 1)
- **No date**: Mặc định GCNM (mới)

**Comparable format:**

```javascript
comparable = year * 10000 + month * 100 + day

Ví dụ:
- 01/01/2012 → 20120101
- 02/2012 → 20120201
- 2012 → 20120101
- 15/03/2013 → 20130315
```

### 4. Apply classification cho cả 2 trang

Classification được apply cho **cả trang 1 và trang 2** của mỗi cặp.

## Thay đổi code

### 1. Gemini Prompt (`ocr_engine_gemini_flash.py`)

**Thay đổi:**
- ❌ Xóa: `certificate_number` extraction
- ✅ Thêm: `issue_date` và `issue_date_confidence` extraction

**Prompt mới:**

```
⚠️ BẮT BUỘC: Tìm NGÀY CẤP (thường ở trang 2, có thể viết tay)
  - Format: DD/MM/YYYY (ví dụ: "01/01/2012", "15/03/2013")
  - Nếu mờ chỉ đọc được: MM/YYYY (ví dụ: "02/2012") hoặc chỉ năm YYYY (ví dụ: "2012")
  - Tìm text gần "Ngày cấp", "Cấp ngày", hoặc ô có handwriting date

Response format:
{
  "short_code": "GCN",
  "issue_date": "01/01/2012",
  "issue_date_confidence": "full",
  "confidence": 0.95,
  "reasoning": "Giấy chứng nhận với quốc huy, màu hồng, ngày cấp 01/01/2012"
}
```

### 2. Process Document (`process_document.py`)

**Thay đổi:**

```python
# OLD (line 177-178):
certificate_number = result.get("certificate_number", None)
"certificate_number": certificate_number,

# NEW:
issue_date = result.get("issue_date", None)
issue_date_confidence = result.get("issue_date_confidence", None)
"issue_date": issue_date,
"issue_date_confidence": issue_date_confidence,
```

### 3. Frontend Logic (`DesktopScanner.js`)

**Thay đổi:**

- ❌ **Commented out**: Toàn bộ logic cũ (certificate_number based classification)
- ✅ **Thêm mới**: 
  - `postProcessGCNBatch()` - Pairing và date comparison logic
  - `parseIssueDate()` - Helper function để parse date

**New function:**

```javascript
const postProcessGCNBatch = (results) => {
  // 1. Normalize GCNM/GCNC → GCN
  // 2. Find all GCN documents
  // 3. Pair documents (index 0,1), (2,3), (4,5)...
  // 4. Extract issue_date from page 2
  // 5. Compare dates between pairs
  // 6. Classify: oldest = GCNC, others = GCNM
  // 7. Apply to both pages
};

const parseIssueDate = (issueDate, confidence) => {
  // Parse date to comparable format
  // full: year*10000 + month*100 + day
  // partial: year*10000 + month*100 + 1
  // year_only: year*10000 + 1*100 + 1
};
```

## Test Cases

### Case 1: Batch với 2 cặp GCN

**Input:**
```
Page 1 (trang 1 - GCN A): issue_date = null
Page 2 (trang 2 - GCN A): issue_date = "01/01/2012"
Page 3 (trang 1 - GCN B): issue_date = null
Page 4 (trang 2 - GCN B): issue_date = "02/01/2012"
```

**Output:**
```
Page 1, 2 → GCNC (ngày 01/01/2012 - sớm nhất)
Page 3, 4 → GCNM (ngày 02/01/2012 - muộn hơn)
```

### Case 2: Ngày mờ (chỉ có tháng/năm)

**Input:**
```
Page 2 (GCN A): issue_date = "02/2012" (partial)
Page 4 (GCN B): issue_date = "04/2013" (partial)
```

**Output:**
```
Page 1, 2 → GCNC (tháng 2/2012 - cũ hơn)
Page 3, 4 → GCNM (tháng 4/2013 - mới hơn)
```

### Case 3: Chỉ có năm

**Input:**
```
Page 2 (GCN A): issue_date = "2012" (year_only)
Page 4 (GCN B): issue_date = "2013" (year_only)
```

**Output:**
```
Page 1, 2 → GCNC (năm 2012 - cũ hơn)
Page 3, 4 → GCNM (năm 2013 - mới hơn)
```

### Case 4: Không có ngày cấp

**Input:**
```
Page 2 (GCN A): issue_date = null
Page 4 (GCN B): issue_date = null
```

**Output:**
```
Page 1, 2 → GCNM (mặc định)
Page 3, 4 → GCNM (mặc định)
```

### Case 5: Chỉ có 1 cặp

**Input:**
```
Page 1 (trang 1): issue_date = null
Page 2 (trang 2): issue_date = "01/01/2012"
```

**Output:**
```
Page 1, 2 → GCNM (mặc định khi chỉ có 1 cặp)
```

## Files Modified

1. **`/app/desktop-app/python/ocr_engine_gemini_flash.py`**
   - Updated `get_classification_prompt_lite()` (line 307-350)
   - Updated `get_classification_prompt()` (line 849-905)
   - Changed from `certificate_number` to `issue_date` extraction

2. **`/app/desktop-app/python/process_document.py`**
   - Updated Gemini Flash result mapping (line 177-190)
   - Changed from `certificate_number` to `issue_date` + `issue_date_confidence`

3. **`/app/desktop-app/src/components/DesktopScanner.js`**
   - **Commented out**: Old logic (line 297-520 approximately)
   - **Added**: New `postProcessGCNBatch()` function (line 262-516)
   - **Added**: Helper `parseIssueDate()` function (line 480-505)

## Lưu ý quan trọng

1. **Gemini handwriting OCR**: Gemini 2.5 có khả năng đọc chữ viết tay khá tốt, nhưng accuracy không phải 100%
2. **Flexible format**: Hỗ trợ 3 formats (DD/MM/YYYY, MM/YYYY, YYYY) để handle trường hợp chữ mờ
3. **Default GCNM**: Khi không có ngày cấp hoặc chỉ có 1 cặp → Mặc định GCNM (theo yêu cầu user)
4. **Pairing logic**: Giả định scan theo thứ tự: trang 1 → trang 2 → trang 1 → trang 2...
5. **Apply to both pages**: Classification được apply cho cả trang 1 và trang 2 của mỗi cặp

## Testing

### Manual Testing

1. Prepare test batch:
   - 2-4 GCN documents (4-8 trang)
   - Scan theo thứ tự: trang 1 → trang 2 → trang 1 → trang 2

2. Check console logs:
   ```
   📋 Found X GCN document(s) to process
   📄 Pair 1: file1.jpg (trang 1) + file2.jpg (trang 2)
   📅 Pair 1: issue_date = 01/01/2012 (full)
   📊 Comparing issue dates between pairs...
   ✅ Pair 1: 01/01/2012 → GCNC
   ✅ Pair 2: 02/01/2012 → GCNM
   ```

3. Verify classification:
   - Cặp với ngày sớm nhất → GCNC
   - Cặp với ngày muộn hơn → GCNM
   - Không có ngày → GCNM

### Automated Testing

Use `deep_testing_backend_v2` to test Python OCR engine with sample images.

## Rollback

Nếu cần quay lại logic cũ (certificate_number based):
1. Uncomment code trong `DesktopScanner.js` (line ~297-520)
2. Revert changes trong `ocr_engine_gemini_flash.py`
3. Revert changes trong `process_document.py`

---

**Ngày tạo**: 2025-01-XX
**Version**: 1.0
**Status**: ✅ Implemented (chưa test)
