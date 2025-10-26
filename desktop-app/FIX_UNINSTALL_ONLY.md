# 🔧 SỬA LỖI: Chỉ Có File Uninstall.exe

## ❌ Vấn Đề

Sau khi cài đặt installer, trong folder cài đặt chỉ có file `Uninstall.exe`, không có app.

---

## 🔍 Nguyên Nhân

Có 2 nguyên nhân chính:

### 1. Folder `dist/win-unpacked` không tồn tại
- Script build-allinone.bat build NSIS installer trước
- Nhưng chưa build Electron app
- Không có files để copy → chỉ có Uninstaller

### 2. NSIS script copy files không đúng
- Dùng `*.*` chỉ copy files, không copy folders
- App Electron cần cả files lẫn folders

---

## ✅ ĐÃ SỬA

### 1. Sửa installer.nsi

**Dòng 73 - TRƯỚC:**
```nsis
File /r "dist\win-unpacked\*.*"
```

**Dòng 73 - SAU:**
```nsis
File /r "dist\win-unpacked\*"
```

**Giải thích:** Bỏ `.` để copy cả files và folders

---

### 2. Cải thiện build-allinone.bat

**Thêm error checking và verification:**
- Check yarn build có thành công không
- Check yarn electron-pack có thành công không
- Verify dist/win-unpacked có .exe files không
- Hiển thị error rõ ràng nếu thiếu

---

### 3. Tạo script riêng: build-electron-only.bat

**Mục đích:** Build và test Electron app trước, tách biệt với NSIS

**Chạy:**
```batch
build-electron-only.bat
```

**Script sẽ:**
1. Check Node.js, Yarn
2. Install dependencies
3. Build React app
4. Build Electron app (unpacked)
5. Verify output có đầy đủ không
6. Hiển thị cấu trúc folder

---

## 🚀 CÁCH SỬA (STEP BY STEP)

### Bước 1: Build Electron App Riêng

```batch
cd desktop-app
build-electron-only.bat
```

**Kiểm tra kết quả:**
- Có folder `dist/win-unpacked/` không?
- Có file `.exe` trong folder đó không?
- Có các folders `locales`, `resources` không?

**Nếu thành công, bạn sẽ thấy:**
```
[OK] dist\win-unpacked\ exists
[OK] Found .exe files:
90dayChonThanh.exe

Folder structure:
└── dist\win-unpacked\
    ├── 90dayChonThanh.exe
    ├── locales\
    ├── resources\
    ├── ... (nhiều files khác)
```

---

### Bước 2: Verify Electron App

**Thử chạy app trực tiếp:**
```batch
cd dist\win-unpacked
90dayChonThanh.exe
```

**Nếu app mở được → OK! Sang bước 3**

**Nếu không mở được:**
- Check error trong console
- Có thể thiếu dependencies
- Xem logs

---

### Bước 3: Build NSIS Installer

```batch
cd desktop-app
build-allinone.bat
```

**Lần này sẽ có app files!**

---

### Bước 4: Test Installer

1. Uninstall bản cũ (nếu có)
2. Chạy installer mới
3. Check folder cài đặt

**Folder cài đặt nên có:**
```
C:\Program Files\90dayChonThanh\
├── 90dayChonThanh.exe        ← APP FILE
├── locales\
├── resources\
├── Uninstall.exe
└── ... (nhiều files khác)
```

---

## 🔍 DEBUG

### Check folder dist/win-unpacked có gì

```batch
cd desktop-app
dir /s dist\win-unpacked
```

**Nên thấy:**
- ✅ 90dayChonThanh.exe
- ✅ Folder locales/
- ✅ Folder resources/
- ✅ Nhiều .dll files
- ✅ node.exe (hoặc tương tự)

**Nếu thấy rỗng hoặc thiếu:**
→ electron-pack failed
→ Chạy lại `build-electron-only.bat` với chế độ verbose

---

### Chạy electron-pack với verbose

```batch
cd desktop-app
yarn build
yarn electron-pack --verbose
```

**Check logs để thấy lỗi gì**

---

## 📊 Cấu Trúc Đúng

