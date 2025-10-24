# Hướng Dẫn Deploy Lên Railway - Tiếng Việt

## ✅ Đã Sửa Lỗi "pip: command not found"

Lỗi đã được khắc phục hoàn toàn. Các file cấu hình đã được cập nhật và sẵn sàng để deploy.

## Bước 1: Chuẩn Bị Tài Khoản Railway

### 1.1 Đăng ký Railway
1. Truy cập: https://railway.app
2. Nhấn "Login" → Chọn "Sign up with GitHub" (khuyến nghị)
3. Hoặc đăng ký bằng email

### 1.2 Chuẩn bị code trên GitHub
Nếu chưa có code trên GitHub:
```bash
# Tạo repository mới trên GitHub
# Sau đó push code:
git add .
git commit -m "Chuẩn bị deploy lên Railway"
git push origin main
```

## Bước 2: Tạo Project Trên Railway

1. Đăng nhập Railway → Vào Dashboard
2. Nhấn nút **"New Project"** (góc trên bên phải)
3. Chọn **"Deploy from GitHub repo"**
4. Chọn repository của bạn từ danh sách

## Bước 3: Thêm MongoDB Database

1. Trong project vừa tạo, nhấn nút **"+ New"**
2. Chọn **"Database"** → **"Add MongoDB"**
3. Railway sẽ tự động tạo MongoDB instance
4. Vào service MongoDB → Tab **"Variables"**
5. Tìm và **copy giá trị của biến MONGO_URL** (dạng: `mongodb://mongo:xxxxx@...`)
   - Lưu lại giá trị này, sẽ dùng ở bước sau

## Bước 4: Deploy Backend (Python/FastAPI)

### 4.1 Tạo Backend Service
1. Trong project, nhấn **"+ New"** → **"GitHub Repo"**
2. Chọn lại repository của bạn (same repo as before)

### 4.2 Cấu Hình Root Directory
⚠️ **QUAN TRỌNG** - Đây là bước dễ nhầm nhất:
1. Nhấn vào service backend vừa tạo
2. Vào tab **"Settings"**
3. Tìm phần **"Build & Deploy"** hoặc **"Service Settings"**
4. Tìm ô **"Root Directory"** hoặc **"Source Directory"**
5. Nhập: `backend` (không có dấu `/` ở đầu)
6. Nhấn **"Save"** hoặc Railway sẽ tự động save

### 4.3 Cấu Hình Environment Variables (Biến môi trường)
1. Vào tab **"Variables"** của backend service
2. Nhấn **"+ New Variable"** hoặc **"Raw Editor"**
3. Thêm các biến sau:

```env
MONGO_URL=mongodb://mongo:password@xxxxx.railway.app:6379/document_scanner
JWT_SECRET_KEY=chuoi-bi-mat-rat-dai-va-phuc-tap-thay-doi-truoc-khi-su-dung
OPENAI_API_KEY=sk-xxxxxxx
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

**Giải thích từng biến**:
- `MONGO_URL`: Copy từ MongoDB service ở Bước 3, thêm `/document_scanner` vào cuối
- `JWT_SECRET_KEY`: Tạo chuỗi ngẫu nhiên dài (ít nhất 32 ký tự) để bảo mật
- `OPENAI_API_KEY`: API key của OpenAI (hoặc dùng Emergent LLM Key nếu bạn có)
- Các biến còn lại: Giữ nguyên như trên

**Cách tạo JWT_SECRET_KEY mạnh**:
```bash
# Chạy lệnh này trên máy tính:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.4 Deploy Backend
1. Sau khi cấu hình xong, Railway sẽ **tự động deploy**
2. Xem logs để theo dõi quá trình build:
   - Vào service → Tab **"Deployments"** → Nhấn vào deployment mới nhất
   - Hoặc tab **"Logs"** để xem realtime
3. Đợi đến khi thấy: ✅ **"Success"** hoặc **"Running"**

### 4.5 Lấy Backend URL
1. Vào backend service → Tab **"Settings"**
2. Tìm phần **"Domains"** hoặc **"Networking"**
3. Nhấn **"Generate Domain"** nếu chưa có
4. **Copy URL** (dạng: `https://abc-xyz-production.up.railway.app`)
5. Lưu lại URL này để dùng cho frontend

## Bước 5: Deploy Frontend (React)

### 5.1 Tạo Frontend Service
1. Trong project, nhấn **"+ New"** → **"GitHub Repo"**
2. Chọn lại repository (cùng repo với backend)

### 5.2 Cấu Hình Root Directory
⚠️ **QUAN TRỌNG**:
1. Nhấn vào service frontend vừa tạo
2. Vào tab **"Settings"**
3. Tìm ô **"Root Directory"**
4. Nhập: `frontend` (không có dấu `/` ở đầu)
5. Nhấn **"Save"**

### 5.3 Cấu Hình Environment Variable
1. Vào tab **"Variables"** của frontend service
2. Thêm biến:

```env
REACT_APP_BACKEND_URL=https://abc-xyz-production.up.railway.app
```

⚠️ **Lưu ý**:
- Thay `https://abc-xyz-production.up.railway.app` bằng **Backend URL** từ Bước 4.5
- **KHÔNG** có dấu `/` ở cuối URL
- **PHẢI** có `https://` ở đầu

### 5.4 Deploy Frontend
1. Railway sẽ tự động deploy sau khi save
2. Xem logs để theo dõi:
   - Build sẽ chạy: `yarn install` → `yarn build`
   - Sau đó start: `serve -s build`
3. Đợi đến khi thấy: ✅ **"Success"** hoặc **"Running"**

### 5.5 Lấy Frontend URL
1. Vào frontend service → Tab **"Settings"**
2. Tìm phần **"Domains"**
3. Nhấn **"Generate Domain"** nếu chưa có
4. **Copy URL** (dạng: `https://xyz-abc-production.up.railway.app`)
5. Đây là URL chính để truy cập ứng dụng

## Bước 6: Khởi Tạo Admin User

### 6.1 Tạo tài khoản admin
1. Mở trình duyệt
2. Truy cập: `https://backend-url-cua-ban.up.railway.app/api/setup-admin`
   - Thay `backend-url-cua-ban` bằng Backend URL thực tế
3. Bạn sẽ thấy thông báo JSON:
   ```json
   {"message": "Admin user created successfully", "username": "admin"}
   ```

### 6.2 Thông tin đăng nhập mặc định
```
Username: admin
Password: Thommit@19
```

⚠️ **QUAN TRỌNG**: Đổi mật khẩu ngay sau khi đăng nhập lần đầu!

## Bước 7: Kiểm Tra Ứng Dụng

### 7.1 Truy cập ứng dụng
1. Mở trình duyệt
2. Truy cập Frontend URL (từ Bước 5.5)
3. Bạn sẽ thấy trang đăng nhập

### 7.2 Đăng nhập
1. Nhập username: `admin`
2. Nhập password: `Thommit@19`
3. Nhấn "Đăng nhập"

### 7.3 Kiểm tra các tính năng
- ✅ Upload ảnh đơn lẻ
- ✅ Quét và nhận diện văn bản (OCR)
- ✅ Tự động đặt tên theo mã viết tắt
- ✅ Xuất PDF đơn lẻ
- ✅ Upload nhiều ảnh (batch)
- ✅ Quét thư mục (ZIP)
- ✅ Quản lý quy tắc (tab Quy Tắc)
- ✅ Xem lịch sử quét

## Tổng Kết Cấu Hình

### Project Structure Trên Railway:
```
Your Project
├── MongoDB Service (Database)
├── Backend Service
│   ├── Root Directory: backend
│   ├── Port: 8001 (auto)
│   └── URL: https://xxx-backend.up.railway.app
└── Frontend Service
    ├── Root Directory: frontend
    ├── Port: 3000 (auto)
    └── URL: https://xxx-frontend.up.railway.app
```

### Environment Variables Summary:

**Backend Variables**:
```
MONGO_URL = (từ MongoDB service + /document_scanner)
JWT_SECRET_KEY = (chuỗi bí mật ngẫu nhiên)
OPENAI_API_KEY = (API key của bạn)
MAX_CONCURRENT = 10
MAX_CONCURRENT_SCANS = 5
UVICORN_TIMEOUT = 300
```

**Frontend Variables**:
```
REACT_APP_BACKEND_URL = (Backend URL)
```

## Xử Lý Sự Cố Thường Gặp

### ❌ Lỗi: Backend build failed với "pip: command not found" hoặc "undefined variable 'pip'"
✅ **Giải pháp**: Lỗi này đã được sửa trong file `backend/nixpacks.toml`. 
- Fix #1: Dùng `python3 -m pip` thay vì `pip` trực tiếp
- Fix #2: Bỏ `pip` khỏi nixPkgs (pip có sẵn trong Python)
- Đảm bảo bạn đã push code mới nhất lên GitHub và trigger rebuild

### ❌ Lỗi: Frontend không kết nối được backend
✅ **Giải pháp**:
1. Kiểm tra `REACT_APP_BACKEND_URL` có đúng Backend URL không
2. Đảm bảo URL có `https://` và không có `/` cuối cùng
3. Vào backend logs xem có lỗi CORS không

### ❌ Lỗi: Cannot connect to MongoDB
✅ **Giải pháp**:
1. Kiểm tra MongoDB service đang chạy (màu xanh)
2. Kiểm tra `MONGO_URL` có đúng format không
3. Đảm bảo có thêm `/document_scanner` vào cuối URL

### ❌ Lỗi: 502 Bad Gateway hoặc 504 Timeout
✅ **Giải pháp**:
1. Tăng `UVICORN_TIMEOUT` lên 600
2. Kiểm tra OpenAI API key còn quota không
3. Xem backend logs có lỗi gì không

