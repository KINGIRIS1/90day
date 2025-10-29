# 📦 HƯỚNG DẪN CHẠY create-user-package.bat

## 🎯 Mục đích

Script này tự động tạo package hoàn chỉnh để giao cho user, bao gồm:
- Installer (.exe)
- Hướng dẫn cài đặt
- Download links
- Requirements
- Tài liệu đầy đủ

---

## 📋 YÊU CẦU TRƯỚC KHI CHẠY

### 1. Đã build app thành công

```bash
# Trong thư mục /app/desktop-app/
npm run build
```

**Kết quả phải có:**
- File: `installers/90dayChonThanh-Setup-1.1.0.exe`
- (Optional): `90dayChonThanh-Portable-Win.zip`

### 2. Verify file tồn tại

```bash
# Check installer
dir installers\90dayChonThanh-Setup-*.exe

# Nếu không có → build lại
npm run build
```

---

## 🚀 CÁCH CHẠY SCRIPT

### **CÁCH 1: Double Click (Đơn giản nhất)**

1. Vào thư mục `/app/desktop-app/`

2. Tìm file: `create-user-package.bat`

3. **Double click** vào file

4. Cửa sổ CMD sẽ mở và hiện:
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║     TẠO PACKAGE GIAO CHO USER - 90dayChonThanh v1.1.0      ║
   ╚══════════════════════════════════════════════════════════════╝
   
   [1/7] Tạo thư mục package...
   [2/7] Copy installer...
       ✓ Installer copied
   [3/7] Copy portable version...
       ⚠ Portable version not found, skipping...
   [4/7] Tạo hướng dẫn nhanh...
       ✓ Quick start guide created
   [5/7] Tạo file download links...
       ✓ Download links created
   [6/7] Tạo file requirements...
       ✓ Requirements created
   [7/7] Copy tài liệu đầy đủ...
       ✓ Full guide copied
   
   Đang tạo file ZIP...
   
   ╔══════════════════════════════════════════════════════════════╗
   ║                    HOÀN THÀNH!                              ║
   ╚══════════════════════════════════════════════════════════════╝
   
   📦 Package created: 90dayChonThanh-v1.1.0-UserPackage.zip
   📁 Folder: 90dayChonThanh-v1.1.0-UserPackage\
   ```

5. Nhấn **bất kỳ phím nào** để đóng

---

### **CÁCH 2: Chạy từ Command Prompt**

1. Mở Command Prompt (CMD)

2. Di chuyển vào thư mục:
   ```batch
   cd C:\path\to\desktop-app
   ```

3. Chạy script:
   ```batch
   create-user-package.bat
   ```

4. Xem output như Cách 1

---

### **CÁCH 3: Chạy từ PowerShell**

1. Mở PowerShell

2. Di chuyển vào thư mục:
   ```powershell
   cd C:\path\to\desktop-app
   ```

3. Chạy script:
   ```powershell
   .\create-user-package.bat
   ```

---

## 📂 KẾT QUẢ SAU KHI CHẠY

### Script sẽ tạo 2 thứ:

#### 1. **Folder:** `90dayChonThanh-v1.1.0-UserPackage/`

```
90dayChonThanh-v1.1.0-UserPackage/
│
├── 90dayChonThanh-Setup-1.1.0.exe     (~150MB - Installer)
├── BAT_DAU_O_DAY.txt                  (Hướng dẫn ngắn cho user)
├── DOWNLOAD_LINKS.txt                 (Links Python & Tesseract)
├── REQUIREMENTS.txt                   (Yêu cầu hệ thống)
│
├── Prerequisites/                     (Rỗng - để thêm offline installers)
│
└── Docs/                              (Tài liệu chi tiết)
    ├── HUONG_DAN_DAY_DU.md
    ├── DEVELOPER_GUIDE.md
    └── README.md
