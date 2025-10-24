# EMERGENT_LLM_KEY - Hướng Dẫn Sử Dụng

## 🔑 Key Của Bạn

```
EMERGENT_LLM_KEY=sk-emergent-c9293E676Df8c48F32
```

## ✅ Cách Sử Dụng Trên Railway

### Bước 1: Thêm Vào Backend Variables

1. **Railway Dashboard** → **Backend service** (backend-production-e38f)
2. Tab **"Variables"**
3. Nhấn **"+ New Variable"**
4. Thêm biến:

```
Variable name: EMERGENT_LLM_KEY
Value: sk-emergent-c9293E676Df8c48F32
```

5. **Save** → Backend sẽ tự động restart

### Bước 2: Xóa OPENAI_API_KEY (Nếu Có)

Nếu bạn đã thêm `OPENAI_API_KEY` trước đó:
- Có thể giữ lại hoặc xóa đi
- Backend sẽ ưu tiên dùng `EMERGENT_LLM_KEY` nếu có

## 📋 Environment Variables Hoàn Chỉnh

**Backend cần các biến sau**:

```env
# Database (BẮT BUỘC)
MONGO_URL=mongodb://mongo:xxx@railway.app:xxxx/document_scanner

# JWT Secret (BẮT BUỘC)
JWT_SECRET_KEY=your-random-32-character-secret-key

# LLM Integration (BẮT BUỘC - chọn 1 trong 2)
EMERGENT_LLM_KEY=sk-emergent-c9293E676Df8c48F32
# hoặc
# OPENAI_API_KEY=sk-xxx

# Optional
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

## 💡 Về EMERGENT_LLM_KEY

**Đây là gì?**
- Universal key của Emergent platform
- Hoạt động với OpenAI, Anthropic, Google models
- Không cần API key riêng từ OpenAI

**Ưu điểm**:
- ✅ Không cần đăng ký OpenAI
- ✅ Không cần credit card
- ✅ Dễ sử dụng
- ✅ Được quản lý tự động

**Lưu ý**:
- Key này có giới hạn budget (usage quota)
- Nếu hết quota, cần nạp thêm trong Emergent dashboard
- Xem budget: Profile → Universal Key → Balance

## 🎯 Các Bước Tiếp Theo

### 1. Thêm EMERGENT_LLM_KEY vào Backend
```
Railway → Backend → Variables → Add:
EMERGENT_LLM_KEY=sk-emergent-c9293E676Df8c48F32
```

### 2. Đảm Bảo Có Đủ Các Biến Khác

**MongoDB** (nếu chưa có):
```
MONGO_URL=mongodb://mongo:password@host:port/document_scanner
```

**JWT Secret** (nếu chưa có):
```
JWT_SECRET_KEY=tao-chuoi-ngau-nhien-32-ky-tu-abc123xyz
```

### 3. Đợi Backend Restart

- Sau khi add biến, backend tự động restart
- Đợi 1-2 phút

### 4. Kiểm Tra Logs

Railway → Backend → Logs → Xem có lỗi không:
```
✅ INFO: Application startup complete
✅ INFO: Connected to MongoDB
```

### 5. Test Setup Admin

Truy cập:
```
https://backend-production-e38f.up.railway.app/api/setup-admin
```

Kết quả mong đợi:
```json
{"message": "Admin user created successfully", "username": "admin"}
```

## 🔧 Template Đầy Đủ

Copy và điền vào Railway Backend Variables:

```env
# === BẮT BUỘC ===

# MongoDB (lấy từ MongoDB service)
MONGO_URL=mongodb://mongo:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/document_scanner

# JWT Secret (tự tạo chuỗi ngẫu nhiên 32+ ký tự)
JWT_SECRET_KEY=your-random-secret-key-32-characters-or-more

# Emergent LLM Key (đã có sẵn)
EMERGENT_LLM_KEY=sk-emergent-c9293E676Df8c48F32

# === TÙY CHỌN (Khuyến nghị) ===

MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
DB_NAME=document_scanner_db
CORS_ORIGINS=*
```

## ⚠️ Bảo Mật

**Không chia sẻ key này công khai!**
- Đây là key cá nhân của bạn
- Chỉ thêm vào Railway Variables (private)
- Không commit vào Git
- Không gửi cho người khác

## 🆘 Nếu Key Hết Budget

Nếu thấy lỗi "Insufficient credits" hoặc "Quota exceeded":

1. Vào Emergent Dashboard
2. Profile → Universal Key → Add Balance
3. Nạp thêm tiền
4. Hoặc enable Auto Top-up

---

**Key của bạn**: `sk-emergent-c9293E676Df8c48F32`

**Thêm ngay vào Railway Backend Variables để bắt đầu!**
