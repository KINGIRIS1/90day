# 💳 Hướng Dẫn Đăng Ký Paid Tier - Gemini API

## 🎯 Tổng Quan:

**Lợi ích Tier 1 Paid:**
- ✅ **UNLIMITED requests/ngày** (Flash Lite)
- ✅ **4,000 RPM** (vs 15 RPM free)
- ✅ Chi phí: **~$0.89/1,000 trang**
- ✅ Không giới hạn scan

---

## 📋 YÊU CẦU:

1. ✅ Có tài khoản Google (Gmail)
2. ✅ Có thẻ tín dụng/thẻ ghi nợ (Visa/Mastercard)
3. ✅ Đã có API key từ AI Studio

---

## 🔧 BƯỚC 1: ENABLE CLOUD BILLING (10 phút)

### 1.1. Truy cập Google Cloud Console:
```
https://console.cloud.google.com/
```

### 1.2. Đăng nhập:
- Dùng Gmail có API key hiện tại
- Chấp nhận Terms of Service nếu lần đầu

### 1.3. Tạo/Chọn Project:

**Option A: Dùng project hiện có**
```
1. Click dropdown ở góc trên (project name)
2. Chọn project đang dùng API key
3. VD: "OCR Scanner" hoặc "My First Project"
```

**Option B: Tạo project mới**
```
1. Click "New Project"
2. Name: "OCR Scanner Paid"
3. Click "Create"
4. Đợi 10-20 giây
```

### 1.4. Enable Billing:

**Bước 1: Mở Billing**
```
1. Click menu ☰ (góc trái trên)
2. Chọn "Billing"
3. Click "Link a billing account"
```

**Bước 2: Tạo Billing Account**
```
1. Click "Create Billing Account"
2. Chọn country: Vietnam
3. Click "Continue"
```

**Bước 3: Nhập thông tin thẻ**
```
✅ Card number: Số thẻ (16 số)
✅ Expiration date: MM/YY
✅ CVC: 3 số sau thẻ
✅ Cardholder name: Tên trên thẻ
✅ Billing address: Địa chỉ
```

**Thẻ được chấp nhận:**
- ✅ Visa
- ✅ Mastercard
- ✅ American Express
- ✅ Thẻ ghi nợ nội địa (Napas)

**Bước 4: Xác thực**
```
1. Google sẽ charge $1-2 để verify
2. Tiền sẽ được hoàn lại sau 3-5 ngày
3. Check SMS/email để confirm
```

**Bước 5: Hoàn tất**
```
1. Click "Start my free trial" hoặc "Submit"
2. ✅ Billing account đã tạo!
```

---

## 🔑 BƯỚC 2: LINK BILLING VÀO PROJECT (2 phút)

### 2.1. Vào Project Settings:
```
1. Click menu ☰ → Billing
2. Click "Link a billing account"
3. Chọn billing account vừa tạo
4. Click "Set account"
```

### 2.2. Verify:
```
1. Vào Billing → Overview
2. Thấy: "Billing account: [Tên account]"
3. Status: "Active" ✅
```

---

## 🎯 BƯỚC 3: ENABLE GENERATIVE LANGUAGE API (2 phút)

### 3.1. Mở API Library:
```
1. Click menu ☰
2. APIs & Services → Library
3. Search: "Generative Language API"
```

### 3.2. Enable API:
```
1. Click "Generative Language API"
2. Click "Enable"
3. Đợi 10-30 giây
4. ✅ API Enabled!
```

---

## ⚡ BƯỚC 4: UPGRADE TIER TRONG AI STUDIO (1 phút)

### 4.1. Truy cập AI Studio:
```
https://aistudio.google.com/app/apikey
```

### 4.2. Tìm project:
```
1. Tìm project đã enable billing
2. Thấy nút "Upgrade" (màu xanh)
```

### 4.3. Click Upgrade:
```
1. Click "Upgrade to Tier 1"
2. Đọc thông tin
3. Click "Confirm"
4. Đợi 5-10 giây
5. ✅ DONE! Lên Tier 1 rồi!
```