```

#### 2. **ZIP File:** `90dayChonThanh-v1.1.0-UserPackage.zip`

- Đã nén folder trên thành ZIP
- Kích thước: ~150MB (không có offline installers)
- Sẵn sàng gửi cho user!

---

## ✅ VERIFY KẾT QUẢ

### Check 1: Folder tồn tại

```batch
dir 90dayChonThanh-v1.1.0-UserPackage
```

**Phải thấy:**
- BAT_DAU_O_DAY.txt ✓
- DOWNLOAD_LINKS.txt ✓
- REQUIREMENTS.txt ✓
- 90dayChonThanh-Setup-1.1.0.exe ✓
- Folders: Prerequisites, Docs ✓

### Check 2: ZIP file tồn tại

```batch
dir *.zip
```

**Phải thấy:**
- 90dayChonThanh-v1.1.0-UserPackage.zip (~150MB) ✓

### Check 3: Test giải nén ZIP

1. Right click ZIP file
2. Extract All...
3. Chọn folder test
4. Extract
5. Mở folder → Verify các files OK

---

## 🔧 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: "Installer not found!"

**Màn hình hiện:**
```
[2/7] Copy installer...
    ⚠ WARNING: Installer not found in installers\
    Tìm kiếm trong thư mục hiện tại...
    ✗ ERROR: Installer not found!
    
    Vui lòng build installer trước:
    npm run build
```

**Nguyên nhân:** Chưa build app

**Giải pháp:**
```bash
# Build app trước
npm run build

# Sau đó chạy lại
create-user-package.bat
```

---

### Lỗi 2: "Lỗi tạo ZIP file!"

**Màn hình hiện:**
```
Đang tạo file ZIP...
✗ Lỗi tạo ZIP file!
```

**Nguyên nhân:** PowerShell không có quyền hoặc lỗi

**Giải pháp:**

**Option A: Chạy as Administrator**
1. Right click `create-user-package.bat`
2. "Run as administrator"
3. Chạy lại

**Option B: Tạo ZIP thủ công**
1. Right click folder `90dayChonThanh-v1.1.0-UserPackage`
2. Send to → Compressed (zipped) folder
3. Đổi tên thành `90dayChonThanh-v1.1.0-UserPackage.zip`

---

### Lỗi 3: "Portable version not found, skipping..."

**Màn hình hiện:**
```
[3/7] Copy portable version...
    ⚠ Portable version not found, skipping...
```

**Đây KHÔNG phải lỗi!**
- Portable version là optional
- Nếu không cần → bỏ qua
- Nếu cần → build portable trước:
  ```bash
  npm run build:portable
  ```

---

### Lỗi 4: "Full guide not copied"

**Nguyên nhân:** Thiếu file HUONG_DAN_CAI_DAT_USER.md

**Giải pháp:**
- File này phải tồn tại trong `/app/desktop-app/`
- Nếu thiếu → không sao, các file khác vẫn đủ dùng

---

## 📤 SAU KHI CHẠY THÀNH CÔNG

### Bước tiếp theo:

#### **Option 1: Gửi ngay cho user (Có internet)**

1. Upload ZIP lên Google Drive / Dropbox
2. Share link cho user
3. User download về

**User cần:**
- Download Python từ python.org
- Download Tesseract từ GitHub
- Follow hướng dẫn trong BAT_DAU_O_DAY.txt

---

#### **Option 2: Package offline (Không internet)**

Nếu user **KHÔNG CÓ INTERNET**, thêm offline installers:

1. **Download Python offline installer (~25MB):**
   ```
   https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
   ```

2. **Download Tesseract offline installer (~40MB):**
   ```
   https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
   ```

3. **Copy 2 files vào:**
   ```
   90dayChonThanh-v1.1.0-UserPackage/Prerequisites/
   ```

4. **Tạo lại ZIP:**
   ```batch
   # Xóa ZIP cũ
   del 90dayChonThanh-v1.1.0-UserPackage.zip
   
   # Tạo ZIP mới (thủ công)
   # Right click folder → Send to → Compressed folder
   ```

5. **Package size giờ:**
   - ~150MB → ~220MB (có offline installers)

---

## 📊 CHECKLIST HOÀN CHỈNH

### Trước khi gửi user:

- [ ] Chạy `npm run build` thành công
- [ ] Chạy `create-user-package.bat` thành công
- [ ] Folder `90dayChonThanh-v1.1.0-UserPackage` tồn tại
- [ ] ZIP file `90dayChonThanh-v1.1.0-UserPackage.zip` tồn tại
- [ ] Test giải nén ZIP → OK
- [ ] Mở `BAT_DAU_O_DAY.txt` → đọc được
- [ ] Check installer: `90dayChonThanh-Setup-1.1.0.exe` trong package
- [ ] (Optional) Thêm offline installers vào Prerequisites/
- [ ] (Optional) Test installer trên máy clean Windows

### Khi gửi user:

- [ ] Upload ZIP lên Drive/Dropbox
- [ ] Share link với user
- [ ] Gửi email hướng dẫn
- [ ] Chuẩn bị support (email/phone)

---

## 🎬 VIDEO DEMO (Step-by-Step)

### Bước 1: Build app
```
1. Mở thư mục desktop-app
2. Mở CMD hoặc Terminal
3. Gõ: npm run build
4. Đợi build xong
5. Check: installers/90dayChonThanh-Setup-1.1.0.exe tồn tại
```

### Bước 2: Chạy script
```
1. Double click: create-user-package.bat
2. Đợi script chạy (3-5 giây)
3. Xem output
4. Nhấn Enter để đóng
```

### Bước 3: Verify
```
1. Check folder: 90dayChonThanh-v1.1.0-UserPackage
2. Check ZIP: 90dayChonThanh-v1.1.0-UserPackage.zip
3. Giải nén test → OK
```

### Bước 4: Gửi user
```
1. Upload ZIP lên Drive
2. Copy share link
3. Gửi email cho user với link
4. Done!
```

**Tổng thời gian:** 2-3 phút

---

## 💡 TIPS & TRICKS

### Tip 1: Tạo package nhanh hơn

Tạo alias trong CMD:
```batch
# Tạo file quick-package.bat
@echo off
cd C:\path\to\desktop-app
npm run build && create-user-package.bat
```

Giờ chỉ cần double click `quick-package.bat` → build + package cùng lúc!

---

### Tip 2: Auto-versioning

Nếu muốn tự động tăng version, sửa trong script:

```batch
REM Đọc version từ package.json
for /f "tokens=2 delims=:, " %%a in ('findstr /C:"\"version\"" package.json') do set APP_VERSION=%%~a
```

---

### Tip 3: Batch processing

Nếu cần tạo nhiều packages (nhiều versions):

```batch
# create-all-packages.bat
@echo off
call create-user-package.bat
rename 90dayChonThanh-v1.1.0-UserPackage.zip 90dayChonThanh-v1.1.0-Full.zip