### ❌ Lỗi: Service keeps restarting (cứ restart liên tục)
✅ **Giải pháp**:
1. Xem deployment logs để tìm lỗi cụ thể
2. Kiểm tra tất cả environment variables đã điền đủ chưa
3. Kiểm tra Root Directory đã đúng chưa (`backend` hoặc `frontend`)

## Chi Phí Dự Kiến

Railway tính phí theo usage (dùng bao nhiêu tính bấy nhiêu):

**Cho 30 người dùng đồng thời**:
- Backend: ~$5-10/tháng
- Frontend: ~$5-10/tháng  
- MongoDB: ~$5-15/tháng
- **Tổng**: Khoảng $15-35/tháng

**Gói khuyến nghị**:
- **Starter**: $5/service/tháng (thử nghiệm)
- **Developer**: $20/tháng (nhiều services) - **Khuyến nghị**
- **Team**: Custom pricing (quy mô lớn)

## Bảo Mật Sau Khi Deploy

### 1. Đổi mật khẩu admin
- Đăng nhập với `admin/Thommit@19`
- Vào Admin Panel → Đổi mật khẩu

### 2. Cập nhật CORS (quan trọng!)
Mở file `/app/backend/server.py`, tìm phần CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Đổi dòng này
    ...
)
```

Đổi thành:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.up.railway.app"  # URL frontend thật
    ],
    ...
)
```

Sau đó push code và Railway sẽ tự động redeploy.

### 3. Rotate JWT Secret
- Sau vài tháng, nên đổi `JWT_SECRET_KEY` để tăng bảo mật
- Lưu ý: Đổi key sẽ logout tất cả users

## Theo Dõi và Bảo Trì

### Xem Logs
1. Vào Railway dashboard
2. Chọn service (Backend hoặc Frontend)
3. Tab **"Logs"** → Xem realtime logs
4. Hoặc tab **"Deployments"** → Chọn deployment → Xem logs

### Xem Metrics (Hiệu suất)
1. Vào service → Tab **"Metrics"**
2. Xem: CPU, Memory, Network usage
3. Nếu vượt ngưỡng → cần upgrade plan

### Backup MongoDB
⚠️ Railway không tự động backup database:
- **Option 1**: Dùng MongoDB Atlas (có auto backup)
- **Option 2**: Setup backup script định kỳ
- **Option 3**: Export data thủ công thường xuyên

### Update Code
Sau khi sửa code:
```bash
git add .
git commit -m "Mô tả thay đổi"
git push origin main
```
Railway sẽ **tự động rebuild và redeploy** 🚀

## Tính Năng Nâng Cao (Tùy Chọn)

### 1. Custom Domain (Tên miền riêng)
1. Vào service → Settings → Domains
2. Nhấn "Add Custom Domain"
3. Nhập domain của bạn (vd: app.domain.com)
4. Cấu hình DNS records theo hướng dẫn Railway

### 2. Scaling (Tăng performance)
1. Vào service → Settings
2. Phần "Resources" hoặc "Plan"
3. Tăng RAM/CPU nếu cần thiết

### 3. Environment-based Deployment
- Tạo branch `staging` cho test
- Railway có thể tự động deploy mỗi branch riêng biệt

## Checklist Hoàn Thành

- [ ] Railway account đã tạo
- [ ] Project đã tạo trên Railway
- [ ] MongoDB service đã thêm và chạy
- [ ] Backend service đã deploy thành công
- [ ] Frontend service đã deploy thành công
- [ ] Admin user đã khởi tạo
- [ ] Đã đăng nhập được ứng dụng
- [ ] Đã test upload và scan ảnh
- [ ] Đã test batch upload
- [ ] Đã test folder scan (ZIP)
- [ ] Đã đổi password admin
- [ ] Đã cập nhật CORS cho production

## Liên Hệ Hỗ Trợ

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Help**: https://help.railway.app

## Tài Liệu Tham Khảo

- `/app/RAILWAY_DEPLOYMENT_GUIDE.md` - Hướng dẫn chi tiết tiếng Anh
- `/app/RAILWAY_QUICK_START.md` - Quick start guide
- `/app/RAILWAY_FIX_SUMMARY.md` - Chi tiết kỹ thuật về fix
- `/app/RAILWAY_DEPLOYMENT_CHECKLIST.md` - Checklist đầy đủ

---

## 🎉 Chúc Mừng Deploy Thành Công!

Nếu làm đúng các bước trên, ứng dụng của bạn đã chạy trên Railway và sẵn sàng phục vụ 30+ người dùng đồng thời!

**Lưu lại các thông tin quan trọng**:
- Frontend URL: _________________
- Backend URL: _________________
- Admin username: admin
- Admin password: (đã đổi)
- MongoDB URL: (trong Railway variables)
