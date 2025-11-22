# 🚀 Hướng dẫn tạo Build Windows

## ✅ Tất cả fixes đã hoàn tất

Build này bao gồm tất cả các sửa lỗi:
1. ✅ PDF timeout 300s (xử lý file lớn)
2. ✅ PDF page preview với ảnh thật
3. ✅ Merge PDF theo đúng pages
4. ✅ Smart batch mode với size tùy chỉnh
5. ✅ File picker hỗ trợ ảnh + PDF
6. ✅ Nút phóng lớn cho mọi preview
7. ✅ Bỏ pagination UI
8. ✅ "Mở PDF" button

## 📦 Tạo Build trên Windows

### Bước 1: Mở Command Prompt
```cmd
cd C:\90day\desktop-app
```

### Bước 2: Cài dependencies
```cmd
yarn install
```

### Bước 3: Build app
```cmd
yarn dist:win
```

**Kết quả:**
```
dist/
  └── 90dayChonThanh Setup 1.1.0.exe  ← Installer
```

## 🎯 Hoặc build Portable (không cần install)

```cmd
yarn electron-pack
```

**Kết quả:**
```
dist/
  └── win-unpacked/
      └── 90dayChonThanh.exe  ← Chạy trực tiếp
```

## ⚡ Quick Test

Sau khi build:
```cmd
cd dist\win-unpacked
90dayChonThanh.exe
```

## 📝 Version: 1.1.0

**Changelog:**
- PDF batch processing (timeout 5 phút)
- Preview ảnh cho PDF pages
- Merge PDF chính xác theo classification
- Smart mode với batch size tùy chỉnh
- UI cải tiến

## ⚠️ User Requirements

App cần:
1. **Poppler** (để xử lý PDF):
   - Download: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract → Add to PATH

2. **Gemini API Key**:
   - Lấy tại: https://makersuite.google.com/app/apikey
   - Nhập trong Settings → Cloud Settings

---

**Build date:** 2025
**Platform:** Windows 10/11 64-bit
