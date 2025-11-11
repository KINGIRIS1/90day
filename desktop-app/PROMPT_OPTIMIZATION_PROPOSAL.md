# 🎯 ĐỀ XUẤT TỐI ƯU HÓA PROMPT - TIẾT KIỆM 40-50% TOKENS

## 📊 **PHÂN TÍCH HIỆN TẠI**

**Prompt hiện tại:**
- Tổng số từ: ~3,500 từ
- Ước tính tokens: ~7,500 tokens
- File: `/app/desktop-app/python/ocr_engine_gemini_flash.py` (dòng 887-1992)

**Chi phí với batch mode (5 trang):**
- Hiện tại: 7,500 tokens × $0.000000075 = $0.00056
- Sau tối ưu: ~4,000 tokens × $0.000000075 = $0.0003
- **Tiết kiệm: ~$0.00026 per batch** (~46%)

---

## 🔍 **PHÂN TÍCH CẤU TRÚC PROMPT**

### ✅ **PHẦN CẦN GIỮ (CRITICAL - 40%)**

#### 1. **Rules Cơ Bản** (~800 tokens)
```
✅ GIỮ LẠI:
- Quy tắc vị trí (TOP 30% = title, MIDDLE = body, BOTTOM = signature)
- Position-aware classification rules
- Phân biệt TITLE vs REFERENCE/MENTION
- Dấu hiệu nhận biết title (độc lập, IN HOA, không có "theo", "căn cứ")
```

**LÝ DO:** Đây là core logic, bỏ sẽ giảm accuracy nghiêm trọng.

#### 2. **GCN Special Rules** (~500 tokens)
```
✅ GIỮ LẠI:
- ❌ KHÔNG BAO GIỜ trả về GCNM/GCNC
- ✅ CHỈ trả về "GCN" generic
- Tìm issue_date (format DD/MM/YYYY)
- Issue_date confidence levels
```

**LÝ DO:** GCN là document type phức tạp nhất, chiếm ~40% volume.

#### 3. **Document List** (~1,500 tokens)
```
✅ GIỮ LẠI (RÚT GỌN):
- 98 loại tài liệu
- Nhưng GỘP CÁC VARIANTS thành 1 dòng
- Bỏ descriptions chi tiết
```

**LÝ DO:** AI cần biết đầy đủ danh sách để classify chính xác.

---

## ❌ **PHẦN CÓ THỂ RÚT GỌN (60%)**

### 🟡 **REDUNDANT EXAMPLES** (~1,500 tokens → 300 tokens)

**Hiện tại:** 10-15 ví dụ ĐÚNG/SAI cho mỗi rule
```
✅ ĐÚNG: Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở TOP...
❌ SAI: Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở MIDDLE...
❌ SAI: Mention trong body...
❌ SAI: Reference với "theo"...
✅ ĐÚNG: Title độc lập...
(còn 10+ ví dụ khác)
```

**ĐỀ XUẤT RÚT GỌN:**
```
✅ TOP title → Classify
❌ Middle/Bottom → UNKNOWN
❌ "theo X", "căn cứ X" → Reference, ignore
```

**TIẾT KIỆM: ~1,200 tokens (80% examples)**

---

### 🟡 **REPETITIVE WARNINGS** (~800 tokens → 200 tokens)

**Hiện tại:** Lặp lại rules nhiều lần
```
⚠️ CỰC KỲ QUAN TRỌNG: CHỈ PHÂN LOẠI DỰA VÀO TEXT Ở PHẦN ĐẦU TRANG!
(xuất hiện 3-4 lần trong prompt)

⚠️ KHÔNG BAO GIỜ trả về GCNM/GCNC
(xuất hiện 5-6 lần)

⚠️ BỎ QUA mentions trong body
(xuất hiện 4-5 lần)
```

**ĐỀ XUẤT:** Chỉ nói 1 lần ở đầu, không lặp lại.

**TIẾT KIỆM: ~600 tokens (75% repetition)**

---

### 🟡 **VERBOSE EXPLANATIONS** (~1,000 tokens → 300 tokens)

