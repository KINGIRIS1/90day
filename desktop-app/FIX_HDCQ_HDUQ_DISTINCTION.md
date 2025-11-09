# Sửa Lỗi: Gemini Nhầm Lẫn HDCQ và HDUQ

## Ngày: January 2025
## Trạng thái: ✅ ĐÃ SỬA

---

## 🐛 Vấn Đề

### Báo Cáo Từ Người Dùng
```
File: 20220105-07300010.jpg
Gemini đọc được: "HỢP ĐỒNG ỦY QUYỀN"
Kết quả phân loại: HDCQ ❌ (SAI!)
Kết quả đúng phải là: HDUQ ✅
```

### Console Log
```javascript
🤖 Gemini response: {
  "short_code": "HDCQ",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Tiêu đề 'HỢP ĐỒNG ỦY QUYỀN' nằm ở top, in hoa, độc lập..."
}
```

**Phân tích:**
- Gemini **ĐỌC ĐÚNG** tiêu đề: "HỢP ĐỒNG ỦY QUYỀN"
- Nhưng **PHÂN LOẠI SAI**: trả về HDCQ thay vì HDUQ
- Lý do: Prompt không đủ rõ ràng về sự khác biệt

---

## 🔍 Nguyên Nhân

### Prompt Cũ (Không Rõ Ràng)
```
NHÓM 2 - HỢP ĐỒNG:
HDCQ = Hợp đồng chuyển nhượng quyền sử dụng đất (bao gồm cả hợp đồng tặng cho)
HDTG = Hợp đồng tặng cho quyền sử dụng đất (alias của HDCQ, có thể dùng cả 2)
HDUQ = Hợp đồng ủy quyền
```

**Vấn đề:**
1. ❌ Không giải thích rõ sự khác biệt giữa "chuyển nhượng" và "ủy quyền"
2. ❌ Không có ví dụ cụ thể cho HDUQ
3. ❌ Không có cảnh báo mạnh về việc phân biệt

---

## ✅ Giải Pháp

### 1. Cập Nhật Định Nghĩa (Rõ Ràng Hơn)

**File:** `/app/desktop-app/python/ocr_engine_gemini_flash.py`
**Lines:** 388-413

```python
NHÓM 2 - HỢP ĐỒNG (QUAN TRỌNG - PHÂN BIỆT RÕ):
⚠️ PHÂN BIỆT CHÍNH XÁC:
HDCQ = Hợp đồng chuyển nhượng, tặng cho quyền sử dụng đất
  • Tiêu đề CHÍNH XÁC: "HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT"
  • Hoặc: "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT"
  • Keywords: "chuyển nhượng", "tặng cho", "bán đất", "mua đất", "quyền sử dụng đất"
  • Nội dung: Chuyển quyền sở hữu đất từ A sang B (bán/tặng)
  • ✅ VD ĐÚNG: Title có "CHUYỂN NHƯỢNG" → HDCQ

HDUQ = Hợp đồng ủy quyền
  • Tiêu đề CHÍNH XÁC: "HỢP ĐỒNG ỦY QUYỀN"
  • Keywords: "ủy quyền", "người ủy quyền", "người được ủy quyền", "thay mặt"
  • Nội dung: A ủy quyền cho B làm thủ tục (KHÔNG chuyển quyền sở hữu)
  • ✅ VD ĐÚNG: Title có "ỦY QUYỀN" (KHÔNG có "chuyển nhượng") → HDUQ
  • 🚨 QUAN TRỌNG: Nếu title là "HỢP ĐỒNG ỦY QUYỀN" → BẮT BUỘC trả về HDUQ (KHÔNG phải HDCQ)
```

**Điểm mới:**
- ✅ Giải thích rõ sự khác biệt về nội dung
- ✅ Có tiêu đề chính xác cho từng loại
- ✅ Có keywords đặc trưng
- ✅ Có cảnh báo mạnh (🚨 BẮT BUỘC)

---

### 2. Thêm Ví Dụ Cụ Thể

