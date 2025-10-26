# 📖 Hướng Dẫn Sử Dụng - 90dayChonThanh Desktop App

## 🎯 Giới Thiệu

**90dayChonThanh Desktop App** là ứng dụng quét và phân loại tài liệu đất đai bằng tiếng Việt.

### ✨ Tính Năng Chính

- ✅ **Quét Offline:** OCR miễn phí, không cần internet (85-88% accuracy)
- ✅ **Cloud Boost:** Tăng độ chính xác lên 93%+ (có phí, cần API key)
- ✅ **Tự động phân loại:** Nhận diện loại tài liệu và đặt tên file
- ✅ **Quét hàng loạt:** Quét cả folder nhiều file cùng lúc
- ✅ **Xuất PDF:** Gộp nhiều tài liệu thành 1 file PDF
- ✅ **Quản lý Rules:** Tùy chỉnh quy tắc phân loại

---

## 💿 Cài Đặt (Lần Đầu)

### Bước 1: Download Installer

File: `90dayChonThanh-AllInOne-Setup.exe` (~235MB)

### Bước 2: Chạy Installer

1. **Double-click** file `90dayChonThanh-AllInOne-Setup.exe`
2. Nếu Windows hỏi "User Account Control" → Click **Yes**
3. Click **Next** → **I Agree** → **Next**
4. Đợi cài đặt (5-10 phút)
5. Click **Finish**

### Bước 3: Mở App

- **Cách 1:** Double-click icon trên Desktop
- **Cách 2:** Start Menu → 90dayChonThanh

---

## 🚀 Hướng Dẫn Sử Dụng

### 1️⃣ Quét Một File

**Bước 1:** Click tab "**Scan Documents**"

**Bước 2:** Click "**📂 Select File**"

**Bước 3:** Chọn file ảnh (JPG, PNG, PDF, ...)

**Bước 4:** Chọn chế độ quét:

- **Offline OCR (Free):** Click "**🔍 Process Offline**"
  - Miễn phí, không cần internet
  - 85-88% accuracy
  - Nhanh, tức thì

- **Cloud Boost (Paid):** Click "**☁️ Process with Cloud Boost**"
  - Cần API key OpenAI
  - 93%+ accuracy
  - Chậm hơn, có phí

**Bước 5:** Xem kết quả:

- ✅ Loại tài liệu được nhận diện
- ✅ Tên file được đề xuất
- ✅ Preview ảnh
- ✅ Raw OCR text (debug)

**Bước 6:** Lưu file

- Click "**💾 Save**" để lưu với tên đề xuất
- Hoặc sửa tên trước khi lưu

---

### 2️⃣ Quét Hàng Loạt (Folder)

**Bước 1:** Click "**📁 Select Folder**"

**Bước 2:** Chọn folder chứa nhiều ảnh

**Bước 3:** App tự động quét từng file

**Bước 4:** Xem tiến độ:

```
Processing: 5/20 files
✓ GCN-001.jpg → Giấy chứng nhận
✓ SODO-002.jpg → Sơ đồ
⏳ DKD-003.jpg → Processing...
```

**Bước 5:** Review kết quả từng file trong tabs

**Bước 6 (Optional):** Gộp PDF

- Click "**📄 Merge to PDF**"
- Chọn files muốn gộp
- Nhập tên PDF
- Done!

---

### 3️⃣ Cấu Hình Settings

Click tab "**Settings**" để:

#### A. OCR Engine

```
✅ Tesseract OCR (Default)
  - Free, offline
  - 85-88% accuracy
```

#### B. Cloud Boost (Optional)

**Để sử dụng Cloud Boost:**

1. Cần OpenAI API Key
2. Vào: https://platform.openai.com/api-keys
3. Copy API key
4. Paste vào "**OpenAI API Key**"
5. Click "**Save Settings**"

**Lưu ý:**
- Mỗi lần quét cloud boost tốn ~$0.01-0.05
- Kiểm tra balance: https://platform.openai.com/usage

#### C. Output Settings

- **Save Directory:** Folder lưu kết quả
- **Naming Format:** Format tên file
- **Sequential Numbering:** Đánh số tự động

---

### 4️⃣ Quản Lý Rules

Click tab "**Rules**" để:

#### Xem Rules Hiện Tại

```
📋 Các loại tài liệu:
- Giấy chứng nhận QSD đất (GCN)
- Sơ đồ địa chính (SODO)
- Đơn đăng ký (DKD)
- ... (15+ loại khác)
```

#### Thêm Rule Mới

1. Click "**+ Add New Rule**"
2. Nhập thông tin:
   - **Document Type:** Tên loại tài liệu
   - **Short Code:** Mã viết tắt (VD: GCN)
   - **Keywords:** Từ khóa nhận diện (mỗi từ 1 dòng)
   - **Priority:** Độ ưu tiên (1-100)
3. Click "**💾 Save Rule**"

#### Sửa Rule

