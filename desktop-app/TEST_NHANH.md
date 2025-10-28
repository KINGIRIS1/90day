# 🧪 TEST NHANH v1.1.0

## Đã cải tiến gì?
✅ Crop thông minh (50% ảnh dọc, 65% ảnh ngang)
✅ Timeout tăng 30s → 60s
✅ Classification logic cải thiện

## Cách test (Windows):

### Bước 1: Mở Command Prompt
Nhấn `Win + R` → Gõ `cmd` → Enter

### Bước 2: Vào thư mục desktop-app
```
cd C:\desktop-app
```
(Thay `C:\desktop-app` bằng đường dẫn thực tế)

### Bước 3: Chạy test
```
test-improvements.bat "C:\đường\dẫn\ảnh.jpg"
```

Ví dụ:
```
test-improvements.bat "C:\Users\nguye\Desktop\test.jpg"
```

## Xem kết quả:

### ✅ TỐT nếu:
- Thời gian < 60s
- Confidence >= 70%
- Nhận diện đúng loại tài liệu

### ⚠️ CẦN FIX nếu:
- Timeout > 60s
- Confidence < 60%
- Nhận diện sai

## Sau khi test:
📝 Báo kết quả cho em → Em build installer

---

**Câu hỏi? Lỗi? → Chụp màn hình gửi em!**
