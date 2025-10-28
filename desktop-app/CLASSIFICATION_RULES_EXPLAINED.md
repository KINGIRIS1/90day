# 📋 QUY TẮC PHÂN LOẠI VÀ ĐẶT TÊN TÀI LIỆU - GIẢI THÍCH CHI TIẾT

## Tổng quan hệ thống

Desktop app sử dụng **hệ thống phân loại 3 tầng (TIER)** để đặt tên tài liệu từ OCR:

```
┌─────────────────────────────────────────┐
│  EasyOCR Extract Text                   │
│  → Title: "CỘNG HÒA ... HỢP ĐỒNG..."   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  TIER 1: Fuzzy Title Matching (80%+)   │
│  → So sánh với templates chuẩn          │
└─────────────────────────────────────────┘
              ↓ (nếu < 80%)
┌─────────────────────────────────────────┐
│  TIER 2: Hybrid Match (50-80%)         │
│  → Fuzzy + Keyword confirmation         │
└─────────────────────────────────────────┘
              ↓ (nếu < 50%)
┌─────────────────────────────────────────┐
│  TIER 3: Pure Keyword Matching         │
│  → Đếm keywords + tính điểm             │
└─────────────────────────────────────────┘
```

---

## TIER 1: Fuzzy Title Matching (Threshold 80%)

### Nguyên lý:
Sử dụng **Levenshtein distance** để tính độ tương đồng giữa title OCR và templates chuẩn.

### Quy trình:

#### Bước 1: Clean Title
```python
# Input từ OCR
title_ocr = "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Đôc lâp HỢP ĐỒNG ỦY QUYỀN"

# Clean: Loại bỏ header
cleaned = clean_title_text(title_ocr)
# Output: "HỢP ĐỒNG ỦY QUYỀN"
```

**Headers bị loại bỏ:**
- `CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM`
- `Độc lập - Tự do - Hạnh phúc`
- `Mẫu số XX/YY`
- `BÊN ỦY QUYỀN`
- `(sau đây...`

#### Bước 2: So sánh với Templates
```python
TITLE_TEMPLATES = {
    "HDUQ": [
        "HỢP ĐỒNG ỦY QUYỀN",
        "HỢP ĐỒNG UỶ QUYỀN",
        "HỢP ĐỎNG ỦY QUYỀN",  # Lỗi OCR phổ biến
    ],
    "HDCQ": [
        "HỢP ĐỒNG CHUYỂN NHƯỢNG",
        "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT",
    ],
    "GUQ": [
        "GIẤY ỦY QUYỀN",
    ],
    # ... more templates
}
```

#### Bước 3: Tính Similarity
```python
cleaned_title = "HỢP ĐỒNG ỦY QUYỀN"
template = "HỢP ĐỒNG ỦY QUYỀN"

# SequenceMatcher (Python difflib)
similarity = SequenceMatcher(None, 
                           normalize_text(cleaned_title),
                           normalize_text(template)).ratio()
# Result: 1.0 (100%)
```

#### Bước 4: Kiểm tra Threshold
```python
if similarity >= 0.8:  # 80% threshold
    return {
        "type": "HDUQ",
        "confidence": 1.0,
        "method": "fuzzy_title_match"
    }
```

### Ví dụ thực tế:

#### Ví dụ 1: Match hoàn hảo (100%)
```
Input OCR: "CỘNG HÒA ... HỢP ĐỒNG ỦY QUYỀN"
Cleaned:   "HỢP ĐỒNG ỦY QUYỀN"
Template:  "HỢP ĐỒNG ỦY QUYỀN"
Similarity: 100% ✅
Result:    HDUQ - Hợp đồng ủy quyền
Method:    fuzzy_title_match
```

#### Ví dụ 2: Có lỗi chính tả (vẫn match)
```
Input OCR: "HỢP ĐỎNG UỶ QUYỀN"  (ĐỎNG thay vì ĐỒNG)
Cleaned:   "HỢP ĐỎNG UỶ QUYỀN"
Template:  "HỢP ĐỎNG ỦY QUYỀN"   (có trong templates)
Similarity: 100% ✅
Result:    HDUQ
```

#### Ví dụ 3: Không đạt 80%
```
Input OCR: "Độc lập Tự do GIẤY ỦY QUYỀN"
Cleaned:   "Độc lập Tự do GIẤY ỦY QUYỀN"  (còn dư header)
Template:  "GIẤY ỦY QUYỀN"
Similarity: 50.9% ❌ < 80%
→ Chuyển sang TIER 2/3
```

---

## TIER 2: Hybrid Match (50-80% similarity)

### Nguyên lý:
Kết hợp **fuzzy matching + keyword confirmation**