**Hiện tại:** Giải thích dài dòng
```
📍 QUY TẮC VỊ TRÍ:

1️⃣ **PHẦN ĐẦU TRANG (TOP 30%)**
   - Đây là vùng TIÊU ĐỀ CHÍNH
   - CHỈ text ở đây MỚI được dùng để phân loại
   - Cỡ chữ LỚN, IN HOA, căn giữa
   - VD: "HỢP ĐỒNG CHUYỂN NHƯỢNG", "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG"

2️⃣ **PHẦN GIỮA TRANG (MIDDLE 30-70%)**
   - Đây là BODY CONTENT
   - ❌ KHÔNG được phân loại dựa vào text ở đây
   - Có thể có mentions của document types khác
   - VD: "...theo hợp đồng chuyển nhượng đã ký..."
   - → CHỈ LÀ MENTION, KHÔNG PHẢI TIÊU ĐỀ!
```

**ĐỀ XUẤT RÚT GỌN:**
```
📍 RULES:
- TOP 30%: Main title (large, uppercase, centered) → Use for classification
- MIDDLE 30-70%: Body content → Ignore
- BOTTOM 70-100%: Signature → Ignore
- Ignore: "theo X", "căn cứ X", "do X cấp"
```

**TIẾT KIỆM: ~700 tokens (70%)**

---

### 🟡 **DOCUMENT LIST VARIANTS** (~800 tokens → 400 tokens)

**Hiện tại:** Liệt kê từng variant
```
BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT → BBKTHT
  (Variants: "BIÊN BẢN\nXác minh thực địa...", 
             "BIÊN BẢN\nKiểm tra xác minh hiện trạng...",
             "BIÊN BẢN\nXác minh hiện trạng sử dụng đất")
```

**ĐỀ XUẤT:**
```
BIÊN BẢN XÁC MINH/KIỂM TRA HIỆN TRẠNG/THỰC ĐỊA → BBKTHT
```

**TIẾT KIỆM: ~400 tokens (50%)**

---

### 🟡 **EMOJIS & FORMATTING** (~200 tokens → 50 tokens)

**Hiện tại:** Nhiều emoji, bullets, formatting
```
🎯 PHÂN TÍCH VỊ TRÍ VĂN BẢN (POSITION-AWARE CLASSIFICATION)
⚠️ CỰC KỲ QUAN TRỌNG: ...
📍 QUY TẮC VỊ TRÍ:
1️⃣ **PHẦN ĐẦU TRANG**...
✅ ĐÚNG:...
❌ SAI:...
```

**ĐỀ XUẤT:** Bỏ emoji, giữ structure đơn giản
```
POSITION-AWARE RULES:
- TOP 30%: title
- MIDDLE: body (ignore)
- BOTTOM: signature (ignore)

CORRECT: Title at top → Classify
WRONG: Mention in body → Ignore
```

**TIẾT KIỆM: ~150 tokens (75%)**

---

## 📊 **TỔNG KẾT RÚT GỌN**

| Phần | Hiện tại | Sau tối ưu | Tiết kiệm |
|------|----------|------------|-----------|
| **Examples** | 1,500 | 300 | 1,200 (80%) |
| **Repetitions** | 800 | 200 | 600 (75%) |
| **Explanations** | 1,000 | 300 | 700 (70%) |
| **Variants** | 800 | 400 | 400 (50%) |
| **Emojis** | 200 | 50 | 150 (75%) |
| **Core Rules** | 3,200 | 2,750 | 450 (14%) |
| **TOTAL** | **7,500** | **4,000** | **3,500 (47%)** |

---

## 💰 **TIẾT KIỆM CHI PHÍ**

### Batch Mode (5 trang):
```
Hiện tại:
- Input: 7,500 tokens × $0.000000075 = $0.00056
- Per batch: $0.00056

Sau tối ưu:
- Input: 4,000 tokens × $0.000000075 = $0.0003
- Per batch: $0.0003

TIẾT KIỆM: $0.00026 per batch (46%)
```

### Tính theo volume (100 trang/ngày = 20 batches):
```
Hiện tại:  20 × $0.00056 = $0.0112/day × 30 = $0.336/month ≈ 7,900 VND/tháng
Sau tối ưu: 20 × $0.0003 = $0.006/day × 30 = $0.18/month ≈ 4,230 VND/tháng

TIẾT KIỆM: ~3,670 VND/tháng (46%)
```

### Tính theo volume (500 trang/ngày = 100 batches):
```
Hiện tại:  100 × $0.00056 = $0.056/day × 30 = $1.68/month ≈ 39,480 VND/tháng
Sau tối ưu: 100 × $0.0003 = $0.03/day × 30 = $0.9/month ≈ 21,150 VND/tháng

TIẾT KIỆM: ~18,330 VND/tháng (46%)
```

---

## 🎯 **CÁC PHẦN ĐỀ XUẤT CỤ THỂ**

### ✅ **GIỮ NGUYÊN (KHÔNG SỬA):**

