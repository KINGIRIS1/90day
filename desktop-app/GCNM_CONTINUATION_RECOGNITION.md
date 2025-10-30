# GCNM Continuation Page Recognition - Implementation Complete

## 📋 Tổng quan (Overview)

Cập nhật logic nhận diện cho các trang tiếp theo của Giấy Chứng Nhận (GCN continuation pages) để tự động phân loại là `GCNM` ngay cả khi trang không có tiêu đề chính.

Updated the recognition logic for GCN (Giấy Chứng Nhận) continuation pages to automatically classify them as `GCNM` even when the page doesn't have a primary title.

---

## 🎯 Vấn đề (Problem)

### Trước đây:
- Trang tiếp theo của GCN không có tiêu đề chính → Phân loại là `UNKNOWN`
- Frontend phải tự động gán tên dựa vào trang trước
- Tuy nhiên, trong batch scanning, trang GCN có thể đứng riêng hoặc sau giấy tờ khác → Bị phân loại sai

### Previously:
- GCN continuation pages without main title → Classified as `UNKNOWN`
- Frontend had to auto-assign name based on previous page
- However, in batch scanning, GCN pages can stand alone or follow other documents → Misclassified

---

## ✅ Giải pháp (Solution)

### Nhận diện thông minh GCN continuation pages:

AI sẽ tự động nhận là `GCNM` khi thấy các section đặc trưng:

1. **"NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" + "XÁC NHẬN CỦA CƠ QUAN"**
   - PHẢI CÓ CẢ HAI: "Nội dung thay đổi" + "Cơ quan"
   - Confidence: 0.85
   
2. **"THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"**
   - Confidence: 0.85
   
3. **"II. NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ"**
   - Section II về thay đổi
   - Confidence: 0.8
   
4. **"III. XÁC NHẬN CỦA CƠ QUAN"**
   - PHẢI có từ "CƠ QUAN", KHÔNG phải "ỦY BAN NHÂN DÂN"
   - Confidence: 0.8

### ⚠️ CRITICAL: Phân biệt GCNM vs DDKBD

**GCNM (Giấy chứng nhận):**
- ✅ "III. XÁC NHẬN CỦA **CƠ QUAN**"
- ✅ "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN"
- Keyword: **"CƠ QUAN"** (agency/authority)
- Thường là section III

**DDKBD (Đơn đăng ký biến động) - KHÔNG PHẢI GCN:**
- ❌ "II. XÁC NHẬN CỦA **ỦY BAN NHÂN DÂN CẤP XÃ**"
- ❌ "XÁC NHẬN CỦA ỦY BAN NHÂN DÂN"
- Keyword: **"ỦY BAN NHÂN DÂN"** (People's Committee)
- Thường là section II
- → Trả về: **UNKNOWN** (không phải GCNM!)

**QUY TẮC:**
- NẾU thấy "ỦY BAN NHÂN DÂN" → KHÔNG phải GCNM
- CHỈ KHI thấy "CƠ QUAN" → Mới xét GCNM

### Additional indicators:
- Bảng thông tin thửa đất (số hiệu, diện tích, vị trí...)
- Section "Nội dung thay đổi", "Cơ sở pháp lý"
- Section "Xác nhận của **CƠ QUAN**" (không phải "Ủy ban nhân dân")
- Format dạng phiếu chính thức với các ô điền thông tin đất đai

---

## 🔧 Files Updated

### 1. **Desktop App - Gemini Flash**
**File:** `/app/desktop-app/python/ocr_engine_gemini_flash.py`

**Changes:**
- Updated the main classification prompt (second version, lines 502-595)
- Added comprehensive GCN continuation page recognition logic
- Added clear distinction between title-based classification vs. content-based GCN detection
- Added Vietnamese examples for clarity

### 2. **Backend - OpenAI Vision**
**File:** `/app/backend/server.py`

**Changes:**
- Updated OpenAI Vision prompt (lines 616-700)
- Added identical GCN continuation page recognition logic
- Ensures consistency between Gemini Flash (desktop) and OpenAI Vision (Cloud Boost)

---

## 📊 Example Cases

### ✅ Correctly classified as GCNM:

1. **Standalone GCN continuation page**
   - Content: Only has section "Nội dung thay đổi và cơ sở pháp lý"
   - No main title
   - Result: `GCNM` (confidence: 0.85)

2. **GCN page after other document in batch scan**
   - Previous page: HDCQ (contract)
   - Current page: Section "Thửa đất, nhà ở và tài sản..."
   - Not related to HDCQ
   - Result: `GCNM` (confidence: 0.85)

3. **GCN page with standard format**
   - Content: "II. NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ"
   - Standard GCN page 2 format
   - Result: `GCNM` (confidence: 0.8)

### ❌ Not classified as GCN:

1. **DDKBD (Đơn đăng ký biến động) pages**
   - Content: "II. XÁC NHẬN CỦA ỦY BAN NHÂN DÂN CẤP XÃ"
   - Keyword: "ỦY BAN NHÂN DÂN" (People's Committee)
   - This is DDKBD, NOT GCN!
   - Result: `UNKNOWN`

2. **Other document sections**
   - Content: "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG"
   - This is NOT a GCN section
   - This is from PCT or other documents
   - Result: `UNKNOWN`

---

## 🎯 Benefits

1. **Improved Batch Scanning:**
   - GCN continuation pages correctly identified even when standalone
   - No dependency on previous page context
   - Reduces `UNKNOWN` classifications

2. **Consistency:**
   - Same logic applied to both Gemini Flash and OpenAI Vision
   - Predictable behavior across AI engines

3. **Smart Detection:**
   - Content-based recognition for specific GCN sections
   - High confidence scores (0.8-0.85) for valid GCN continuation pages
   - Clear distinction from other document types

---

## 🧪 Testing Recommendations

Test with the following scenarios:

1. **Single GCN document (multiple pages)**
   - Page 1: Title page → GCNM
   - Page 2: Continuation → GCNM (0.8-0.85)
   
2. **Mixed batch scan**
   - HDCQ page
   - GCN continuation page
   - Should correctly classify GCN page as GCNM

3. **Edge cases**
   - Other documents with similar section headers
   - Should NOT be classified as GCNM

---

## 📝 Notes

- This update only affects AI-based classification (Gemini Flash, OpenAI Vision)
- Rule-based classification still relies on title matching
- Frontend sequential naming logic remains as fallback for other continuation pages
- The logic is explicitly documented in Vietnamese for clarity with the AI models

---

## 📅 Date

**Implemented:** December 2024

**Status:** ✅ Complete and deployed
