# 📦 Cách Build App cho Windows

## ⚡ Cách Nhanh Nhất

### Bước 1️⃣: Copy toàn bộ folder `desktop-app` về máy Windows của bạn

### Bước 2️⃣: Click đúp vào file:
```
build-windows.bat
```

### Bước 3️⃣: Đợi build xong (3-5 phút), lấy file:
```
dist\90dayChonThanh Setup 1.1.0.exe
```

**✅ XONG! Bây giờ bạn có file cài đặt cho Windows!**

---

## 📋 Yêu cầu

Trước khi build, đảm bảo máy Windows có:
- ✅ Node.js 16+ ([tải tại đây](https://nodejs.org/))
- ✅ ~5GB dung lượng trống

---

## 🚀 Cách Build Chi Tiết

### Dùng Command Prompt (.bat)
```bash
# Mở Command Prompt trong thư mục desktop-app
build-windows.bat
```

### Dùng PowerShell (.ps1) 
```powershell
# Mở PowerShell trong thư mục desktop-app
# Nếu bị lỗi, chạy trước:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Sau đó chạy:
.\build-windows.ps1
```

### Dùng lệnh thủ công
```bash
# 1. Cài dependencies
yarn install

# 2. Build React
yarn build

# 3. Build Windows installer
npx electron-builder --win --x64
```

---

## 📂 Files sau khi Build

Sau khi build xong, trong folder `dist\` sẽ có:

```
dist\
├── 90dayChonThanh Setup 1.1.0.exe    ← File installer (gửi cho user)
├── win-unpacked\                      ← Version portable (không cần cài)
│   └── 90daychonhanh-desktop.exe
└── builder-debug.yml                  ← Log file (không cần gửi)
```

---

## ❓ Lỗi thường gặp

### Lỗi: "node is not recognized"
**→ Cài Node.js:** https://nodejs.org/

### Lỗi: "yarn is not recognized"
```bash
npm install -g yarn
```

### Lỗi: Out of memory
```bash
set NODE_OPTIONS=--max-old-space-size=4096
build-windows.bat
```

### Build chậm hoặc bị treo
- Tắt antivirus tạm thời
- Kiểm tra kết nối internet (cần tải Electron binaries)
- Đảm bảo có đủ RAM (tối thiểu 4GB)

---

## 📤 Phân phối cho người dùng

**Gửi file này:**
```
dist\90dayChonThanh Setup 1.1.0.exe
```

**Hướng dẫn cài đặt cho user:**
1. Double-click file Setup
2. Chọn thư mục cài đặt
3. Đợi cài xong
4. Chạy app từ Desktop shortcut

---

## 🔧 Build Options khác

### Build Portable (không cần installer)
```bash
npx electron-builder --win --x64 --dir
# File ở: dist\win-unpacked\90daychonhanh-desktop.exe
```

### Build cho 32-bit
```bash
npx electron-builder --win --ia32
```

### Build ZIP (nén thành file zip)
```bash
# Chỉnh package.json:
"win": {
  "target": ["zip"]
}
# Rồi chạy:
npx electron-builder --win
```

---

## 💡 Tips

- **Lần build đầu**: Sẽ lâu hơn (tải Electron binaries ~100MB)
- **Build lần sau**: Nhanh hơn (đã có cache)
- **Size installer**: ~150-200MB
- **Thời gian build**: 3-5 phút (tùy máy)

---

## 📝 Ghi chú kỹ thuật

**Môi trường hiện tại (Linux ARM64):**
- ❌ Không thể build trực tiếp cho Windows
- ❌ Cần wine nhưng không có sẵn
- ✅ Giải pháp: Build trên máy Windows thật

**Vì sao phải build trên Windows?**
- Cross-platform build cần wine (phức tạp)
- Native build trên Windows = nhanh + ổn định
- Tránh lỗi signing và compatibility

---

## 🆘 Cần giúp đỡ?

Nếu build bị lỗi, gửi cho tôi:
1. Screenshot lỗi
2. File log: `dist\builder-debug.yml`
3. Output từ Command Prompt

---

**🎉 Chúc bạn build thành công!**