### Quy trình:
```python
if 0.5 <= similarity < 0.8:
    # Check keywords trong body text
    if keywords_match:
        score += fuzzy_boost  # Bonus từ similarity
        # Có thể classify nếu đủ keywords
```

### Ví dụ:
```
Title similarity: 65%  (không đạt 80%)
Body keywords: ["ủy quyền", "đại diện", "thực hiện"]
→ Boost score từ similarity
→ Classify: GUQ (via hybrid match)
```

---

## TIER 3: Pure Keyword Matching

### Nguyên lý:
Đếm và tính điểm keywords trong **title** và **body text**

### Công thức tính điểm:

```python
total_score = Σ (keyword_weight × specificity × multiplier)

Trong đó:
- keyword_weight: Độ quan trọng của keyword (1.0 - 2.0)
- specificity: Độ đặc trưng (1.0 / số doc types dùng keyword này)
- multiplier: 
    • 3.0 nếu keyword xuất hiện trong TITLE
    • 1.0 nếu keyword xuất hiện trong BODY
```

### Ví dụ chi tiết:

#### Document type: HDCQ (Hợp đồng chuyển nhượng)
```python
DOCUMENT_RULES = {
    "HDCQ": {
        "keywords": [
            "hợp đồng chuyển nhượng",
            "chuyển nhượng quyền",
            "hợp đồng",
            "chuyển nhượng",
            "quyền sử dụng đất",
            # ... more keywords
        ],
        "weight": 1.6,
        "min_matches": 2
    }
}
```

#### Tính điểm:

**Input:**
- Title: "HỢP ĐỒNG CHUYỂN NHƯỢNG"
- Body: "Bên A chuyển nhượng quyền sử dụng đất cho Bên B"

**Matching:**
```
1. "hợp đồng" → Found in TITLE
   Score: 1.6 (weight) × 0.5 (specificity) × 3.0 (title) = 2.4

2. "chuyển nhượng" → Found in TITLE
   Score: 1.6 × 0.8 × 3.0 = 3.84

3. "quyền sử dụng đất" → Found in BODY
   Score: 1.6 × 1.0 × 1.0 = 1.6

Total score: 2.4 + 3.84 + 1.6 = 7.84
```

**Confidence:**
```python
confidence = min(total_score / (num_keywords × weight × 2), 1.0)
confidence = min(7.84 / (50 × 1.6 × 2), 1.0) = ~0.049

# Nếu có title matches, boost 20%
if title_matches > 0:
    confidence = min(confidence × 1.2, 1.0)
```

---

## Case-Aware Scoring

### Nguyên lý:
Văn bản hành chính VN có tiêu đề **VIẾT HOA** (uppercase ratio 70-100%)

### Boost confidence:
```python
title_uppercase_ratio = calculate_uppercase_ratio(title_text)

if title_uppercase_ratio >= 0.7:
    # Title có uppercase cao → đáng tin cậy hơn
    confidence = min(confidence × 1.05, 1.0)  # +5% boost
```

### Ví dụ:
```
Title 1: "HỢP ĐỒNG CHUYỂN NHƯỢNG"  (100% uppercase)
→ Boost: +5%

Title 2: "Hợp đồng chuyển nhượng"  (0% uppercase)
→ No boost, thậm chí giảm confidence
```

---

## Specificity Score

### Nguyên lý:
Keywords xuất hiện trong **ÍT document types** → ĐẶC TRƯNG hơn → ĐIỂM CAO hơn

### Công thức:
```python
specificity = 1.0 / (số doc types dùng keyword này)
```

### Ví dụ:

#### Keyword: "chuyển nhượng"
```
Xuất hiện trong:
- HDCQ (Hợp đồng chuyển nhượng)
- GSND (Giấy sang nhượng đất)
→ 2 types

Specificity: 1.0 / 2 = 0.5
```

#### Keyword: "đăng ký biến động"
```
Xuất hiện trong:
- DDKBD (Đơn đăng ký biến động)
→ 1 type

Specificity: 1.0 / 1 = 1.0  ← Rất đặc trưng!
```

---

## Required Keywords (Tier 2 filter)

### Nguyên lý:
Một số document types YÊU CẦU keywords bắt buộc trong **TITLE**

### Config:
```python
DOCUMENT_TYPE_CONFIG = {
    "GCNM": {
        "required_in_title": [
            "giấy chứng nhận", 
            "GIẤY CHỨNG NHẬN"
        ],
        "weight": 1.5
    },
    "HDCQ": {
        "required_in_title": [
            "hợp đồng", 
            "HỢP ĐỒNG"
        ],
        "weight": 1.6
    }
}
```

