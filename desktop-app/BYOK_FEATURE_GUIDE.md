# Hướng dẫn BYOK (Bring Your Own Key) - Cloud OCR

## 📌 Tổng quan

Tính năng **BYOK (Bring Your Own Key)** cho phép người dùng tích hợp API key riêng của mình để sử dụng các dịch vụ Cloud OCR cao cấp:

- **Google Cloud Vision** (accuracy 90-95%)
- **Azure Computer Vision** (accuracy 92-96%)

Lợi ích:
- ✅ Tận dụng **free tier** của từng nhà cung cấp
- ✅ Quản lý chi phí tự do
- ✅ Không phụ thuộc backend server
- ✅ Accuracy cao hơn offline OCR (90-95% vs 85-88%)

---

## 🚀 Cách sử dụng

### 1. Truy cập Cloud OCR Settings

Trong ứng dụng Desktop:
1. Click tab **☁️ Cloud OCR** trên thanh navigation
2. Chọn OCR engine mong muốn:
   - **Offline Tesseract** (miễn phí, 75-85%)
   - **Offline EasyOCR** (miễn phí, 88-92%)
   - **Google Cloud Vision** (cloud, 90-95%)
   - **Azure Computer Vision** (cloud, 92-96%)

---

### 2. Lấy Google Cloud Vision API Key

#### Bước 1: Tạo Google Cloud account
- Truy cập: https://console.cloud.google.com
- Đăng nhập hoặc tạo account mới
- Google cung cấp **$300 free credit** cho tài khoản mới

#### Bước 2: Tạo project mới
- Click "Select a project" → "New Project"
- Đặt tên project (ví dụ: "OCR-Desktop-App")
- Click "Create"

#### Bước 3: Enable Cloud Vision API
- Vào **APIs & Services** → **Library**
- Tìm "**Cloud Vision API**"
- Click "**Enable**"

#### Bước 4: Tạo API Key
- Vào **APIs & Services** → **Credentials**
- Click "**Create Credentials**" → "**API key**"
- Copy API key (dạng: `AIzaSyD...`)
- (Tùy chọn) Click "Restrict Key" để giới hạn sử dụng chỉ cho Cloud Vision API

#### Bước 5: Nhập vào app
- Paste API key vào ô **API Key** trong CloudSettings
- Click **🧪 Test API Key** để kiểm tra
- Click **💾 Lưu cài đặt**

#### 💰 Chi phí:
- **Free tier**: 1,000 requests/tháng
- **Sau đó**: $1.50 per 1,000 requests

---

### 3. Lấy Azure Computer Vision API Key

#### Bước 1: Tạo Azure account
- Truy cập: https://portal.azure.com
- Đăng nhập hoặc tạo account mới
- Azure cung cấp **$200 free credit** trong 30 ngày đầu

#### Bước 2: Tạo Computer Vision resource
- Click "**Create a resource**"
- Tìm "**Computer Vision**"
- Click "**Create**"

#### Bước 3: Cấu hình resource
- **Subscription**: Chọn subscription của bạn
- **Resource group**: Tạo mới hoặc chọn existing
- **Region**: Chọn region gần nhất (ví dụ: Southeast Asia)
- **Name**: Đặt tên (ví dụ: "ocr-vision-app")
- **Pricing tier**: Chọn "**Free F0**" (5,000 calls/month miễn phí)
- Click "**Review + create**" → "**Create**"

#### Bước 4: Lấy API Key và Endpoint
- Sau khi tạo xong, vào resource vừa tạo
- Click "**Keys and Endpoint**" ở menu bên trái
- Copy:
  - **KEY 1** hoặc **KEY 2** (API key)
  - **Endpoint** (URL dạng: `https://your-resource.cognitiveservices.azure.com/`)

#### Bước 5: Nhập vào app
- Paste **API Key** vào ô tương ứng
- Paste **Endpoint URL** vào ô tương ứng
- Click **🧪 Test API Key** để kiểm tra
- Click **💾 Lưu cài đặt**

#### 💰 Chi phí:
- **Free tier**: 5,000 requests/tháng
- **Sau đó**: $1.00 per 1,000 requests

---

## 🔒 Bảo mật API Keys

- API keys được lưu trữ **an toàn** trên máy tính của bạn qua `electron-store`
- Dữ liệu được **encrypt** tự động
- Không được gửi lên server nào khác
- Chỉ dùng để gọi trực tiếp Cloud API

---

## 🧪 Test API Key

