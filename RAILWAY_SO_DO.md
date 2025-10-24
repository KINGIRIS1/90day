# Sơ Đồ Deploy Railway - Visual Guide

## 🎨 Kiến Trúc Ứng Dụng Trên Railway

```
┌─────────────────────────────────────────────────────────┐
│           RAILWAY PROJECT: Document Scanner             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │   MongoDB      │  │    Backend     │  │ Frontend  │ │
│  │   Service      │  │    Service     │  │  Service  │ │
│  ├────────────────┤  ├────────────────┤  ├───────────┤ │
│  │                │  │                │  │           │ │
│  │ Port: 6379    │◄─┤ Port: 8001    │◄─┤Port: 3000 │ │
│  │                │  │                │  │           │ │
│  │ Database:     │  │ Root Dir:     │  │Root Dir:  │ │
│  │ document_     │  │ backend       │  │ frontend  │ │
│  │ scanner       │  │                │  │           │ │
│  │                │  │ Python 3.10   │  │Node 18.x  │ │
│  │ MongoDB 7.x   │  │ FastAPI       │  │React      │ │
│  │                │  │ Uvicorn       │  │Serve      │ │
│  └────────────────┘  └────────────────┘  └───────────┘ │
│                                                          │
│  URL: internal     URL: https://xxx    URL: https://    │
│                    -backend.up...      yyy-frontend.up  │
└─────────────────────────────────────────────────────────┘
         │                    │                   │
         │                    │                   │
         └────────────────────┴───────────────────┘
                              │
                       ┌──────▼──────┐
                       │   Internet  │
                       │   Người dùng│
                       └─────────────┘
```

## 📊 Flow Hoạt Động

```
Người dùng truy cập ứng dụng:
═════════════════════════════════

1. User mở browser → Frontend URL
   │
   └──► Railway Frontend Service (Port 3000)
         │
         ├─ Serve React build files
         └─ Hiển thị giao diện web

2. User upload ảnh → Click "Quét"
   │
   └──► Frontend gọi API
         │
         ├─ POST /api/batch-scan
         └─ Gửi đến Backend URL

3. Backend nhận request
   │
   └──► Railway Backend Service (Port 8001)
         │
         ├─ Resize ảnh (1024px, crop 35%)
         ├─ Gọi OpenAI GPT-4 Vision (OCR)
         ├─ Áp dụng rules (tên tài liệu)
         ├─ Lưu vào MongoDB
         └─ Trả kết quả về Frontend

4. Frontend hiển thị kết quả
   │
   └──► User thấy: Tên tài liệu, confidence, PDF export
```

## 🔧 Chi Tiết Environment Variables

```
┌─────────────────────────────────────────────────────┐
│              BACKEND VARIABLES                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  MONGO_URL                                         │
│  ├─ Kết nối đến MongoDB Service                   │
│  ├─ Format: mongodb://user:pass@host:port/db      │
│  └─ Ví dụ: mongodb://mongo:xxx@rail...../         │
│            document_scanner                        │
│                                                     │
│  JWT_SECRET_KEY                                    │
│  ├─ Mã hóa token đăng nhập                        │
│  ├─ Phải dài ít nhất 32 ký tự                     │
│  └─ Ví dụ: abc123xyz789....(32+ chars)           │
│                                                     │
│  OPENAI_API_KEY                                    │
│  ├─ Gọi GPT-4 Vision để OCR                       │
│  └─ Ví dụ: sk-xxxxx...                           │
│                                                     │
│  MAX_CONCURRENT=10                                 │
│  └─ Giới hạn xử lý đồng thời                      │
│                                                     │
│  MAX_CONCURRENT_SCANS=5                            │
│  └─ Giới hạn scan đồng thời                       │
│                                                     │
│  UVICORN_TIMEOUT=300                               │
│  └─ Timeout cho mỗi request (5 phút)              │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              FRONTEND VARIABLES                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  REACT_APP_BACKEND_URL                             │
│  ├─ URL của Backend Service                       │
│  ├─ Frontend dùng để gọi API                      │
│  └─ Ví dụ: https://xxx-backend.up.railway.app    │
│     (KHÔNG có dấu / ở cuối)                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 📝 Timeline Deploy (Từng Bước)

```
BƯỚC 1: Tạo Project (2 phút)
═══════════════════════════════
[Railway Dashboard] → New Project → Deploy from GitHub
                      ↓
                 Chọn repository
                      ↓
                Project đã tạo ✓


BƯỚC 2: Thêm MongoDB (1 phút)
═══════════════════════════════
[Project] → + New → Database → Add MongoDB
                      ↓
            MongoDB provisioned
                      ↓
      Copy MONGO_URL từ Variables ✓


