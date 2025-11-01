# 🖼️ Tính năng Smart Image Resize - Tối ưu chi phí Gemini

## 📖 Tổng quan

Tính năng Smart Image Resize tự động giảm kích thước ảnh trước khi gửi lên Gemini API, giúp tiết kiệm 50-70% chi phí mà vẫn duy trì độ chính xác OCR cao.

## ✨ Tính năng chính

- **Smart Resize**: Chỉ resize ảnh nếu vượt quá kích thước tối đa
- **Giữ tỷ lệ khung hình**: Không làm biến dạng ảnh
- **Chất lượng cao**: Sử dụng LANCZOS resampling + JPEG quality 85%
- **Tùy chỉnh linh hoạt**: Điều chỉnh kích thước tối đa trong Settings
- **Hiển thị thống kê**: Xem được tỷ lệ giảm kích thước và tiết kiệm chi phí

## 🎯 Cách sử dụng

### 1. Bật tính năng trong Settings

1. Mở **Cloud Settings** (⚙️ trong menu)
2. Chọn **Gemini Flash** hoặc **Gemini Flash Lite**
3. Tìm phần **"💰 Tối ưu hóa chi phí Gemini"**
4. Tích vào ✅ **"Tự động resize ảnh trước khi gửi lên Gemini API"**

### 2. Điều chỉnh kích thước (tùy chọn)

- **Chiều rộng tối đa**: Mặc định 2000px (khuyến nghị: 1500-2500px)
- **Chiều cao tối đa**: Mặc định 2800px (khuyến nghị: 2000-3500px)

### 3. Lưu cài đặt

Nhấn **💾 Lưu cài đặt** để áp dụng.

## 📊 Ví dụ tiết kiệm

| Kích thước gốc | Sau resize | Tiết kiệm tokens | Tiết kiệm chi phí |
|----------------|------------|------------------|-------------------|
| 4000x5600px    | 2000x2800px| ~60-70%         | ~60-70%          |
| 3000x4200px    | 2000x2800px| ~40-50%         | ~40-50%          |
| 2500x3500px    | 2000x2800px| ~20-30%         | ~20-30%          |
| 1500x2000px    | Giữ nguyên | 0%              | 0%               |

## 💡 Khuyến nghị

### Khi nào NÊN bật resize:
- ✅ Documents scan chất lượng tốt, rõ ràng
- ✅ Ảnh chụp từ điện thoại (thường > 3000px)
- ✅ Scan từ máy quét chất lượng cao
- ✅ Muốn tối ưu chi phí API

### Khi nào NÊN TẮT resize:
- ❌ Documents mờ, nhòe, chất lượng kém
- ❌ Chữ viết tay nhỏ, khó đọc
- ❌ Ảnh đã có kích thước nhỏ (<2000px)
- ❌ Cần độ chính xác tối đa (>97%)

## 🔧 Cài đặt nâng cao

### Điều chỉnh theo loại documents:

**Documents chất lượng tốt:**
- Max: 1800x2500px
- Tiết kiệm tối đa, vẫn chính xác

**Documents chất lượng trung bình:**
- Max: 2000x2800px (mặc định)
- Cân bằng giữa chi phí và độ chính xác

**Documents chất lượng kém:**
- Max: 2500x3500px hoặc tắt resize
- Ưu tiên độ chính xác

## 📈 Hiển thị trong kết quả

Sau khi scan, bạn sẽ thấy:

```
Ước tính: $0.000234 (in 4500, out 120) 📉 -55.6%
```

- `$0.000234`: Chi phí ước tính
- `in 4500, out 120`: Input/output tokens
- `📉 -55.6%`: Giảm 55.6% kích thước ảnh (hover để xem chi tiết)

## ⚙️ Cấu hình kỹ thuật

### Thuật toán resize:
- **Resampling**: LANCZOS (chất lượng cao nhất)
- **Format**: JPEG với quality 85%
- **Mode conversion**: Auto convert RGBA → RGB

### Logic xử lý:
```python
if image_width <= max_width AND image_height <= max_height:
    # Giữ nguyên, không resize
else:
    # Resize giữ tỷ lệ, chọn ratio nhỏ hơn
    ratio = min(max_width/width, max_height/height)
    new_size = (width * ratio, height * ratio)
```

## 🐛 Xử lý sự cố

### Nếu độ chính xác giảm:
1. Tăng max dimensions lên 2500x3500
2. Hoặc tắt resize trong Settings
3. Test với vài ảnh mẫu để tìm ngưỡng tối ưu

### Nếu chi phí vẫn cao:
1. Kiểm tra kích thước ảnh gốc (có thể đã nhỏ)
2. Giảm max dimensions xuống 1800x2500
3. Xem xét dùng Flash Lite thay vì Flash

## 📝 Lưu ý

- Tính năng chỉ áp dụng cho Gemini Flash/Flash Lite
- Không ảnh hưởng đến các OCR engine khác
- Cài đặt được lưu cục bộ, mỗi máy có thể khác nhau
- Resize info được lưu trong kết quả scan để theo dõi

## 🎓 Giải thích kỹ thuật

### Tại sao JPEG quality 85%?
- 85% là sweet spot giữa size và quality
- Documents (text) không cần 100% quality như ảnh thường
- Gemini OCR vẫn đọc chính xác ở quality 85%

### Tại sao dùng LANCZOS?
- Thuật toán resampling chất lượng cao nhất
- Giữ được độ sắc nét của text
- Tránh artifacts và blur

### Tại sao resize về ~2000x2800?
- A4 aspect ratio: 1:1.4 → 2000x2800 phù hợp
- Gemini tính tokens dựa vào pixels
- 2000x2800 ≈ 5.6M pixels → đủ để OCR chính xác
- Ảnh gốc 4000x5600 ≈ 22.4M pixels → dư thừa

## 📞 Hỗ trợ

Nếu có vấn đề, vui lòng:
1. Kiểm tra logs trong Console (F12)
2. Test với resize tắt để so sánh
3. Báo cáo kèm ảnh mẫu và settings

---

**Version**: 1.1.0  
**Last Updated**: January 2025
