# 🎉 Backend Đã Active - Các Bước Tiếp Theo

## ✅ Backend Đã Thành Công!

Backend của bạn đã chạy trên Railway! 

## 📋 Các Bước Tiếp Theo

### Bước 1: Lấy Backend URL

1. Vào Railway Dashboard → Chọn Backend service
2. Tab **"Settings"** → Phần **"Domains"**
3. Nếu chưa có domain, nhấn **"Generate Domain"**
4. **Copy URL** (dạng: `https://your-backend-xyz.up.railway.app`)
5. **LƯU LẠI URL NÀY** - cần dùng cho frontend!

### Bước 2: Deploy Frontend

#### A. Tạo Frontend Service (nếu chưa có)

1. Trong Railway project, nhấn **"+ New"**
2. Chọn **"GitHub Repo"** (cùng repository với backend)
3. Service mới sẽ được tạo

#### B. Cấu Hình Frontend Service

1. **Nhấn vào Frontend service** vừa tạo
2. **Settings** → Tìm **"Root Directory"**
3. Nhập: `frontend` (không có dấu `/`)
4. **Save**

#### C. Set Environment Variable cho Frontend

1. Tab **"Variables"** của frontend service
2. Nhấn **"+ New Variable"**
3. Thêm biến:

```
REACT_APP_BACKEND_URL=https://your-backend-xyz.up.railway.app
```

⚠️ **QUAN TRỌNG**: 
- Thay `https://your-backend-xyz.up.railway.app` bằng Backend URL thực tế từ Bước 1
- **KHÔNG** có dấu `/` ở cuối
- **PHẢI** có `https://` ở đầu

4. Nhấn **"Add"** hoặc **"Save"**

#### D. Đợi Frontend Deploy

Railway sẽ tự động build frontend:
- `yarn install` → `yarn build` → `serve -s build`
- Xem logs trong tab **"Deployments"** hoặc **"Logs"**
- Đợi đến khi thấy **"Success"** hoặc **"Running"**

#### E. Lấy Frontend URL

1. Frontend service → Tab **"Settings"**
2. Phần **"Domains"**
3. Nhấn **"Generate Domain"** nếu chưa có
4. **Copy Frontend URL** (dạng: `https://your-app-xyz.up.railway.app`)

### Bước 3: Khởi Tạo Admin User

Sau khi frontend deploy xong:

1. Mở trình duyệt
2. Truy cập: `https://your-backend-url.up.railway.app/api/setup-admin`
3. Bạn sẽ thấy JSON response:
   ```json
   {"message": "Admin user created successfully", "username": "admin"}
   ```

### Bước 4: Test Ứng Dụng

1. **Truy cập frontend**: Mở `https://your-app-xyz.up.railway.app`
2. **Đăng nhập**:
   - Username: `admin`
   - Password: `Thommit@19`
3. **Test các tính năng**:
   - ✅ Upload ảnh đơn lẻ
   - ✅ Quét và nhận diện (OCR)
   - ✅ Tự động đặt tên theo mã viết tắt
   - ✅ Xuất PDF
   - ✅ Upload nhiều ảnh (batch)
   - ✅ Quét thư mục (ZIP)
   - ✅ Xem lịch sử

### Bước 5: Bảo Mật (Quan Trọng!)

#### A. Đổi Mật Khẩu Admin
- Đăng nhập với `admin/Thommit@19`
- Vào Admin Panel
- Đổi mật khẩu ngay lập tức

#### B. Cập Nhật CORS (Production)

Hiện tại backend cho phép tất cả origins (`*`). Để bảo mật:

1. SSH vào code hoặc edit trên GitHub
2. Mở file `backend/server.py`
3. Tìm phần CORS middleware (khoảng dòng 50-60):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Đổi dòng này
    ...
)
```

4. Đổi thành:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app-xyz.up.railway.app",  # Frontend URL thật
        "http://localhost:3000",  # Cho development (optional)
    ],
    ...
)
```

5. Commit và push:
```bash
git add backend/server.py
git commit -m "Update CORS for production"
git push origin main
```

Railway sẽ tự động redeploy backend.

## 🎯 Checklist Hoàn Thành

- [ ] Backend đã active ✅ (Xong rồi!)
- [ ] Đã lấy Backend URL
- [ ] Frontend service đã tạo
- [ ] Frontend Root Directory = `frontend`
- [ ] Frontend environment variable đã set (`REACT_APP_BACKEND_URL`)
- [ ] Frontend đã deploy thành công
- [ ] Đã lấy Frontend URL
- [ ] Admin user đã khởi tạo (`/api/setup-admin`)
- [ ] Đã test đăng nhập
- [ ] Đã test upload và scan ảnh
- [ ] Đã đổi password admin
- [ ] Đã cập nhật CORS cho production

## 📊 Thông Tin Lưu Trữ

**Dự án Railway của bạn**:
```
Project: Document Scanner
├── MongoDB Service
│   └── Internal connection
├── Backend Service ✅
│   ├── URL: https://_____________.up.railway.app
│   └── Status: Active
└── Frontend Service
    ├── URL: https://_____________.up.railway.app
    └── Status: (đang deploy...)
```

**Thông tin đăng nhập**:
```
Frontend URL: https://_____________.up.railway.app
Username: admin
Password: Thommit@19 (đổi ngay sau khi login!)
```

## ❓ Xử Lý Sự Cố

### Frontend không kết nối được backend

**Kiểm tra**:
1. Frontend có biến `REACT_APP_BACKEND_URL` chưa?
2. Backend URL có đúng không? (có `https://`, không có `/` cuối)
3. Backend có đang chạy không? (Status = Active)
4. Xem frontend logs có lỗi CORS không?

**Fix**:
- Đảm bảo CORS trong `backend/server.py` cho phép frontend domain
- Restart frontend service nếu cần

### Admin setup không hoạt động

**Kiểm tra**:
1. Truy cập đúng backend URL chưa? (không phải frontend URL)
2. Đường dẫn: `/api/setup-admin` (có `/api/`)

**Fix**:
- Đảm bảo MongoDB service đang chạy
- Kiểm tra backend logs: Railway → Backend service → Logs

### Upload ảnh bị lỗi 502/504

**Nguyên nhân**: Timeout khi xử lý ảnh lớn

**Fix**:
1. Vào Backend service → Variables
2. Tăng `UVICORN_TIMEOUT=600` (10 phút)
3. Service sẽ tự restart

## 🚀 Hoàn Thành!

Sau khi làm xong các bước trên, ứng dụng của bạn đã:
- ✅ Chạy trên Railway (production)
- ✅ Hỗ trợ 30+ người dùng đồng thời
- ✅ SSL/HTTPS tự động
- ✅ Auto-deploy khi push code mới

**Chi phí dự kiến**: ~$15-35/tháng (Developer Plan khuyến nghị)

---

**Cần trợ giúp?** Xem các file hướng dẫn:
- `RAILWAY_HUONG_DAN_TIENG_VIET.md` - Hướng dẫn đầy đủ
- `RAILWAY_TOM_TAT.md` - Tóm tắt nhanh
- `RAILWAY_SO_DO.md` - Sơ đồ kiến trúc