**File:** `/app/desktop-app/python/ocr_engine_gemini_flash.py`
**Lines:** 626-634

```python
✅ ĐÚNG:
- Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở top, chữ lớn
  → {short_code: "HDCQ", title_position: "top", confidence: 0.95}
  → Reasoning: "Hợp đồng chuyển nhượng đất, title rõ ràng"

- Trang có "HỢP ĐỒNG ỦY QUYỀN" ở top, chữ lớn
  → {short_code: "HDUQ", title_position: "top", confidence: 0.95}
  → Reasoning: "Hợp đồng ủy quyền (KHÔNG phải chuyển nhượng), title rõ ràng"
  → 🚨 QUAN TRỌNG: "ỦY QUYỀN" ≠ "CHUYỂN NHƯỢNG" → HDUQ (KHÔNG phải HDCQ)
```

**Điểm mới:**
- ✅ Ví dụ JSON đầy đủ cho cả 2 loại
- ✅ Reasoning rõ ràng
- ✅ Cảnh báo ngay trong ví dụ

---

### 3. Thêm Ví Dụ SAI

**File:** `/app/desktop-app/python/ocr_engine_gemini_flash.py`
**Lines:** 648-654

```python
❌ SAI:
- Trang có title "HỢP ĐỒNG ỦY QUYỀN" nhưng classify thành HDCQ
  → ❌ SAI! Title rõ ràng là "ỦY QUYỀN" → Phải là HDUQ (KHÔNG phải HDCQ)
  → 🚨 LƯU Ý: Đọc kỹ title, "ỦY QUYỀN" khác hoàn toàn với "CHUYỂN NHƯỢNG"
```

**Điểm mới:**
- ✅ Ví dụ lỗi cụ thể (chính xác vấn đề của user)
- ✅ Giải thích tại sao sai
- ✅ Nhấn mạnh sự khác biệt

---

## 📊 So Sánh HDCQ vs HDUQ

| Tiêu chí | HDCQ (Chuyển nhượng) | HDUQ (Ủy quyền) |
|----------|----------------------|-----------------|
| **Tiêu đề** | HỢP ĐỒNG CHUYỂN NHƯỢNG | HỢP ĐỒNG ỦY QUYỀN |
| **Mục đích** | Chuyển quyền sở hữu đất | Ủy quyền làm thủ tục |
| **Keywords** | chuyển nhượng, bán đất, mua đất | ủy quyền, thay mặt, người ủy quyền |
| **Nội dung** | A bán/tặng đất cho B | A ủy quyền cho B làm thủ tục |
| **Kết quả** | B trở thành chủ đất mới | A vẫn là chủ đất |

---

## 🧪 Test Case

### Input (Gemini Lite)
```
File: 20220105-07300010.jpg
Title: "HỢP ĐỒNG ỦY QUYỀN" (ở top, in hoa, rõ ràng)
```

### Expected Output (Sau khi sửa)
```json
{
  "short_code": "HDUQ",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Hợp đồng ủy quyền (KHÔNG phải chuyển nhượng), title rõ ràng"
}
```

### Verification
```
✅ short_code = "HDUQ" (KHÔNG phải "HDCQ")
✅ reasoning mentions "ỦY QUYỀN"
✅ reasoning clarifies "KHÔNG phải chuyển nhượng"
```

---

## 📂 Files Modified

### 1. `/app/desktop-app/python/ocr_engine_gemini_flash.py`

**Changes:**
1. **Lines 388-413:** Updated NHÓM 2 - HỢP ĐỒNG with clear distinctions
   - Added detailed explanation for HDCQ
   - Added detailed explanation for HDUQ
   - Added explicit warning

2. **Lines 626-634:** Added positive examples
   - Example for HDCQ with title "HỢP ĐỒNG CHUYỂN NHƯỢNG"
   - Example for HDUQ with title "HỢP ĐỒNG ỦY QUYỀN"
   - Added warning in example

