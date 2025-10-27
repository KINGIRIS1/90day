# ⚡ FIX NHANH: Missing pytesseract

## 🚀 GIẢI PHÁP NHANH NHẤT (1 PHÚT)

### Bước 1: Chạy Script Tự Động

```batch
cd C:\desktop-app
install-python-packages.bat
```

**Script sẽ tự động:**
- ✅ Cài pytesseract
- ✅ Cài Pillow
- ✅ Test xem packages hoạt động chưa
- ✅ Báo kết quả

---

### Bước 2: Restart App

```batch
# Tắt app (Ctrl+C)
# Chạy lại
yarn electron-dev
```

Hoặc nếu dùng script:
```batch
start-dev.bat
```

---

### Bước 3: Test Quét File

1. Mở app
2. Click "Scan Documents"
3. Chọn file ảnh
4. Click "🔍 Process Offline"
5. Xem kết quả

**Nếu thành công → Done! ✅**

---

## 🔧 NẾU SCRIPT KHÔNG HOẠT ĐỘNG

### Method A: Manual Install (Recommended)

**Mở Command Prompt as Administrator:**

```batch
py -m pip install pytesseract Pillow
```

**Verify:**
```batch
py -m pip show pytesseract
py -m pip show Pillow
```

**Test import:**
```batch
py -c "import pytesseract; import PIL; print('OK')"
```

---

### Method B: Specific Python Version

**Nếu có nhiều Python versions:**

```batch
# List all Python versions
py -0

# Install to specific version (e.g., 3.11)
py -3.11 -m pip install pytesseract Pillow
```

---

### Method C: User Install (No Admin)

**Nếu không có quyền admin:**

```batch
py -m pip install --user pytesseract Pillow
```

---

## 🔍 DEBUG

### Kiểm tra Python được app dùng

**Check trong app error:**
```
Spawning: py c:\desktop-app\python\process_document.py ...
          ^^
          App dùng "py" command
```

**Verify py command:**
```batch
where py
py --version
py -m pip --version
```

---

### Kiểm tra packages đã cài

```batch
# List all installed packages
py -m pip list

# Search for pytesseract
py -m pip list | findstr pytesseract

# Search for Pillow
py -m pip list | findstr Pillow
```

**Nếu thấy → Đã cài ✓**

---

### Kiểm tra Python paths

```batch
# Check Python executable
py -c "import sys; print(sys.executable)"

# Check site-packages location
py -c "import site; print(site.getsitepackages())"
```

---

## ⚠️ COMMON ISSUES

### Issue 1: Multiple Python Installations

**Problem:**
```
Cài vào Python A
Nhưng app dùng Python B
```

**Solution:**
```batch
# Find which Python app uses
where py
where python

# Install to all
py -m pip install pytesseract Pillow
python -m pip install pytesseract Pillow
```

---

### Issue 2: Permission Denied

**Problem:**
```
ERROR: Could not install packages due to an EnvironmentError: [WinError 5] Access is denied
```

**Solution:**
```batch
# Run as Administrator
# Or use --user flag
py -m pip install --user pytesseract Pillow
```

---

### Issue 3: pip Not Found

**Problem:**
```
No module named pip
```

**Solution:**
```batch
# Reinstall pip
py -m ensurepip --upgrade

# Try again
py -m pip install pytesseract Pillow
```

---

### Issue 4: Network Error

**Problem:**
```
Could not fetch URL ... connection error
```

**Solution:**
```batch
# Use mirror
py -m pip install pytesseract Pillow --index-url https://pypi.org/simple

# Or retry
py -m pip install pytesseract Pillow --retries 5
```

---

## 📊 VERIFICATION CHECKLIST

After installation, verify:

- [ ] Run: `py -m pip show pytesseract` → See version info
- [ ] Run: `py -m pip show Pillow` → See version info
- [ ] Run: `py -c "import pytesseract"` → No error
- [ ] Run: `py -c "import PIL"` → No error
- [ ] Restart app
- [ ] Test scan → Works!

---

## 🎯 COMPLETE WORKFLOW

```batch
# Step 1: Install packages
cd C:\desktop-app
install-python-packages.bat

# Step 2: Verify
py -m pip show pytesseract
py -m pip show Pillow

# Step 3: Test import
py -c "import pytesseract; import PIL; print('OK')"

# Step 4: Restart app
start-dev.bat

# Step 5: Test scan
# (Use app UI)
```

---

## 💡 FOR PRODUCTION (Installer)

**The installer already handles this!**

File: `installer.nsi` (lines 67-70)
```nsis
; Install pip packages (ensure using correct Python)
DetailPrint "Đang cài Python packages..."
; Try multiple methods to ensure packages are installed
nsExec::ExecToLog 'python -m pip install pytesseract Pillow'
nsExec::ExecToLog 'py -m pip install pytesseract Pillow'
nsExec::ExecToLog 'pip install pytesseract Pillow'
```

**When user runs installer:**
- ✅ Python installed automatically
- ✅ Tesseract installed automatically
- ✅ Packages installed automatically
- ✅ Everything ready to use

**Current error = Development environment issue**

---

## 🚀 TÓM TẮT

**Vấn đề:** App không tìm thấy pytesseract

**Giải pháp nhanh:**
```batch
cd C:\desktop-app
install-python-packages.bat
```

**Hoặc manual:**
```batch
py -m pip install pytesseract Pillow
```

**Sau đó:**
- Restart app
- Test quét file
- Done!

---

**Chạy `install-python-packages.bat` ngay và báo kết quả!** 🚀
