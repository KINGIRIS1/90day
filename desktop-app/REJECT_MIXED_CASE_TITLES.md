# 🚫 Quy tắc REJECT Mixed Case Titles

## Vấn đề phát hiện

### Tình huống:
```
Trang 1: HỢP ĐỒNG CHUYỂN NHƯỢNG (uppercase 100%)
→ Classify: HDCQ ✅

Trang 2: Giấy chứng nhận quyền sử dụng đất (uppercase 3.7%)
         ↑ Đây là MENTION trong body hợp đồng, KHÔNG phải title!
→ TRƯỚC: Classify GCNM (96.7% match!) ❌
→ SAU:   Ignore title, confidence 5% → Sequential logic ✅
```

### Nguyên nhân:
- OCR bắt được text "Giấy chứng nhận..." từ top 35%
- Text này match 96.7% với GCNM template
- NHƯNG đây chỉ là **mention trong body**, không phải **title thực**

### Cách nhận biết:
Vietnamese admin document titles **BẮT BUỘC viết HOA** (uppercase 70-100%)

```
✅ Title thực:  "GIẤY CHỨNG NHẬN..."      (100% uppercase)
❌ Body mention: "Giấy chứng nhận..."      (3.7% uppercase)
❌ Body mention: "giấy chứng nhận..."      (0% uppercase)
```

---

## Giải pháp implement

### PRE-CHECK: Ignore low uppercase titles

**File:** `rule_classifier.py` - `classify_by_rules()`

```python
# PRE-CHECK trước TIER 1
if title_text:
    title_uppercase_ratio = calculate_uppercase_ratio(title_text)
    
    if title_uppercase_ratio < 0.7:
        # Đây KHÔNG phải title thực → Ignore hoàn toàn
        print(f"⚠️ Title has low uppercase ({title_uppercase_ratio:.0%}), "
              f"likely not a real title. Using body text only.", 
              file=sys.stderr)
        
        title_text = None  # Set to None
        title_normalized = ""
```

### Kết quả:
```python
# TRƯỚC (có title với uppercase thấp):
title = "Giấy chứng nhận..."
→ Fuzzy match: GCNM (96.7%)
→ Classify: GCNM ❌

# SAU (ignore title):
title = None  # Ignored vì uppercase < 70%
→ Chỉ dùng body text
→ Keywords match thấp: DKTC (5%)
→ Sequential logic kích hoạt → HDCQ ✅
```

---

## Test Results

### Test 1: Title thực (UPPERCASE)
```
Title: "HỢP ĐỒNG CHUYỂN NHƯỢNG"
Uppercase: 100%
Result: HDCQ (100%)
Method: fuzzy_title_match
Status: ✅ PASS
```

### Test 2: Mention trong body (Mixed case)
```
Title: "Giấy chứng nhận quyền sử dụng đất"
Uppercase: 3.7% ← Bị REJECT!
Title được ignore → Chỉ dùng body text
Result: DKTC (5%)
Method: keyword_match
Sequential will trigger: ✅ YES (5% < 30%)
Status: ✅ PASS
```

### Test 3: Title thực mới (UPPERCASE)
```
Title: "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT"
Uppercase: 100%
Result: GCNM (100%)
Method: fuzzy_title_match
Status: ✅ PASS
```

---

## Luồng xử lý đầy đủ

```
┌─────────────────────────────────────┐
│ EasyOCR Extract (top 35%)           │
│ Title: "Giấy chứng nhận..."         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ PRE-CHECK: Calculate uppercase      │ ← MỚI
│ Uppercase: 3.7% < 70%               │
│ → Ignore title, set to None         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Classification (TIER 3 only)        │
│ Title: None (ignored)               │
│ Body: "giấy chứng nhận số 123..."   │
│ → Keyword match: DKTC (5%)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Sequential Logic Check (Frontend)   │
│ if confidence < 30% && lastType:    │
│   use lastType (HDCQ)               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Final Result                        │
│ - Original: DKTC (5%)               │
│ - Applied: HDCQ (90%)               │
│ - Note: "Trang tiếp theo của HDCQ" │
└─────────────────────────────────────┘
```

---

## Uppercase Ratio Thresholds

```python
Vietnamese Admin Document Standards:

TITLE (Tiêu đề):       70-100% uppercase
├─ "HỢP ĐỒNG..."       100%  ✅
├─ "GIẤY..."           100%  ✅
└─ "ĐƠN..."            100%  ✅

BODY (Nội dung):       0-40% uppercase
├─ "Giấy chứng nhận..."  3.7%  ❌ (mention)
├─ "giấy chứng nhận..."  0%    ❌ (mention)
└─ "Theo GCN số 123"     20%   ❌ (mixed)

THRESHOLD: 70%
- >= 70%: Accept as real title
- < 70%:  Reject, likely body mention
```

---

## Benefits

### 1. Tránh False Positive
```
TRƯỚC:
Trang 2 của HDCQ → Nhầm thành GCNM (vì match cao)

SAU:
Trang 2 của HDCQ → Dùng sequential logic → Đúng HDCQ ✅
```

### 2. Multi-page Documents
```
Page 1: HỢP ĐỒNG... (HDCQ) ✅
Page 2: "giấy chứng nhận..." → HDCQ (sequential) ✅
Page 3: "điều khoản..." → HDCQ (sequential) ✅
Page 4: "chữ ký..." → HDCQ (sequential) ✅
Page 5: GIẤY CHỨNG NHẬN... (GCNM - new doc) ✅
```

### 3. Consistent với Vietnamese Standards
```
✅ Admin titles ALWAYS uppercase
✅ Body text mixed/lowercase
✅ Easy to distinguish
```

---

## Edge Cases

### Case 1: Title có accent marks sai
```
Title: "GIAY CHUNG NHAN..."  (no accents)
Uppercase: 100% ✅
→ Still accepted (fuzzy match handles typos)
```

### Case 2: Title với số
```
Title: "MẪU SỐ 09/ĐK"
Uppercase: ~80% ✅
→ Accepted
```

### Case 3: Proper nouns trong body
```
Body: "Ông Nguyễn Văn A..."
Title from OCR: "Nguyễn Văn A"
Uppercase: 30% ❌
→ Rejected (not a title)
```

---

## Configuration

### Current Settings:
```python
UPPERCASE_THRESHOLD = 0.7  # 70%
FUZZY_THRESHOLD = 0.8      # 80%
SEQUENTIAL_CONFIDENCE = 0.3  # 30%
```

### Recommended (tuned):
```python
# Keep as is - working well
UPPERCASE_THRESHOLD = 0.7
```

---

## Kết luận

✅ **Implemented:** Pre-check reject titles với uppercase < 70%
✅ **Result:** Trang continuation không bị nhầm với document mới
✅ **Compatible:** Hoạt động với sequential logic hiện có
✅ **Standard:** Tuân thủ chuẩn văn bản hành chính VN

**Confidence cải thiện:**
- TRƯỚC: 96.7% (SAI - classify nhầm GCNM)
- SAU: 5% → Sequential → 90% (ĐÚNG - HDCQ từ trang trước)
