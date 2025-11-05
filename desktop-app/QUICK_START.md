# ⚡ Quick Start - Build Installer trong 5 phút

## 🎯 Mục Tiêu
Build file installer `90dayChonThanh-Setup-1.1.0.exe` để phân phối cho users.

---

## 📋 Bước 1: Kiểm Tra Prerequisites (30 giây)

Mở Command Prompt và chạy:

```bash
node --version
yarn --version
python --version
```

**✅ Nếu tất cả hiện version:** Sang bước 2

**❌ Nếu có lỗi "not found":** Cài đặt thiếu gì:
- Node.js: https://nodejs.org/ (LTS version)
- Yarn: `npm install -g yarn`
- Python: https://www.python.org/ (3.10-3.12)

**⚠️ Quan trọng:** Sau khi cài, **MỞ LẠI Command Prompt mới**!

---

## 🚀 Bước 2: Build Installer (5-10 phút)

### Cách 1: Dùng Build Script (Đơn giản nhất)

```bash
# Di chuyển vào thư mục desktop-app
cd C:\path\to\desktop-app

# Chạy build script
build-installer.bat
```

Chờ script chạy xong. Nó sẽ tự động:
1. Clean Python vendor
2. Install dependencies
3. Build React app
4. Build Windows installer

### Cách 2: Manual Build (Nếu script lỗi)

```bash
# 1. Clean Python vendor
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1

# 2. Install dependencies
yarn install

# 3. Build React
yarn build

# 4. Build installer
yarn dist:win
```

---

## ✅ Bước 3: Verify Output (10 giây)

Kiểm tra file đã được tạo:

```bash
dir dist\90dayChonThanh-Setup-1.1.0.exe
```

Hoặc mở thư mục:
```bash
explorer dist
```

**Kết quả mong đợi:**
- ✅ File: `90dayChonThanh-Setup-1.1.0.exe`
- ✅ Size: ~150-250 MB
- ✅ Có thể double-click để chạy

---

## 🧪 Bước 4: Test Installer (2 phút)

### Quick Test:
```bash
test-installer.bat
```

Chọn option 1 để chạy installer và test.

### Manual Test:
1. Double-click file `90dayChonThanh-Setup-1.1.0.exe`
2. Installer tự động cài app
3. Launch app từ Desktop hoặc Start Menu
4. Test quét 1-2 files để đảm bảo hoạt động

---

## 📤 Bước 5: Phân Phối (5 phút)

### Option A: Google Drive (Đơn giản nhất)
1. Upload file .exe lên Google Drive
2. Chuột phải → Share → Get link
3. Chọn "Anyone with the link"
4. Copy link và share cho users

### Option B: GitHub Release
1. Push code lên GitHub
2. Create new Release
3. Attach file .exe
4. Share release URL

---

## 🎉 Done!

Bạn đã có file installer sẵn sàng phân phối!

**File location:**
```
C:\path\to\desktop-app\dist\90dayChonThanh-Setup-1.1.0.exe
```

---

## ⚡ Quick Rebuild (Sau lần build đầu)

Nếu bạn sửa code và cần build lại:

```bash
# Dùng quick build (2-3 phút)
quick-build.bat
```

---

## 🆘 Troubleshooting Quick Fix

### Lỗi: "Node not found"
```bash
# Cài Node.js từ https://nodejs.org/
# Sau đó MỞ LẠI Command Prompt
```

### Lỗi: "Yarn not found"
```bash
npm install -g yarn
# Sau đó MỞ LẠI Command Prompt
```

### Lỗi: "NSIS not found"
```bash
# Download: https://nsis.sourceforge.io/Download
# Cài và thêm vào PATH
# Sau đó MỞ LẠI Command Prompt
```

### Lỗi: "EPERM" hoặc "operation not permitted"
```bash
# Đóng app nếu đang chạy
# Xóa dist folder
rmdir /s /q dist
# Build lại
build-installer.bat
```

### Build bị treo hoặc quá lâu
```bash
# Ctrl+C để stop
# Clean build:
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q build
yarn install
build-installer.bat
```

---

## 📚 Tài Liệu Đầy Đủ

Để biết thêm chi tiết:
- **BUILD_README.md** - Hướng dẫn đầy đủ
- **HUONG_DAN_BUILD_INSTALLER.md** - Hướng dẫn tiếng Việt chi tiết
- **BUILD_CHECKLIST.md** - Checklist từng bước

---

## 💡 Pro Tips

✅ **Làm đúng:**
- Luôn mở Command Prompt MỚI sau khi cài phần mềm
- Dùng `build-installer.bat` cho lần build đầu
- Dùng `quick-build.bat` cho rebuild nhanh
- Test trên máy sạch trước khi phân phối

❌ **Tránh:**
- Dùng Command Prompt cũ sau khi cài tools
- Build khi app đang chạy
- Bỏ qua error messages
- Phân phối installer chưa test

---

**Thời gian tổng:** ~10-15 phút (bao gồm cả test)

**🚀 Happy Building!**
