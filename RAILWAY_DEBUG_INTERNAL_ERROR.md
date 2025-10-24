# Debug Internal Server Error - Checklist Chi Tiết

## 🔍 Bước 1: Kiểm Tra Backend Logs (QUAN TRỌNG NHẤT!)

### Cách Xem Logs:

1. **Railway Dashboard** → **Backend service** (backend-production-e38f)
2. Click vào tab **"Deployments"** hoặc **"Logs"**
3. Nếu tab "Deployments": Click vào deployment mới nhất → Click **"View Logs"**
4. **Scroll xuống cuối** để xem logs mới nhất
5. Tìm các dòng có chữ **"ERROR"**, **"Exception"**, **"Failed"**

### Lỗi Thường Gặp Và Cách Fix:

#### Lỗi 1: KeyError hoặc Missing Environment Variable
```
KeyError: 'MONGO_URL'
KeyError: 'JWT_SECRET_KEY'
KeyError: 'EMERGENT_LLM_KEY'
```
**Fix**: Biến chưa được thêm hoặc tên sai

#### Lỗi 2: MongoDB Connection Error
```
ServerSelectionTimeoutError: godb.railway.internal:27017: [Errno -2] Name or service not known
Cannot connect to MongoDB
```
**Fix**: MONGO_URL sai hoặc MongoDB service chưa chạy

#### Lỗi 3: Authentication Error
```
Authentication failed
MongoAuthenticationError
```
**Fix**: Username/password trong MONGO_URL sai

#### Lỗi 4: Module Import Error
```
ModuleNotFoundError: No module named 'auth_dependencies'
ImportError: cannot import name 'xxx'
```
**Fix**: File thiếu hoặc import path sai

---

## ✅ Bước 2: Kiểm Tra Variables Đã Thêm Chưa

### Railway → Backend service → Tab "Variables"

**Checklist 3 biến BẮT BUỘC**:

- [ ] **MONGO_URL** có đúng giá trị:
  ```
  mongodb://mongo:YvuqFiFpDxyAvJXWPvNMGcjnliAvVtTT@godb.railway.internal:27017/document_scanner
  ```

- [ ] **JWT_SECRET_KEY** có giá trị (bất kỳ chuỗi dài 32+ ký tự):
  ```
  mySecretKey2024RandomString32CharactersOrMore
  ```

- [ ] **EMERGENT_LLM_KEY** có giá trị:
  ```
  sk-emergent-c9293E676Df8c48F32
  ```

### Nếu thiếu biến nào:
1. Click **"+ New Variable"** hoặc **"Raw Editor"**
2. Thêm biến còn thiếu
3. **Save**
4. Đợi backend restart (1-2 phút)

---

## 🔧 Bước 3: Kiểm Tra Backend Service Status

Railway → Backend service → Kiểm tra:

- [ ] Status có phải **"Active"** (màu xanh)?
- [ ] Build có **"Success"**?
- [ ] Deployment time gần nhất (sau khi add variables)?

**Nếu Status = "Crashed" hoặc "Failed"**:
- Xem logs để biết lỗi
- Fix lỗi theo logs
- Trigger redeploy nếu cần

---

## 🎯 Bước 4: Test Từng Phần

### Test 1: Health Check (Nếu có)
```
https://backend-production-e38f.up.railway.app/
```
Kết quả mong đợi: Không bị 500 error

### Test 2: API Docs (FastAPI có docs tự động)
```
https://backend-production-e38f.up.railway.app/docs
```
Kết quả mong đợi: Thấy Swagger UI

### Test 3: Setup Admin
```
https://backend-production-e38f.up.railway.app/api/setup-admin
```
Kết quả mong đợi: JSON success message

---

## 📋 Template Variables (Copy Và Paste)

Nếu bạn muốn thêm tất cả biến một lúc, dùng **"Raw Editor"**:

```env
MONGO_URL=mongodb://mongo:YvuqFiFpDxyAvJXWPvNMGcjnliAvVtTT@godb.railway.internal:27017/document_scanner
JWT_SECRET_KEY=mySecretKey2024RandomString32CharactersOrMore
EMERGENT_LLM_KEY=sk-emergent-c9293E676Df8c48F32
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
DB_NAME=document_scanner_db
CORS_ORIGINS=*
```

---

## 🆘 Nếu Vẫn Lỗi - Gửi Thông Tin Này

**Để tôi debug chính xác, cần**:

### 1. Backend Logs (20-30 dòng cuối)
Railway → Backend → Logs → Copy dòng cuối

Ví dụ:
```
2024-01-10 10:30:45 INFO: Starting application...
2024-01-10 10:30:46 ERROR: KeyError: 'MONGO_URL'
2024-01-10 10:30:46 ERROR: Application failed to start
```

### 2. Screenshot Backend Variables
Railway → Backend → Variables → Screenshot (có thể che password)

### 3. MongoDB Service Status
Railway → MongoDB service → Status là gì? (Active/Crashed?)

---

## 🔍 Common Issues & Quick Fixes

### Issue 1: Variables Chưa Apply
**Triệu chứng**: Vừa thêm biến nhưng vẫn lỗi
**Fix**: 
- Đợi 2-3 phút để backend restart hoàn toàn
- Hoặc manual restart: Backend → Settings → Restart

### Issue 2: Typo Trong Variable Name
**Triệu chứng**: Lỗi "KeyError: MONGO_URL"
**Fix**: 
- Kiểm tra tên biến phải CHÍNH XÁC: `MONGO_URL` (không có space, đúng chữ hoa/thường)

### Issue 3: MONGO_URL Thiếu Database Name
**Triệu chứng**: Connected to MongoDB nhưng không tạo được admin
**Fix**: 
- Đảm bảo URL có `/document_scanner` ở cuối:
  ```
  ...railway.internal:27017/document_scanner
  ```

### Issue 4: MongoDB Service Chưa Sẵn Sàng
**Triệu chứng**: Connection timeout
**Fix**: 
- Kiểm tra MongoDB service có Active không
- Đợi MongoDB khởi động xong

---

## 📞 Next Steps

1. **XEM LOGS NGAY** - Đây là bước quan trọng nhất!
2. Copy 20-30 dòng logs cuối và gửi cho tôi
3. Hoặc chụp màn hình logs gửi qua
4. Tôi sẽ xác định lỗi chính xác và hướng dẫn fix

---

## 💡 Quick Debug Command

Nếu muốn test MongoDB connection từ backend:

1. Railway → Backend → Settings → **"Deploy"** tab
2. Có option "Railway Shell" hoặc terminal
3. Test connection:
```bash
curl http://localhost:8001/api/setup-admin
```

Hoặc check environment variables:
```bash
echo $MONGO_URL
echo $JWT_SECRET_KEY
echo $EMERGENT_LLM_KEY
```

---

**Hãy xem logs và gửi cho tôi, tôi sẽ giúp fix ngay!**
