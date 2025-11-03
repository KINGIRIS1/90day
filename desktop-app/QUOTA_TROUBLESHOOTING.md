# 🚨 Xử Lý Lỗi Quota & Rate Limit - Gemini API

## ❌ Lỗi phổ biến

### 1. "⚠️ VƯỢT QUÁ GIỚI HẠN REQUEST!"

Có 2 loại:

#### A. Rate Limit (Requests Per Minute)
```
🔥 Rate Limit: Quá nhiều requests trong thời gian ngắn
```

**Nguyên nhân:**
- Scan quá nhanh (nhiều trang cùng lúc)
- Vượt quá ~60 requests/phút

**Giải pháp:**

1. **Đợi 1-2 phút** rồi thử lại
2. **Giảm tốc độ scan:**
   - Scan từng trang thay vì batch
   - Đợi 1-2 giây giữa mỗi lần scan
3. **Scan trong multiple sessions:**
   - Chia nhỏ batch (10-20 trang/lần)
   - Đợi giữa các batch

#### B. Quota Exhausted (Free Tier)
```
📊 Free Tier hết quota (1,500 requests/ngày)
```

**Nguyên nhân:**
- Đã dùng hết 1,500 requests/ngày

**Giải pháp:**

### 🔄 GIẢI PHÁP CHI TIẾT:

---

## 1️⃣ Đợi Reset Quota (MIỄN PHÍ)

**Free tier reset:**
- **Hàng ngày** vào **0:00 UTC** = **7:00 AM giờ Việt Nam**
- Lại có 1,500 requests mới

**Timeline:**
```
Hôm nay 8:00 AM  → Dùng hết 1,500 requests
Hôm nay 9:00 AM  → ❌ Hết quota, không scan được
Hôm nay 8:00 PM  → ❌ Vẫn hết quota
Mai 7:00 AM      → ✅ Reset, lại có 1,500 requests!
```

**Khi nào dùng:**
- ✅ Không urgent
- ✅ Có thể đợi đến sáng mai
- ✅ Muốn tiếp tục dùng miễn phí

---

## 2️⃣ Upgrade Paid Tier (CHỈ ~$1/1000 TRANG)

**Lợi ích:**
- ✅ **Không giới hạn** requests/ngày
- ✅ Chi phí **cực rẻ**: $0.89/1,000 trang (Flash Lite)
- ✅ Không phải đợi reset
- ✅ Rate limit cao hơn

**Chi phí thực tế:**
```
100 trang:      ~$0.089  (~89₫)
1,000 trang:    ~$0.89   (~890₫)
10,000 trang:   ~$8.90   (~8,900₫)
```

**Cách upgrade:**

