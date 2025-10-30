# ⚡ HƯỚNG DẪN BUILD WINDOWS - ĐƠN GIẢN

## 🎯 Làm gì bây giờ?

Vì máy bạn chạy **Windows**, nhưng môi trường này là **Linux**, nên:

❌ **KHÔNG THỂ** build trực tiếp cho Windows ở đây
✅ **PHẢI** build trên máy Windows của bạn

---

## 📥 BƯỚC 1: Tải source code về Windows

### Cách 1: Download folder desktop-app
```
Copy toàn bộ folder này về máy Windows:
/app/desktop-app/
```

### Cách 2: Nếu dùng Git
```bash
git clone [your-repo]
cd desktop-app
```

---

## 🚀 BƯỚC 2: Build trên Windows

### Cách đơn giản nhất (khuyến nghị):

1. **Mở Command Prompt** trong folder `desktop-app`
2. **Click đúp** vào file: `build-windows.bat`
3. **Đợi** 3-5 phút
4. **Lấy file** tại: `dist\90dayChonThanh Setup 1.1.0.exe`

### Hoặc dùng PowerShell:

1. Mở PowerShell trong folder `desktop-app`
2. Chạy:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build-windows.ps1
```

---

## 📦 Kết quả

Sau khi build xong, bạn sẽ có:

```
desktop-app\
└── dist\
    ├── 90dayChonThanh Setup 1.1.0.exe  ← GửI FILE NÀY cho người dùng
    └── win-unpacked\                    ← Version portable
```

---

## ⚙️ Yêu cầu trên máy Windows

Cài **trước khi build**:
- Node.js 16+ → https://nodejs.org/
- ~5GB dung lượng trống

---

## 🔥 TÓM TẮT

1. **Copy** folder `desktop-app` về máy Windows
2. **Chạy** `build-windows.bat`
3. **Lấy** file `dist\90dayChonThanh Setup 1.1.0.exe`
4. **Xong!** Gửi file .exe này cho user

---

## 📚 Tài liệu chi tiết

Xem thêm trong:
- `HOW_TO_BUILD_WINDOWS.md` - Hướng dẫn chi tiết
- `BUILD_WINDOWS_GUIDE.md` - Hướng dẫn đầy đủ
- `build-windows.bat` - Script tự động
- `build-windows.ps1` - PowerShell script

---

## ❓ Câu hỏi thường gặp

**Q: Tại sao không build được ở đây?**
→ Môi trường này là Linux ARM64, build Windows cần wine (phức tạp) hoặc máy Windows thật

**Q: Có cách nào build Windows từ Linux không?**
→ Có, nhưng cần cài wine + nhiều dependencies, không khuyến nghị. Build native trên Windows nhanh và ổn định hơn.

**Q: Tôi không có máy Windows?**
→ Có thể dùng:
- Virtual Machine (VMware, VirtualBox)
- GitHub Actions (CI/CD)
- AppVeyor (CI service)

**Q: Build mất bao lâu?**
→ Lần đầu: 5-10 phút (tải Electron binaries)
→ Lần sau: 3-5 phút

---

## 🆘 Cần hỗ trợ?

Nếu gặp lỗi khi build trên Windows:
1. Chụp screenshot lỗi
2. Copy toàn bộ log từ Command Prompt
3. Gửi cho tôi để debug

---

**✅ Đã tạo đầy đủ các file hỗ trợ build cho bạn!**