### 4.4. Verify Tier:
```
1. Vào Usage page: https://aistudio.google.com/usage
2. Check "Rate Limits"
3. Thấy:
   - RPM: 4,000 (vs 15 trước)
   - RPD: Unlimited (vs 1,000 trước)
   - ✅ Đã lên Tier 1!
```

---

## 🧪 BƯỚC 5: TEST API (2 phút)

### 5.1. Test trong app:
```
1. Mở app
2. Chọn 50-100 files
3. Set delay: 500ms (nhanh hơn)
4. Click "Bắt đầu quét"
5. ✅ Không bị rate limit!
```

### 5.2. Monitor usage:
```
1. Vào https://aistudio.google.com/usage
2. Check:
   - Requests made
   - Tokens used
   - Estimated cost
```

---

## 💰 BƯỚC 6: QUẢN LÝ CHI PHÍ

### 6.1. Set Budget Alert:

**Tránh chi quá mức:**
```
1. Vào Google Cloud Console
2. Billing → Budgets & alerts
3. Click "Create Budget"
4. Set amount: VD $50/month
5. Set alert: 50%, 90%, 100%
6. Add email notification
7. Click "Finish"
```

**Khi nào nhận alert:**
```
- 50% budget: "Bạn đã dùng $25/$50"
- 90% budget: "Bạn đã dùng $45/$50" ⚠️
- 100% budget: "Bạn đã vượt budget!" 🚨
```

### 6.2. Monitor Cost:
```
1. Vào Billing → Reports
2. Filter by:
   - Service: Generative Language API
   - Time range: Last 7 days
3. Xem:
   - Daily cost
   - Usage by model
   - Cost trends
```

### 6.3. Cost Optimization:
```
✅ Dùng Flash Lite (rẻ hơn Flash)
✅ Enable resize (giảm 50% cost)
✅ Scan off-peak hours
✅ Monitor usage daily
```

---

## 📊 CHI PHÍ THỰC TẾ:

### Ví dụ tính toán:

**Scenario 1: Văn phòng nhỏ (1,000 trang/ngày)**
```
1,000 trang/ngày × 30 ngày = 30,000 trang/tháng
Chi phí: 30,000 × $0.00089 = $26.70/tháng
```

**Scenario 2: Văn phòng vừa (5,000 trang/ngày)**
```
5,000 trang/ngày × 30 ngày = 150,000 trang/tháng
Chi phí: 150,000 × $0.00089 = $133.50/tháng
```

**Scenario 3: Doanh nghiệp (20,000 trang/ngày)**
```
20,000 trang/ngày × 30 ngày = 600,000 trang/tháng
Chi phí: 600,000 × $0.00089 = $534/tháng

So với thuê người: 3-4 người × $500 = $1,500-2,000/tháng
TIẾT KIỆM: ~70-75%! 🎉
```

---

## ⚠️ LƯU Ý QUAN TRỌNG:

### 1. Billing & Charges:

**Google chỉ charge khi:**
- ✅ Vượt free tier limits
- ✅ Thực tế dùng API
- ❌ KHÔNG auto-charge nếu không dùng

**Free trial:**
```
- Google Cloud: $300 credit (90 ngày)
- Có thể dùng free credit cho Gemini API
- Sau khi hết, mới charge thẻ
```

**Cancel anytime:**
```
1. Vào Billing → Account Management
2. Click "Close billing account"
3. Confirm
→ Không bị charge nữa
```

### 2. Security:

**Protect API key:**
```
✅ Restrict key to Generative Language API only
✅ Set quota limits
✅ Monitor usage daily
✅ Rotate key every 3-6 months
```

**Set API restrictions:**
```
1. APIs & Services → Credentials
2. Click key name
3. API restrictions → Select "Generative Language API"
4. Save
```

### 3. Tier 2 & 3:

**Tự động lên tier cao hơn:**
```
Tier 2:
- Điều kiện: Spend > $250 + 30 days
- Limits: RPM 10,000, RPD unlimited
- Auto upgrade khi đủ điều kiện

Tier 3:
- Điều kiện: Spend > $1,000 + 30 days
- Limits: RPM 30,000, RPD unlimited
```

