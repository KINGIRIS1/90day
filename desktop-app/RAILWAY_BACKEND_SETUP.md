# 🚂 Railway Backend Configuration

## Railway Backend URL đã được cấu hình

**URL:** `https://sohoavpdkct.up.railway.app`

Desktop app đã được cấu hình để sử dụng Railway backend theo mặc định.

---

## Cách sử dụng Cloud Boost với Railway

### 1. **Tự động (Default)**
- Desktop app đã tự động sử dụng Railway URL
- Không cần cấu hình gì thêm
- Nhấn nút "☁️ Cloud" để sử dụng Cloud Boost

### 2. **Kiểm tra cấu hình**
1. Mở Desktop App
2. Vào **Settings/Cài đặt** (icon ⚙️)
3. Xem phần "Backend URL"
4. Nên hiển thị: `https://sohoavpdkct.up.railway.app`

### 3. **Đổi Backend URL (nếu cần)**
1. Vào Settings
2. Sửa field "Backend URL"
3. Nhập URL mới (ví dụ: `https://your-new-backend.railway.app`)
4. Nhấn "Lưu cài đặt"

---

## API Endpoints trên Railway Backend

Desktop app sẽ gọi các endpoints sau:

```
POST https://sohoavpdkct.up.railway.app/api/scan-document-public
```

### Yêu cầu Backend phải có:

✅ **FastAPI endpoints:**
- `POST /api/scan-document-public` - Scan single document
- `POST /api/process-batch` - Batch processing (optional)

✅ **CORS configuration:**
```python
CORS_ORIGINS="*"  # Cho phép desktop app kết nối
```

✅ **Environment variables:**
- `OPENAI_API_KEY` hoặc `EMERGENT_LLM_KEY` - Để dùng GPT-4
- `MONGO_URL` - MongoDB connection
- `DB_NAME` - Database name

---

## Test Backend Connection

### Từ Desktop App:
1. Mở app
2. Chọn một file ảnh
3. Nhấn nút "☁️ Cloud"
4. Xem kết quả

### Từ Command Line:
```bash
# Test health endpoint
curl https://sohoavpdkct.up.railway.app/api/health

# Test scan endpoint
curl -X POST https://sohoavpdkct.up.railway.app/api/scan-document-public \
  -F "file=@/path/to/your/image.jpg"
```

---

## Troubleshooting

### ❌ "Backend URL not configured"
- Vào Settings và kiểm tra URL
- Đảm bảo có format: `https://sohoavpdkct.up.railway.app`

### ❌ "Network Error" / "Timeout"
- Kiểm tra Railway backend có đang chạy không
- Kiểm tra internet connection
- Thử test với curl command

### ❌ "500 Internal Server Error"
- Kiểm tra Railway logs
- Đảm bảo OPENAI_API_KEY được set đúng
- Kiểm tra MongoDB connection

---

## Chi phí Railway

**Free Tier:**
- $5 credit/tháng
- ~500 hours uptime
- Đủ cho dev và test

**Paid Tier:**
- $5/tháng cho hobby project
- Unlimited uptime
- Better performance

---

## Backup Configuration

Nếu muốn dùng backend khác, có thể thay đổi trong Settings:

| Backend | URL | Use Case |
|---------|-----|----------|
| **Railway** | `https://sohoavpdkct.up.railway.app` | Production (Always-on) |
| **Emergent** | `https://docuscanviet.preview.emergentagent.com` | Development |
| **Localhost** | `http://localhost:8001` | Local testing |

---

## Notes

- Railway backend phải có prefix `/api` cho tất cả routes
- Desktop app tự động thêm `/api/scan-document-public` vào URL
- Không cần authentication token cho public endpoint
- Railway URL được set làm default trong code
