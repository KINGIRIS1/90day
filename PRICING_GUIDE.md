# 💰 Bảng giá: Chi phí quét tài liệu

## 📊 Tóm tắt nhanh

| Phương thức | Chi phí/ảnh | Chi phí/50 ảnh | Chi phí/1000 ảnh |
|-------------|-------------|----------------|------------------|
| **Emergent LLM** (đang dùng) | ~$0.002 | ~$0.10 | **~$2.00** |
| **OpenAI Direct** (fallback) | ~$0.003 | ~$0.15 | **~$3.00** |

💡 **Khuyến nghị**: Dùng **Emergent LLM Key** (tiết kiệm 33%)

---

## 🔍 Chi tiết pricing

### 1. **Emergent LLM Key** (Đang sử dụng - PRIMARY)

Cấu hình hiện tại:
```
LLM_PRIMARY=emergent
Model: gpt-4o (qua Emergent)
Max tokens: 700 tokens/ảnh
```

**Pricing breakdown**:

| Component | Giá | Chi phí/ảnh |
|-----------|-----|-------------|
| Input tokens | ~1,000 tokens (ảnh 800px + prompt) | $0.0025/1K = **$0.0025** |
| Output tokens | ~200 tokens (JSON response) | $0.010/1K = **$0.0020** |
| **Tổng** | | **~$0.0045/ảnh** |

*Note: Emergent LLM Key có thể có discount, giá thực tế có thể thấp hơn*

**Ví dụ tính toán**:

```
Văn phòng quét 1000 hồ sơ/ngày:
- Trung bình: 10 ảnh/hồ sơ = 10,000 ảnh/ngày
- Chi phí: 10,000 × $0.0045 = $45/ngày
- Chi phí tháng: $45 × 22 ngày = ~$990/tháng

Nếu có discount 50% từ Emergent:
→ ~$495/tháng
```

---

### 2. **OpenAI Direct API** (Fallback)

Cấu hình:
```
Model: gpt-4o-mini
Max tokens: 700 tokens/ảnh
```

**Pricing công khai** (OpenAI official):

| Component | Giá | Chi phí/ảnh |
|-----------|-----|-------------|
| Input tokens | ~1,000 tokens | $0.150/1M tokens = **$0.00015** |
| Output tokens | ~200 tokens | $0.600/1M tokens = **$0.00012** |
| **Vision API surcharge** | Image processing | **+$0.00170** |
| **Tổng** | | **~$0.00197/ảnh** |

*Giá cập nhật: Jan 2025*

**Ví dụ**:
```
1000 hồ sơ × 10 ảnh = 10,000 ảnh
Chi phí: 10,000 × $0.00197 = $19.70/ngày
Chi phí tháng: ~$433/tháng
```

---

### 3. **So sánh chi phí thực tế**

#### Scenario 1: Văn phòng nhỏ (100 hồ sơ/ngày)

```
100 hồ sơ × 10 ảnh/hồ sơ = 1,000 ảnh/ngày

Emergent LLM:
- 1,000 × $0.0045 = $4.50/ngày
- Tháng: $4.50 × 22 = $99/tháng

OpenAI Direct:
- 1,000 × $0.00197 = $1.97/ngày
- Tháng: $1.97 × 22 = $43/tháng

✅ OpenAI rẻ hơn cho usage thấp
```

#### Scenario 2: Văn phòng lớn (500 hồ sơ/ngày)

```
500 hồ sơ × 10 ảnh/hồ sơ = 5,000 ảnh/ngày

Emergent LLM (có thể có discount):
- 5,000 × $0.0045 = $22.50/ngày
- Tháng: $495/tháng
- Với discount 30%: ~$346/tháng

OpenAI Direct:
- 5,000 × $0.00197 = $9.85/ngày
- Tháng: $217/tháng

⚠️ Cần check OpenAI rate limit!
```

#### Scenario 3: Quy mô lớn (2000 hồ sơ/ngày)

```
2,000 hồ sơ × 10 ảnh/hồ sơ = 20,000 ảnh/ngày

Emergent LLM:
- 20,000 × $0.0045 = $90/ngày
- Tháng: $1,980/tháng
- Với enterprise discount: ~$1,200/tháng

OpenAI Direct:
- 20,000 × $0.00197 = $39.40/ngày
- Tháng: $867/tháng
- ❌ Có thể bị rate limit (429 errors)
```

---

## 🎯 Chi phí khác

### Infrastructure (Monthly)

| Dịch vụ | Mức | Chi phí |
|---------|-----|---------|
| **Railway Hosting** | Pro plan | $20-50/tháng |
| **MongoDB Atlas** | M0 Free / M10 | $0-25/tháng |
| **Bandwidth** | ~500GB/tháng | Included |
| **Storage** | PDF results | ~$5/tháng |
| **Total Infrastructure** | | **~$30-80/tháng** |

---

## 💡 Tối ưu chi phí

### 1. **Giảm số lần gọi API**

Hiện tại mỗi ảnh = 1 API call

**Tối ưu**:
- ✅ Cache kết quả đã quét (giống nhau)
- ✅ Batch processing (đã implement)
- ✅ Skip ảnh trùng lặp

**Tiết kiệm**: 10-20%

### 2. **Giảm tokens**

Hiện tại: max_tokens=700

**Tối ưu**:
- Giảm prompt size (hiện tại ~500 tokens)
- Giảm max_tokens xuống 500 (vẫn đủ)
- Compress ảnh tốt hơn (800px → 600px)