REM Tạo version minimal (không có Docs)
rmdir /s /q 90dayChonThanh-v1.1.0-UserPackage\Docs
powershell -command "Compress-Archive -Path '90dayChonThanh-v1.1.0-UserPackage' -DestinationPath '90dayChonThanh-v1.1.0-Minimal.zip' -Force"
```

---

## 🆘 SUPPORT & CONTACT

**Nếu gặp vấn đề:**

1. **Check prerequisites:**
   - Node.js installed?
   - npm install đã chạy?
   - Build thành công?

2. **Check logs:**
   - Script có báo lỗi gì?
   - Screenshot error message

3. **Manual fallback:**
   - Copy files thủ công vào folder
   - Tạo ZIP thủ công

4. **Contact:**
   - Mô tả vấn đề chi tiết
   - Attach screenshot
   - Attach log (nếu có)

---

## ✅ SUMMARY

### **3 BƯỚC ĐƠN GIẢN:**

```
1. npm run build
   → Tạo installer

2. create-user-package.bat
   → Tạo package tự động

3. Gửi ZIP cho user
   → Done!
```

**Thời gian:** 2-3 phút  
**Kết quả:** Package hoàn chỉnh sẵn sàng gửi user  
**Dễ dàng:** ⭐⭐⭐⭐⭐ (Cực kỳ đơn giản!)

---

## 📋 QUICK REFERENCE

### Commands:
```batch
# Build app
npm run build

# Tạo package
create-user-package.bat

# Check kết quả
dir 90dayChonThanh-v*

# Test ZIP
# Right click → Extract All
```

### Files output:
```
90dayChonThanh-v1.1.0-UserPackage/      (Folder)
90dayChonThanh-v1.1.0-UserPackage.zip   (ZIP ~150MB)
```

### Gửi cho user:
```
- Upload ZIP lên Drive/Dropbox
- Share link
- User download → giải nén → follow hướng dẫn
```

---

✅ **CỰC KỲ ĐƠN GIẢN - CHỈ MỘT CLICK!** 🚀