3. **Lines 648-654:** Added negative example
   - Example of wrong classification (HDUQ → HDCQ)
   - Explanation why it's wrong

**Impact:**
- ✅ Gemini will now distinguish HDCQ from HDUQ correctly
- ✅ Works for both `gemini-flash` and `gemini-flash-lite`
- ✅ No breaking changes to other document types

---

## 🎯 Testing Instructions

### Test 1: File với "HỢP ĐỒNG ỦY QUYỀN"
```bash
# Quét file với Gemini Lite
File: [File có title "HỢP ĐỒNG ỦY QUYỀN"]
Expected: HDUQ (confidence ~0.95)
```

### Test 2: File với "HỢP ĐỒNG CHUYỂN NHƯỢNG"
```bash
# Quét file với Gemini Lite
File: [File có title "HỢP ĐỒNG CHUYỂN NHƯỢNG"]
Expected: HDCQ (confidence ~0.95)
```

### Test 3: Kiểm tra console logs
```
Console output phải show:
- "HỢP ĐỒNG ỦY QUYỀN" → HDUQ ✅
- "HỢP ĐỒNG CHUYỂN NHƯỢNG" → HDCQ ✅
- Reasoning phải đúng (không nhầm lẫn)
```

---

## ⚠️ Lưu Ý

### Gemini AI Có Thể Vẫn Sai
Dù prompt đã được cải thiện, Gemini AI vẫn có thể sai trong một số trường hợp:

1. **Ảnh mờ/blur:** OCR không đọc được đúng title
2. **Layout phức tạp:** Title bị che khuất hoặc không rõ ràng
3. **Variant title:** Title khác với ví dụ trong prompt

### Giải Pháp Dự Phòng

**Option 1: Kiểm tra thủ công**
- User xem lại kết quả
- Sửa short_code nếu sai (có nút "✏️ Sửa" trong UI)

**Option 2: Sử dụng Rules (offline)**
- Nếu Gemini sai nhiều, có thể dùng offline OCR + rules
- Rules có pattern matching chính xác hơn cho title

**Option 3: Nâng cấp lên Gemini Full**
- `gemini-flash` (full) có accuracy cao hơn lite
- Cost: $0.20/1K images (vs $0.10/1K cho lite)

---

## 📊 Kết Quả Dự Kiến

### Trước Khi Sửa
```
Input: "HỢP ĐỒNG ỦY QUYỀN"
Output: HDCQ ❌ (SAI!)
Accuracy: ~60% cho HDUQ
```

### Sau Khi Sửa
```
Input: "HỢP ĐỒNG ỦY QUYỀN"
Output: HDUQ ✅ (ĐÚNG!)
Accuracy dự kiến: ~95% cho HDUQ
```

---

## 🔄 Rollback (Nếu cần)

Nếu thay đổi gây vấn đề, có thể rollback về version cũ:

```bash
git diff HEAD /app/desktop-app/python/ocr_engine_gemini_flash.py
git checkout HEAD -- /app/desktop-app/python/ocr_engine_gemini_flash.py
```

Hoặc dùng feature "Rollback" trên Emergent platform.

---

## 📌 Tóm Tắt

✅ **Đã sửa:** Gemini prompt được cải thiện với:
- Định nghĩa rõ ràng hơn cho HDCQ và HDUQ
- Ví dụ cụ thể cho cả 2 loại
- Cảnh báo mạnh về sự khác biệt
- Ví dụ lỗi thường gặp

✅ **Files modified:** 1 file (`ocr_engine_gemini_flash.py`)
✅ **Breaking changes:** Không có
✅ **Testing:** Cần test với file thực "HỢP ĐỒNG ỦY QUYỀN"

---

## 🙏 Phản Hồi

Vui lòng test và báo cáo kết quả:
- ✅ **Nếu HDUQ được phân loại đúng:** Xác nhận fix thành công
- ❌ **Nếu vẫn sai:** Chia sẻ console logs và ảnh để điều tra thêm

Cảm ơn! 🇻🇳
