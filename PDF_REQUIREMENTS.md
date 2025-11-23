# 📄 Yêu cầu để quét PDF

## ✅ Những gì đã có sẵn trong App

App đã bundle các Python libraries:
- ✅ `pdf2image` - Convert PDF → Images
- ✅ `pypdf` - PDF manipulation
- ✅ `Pillow (PIL)` - Image processing
- ✅ Python scripts để xử lý PDF

→ **Không cần cài thêm Python packages!**

---

## ⚠️ Yêu cầu BẮT BUỘC: Poppler

### Poppler là gì?
Poppler là một bộ công cụ để render và xử lý PDF.
`pdf2image` library cần Poppler để convert PDF → images.

### 🪟 Cài đặt trên Windows

#### Option 1: Download Binary (Đề xuất)
1. **Download Poppler**:
   - Tải tại: https://github.com/oschwartz10612/poppler-windows/releases
   - Chọn: `Release-24.08.0-0.zip` (hoặc latest)
   
2. **Extract**:
   ```
   Extract vào: C:\Program Files\poppler
   ```
   
3. **Add to PATH**:
   - Mở System Properties → Environment Variables
   - Edit `Path` variable
   - Thêm: `C:\Program Files\poppler\Library\bin`
   - Click OK

4. **Verify**:
   ```cmd
   pdftoppm -h
   ```
   Nếu thấy help text → Thành công! ✅

#### Option 2: Conda (Nếu có Anaconda)
```cmd
conda install -c conda-forge poppler
```

#### Option 3: Chocolatey
```cmd
choco install poppler
```

---

## 🐧 Cài đặt trên Linux

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

### Fedora/RHEL:
```bash
sudo dnf install poppler-utils
```

### Arch:
```bash
sudo pacman -S poppler
```

---

## 🍎 Cài đặt trên macOS

### Homebrew:
```bash
brew install poppler
```

---

## 🧪 Kiểm tra Poppler đã cài chưa

### Windows:
```cmd
where pdftoppm
```

### Linux/Mac:
```bash
which pdftoppm
```

**Nếu thấy path** → Đã cài ✅
**Nếu không thấy** → Chưa cài hoặc chưa add vào PATH ❌

---

## ⚙️ Cách App sử dụng Poppler

### Flow xử lý PDF:

```
1. User chọn PDF file
   ↓
2. Python script gọi pdf_splitter.py
   ↓
3. pdf_splitter.py sử dụng pdf2image
   ↓
4. pdf2image gọi Poppler command:
   pdftoppm -png -r 200 input.pdf output
   ↓
5. Poppler convert PDF → PNG images (1 file/page)
   ↓
6. App xử lý images như bình thường
```

**Nếu không có Poppler** → App sẽ báo lỗi khi quét PDF!

---

## 🚨 Troubleshooting

### Lỗi: "pdftoppm not found"
**Nguyên nhân**: Poppler chưa được cài hoặc chưa có trong PATH

**Giải pháp**:
1. Verify Poppler đã cài: `pdftoppm -h`
2. Nếu chưa → Cài theo hướng dẫn trên
3. Nếu đã cài nhưng vẫn lỗi → Check PATH environment variable

### Lỗi: "Unable to open file"
**Nguyên nhân**: PDF file bị lock hoặc corrupted

**Giải pháp**:
1. Đóng PDF nếu đang mở trong Adobe Reader
2. Thử PDF khác để test
3. Kiểm tra file permissions

### Lỗi: "Conversion failed"
**Nguyên nhân**: PDF quá lớn hoặc có vấn đề

**Giải pháp**:
1. Thử PDF nhỏ hơn (< 100 trang)
2. Giảm DPI nếu có option (default: 200)
3. Kiểm tra disk space

---

## 📊 Settings trong App

Sau khi cài Poppler, trong app Settings:

### OCR Settings:
- **Batch Mode**: Sequential / Smart
- **Batch Size**: 2-20 files (cho Smart mode)
- **Enable Resize**: ON (để optimize)

### PDF Processing:
- **Auto split**: ON (tự động tách pages)
- **DPI**: 200 (default, đủ cho OCR)
- **Timeout**: 300s (5 phút)

---

## ✅ Checklist Setup hoàn chỉnh

### Để app hoạt động đầy đủ:

- [ ] **App installed**: 90dayChonThanh.exe
- [ ] **Poppler installed**: `pdftoppm -h` OK
- [ ] **Gemini API Key**: Nhập trong Settings → Cloud Settings
- [ ] **Internet**: Connected

### Để quét PDF:

- [ ] Poppler trong PATH
- [ ] PDF file không bị lock
- [ ] Có đủ disk space cho temp files

---

## 🎯 Quick Start

1. **Cài Poppler** (nếu chưa)
2. **Mở app**
3. **Vào Settings** → Cloud Settings → Nhập API key
4. **Chọn PDF file** (hoặc folder)
5. **Click "Quét"**
6. **Chờ kết quả** (hiển thị preview từng trang)

---

## 💡 Tips

### Tối ưu Performance:
- PDF < 50 trang: Dùng Sequential mode
- PDF 50-100 trang: Dùng Smart mode (batch 8)
- PDF > 100 trang: Dùng Smart mode (batch 5-8)

### Tiết kiệm Chi phí:
- Smart batch mode tiết kiệm 80-90% so với Sequential
- Resize images before OCR (auto enabled)
- Batch size 8 là optimal

### Tránh Timeout:
- PDF > 100 trang có thể mất 3-5 phút
- Timeout đã set 300s (đủ cho ~150 trang)
- Nếu vẫn timeout → Giảm batch size hoặc chia PDF nhỏ hơn

---

## 📞 Support

**Lỗi không tìm được giải pháp?**
1. Check logs trong app console
2. Verify Poppler: `pdftoppm -version`
3. Test với PDF đơn giản (1-2 trang)
4. Báo lỗi với full error message

---

**Poppler version recommended**: 23.x hoặc 24.x
**Python version**: 3.8+ (bundled)
**Disk space cần**: ~100MB cho temp files khi xử lý PDF lớn
