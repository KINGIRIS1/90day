# 🚀 HƯỚNG DẪN CÀI ĐẶT - 90dayChonThanh Desktop App

## ✅ Hướng dẫn cài đặt hoàn chỉnh trên máy mới

---

## 📋 YÊU CẦU HỆ THỐNG

- **Hệ điều hành:** Windows 10/11 (64-bit)
- **Dung lượng:** ~500MB trống
- **RAM:** Tối thiểu 4GB
- **Internet:** Để download và sử dụng Cloud OCR

---

## 🔧 CÀI ĐẶT (4 BƯỚC)

### **BƯỚC 1: CÀI ĐẶT PYTHON** ⏱️ 5 phút

#### 1.1. Download Python

- Truy cập: https://www.python.org/downloads/
- Click nút **"Download Python 3.12.X"** (phiên bản mới nhất)
- Download file `.exe` (khoảng 25MB)

#### 1.2. Cài đặt Python

1. **Chạy file `.exe` vừa download**
2. ⚠️ **QUAN TRỌNG:** Tick ✅ **"Add Python to PATH"** (ô checkbox ở dưới cùng)
3. Click **"Install Now"**
4. Đợi cài đặt hoàn tất (2-3 phút)
5. Click **"Close"**

#### 1.3. Kiểm tra Python đã cài thành công

1. Nhấn `Windows + R`
2. Gõ: `cmd` → Enter
3. Trong cửa sổ Command Prompt, gõ:
   ```cmd
   python --version
   ```
4. **Kết quả mong đợi:** `Python 3.12.X`
5. Nếu thấy → ✅ Thành công! Tiếp tục bước 2

**Nếu báo lỗi "python not found":**
- Khởi động lại máy
- Thử lại lệnh trên
- Nếu vẫn lỗi: Cài lại Python và nhớ tick ✅ "Add Python to PATH"

---

### **BƯỚC 2: CÀI ĐẶT PYTHON LIBRARIES** ⏱️ 2 phút

#### 2.1. Mở Command Prompt

- Nhấn `Windows + R`
- Gõ: `cmd` → Enter

#### 2.2. Cài đặt các thư viện cần thiết

Copy và paste lệnh sau vào Command Prompt:

```cmd
pip install pdf2image pypdf Pillow
```

**Chờ cài đặt hoàn tất** (30 giây - 1 phút)

#### 2.3. Kiểm tra đã cài thành công

```cmd
python -c "import pdf2image; import pypdf; from PIL import Image; print('OK')"
```

**Kết quả mong đợi:** `OK`

---

### **BƯỚC 3: CÀI ĐẶT POPPLER** (Để quét PDF) ⏱️ 5 phút

#### 3.1. Download Poppler

- Truy cập: https://github.com/oschwartz10612/poppler-windows/releases
- Tìm phiên bản mới nhất (ví dụ: `Release-24.08.0-0`)
- Download file: `Release-XX.XX.X-X.zip` (khoảng 20MB)

#### 3.2. Extract Poppler

1. **Extract file `.zip`** vào vị trí bạn muốn
   - **Khuyên dùng:** `C:\Program Files\poppler`
   - Hoặc bất kỳ đâu (nhưng nhớ đường dẫn)

2. **Kết quả sau khi extract:**
   ```
   C:\Program Files\poppler\
     └── Library\
         └── bin\
             ├── pdftoppm.exe
             ├── pdftocairo.exe
             └── ... (các file khác)
   ```

#### 3.3. Thêm Poppler vào PATH

1. Nhấn `Windows + R`
2. Gõ: `sysdm.cpl` → Enter
3. Chọn tab **"Advanced"**
4. Click nút **"Environment Variables..."**
5. Trong phần **"System variables"** (ô dưới):
   - Tìm và click chọn dòng **"Path"**
   - Click **"Edit..."**
6. Click **"New"**
7. Thêm đường dẫn: `C:\Program Files\poppler\Library\bin`
   - (Nếu bạn extract vào chỗ khác, thay đường dẫn tương ứng)
8. Click **"OK"** → **"OK"** → **"OK"**

#### 3.4. Kiểm tra Poppler đã cài thành công

1. **Đóng tất cả cửa sổ Command Prompt cũ** (để load PATH mới)
2. Mở Command Prompt mới: `Windows + R` → `cmd`
3. Gõ:
   ```cmd
   pdftoppm -h
   ```
4. **Kết quả mong đợi:** Hiển thị help text của pdftoppm
5. Nếu thấy → ✅ Thành công!

**Nếu báo lỗi:**
- Kiểm tra lại đường dẫn PATH đã đúng chưa
- Khởi động lại máy và thử lại

---

### **BƯỚC 4: CÀI ĐẶT APP** ⏱️ 3 phút

#### 4.1. Cài đặt app

1. **Chạy file:** `90dayChonThanh-Setup-1.1.0.exe`
2. App sẽ tự động cài vào: `C:\Users\[TenBan]\AppData\Local\Programs\90daychonhanh-desktop`
3. Desktop shortcut sẽ được tạo tự động
4. Click **"Finish"**

#### 4.2. Khởi động app

