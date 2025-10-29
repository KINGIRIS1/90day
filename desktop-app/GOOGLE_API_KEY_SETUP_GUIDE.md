# HƯỚNG DẪN CHI TIẾT - Lấy Google API Key cho Gemini Flash

**Mục đích**: Lấy Google API Key để sử dụng Gemini Flash 2.0 trong app

**Thời gian**: ~5-10 phút

**Chi phí**: Miễn phí (có free tier: 45,000 requests/tháng)

---

## 📋 YÊU CẦU:

- ✅ Tài khoản Gmail (Google Account)
- ✅ Trình duyệt web
- ✅ Internet connection

---

## 🚀 BƯỚC 1: TẠO PROJECT MỚI

### 1.1. Truy cập Google Cloud Console

1. Mở trình duyệt → Truy cập: **https://console.cloud.google.com/**

2. Đăng nhập bằng tài khoản Gmail của bạn

3. Lần đầu sử dụng sẽ thấy màn hình chào mừng:
   ```
   Welcome to Google Cloud Console
   ```

### 1.2. Tạo Project

**Bước 1**: Tìm dropdown "Select a project"
- Vị trí: Góc trên bên trái, cạnh logo Google Cloud
- Có icon: ▼ (mũi tên xuống)
- Text: "Select a project" hoặc tên project hiện tại

**Bước 2**: Click vào dropdown → Hiện popup

**Bước 3**: Trong popup, click button **"NEW PROJECT"**
- Vị trí: Góc trên bên phải của popup
- Màu xanh dương

**Bước 4**: Điền thông tin project

Màn hình "New Project":

```
┌─────────────────────────────────────────┐
│  New Project                            │
├─────────────────────────────────────────┤
│                                         │
│  Project name *                         │
│  ┌───────────────────────────────────┐ │
│  │ Vietnamese-OCR-Scanner            │ │ ← Nhập tên ở đây
│  └───────────────────────────────────┘ │
│                                         │
│  Project ID                             │
│  ┌───────────────────────────────────┐ │
│  │ vietnamese-ocr-scanner-xxxxx      │ │ ← Tự động generate
│  └───────────────────────────────────┘ │
│                                         │
│  Location                               │
│  ┌───────────────────────────────────┐ │
│  │ No organization                   │ │ ← Để mặc định
│  └───────────────────────────────────┘ │
│                                         │
│         [CANCEL]        [CREATE]        │
└─────────────────────────────────────────┘
```

**Điền thông tin**:
- **Project name**: `Vietnamese-OCR-Scanner` (hoặc tên bất kỳ)
- **Project ID**: Tự động generate (không cần sửa)
- **Location**: "No organization" (để mặc định)

**Bước 5**: Click button **"CREATE"** (màu xanh)

**Bước 6**: Đợi ~10-30 giây
- Góc trên bên phải sẽ có thông báo:
  ```
  ✓ Creating project "Vietnamese-OCR-Scanner"...
  ```

**Bước 7**: Sau khi tạo xong:
- Popup đóng lại
- Project đã được chọn (thấy tên project ở góc trên trái)

---

## 🚀 BƯỚC 2: BẬT GENERATIVE LANGUAGE API

### 2.1. Truy cập API Library

**Cách 1: Qua Menu**

1. Click ☰ (hamburger menu) ở góc trên trái

2. Scroll xuống → Tìm section "**APIs & Services**"

3. Click "**Library**"

**Cách 2: Trực tiếp (Nhanh hơn)**

Truy cập URL: **https://console.cloud.google.com/apis/library**

### 2.2. Tìm Generative Language API

Màn hình API Library:

```
┌─────────────────────────────────────────────────┐
│  API Library                                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │  🔍 Search for APIs & Services      │       │ ← Search box
│  └─────────────────────────────────────┘       │
│                                                 │
│  Featured                                       │
│  ┌────────┐ ┌────────┐ ┌────────┐             │
│  │ Maps   │ │ Vision │ │ Speech │             │
│  └────────┘ └────────┘ └────────┘             │
└─────────────────────────────────────────────────┘
```

**Bước 1**: Click vào search box

**Bước 2**: Gõ: `Generative Language API`

**Lưu ý**: Có thể search bằng các từ khóa:
- ✅ `Generative Language API` (chính xác)
- ✅ `Gemini API` (cũng được)
- ✅ `generative ai` (cũng tìm được)

