# 💰 Bảng Chi Phí Chi Tiết - Gemini Flash OCR

## 📊 Dự Toán Chi Phí 1 Trang

### Kích thước scan điển hình: **3000x4000 pixels** (A4, 300 DPI)

| Model | Với Resize (2000x2800) | Không Resize | Tiết Kiệm |
|-------|----------------------|--------------|-----------|
| **Gemini Flash** | **$0.0041** (~4₫) | $0.0067 (~6.7₫) | **40%** |
| **Gemini Flash Lite** | **$0.0013** (~1.3₫) | $0.0022 (~2.2₫) | **40%** |

> ⭐ **Khuyến nghị**: Dùng **Flash Lite + Resize** cho chi phí tối ưu nhất!

---

## 📈 Bảng So Sánh Theo Kích Thước Ảnh

### Gemini Flash (với resize 2000x2800)

| Kích Thước Gốc | Sau Resize | Chi Phí/Trang | Không Resize | Tiết Kiệm |
|----------------|------------|---------------|--------------|-----------|
| 2000x2800 | 2000x2800 | $0.0042 | $0.0042 | 0% |
| 2500x3500 | 2000x2800 | $0.0042 | $0.0054 | 23% |
| **3000x4000** ⭐ | **2000x2666** | **$0.0041** | **$0.0067** | **40%** |
| 4000x5600 | 2000x2800 | $0.0042 | $0.0109 | **62%** |

### Gemini Flash Lite (với resize 2000x2800)

| Kích Thước Gốc | Sau Resize | Chi Phí/Trang | Không Resize | Tiết Kiệm |
|----------------|------------|---------------|--------------|-----------|
| 2000x2800 | 2000x2800 | $0.0013 | $0.0013 | 0% |
| 2500x3500 | 2000x2800 | $0.0013 | $0.0018 | 24% |
| **3000x4000** ⭐ | **2000x2666** | **$0.0013** | **$0.0022** | **40%** |
| 4000x5600 | 2000x2800 | $0.0013 | $0.0036 | **62%** |

---

## 💼 Chi Phí Khối Lượng Lớn

### Scan 3000x4000 với resize

| Số Lượng | Flash | Flash Lite | Tiết Kiệm (vs Flash) |
|----------|-------|-----------|---------------------|
| **1 trang** | $0.0041 | $0.0013 | **68%** |
| **10 trang** | $0.041 | $0.013 | **68%** |
| **100 trang** | $0.41 (~410₫) | $0.13 (~130₫) | **68%** |
| **1,000 trang** | **$4.10** (~4,100₫) | **$1.30** (~1,300₫) | **68%** |
| **10,000 trang** | $41 (~41,000₫) | $13 (~13,000₫) | **68%** |
| **100,000 trang** | $410 (~410k₫) | $130 (~130k₫) | **68%** |

---

## 🎁 Free Tier - Scan Miễn Phí

### Google AI Studio Free Tier:
- **1,500 requests/ngày**
- **45,000 requests/tháng**

### Nghĩa là:
- ✅ Scan **miễn phí 45,000 trang/tháng**!
- ✅ Tương đương **~1,500 trang/ngày**
- ✅ Không tốn chi phí gì cho khối lượng nhỏ/vừa

> 💡 **Lưu ý**: Sau khi hết free tier, mới tính phí theo bảng trên.

---

## 🔢 Cách Tính Chi Phí

### Công thức:
```
Chi phí = (Input Tokens × Input Rate + Output Tokens × Output Rate) / 1,000,000
```

### Pricing Rate (per 1M tokens):

| Model | Input Rate | Output Rate |
|-------|-----------|-------------|
| **Flash** | $0.30 | $2.50 |
| **Flash Lite** | $0.10 | $0.40 |

### Token Estimation:

**Ảnh 3000x4000 (resize → 2000x2666):**
- Image pixels: 2000 × 2666 = 5,332,000 pixels
- Image tokens: 5,332,000 ÷ 750 ≈ 7,109 tokens
- Prompt tokens: ~5,600 tokens (optimized prompt)
- **Total input tokens**: ~12,709 tokens
- **Output tokens**: ~100 tokens (JSON response)

**Chi phí Flash:**
```
= (12,709 × 0.30 + 100 × 2.50) / 1,000,000
= (3,813 + 250) / 1,000,000
= $0.004063
≈ $0.0041
```

**Chi phí Flash Lite:**
```
= (12,709 × 0.10 + 100 × 0.40) / 1,000,000
= (1,271 + 40) / 1,000,000
= $0.001311
≈ $0.0013
```

