# ✅ CẢI TIẾN: Sequential Naming Logic

## 🎯 Vấn đề

Khi scan nhiều trang liên tiếp, các trang không có tiêu đề rõ ràng bị phân loại thành **UNKNOWN**.

**Ví dụ từ screenshot:**
- File 1: DDKBD ✓
- File 2: UNKNOWN ❌ (nên là DDKBD - trang 2)
- File 3: HDCQ ✓
- File 4: UNKNOWN ❌ (nên là HDCQ - trang 2)
- File 5: UNKNOWN ❌ (nên là HDCQ - trang 3)

---

## ✅ Giải pháp đã implement

### Logic Sequential Naming:
Tự động gán short code của file trước đó cho file UNKNOWN hoặc confidence thấp.

### Điều kiện áp dụng:
File sẽ được gán short code của file trước nếu:
1. **`short_code === 'UNKNOWN'`** (không nhận dạng được)
2. **`confidence < 0.7`** (độ tin cậy thấp, có thể là trang không có title)
3. **`!title_text`** (không có title text)
4. **`title_text.length < 10`** (title quá ngắn)

### Kết quả:
```javascript
{
  doc_type: "Đơn đăng ký biến động...",
  short_code: "DDKBD",  // Copy từ file trước
  confidence: 0.65,  // Confidence hợp lý
  original_confidence: 0.0,  // Lưu lại confidence gốc
  original_short_code: "UNKNOWN",  // Lưu lại short code gốc
  applied_sequential_logic: true,  // Flag đánh dấu
  note: "📄 Trang tiếp theo của DDKBD (không nhận dạng được)"
}
```

---

## 🔄 Logic hoạt động

### Ví dụ scan 5 files:

```
File 1: DDKBD (confidence 0.95) ✓
  → currentLastKnown = { short_code: "DDKBD", confidence: 0.95 }

File 2: UNKNOWN (confidence 0.0)
  → Áp dụng sequential naming
  → Kết quả: DDKBD (trang 2)
  → currentLastKnown không thay đổi (vẫn DDKBD)

File 3: HDCQ (confidence 0.92) ✓
  → currentLastKnown = { short_code: "HDCQ", confidence: 0.92 }

File 4: UNKNOWN (confidence 0.0)
  → Áp dụng sequential naming
  → Kết quả: HDCQ (trang 2)
  → currentLastKnown không thay đổi (vẫn HDCQ)

File 5: UNKNOWN (confidence 0.0)
  → Áp dụng sequential naming
  → Kết quả: HDCQ (trang 3)
  → currentLastKnown không thay đổi (vẫn HDCQ)
```

---

## 📝 Code Changes

### `/app/desktop-app/src/components/DesktopScanner.js`:

**Cải tiến 1: Tăng confidence threshold**
- Trước: `confidence < 0.5`
- Sau: `confidence < 0.7`
- **Lý do**: Cloud boost có thể trả về confidence 0.5-0.6 cho trang không có title

**Cải tiến 2: Kiểm tra title_text chặt chẽ hơn**
- Thêm check: `!result.title_text` (không có title)
- Thêm check: `title_text.trim().length < 10` (title quá ngắn)

**Cải tiến 3: Lưu thêm metadata**
- `original_confidence`: Confidence gốc
- `original_short_code`: Short code gốc (UNKNOWN)
- `note`: Mô tả rõ ràng cho user

---

## 🧪 Testing

### Test Case 1: Scan multi-page document
```
Input:
  - File 1: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG" (có title rõ ràng)
  - File 2: (trang 2, không có title)
  - File 3: (trang 3, không có title)

Expected Output:
  - File 1: DDKBD ✓
  - File 2: DDKBD (trang tiếp theo) ✓
  - File 3: DDKBD (trang tiếp theo) ✓
```

### Test Case 2: Mixed documents
```
Input:
  - File 1: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG" (DDKBD)
  - File 2: (trang 2, không có title)
  - File 3: "HỢP ĐỒNG CHUYỂN NHƯỢNG" (HDCQ)
  - File 4: (trang 2, không có title)

Expected Output:
  - File 1: DDKBD ✓
  - File 2: DDKBD (trang tiếp theo) ✓
  - File 3: HDCQ ✓
  - File 4: HDCQ (trang tiếp theo) ✓
```

---

## 💡 Notes

### Khi nào logic này KHÔNG áp dụng?
1. File đầu tiên trong batch (không có file trước đó)
2. File có classification rõ ràng (confidence >= 0.7 && short_code !== UNKNOWN)
3. File có title đầy đủ (>= 10 ký tự)

### UI Display:
- File sequential sẽ hiển thị note: "📄 Trang tiếp theo của XXX"
- Có thể xem `original_short_code` và `original_confidence` trong details

### Tương thích:
- ✅ Hoạt động cho cả **Cloud Boost** và **Offline OCR**
- ✅ Hoạt động cho cả **File Scan** và **Folder Scan** (ĐÃ FIX)
- ✅ Tương thích với **Stop/Resume** functionality

### 📝 Update Log:
**2025-01-28:** Fixed Folder Scan - Đã áp dụng sequential naming cho cả Folder Scan. Giờ cả File Scan và Folder Scan đều kế thừa short code từ file trước khi gặp UNKNOWN.

---

## ✅ Summary

- ✅ Logic sequential naming đã được cải tiến
- ✅ Tăng confidence threshold: 0.5 → 0.7
- ✅ Kiểm tra title_text chặt chẽ hơn
- ✅ Lưu metadata đầy đủ (original_confidence, original_short_code)
- ✅ Note rõ ràng cho user
- ✅ Tương thích với cả Cloud và Offline

**Kết quả**: Files UNKNOWN trong batch sẽ tự động kế thừa short code của file trước đó.
