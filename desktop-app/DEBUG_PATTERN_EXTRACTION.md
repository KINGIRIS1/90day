# 🔧 Debug Guide: Pattern Title Extraction

## Cách kiểm tra

Khi chạy desktop app, xem log trong console để kiểm tra:

### 1. Full Text từ EasyOCR
```
📝 Full text (first 500 chars): CỘNG HÒA ... ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ...
```

**Kiểm tra:** Có chứa title cần tìm không?

### 2. Pattern Match Result
```
✅ Extracted title via pattern: ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI...
```

**Hoặc:**
```
⚠️ No title pattern found in full text
```

### 3. Final Classification
```
Result: DDKBD
Confidence: 95%
```

---

## Các trường hợp có thể xảy ra

### Case 1: Pattern tìm thấy ✅
```
📝 Full text: ... ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ...
✅ Extracted title via pattern: ĐƠN ĐĂNG KÝ BIẾN ĐỘNG...
Result: DDKBD (95%)
```
→ **Hoạt động tốt!**

### Case 2: Pattern không tìm thấy ❌
```
📝 Full text: CỘNG HÒA ... PHẦN GHI ...
⚠️ No title pattern found in full text
⚠️ Title has low uppercase (30%)
Result: UNKNOWN hoặc fallback
```
→ **Vấn đề:** EasyOCR không đọc được title chính

### Case 3: Full text không chứa title ❌
```
📝 Full text: (không có "ĐƠN ĐĂNG KÝ")
⚠️ No title pattern found
```
→ **Nguyên nhân:** Crop 40% vẫn chưa đủ hoặc EasyOCR bỏ qua

---

## Giải pháp khi Pattern không tìm thấy

### Option 1: Tăng crop lên 50%
```python
# ocr_engine_easyocr.py
crop_height = int(height * 0.50)  # 50%
```

### Option 2: Thêm pattern mới
Nếu title có format khác, thêm vào `title_patterns`:

```python
# process_document.py - extract_document_title_from_text()
title_patterns = [
    # ... existing patterns
    r'(YOUR_NEW_PATTERN[^.]{0,100})',  # Add here
]
```

### Option 3: Dùng toàn bộ ảnh (no crop)
```python
# Test với full image
crop_height = height  # 100%
```

**Trade-off:** Chậm hơn nhưng chính xác hơn

---

## Debug Steps

### Bước 1: Kiểm tra Full Text
Trong log, tìm dòng:
```
📝 Full text (first 500 chars): ...
```

Copy text ra và kiểm tra thủ công:
- Có chứa "ĐƠN ĐĂNG KÝ" không?
- Có chứa "HỢP ĐỒNG" không?
- Có chứa title nào khác không?

### Bước 2: Test Pattern Manually
```python
import re

text = "YOUR_FULL_TEXT_HERE"
pattern = r'(Đ[OƠ]N\s+[ĐD][AĂ]NG\s+K[YÝ]\s+BI[EẾ]N\s+[ĐD][OỘ]NG[^.]{0,100})'
match = re.search(pattern, text, re.IGNORECASE)

if match:
    print(f"Found: {match.group(1)}")
else:
    print("Not found")
```

### Bước 3: Kiểm tra OCR Quality
Nếu full text không chứa title:
1. Mở ảnh trong image viewer
2. Crop thủ công top 40%
3. Check xem title có nằm trong vùng crop không?
4. Nếu không → Tăng crop %

---

## Pattern Format

### Current Patterns (Flexible với typos):

```python
# ĐƠN ĐĂNG KÝ BIẾN ĐỘNG
r'(Đ[OƠ]N\s+[ĐD][AĂ]NG\s+K[YÝ]\s+BI[EẾ]N\s+[ĐD][OỘ]NG[^.]{0,100})'

# Matches:
✅ ĐƠN ĐĂNG KÝ BIẾN ĐỘNG
✅ ĐON DĂNG KÝ BIẾN DỘNG (typos)
✅ Đơn đăng ký biến động (mixed case)
❌ DON DANG KY (no Vietnamese chars)
```

### Cách thêm pattern mới:

1. Xác định title cần detect
2. Viết regex với character variants:
   - `[OƠ]` = O hoặc Ơ
   - `[ĐD]` = Đ hoặc D
   - `[AĂ]` = A hoặc Ă
3. Thêm vào list `title_patterns`

---

## Performance Notes

### Crop Percentage vs Speed:

| Crop | Speed | Coverage |
|------|-------|----------|
| 25% | ~7s | Title at 0-12% |
| 35% | ~8s | Title at 0-17% |
| 40% | ~9s | Title at 0-20% ← Current |
| 50% | ~11s | Title at 0-25% |
| 100% | ~20s | Full page |

**Recommendation:** 40% là sweet spot cho most cases

---

## Kết luận

**Khi nào cần debug:**
- Log không show "✅ Extracted title via pattern"
- Classification sai hoặc UNKNOWN
- Confidence thấp bất thường

**Các bước debug:**
1. Check full text trong log
2. Verify title có trong full text không
3. Test pattern manually
4. Nếu cần: Tăng crop % hoặc thêm pattern

**Expected behavior:**
```
📝 Full text: ... [có chứa title] ...
✅ Extracted title via pattern: [title text]
Result: [correct doc type] (95%+)
```
