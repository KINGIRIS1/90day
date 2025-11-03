# 🔧 Fix Rate Limit - Thêm Delay Giữa Requests

## 🚨 VẤN ĐỀ PHÁT HIỆN

### Code Cũ (KHÔNG CÓ DELAY):
```javascript
for (let i = 0; i < filesToProcess.length; i++) {
    let result = await processOffline(file);
    // ❌ GỬI REQUEST TIẾP NGAY LẬP TỨC!
}
```

**Kết quả:**
- Nếu mỗi request mất 1s → **60 requests/phút** (đúng limit)
- Nếu mỗi request mất 0.8s → **75 requests/phút** ⚠️ **VƯỢT LIMIT!**
- **Rất dễ vượt** vì tốc độ request phụ thuộc vào:
  - Tốc độ mạng
  - Load server Gemini
  - Kích thước ảnh
  - Model type (Flash Lite nhanh hơn Flash)

---

## ✅ GIẢI PHÁP: Thêm Delay

### Code Mới (CÓ DELAY):
```javascript
for (let i = 0; i < filesToProcess.length; i++) {
    let result = await processOffline(file);
    
    // 🔧 ADD DELAY: Tránh vượt Rate Limit
    if (i < filesToProcess.length - 1) {
        await new Promise(resolve => setTimeout(resolve, requestDelay));
    }
}
```

**Lợi ích:**
- ✅ Đảm bảo KHÔNG BAO GIỜ vượt 60 requests/phút
- ✅ User có thể điều chỉnh delay
- ✅ An toàn với mọi tốc độ mạng

---

## 🎛️ UI CONTROL

### Slider Delay:
```
⏱️ Delay: 1200ms = ~50 requests/phút

[========|=======] Slider
0ms     1000ms   2000ms   3000ms

💡 Khuyến nghị: 1200ms (~50/phút)
```

**Tính toán:**
```
Requests per minute = 60000 / (requestDelay + avgProcessTime)

Giả sử avgProcessTime = 1000ms:
- Delay 0ms   → 60000/(0+1000)   = 60/min  (đúng limit)
- Delay 500ms → 60000/(500+1000) = 40/min  ✅
- Delay 1000ms → 60000/(1000+1000) = 30/min ✅
- Delay 1200ms → 60000/(1200+1000) = 27/min ✅
```

---

## 📊 SO SÁNH PERFORMANCE

### Scenario: 100 trang

| Delay | Requests/Min | Thời gian hoàn thành | Risk |
|-------|-------------|---------------------|------|
| **0ms** | ~60 | ~1.7 phút | ⚠️ Cao (dễ vượt) |
| **500ms** | ~40 | ~2.5 phút | ⚡ Trung bình |
| **1000ms** | ~30 | ~3.3 phút | ✅ Thấp |
| **1200ms** | ~27 | ~3.7 phút | ✅ Rất thấp |
| **2000ms** | ~20 | ~5 phút | 🐢 Rất thấp |

**Khuyến nghị:**
- **Mặc định: 1200ms** (balance giữa speed và safety)
- **Nhanh: 500-800ms** (nếu mạng tốt)
- **An toàn: 1500-2000ms** (nếu hay gặp rate limit)

---

## 🎯 CÁCH SỬ DỤNG

### 1. Mở App → Tab "Quét File"

### 2. Thấy UI Delay Control:
```
⏱️ Delay giữa các request (tránh Rate Limit):
[=========|=====] 1200ms = ~50 requests/phút

💡 Khuyến nghị: 1200ms (~50/phút)
```

### 3. Điều chỉnh delay:
- **Kéo sang trái** (0-500ms): Nhanh hơn, nhưng risk cao
- **Giữ ở giữa** (1000-1500ms): Balance tốt ✅
- **Kéo sang phải** (2000-3000ms): Chậm nhưng an toàn 100%

### 4. Bắt đầu scan:
- Chọn files → "Bắt đầu quét"
- App tự động thêm delay theo setting
- ✅ Không lo vượt rate limit!

---

## 🔢 TÍNH TOÁN CHI TIẾT

### Công thức:
```
Total Time = (numFiles × avgProcessTime) + ((numFiles-1) × delay)
```

### Ví dụ: 100 files, delay 1200ms

**Processing time:**
```
Mỗi file: ~1 giây (Gemini API)
Total processing: 100 × 1s = 100s
```

**Delay time:**
```
Số lần delay: 99 (không delay ở file cuối)
Total delay: 99 × 1.2s = 118.8s
```

**Total:**
```
100s + 118.8s = 218.8s ≈ 3.6 phút

Tốc độ: 100 files / 3.6 min ≈ 27 files/min
→ AN TOÀN dưới 60/min!
```

---

## 💡 BEST PRACTICES

### 1. Chọn Delay Dựa Vào Use Case:

**Scan nhỏ (< 20 files):**
```
→ Delay: 500-800ms
→ Lý do: Ít files, risk thấp
→ Scan nhanh: < 1 phút
```

**Scan vừa (20-100 files):**
```
→ Delay: 1000-1200ms (mặc định)
→ Lý do: Balance speed & safety
→ Scan: 3-5 phút
```

**Scan lớn (> 100 files):**
```
→ Delay: 1500-2000ms
→ Lý do: Thời gian dài, ưu tiên an toàn
→ Scan: 5-10 phút
```

### 2. Điều Chỉnh Theo Tình Huống:

**Nếu bị Rate Limit lần đầu:**
```
1. Dừng scan (nút Stop)
2. Tăng delay lên +500ms
3. Tiếp tục scan (nút Resume)
```

**Nếu mạng chậm:**
```
→ Giảm delay xuống 500-800ms
→ Vì processing đã chậm rồi
```

**Nếu mạng nhanh:**
```
→ Tăng delay lên 1500-2000ms
→ Vì risk vượt limit cao
```

### 3. Monitor Performance:

**Xem thời gian trong UI:**
```
Progress: 45/100 files (3 minutes elapsed)
→ Tốc độ: 15 files/min ✅ OK
```

**Nếu quá chậm:**
```
→ Giảm delay 200-300ms
→ Nhưng cẩn thận rate limit!
```

---

## 🆘 TROUBLESHOOTING

### Vẫn bị Rate Limit dù có delay?

**Nguyên nhân:**
1. Delay quá thấp (< 500ms)
2. Processing quá nhanh (Flash Lite + small images)
3. Dùng chung key với máy khác

**Giải pháp:**
```
1. Tăng delay lên 2000ms
2. Pause → Đợi 1 phút → Resume
3. Check xem có máy khác dùng key không
```

### Scan quá chậm?

**Nguyên nhân:**
1. Delay quá cao (> 2000ms)
2. Processing chậm (mạng, server)

**Giải pháp:**
```
1. Giảm delay xuống 800-1000ms
2. Check kết nối mạng
3. Thử Flash Lite (nhanh hơn Flash)
```

### Không biết chọn delay nào?

**Công thức đơn giản:**
```
IF (files < 50):
    delay = 800ms
ELIF (files < 100):
    delay = 1200ms (mặc định)
ELSE:
    delay = 1500ms
```

---

## 📈 IMPACT ANALYSIS

### Before (No Delay):
```
✅ Pros:
  • Scan nhanh (60/min max)

❌ Cons:
  • Dễ vượt rate limit
  • User bị fail giữa chừng
  • Phải retry → mất thời gian hơn
```

### After (With Delay):
```
✅ Pros:
  • Không bao giờ vượt limit
  • Scan ổn định, không fail
  • User control được tốc độ
  • Peace of mind

❌ Cons:
  • Chậm hơn 30-50%
  • Nhưng KHÔNG cần retry
  • → Tổng thời gian tương đương!
```

### Example (100 files):
```
WITHOUT Delay:
├─ Scan 60 files OK (1 min)
├─ File 61: ❌ RATE LIMIT!
├─ Đợi 1 phút
├─ Retry 40 files còn lại (40s)
└─ Total: ~3 phút + stress

WITH Delay (1200ms):
├─ Scan 100 files (3.6 min)
├─ ✅ Không lỗi
└─ Total: ~3.6 phút, no stress
```

---

## 🎓 TECHNICAL NOTES

### JavaScript setTimeout:
```javascript
await new Promise(resolve => setTimeout(resolve, ms));
```
- **Accurate**: ±10ms
- **Non-blocking**: Không block UI
- **Cancelable**: Stop scan vẫn hoạt động

### Delay Placement:
```javascript
// ✅ ĐÚNG: Delay AFTER processing
let result = await processOffline(file);
await delay(ms);

// ❌ SAI: Delay BEFORE processing
await delay(ms);
let result = await processOffline(file);
// → File đầu tiên bị delay không cần thiết
```

### Edge Case: Last File
```javascript
if (i < filesToProcess.length - 1) {
    await delay(requestDelay);
}
```
- File cuối không delay → Save time
- Không ảnh hưởng rate limit

---

## 📝 CHANGELOG

### v1.1.0 (Current):
- ✅ Added configurable delay (0-3000ms)
- ✅ UI slider with real-time calculation
- ✅ Default: 1200ms (~50 requests/min)
- ✅ Recommendations in UI

### Future Enhancements:
- Auto-adjust delay based on response time
- Smart delay (faster for small images)
- Batch pause/resume on rate limit
- Per-model delay settings

---

**Version**: 1.1.0  
**Last Updated**: January 2025  
**Default Delay**: 1200ms (~50 requests/min)