### Ví dụ:
```
Title: "BIÊN BẢN BÀN GIAO"
Body: Có nhiều keywords của GCNM (giấy chứng nhận, quyền sử dụng đất...)

Check: "giấy chứng nhận" có trong title?
→ NO ❌

Result: KHÔNG classify thành GCNM, dù có nhiều keywords
→ Tránh false positive
```

---

## Tóm tắt quy trình đầy đủ

### Bước 1: OCR Extract
```
EasyOCR → Extract top 35% of image
→ Title text: "CỘNG HÒA ... HỢP ĐỒNG..."
→ Body text: "... ủy quyền đại diện ..."
```

### Bước 2: Clean Title
```
clean_title_text(title)
→ Remove: "CỘNG HÒA...", "Độc lập...", "Mẫu số..."
→ Result: "HỢP ĐỒNG ỦY QUYỀN"
```

### Bước 3: TIER 1 - Fuzzy Match
```
Compare cleaned title with templates
→ Best match: HDUQ (100%)
→ If >= 80%: RETURN HDUQ ✅
```

### Bước 4: TIER 2 - Hybrid (nếu 50-80%)
```
Similarity: 65%
→ Check keywords in body
→ If keywords match: Classify với fuzzy boost
```

### Bước 5: TIER 3 - Keyword Match (nếu < 50%)
```
Count keywords in title + body
Calculate: score = Σ(weight × specificity × multiplier)
Check: required keywords present?
→ Best score: HDCQ
→ Confidence: 0.45
```

### Bước 6: Return Result
```json
{
  "doc_type": "Hợp đồng ủy quyền",
  "short_code": "HDUQ",
  "confidence": 1.0,
  "method": "fuzzy_title_match",
  "reasoning": "✅ HIGH CONFIDENCE title match (100% similarity)"
}
```

---

## Độ ưu tiên các phương pháp

```
1. TIER 1 (Fuzzy ≥80%)     → Confidence cao nhất (95%+)
   └─ Ưu tiên: Clean title matching

2. TIER 2 (Hybrid 50-80%)  → Confidence trung bình (60-90%)
   └─ Ưu tiên: Fuzzy + Keyword confirmation

3. TIER 3 (Keyword <50%)   → Confidence thấp nhất (30-70%)
   └─ Ưu tiên: Title keywords > Body keywords
```

---

## Các tham số quan trọng

### Thresholds:
- **Fuzzy match**: 80% (cố định cho tất cả)
- **Minimum confidence**: 30% (dưới này = UNKNOWN)
- **Title boost**: ×3.0 (keywords in title)
- **Body multiplier**: ×1.0 (keywords in body)

### Weights:
- Document types: 1.0 - 2.0
- Specificity: 0.3 - 2.0 (dựa vào usage count)
- Case-aware boost: +5% (nếu uppercase ≥70%)

### Crop settings:
- **Top crop**: 35% (bắt được full title)
- **Max width**: 1920px (resize nếu lớn hơn)

---

## Ví dụ End-to-End

### Input Image: `20240504-01700001.jpg`

**Step 1: OCR**
```
EasyOCR (top 35%):
"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Mẫu số O9/ĐK
Đôc Lâp Tu Do Hanh Phúc
ĐƠN ĐĂNG KÝ BIẾN ĐỘNG
ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT"
```

**Step 2: Clean**
```
Cleaned title: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI TÀI SẢN GẮN LIỀN VỚI ĐẤT"
```

**Step 3: Fuzzy Match**
```
Template: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI TÀI SẢN GẮN LIỀN VỚI ĐẤT"
Similarity: 95% ✅ >= 80%
```

**Step 4: Result**
```json
{
  "doc_type": "Đơn đăng ký biến động đất đai, tài sản gắn liền với đất",
  "short_code": "DDKBD",
  "confidence": 0.9975,  // 95% × 1.05 (uppercase boost)
  "method": "fuzzy_title_match",
  "reasoning": "✅ HIGH CONFIDENCE title match (95% similarity, 87% uppercase)"
}
```

---

## Kết luận

Hệ thống sử dụng **3-tier cascade** để đảm bảo:

✅ **Accuracy**: Fuzzy matching 80% cho titles chuẩn
✅ **Robustness**: Fallback to keywords nếu OCR có lỗi
✅ **Speed**: Crop 35% + resize + optimized parameters
✅ **Vietnamese-specific**: Clean headers, case-aware, specificity scoring

**Độ chính xác kỳ vọng:**
- TIER 1 (Fuzzy): 95%+ accuracy
- TIER 2 (Hybrid): 85-90% accuracy
- TIER 3 (Keywords): 75-85% accuracy
