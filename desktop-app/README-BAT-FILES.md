# Hướng dẫn sử dụng các file .bat

## 📋 Danh sách các file .bat

### 1. `install-dependencies.bat` ⚙️
**Mục đích**: Cài đặt tất cả dependencies cần thiết

**Khi nào dùng**:
- Lần đầu tiên setup project
- Sau khi clone code mới
- Khi có thay đổi trong package.json

**Chức năng**:
- Kiểm tra Node.js và Yarn
- Cài đặt tất cả npm packages
- Tự động cài Yarn nếu chưa có

**Cách dùng**:
```
Double-click file hoặc:
install-dependencies.bat
```

---

### 2. `run-app.bat` 🚀
**Mục đích**: Chạy ứng dụng ở chế độ production

**Khi nào dùng**:
- Chạy app bình thường
- Sau khi build xong
- Khi muốn test version production

**Chức năng**:
- Kiểm tra và cài dependencies (nếu chưa có)
- Build React app
- Khởi động Electron app

**Cách dùng**:
```
Double-click file hoặc:
run-app.bat
```

---

### 3. `run-dev.bat` 🛠️
**Mục đích**: Chạy ứng dụng ở chế độ development

**Khi nào dùng**:
- Khi đang develop/debug
- Muốn hot reload (tự động refresh khi sửa code)
- Muốn xem console logs chi tiết

**Chức năng**:
- Kiểm tra dependencies
- Start React dev server (http://localhost:3001)
- Start Electron với hot reload
- Mở DevTools tự động

**Cách dùng**:
```
Double-click file hoặc:
run-dev.bat
```

**Lưu ý**: 
- Chế độ này chậm hơn production
- Để stop: Close cửa sổ cmd

---

### 4. `build-installer.bat` 📦
**Mục đích**: Tạo file cài đặt Windows (.exe)

**Khi nào dùng**:
- Muốn tạo installer để cài trên máy khác
- Chuẩn bị release version mới
- Muốn distribute app

**Chức năng**:
- Build React app
- Package thành file .exe installer
- Tạo file trong folder `dist/`

**Cách dùng**:
```
Double-click file hoặc:
build-installer.bat
```

**Output**: `dist\90dayChonThanh Setup.exe`

---

### 5. `clean-rebuild.bat` 🧹
**Mục đích**: Xóa sạch và rebuild từ đầu

**Khi nào dùng**:
- Gặp lỗi lạ không sửa được
- Sau khi update dependencies lớn
- Khi build bị lỗi cache
- Trước khi tạo installer quan trọng

**Chức năng**:
- Xóa `node_modules/`
- Xóa `build/`
- Cài lại dependencies
- Build lại từ đầu

**Cách dùng**:
```
Double-click file hoặc:
clean-rebuild.bat
```

**⚠️ Cảnh báo**: 
- Quá trình này mất nhiều thời gian (5-10 phút)
- Cần kết nối internet để download dependencies

---

## 🔄 Workflow thông thường

### Lần đầu setup:
```
1. install-dependencies.bat  (cài đặt)
2. run-app.bat               (chạy app)
```

### Development thường ngày:
```
run-dev.bat                  (chế độ dev với hot reload)
```

### Khi gặp lỗi:
```
1. clean-rebuild.bat         (clean và rebuild)
2. run-app.bat               (chạy lại)
```

### Tạo installer:
```
1. clean-rebuild.bat         (đảm bảo build sạch)
2. build-installer.bat       (tạo file .exe)
```

---

## ⚠️ Requirements

**Cần cài đặt trước**:
- Node.js (v16 hoặc mới hơn): https://nodejs.org/
- Python 3.x: https://www.python.org/downloads/
- Git (optional): https://git-scm.com/

**Kiểm tra**:
```cmd
node --version
python --version
```

---

## 🐛 Troubleshooting

### Lỗi: "Node.js is not installed"
**Giải pháp**: Cài Node.js từ https://nodejs.org/

### Lỗi: "Yarn is not installed"
**Giải pháp**: File .bat sẽ tự động cài Yarn, hoặc chạy:
```cmd
npm install -g yarn
```

### Lỗi: "Python not found"
**Giải pháp**: 
1. Cài Python 3.x
2. Thêm Python vào PATH
3. Restart cmd

### Lỗi: "Port 3001 already in use"
**Giải pháp**:
1. Tắt app đang chạy
2. Hoặc kill process:
```cmd
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### App không start
**Giải pháp**:
1. Chạy `clean-rebuild.bat`
2. Check logs trong console
3. Xóa cache: `%APPDATA%\Electron`

---

## 📞 Support

Nếu gặp vấn đề:
1. Check README.md chính
2. Xem logs trong console
3. Liên hệ team support

---

**Version**: 1.1.0  
**Last Updated**: 2025
