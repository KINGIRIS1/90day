# 🚀 Build Scripts - Hướng Dẫn Sử Dụng

## 📦 Các File Build Script Có Sẵn

Dự án cung cấp **3 build script** để bạn chọn tùy theo nhu cầu:

| Script | Khi nào sử dụng | Ưu điểm |
|--------|----------------|---------|
| `build-installer.bat` | Build lần đầu hoặc build đầy đủ | ✓ Kiểm tra prerequisites<br>✓ Cài đặt dependencies<br>✓ Clean build<br>✓ Thông báo chi tiết |
| `build-installer.ps1` | Build với PowerShell (advanced users) | ✓ Tương tự .bat nhưng với PowerShell<br>✓ Hiển thị đẹp hơn<br>✓ Xử lý lỗi tốt hơn |
| `quick-build.bat` | Build nhanh sau khi đã build thành công 1 lần | ✓ Nhanh nhất<br>✓ Không cài lại dependencies<br>✓ Chỉ rebuild code |

---

## 🎯 Build Lần Đầu Tiên (Recommended)

### Cách 1: Sử dụng Batch Script (Đơn giản nhất)

```batch
# Mở Command Prompt trong thư mục desktop-app
cd C:\path\to\desktop-app

# Chạy build script
build-installer.bat
```

### Cách 2: Sử dụng PowerShell Script (Nâng cao)

```powershell
# Mở PowerShell trong thư mục desktop-app
cd C:\path\to\desktop-app

# Cho phép chạy script (chỉ cần làm 1 lần)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Chạy build script
.\build-installer.ps1
```

**⏱ Thời gian build:** 5-10 phút (tùy máy)

**📂 Kết quả:**
```
dist\90dayChonThanh-Setup-1.1.0.exe  (~150-250 MB)
```

---

## ⚡ Build Nhanh (Quick Rebuild)

Sau khi đã build thành công 1 lần, bạn có thể dùng `quick-build.bat` để build lại nhanh hơn:

```batch
# Chỉ cần chạy
quick-build.bat
```

**⏱ Thời gian:** 2-3 phút

**Khi nào dùng:**
- ✅ Sau khi sửa code React/JavaScript
- ✅ Sau khi thay đổi Python scripts
- ✅ Khi muốn rebuild nhanh để test
- ❌ KHÔNG dùng khi thay đổi dependencies trong package.json

---

## 📋 Prerequisites (Yêu Cầu)

Trước khi chạy build script, đảm bảo đã cài đặt:

### 1. **Node.js** (Bắt buộc)
- Version: >= 16.x
- Download: https://nodejs.org/ (chọn LTS)
- ✅ Nhớ check "Add to PATH" khi cài

**Kiểm tra:**
```bash
node --version   # Phải hiện v16.x.x trở lên
```

### 2. **Yarn** (Bắt buộc)
```bash
npm install -g yarn
```

**Kiểm tra:**
```bash
yarn --version   # Phải hiện 1.22.x
```

### 3. **Python** (Bắt buộc)
- Version: 3.10, 3.11, hoặc 3.12
- Download: https://www.python.org/downloads/
- ✅ Nhớ check "Add Python to PATH" khi cài

**Kiểm tra:**
```bash
python --version   # hoặc py --version
```

### 4. **NSIS** (Recommended)
- Để tạo installer .exe
- Download: https://nsis.sourceforge.io/Download
- Cài và thêm vào PATH

**Kiểm tra:**
```bash
makensis /VERSION
```

---

## 🎬 Quy Trình Build Chi Tiết

### Script `build-installer.bat` thực hiện các bước sau:

```
[0/5] Kiểm tra prerequisites (Node, Yarn, Python, NSIS)
      ↓
[1/5] Clean Python vendor directories
      ↓ Xóa các thư viện Python cũ
      ↓
[2/5] Install Node.js dependencies
      ↓ yarn install
      ↓
[3/5] Build React production
      ↓ yarn build → tạo thư mục build/
      ↓
[4/5] Build Windows installer
      ↓ yarn dist:win → electron-builder
      ↓
[5/5] Verify output
      ✓ dist\90dayChonThanh-Setup-1.1.0.exe
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### ❌ Lỗi: "Node.js not found"
**Giải pháp:**
1. Cài Node.js từ https://nodejs.org/
2. Check "Add to PATH" khi cài
3. **MỞ LẠI Command Prompt mới** sau khi cài
4. Chạy lại build script

---

### ❌ Lỗi: "Yarn not found"
**Giải pháp:**
```bash
npm install -g yarn
```
Sau đó chạy lại build script.

---

### ❌ Lỗi: "NSIS not found" hoặc "electron-builder failed"
**Giải pháp:**
1. Download NSIS: https://nsis.sourceforge.io/Download
2. Cài đặt (khuyến nghị: `C:\Program Files (x86)\NSIS`)
3. Thêm vào PATH:
   ```
   C:\Program Files (x86)\NSIS
   ```
4. **MỞ LẠI Command Prompt**
5. Kiểm tra:
   ```bash
   makensis /VERSION
   ```
6. Chạy lại build script

---

### ❌ Lỗi: "Python not found"
**Giải pháp:**
1. Cài Python 3.10-3.12 từ https://www.python.org/
2. Check "Add Python to PATH" khi cài
3. **MỞ LẠI Command Prompt**
4. Kiểm tra:
   ```bash
   python --version
   ```

---

### ❌ Lỗi: "EPERM: operation not permitted"
**Nguyên nhân:** File trong `dist/` đang được sử dụng

**Giải pháp:**
1. **Đóng app** nếu đang chạy
2. Xóa thư mục dist:
   ```bash
   rmdir /s /q dist
   ```
3. Chạy lại build script

---

### ❌ Lỗi: "Out of memory" / "heap limit"
**Giải pháp:**
1. Đóng các ứng dụng khác để giải phóng RAM
2. Tăng memory cho Node.js:
   ```bash
   set NODE_OPTIONS=--max_old_space_size=4096
   build-installer.bat
   ```

---

## 🔧 Tùy Chỉnh Installer

### Thay đổi Icon
1. Chuẩn bị icon file: `.ico` hoặc `.png` (256x256)
2. Copy vào: `assets/icon.ico` hoặc `assets/icon.png`
3. Build lại

### Thay đổi Version
1. Mở `package.json`
2. Sửa `"version": "1.1.0"` thành version mới
3. Build lại
4. Installer sẽ có tên: `90dayChonThanh-Setup-[VERSION].exe`

### Thay đổi App Name
1. Mở `package.json`
2. Sửa `"productName": "90dayChonThanh"`
3. Build lại

---

## 📤 Phân Phối Installer

### Option 1: Google Drive
1. Upload file .exe lên Google Drive
2. Chuột phải → Get link → Anyone with the link
3. Share link cho users

### Option 2: GitHub Releases
1. Tạo repository trên GitHub
2. Push code lên
3. Create new Release
4. Đính kèm file .exe
5. Users download từ Releases page

### Option 3: Website
- Upload lên hosting (AWS S3, Azure Blob, etc.)
- Tạo download link

---

## 📊 Checklist Trước Khi Phân Phối

- [ ] Build thành công không có lỗi
- [ ] Test cài đặt trên máy hiện tại
- [ ] Test trên máy Windows sạch (nếu có)
- [ ] Test tất cả chức năng:
  - [ ] Quét file hoạt động
  - [ ] OCR hoạt động
  - [ ] Classification chính xác
  - [ ] Export PDF hoạt động
  - [ ] Settings lưu được
- [ ] File size hợp lý (~150-250 MB)
- [ ] Version number đúng

---

## 🚀 Build Commands Nhanh

### Full build từ đầu:
```bash
build-installer.bat
```

### Quick rebuild (sau khi đã build 1 lần):
```bash
quick-build.bat
```

### Manual build (từng bước):
```bash
# 1. Clean Python vendor
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1

# 2. Install dependencies (nếu cần)
yarn install

# 3. Build React
yarn build

# 4. Build installer
yarn dist:win
```

### Clean build (khi có vấn đề):
```bash
# Xóa tất cả
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q build

# Cài lại và build
yarn install
build-installer.bat
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề không giải quyết được:

1. **Kiểm tra logs:** Đọc kỹ thông báo lỗi trong console
2. **Kiểm tra prerequisites:** Đảm bảo tất cả đã cài đúng
3. **Clean build:** Thử xóa `node_modules`, `dist`, `build` và build lại
4. **Tìm kiếm lỗi:** Google error message
5. **Liên hệ:** contact@90daychonthanh.vn

---

## 💡 Tips

✅ **DO:**
- Luôn mở Command Prompt **MỚI** sau khi cài phần mềm mới
- Kiểm tra PATH sau khi cài
- Test installer trên máy sạch trước khi phân phối
- Đọc kỹ error messages
- Dùng `quick-build.bat` cho rebuild nhanh

❌ **DON'T:**
- Đừng dùng cửa sổ Command Prompt cũ sau khi cài phần mềm
- Đừng build khi app đang chạy
- Đừng bỏ qua error messages
- Đừng phân phối installer chưa test

---

**Version:** 1.1.0  
**Last Updated:** 2025  
**Platform:** Windows x64

Happy Building! 🎉