- Double-click icon **"90dayChonThanh"** trên Desktop
- Hoặc tìm trong Start Menu

---

## ⚙️ CẤU HÌNH LẦN ĐẦU

### **Bước 1: Nhập Gemini API Key** (Nếu dùng Cloud OCR)

1. Mở app
2. Click **"Settings"** (biểu tượng bánh răng)
3. Chọn tab **"Cloud Settings"**
4. Paste **Gemini API Key** của bạn vào ô
5. Click **"Save"**

**Cách lấy Gemini API Key:**
- Truy cập: https://makersuite.google.com/app/apikey
- Đăng nhập bằng Google Account
- Click **"Create API Key"**
- Copy key và paste vào app

---

## 🧪 TEST APP

### Test 1: Quét ảnh đơn

1. Click **"Chọn Files"**
2. Chọn 1 file ảnh (JPG/PNG)
3. Click **"Quét"**
4. Chờ kết quả hiển thị (5-10 giây)

**✅ Thành công nếu:**
- Thấy preview ảnh
- Thấy loại tài liệu được phân loại

### Test 2: Quét PDF

1. Click **"Chọn Files"**
2. Chọn 1 file PDF (1-5 trang)
3. Click **"Quét"**
4. Chờ kết quả (10-30 giây tùy số trang)

**✅ Thành công nếu:**
- Thấy từng trang PDF hiển thị riêng
- Mỗi trang có preview và phân loại

---

## ❓ TROUBLESHOOTING

### ❌ Lỗi: "python not found" hoặc "pip not found"

**Nguyên nhân:** Python chưa được thêm vào PATH

**Giải pháp:**
1. Gỡ cài đặt Python (Settings → Apps → Python → Uninstall)
2. Cài lại Python
3. **Nhớ tick ✅ "Add Python to PATH"**

---

### ❌ Lỗi: "pdftoppm not found" khi quét PDF

**Nguyên nhân:** Poppler chưa được thêm vào PATH hoặc chưa cài

**Giải pháp:**
1. Kiểm tra Poppler đã extract đúng vị trí
2. Kiểm tra PATH đã thêm đúng: `C:\Program Files\poppler\Library\bin`
3. Khởi động lại máy
4. Test lại: `pdftoppm -h`

---

### ❌ Lỗi: "ModuleNotFoundError: No module named 'pdf2image'"

**Nguyên nhân:** Python libraries chưa được cài

**Giải pháp:**
```cmd
pip install pdf2image pypdf Pillow
```

---

### ❌ Lỗi: "ImportError: cannot import name '_imaging'"

**Nguyên nhân:** Pillow bị lỗi binary

**Giải pháp:**
```cmd
pip uninstall Pillow
pip install Pillow
```

---

### ❌ App không khởi động hoặc crash

**Giải pháp:**
1. Chạy app **as Administrator**:
   - Right-click icon app → **"Run as administrator"**
2. Tắt Antivirus tạm thời và thử lại
3. Cài lại app

---

### ❌ Quét ảnh OK nhưng quét PDF lỗi

**Nguyên nhân:** 99% do thiếu Poppler

**Giải pháp:**
- Xem lại **BƯỚC 3** và làm lại từ đầu
- Test Poppler: `pdftoppm -h`

---

## 📊 CHECKLIST HOÀN CHỈNH

### Trước khi test app:

- [ ] Python 3.12 đã cài (`python --version`)
- [ ] Python libraries đã cài (`python -c "import pdf2image; print('OK')"`)
- [ ] Poppler đã cài (`pdftoppm -h`)
- [ ] App đã cài và khởi động được
- [ ] Gemini API Key đã nhập (nếu dùng Cloud OCR)

### Test functions:

- [ ] Quét 1 ảnh thành công
- [ ] Quét nhiều ảnh thành công
- [ ] Quét PDF thành công
- [ ] Kết quả phân loại chính xác
- [ ] Export/Merge PDF hoạt động

---

## 💡 TIPS

### Tối ưu hiệu suất:

- **Sequential Mode:** Dùng cho < 10 files
- **Smart Batch Mode:** Dùng cho ≥ 10 files (tiết kiệm 80-90% chi phí AI)
- **Batch Size:** Đặt 8 là optimal

### Tiết kiệm chi phí:

- Smart Batch Mode tiết kiệm rất nhiều so với Sequential
- Enable "Resize images" trong Settings
- Sử dụng Batch size phù hợp với số lượng files

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề không giải quyết được:**

1. Chụp màn hình lỗi
2. Copy toàn bộ text lỗi (nếu có)
3. Ghi rõ bạn đang ở bước nào
4. Liên hệ hỗ trợ

---

## ✅ TÓM TẮT NHANH

**Máy mới cần cài:**

1. ✅ Python 3.12 (nhớ tick "Add to PATH")
2. ✅ pip install pdf2image pypdf Pillow
3. ✅ Poppler (extract + add to PATH)
4. ✅ App installer

**Tổng thời gian:** 15-20 phút

**Dung lượng:** ~500MB

---

**🎉 Chúc bạn sử dụng app thành công!**

Version: 1.1.0  
Build Date: 2025  
Platform: Windows 10/11 64-bit