1. Truy cập [Google AI Studio](https://aistudio.google.com/)
2. Đăng nhập với Gmail có API key
3. Click "Billing" → Enable billing
4. Thêm credit card (Google chỉ charge khi dùng)
5. Done! Không giới hạn nữa

**Lưu ý:**
- Không tự động charge, chỉ charge khi vượt free tier
- Google có $300 free credit cho new users!

---

## 3️⃣ Tạo API Key Mới (MIỄN PHÍ)

**Cách làm:**

1. Tạo **Gmail mới** (nếu chưa có Gmail backup)
2. Truy cập [Google AI Studio](https://aistudio.google.com/)
3. Đăng nhập với Gmail mới
4. Tạo API key mới:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - Copy key
5. Paste vào app Settings
6. ✅ Lại có **1,500 requests/ngày** mới!

**Lưu ý:**
- Mỗi Gmail = 1 free tier
- Có thể tạo nhiều Gmail = nhiều API keys
- Switch giữa các keys khi hết quota

---

## 4️⃣ Dùng OCR Offline (MIỄN PHÍ, KHÔNG GIỚI HẠN)

**Ưu điểm:**
- ✅ **100% miễn phí**
- ✅ **Không giới hạn** số lượng
- ✅ Không cần internet
- ✅ Không cần API key

**Nhược điểm:**
- ❌ Accuracy thấp hơn (75-95% vs 93-97%)
- ❌ Cần rules-based classification

**Cách chuyển:**

1. Vào **Settings → Cloud OCR**
2. Chọn OCR Engine:
   - **VietOCR** (khuyến nghị): 90-95% accuracy
   - **EasyOCR**: 88-92% accuracy
   - **Tesseract**: 75-85% accuracy
3. Click **Save**
4. ✅ Scan không giới hạn!

**Khi nào dùng:**
- Documents rõ ràng, chữ lớn
- Không cần accuracy tối đa
- Khối lượng lớn (>10,000 trang)
- Hết quota Gemini

---

## 5️⃣ Hybrid Strategy (SMART!)

**Chiến lược thông minh:**

```
┌─────────────────────────────────────┐
│ Documents rõ ràng, đơn giản (80%)   │
│ → Dùng VietOCR Offline (miễn phí)  │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ Documents phức tạp, khó đọc (20%)   │
│ → Dùng Gemini Flash (1,500/ngày)   │
└─────────────────────────────────────┘
```

**Lợi ích:**
- Tiết kiệm quota Gemini
- Chi phí = $0
- Accuracy vẫn cao (average ~92%)

**Cách làm:**
1. Scan batch đầu với VietOCR
2. Review results
3. Documents có confidence < 80% → Re-scan với Gemini
4. Documents có confidence > 80% → Giữ nguyên

---

## 📊 So Sánh Các Giải Pháp

| Giải pháp | Chi phí | Thời gian | Accuracy | Giới hạn |
|-----------|---------|-----------|----------|----------|
| **Đợi reset** | $0 | ~12-24h | 93-97% | 1,500/ngày |
| **Paid tier** | $0.89/1K | Ngay | 93-97% | Unlimited |
| **API key mới** | $0 | ~5 phút | 93-97% | 1,500/ngày |
| **VietOCR** | $0 | Ngay | 90-95% | Unlimited |
| **Hybrid** | $0 | Ngay | ~92% | Smart |

---

## 🎯 Khuyến Nghị Theo Use Case

### Case 1: Sinh viên / Cá nhân (< 1,500 trang/ngày)
→ **Dùng Free Tier**
- Đủ với 1,500 requests/ngày
- Nếu vượt → Đợi ngày mai
- Chi phí: $0

### Case 2: Văn phòng nhỏ (1,500-5,000 trang/ngày)
→ **Multiple API Keys**
- Gmail 1: 1,500 requests
- Gmail 2: 1,500 requests
- Gmail 3: 1,500 requests
- Total: 4,500 requests/ngày
- Chi phí: $0

### Case 3: Văn phòng vừa (5,000-10,000 trang/ngày)
→ **Hybrid Strategy**
- VietOCR: 80% documents (4,000 trang)
- Gemini: 20% complex (1,000 trang)
- Trong free tier, chi phí: $0

### Case 4: Doanh nghiệp (> 10,000 trang/ngày)
→ **Paid Tier**
- 10,000 trang/ngày × 30 = 300K/tháng
- Chi phí: ~$270/tháng (~6.7tr VNĐ)
- ROI: Vẫn rẻ hơn thuê người scan 100x

---

## 🛠️ Troubleshooting

### Lỗi: "429 RATE_LIMIT_EXCEEDED"
**Giải pháp:**
1. Đợi 60 giây
2. Retry
3. Giảm scan speed

### Lỗi: "403 API_KEY_INVALID"
**Giải pháp:**
1. Check API key trong Settings
2. Enable "Generative Language API"
3. Tạo key mới

### Lỗi: "RESOURCE_EXHAUSTED"
**Giải pháp:**
1. Hết quota → Đợi reset
2. Hoặc upgrade Paid
3. Hoặc dùng OCR offline

---

## 📱 Check Quota Usage

**Cách 1: Google AI Studio**
1. Truy cập [Google AI Studio](https://aistudio.google.com/)
2. Click "Usage" → Xem quota remaining

**Cách 2: Monitor trong App**
- App tự động track số requests
- Show warning khi gần hết quota

---

## 💡 Tips Tối Ưu

1. **Scan buổi sáng:**
   - Quota mới reset lúc 7AM
   - Còn full 1,500 requests

2. **Batch nhỏ:**
   - 10-20 trang/batch
   - Tránh rate limit

3. **Dùng Resize:**
   - Giảm tokens = giảm quota usage
   - Vẫn giữ accuracy

4. **Monitor usage:**
   - Check quota định kỳ
   - Plan trước khi scan lớn

5. **Backup plan:**
   - Luôn có OCR offline ready
   - Hoặc có API key backup

---

## 🆘 Support

**Nếu vẫn gặp vấn đề:**

1. Check [Google AI Studio Status](https://status.google.com/)
2. Verify API key permissions
3. Test với 1 trang trước
4. Check logs trong app console (F12)

**Contact:**
- Google AI Support: [Google Cloud Support](https://cloud.google.com/support)
- App Issues: Check app logs

---

**Version**: 1.1.0  
**Last Updated**: January 2025  
**Quota Limits**: 1,500 requests/day (Free Tier)
