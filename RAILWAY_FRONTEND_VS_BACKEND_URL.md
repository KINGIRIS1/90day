# ⚠️ Phân Biệt Frontend URL và Backend URL

## 🔍 Vấn Đề Hiện Tại

Bạn đang truy cập: `https://sohoavpdkct.up.railway.app/api/setup-admin`

**Lỗi 404 "Not Found"** vì đây là **Frontend URL** (React app), không phải Backend URL (FastAPI).

## 📊 Sự Khác Biệt

### Frontend Service (React)
- **URL bạn đã có**: `https://sohoavpdkct.up.railway.app`
- **Chức năng**: Hiển thị giao diện web (HTML, CSS, JavaScript)
- **Không có** `/api/setup-admin` endpoint
- **Port**: 3000 (internal)

### Backend Service (FastAPI)
- **URL cần tìm**: `https://backend-production-XXXX.up.railway.app` (chưa biết)
- **Chức năng**: Xử lý logic, database, API endpoints
- **CÓ** `/api/setup-admin` endpoint ✅
- **Port**: 8001 (internal)

## ✅ Cách Tìm Backend URL

### Bước 1: Vào Railway Dashboard

1. Đăng nhập Railway: https://railway.app
2. Chọn project của bạn (có tên "Document Scanner" hoặc tương tự)

### Bước 2: Xác Định Backend Service

Trong project, bạn sẽ thấy **nhiều services**:

```
Your Project
├── MongoDB (Database)
├── backend (hoặc tên khác) ← CẦN SERVICE NÀY
└── sohoavpdkct (Frontend) ← Đây là service bạn đã biết
```

**Backend service** thường có tên:
- `backend`
- `backend-production`
- `document-scanner-backend`
- Hoặc tên repository với Root Directory = `backend`

### Bước 3: Lấy Backend URL

1. **Click vào Backend service** (KHÔNG phải sohoavpdkct)
2. Vào tab **"Settings"**
3. Scroll xuống phần **"Networking"** hoặc **"Domains"**
4. Bạn sẽ thấy một hoặc nhiều URLs:
   ```
   https://backend-production-abcd.up.railway.app
   hoặc
   https://xxxx-backend.up.railway.app
   ```
5. **Copy URL này** - đây là Backend URL!

### Bước 4: Truy Cập Backend Setup Admin

Sử dụng Backend URL vừa tìm được:

```
https://BACKEND-URL-CUA-BAN/api/setup-admin
```

**Ví dụ**:
```
https://backend-production-abcd.up.railway.app/api/setup-admin
```

**Kết quả mong đợi**:
```json
{
  "message": "Admin user created successfully",
  "username": "admin"
}
```

## 🔧 Nếu Không Tìm Thấy Backend Service

### Trường Hợp 1: Backend Chưa Deploy

Nếu trong Railway project chỉ thấy **1 service** (sohoavpdkct - frontend):
- Backend chưa được deploy!
- Cần deploy backend theo hướng dẫn trong `RAILWAY_NEXT_STEPS.md`

### Trường Hợp 2: Backend Service Không Có Domain

Nếu thấy backend service nhưng không có domain/URL:

1. Click vào Backend service
2. Tab "Settings" → Phần "Networking"
3. Nhấn **"Generate Domain"**
4. Railway sẽ tạo public URL
5. Đợi vài giây → Copy URL

## 📝 Sau Khi Có Backend URL

### 1. Tạo Admin User

Truy cập:
```
https://BACKEND-URL/api/setup-admin
```

### 2. Cập Nhật Frontend Environment Variable

Để frontend kết nối được backend:

1. Railway → **Frontend service (sohoavpdkct)**
2. Tab **"Variables"**
3. Thêm/cập nhật:
   ```
   REACT_APP_BACKEND_URL=https://BACKEND-URL
   ```
4. Save → Frontend sẽ redeploy (3-5 phút)

### 3. Test Kết Nối

1. Đợi frontend redeploy xong
2. Truy cập: `https://sohoavpdkct.up.railway.app`
3. Thử đăng nhập:
   - Username: `admin`
   - Password: `Thommit@19`

## 🎯 Quick Checklist

- [ ] Tìm được Backend service trong Railway project
- [ ] Backend service có status "Active" (màu xanh)
- [ ] Lấy được Backend URL từ backend service → Settings → Domains
- [ ] Truy cập `https://BACKEND-URL/api/setup-admin` → Thấy JSON success
- [ ] Cập nhật `REACT_APP_BACKEND_URL` trong frontend variables
- [ ] Đợi frontend redeploy
- [ ] Test login từ frontend URL

## 🆘 Nếu Vẫn Không Tìm Thấy

Hãy screenshot Railway project dashboard của bạn (nơi hiển thị tất cả services) và gửi cho tôi. Tôi sẽ giúp xác định backend service.

---

**TÓM TẮT**:
- ✅ Frontend URL (đã có): `https://sohoavpdkct.up.railway.app`
- ❓ Backend URL (cần tìm): `https://backend-?????.up.railway.app`
- 🎯 Endpoint cần truy cập: `Backend-URL + /api/setup-admin`