**Bước 3**: Kết quả tìm kiếm

Sẽ thấy card:

```
┌────────────────────────────────────────┐
│  🤖 Generative Language API           │
│                                        │
│  Build with Gemini, Google's largest  │
│  and most capable AI model             │
│                                        │
│  By Google                             │
│                                        │
│              [VIEW]                    │ ← Click vào đây
└────────────────────────────────────────┘
```

**Bước 4**: Click vào card hoặc button **"VIEW"**

### 2.3. Enable API

Màn hình Generative Language API:

```
┌──────────────────────────────────────────────────┐
│  Generative Language API                         │
├──────────────────────────────────────────────────┤
│                                                  │
│  🤖 Generative Language API                     │
│                                                  │
│  Build with Gemini, Google's largest and most   │
│  capable AI model. The Gemini API gives you     │
│  access to Gemini models created by Google      │
│  DeepMind.                                       │
│                                                  │
│  Status: ⚠️ API not enabled                     │
│                                                  │
│         [         ENABLE         ]               │ ← Click đây
│                                                  │
│  Pricing: Free tier available                   │
│  • 45,000 requests per month                    │
│  • After: $0.16 per 1,000 requests              │
└──────────────────────────────────────────────────┘
```

**Bước 1**: Click button **"ENABLE"** (màu xanh, to, ở giữa)

**Bước 2**: Đợi ~10-30 giây
- Hiện loading spinner
- Text: "Enabling API..."

**Bước 3**: Sau khi enable xong:
- Redirect sang trang API details
- Status: ✅ API enabled
- Button "ENABLE" → "MANAGE"

```
┌──────────────────────────────────────────────────┐
│  Generative Language API                         │
├──────────────────────────────────────────────────┤
│                                                  │
│  Status: ✅ API enabled                         │
│                                                  │
│         [         MANAGE         ]               │
│                                                  │
│  Metrics  Quotas  Credentials                   │
└──────────────────────────────────────────────────┘
```

**✅ THÀNH CÔNG!** API đã được bật.

---

## 🚀 BƯỚC 3: TẠO API KEY

### 3.1. Truy cập Credentials

**Cách 1: Qua Menu**

1. Click ☰ (menu) → "**APIs & Services**" → "**Credentials**"

**Cách 2: Trực tiếp (Nhanh hơn)**

Truy cập URL: **https://console.cloud.google.com/apis/credentials**

### 3.2. Tạo API Key

Màn hình Credentials:

```
┌──────────────────────────────────────────────────┐
│  Credentials                                     │
├──────────────────────────────────────────────────┤
│                                                  │
│  + CREATE CREDENTIALS  ▼                         │ ← Click đây
│                                                  │
│  ┌────────────────────────────────────┐        │
│  │  No credentials yet                │        │
│  └────────────────────────────────────┘        │
└──────────────────────────────────────────────────┘
```

**Bước 1**: Click button **"+ CREATE CREDENTIALS"**

**Bước 2**: Dropdown hiện ra → Click **"API key"**

```
Dropdown menu:
┌─────────────────────────┐
│  API key                │ ← Click đây
│  OAuth client ID        │
│  Service account        │
└─────────────────────────┘
```

**Bước 3**: Popup hiện ra với API key

```
┌────────────────────────────────────────┐
│  API key created                       │
├────────────────────────────────────────┤
│                                        │
│  Your API key:                         │
│  ┌──────────────────────────────────┐ │
│  │ AIzaSyABC123...xyz789           │ │ ← Copy cái này!
│  └──────────────────────────────────┘ │
│                                        │
│  [COPY]  [CLOSE]  [RESTRICT KEY]      │
└────────────────────────────────────────┘
```

**Bước 4**: Click button **"COPY"** để copy API key

**Bước 5**: Lưu key vào notepad hoặc paste trực tiếp vào app

**⚠️ LƯU Ý BẢO MẬT**:
- ❌ KHÔNG chia sẻ key này cho ai
- ❌ KHÔNG commit key lên GitHub/public repos
- ✅ Chỉ dùng trong app của bạn

**Bước 6**: Click **"CLOSE"** để đóng popup

---

## 🚀 BƯỚC 4: (OPTIONAL) RESTRICT API KEY

**Tại sao?** Để bảo mật hơn - chỉ cho phép API key sử dụng Gemini API

**Bước 1**: Trong màn hình Credentials, tìm API key vừa tạo

