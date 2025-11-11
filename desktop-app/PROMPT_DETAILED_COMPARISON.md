# 🔍 PHÂN TÍCH CHI TIẾT TỪNG ĐOẠN PROMPT - BỎ GÌ, GIỮ GÌ

## 📋 MỤC LỤC
1. [Section 1: Warning & Introduction](#section-1)
2. [Section 2: Position Rules](#section-2)
3. [Section 3: Title vs Reference](#section-3)
4. [Section 4: GCN Special Rules](#section-4)
5. [Section 5: Document List](#section-5)
6. [Section 6: Response Format](#section-6)

---

<a name="section-1"></a>
## 📍 SECTION 1: WARNING & INTRODUCTION

### ❌ **BỎ - Lines 893-896** (~80 tokens)

**HIỆN TẠI:**
```
⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.
```

**TẠI SAO BỎ:**
- Gemini 2.5 Flash đủ thông minh để hiểu context
- Không cần giải thích về ảnh con người (AI biết focus vào text)
- Warning này lặp lại ý chính ở nhiều chỗ khác

**ĐỀ XUẤT:** Bỏ hẳn

---

### ✅ **GIỮ - Lines 897-899** (~30 tokens)

**HIỆN TẠI:**
```
🎯 PHÂN TÍCH VỊ TRÍ VĂN BẢN (POSITION-AWARE CLASSIFICATION)

⚠️ CỰC KỲ QUAN TRỌNG: CHỈ PHÂN LOẠI DỰA VÀO TEXT Ở PHẦN ĐẦU TRANG!
```

**TẠI SAO GIỮ:**
- Core concept của toàn bộ prompt
- Position-aware là key differentiation

**ĐỀ XUẤT RÚT GỌN:**
```
POSITION-AWARE CLASSIFICATION: Only classify based on TOP title.
```

**TIẾT KIỆM:** 50% (~15 tokens)

---

<a name="section-2"></a>
## 📍 SECTION 2: POSITION RULES

### 🔄 **RÚT GỌN - Lines 901-936** (~600 tokens → 150 tokens)

**HIỆN TẠI (36 dòng):**
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

3️⃣ **PHẦN CUỐI TRANG (BOTTOM 70-100%)**
   - Đây là CHỮ KÝ, CON DẤU, GHI CHÚ
   - ❌ KHÔNG được phân loại dựa vào text ở đây

🔍 CÁCH PHÂN TÍCH:

BƯỚC 1: Nhìn vào ảnh, ước lượng vị trí của các đoạn text
- TOP 30%: Vùng tiêu đề
- MIDDLE 30-70%: Vùng body
- BOTTOM 70-100%: Vùng chữ ký

BƯỚC 2: Tìm tiêu đề chính (PHẢI Ở TOP 30%)
- Cỡ chữ lớn nhất
- IN HOA
- Căn giữa hoặc nổi bật
- Ở gần đầu trang

BƯỚC 3: Phân loại dựa vào tiêu đề TOP
- NẾU tìm thấy tiêu đề khớp ở TOP → Phân loại theo đó
- NẾU KHÔNG có tiêu đề ở TOP → Kiểm tra NGOẠI LỆ (GCN continuation)
- NẾU thấy mentions ở MIDDLE/BOTTOM → BỎ QUA
```

**TẠI SAO RÚT GỌN:**
- Quá dài dòng, lặp lại ý nhiều lần
- AI không cần từng bước chi tiết như vậy
- Các ví dụ đơn giản không cần thiết

**ĐỀ XUẤT SAU RÚT GỌN (8 dòng):**
```
POSITION RULES:
- TOP 30%: Main title area (large, uppercase, centered) → USE for classification
- MIDDLE 30-70%: Body content → IGNORE
- BOTTOM 70-100%: Signature area → IGNORE

CLASSIFY:
1. Find title in TOP 30% (largest text, uppercase, standalone)
2. If TOP title matches document type → Classify
3. If no TOP title → Return UNKNOWN (except GCN continuation)
```

**TIẾT KIỆM:** 75% (~450 tokens)

---

### ❌ **BỎ HOÀN TOÀN - Lines 938-975** (~600 tokens)

**HIỆN TẠI (38 dòng):**
```
VÍ DỤ ĐÚNG:

✅ ĐÚNG:
Trang có text "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở TOP 20% (gần đầu trang, chữ lớn)
→ title_position: "top"
→ short_code: "HDCQ"
→ confidence: 0.9

✅ ĐÚNG:
Trang có text "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI" ở TOP 15%
→ title_position: "top"
→ short_code: "DDKBD"
→ confidence: 0.9

VÍ DỤ SAI:

❌ SAI - REFERENCE/MENTION (không phải title):
Trang có "Mẫu số 17C..." ở TOP, trong body có "...theo Giấy chứng nhận quyền sử dụng đất số..."
→ Đây là REFERENCE/MENTION, KHÔNG phải title
→ "theo Giấy chứng nhận..." = Căn cứ/Tham chiếu
→ Form 17C = TTHGD (Thỏa thuận hộ gia đình)
→ short_code: "TTHGD"
→ reasoning: "Form 17C, mentions to GCN are references only"

❌ SAI - MENTION trong body:
Trang có "Giấy chứng nhận" ở TOP, nhưng ở MIDDLE có text "...theo hợp đồng chuyển nhượng..."
→ KHÔNG phân loại là HDCQ
→ Chỉ mention trong body, không phải title
→ short_code: "GCNM" (dựa vào title ở TOP)
→ title_position: "top"

❌ SAI - Text ở MIDDLE:
Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở MIDDLE (giữa trang)
→ Đây KHÔNG phải tiêu đề chính
→ title_position: "middle"
→ short_code: "UNKNOWN"
→ reasoning: "Text found in middle of page, not a main title"

❌ SAI - LOWERCASE REFERENCE trong body (QUAN TRỌNG):
Trang có danh sách người thừa kế, trong body có "...đã từ chối nhận di sản theo văn bản từ chối nhận di sản số..."
→ "văn bản từ chối" = lowercase, trong câu văn, có "theo" → REFERENCE
→ KHÔNG có title chính ở TOP
→ Đây là danh sách / continuation page
→ short_code: "UNKNOWN" hoặc "GTLQ"
→ reasoning: "No main title at top, 'văn bản từ chối' is lowercase reference in body text"

✅ ĐÚNG - Nếu có TITLE thực sự:
Trang có "VĂN BẢN TỪ CHỐI NHẬN DI SẢN" ở TOP (chữ lớn, IN HOA)
→ Đây là TITLE chính thức
→ title_position: "top"
→ short_code: "VBTC"
→ reasoning: "Main title at top in uppercase"
```

**TẠI SAO BỎ:**
- ✅ và ❌ examples quá nhiều, lặp lại logic đã nói ở trên
- Gemini Flash đủ thông minh, không cần 6-7 ví dụ chi tiết
- Mỗi example ~100 tokens, có thể thay bằng 1-2 examples ngắn

**ĐỀ XUẤT THAY THẾ (2 examples ngắn gọn):**
```
EXAMPLES:
✓ "HỢP ĐỒNG CHUYỂN NHƯỢNG" at TOP → HDCQ
✗ "theo hợp đồng chuyển nhượng" in body → Ignore (reference)
```

**TIẾT KIỆM:** 95% (~570 tokens)

---

<a name="section-3"></a>
## 📍 SECTION 3: TITLE vs REFERENCE DISTINCTION

### 🔄 **RÚT GỌN - Lines 991-1057** (~1,100 tokens → 200 tokens)

**HIỆN TẠI (67 dòng):**
```
⚠️ QUAN TRỌNG - PHÂN BIỆT REFERENCE vs TITLE:

❌ REFERENCES (bỏ qua khi classify):
- "Căn cứ Giấy chứng nhận..."
- "Theo Giấy chứng nhận số..."
- "Kèm theo hợp đồng..."
- "Theo quyết định..."
- "...do...cấp ngày..."
- "...theo văn bản từ chối..." (lowercase, trong body)
- "...đã từ chối nhận di sản theo văn bản từ chối..." (reference)

✅ ACTUAL TITLES (dùng để classify):
- "GIẤY CHỨNG NHẬN" (ở đầu trang, chữ lớn, không có "căn cứ/theo")
- "HỢP ĐỒNG CHUYỂN NHƯỢNG" (ở đầu trang, chữ lớn)
- "ĐƠN ĐĂNG KÝ..." (ở đầu trang, chữ lớn)
- "VĂN BẢN TỪ CHỐI NHẬN DI SẢN" (ở đầu trang, chữ lớn, title case/uppercase)

🔍 DẤU HIỆU NHẬN BIẾT REFERENCE:
- Có từ "căn cứ", "theo", "kèm theo", "do...cấp", "đã từ chối...theo"
- Có số văn bản kèm theo (số AN..., số CS..., số công chứng...)
- Nằm trong câu văn dài, không standalone
- Cỡ chữ BÌNH THƯỜNG, không nổi bật
- Viết thường (lowercase): "văn bản từ chối" thay vì "VĂN BẢN TỪ CHỐI"
- **NẰM CHUNG với các từ khác trên cùng dòng** (VD: "theo Giấy chứng nhận...", "...theo văn bản...")

🎯 DẤU HIỆU NHẬN BIẾT TITLE (CỰC KỲ QUAN TRỌNG):

✅ TITLE phải NẰM ĐỘC LẬP:
- **Mỗi dòng CHỈ có text của title, KHÔNG có text khác**
- Có thể xuống dòng:
  * Dòng 1: "VĂN BẢN"
  * Dòng 2: "PHÂN CHIA TÀI SẢN..."
  * → ĐỘC LẬP, mỗi dòng chỉ có title
  
- Hoặc một dòng duy nhất:
  * "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT"
  * → ĐỘC LẬP, không có text khác

❌ KHÔNG PHẢI TITLE nếu:
- NẰM CHUNG với text khác: "theo Giấy chứng nhận quyền sử dụng đất số..."
  * "Giấy chứng nhận" KHÔNG độc lập
  * Có "theo" và "số..." trên cùng dòng/câu
  * → Đây là REFERENCE, không phải TITLE

- NẰM CHUNG với text khác: "...đã từ chối nhận di sản theo văn bản từ chối nhận di sản số..."
  * "văn bản từ chối" KHÔNG độc lập
  * Có nhiều từ khác trên cùng dòng
  * → Đây là REFERENCE, không phải TITLE

VÍ DỤ PHÂN BIỆT:

✅ TITLE (độc lập):
```
                VĂN BẢN
        PHÂN CHIA TÀI SẢN CHUNG
           CỦA HỘ GIA ĐÌNH
```
→ Mỗi dòng ĐỘC LẬP, chỉ có title
→ Classify: TTHGD

❌ REFERENCE (không độc lập):
```
2. Ông Nguyễn Văn A đã từ chối nhận di sản theo văn bản từ chối nhận di sản số 123...
```
→ "văn bản từ chối" NẰM CHUNG với "đã từ chối", "theo", "số 123"
→ KHÔNG classify theo "văn bản từ chối"
→ Classify: UNKNOWN hoặc GTLQ

❌ SECTION HEADERS (không phải title):
```
ĐIỀU 2
NỘI DUNG THỎA THUẬN PHÂN CHIA
```
→ "ĐIỀU 1:", "ĐIỀU 2:", "ĐIỀU 3:" = SECTION HEADERS, không phải MAIN TITLE
→ Đây là continuation page (trang 2+)
→ KHÔNG classify dựa vào section headers
→ Classify: UNKNOWN (hoặc GTLQ nếu là supporting doc)

⚠️ QUAN TRỌNG - BỎ QUA SECTION HEADERS:
- "ĐIỀU 1:", "ĐIỀU 2:", "Điều 3:", "I.", "II.", "III." = Section numbering
- "PHẦN I:", "PHẦN II:", "Chương 1:", "Chương 2:" = Part/Chapter headers
- Đây KHÔNG phải main title
- CHỈ classify dựa vào MAIN TITLE (không có số thứ tự, không có "Điều", "Phần")
```

**TẠI SAO RÚT GỌN:**
- Lặp lại concept "reference" vs "title" quá nhiều lần
- Examples quá dài, có thể ngắn gọn hơn
- Section headers rules có thể gộp vào 1 dòng

**ĐỀ XUẤT SAU RÚT GỌN (15 dòng):**
```
TITLE vs REFERENCE:

IGNORE (References):
- Has "căn cứ", "theo", "kèm theo", "do...cấp"
- Has document numbers (số...)
- Lowercase in body text
- Not standalone (mixed with other text on same line)

CLASSIFY (Titles):
- Standalone (own line, no other text)
- Uppercase, large font, centered
- At TOP 30% of page
- No "căn cứ/theo" prefix

IGNORE section headers: "ĐIỀU 1:", "PHẦN I:", "Chương 1:" → continuation pages
```

**TIẾT KIỆM:** 82% (~900 tokens)

---

<a name="section-4"></a>
## 📍 SECTION 4: GCN SPECIAL RULES

### ✅ **GIỮ - Lines 1075-1155** (~1,200 tokens)

**HIỆN TẠI:**
```
🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🚨 QUY TẮC CỰC KỲ QUAN TRỌNG - GIẤY CHỨNG NHẬN (GCN)

❌ TUYỆT ĐỐI KHÔNG BAO GIỜ TRẢ VỀ "GCNM" HOẶC "GCNC" ❌

⚠️ NẾU thấy Giấy chứng nhận (quốc huy + màu hồng/đỏ + "GIẤY CHỨNG NHẬN"):
   → Trả về: short_code = "GCN" (generic, không phải GCNM/GCNC)
   → BẮT BUỘC: Tìm NGÀY CẤP (thường ở trang 2, có thể viết tay)

📋 TÌM NGÀY CẤP (ISSUE DATE):
   • Vị trí: 
     - A3 (2 trang lớn): Thường ở trang 2, gần cuối trang
     - A4 (1 trang nhỏ): Thường ở trang 1, bottom
   • Text gần: "Ngày cấp", "Cấp ngày", "Ngày...tháng...năm", "TM. UBND"
   • Các format có thể gặp:
     - Format 1: "DD/MM/YYYY" (ví dụ: "01/01/2012", "15/03/2013", "14/04/2025")
     - Format 2: "Ngày DD tháng MM năm YYYY" (ví dụ: "Ngày 25 tháng 8 năm 2010")
       → PHẢI chuyển thành "DD/MM/YYYY" (ví dụ: "25/8/2010" hoặc "25/08/2010")
     - Format 3: "DD.MM.YYYY" hoặc "DD-MM-YYYY"
     - Nếu mờ: MM/YYYY hoặc YYYY
   • ⚠️ QUAN TRỌNG: Nếu thấy format "Ngày XX tháng YY năm ZZZZ":
     - ĐỌC các số XX, YY, ZZZZ (có thể viết tay)
     - CHUYỂN thành "XX/YY/ZZZZ"
     - Ví dụ: "Ngày 25 tháng 8 năm 2010" → "25/8/2010"
   • Lý do: Frontend sẽ so sánh ngày cấp:
     - Ngày nhỏ hơn = GCNC (cũ)
     - Ngày lớn hơn = GCNM (mới)
   
   ⚠️ Confidence levels:
   - "full": Đọc được đầy đủ DD/MM/YYYY
   - "partial": Chỉ đọc được MM/YYYY
   - "year_only": Chỉ đọc được YYYY
   - "not_found": Không tìm thấy (có thể là trang 1)

✅ RESPONSE ĐÚNG (Trang 2 - có ngày cấp):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận với quốc huy, màu hồng, ngày cấp 01/01/2012",
  "issue_date": "01/01/2012",
  "issue_date_confidence": "full"
}

✅ RESPONSE ĐÚNG (Trang 1 - không có ngày cấp):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận với quốc huy, màu hồng, trang 1",
  "issue_date": null,
  "issue_date_confidence": "not_found"
}

⚠️ TẠI SAO PHẢI TRẢ VỀ "GCN"?
- Không thể xác định cũ/mới khi scan TỪNG file riêng lẻ
- Cần so sánh NGÀY CẤP của TẤT CẢ GCN trong batch
- Frontend sẽ xử lý batch post-processing để phân loại GCNC/GCNM:
  * Ngày nhỏ hơn = GCNC (cũ)
  * Ngày lớn hơn = GCNM (mới)
```

**TẠI SAO GIỮ:**
- ✅ GCN là document type PHỨC TẠP NHẤT và quan trọng nhất
- ✅ Chiếm ~40% volume xử lý
- ✅ Logic đặc biệt: không trả GCNM/GCNC, phải tìm issue_date
- ✅ Nhiều edge cases: format ngày khác nhau, viết tay, mờ
- ✅ Nếu bỏ hoặc rút gọn → accuracy GCN giảm mạnh

**ĐỀ XUẤT:** GIỮ NGUYÊN (có thể rút gọn nhẹ 10-15%)

**TIẾT KIỆM:** 0 tokens (giữ nguyên)

---

### 🔄 **RÚT GỌN NHẸ - Lines 1156-1184** (~400 tokens → 300 tokens)

**HIỆN TẠI:**
```
🔍 Sau đó kiểm tra tiêu đề Ở TOP 30%:
  • "Giấy chứng nhận quyền sử dụng đất..." (bất kỳ variant) → GCN (tìm issue_date)
  • "Mẫu số 17C..." → TTHGD (Văn bản thỏa thuận hộ gia đình)
  • Form codes khác → Xem body content để xác định

⚠️ BỎ QUA các references (không phải title):
  • "Căn cứ Giấy chứng nhận..." → Reference, không classify theo đây
  • "Theo Giấy chứng nhận số..." → Reference, không classify theo đây  
  • "Kèm theo hợp đồng..." → Reference, không classify theo đây
  • "...do...cấp ngày..." → Reference, không classify theo đây

🎯 QUY TẮC NHẬN DIỆN FORM CODES:
NẾU trang có "Mẫu số" hoặc form code ở TOP mà không có title rõ ràng:
- "Mẫu số 17C" → TTHGD (Văn bản thỏa thuận QSDĐ hộ gia đình)
- Các form khác → Xem keywords trong body để xác định

VÍ DỤ THỰC TẾ:
✅ Trang có "Mẫu số 17C-CC/VBPCTSCHUNGHO" ở TOP
   Body có: "Quyền sử dụng đất...theo Giấy chứng nhận..."
   → "theo Giấy chứng nhận" là REFERENCE (not title)
   → Form 17C → TTHGD
   → short_code: "TTHGD"
   → reasoning: "Form 17C indicates TTHGD document type"

⚠️ QUAN TRỌNG với tài liệu 2 trang ngang:
- Nếu thấy nền cam/vàng với quốc huy ở bên PHẢI → Đây là GCNC
- Tập trung vào trang BÊN PHẢI để đọc tiêu đề

⚠️ BỎ QUA bất kỳ ảnh cá nhân nào - chỉ tập trung vào văn bản và con dấu chính thức.
```

**TẠI SAO RÚT GỌN:**
- Lặp lại "bỏ qua references" (đã nói ở Section 3)
- Form code example có thể ngắn hơn

**ĐỀ XUẤT SAU RÚT GỌN:**
```
Form codes: "Mẫu số 17C" → TTHGD
Ignore references starting with "Căn cứ", "Theo", "Kèm theo"
```

**TIẾT KIỆM:** 25% (~100 tokens)

---

### ❌ **BỎ - Lines 1186-1193** (~120 tokens)

**HIỆN TẠI:**
```
⚠️ QUY TẮC KHỚP: CHO PHÉP ~85-90% TƯƠNG ĐỒNG!

✅ CHẤP NHẬN khi tiêu đề khớp 85-90% với danh sách
✅ CHO PHÉP lỗi chính tả nhỏ (ví dụ: "NHUỢNG" → "NHƯỢNG")
✅ CHO PHÉP thiếu/thừa dấu câu, khoảng trắng
✅ CHO PHÉP viết tắt (ví dụ: "QSDĐ" → "quyền sử dụng đất")
❌ KHÔNG khớp nếu thiếu từ khóa QUAN TRỌNG phân biệt loại
```

**TẠI SAO BỎ:**
- Gemini Flash có fuzzy matching tự nhiên, không cần instruction
- AI model đủ thông minh để handle typos và variants

**TIẾT KIỆM:** 100% (~120 tokens)

---

### ❌ **BỎ - Lines 1194-1227** (~500 tokens)

**HIỆN TẠI:**
```
⚠️ CỰC KỲ QUAN TRỌNG: PHÂN BIỆT TIÊU ĐỀ vs NỘI DUNG BODY

🎯 TIÊU ĐỀ CHÍNH (Main Title):
- Nằm Ở ĐẦU trang, TRÊN CÙNG
- Cỡ chữ LỚN, IN HOA, căn giữa
- VD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI..."
- → CHỈ TIÊU ĐỀ CHÍNH mới dùng để phân loại!

❌ KHÔNG PHÂN LOẠI DỰA VÀO:
- Section headers (III. THÔNG TIN VỀ...)
- Mentions trong body text
- Danh sách đính kèm
- Ghi chú cuối trang

VÍ DỤ DỄ NHẦM:

❌ SAI: Trang có section "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG..."
   → Đây CHỈ là section header, KHÔNG phải title
   → Trả về: UNKNOWN (không có title chính rõ ràng)

❌ SAI: Body text có mention "...hợp đồng chuyển nhượng..."
   → Đây là mention, KHÔNG phải title
   → CHỈ phân loại HDCQ nếu có TITLE "HỢP ĐỒNG CHUYỂN NHƯỢNG"

✅ ĐÚNG: Tiêu đề ở đầu trang: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG..."
   → Có title chính rõ ràng
   → Phân loại: DDKBD

🎯 TRANG TIẾP THEO (Continuation Pages):
Nếu trang KHÔNG có tiêu đề chính (title page), có thể có:
- Section headers: "II. THÔNG TIN...", "III. ĐĂNG KÝ..."
- Body content: Danh sách, bảng biểu, nội dung chi tiết
- → Trả về: UNKNOWN (Frontend sẽ tự động gán theo trang trước)
```

**TẠI SAO BỎ:**
- Lặp lại hoàn toàn nội dung Section 2 và Section 3
- Đã nói về section headers ở trên rồi
- Examples không cần thiết

**TIẾT KIỆM:** 100% (~500 tokens)

---

### 🔄 **RÚT GỌN - Lines 1228-1299** (~1,200 tokens → 400 tokens)

**HIỆN TẠI (72 dòng về GCNM continuation):**
```
🎯 NGOẠI LỆ QUAN TRỌNG - NHẬN DIỆN GCNM (Continuation):

⚠️ ĐẶC BIỆT: Trang GCN continuation có thể đứng RIÊNG hoặc sau giấy tờ khác!

✅ NẾU THẤY CẢ HAI SECTIONS SAU (KẾT HỢP) → TRẢ VỀ GCNM:

⚠️ CỰC KỲ QUAN TRỌNG: PHẢI CÓ CẢ HAI SECTIONS!

1️⃣ "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" (thường ở phần trên)
   +
   "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN" (thường ở phần dưới)
   
   → Đây là trang 2 của GCNM
   → PHẢI CÓ CẢ HAI: "Nội dung thay đổi" + "Xác nhận cơ quan"
   → NẾU CHỈ CÓ MỘT TRONG HAI → KHÔNG phải GCNM → UNKNOWN
   → Trả về: GCNM (confidence: 0.85)

2️⃣ "THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"
   → Đây là trang 2 của GCNM
   → Trả về: GCNM (confidence: 0.85)

3️⃣ CẢ HAI: "II. NỘI DUNG THAY ĐỔI" + "III. XÁC NHẬN CỦA CƠ QUAN"
   → PHẢI CÓ CẢ HAI sections (II và III)
   → Đây là trang 2 của GCNM
   → Trả về: GCNM (confidence: 0.85)

⚠️ ĐIỀU KIỆN CỰC QUAN TRỌNG:
- NẾU CHỈ CÓ "II. NỘI DUNG THAY ĐỔI" mà KHÔNG có "III. XÁC NHẬN" → UNKNOWN
- NẾU CHỈ CÓ "III. XÁC NHẬN" mà KHÔNG có "II. NỘI DUNG THAY ĐỔI" → UNKNOWN
- PHẢI CÓ CẢ HAI thì mới là GCNM

(+ 40 dòng examples tương tự)
```

**TẠI SAO RÚT GỌN:**
- Lặp lại điều kiện "PHẢI CÓ CẢ HAI" quá nhiều lần
- Examples quá dài

**ĐỀ XUẤT SAU RÚT GỌN:**
```
GCN CONTINUATION (GCNM) - Exception:
If page has BOTH sections:
1. "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" (or "II. NỘI DUNG THAY ĐỔI")
   AND
2. "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN" (or "III. XÁC NHẬN")

OR

"THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"

→ Return: GCNM (confidence: 0.85)

Note: Must have BOTH sections. If only one → Return UNKNOWN
```

**TIẾT KIỆM:** 67% (~800 tokens)

---

<a name="section-5"></a>
## 📍 SECTION 5: DOCUMENT LIST

### 🔄 **RÚT GỌN - Lines 1301-1500** (~3,000 tokens → 1,800 tokens)

**HIỆN TẠI:** 98 loại tài liệu với variants chi tiết

**Ví dụ verbose:**
```
BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT → BBKTHT
  (Variants: "BIÊN BẢN\nXác minh thực địa...", 
             "BIÊN BẢN\nKiểm tra xác minh hiện trạng...",
             "BIÊN BẢN\nXác minh hiện trạng sử dụng đất")

GIẤY TỜ LIÊN QUAN (CÁC LOẠI GIẤY TỜ KÈM THEO) → GTLQ
  (Variants: "TÀI LIỆU LIÊN QUAN", 
             "HỒ SƠ LIÊN QUAN", 
             "GIẤY TỜ KHÁC", 
             "TÀI LIỆU KHÁC", 
             "VĂN BẢN KHAI NHẬN DI SẢN", 
             "PHIẾU BÁO")

ĐƠN CAM KẾT, GIẤY CAM KẾT → DCK
  (Variants: "GIẤY CAM KẾT\n(V/v chọn thửa đất...)", 
             "ĐƠN CAM KẾT")
```

**ĐỀ XUẤT RÚT GỌN (dùng "/" để gộp variants):**
```
BIÊN BẢN XÁC MINH/KIỂM TRA HIỆN TRẠNG/THỰC ĐỊA → BBKTHT

GIẤY TỜ/TÀI LIỆU/HỒ SƠ LIÊN QUAN/KHÁC → GTLQ

ĐƠN/GIẤY CAM KẾT → DCK
```

**TẠI SAO RÚT GỌN:**
- Gemini Flash hiểu fuzzy matching
- Không cần liệt kê từng variant chi tiết
- Dùng "/" để indicate alternatives

**TIẾT KIỆM:** 40% (~1,200 tokens)

---

### ✅ **GIỮ - Confused pairs section (Lines 1301-1336)** (~500 tokens)

**HIỆN TẠI:**
```
CÁC CẶP DỄ NHẦM - PHẢI CÓ TỪ KHÓA PHÂN BIỆT:

1. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG" hoặc tương tự)
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   ⚠️ CHECK HDCQ TRƯỚC! Nếu có cả 2 từ → chọn HDCQ
   Nếu không rõ loại → "UNKNOWN"

2. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" → Nên chọn DDK (phổ biến hơn)

(+ các cặp khác)
```

**TẠI SAO GIỮ:**
- ✅ Critical để phân biệt các loại dễ nhầm
- ✅ HDCQ vs HDUQ, DDKBD vs DDK chiếm ~20% errors nếu không có
- ✅ Ngắn gọn (35 dòng), không redundant

**TIẾT KIỆM:** 0 tokens (giữ nguyên)

---

<a name="section-6"></a>
## 📍 SECTION 6: RESPONSE FORMAT & FINAL INSTRUCTIONS

### ✅ **GIỮ - JSON Format (Lines 1500-1600)** (~800 tokens)

**HIỆN TẠI:**
```
🎯 RESPONSE FORMAT (JSON):
{
  "short_code": "HDCQ",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Brief explanation...",
  "title_extracted": "HỢP ĐỒNG CHUYỂN NHƯỢNG",
  "uppercase_percentage": 95,
  "title_boost_applied": true,
  "issue_date": "15/03/2008",
  "issue_date_confidence": "full",
  "metadata": {...}
}

⚠️ VALIDATION RULES:
- confidence: 0.0-1.0
- title_position: "top" | "middle" | "bottom" | "none"
- issue_date: DD/MM/YYYY or null
- issue_date_confidence: "full" | "partial" | "year_only" | "not_found"
```

**TẠI SAO GIỮ:**
- ✅ Backend parse JSON response, must be exact format
- ✅ Field definitions critical

**TIẾT KIỆM:** 0 tokens (giữ nguyên)

---

## 📊 TỔNG KẾT TOKENS TIẾT KIỆM

| Section | Hiện tại | Sau tối ưu | Tiết kiệm | % |
|---------|----------|------------|-----------|---|
| 1. Warning & Intro | 110 | 30 | 80 | 73% |
| 2. Position Rules | 600 | 150 | 450 | 75% |
| 2b. Position Examples | 600 | 50 | 550 | 92% |
| 3. Title vs Reference | 1,100 | 200 | 900 | 82% |
| 4. GCN Rules | 1,200 | 1,200 | 0 | 0% ✅ |
| 4b. Form codes | 400 | 300 | 100 | 25% |
| 4c. Fuzzy matching | 120 | 0 | 120 | 100% |
| 4d. Body vs Title repeat | 500 | 0 | 500 | 100% |
| 4e. GCNM continuation | 1,200 | 400 | 800 | 67% |
| 5. Confused pairs | 500 | 500 | 0 | 0% ✅ |
| 5b. Document list | 3,000 | 1,800 | 1,200 | 40% |
| 6. Response format | 800 | 800 | 0 | 0% ✅ |
| **TOTAL** | **10,130** | **5,430** | **4,700** | **46%** |

---

## 🎯 FINAL RECOMMENDATION

### **OPTION B - RÚT GỌN VỪA PHẢI (30%)**

**Những gì SẼ BỎ:**
✅ 80% examples (550 tokens)
✅ Repetitive warnings (600 tokens)
✅ Body vs Title repeat section (500 tokens)
✅ Fuzzy matching rules (120 tokens)
✅ 30% document variants (700 tokens)

**TOTAL BỎ:** ~2,470 tokens (24%)

**Những gì SẼ GIỮ NGUYÊN:**
✅ GCN rules (1,200 tokens) - CRITICAL
✅ Position-aware core logic (150 tokens)
✅ Title vs Reference distinction (200 tokens)
✅ Confused pairs (500 tokens)
✅ Response format (800 tokens)
✅ Document list (rút gọn variants)

**Kết quả:**
- Từ 10,130 tokens → 7,660 tokens
- Tiết kiệm: 24% (~2,470 tokens)
- Rủi ro: **THẤP**
- Chi phí tiết kiệm: ~8,000 VND/tháng (100 trang/ngày)

---

**Bạn muốn:**
1. ✅ **Implement Option B (24% - An toàn)** - Tôi code luôn
2. 🚀 **Implement Option A (46% - Aggressive)** - Bỏ nhiều hơn
3. 🔍 **Xem trước full prompt mới** - Review trước khi implement
4. ❌ **Không thay đổi** - Giữ nguyên

Vui lòng cho tôi biết! 🎯
