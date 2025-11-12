# 🔒 Backend Validation Fix - Chỉ Cho Phép 98 Mã Hợp Lệ

## Vấn Đề

**Trước khi fix:**
- Backend (Python OCR engine) có thể trả về **BẤT KỲ mã nào** từ Gemini AI
- Gemini đôi khi trả về mã sai, không có trong 98 mã đã định nghĩa
- Ví dụ: "GCN" thay vì "GCNC"/"GCNM", hoặc các mã tùy ý khác
- → Gây lỗi, không thống nhất, khó quản lý

## Giải Pháp

### 1. Thêm Danh Sách Mã Hợp Lệ (VALID_DOCUMENT_CODES)

**File**: `/app/desktop-app/python/ocr_engine_gemini_flash.py`

```python
# Valid document codes - MUST match rule_classifier.py
# Total: 98 valid codes (95 from classifier + GCNC + GCNM + hoadon)
VALID_DOCUMENT_CODES = {
    'BBBDG', 'BBGD', 'BBHDDK', ... (98 mã)
}
```

### 2. Validation trong `parse_gemini_response()`

**Logic mới:**
```python
# After sanitization
short_code_upper = short_code.upper()
if short_code_upper not in VALID_DOCUMENT_CODES:
    print(f"❌ INVALID CODE: '{short_code}' không nằm trong 98 mã hợp lệ → UNKNOWN")
    short_code = 'UNKNOWN'
else:
    # Normalize to uppercase
    short_code = short_code_upper
    print(f"✅ Valid code: '{short_code}'")
```

**Áp dụng ở 2 nơi:**
1. JSON parsing (main path)
2. Text fallback parsing (backup path)

### 3. Behavior Changes

**Trước:**
```
Gemini trả về: "GCN" → Backend accept → Frontend nhận "GCN"
Gemini trả về: "ABC123" → Backend accept → Frontend nhận "ABC123"
```

**Bây giờ:**
```
Gemini trả về: "GCN" → Backend validate → Không hợp lệ → "UNKNOWN"
Gemini trả về: "GCNC" → Backend validate → Hợp lệ → "GCNC" ✅
Gemini trả về: "ABC123" → Backend validate → Không hợp lệ → "UNKNOWN"
```

## Console Logging

**Khi gặp mã không hợp lệ:**
```
❌ INVALID CODE: 'GCN' không nằm trong 98 mã hợp lệ → UNKNOWN
   Gemini trả về mã sai. Chỉ chấp nhận mã trong danh sách VALID_DOCUMENT_CODES
```

**Khi mã hợp lệ:**
```
✅ Valid code: 'GCNC'
```

## Impact Analysis

### Trường Hợp Bị Ảnh Hưởng:

**1. Mã "GCN" (không có C/M)**
- **Trước**: Gemini trả về "GCN" → accept
- **Bây giờ**: "GCN" không hợp lệ → "UNKNOWN"
- **Lý do**: Phải là "GCNC" (cũ) hoặc "GCNM" (mới)
- **Giải pháp**: Prompt đã được thiết kế để Gemini phân biệt GCNC/GCNM dựa vào màu sắc

**2. Typo hoặc Mã Tùy Ý**
- **Trước**: "GCNN", "GCN1", "XYZ" → accept
- **Bây giờ**: Tất cả → "UNKNOWN"
- **Impact**: ✅ Positive - loại bỏ dữ liệu sai

**3. Mã Không Được Định Nghĩa**
- Nếu sau này cần thêm mã mới:
  1. Thêm vào `rule_classifier.py`
  2. Thêm vào `VALID_DOCUMENT_CODES` trong `ocr_engine_gemini_flash.py`
  3. Thêm vào `documentCodes.js` (frontend)

## Testing Checklist

### Backend:
```bash
# Test với file có GCN
python ocr_engine_gemini_flash.py test_gcn.jpg

# Kiểm tra log:
# ✅ Should see: "Valid code: 'GCNC'" hoặc "Valid code: 'GCNM'"
# ❌ Should NOT see: "Valid code: 'GCN'"
```

### Integration:
1. Quét tài liệu GCN → Kết quả phải là GCNC hoặc GCNM (không phải GCN)
2. Kiểm tra console log → Phải thấy validation messages
3. Nếu thấy "UNKNOWN" nhiều → Check Gemini prompt có đúng không

## Danh Sách 98 Mã Hợp Lệ

### Nhóm Giấy Chứng Nhận (GCN):
- **GCNC**: Giấy chứng nhận cũ (màu đỏ/nâu)
- **GCNM**: Giấy chứng nhận mới (màu hồng)

### Nhóm Giấy Tờ Cá Nhân:
- CCCD, GKH, GKS, GUQ

### Nhóm Phiếu:
- PCT, PKTHS, PLYKDC, PXNKQDD, PCTSVC

### Nhóm Quyết Định (14 mã):
- QDCMD, QDCHTGD, QDDCGD, QDDCQH, QDDCTH, QDGH, QDGTD, QDHG, QDHTSD, QDPDBT, QDPDDG, QDTH, QDTHA, QDTT, QDXP

### Nhóm Hợp Đồng (6 mã):
- HDBDG, HDCQ, HDTCO, HDTD, HDTHC, HDUQ

### Nhóm Biên Bản (7 mã):
- BBBDG, BBGD, BBHDDK, BBKTDC, BBKTHT, BBKTSS, BBNT

### Nhóm Đơn Xin (10+ mã):
- DDK, DDKBD, DXCD, DXCMD, DXGD, DXN, DXNTH, DXTHT, DCK, ...

### Nhóm Khác:
- HSKT, BMT, BVHC, BVN, GTLQ, GPXD, UNKNOWN, hoadon, ...

**Total: 98 mã**

## Notes

### Về "UNKNOWN":
- "UNKNOWN" là mã hợp lệ (trong danh sách)
- Dùng khi:
  1. Gemini không phân loại được
  2. Gemini trả về mã không hợp lệ
  3. OCR thất bại

### Về Case Sensitivity:
- Tất cả mã được normalize về uppercase
- Ngoại lệ: "hoadon" (lowercase theo classifier)

### Synchronization:
3 files phải đồng bộ:
1. `/app/desktop-app/python/rule_classifier.py` (source of truth)
2. `/app/desktop-app/python/ocr_engine_gemini_flash.py` (backend validation)
3. `/app/desktop-app/src/constants/documentCodes.js` (frontend validation)

---

**Cập nhật**: 12/01/2025  
**Version**: 1.3.0  
**Tác giả**: AI Developer
