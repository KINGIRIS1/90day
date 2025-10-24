# Hướng Dẫn Deploy Railway - TÓM TẮT NHANH

## 🎯 6 Bước Chính - Deploy Trong 15 Phút

### Bước 1️⃣: Tạo Project
- Vào https://railway.app → Login
- "New Project" → "Deploy from GitHub repo"
- Chọn repository code của bạn

### Bước 2️⃣: Thêm MongoDB
- Trong project → "+ New" → "Database" → "Add MongoDB"
- Copy biến `MONGO_URL` (tab Variables của MongoDB)

### Bước 3️⃣: Deploy Backend
**Cài đặt**:
- "+ New" → chọn repo
- Settings → **Root Directory = `backend`** ⚠️ QUAN TRỌNG
- Tab Variables → Thêm:
```
MONGO_URL=(paste từ bước 2, thêm /document_scanner vào cuối)
JWT_SECRET_KEY=(tạo chuỗi ngẫu nhiên dài 32+ ký tự)
OPENAI_API_KEY=(key của bạn)
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
```
- Đợi deploy xong → Copy Backend URL

### Bước 4️⃣: Deploy Frontend
**Cài đặt**:
- "+ New" → chọn repo (cùng repo)
- Settings → **Root Directory = `frontend`** ⚠️ QUAN TRỌNG  
- Tab Variables → Thêm:
```
REACT_APP_BACKEND_URL=(Backend URL từ bước 3)
```
- Đợi deploy xong → Copy Frontend URL

### Bước 5️⃣: Tạo Admin
- Mở trình duyệt: `https://backend-url/api/setup-admin`
- Thấy `{"message": "Admin user created successfully"}` là OK

### Bước 6️⃣: Kiểm Tra
- Vào Frontend URL
- Login: `admin` / `Thommit@19`
- Test upload ảnh và scan

## ✅ XONG! Ứng dụng đã chạy trên Railway

---

## ⚠️ Lỗi Thường Gặp

### "pip: command not found" HOẶC "undefined variable 'pip'"
✅ Đã fix rồi! File `backend/nixpacks.toml` đã được cập nhật:
- Dùng `python3 -m pip` thay vì `pip` trực tiếp
- Không thêm `pip` vào nixPkgs (vì pip có sẵn trong Python)
- Push code mới nhất lên GitHub và rebuild

### Frontend không kết nối backend
✅ Kiểm tra:
- `REACT_APP_BACKEND_URL` có đúng Backend URL không?
- URL có `https://` không? Có dấu `/` cuối không? (phải bỏ `/`)

### Cannot connect to MongoDB  
✅ Kiểm tra:
- `MONGO_URL` có thêm `/document_scanner` ở cuối chưa?
- MongoDB service có đang chạy không? (màu xanh)

---

## 📝 Template Environment Variables

### Backend Variables (copy và điền):
```env
MONGO_URL=mongodb://mongo:xxx@containers-us-west-xxx.railway.app:7xxx/document_scanner
JWT_SECRET_KEY=thay-bang-chuoi-ngau-nhien-dai-32-ky-tu-tai-day-abc123xyz789
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

### Frontend Variables (copy và điền):
```env
REACT_APP_BACKEND_URL=https://your-backend-name.up.railway.app
```

---

## 🔑 Cách Tạo JWT Secret Key Mạnh

**Option 1**: Dùng Python
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2**: Dùng OpenSSL
```bash
openssl rand -base64 32
```

**Option 3**: Tự tạo chuỗi ngẫu nhiên dài (ít nhất 32 ký tự)

---

## 💰 Chi Phí Dự Kiến

**Railway Developer Plan** (~$20/tháng):
- ✅ Bao gồm nhiều services
- ✅ Đủ cho 30+ người dùng đồng thời
- ✅ Unlimited deployment
- ✅ SSL/HTTPS miễn phí

**Hoặc Starter Plan** (~$15-30/tháng):
- Backend: $5-10
- Frontend: $5-10  
- MongoDB: $5-15

---

## 📚 Tài Liệu Đầy Đủ

Muốn hướng dẫn chi tiết hơn? Xem:
- **`/app/RAILWAY_HUONG_DAN_TIENG_VIET.md`** ← Hướng dẫn đầy đủ tiếng Việt
- **`/app/RAILWAY_DEPLOYMENT_GUIDE.md`** ← Full guide (English)
- **`/app/RAILWAY_DEPLOYMENT_CHECKLIST.md`** ← Checklist đầy đủ

---

## 🎯 Root Directory - QUAN TRỌNG!

Đây là lỗi thường gặp nhất! Phải set đúng:

**Backend Service**:
```
Settings → Root Directory → nhập: backend
```

**Frontend Service**:
```
Settings → Root Directory → nhập: frontend
```

❌ **KHÔNG** nhập `/backend` hay `/frontend` (không có dấu `/` đầu)
✅ Chỉ nhập `backend` hoặc `frontend`

---

## 🚀 Sau Khi Deploy

### Bảo mật:
- [ ] Đổi password admin ngay
- [ ] Cập nhật CORS trong `backend/server.py`

### Test:
- [ ] Upload ảnh đơn
- [ ] Batch upload  
- [ ] Folder scan (ZIP)
- [ ] PDF export

### Giám sát:
- Vào Railway → Service → Tab "Logs" để xem logs
- Tab "Metrics" để xem CPU/Memory usage

---

## 🆘 Cần Trợ Giúp?

1. **Xem logs**: Railway Dashboard → Service → Tab "Logs"
2. **Rebuild**: Service → Settings → "Redeploy"
3. **Railway Support**: https://help.railway.app
4. **Docs đầy đủ**: Xem file `RAILWAY_HUONG_DAN_TIENG_VIET.md`

---

**Tóm tắt lại**: 
1. Tạo project → 2. Thêm MongoDB → 3. Deploy backend (root: `backend`) → 4. Deploy frontend (root: `frontend`) → 5. Setup admin → 6. Test!

🎉 **15 phút là xong!**