---

## 🆘 TROUBLESHOOTING:

### Không thấy nút "Upgrade"?

**Check:**
```
1. Billing đã enable chưa?
   → Vào Billing → Overview → Check "Active"

2. Project đúng chưa?
   → Check project name trong API key page

3. Đợi 5-10 phút
   → Google cần thời gian sync
```

### Thẻ bị từ chối?

**Solutions:**
```
1. Check số dư
2. Gọi bank enable international payment
3. Thử thẻ khác (Visa/Mastercard)
4. Dùng thẻ ảo (VD: MoMo virtual card)
```

### API vẫn bị limit?

**Check:**
```
1. Tier đã upgrade chưa?
   → Vào Usage page check

2. Delay đủ lớn chưa?
   → Set 500-1000ms

3. API key đúng project chưa?
   → Generate key mới từ project đã upgrade
```

### Chi phí cao hơn dự tính?

**Optimize:**
```
1. Enable resize trong app
2. Dùng Flash Lite (không dùng Flash)
3. Check usage report
4. Set budget alert
```

---

## 📱 ALTERNATIVE: DÙNG FREE TIER UNLIMITED

### Nếu không muốn paid:

**Option 1: Multiple keys**
```
- Tạo 3-5 Gmail
- Mỗi Gmail 1 API key
- Mỗi key: 1,000 RPD (Flash Lite)
- Total: 3,000-5,000 RPD
- Chi phí: $0
```

**Option 2: Hybrid (Free + Offline)**
```
- Documents đơn giản: VietOCR (free, unlimited)
- Documents phức tạp: Gemini (1,000/day)
- Chi phí: $0
- Accuracy: ~92% average
```

**Option 3: Wait & Rotate**
```
- Scan trong free tier (1,000/day)
- Hết quota → Đợi 7 AM ngày mai
- Hoặc switch sang key backup
- Chi phí: $0
```

---

## 📊 DECISION MATRIX:

| Nhu cầu | Solution | Chi phí/tháng |
|---------|----------|---------------|
| < 1,000 trang/ngày | **Free tier** | $0 |
| 1,000-5,000/ngày | **Multiple keys** | $0 |
| 5,000-10,000/ngày | **Tier 1 Paid** | ~$50-90 |
| > 10,000/ngày | **Tier 1 Paid** | ~$90-270 |

---

## 🎓 BEST PRACTICES:

### 1. Start small:
```
Week 1: Test với free tier
Week 2: Estimate usage (bao nhiêu trang/ngày?)
Week 3: Upgrade nếu > 1,000/day
Week 4: Monitor & optimize
```

### 2. Monitor daily:
```
- Check usage mỗi sáng
- Set budget alerts
- Review reports weekly
- Optimize settings based on cost
```

### 3. Optimize:
```
✅ Enable resize (save 50%)
✅ Use Flash Lite (save 78% vs Flash)
✅ Batch scan (efficient)
✅ Monitor accuracy (không cần perfect)
```

---

## 📞 SUPPORT:

### Nếu cần help:

**Google Cloud Support:**
```
1. Free tier: Community support
2. Paid tier: Email support
3. Premium: 24/7 phone support
```

**Resources:**
```
- Docs: https://ai.google.dev/gemini-api/docs
- Community: https://discuss.ai.google.dev/
- Stack Overflow: google-gemini-api tag
```

---

## ✅ CHECKLIST HOÀN THÀNH:

```
□ Enable Cloud Billing
□ Link billing to project
□ Enable Generative Language API
□ Upgrade to Tier 1
□ Verify tier upgrade
□ Test API
□ Set budget alert
□ Monitor usage
```

---

**Total time: ~20 phút**  
**Chi phí setup: $0** (chỉ charge khi dùng)  
**Kết quả: UNLIMITED scans!** 🎉

---

**Summary:**
1. Enable billing trong Google Cloud (10 phút)
2. Link billing vào project (2 phút)
3. Enable API (2 phút)
4. Upgrade tier trong AI Studio (1 phút)
5. Test & monitor (5 phút)

**Total: ~20 phút để có unlimited scans!** 🚀