**Tiết kiệm**: 20-30%

### 3. **Use Emergent LLM Key discount**

Emergent platform có thể offer:
- Volume discount (>10K calls/month)
- Enterprise plan
- Custom pricing

**Liên hệ**: Emergent support để hỏi về pricing

---

## 📊 Công thức tính chi phí

### Cho 1 ảnh:

```
Chi phí/ảnh = (Input tokens × $rate_in) + (Output tokens × $rate_out)

Emergent (gpt-4o):
= (1000 × $0.0025/1K) + (200 × $0.010/1K)
= $0.0025 + $0.0020
= $0.0045/ảnh

OpenAI (gpt-4o-mini):
= (1000 × $0.00015/1K) + (200 × $0.00012/1K) + $0.0017 (vision)
= $0.00015 + $0.00012 + $0.0017
= $0.00197/ảnh
```

### Cho 1 hồ sơ (10 ảnh):

```
Emergent: 10 × $0.0045 = $0.045/hồ sơ
OpenAI:   10 × $0.00197 = $0.0197/hồ sơ
```

### Cho 1 tháng (X hồ sơ/ngày):

```
Chi phí tháng = X hồ sơ × 10 ảnh/hồ sơ × $rate/ảnh × 22 ngày

Ví dụ: 500 hồ sơ/ngày
= 500 × 10 × $0.00197 × 22
= $217/tháng (OpenAI)
```

---

## 🔧 Cấu hình hiện tại

```bash
# /app/backend/.env
LLM_PRIMARY=emergent          # Dùng Emergent làm primary
OPENAI_API_KEY=sk-proj-...    # Fallback nếu Emergent fail
LLM_FALLBACK_ENABLED=true     # Enable fallback
MAX_CONCURRENT_SCANS=5        # Process 5 ảnh đồng thời
```

**Behavior**:
1. Mỗi ảnh gọi Emergent LLM first
2. Nếu Emergent fail/rate limit → Fallback OpenAI
3. Nếu cả 2 fail → Return error

---

## 📈 Dự báo chi phí

### Projection cho 1 năm

| Scale | Ảnh/ngày | Chi phí/tháng | Chi phí/năm |
|-------|----------|---------------|-------------|
| **Small** (10 hồ sơ/ngày) | 100 | $4 | **$50** |
| **Medium** (100 hồ sơ/ngày) | 1,000 | $43 | **$520** |
| **Large** (500 hồ sơ/ngày) | 5,000 | $217 | **$2,600** |
| **Enterprise** (2000 hồ sơ/ngày) | 20,000 | $867 | **$10,400** |

*Giá dựa trên OpenAI gpt-4o-mini*

---

## 💰 Khuyến nghị

### Cho startup/test (< 100 hồ sơ/ngày):
✅ **Dùng OpenAI gpt-4o-mini** 
- Rẻ nhất: ~$43/tháng
- Ổn định
- Pay-as-you-go

### Cho văn phòng (100-500 hồ sơ/ngày):
✅ **Dùng Emergent LLM Key với discount**
- Liên hệ Emergent để negotiate giá
- Volume discount
- Better support

### Cho enterprise (>1000 hồ sơ/ngày):
✅ **Custom solution**
- Self-host LLM (LLaMA, Qwen-VL)
- Cloud GPU (A100) ~$1,000/tháng
- Unlimited usage
- Chi phí cố định

---

## 🔍 Kiểm tra usage hiện tại

### Xem Emergent LLM usage:

1. Login vào Emergent platform
2. Go to **Profile** → **Universal Key** → **Usage**
3. Xem:
   - Total calls
   - Total tokens
   - Cost breakdown
   - Balance remaining

### Xem OpenAI usage:

1. Login https://platform.openai.com
2. Go to **Usage**
3. Xem:
   - Daily usage
   - Cost per day
   - Current billing cycle

---

## ❓ FAQ

### 1. Có tính phí cho ảnh bị lỗi không?

❌ **CÓ** - Mỗi API call đều tính phí, kể cả fail.

**Giải pháp**: Filter kỹ ảnh trước khi gửi (đã implement)

### 2. Có thể giảm chi phí xuống không?

✅ **CÓ**:
- Giảm image size (đã optimize: 800px)
- Cache results
- Use cheaper model (gpt-3.5-turbo-vision)
- Self-host LLM

### 3. Chi phí có tăng khi nhiều người dùng không?

✅ **CÓ** - Tính theo số ảnh quét, không phải số user.

### 4. Có package giá cố định không?

❌ Hiện tại: Pay-as-you-go
✅ Có thể: Negotiate với Emergent cho enterprise plan

---

## 📞 Liên hệ để optimize pricing

**Emergent Support**: support@emergent.ai
- Hỏi về volume discount
- Enterprise pricing
- Custom solutions

**Alternative**:
- Sử dụng OpenAI Tier pricing
- Consider self-hosted LLM cho scale lớn

---

## 📝 Summary

**Chi phí chính**: LLM API calls
**Giá trung bình**: $0.002-0.005/ảnh
**Chi phí khác**: Infrastructure ~$30-80/tháng

**Total cost** cho 100 hồ sơ/ngày:
```
LLM: $43/tháng
Infrastructure: $50/tháng
Total: ~$93/tháng (~2.1 triệu VNĐ/tháng)
```

💡 **Khuyến nghị**: Start với OpenAI gpt-4o-mini, scale lên Emergent enterprise plan khi volume cao.