BƯỚC 3: Deploy Backend (5 phút)
═══════════════════════════════
[Project] → + New → GitHub Repo
                      ↓
      Settings → Root Directory = backend
                      ↓
      Variables → Thêm tất cả biến môi trường
                      ↓
              Railway auto-build
                      ↓
      [Logs] Xem quá trình: install → build → start
                      ↓
            Deploy success ✓
                      ↓
      Settings → Domains → Copy Backend URL


BƯỚC 4: Deploy Frontend (5 phút)
═══════════════════════════════
[Project] → + New → GitHub Repo (cùng repo)
                      ↓
      Settings → Root Directory = frontend
                      ↓
      Variables → REACT_APP_BACKEND_URL = (Backend URL)
                      ↓
              Railway auto-build
                      ↓
      [Logs] Xem: yarn install → yarn build → serve
                      ↓
            Deploy success ✓
                      ↓
      Settings → Domains → Copy Frontend URL


BƯỚC 5: Setup Admin (1 phút)
═══════════════════════════════
Browser → https://backend-url/api/setup-admin
                      ↓
      {"message": "Admin user created"} ✓


BƯỚC 6: Test App (1 phút)
═══════════════════════════════
Browser → https://frontend-url
                      ↓
          Login: admin / Thommit@19
                      ↓
          Upload ảnh → Click Quét
                      ↓
            Kết quả hiển thị ✓

═══════════════════════════════
TỔNG: ~15 phút
```

## 🎯 Root Directory - Quan Trọng Nhất!

```
Cấu trúc thư mục trong GitHub repo:
═══════════════════════════════════════

/app/
  ├── backend/              ← Backend Service
  │   ├── server.py             phải trỏ đến
  │   ├── requirements.txt      thư mục này!
  │   ├── nixpacks.toml         
  │   └── ...                   Root Dir: backend
  │
  └── frontend/             ← Frontend Service
      ├── package.json          phải trỏ đến
      ├── src/                  thư mục này!
      ├── nixpacks.toml
      └── ...                   Root Dir: frontend


⚠️  Lỗi thường gặp:
════════════════════
❌ Root Directory = /backend   (SAI - có dấu /)
❌ Root Directory = app/backend (SAI - có app/)
✅ Root Directory = backend     (ĐÚNG)
✅ Root Directory = frontend    (ĐÚNG)
```

## 🔄 Auto-Deploy Workflow

```
Developer làm việc:
═══════════════════════════════════════════════

1. Sửa code trên máy local
   │
   ├── Sửa backend/server.py
   ├── Sửa frontend/src/App.js
   └── Test local OK
       │
       ▼
2. Git commit & push
   │
   └── git add .
       git commit -m "Update feature"
       git push origin main
           │
           ▼
3. Railway tự động phát hiện
   │
   ├── Webhook từ GitHub
   ├── Railway nhận push event
   └── Trigger auto-deployment
       │
       ▼
4. Railway rebuild & redeploy
   │
   ├── Backend: install → build → restart
   ├── Frontend: install → build → restart
   └── Deployment hoàn thành
       │
       ▼
5. Ứng dụng đã update
   │
   └── User truy cập → thấy thay đổi mới!

═══════════════════════════════════════════════
Không cần làm gì thêm - Railway tự động deploy!
```

## 💾 MongoDB Connection Flow

```
Backend cần lưu dữ liệu:
════════════════════════════════════════

Backend Service                    MongoDB Service
(FastAPI)                          (Database)
    │                                   │
    │  1. Khởi tạo connection          │
    ├──────────────────────────────────►│
    │     MONGO_URL                     │
    │                                   │
    │  2. Insert scan result            │
    ├──────────────────────────────────►│
    │     db.scans.insert_one()         │
    │                                   │
    │  3. Query scan history            │
    ├──────────────────────────────────►│
    │     db.scans.find()               │
    │                                   │
    │  4. Update document               │
    ├──────────────────────────────────►│
    │     db.scans.update_one()         │
    │                                   │

Connection String Format:
═════════════════════════════════════════
mongodb://[username]:[password]@[host]:[port]/[database]
   │         │           │          │      │      │
   │         │           │          │      │      └─ Database name
   │         │           │          │      └─ Port (thường 6379)
   │         │           │          └─ Host (Railway internal)
   │         │           └─ Password (auto-generated)
   │         └─ Username (thường là "mongo")
   └─ Protocol

