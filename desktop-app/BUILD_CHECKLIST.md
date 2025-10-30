# ✅ Checklist Build Windows

## Trước khi build trên Windows

### 1. Chuẩn bị môi trường
- [ ] Đã cài Node.js 16+ (check: `node --version`)
- [ ] Có kết nối internet ổn định (cần tải Electron ~100MB)
- [ ] Còn >5GB dung lượng trống
- [ ] Tắt antivirus (tránh false positive khi build)

### 2. Source code đầy đủ
- [ ] Folder `desktop-app` đã được copy về Windows
- [ ] File `package.json` có đầy đủ
- [ ] Folder `src/` và `public/` tồn tại
- [ ] Folder `python/` với OCR engines tồn tại
- [ ] Folder `assets/` có `icon.png`

### 3. File build scripts
- [ ] `build-windows.bat` - Script build tự động
- [ ] `build-windows.ps1` - PowerShell script
- [ ] `package.json` có config "build.win"

## Trong quá trình build

### Bước 1: Install dependencies
```bash
yarn install
```
- [ ] Không có lỗi
- [ ] Folder `node_modules` được tạo
- [ ] File `yarn.lock` được tạo

### Bước 2: Build React
```bash
yarn build
```
- [ ] Không có lỗi compile
- [ ] Folder `build/` được tạo
- [ ] Files trong `build/static/` tồn tại

### Bước 3: Build Electron
```bash
npx electron-builder --win --x64
```
- [ ] Download Electron binaries thành công
- [ ] Packaging hoàn tất
- [ ] Folder `dist/` được tạo

## Sau khi build

### Kiểm tra output
- [ ] File `dist\90dayChonThanh Setup 1.1.0.exe` tồn tại
- [ ] Size ~150-200MB (nếu nhỏ hơn 50MB = có vấn đề)
- [ ] Folder `dist\win-unpacked\` tồn tại
- [ ] File `dist\builder-debug.yml` tồn tại

### Test installer
- [ ] Double-click file Setup.exe
- [ ] Installer mở được (không bị Windows Defender block)
- [ ] Chọn folder cài đặt
- [ ] Cài đặt thành công
- [ ] App chạy được từ Start Menu
- [ ] App chạy được từ Desktop shortcut

### Test app sau cài
- [ ] App mở được (không crash)
- [ ] UI hiển thị đúng
- [ ] Kiểm tra menu Settings
- [ ] Test scan 1 file (bất kỳ OCR engine nào)
- [ ] Kiểm tra folder output

### Test Python OCR
- [ ] Tesseract OCR hoạt động
- [ ] VietOCR hoạt động (nếu đã cài dependencies)
- [ ] BYOK (Gemini Flash) hoạt động (với API key)
- [ ] Cloud Boost hoạt động (nếu có)

## Phân phối

### Chuẩn bị files
- [ ] Rename file nếu cần (VD: 90dayChonThanh-v1.1.0-Windows-Setup.exe)
- [ ] Tạo file README cho user
- [ ] Đóng gói (zip) nếu cần
- [ ] Tính checksum (MD5/SHA256) nếu upload web

### Upload/Share
- [ ] Test download lại file đã upload
- [ ] Viết release notes (changelog)
- [ ] Hướng dẫn cài đặt cho user
- [ ] Hướng dẫn cài Python dependencies (nếu cần)

## Lỗi thường gặp

### Build bị fail
- [ ] Check log trong Command Prompt
- [ ] Check file `dist\builder-debug.yml`
- [ ] Check network (có thể fail khi tải Electron)
- [ ] Try lại với: `yarn cache clean && yarn install`

### Installer không chạy
- [ ] Windows Defender có thể block → Add exclusion
- [ ] File bị corrupt → Build lại
- [ ] Thiếu Visual C++ Redistributable → Cài thêm

### App crash sau cài
- [ ] Check logs tại: `%APPDATA%\90daychonhanh-desktop\logs\`
- [ ] Python dependencies chưa cài → Run install script
- [ ] Node modules bị thiếu → Build lại với clean install

## Tips để build nhanh hơn

- [ ] Tắt Windows Defender realtime scan tạm thời
- [ ] Close các app nặng khác (browser, IDE)
- [ ] Dùng SSD (nhanh hơn HDD rất nhiều)
- [ ] Upgrade RAM nếu có thể (min 8GB recommended)

## Ghi chú

**Lần build đầu tiên:**
- Lâu nhất (5-10 phút)
- Tải Electron binaries (~100MB)
- Tải dependencies (~200MB)

**Lần build tiếp theo:**
- Nhanh hơn (3-5 phút)
- Có cache rồi

**Build environment:**
- OS: Windows 10/11 (64-bit)
- Node: v16+ / v18+ (recommended)
- RAM: 4GB min, 8GB recommended
- Disk: 5GB free space

---

**✅ Hoàn thành checklist = Build thành công!**