1. ✅ **Position-aware rules** (TOP/MIDDLE/BOTTOM logic)
2. ✅ **GCN special handling** (không trả GCNM/GCNC, tìm issue_date)
3. ✅ **Title vs Reference distinction** (độc lập vs có "theo/căn cứ")
4. ✅ **98 document types list** (nhưng rút gọn variants)
5. ✅ **JSON response format**

### 🔧 **RÚT GỌN MẠNH (KHUYẾN NGHỊ):**

1. ❌ **Bỏ 80% examples** (giữ 2-3 examples quan trọng nhất)
2. ❌ **Bỏ repetitive warnings** (mỗi rule chỉ nói 1 lần)
3. ❌ **Bỏ verbose explanations** (chỉ giữ core rules)
4. ❌ **Gộp variants thành 1 dòng** (dùng "/" thay vì liệt kê)
5. ❌ **Bỏ emojis, simplify formatting**

### 🟡 **RÚT GỌN VỪA PHẢI (NẾU LO GIẢM ACCURACY):**

1. 🔸 **Giữ 50% examples** (thay vì 20%)
2. 🔸 **Giữ key warnings** (lặp 2 lần thay vì 5 lần)
3. 🔸 **Simplify nhưng không bỏ hẳn explanations**

---

## 🧪 **TESTING PLAN**

### Sau khi tối ưu, cần test:
1. ✅ **Accuracy check** (100 samples random)
2. ✅ **GCN classification** (quan trọng nhất)
3. ✅ **Edge cases** (continuation pages, references, mentions)
4. ✅ **Cost verification** (đo actual tokens used)

### Acceptance criteria:
- ✅ Accuracy >= 93% (giống hiện tại)
- ✅ Token usage giảm >= 40%
- ✅ GCN classification vẫn chính xác 100%

---

## 🚀 **IMPLEMENTATION PLAN**

### Phase 1: Rút gọn ít rủi ro (KHUYẾN NGHỊ LÀM TRƯỚC)
```
1. Bỏ 80% examples (giữ 2-3 quan trọng)
2. Bỏ repetitive warnings
3. Bỏ emojis & formatting
4. Gộp variants

TIẾT KIỆM: ~2,500 tokens (33%)
RỦI RO: Thấp (không ảnh hưởng core logic)
```

### Phase 2: Rút gọn explanations (NẾU PHASE 1 OK)
```
1. Simplify verbose explanations
2. Condense rules descriptions
3. Shorten document descriptions

TIẾT KIỆM: ~1,000 tokens (thêm 13%)
RỦI RO: Trung bình (có thể ảnh hưởng clarity)
```

---

## 📝 **QUYẾT ĐỊNH CỦA BẠN**

**Option A: RÚT GỌN MẠNH (47% - Khuyến nghị)**
- Tiết kiệm: 3,500 tokens
- Rủi ro: Trung bình
- Cần test kỹ

**Option B: RÚT GỌN VỪA PHẢI (30%)**
- Tiết kiệm: 2,250 tokens
- Rủi ro: Thấp
- An toàn hơn

**Option C: CHỈ RÚT GỌN ÍT (15% - An toàn nhất)**
- Tiết kiệm: 1,125 tokens
- Rủi ro: Rất thấp
- Giữ hầu hết content

**Option D: KHÔNG THAY ĐỔI**
- Giữ nguyên 7,500 tokens
- Zero risk
- Chi phí cao hơn

---

## 🎯 **KHUYẾN NGHỊ CỦA TÔI**

### ✅ **BẮT ĐẦU VỚI OPTION B (30% - VỪA PHẢI)**

**Lý do:**
1. ✅ Tiết kiệm đáng kể (~2,250 tokens ≈ $0.00017/batch)
2. ✅ Rủi ro thấp (chỉ bỏ redundant content)
3. ✅ Dễ rollback nếu có vấn đề
4. ✅ Giữ đủ context cho AI hiểu rõ

**Sau đó:**
- Test 100-200 samples
- Nếu accuracy OK → Tiến tới Option A (47%)
- Nếu accuracy giảm → Rollback hoặc dừng ở Option B

---

**Bạn muốn tôi:**
1. ✅ Implement Option B (30% - Khuyến nghị) ngay?
2. 🔧 Implement Option A (47% - Aggressive) luôn?
3. 🟡 Tạo version mới để bạn review trước?
4. ❌ Không thay đổi, giữ nguyên?

Vui lòng cho tôi biết lựa chọn của bạn! 🚀
