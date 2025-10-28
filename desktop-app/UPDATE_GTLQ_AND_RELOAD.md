# Cập nhật GTLQ Keywords & Rules Reload Mechanism

## 📋 Tổng quan

Đã thực hiện 2 nhiệm vụ chính:

1. ✅ **Bổ sung keywords cho GTLQ**: Thêm "Giấy tiếp nhận hồ sơ và trả kết quả" (variant name)
2. ✅ **Fix Rules Reload**: User thay đổi rules trong UI → có hiệu lực NGAY LẬP TỨC (không cần restart app)

---

## 1. Keywords GTLQ (Giấy tiếp nhận hồ sơ và hẹn trả kết quả)

### ✅ Đã thêm vào GTLQ:
- "giấy tiếp nhận hồ sơ và trả kết quả" (có dấu)
- "giay tiep nhan ho so va tra ket qua" (không dấu)
- "GIẤY TIẾP NHẬN HỒ SƠ VÀ TRẢ KẾT QUẢ" (viết hoa)
- "giấy tiếp nhận hồ sơ và hẹn trả kết quả" (variant)

### 📝 Lưu ý về "Biên nhận hồ sơ" (BNHS):
- "Biên nhận hồ sơ" là loại giấy tờ **RIÊNG BIỆT** (short code: BNHS)
- Không gộp vào GTLQ để tránh nhầm lẫn
- Cloud backend cũng phân biệt: GTLQ ≠ BNHS

### 🔍 So sánh:
| Loại giấy | Short Code | Keywords chính |
|-----------|------------|----------------|
| Giấy tiếp nhận hồ sơ và hẹn trả kết quả | **GTLQ** | "giấy tiếp nhận hồ sơ", "hẹn trả kết quả", "trung tâm hành chính công" |
| Biên nhận hồ sơ | **BNHS** | "biên nhận hồ sơ", "biên nhận", "phiếu biên nhận" |

---

## 2. Rules Reload Mechanism

### ❌ VẤN ĐỀ TRƯỚC ĐÂY:
- User thêm/sửa/xóa rules trong UI → lưu vào `rules_overrides.json`
- Nhưng khi scan file → Python vẫn dùng rules CŨ (hardcoded trong `rule_classifier.py`)
- **Phải restart app mới có hiệu lực**

### ✅ GIẢI PHÁP:
1. Thêm function `get_active_rules()` trong `rule_classifier.py`:
   - Đọc `rules_overrides.json` (user changes)
   - Merge với DEFAULT_RULES
   - Return merged rules

2. Sửa `classify_by_rules()` để dùng `get_active_rules()` thay vì hardcoded `DOCUMENT_RULES`

### 🎯 KẾT QUẢ:
- ✅ Mỗi lần scan → load rules mới nhất (merged defaults + overrides)
- ✅ User thêm/sửa/xóa rules → **có hiệu lực NGAY LẬP TỨC**
- ✅ KHÔNG cần restart app

---

## 3. Cách thử nghiệm

### Test script:
```bash
cd /app/desktop-app
python3 test-rules-reload.py
```

### Test thủ công:
1. Mở app → Settings → Rules Manager
2. Chỉnh sửa 1 rule (ví dụ: thêm keyword cho GTLQ)
3. Lưu rule
4. Quay lại scan file → thấy rule mới có hiệu lực ngay
5. **KHÔNG** cần restart app

---

## 4. Files đã sửa

### `/app/desktop-app/python/rule_classifier.py`:
- ✅ Thêm imports: `os`, `json`, `Path`
- ✅ Thêm function `get_active_rules()`: Load rules từ overrides file
- ✅ Sửa `classify_by_rules()`: Dùng `active_rules = get_active_rules()` thay vì `DOCUMENT_RULES`
- ✅ Bổ sung keywords cho GTLQ: "Giấy tiếp nhận hồ sơ và trả kết quả"
- ✅ Thêm TITLE_TEMPLATES cho GTLQ variants

### `/app/backend/server.py`:
- ✅ Đã đổi short code cho "Giấy tiếp nhận hồ sơ và hẹn trả kết quả" từ "BN" → "GTLQ" (done trước đây)
- ✅ "Biên nhận hồ sơ" → "BNHS" (giữ nguyên, đúng rồi)

---

## 5. Thông báo cho User

### ⚠️ CẦN XÁC NHẬN:

Hiện tại em đã implement theo logic:
- **GTLQ** = "Giấy tiếp nhận hồ sơ và hẹn trả kết quả" (và các variants)
- **BNHS** = "Biên nhận hồ sơ" (riêng biệt)

❓ **Câu hỏi cho anh**:
1. Có cần gộp BNHS vào GTLQ không? (hay giữ riêng như hiện tại?)
2. Nếu gộp → tất cả "Biên nhận hồ sơ" sẽ được rename thành GTLQ
3. Nếu KHÔNG gộp → giữ nguyên logic hiện tại (GTLQ ≠ BNHS)

### ✅ THÔNG BÁO:
**Rules reload đã hoạt động!** 
- User thay đổi rules trong UI → áp dụng ngay lập tức
- KHÔNG cần restart app
- Có thể test bằng cách:
  1. Mở Rules Manager
  2. Sửa 1 rule
  3. Lưu
  4. Scan file → thấy rule mới có hiệu lực

---

## 6. Next Steps

### Nếu anh muốn merge BNHS vào GTLQ:
1. Xóa định nghĩa BNHS trong `rule_classifier.py`
2. Thêm tất cả keywords của BNHS vào GTLQ
3. Update `code_to_name` mapping

### Nếu giữ nguyên (GTLQ ≠ BNHS):
1. ✅ Đã hoàn thành
2. Test thử với ảnh thật
3. Verify classification accuracy

---

## 📝 Summary

**ĐÃ HOÀN THÀNH:**
1. ✅ Thêm "Giấy tiếp nhận hồ sơ và trả kết quả" vào GTLQ keywords
2. ✅ Fix rules reload → user changes có hiệu lực ngay lập tức
3. ✅ Giữ BNHS và GTLQ riêng biệt (theo cloud backend)

**CẦN XÁC NHẬN:**
- Có gộp BNHS vào GTLQ không?

**TESTING:**
- ✅ Keywords đã được thêm
- ✅ Rules reload mechanism hoạt động
- ⏳ Chờ test với ảnh thật để verify classification accuracy
