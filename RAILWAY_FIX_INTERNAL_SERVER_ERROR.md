# Fix Lỗi "Internal Server Error" Trên Backend

## ✅ Backend URL Đã Tìm Thấy
`https://backend-production-e38f.up.railway.app`

## ⚠️ Lỗi: Internal Server Error

Lỗi 500 "Internal Server Error" nghĩa là:
- ✅ Backend đang chạy
- ❌ Có lỗi trong code hoặc database connection

## 🔍 Nguyên Nhân Thường Gặp

### 1. MongoDB Connection Chưa Được Cấu Hình (90% trường hợp)

Backend cần biến `MONGO_URL` để kết nối database.

### 2. Environment Variables Còn Thiếu

Backend cần nhiều biến môi trường để chạy.

### 3. MongoDB Service Chưa Được Tạo

Nếu chưa có MongoDB trong Railway project.

## ✅ Các Bước Fix

### Bước 1: Kiểm Tra Backend Logs

**Quan trọng nhất** - logs sẽ cho biết lỗi chính xác!

1. **Railway Dashboard** → **Backend service** (backend-production-e38f)
2. Tab **"Logs"** (hoặc "Deployments" → Latest deployment → Logs)
3. **Scroll xuống cuối** để xem logs mới nhất
4. Tìm các dòng có chữ **"ERROR"** hoặc **"Exception"**

**Các lỗi thường thấy**:

**A. MongoDB Connection Error:**
```
ERROR: Cannot connect to MongoDB
ERROR: No value for MONGO_URL
ServerSelectionTimeoutError: connection refused
```
→ **Fix**: Cần thêm biến `MONGO_URL`

**B. Missing Environment Variables:**
```
KeyError: 'JWT_SECRET_KEY'
KeyError: 'OPENAI_API_KEY'
```
→ **Fix**: Cần thêm các biến còn thiếu

**C. Import Errors:**
```
ModuleNotFoundError: No module named 'xxx'
```
→ **Fix**: Package chưa được cài (thường không xảy ra nếu build thành công)

### Bước 2: Kiểm Tra Environment Variables Của Backend

1. **Railway Dashboard** → **Backend service**
2. Tab **"Variables"**
3. Kiểm tra các biến **BẮT BUỘC**:

```
✅ Cần có:
MONGO_URL=mongodb://...
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-xxx (hoặc EMERGENT_LLM_KEY)
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

### Bước 3: Thêm MongoDB Service (Nếu Chưa Có)

**Kiểm tra MongoDB**:
1. Railway Dashboard → Project của bạn
2. Có service tên "MongoDB" hoặc "Postgres" không?

**Nếu CHƯA có MongoDB**:

1. Trong project, nhấn **"+ New"**
2. Chọn **"Database"** → **"Add MongoDB"**
3. Railway sẽ tự động provision MongoDB
4. Đợi vài giây đến khi status = "Active"

**Lấy MongoDB URL**:

1. Click vào **MongoDB service**
2. Tab **"Variables"**
3. Tìm biến có tên **`MONGO_URL`** hoặc **`DATABASE_URL`** hoặc **`MONGO_PRIVATE_URL`**
4. **Copy giá trị** (dạng: `mongodb://mongo:password@...`)

### Bước 4: Cấu Hình Backend Environment Variables

1. **Railway Dashboard** → **Backend service**
2. Tab **"Variables"**
3. Click **"+ New Variable"** hoặc **"Raw Editor"**

**Thêm các biến sau**:

```env
MONGO_URL=mongodb://mongo:xxxxx@containers-us-west-xxxx.railway.app:6379/document_scanner
JWT_SECRET_KEY=thay-bang-chuoi-ngau-nhien-dai-32-ky-tu-abc123xyz
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

**Giải thích từng biến**:

**A. MONGO_URL** (BẮT BUỘC):
- Copy từ MongoDB service (Bước 3)
- Thêm `/document_scanner` vào cuối nếu chưa có
- Ví dụ: `mongodb://mongo:abc123@railway.app:6379/document_scanner`

**B. JWT_SECRET_KEY** (BẮT BUỘC):
- Tạo chuỗi ngẫu nhiên dài ít nhất 32 ký tự
- Dùng lệnh: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- Hoặc tự tạo: `mySuper$ecret123KeyForJWT2024RandomString`

**C. OPENAI_API_KEY** (BẮT BUỘC cho OCR):
- API key của OpenAI (nếu bạn có)
- Hoặc dùng **EMERGENT_LLM_KEY** nếu bạn đang dùng Emergent platform

**D. Các biến khác** (Khuyến nghị):
```
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

### Bước 5: Save và Restart Backend

1. Sau khi thêm tất cả biến, nhấn **"Save"** hoặc **"Add"**
2. Backend sẽ **tự động restart** (hoặc redeploy)
3. Đợi 1-2 phút để backend khởi động lại

### Bước 6: Kiểm Tra Logs Sau Khi Restart

1. Tab **"Logs"** của backend service
2. Xem các dòng mới:
   ```
   ✅ INFO: Uvicorn running on 0.0.0.0:8001
   ✅ INFO: Application startup complete
   ✅ INFO: Connected to MongoDB
   ```

3. Nếu thấy các dòng trên → Backend đã sẵn sàng!

### Bước 7: Thử Lại Tạo Admin

Truy cập lại:
```
https://backend-production-e38f.up.railway.app/api/setup-admin
```

**Kết quả mong đợi**:
```json
{
  "message": "Admin user created successfully",
  "username": "admin"
}
```

## 🎯 Quick Checklist

- [ ] Đã xem backend logs để xác định lỗi
- [ ] Đã có MongoDB service trong project
- [ ] Đã lấy MONGO_URL từ MongoDB service
- [ ] Đã thêm biến `MONGO_URL` vào backend
- [ ] Đã thêm biến `JWT_SECRET_KEY` vào backend
- [ ] Đã thêm biến `OPENAI_API_KEY` hoặc `EMERGENT_LLM_KEY` vào backend
- [ ] Backend đã restart sau khi thêm biến
- [ ] Logs hiển thị "Application startup complete"
- [ ] Truy cập `/api/setup-admin` → Thấy JSON success

## 🆘 Nếu Vẫn Lỗi

**Hãy gửi cho tôi**:
1. **Backend logs** (copy 20-30 dòng cuối trong tab Logs)
2. **Screenshot các biến** trong Backend → Variables (có thể che password)
3. Tôi sẽ giúp debug chính xác hơn

## 📝 Template Environment Variables

Để dễ dàng, copy template này:

```env
# MongoDB Connection (BẮT BUỘC - lấy từ MongoDB service)
MONGO_URL=mongodb://mongo:password@host:port/document_scanner

# JWT Secret (BẮT BUỘC - tạo ngẫu nhiên)
JWT_SECRET_KEY=your-random-32-character-secret-key-here-abc123xyz

# OpenAI API (BẮT BUỘC cho OCR - hoặc dùng EMERGENT_LLM_KEY)
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (Khuyến nghị)
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
DB_NAME=document_scanner_db
CORS_ORIGINS=*
```

---

**90% lỗi "Internal Server Error" là do thiếu `MONGO_URL`!**

Kiểm tra logs ngay để biết lỗi cụ thể!
