# GCN Issue Date Extraction Debug

## 🐛 Vấn Đề Hiện Tại

**Triệu chứng**:
```
📊 Tokens: input=12722, output=0
✅ TIER 2 COMPLETE:
   ├─ Classification: UNKNOWN
   ├─ Confidence: 30.00%
   └─ Reasoning: Could not parse Gemini response...
```

**Phân tích**:
- Tier 1 (60% top): Detect GCN đúng (98%)
- Tier 2 (100% full): **output=0 tokens** → parse fail → UNKNOWN
- Không lấy được `issue_date` → không phân loại GCNC/GCNM

---

## 🔍 Root Cause Analysis

### Nguyên nhân có thể:

1. **Safety Filters** (Khả năng cao nhất)
   - Gemini có thể block response vì có ảnh thẻ (personal photo) trong GCN
   - Hoặc thông tin cá nhân (tên, địa chỉ, CMND)
   - Finish reason: `SAFETY` thay vì `STOP`

2. **Content Policy**
   - Government documents có thể trigger content filters
   - Quốc huy có thể bị detect như sensitive content

3. **Max Tokens**
   - Response quá dài (unlikely vì output=0)

4. **Image Size/Quality**
   - Image quá lớn sau resize
   - Format không support

---

## ✅ Fixes Đã Thực Hiện

### Fix 1: Enhanced Debug Logging

**File**: `/app/desktop-app/python/ocr_engine_gemini_flash.py`

**Thêm debug info**:
```python
# Check finish reason
finish_reason = candidate.get('finishReason', 'UNKNOWN')
if finish_reason != 'STOP':
    print(f"⚠️ Gemini finish reason: {finish_reason}")
    
    # Check safety ratings
    if 'safetyRatings' in candidate:
        print(f"🛡️ Safety ratings: {candidate['safetyRatings']}")
```

**Output mới sẽ có**:
```
⚠️ Gemini finish reason: SAFETY
🛡️ Safety ratings: [{'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability': 'HIGH'}]
```

---

### Fix 2: Tier 2 Fallback Protection (Đã có)

**Nếu Tier 2 fail** → Giữ kết quả Tier 1 (GCN)

**Console log**:
```
⚠️ TIER 2 WORSE THAN TIER 1 - KEEPING TIER 1 RESULT:
   ├─ Tier 1: GCN (98.00%) ✅ FINAL
   └─ Tier 2: UNKNOWN (30.00%) ❌ DISCARDED
```

**Kết quả**: Classify đúng GCN, nhưng **KHÔNG có issue_date**

---

## 🚀 Solutions

### Solution 1: Adjust Safety Settings (RECOMMENDED)

**API Request có thể thêm safety settings**:

```python
"safetySettings": [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]
```

**Nơi thêm**: `/app/desktop-app/python/ocr_engine_gemini_flash.py` line ~125

**Trong payload**:
```python
payload = {
    "contents": [...],
    "generationConfig": {...},
    "safetySettings": [...]  # <- THÊM VÀO ĐÂY
}
```

---

### Solution 2: Use Flash Lite for Date Extraction

**Ý tưởng**: 
- Tier 1 (60% top): Detect GCN
- Tier 2 (40% bottom): Extract issue_date với Flash Lite
- Nhanh hơn, rẻ hơn, ít risk safety filter hơn

**Implementation**:
```python
# After Tier 1 detects GCN
if tier1_code == 'GCN':
    # Scan bottom 40% to extract issue_date
    date_result = classify_document_gemini_flash(
        image_path=image_path,
        api_key=api_key,
        crop_top_percent=0.60,  # Skip top 60%, scan bottom 40%
        crop_from_bottom=True,  # NEW parameter
        model_type='gemini-flash-lite',
        extract_date_only=True  # NEW parameter
    )
    
    issue_date = date_result.get('issue_date')
    tier1_result['issue_date'] = issue_date
    
    return tier1_result  # No need Tier 2
```

**Ưu điểm**:
- ✅ Tránh safety filter (không scan ảnh thẻ ở top)
- ✅ Nhanh hơn (Flash Lite thay vì Flash Full)
- ✅ Rẻ hơn (~$0.16 thay vì $0.24)
- ✅ Focused extraction (chỉ lấy date)

