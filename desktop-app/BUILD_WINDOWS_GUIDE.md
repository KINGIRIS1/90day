# Hướng dẫn Build ứng dụng cho Windows

## Yêu cầu hệ thống
- Windows 10/11
- Node.js 16.x hoặc cao hơn (tải từ https://nodejs.org/)
- Python 3.9+ (nếu chưa có)
- 5GB dung lượng trống

## Cách 1: Build Tự Động (Khuyến nghị)

### Bước 1: Tải source code về máy Windows
```bash
# Clone hoặc copy toàn bộ folder desktop-app về máy Windows
```

### Bước 2: Chạy script tự động
```bash
# Double-click vào file: build-windows.bat
```

Script này sẽ tự động:
1. Kiểm tra và cài đặt dependencies
2. Build React app
3. Tạo Windows installer (.exe)

### Bước 3: Lấy file installer
Sau khi build xong, file installer sẽ ở:
```
desktop-app\dist\90dayChonThanh Setup 1.1.0.exe
```

## Cách 2: Build Thủ Công

### Bước 1: Cài đặt dependencies
```bash
cd desktop-app
yarn install
```

### Bước 2: Build React app
```bash
yarn build
```

### Bước 3: Build Windows installer
```bash
# Build với NSIS installer
npx electron-builder --win --x64

# Hoặc build với Portable (không cần cài đặt)
npx electron-builder --win --x64 --dir
```

### Bước 4: Lấy file
- **NSIS Installer**: `dist\90dayChonThanh Setup 1.1.0.exe`
- **Portable**: `dist\win-unpacked\90daychonhanh-desktop.exe`

## Các Options Build

### Build cho Windows 32-bit
```bash
npx electron-builder --win --ia32
```

### Build cho cả 32-bit và 64-bit
```bash
npx electron-builder --win
```

### Build Portable (không cần cài đặt)
```bash
npx electron-builder --win --x64 --dir
```

### Build với custom config
```bash
# Chỉnh sửa package.json trước khi build
"build": {
  "win": {
    "target": ["nsis", "portable", "zip"],
    "icon": "assets/icon.png"
  }
}
```

## Cài đặt Python Dependencies (cho app)

Sau khi cài app, người dùng cần cài Python dependencies:

### Cách 1: Tự động (đã có trong app)
```bash
# Chạy từ thư mục cài đặt
cd "%LOCALAPPDATA%\Programs\90daychonhanh-desktop\resources\python"
pip install -r requirements.txt
```

### Cách 2: Script tự động (khuyến nghị)
App sẽ tự động kiểm tra và cài dependencies khi chạy lần đầu.

## Lỗi thường gặp

### 1. "node is not recognized"
**Giải pháp**: Cài đặt Node.js từ https://nodejs.org/

### 2. "yarn is not recognized"
**Giải pháp**: 
```bash
npm install -g yarn
```

### 3. "electron-builder command not found"
**Giải pháp**: 
```bash
yarn install
# hoặc
npm install -g electron-builder
```

### 4. Build bị lỗi "out of memory"
**Giải pháp**: 
```bash
# Tăng memory cho Node.js
set NODE_OPTIONS=--max-old-space-size=4096
yarn build
```

### 5. Thiếu icon
**Giải pháp**: Đảm bảo có file `assets/icon.png` (256x256 trở lên)

## Tùy chỉnh Installer

### Thay đổi tên app
Chỉnh trong `package.json`:
```json
{
  "name": "ten-app-moi",
  "build": {
    "productName": "Tên Hiển Thị"
  }
}
```

### Thay đổi icon
1. Đặt file icon vào `assets/icon.png` (PNG, 256x256 hoặc 512x512)
2. Electron-builder sẽ tự động chuyển sang .ico

### Thêm file license
Tạo file `LICENSE.txt` trong thư mục gốc, nó sẽ tự động được thêm vào installer.

## Phân phối App

### File cần gửi cho người dùng:
1. **File installer**: `90dayChonThanh Setup 1.1.0.exe` (NSIS)
2. **Hướng dẫn cài đặt**: Cài Python dependencies sau khi cài app

### Upload lên web:
```bash
# Nén file installer
7z a 90dayChonThanh-v1.1.0-Windows.zip "dist\90dayChonThanh Setup 1.1.0.exe"
```

## Kiểm tra App sau Build

### Test installer:
1. Chạy file `90dayChonThanh Setup 1.1.0.exe`
2. Chọn thư mục cài đặt
3. Cài đặt
4. Chạy app từ Start Menu hoặc Desktop shortcut

### Test Portable:
1. Vào `dist\win-unpacked\`
2. Chạy `90daychonhanh-desktop.exe`
3. Kiểm tra các tính năng OCR

## Ghi chú

- Build time: ~3-5 phút tùy máy
- Size installer: ~150-200MB
- Size sau cài: ~400-500MB (chưa tính Python dependencies)
- Yêu cầu: Windows 10 trở lên (64-bit)

## Hỗ trợ

Nếu gặp lỗi, check log tại:
```
%APPDATA%\90daychonhanh-desktop\logs\
```