### Electron app (dist/win-unpacked/)

```
dist/
└── win-unpacked/
    ├── 90dayChonThanh.exe         ← Main executable
    ├── chrome_100_percent.pak
    ├── chrome_200_percent.pak
    ├── d3dcompiler_47.dll
    ├── ffmpeg.dll
    ├── icudtl.dat
    ├── libEGL.dll
    ├── libGLESv2.dll
    ├── LICENSE.electron.txt
    ├── LICENSES.chromium.html
    ├── snapshot_blob.bin
    ├── v8_context_snapshot.bin
    ├── vk_swiftshader.dll
    ├── vk_swiftshader_icd.json
    ├── vulkan-1.dll
    ├── locales/                    ← Locale files
    │   ├── am.pak
    │   ├── en-US.pak
    │   ├── vi.pak
    │   └── ... (60+ locale files)
    ├── resources/                  ← App resources
    │   ├── app.asar                ← Your packed app
    │   └── python/                 ← Python scripts
    └── swiftshader/
        ├── libEGL.dll
        └── libGLESv2.dll
```

**Kích thước:** ~150-200 MB

---

### Sau khi NSIS installer chạy

```
C:\Program Files\90dayChonThanh\
├── 90dayChonThanh.exe         ← Từ dist/win-unpacked
├── chrome_100_percent.pak
├── ... (tất cả files từ win-unpacked)
├── locales/                    ← Folder được copy
├── resources/                  ← Folder được copy
│   ├── app.asar
│   └── python/
└── Uninstall.exe              ← NSIS tạo ra
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. Phải build Electron app TRƯỚC

**Workflow đúng:**
```
yarn install
→ yarn build (React)
→ yarn electron-pack (Electron app)
→ build-allinone.bat (NSIS installer)
```

**KHÔNG làm:**
```
build-allinone.bat ← Sai! Chưa có app
```

---

### 2. Folder win-unpacked rất quan trọng

- Đây là source cho NSIS installer
- NSIS copy TẤT CẢ từ folder này
- Nếu folder rỗng → installer cũng rỗng

---

### 3. Check trước khi build installer

**Trước khi chạy build-allinone.bat:**
```batch
# Check folder tồn tại
dir dist\win-unpacked

# Check có .exe
dir dist\win-unpacked\*.exe

# Check kích thước (phải >100MB)
```

**Nếu không thấy → Build electron-pack trước!**

---

## 🎯 SCRIPT MỚI TẠO

### build-electron-only.bat

**Mục đích:** Build và verify Electron app

**Khi nào dùng:**
- Lần đầu build
- Debug build issues
- Test app trước khi tạo installer

**Chạy:**
```batch
build-electron-only.bat
```

**Kết quả:**
- Build app
- Hiển thị cấu trúc folder
- Verify .exe tồn tại
- Báo lỗi rõ ràng nếu thiếu

---

## 📝 CHECKLIST SỬA LỖI

- [x] Sửa installer.nsi (*.* → *)
- [x] Cải thiện build-allinone.bat (thêm error checking)
- [x] Tạo build-electron-only.bat
- [ ] **Chạy build-electron-only.bat** ← BẠN Ở ĐÂY
- [ ] Verify dist/win-unpacked có đầy đủ
- [ ] Chạy build-allinone.bat
- [ ] Test installer mới
- [ ] Verify folder cài đặt có app files

---

## 🚀 TÓM TẮT NHANH

**Vấn đề:** Chỉ có Uninstall.exe  
**Nguyên nhân:** Electron app chưa được build  
**Giải pháp:**

```batch
# Bước 1: Build Electron app
build-electron-only.bat

# Bước 2: Verify có .exe files
dir dist\win-unpacked\*.exe

# Bước 3: Build installer
build-allinone.bat

# Bước 4: Test installer
```

---

**Files đã thay đổi:**
1. ✅ `installer.nsi` - Fixed file copy pattern
2. ✅ `build-allinone.bat` - Added verification
3. ✅ `build-electron-only.bat` - NEW script

---

**Chạy build-electron-only.bat và báo kết quả nhé!** 🚀