Sau khi nhập API key, **bắt buộc** phải test trước khi sử dụng:

1. Click nút **🧪 Test API Key**
2. App sẽ gửi 1 request test đến Cloud API
3. Kết quả:
   - ✅ **Thành công**: API key hợp lệ, sẵn sàng sử dụng
   - ❌ **Thất bại**: Kiểm tra lại API key hoặc endpoint

**Lưu ý**: Test không tốn quota (sử dụng ảnh dummy 1x1 pixel)

---

## 📊 So sánh OCR Engines

| Engine | Accuracy | Tốc độ | Chi phí | Internet | Ghi chú |
|--------|----------|--------|---------|----------|---------|
| **Tesseract** | 75-85% | Nhanh (0.5-1s) | Miễn phí | Không | Đa ngôn ngữ, bulk processing |
| **EasyOCR** | 88-92% | Trung bình (7-8s) | Miễn phí | Không | Tốt cho tiếng Việt |
| **VietOCR** | 90-95% | Nhanh (1-2s) | Miễn phí | Không | Chuyên tiếng Việt |
| **Google Cloud Vision** | 90-95% | Rất nhanh (1-2s) | $1.50/1K | Cần | Free 1K/tháng |
| **Azure Vision** | 92-96% | Rất nhanh (1-2s) | $1.00/1K | Cần | Free 5K/tháng |

---

## 💡 Khuyến nghị sử dụng

### Tình huống 1: Bulk processing hàng ngày
→ **EasyOCR** hoặc **VietOCR** (offline, miễn phí)

### Tình huống 2: Documents quan trọng, cần accuracy cao
→ **Google Cloud Vision** hoặc **Azure Vision** (tận dụng free tier)

### Tình huống 3: Ngân sách eo hẹp
→ **VietOCR** (miễn phí, accuracy 90-95%)

### Tình huống 4: Không có internet
→ **Tesseract** / **EasyOCR** / **VietOCR**

---

## 🛠️ Troubleshooting

### Lỗi: "API key không hợp lệ"
- ✅ Kiểm tra lại API key đã copy đúng chưa
- ✅ Xác nhận Cloud Vision API / Computer Vision đã được **enable**
- ✅ (Google) Kiểm tra API key restrictions trong Google Cloud Console

### Lỗi: "Endpoint URL không hợp lệ" (Azure)
- ✅ Endpoint phải có dạng: `https://<resource-name>.cognitiveservices.azure.com/`
- ✅ Không thêm `/` ở cuối URL
- ✅ Kiểm tra region có đúng không

### Lỗi: "Vượt quá quota"
- ✅ (Google) Free tier: 1,000 requests/tháng
- ✅ (Azure) Free tier: 5,000 requests/tháng
- ✅ Kiểm tra usage trong console của nhà cung cấp

### Lỗi: "Không kết nối được"
- ✅ Kiểm tra kết nối internet
- ✅ Tắt VPN hoặc firewall tạm thời
- ✅ Thử lại sau vài phút

---

## 📝 Files liên quan

### Frontend:
- `/desktop-app/src/components/CloudSettings.js` - UI cho Cloud OCR settings
- `/desktop-app/src/App.js` - Routing và tab Cloud OCR

### Backend (Electron):
- `/desktop-app/electron/main.js` - IPC handlers cho API key management
- `/desktop-app/electron/preload.js` - Expose API cho renderer

### Storage:
- API keys được lưu trong `electron-store` (encrypted)
- Location: `~/.config/<app-name>/config.json` (Linux/Mac) hoặc `%APPDATA%/<app-name>/config.json` (Windows)

---

## 🎯 Roadmap

### Hoàn thành:
- ✅ Google Cloud Vision integration
- ✅ Azure Computer Vision integration
- ✅ API key test functionality
- ✅ Encrypted storage

### Đang phát triển:
- ⏳ OpenAI GPT-4 Vision integration
- ⏳ Cost tracking và usage statistics
- ⏳ Batch processing với Cloud OCR

### Tương lai:
- 📋 Tesseract Cloud (AWS Textract)
- 📋 Anthropic Claude Vision
- 📋 Auto-rotate và image preprocessing

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra troubleshooting guide ở trên
2. Xem console logs trong DevTools (Development mode)
3. Liên hệ support team với thông tin:
   - Provider đang dùng (Google/Azure)
   - Error message cụ thể
   - Screenshot (nếu có)

---

**Cập nhật**: 2025-01-XX
**Version**: 1.1.0
