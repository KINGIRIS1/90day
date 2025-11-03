# 🔑 Hướng Dẫn Tạo API Key Mới Khi Hết Quota

## 🎯 Tình huống: Key hiện tại hết 1,500 requests/ngày

### ✅ SOLUTION: Tạo Gmail mới → Key mới → 1,500 requests mới!

---

## 📝 BƯỚC 1: Tạo Gmail Mới (5 phút)

### 1.1. Truy cập:
```
https://accounts.google.com/signup
```

### 1.2. Điền thông tin:
```
✅ Họ tên: Tùy ý (VD: "Scan App 2")
✅ Username: Tùy ý (VD: scanapp2024)
✅ Password: Tạo password mạnh
✅ Số điện thoại: Có thể dùng số cũ
✅ Email khôi phục: Có thể bỏ qua
```

### 1.3. Xác thực:
```
- Google có thể yêu cầu verify số điện thoại
- Dùng số điện thoại hiện tại (OK)
- Nhận mã OTP → Nhập vào
```

### 1.4. Hoàn tất:
```
✅ Gmail mới đã tạo xong!
VD: scanapp2024@gmail.com
```

---

## 🔑 BƯỚC 2: Tạo API Key Mới

### 2.1. Truy cập Google AI Studio:
```
https://aistudio.google.com/
```

### 2.2. Đăng nhập:
```
- Dùng Gmail MỚI vừa tạo
- Chấp nhận Terms of Service
```

### 2.3. Tạo API Key:

**Method A: Trực tiếp từ AI Studio**
```
1. Click "Get API Key" (góc phải trên)
2. Click "Create API Key"
3. Chọn "Create API key in new project"
4. Đặt tên project (VD: "OCR Scanner")
5. Click "Create"
6. ✅ Copy API key (dạng: AIzaSy...)
```

**Method B: Từ Google Cloud Console**
```
1. Truy cập: https://console.cloud.google.com/
2. Create New Project
   - Name: "OCR Scanner"
   - Click "Create"
3. Enable API:
   - Search: "Generative Language API"
   - Click "Enable"
4. Create Credentials:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - ✅ Copy API key
5. (Optional) Restrict key:
   - Click key name → Restrictions
   - API restrictions → Select "Generative Language API"
   - Save
```

### 2.4. Test Key:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

---

## 🔄 BƯỚC 3: Thay Key Trong App

### 3.1. Mở App:
```
1. Click Settings (⚙️)
2. Vào "Cloud OCR Settings"
```

### 3.2. Chọn Gemini Flash:
```
1. Chọn radio button: "Gemini 2.5 Flash" hoặc "Flash Lite"
2. Paste API key mới vào ô "API Key"
3. Click "Test API Key" (nếu có)
```

### 3.3. Lưu:
```
1. Click "💾 Lưu cài đặt"
2. Thấy: "✅ Đã lưu cài đặt thành công!"
```

### 3.4. Test Scan:
```
1. Quay lại trang chính
2. Chọn 1 file test
3. Click "Bắt đầu quét"
4. ✅ Nếu OK → Key hoạt động!
```

---

## 💡 TIPS & BEST PRACTICES

### 📌 Quản lý nhiều Keys:

**Lưu keys an toàn:**
```
Gmail 1: your.email@gmail.com
Key 1:   AIzaSyABC123...
Quota:   1,500/day
Used:    ✅ Còn 200

Gmail 2: scanapp2024@gmail.com  
Key 2:   AIzaSyDEF456...
Quota:   1,500/day
Used:    🆕 Chưa dùng
```

**Rotation strategy:**
```
Day 1: Dùng Key 1 (1,500 requests)
Day 2: Dùng Key 2 (1,500 requests)
Day 3: Dùng Key 1 (đã reset)
→ Luân phiên, không bao giờ hết!
```

### 📊 Monitor Usage:

**Check quota định kỳ:**
```
1. Vào https://aistudio.google.com/
2. Click "Usage"
3. Xem:
   - Requests used: 1,234/1,500
   - Resets in: 5 hours
```

**Set reminder:**
```
- Mỗi sáng 7 AM: Check quota
- Nếu < 500 còn lại → Chuẩn bị key backup
```

### 🔐 Security:

**Protect your keys:**
```
✅ DO:
- Lưu trong password manager
- Restrict key (only Generative Language API)
- Delete key không dùng

❌ DON'T:
- Share key publicly
- Commit to GitHub
- Dùng key trong production app (client-side)
```

---

## ⚠️ TROUBLESHOOTING

### Key mới vẫn không hoạt động?

**Check 1: Enable API**
```
1. Vào https://console.cloud.google.com/
2. Select project
3. APIs & Services → Library
4. Search "Generative Language API"
5. Click "Enable" nếu chưa enable
```

**Check 2: Key restrictions**
```
1. Credentials → Click key name
2. Check "API restrictions"
3. Nếu có restrict → Phải add "Generative Language API"
```

**Check 3: Billing**
```
- Free tier KHÔNG CẦN billing
- Nếu muốn unlimited → Enable billing
```

### Gmail không tạo được?

**Solution:**
```
1. Dùng số điện thoại khác
2. Hoặc xin bạn/người thân tạo hộ
3. Hoặc mua SIM mới (~20-30k)
```

### Tạo bao nhiêu Gmail được?

**Không giới hạn, nhưng:**
```
- Google có thể yêu cầu verify SĐT
- Mỗi SĐT verify được ~3-5 Gmail
- Solution: Dùng nhiều SĐT hoặc email khôi phục
```

---

## 📊 COST COMPARISON

### Tạo Key Mới vs Upgrade Paid:

| Option | Cost | Quota | Setup Time |
|--------|------|-------|------------|
| **Key mới (free)** | $0 | 1,500/day | 5 phút |
| **Paid tier** | ~$0.89/1K | Unlimited | 2 phút |

**Khuyến nghị:**
```
IF (scan < 1,500/day):
    → Tạo key mới (free)
    
IF (scan > 1,500/day):
    → Upgrade paid (chỉ ~$1/1K trang)
    
IF (scan 1,500-3,000/day):
    → Dùng 2 keys luân phiên (free)
```

---

## 🎓 ADVANCED: Multiple Keys Auto-Rotation

### Script tự động switch key:

```javascript
// Trong app (future feature)
const keys = [
    { gmail: 'key1@gmail.com', key: 'AIza...', quota: 1500 },
    { gmail: 'key2@gmail.com', key: 'AIzb...', quota: 1500 }
];

let currentKeyIndex = 0;

async function scanWithAutoRotation(files) {
    for (let file of files) {
        try {
            await scan(file, keys[currentKeyIndex].key);
        } catch (error) {
            if (error.code === 'QUOTA_EXCEEDED') {
                // Switch to next key
                currentKeyIndex = (currentKeyIndex + 1) % keys.length;
                console.log(`Switched to key ${currentKeyIndex + 1}`);
                // Retry
                await scan(file, keys[currentKeyIndex].key);
            }
        }
    }
}
```

---

## 📞 SUPPORT

### Nếu vẫn gặp vấn đề:

**1. Check Google AI Studio Status:**
```
https://status.google.com/
```

**2. Google Cloud Support:**
```
https://cloud.google.com/support
```

**3. Community:**
```
- Stack Overflow: google-generative-ai tag
- Reddit: r/GoogleCloud
```

---

**Summary:**
1. Tạo Gmail mới (5 phút)
2. Tạo API key mới (2 phút)
3. Paste vào app (30 giây)
4. ✅ Lại có 1,500 requests!

**Total time: ~8 phút**  
**Cost: $0**  
**Result: Unlimited scans (với nhiều keys)** 🎉