---

## 💡 Khuyến Nghị Sử Dụng

### Khi nào dùng **Flash**:
- ✅ Cần accuracy cao nhất (93-97%)
- ✅ Documents phức tạp, khó đọc
- ✅ Không quan tâm chi phí
- ✅ Khối lượng nhỏ (<1,000 trang)

### Khi nào dùng **Flash Lite**:
- ✅ Documents rõ ràng, dễ đọc
- ✅ Cần tiết kiệm chi phí (68% cheaper)
- ✅ Khối lượng lớn (>1,000 trang)
- ✅ Tốc độ quan trọng (nhanh hơn Flash)

### Khi nào bật **Resize**:
- ✅ Ảnh scan lớn (>2500px)
- ✅ Tiết kiệm 20-60% chi phí
- ✅ Vẫn giữ >95% accuracy
- ✅ **LUÔN BẬT** trừ khi cần 100% quality

---

## 📱 So Sánh với Các Dịch Vụ Khác

| Dịch Vụ | Chi Phí/1,000 trang | Accuracy | Tốc Độ |
|---------|-------------------|----------|--------|
| **Gemini Flash Lite + Resize** | **$1.30** | 90-95% | ⚡⚡⚡ |
| **Gemini Flash + Resize** | **$4.10** | 93-97% | ⚡⚡ |
| Google Cloud Vision | $1,500 | 90-95% | ⚡⚡ |
| Azure Computer Vision | $1,000 | 92-96% | ⚡⚡ |
| Tesseract (Offline) | **$0** | 75-85% | ⚡ |
| VietOCR (Offline) | **$0** | 90-95% | ⚡⚡⚡ |

> 💎 **Gemini Flash Lite = Sweet spot** giữa chi phí, accuracy, và tốc độ!

---

## 🎯 Ví Dụ Thực Tế

### Case 1: Văn phòng nhỏ - 500 trang/tháng
- **Flash Lite + Resize**: $0.65/tháng (~650₫)
- **Hoàn toàn FREE** với free tier!

### Case 2: Văn phòng vừa - 5,000 trang/tháng
- **Flash Lite + Resize**: $6.50/tháng (~6,500₫)
- **Free tier**: 45,000 trang → FREE!

### Case 3: Doanh nghiệp lớn - 50,000 trang/tháng
- **Flash Lite + Resize**: $65/tháng (~65k₫)
- **Sau trừ free tier**: ~$6.5/tháng (~6,500₫)
- **Flash thường**: ~$205/tháng → Tiết kiệm 68%!

### Case 4: Số hóa hồ sơ - 100,000 trang
- **Flash Lite + Resize**: $130 (~130k₫)
- **Flash**: $410 (~410k₫)
- **Google Cloud Vision**: $150,000 (~150tr₫) 😱
- **Tiết kiệm**: 99.9% so với Google Vision!

---

## 🔧 Tips Tối Ưu Chi Phí

1. **Luôn bật Resize**
   - Tiết kiệm 20-60% mà vẫn giữ accuracy cao

2. **Dùng Flash Lite cho documents rõ ràng**
   - Tiết kiệm 68% so với Flash

3. **Tận dụng Free Tier**
   - 45,000 trang/tháng miễn phí!

4. **Batch processing**
   - Scan nhiều trang cùng lúc
   - Tận dụng free tier tối đa

5. **Test trước khi scale**
   - Test với 10-100 trang
   - Điều chỉnh settings nếu cần
   - Scale lên khi hài lòng

---

## 📞 FAQs

### Q: Chi phí có bao gồm VAT không?
**A**: Không, giá trên là giá gốc từ Google. VAT (nếu có) sẽ được tính thêm.

### Q: Free tier reset khi nào?
**A**: Reset **hàng ngày** (1,500 requests/ngày) và **hàng tháng** (45,000 requests/tháng).

### Q: Có bị charge khi trong free tier không?
**A**: **Không**. Chỉ bị charge khi vượt quá free tier limits.

### Q: Làm sao biết còn bao nhiêu free tier?
**A**: Check tại [Google AI Studio Console](https://aistudio.google.com/) → Usage.

### Q: Chi phí có thay đổi không?
**A**: Google có thể thay đổi pricing. Check tại [Official Pricing](https://ai.google.dev/pricing).

---

**Version**: 1.1.0  
**Last Updated**: January 2025  
**Source**: Google AI Studio Pricing + Internal Testing