**Bước 2**: Click vào API key name

**Bước 3**: Section "API restrictions"

```
┌────────────────────────────────────────┐
│  API restrictions                      │
├────────────────────────────────────────┤
│                                        │
│  ⚪ Don't restrict key                │
│  ⚫ Restrict key                       │ ← Chọn cái này
│                                        │
│  Select APIs:                          │
│  ┌──────────────────────────────────┐ │
│  │ 🔍 Search APIs                   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ☑️ Generative Language API          │ ← Check cái này
└────────────────────────────────────────┘
```

**Bước 4**: Chọn "**Restrict key**"

**Bước 5**: Search và check: **"Generative Language API"**

**Bước 6**: Click **"SAVE"** ở cuối trang

---

## 🚀 BƯỚC 5: SỬ DỤNG TRONG APP

### 5.1. Mở App của bạn

1. Click "**⚙️ Cài đặt**" → "**Cloud OCR**"

2. Chọn radio button: **"🤖 Gemini Flash 2.0"**

3. Section màu tím sẽ hiện ra

### 5.2. Nhập API Key

1. Trong ô "**Google API Key**"

2. Paste API key: `AIzaSyABC123...xyz789`

3. Click "**🧪 Test API Key**" (optional)
   - ✅ Nếu hợp lệ: Alert "API key hợp lệ!"
   - ❌ Nếu lỗi: Kiểm tra lại key hoặc API đã enable chưa

4. Click "**💾 Lưu cài đặt**"

### 5.3. Sử dụng

- Scan documents → App tự động dùng Gemini Flash
- Console log: `🤖 Using Gemini Flash 2.0 AI`

---

## 💰 PRICING & BILLING

### Free Tier (Không cần credit card)

- ✅ **45,000 requests/tháng** miễn phí
- ✅ Đủ để test và sử dụng nhỏ

### Paid Tier (Cần credit card)

**Khi nào cần?**
- Khi vượt 45,000 requests/tháng
- Muốn tăng quota

**Cách setup billing**:

1. Truy cập: https://console.cloud.google.com/billing

2. Click "**Link a billing account**"

3. Chọn "**Create billing account**" (lần đầu)

4. Điền thông tin:
   - Tên
   - Địa chỉ
   - Credit card

5. Accept terms → Submit

**Giá**:
- $0.16 per 1,000 images
- 60K hồ sơ × 50 trang = $500

---

## ❓ TROUBLESHOOTING

### Lỗi 1: "API not enabled"

**Nguyên nhân**: Quên enable API

**Giải pháp**:
1. Quay lại Bước 2
2. Đảm bảo đã click "ENABLE"
3. Đợi ~30 giây

### Lỗi 2: "API key invalid"

**Nguyên nhân**:
- Copy sai key (thiếu ký tự, có spaces)
- Key bị revoke
- API restrictions sai

**Giải pháp**:
1. Copy lại key (không có spaces)
2. Kiểm tra: Credentials page → Key còn active không
3. Kiểm tra: API restrictions có Generative Language API không

### Lỗi 3: "Quota exceeded"

**Nguyên nhân**: Vượt 45,000 requests/tháng (free tier)

**Giải pháp**:
1. Setup billing account
2. Hoặc đợi tháng sau (quota reset)

### Lỗi 4: "Project not found"

**Nguyên nhân**: API key thuộc project khác

**Giải pháp**:
1. Đảm bảo đang ở đúng project
2. Dropdown "Select a project" → Chọn project đúng

---

## ✅ CHECKLIST HOÀN TẤT:

- [ ] Tạo Google Cloud Project
- [ ] Enable "Generative Language API"
- [ ] Create API Key
- [ ] Copy API Key
- [ ] (Optional) Restrict API Key
- [ ] Paste vào app
- [ ] Test API Key
- [ ] Save settings
- [ ] Scan document test

---

## 📞 HỖ TRỢ:

Nếu gặp vấn đề:

1. **Check Google Cloud Status**:
   - https://status.cloud.google.com/

2. **Check Quota**:
   - https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

3. **Google AI Documentation**:
   - https://ai.google.dev/gemini-api/docs

---

**🎉 HOÀN TẤT! Bây giờ bạn có thể dùng Gemini Flash trong app!**

**Chi phí**: $0.16/1,000 images (rẻ nhất)
**Accuracy**: 93-97% (AI reasoning)