Ví dụ thực tế:
mongodb://mongo:K8xpQz2@containers-us-west-123.railway.app:6379/document_scanner
```

## 🌐 API Request Flow

```
Frontend gửi request đến Backend:
═════════════════════════════════════════════════

Browser                Frontend            Backend           MongoDB
  │                      │                   │                 │
  │  1. User click      │                   │                 │
  │     "Quét"          │                   │                 │
  ├────────────────────►│                   │                 │
  │                      │                   │                 │
  │                      │  2. POST request │                 │
  │                      │     /api/batch-  │                 │
  │                      │      scan        │                 │
  │                      ├──────────────────►│                 │
  │                      │  (files + auth   │                 │
  │                      │   headers)       │                 │
  │                      │                   │                 │
  │                      │                   │  3. Process:   │
  │                      │                   │    - Resize    │
  │                      │                   │    - Crop 35%  │
  │                      │                   │    - Call GPT  │
  │                      │                   │    - Apply     │
  │                      │                   │      rules     │
  │                      │                   │                 │
  │                      │                   │  4. Save       │
  │                      │                   ├────────────────►│
  │                      │                   │   insert_one() │
  │                      │                   │                 │
  │                      │  5. Return       │                 │
  │                      │     results      │                 │
  │                      │◄──────────────────┤                 │
  │                      │  (JSON)          │                 │
  │                      │                   │                 │
  │  6. Display          │                   │                 │
  │     results          │                   │                 │
  │◄─────────────────────┤                   │                 │
  │                      │                   │                 │

Key Points:
───────────
• Frontend URL: https://xxx-frontend.up.railway.app
• Backend URL:  https://xxx-backend.up.railway.app  
• Frontend luôn gọi Backend qua REACT_APP_BACKEND_URL
• Backend luôn kết nối MongoDB qua MONGO_URL
```

## 📊 Resource Usage (Dự kiến)

```
Cho 30 người dùng đồng thời:
════════════════════════════════════════

┌─────────────────────────────────────┐
│      Backend Service                │
│  ┌───────────────────────────────┐ │
│  │ CPU: ~50-70% (2 vCPU)        │ │
│  │ RAM: ~1-1.5GB (2GB total)    │ │
│  │ Network: ~100-200MB/day      │ │
│  └───────────────────────────────┘ │
│  Cost: $8-12/month                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Frontend Service               │
│  ┌───────────────────────────────┐ │
│  │ CPU: ~20-30% (1 vCPU)        │ │
│  │ RAM: ~512MB-1GB              │ │
│  │ Network: ~50-100MB/day       │ │
│  └───────────────────────────────┘ │
│  Cost: $5-8/month                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      MongoDB Service                │
│  ┌───────────────────────────────┐ │
│  │ Storage: ~1-5GB              │ │
│  │ RAM: ~512MB                  │ │
│  └───────────────────────────────┘ │
│  Cost: $5-10/month                  │
└─────────────────────────────────────┘

        TOTAL: $18-30/month
        (Developer Plan: $20/month bao tất cả)
```

## 🎓 Các File Cấu Hình Quan Trọng

```
/app/backend/nixpacks.toml
═══════════════════════════════════════
Mục đích: Hướng dẫn Railway cách build Backend
Nội dung chính:
  • Packages: Python 3.10, pip, cairo, pango
  • Install: python3 -m pip install -r requirements.txt
  • Start: python3 -m uvicorn server:app
⚠️  Fix: Dùng python3 -m pip (không dùng pip trực tiếp)


/app/backend/railway.json
═══════════════════════════════════════
Mục đích: Cấu hình deployment Railway cho Backend
Nội dung chính:
  • Builder: NIXPACKS
  • Start command: python3 -m uvicorn...
  • Restart policy: ON_FAILURE


/app/frontend/nixpacks.toml
═══════════════════════════════════════
Mục đích: Hướng dẫn Railway cách build Frontend
Nội dung chính:
  • Packages: Node 18.x, yarn
  • Install: yarn install
  • Build: yarn build
  • Start: serve -s build


/app/frontend/railway.json
═══════════════════════════════════════
Mục đích: Cấu hình deployment Railway cho Frontend
Nội dung chính:
  • Builder: NIXPACKS
  • Start command: serve -s build
  • Restart policy: ON_FAILURE
```

---

**Tất cả các sơ đồ và hướng dẫn trên đã bao gồm fix cho lỗi "pip: command not found"!**

Để biết chi tiết từng bước, xem file:
- `/app/RAILWAY_HUONG_DAN_TIENG_VIET.md` - Hướng dẫn đầy đủ
- `/app/RAILWAY_TOM_TAT.md` - Tóm tắt nhanh
