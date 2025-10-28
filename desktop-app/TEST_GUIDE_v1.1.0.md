# 🧪 HƯỚNG DẪN TEST v1.1.0 IMPROVEMENTS

## 📋 Những gì đã cải tiến trong v1.1.0:

### ✅ 1. Smart Crop (giống Cloud Backend)
- **Trước:** Crop cứng 40% phần trên
- **Sau:** Tự động phát hiện:
  - Ảnh dọc (1 trang) → Crop 50%
  - Ảnh ngang (2 trang) → Crop 65%

### ✅ 2. Timeout tăng lên
- **Trước:** 30 giây → Dễ bị timeout với EasyOCR
- **Sau:** 60 giây → Xử lý tốt hơn cho ảnh phức tạp

### ✅ 3. Classification Logic
- Fuzzy matching 75% (giống Cloud)
- 150+ document types
- GTLQ specific keywords

---

## 🚀 CÁCH TEST (Windows):

### Phương pháp 1: Dùng batch file (Đơn giản nhất)

1. Mở **Command Prompt** hoặc **PowerShell**
2. Di chuyển đến thư mục desktop-app:
   ```
   cd C:\path\to\desktop-app
   ```

3. Chạy test với ảnh của bạn:
   ```
   test-improvements.bat "C:\Users\nguye\OneDrive\Máy tính\AI\5-3442 CN TRUONG QUANG LAM\20250318-03400005.jpg"
   ```

4. Xem kết quả trên màn hình

### Phương pháp 2: Dùng Python trực tiếp

```bash
python test-improvements.py "path\to\your\image.jpg"
```

---

## 📊 CÁCH ĐỌC KẾT QUẢ:

Script sẽ hiển thị:

### ✅ STEP 1: Smart Crop Analysis
- Kích thước ảnh
- Aspect ratio
- Loại crop được chọn (50% hay 65%)

### ✅ STEP 2: OCR + Classification
- Thời gian xử lý (phải < 60s)
- Có timeout không?

### ✅ STEP 3: Results Analysis
- Document Type (loại tài liệu)
- Short Code (mã ngắn)
- Confidence (độ tin cậy)
- Accuracy Estimate (ước tính độ chính xác)

### ✅ STEP 4: Title Extraction
- Có trích xuất được tiêu đề không?
- Phương pháp: Regex Pattern hay OCR Title Area?

### ✅ STEP 5: Full Text Preview
- Độ dài text
- Preview 300 ký tự đầu

### ✅ STEP 6: Recommendations
- High/Medium/Low confidence
- Có nên dùng Cloud Boost không?

---

## 🎯 KẾT QUẢ MONG ĐỢI:

### ✅ Thành công:
- ⏱️ Processing time: < 30s (FAST) hoặc < 60s (OK)
- 📊 Confidence: >= 80% (HIGH)
- ✅ Title extracted successfully
- 📄 Document Type: Đúng loại

### ⚠️ Cần cải thiện:
- ⏱️ Processing time: 30-60s (SLOW but OK)
- 📊 Confidence: 60-80% (MEDIUM)
- ⚠️ Title extraction failed (nhưng vẫn classify được)

### ❌ Vẫn có vấn đề:
- ⏱️ Processing time: > 60s (TIMEOUT)
- 📊 Confidence: < 60% (LOW)
- ❌ No title, wrong classification

---

## 📝 SAU KHI TEST:

### Nếu kết quả TỐT:
✅ Anh/chị báo em → Em sẽ **build installer v1.1.0** ngay

### Nếu vẫn có vấn đề:
❌ Anh/chị gửi em:
1. Screenshot kết quả test
2. File ảnh bị lỗi (nếu được)
3. Mô tả vấn đề cụ thể

→ Em sẽ debug và fix thêm trước khi build

---

## 💡 GỢI Ý:

Test với **nhiều loại ảnh khác nhau**:
- ✅ Ảnh dọc (GCN, hợp đồng)
- ✅ Ảnh ngang (GCN 2 trang)
- ✅ Ảnh mờ/xiêng
- ✅ Ảnh có nhiều text

Để đảm bảo cải tiến hoạt động tốt cho mọi trường hợp!

---

## ❓ CÓ VẤN ĐỀ?

Nếu gặp lỗi:
1. Kiểm tra Python đã cài đặt chưa: `python --version`
2. Kiểm tra dependencies: `pip list | grep -E "easyocr|opencv|pillow"`
3. Báo em kèm error message

---

**Chúc anh/chị test tốt! 🎉**
