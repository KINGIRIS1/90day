# 🐍 SỬA LỖI: Missing Python Packages (pytesseract)

## ❌ Lỗi Gặp Phải

```
Missing dependency: No module named 'pytesseract'
Install with: pip install pytesseract pillow
```

**Nguyên nhân:**
- App đã chạy được! ✅
- Nhưng Python không có packages `pytesseract` và `Pillow`
- App dùng `py` command (Python launcher)
- Packages chưa được cài vào Python đó

---

## ✅ GIẢI PHÁP NHANH (Ngay Lập Tức)

### Cách 1: Cài Packages (RECOMMENDED)

Mở **Command Prompt as Administrator** và chạy:

```batch
py -m pip install pytesseract Pillow
```

Hoặc:

```batch
python -m pip install pytesseract Pillow
```

Hoặc:

```batch
pip install pytesseract pillow
```

**Sau đó:**
1. Restart app
2. Test quét lại
3. Sẽ hoạt động! ✅

---

### Cách 2: Verify Python và Packages

**Kiểm tra Python nào đang được dùng:**

```batch
py --version
python --version
where python
where py
```

**Kiểm tra packages đã cài chưa:**

```batch
py -m pip list | findstr pytesseract
py -m pip list | findstr Pillow
```

**Nếu không thấy → Cài:**

```batch
py -m pip install pytesseract Pillow
```

---

## 🔧 SỬA CHO ALL-IN-ONE INSTALLER

Installer cần đảm bảo cài packages vào đúng Python.

### Đã sửa trong `installer.nsi`

**TRƯỚC:**
```nsis
; Install pip packages
DetailPrint "Đang cài Python packages..."
nsExec::ExecToLog 'pip install pytesseract Pillow'
```

**SAU:**
```nsis
; Install pip packages (ensure using correct Python)
DetailPrint "Đang cài Python packages..."
; Try multiple methods to ensure packages are installed
nsExec::ExecToLog 'python -m pip install pytesseract Pillow'
nsExec::ExecToLog 'py -m pip install pytesseract Pillow'
nsExec::ExecToLog 'pip install pytesseract Pillow'
```

**Giải thích:**
- Thử cài bằng 3 cách
- `python -m pip` → Dùng python command
- `py -m pip` → Dùng py launcher
- `pip` → Dùng pip trực tiếp
- Ít nhất 1 cách sẽ thành công

---

## 🚀 TEST NGAY

### Bước 1: Cài Packages

```batch
py -m pip install pytesseract Pillow
```

**Mong đợi:**
```
Collecting pytesseract
  Downloading pytesseract-0.3.13-py3-none-any.whl
Collecting Pillow
  Downloading pillow-10.4.0-cp311-cp311-win_amd64.whl
Installing collected packages: Pillow, pytesseract
Successfully installed Pillow-10.4.0 pytesseract-0.3.13
```

---

### Bước 2: Verify

```batch
py -m pip show pytesseract
py -m pip show Pillow
```

**Phải thấy:**
```
Name: pytesseract
Version: 0.3.13
...

Name: Pillow
Version: 10.4.0
...
```

---

### Bước 3: Test App

1. Mở app: `90dayChonThanh`
2. Click "Scan Documents"
3. Chọn file ảnh
4. Click "Process Offline"
5. Xem kết quả

**Nếu thành công:**
- ✅ Thấy loại tài liệu
- ✅ Thấy text OCR
- ✅ Thấy confidence score
- ✅ Không còn lỗi!

---

## 🎯 CHO USER CUỐI (Distribution)

Khi phân phối installer cho users:

### Option 1: All-in-One Installer (Đã sửa)

**Rebuild installer với fix mới:**

```batch
cd C:\desktop-app
build-allinone.bat
```

**Installer mới sẽ:**
1. Cài Python
2. Cài Tesseract
3. **Cài packages bằng 3 cách khác nhau** ← MỚI
4. Cài app

**User chỉ cần chạy installer → Done!**

---

### Option 2: Manual Instructions (Backup)

Nếu installer vẫn miss packages, cung cấp hướng dẫn cho user:

**File: `HUONG_DAN_CAI_PACKAGES.txt`**

```
Nếu app báo lỗi "Missing dependency pytesseract":

1. Mở Command Prompt as Administrator:
   - Click phải Start Menu
   - Gõ "cmd"
   - Click phải "Command Prompt"
   - Chọn "Run as administrator"

2. Chạy lệnh:
   py -m pip install pytesseract Pillow

3. Đợi cài đặt hoàn tất

4. Restart app

5. Done!
```

---

## 📊 Kiểm Tra Môi Trường

### Script kiểm tra (check-python-env.bat)

```batch
@echo off
echo Checking Python environment...
echo.

echo [1] Python versions:
py --version
python --version
echo.

echo [2] Python locations:
where py
where python
echo.

echo [3] Installed packages:
py -m pip list | findstr pytesseract
py -m pip list | findstr Pillow
echo.

echo [4] pip version:
py -m pip --version
echo.

pause
```

**Lưu vào `desktop-app/check-python-env.bat`**

**Chạy để debug:**
```batch
check-python-env.bat
```

---

## 🔍 Troubleshooting

### Lỗi: "pip not found"

**Fix:**
```batch
python -m ensurepip --upgrade
```

---

### Lỗi: "Permission denied"

**Fix:**
- Chạy Command Prompt as Administrator
- Hoặc cài vào user folder:
```batch
py -m pip install --user pytesseract Pillow
```

---

### Lỗi: Multiple Python versions

**Kiểm tra:**
```batch
py -0
```

**Hiển thị tất cả Python versions.**

**Chọn version cụ thể:**
```batch
py -3.11 -m pip install pytesseract Pillow
```

---

### Lỗi: "No module named pip"

**Fix:**
```batch
python -m ensurepip
py -m ensurepip
```

---

## 📝 Files Đã Thay Đổi

1. ✅ `installer.nsi` - Cài packages bằng 3 cách
2. ✅ `FIX_PYTHON_PACKAGES.md` - File này
3. ✅ `check-python-env.bat` - Script kiểm tra (sẽ tạo)

---

## 🎉 TÓM TẮT

**Vấn đề:** App chạy nhưng thiếu Python packages  
**Nguyên nhân:** pytesseract và Pillow chưa cài  
**Giải pháp nhanh:** `py -m pip install pytesseract Pillow`  
**Giải pháp lâu dài:** Sửa installer để cài packages đúng cách  

---

## ⏭️ NEXT STEPS

### Bước 1: Fix ngay (Development)

```batch
py -m pip install pytesseract Pillow
```

### Bước 2: Test app

Restart app và test quét file

### Bước 3: Rebuild installer (Production)

```batch
cd C:\desktop-app
build-allinone.bat
```

Installer mới sẽ tự cài packages đúng cách!

---

## 🎯 Checklist

- [ ] **Cài packages:** `py -m pip install pytesseract Pillow` ← LÀM NGAY
- [ ] Verify: `py -m pip show pytesseract`
- [ ] Test app: Quét 1 file ảnh
- [ ] Nếu OK → Rebuild installer
- [ ] Test installer trên VM sạch
- [ ] Distribute!

---

**Chạy `py -m pip install pytesseract Pillow` ngay và test lại!** 🚀

**App đã chạy được, chỉ thiếu packages thôi!** 🎉