1. Click "**✏️ Edit**" ở rule muốn sửa
2. Sửa thông tin
3. Click "**💾 Update Rule**"

#### Xóa Rule

1. Click "**🗑️ Delete**" ở rule muốn xóa
2. Confirm → Deleted

#### Auto-generate Variants

**Tính năng:** Tự động tạo biến thể từ khóa

Ví dụ:
```
Input: giấy chứng nhận
Output:
- giấy chứng nhận
- Giấy Chứng Nhận
- GIẤY CHỨNG NHẬN
- giay chung nhan (không dấu)
- giaychungnhan (không space)
```

**Cách dùng:**
1. Nhập 1 từ khóa cơ bản
2. Check "**🔄 Auto-generate variants**"
3. App tự tạo 10+ biến thể

#### Import/Export Rules

**Export (Backup):**
1. Click "**📤 Export Rules**"
2. Save file JSON
3. Giữ file để backup

**Import (Restore):**
1. Click "**📥 Import Rules**"
2. Chọn file JSON đã export
3. Rules được khôi phục

#### Reset to Default

1. Click "**🔄 Reset to Default**"
2. Confirm
3. Rules về mặc định

---

## 💡 Tips & Tricks

### Tăng Accuracy

1. **Dùng ảnh chất lượng cao:**
   - Resolution: 300+ DPI
   - Format: JPG, PNG (không nén quá)
   - Màu: Đen trắng hoặc màu tốt

2. **Scan똑바로:**
   - Không nghiêng
   - Đầy đủ nội dung
   - Sáng đủ, không tối

3. **Tinh chỉnh keywords:**
   - Thêm từ khóa phổ biến
   - Dùng auto-generate variants
   - Tăng priority cho rule quan trọng

### Xử Lý Lỗi

**Lỗi: "Python not found"**
```
Fix:
1. Restart máy tính
2. Hoặc reinstall app
```

**Lỗi: "Tesseract not found"**
```
Fix:
1. Check: C:\Program Files\Tesseract-OCR\
2. Nếu không có → reinstall app
```

**Lỗi: "OpenAI API error"**
```
Fix:
1. Check API key đúng không
2. Check balance còn không
3. Check internet connection
```

**OCR kết quả sai:**
```
Fix:
1. Thử Cloud Boost
2. Scan lại ảnh chất lượng cao hơn
3. Thêm keywords vào rules
```

---

## 🔧 Advanced Usage

### Command Line (Dev)

```batch
# Run in dev mode
yarn electron-dev

# Build app
yarn build
yarn electron-build

# Test Python script
cd python
python process_document.py test.jpg
```

### Custom Rules File

Rules được lưu tại:
```
%APPDATA%\90dayChonThanh\rules\classification_rules.json
```

Có thể edit trực tiếp file JSON (advanced users)

### Batch Processing Script

Tạo file `batch_process.bat`:
```batch
@echo off
for %%f in (*.jpg) do (
    python python\process_document.py "%%f"
)
```

---

## 📊 Performance

| Chế độ | Accuracy | Speed | Cost | Internet |
|--------|----------|-------|------|----------|
| Offline OCR | 85-88% | 1-2s/file | Free | ❌ |
| Cloud Boost | 93%+ | 5-10s/file | ~$0.01-0.05 | ✅ |

**Khuyến nghị:**
- Dùng **Offline** cho khối lượng lớn
- Dùng **Cloud Boost** cho tài liệu quan trọng

---

## 🆘 Support

### Liên Hệ

- **Email:** support@90daychonthanh.com
- **Website:** https://90daychonthanh.com
- **Hotline:** (Số điện thoại)

### Báo Lỗi

Khi báo lỗi, vui lòng cung cấp:
1. Version app (Settings → About)
2. Screenshot lỗi
3. File ảnh test (nếu có)
4. Mô tả chi tiết

### Yêu Cầu Tính Năng

Submit tại: https://github.com/yourrepo/issues

---

## 📝 Gỡ Cài Đặt

### Cách 1: Windows Settings

1. Settings → Apps → Apps & features
2. Tìm "90dayChonThanh"
3. Click → Uninstall

### Cách 2: Control Panel

1. Control Panel → Programs → Uninstall a program
2. Chọn "90dayChonThanh"
3. Uninstall

### Xóa Dữ Liệu

App data tại:
```
C:\Users\[User]\AppData\Roaming\90dayChonThanh\
```

Xóa folder này để xóa hoàn toàn settings và rules.

---

## 🎉 Changelog

### v1.0.0 (Current)
- ✅ Tesseract OCR offline
- ✅ Cloud Boost (GPT-4 Vision)
- ✅ Batch processing
- ✅ Rules Manager
- ✅ Auto keyword variants
- ✅ PDF export
- ✅ All-in-one installer

---

## 📜 License

MIT License

Copyright (c) 2024 90dayChonThanh

---

**Chúc bạn sử dụng app hiệu quả! 🚀**