---

### Solution 3: Skip Tier 2 for GCN Page 1, Use Sequential for Page 2

**Logic**:
```
GCN Page 1:
- Tier 1 (60% top): Detect GCN (98%)
- Skip Tier 2 (vì safety filter)
- Extract issue_date từ Tier 1 response (nếu có)
- Hoặc scan bottom 40% riêng

GCN Page 2:
- Sequential naming từ Page 1
- Không cần API call
- Copy issue_date từ Page 1
```

**Implementation trong BatchScanner.js**:
```javascript
let lastGCN = null;

for (let i = 0; i < files.length; i++) {
  const file = files[i];
  
  // Check if this is GCN page 2 (continuation)
  if (lastGCN && i === lastGCN.index + 1) {
    // This is page 2 of GCN
    result = {
      short_code: 'GCN',
      issue_date: lastGCN.issue_date,  // Copy from page 1
      color: lastGCN.color,
      method: 'sequential_gcn_continuation'
    };
    
    lastGCN = null;  // Reset
    continue;
  }
  
  // Normal scan
  const result = await scanFile(file);
  
  if (result.short_code === 'GCN') {
    lastGCN = {
      index: i,
      issue_date: result.issue_date,
      color: result.color
    };
  }
}
```

---

## 🧪 Testing Steps

### Step 1: Check Finish Reason

**Scan lại GCN** và xem console log:

**Nếu thấy**:
```
⚠️ Gemini finish reason: SAFETY
```
→ **Confirmed**: Safety filter đang block

**Nếu thấy**:
```
⚠️ Gemini finish reason: STOP
```
→ Response thành công nhưng parse fail (khác issue)

---

### Step 2: Test với Safety Settings

**Thêm safety settings vào code** (Solution 1)

**Expected**:
```
✅ TIER 2 COMPLETE:
   ├─ Classification: GCN
   ├─ Confidence: 95.00%
   └─ Reasoning: Có quốc huy + ngày cấp: 27/10/2021

📅 Issue date extracted: 27/10/2021 (full)
```

---

### Step 3: Test Bottom Crop

**Scan chỉ 40% bottom của GCN page**

**Expected**:
- Không có ảnh thẻ (ở top)
- Không có quốc huy (ở top)
- Chỉ có ngày cấp + chữ ký + con dấu
- → Không trigger safety filter

---

## 📊 Comparison

| Approach | API Calls | Cost | Safety Risk | Date Accuracy |
|----------|-----------|------|-------------|---------------|
| **Current (Tier 2 Full)** | 2 | $0.24 | HIGH (blocked) | 0% (fail) |
| **Solution 1 (Safety Settings)** | 2 | $0.24 | LOW | 90%+ |
| **Solution 2 (Bottom Crop)** | 2 | $0.16 | VERY LOW | 85-90% |
| **Solution 3 (Sequential)** | 1 | $0.08 | VERY LOW | 85-90% |

---

## 🎯 Recommended Approach

### Immediate (Quick Fix):
**Solution 1**: Add safety settings to allow government documents

**Code changes**: 1 file, ~10 lines

**Expected result**: 
- ✅ Tier 2 hoạt động
- ✅ Extract issue_date
- ✅ Phân loại GCNC/GCNM đúng

---

### Long-term (Optimal):
**Solution 2 + 3**: 
- Scan bottom 40% để extract date (tránh safety filter)
- Sequential naming cho page 2 (skip API call)

**Expected result**:
- ✅ Cost: ~$0.12/GCN (giảm 50%)
- ✅ Speed: 4-5s thay vì 9-10s
- ✅ No safety filter risk
- ✅ Accurate date extraction

---

## 📝 Next Steps

1. **Test lại với debug logs** → Xác nhận finish reason
2. **If SAFETY** → Implement Solution 1 (safety settings)
3. **If still fail** → Implement Solution 2 (bottom crop)
4. **Optimize** → Implement Solution 3 (sequential for page 2)

---

**Status**: 🔍 Debugging Phase  
**Priority**: HIGH (ảnh hưởng GCN classification accuracy)  
**ETA**: Solution 1 - 30 mins | Solution 2+3 - 2-3 hours
