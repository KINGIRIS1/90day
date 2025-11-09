# 📋 Batch Scan from List - Hướng dẫn sử dụng

## 🎯 Tổng quan

Tính năng **Quét theo danh sách** cho phép bạn quét nhiều thư mục cùng lúc bằng cách cung cấp file TXT chứa danh sách đường dẫn thư mục.

## 📄 Định dạng file TXT

File TXT đơn giản với **mỗi dòng là đường dẫn đến 1 thư mục**:

```
C:\Documents\HoSo001
C:\Documents\HoSo002
D:\TaiLieu\Batch2024
E:\Scan\ThangĐÈN
```

### ⚠️ Lưu ý quan trọng:
- **Chỉ quét file ảnh** JPG, JPEG, PNG
- **Không quét sub-folder** (chỉ quét file ở cấp thư mục được chỉ định)
- Thư mục không tồn tại hoặc không có ảnh sẽ bị **bỏ qua** và ghi log

## 🔧 Các chế độ Output

### 1️⃣ Lưu trong thư mục gốc (Same Folder)
- **Merge ảnh cùng loại** thành 1 file PDF
- Lưu PDF **ngay trong thư mục gốc**
- Ví dụ: `C:\Scan\Folder1\` → `C:\Scan\Folder1\HDCQ.pdf`, `C:\Scan\Folder1\GCNM.pdf`

**Khi nào dùng:**
- Bạn muốn giữ PDF ở vị trí hiện tại
- Không muốn tạo thêm thư mục

### 2️⃣ Lưu trong thư mục mới có suffix (New Folder)
- **Merge ảnh cùng loại** thành 1 file PDF
- Tạo thư mục mới **bên cạnh thư mục gốc** với suffix tùy chọn
- Ví dụ: `C:\Scan\Folder1\` → `C:\Scan\Folder1_merged\HDCQ.pdf`, `C:\Scan\Folder1_merged\GCNM.pdf`

**Khi nào dùng:**
- Bạn muốn **tổ chức riêng** file PDF
- Giữ nguyên thư mục gốc (không thay đổi)
- Tùy chọn suffix: `_merged`, `_output`, `_pdf`, etc.

### 3️⃣ Lưu trong thư mục chỉ định (Custom Folder)
- **Merge ảnh cùng loại** thành 1 file PDF
- Lưu trong **thư mục chỉ định**, tổ chức theo tên thư mục gốc
- Ví dụ: Output = `D:\Results\`
  - `C:\Scan\Folder1\` → `D:\Results\Folder1\HDCQ.pdf`, `D:\Results\Folder1\GCNM.pdf`
  - `C:\Scan\Folder2\` → `D:\Results\Folder2\HDCQ.pdf`, `D:\Results\Folder2\GCNM.pdf`

**Khi nào dùng:**
- Bạn muốn **tập trung** tất cả kết quả vào 1 nơi
- Tổ chức theo cấu trúc rõ ràng
- Backup/archive toàn bộ batch

## 📝 Hướng dẫn từng bước

### Bước 1: Chuẩn bị file TXT
```txt
# Ví dụ: folders.txt
C:\Documents\HoSo001
C:\Documents\HoSo002
C:\Documents\HoSo003
```

### Bước 2: Mở app và chọn tab "📋 Quét danh sách"

### Bước 3: Chọn file TXT
- Click nút **"📄 Chọn file TXT"**
- Chọn file TXT bạn đã chuẩn bị

### Bước 4: Xác nhận OCR Engine
- OCR engine được lấy từ **Cài đặt**
- Để thay đổi → vào tab **"⚙️ Cài đặt"**

### Bước 5: Chọn chế độ output
- **Đổi tên tại chỗ**: Không cần chọn thư mục đích
- **Copy theo loại** hoặc **Copy tất cả**: Click **"📁 Chọn thư mục đích"**

### Bước 6: Bắt đầu quét
- Click **"🚀 Bắt đầu quét"**
- Đợi quá trình hoàn tất (có thể mất vài phút)

### Bước 7: Xem kết quả
- **Thống kê**: Tổng thư mục, thư mục hợp lệ, files xử lý, lỗi
- **Thư mục bị bỏ qua**: Danh sách thư mục không hợp lệ + lý do
- **Lỗi xử lý**: Danh sách file lỗi + mô tả lỗi

## 📊 Ví dụ thực tế

### Ví dụ 1: Batch scan 3 thư mục với "Đổi tên tại chỗ"

**Input (folders.txt):**
```
C:\Scan\HoSo001
C:\Scan\HoSo002
C:\Scan\HoSo003
```

**Kết quả:**
```
C:\Scan\HoSo001\
  - HDCQ_image001.jpg (từ image001.jpg)
  - GCNM_image002.jpg (từ image002.jpg)

C:\Scan\HoSo002\
  - DKTC_doc001.jpg (từ doc001.jpg)
  - HDCQ_doc002.jpg (từ doc002.jpg)
```

### Ví dụ 2: Copy theo loại tài liệu

**Input (folders.txt):**
```
C:\Scan\Batch2024-01
C:\Scan\Batch2024-02
```

**Output folder:** `D:\Organized`

**Kết quả:**
```
D:\Organized\
  ├── HDCQ\
  │   ├── image001.jpg
  │   └── doc002.jpg
  ├── GCNM\
  │   └── image002.jpg
  └── DKTC\
      └── doc001.jpg
```

## 🔍 Xử lý lỗi

### Thư mục bị bỏ qua:
- ❌ Thư mục không tồn tại
- ❌ Đường dẫn không phải là thư mục
- ❌ Không có file ảnh (JPG, JPEG, PNG)

→ Các thư mục này sẽ được **ghi log** trong kết quả

### Lỗi xử lý file:
- ❌ File bị hỏng/không đọc được
- ❌ OCR thất bại
- ❌ Không đủ quyền ghi file

→ File lỗi sẽ được **bỏ qua**, tiếp tục xử lý file khác

## ⚙️ Cấu hình nâng cao

### OCR Engine
Batch scan sử dụng OCR engine từ **Cài đặt**:
- **Tesseract**: Nhanh, offline, 85-88% accuracy
- **EasyOCR**: Chậm hơn, offline, 90-92% accuracy
- **VietOCR**: Offline, tiếng Việt, 90-95% accuracy
- **Gemini Flash**: Cloud, AI, 93-97% accuracy (cần API key)

### Timeout
- Mỗi file: 60 giây
- Toàn bộ batch: 300 giây (5 phút)

## 🐛 Troubleshooting

### "Python 3.10–3.12 not found"
→ Cài đặt Python 3.10, 3.11, hoặc 3.12

### "API key not configured"
→ Nếu dùng Gemini Flash, vào **"☁️ Cloud OCR"** để thêm API key

### "Batch scan timeout"
→ Giảm số lượng folder trong file TXT hoặc tăng timeout

### File bị trùng tên
→ App tự động thêm số thứ tự: `HDCQ_file_1.jpg`, `HDCQ_file_2.jpg`

## 📋 Technical Details

### Files Created/Modified:
1. **NEW**: `/app/desktop-app/python/batch_scanner.py` - Python backend
2. **NEW**: `/app/desktop-app/src/components/BatchScanner.js` - React UI
3. **MODIFIED**: `/app/desktop-app/electron/main.js` - Added 2 IPC handlers
4. **MODIFIED**: `/app/desktop-app/electron/preload.js` - Exposed 2 APIs
5. **MODIFIED**: `/app/desktop-app/src/App.js` - Added "Batch Scan" tab

### IPC Communication:
```
Renderer → Main:
  - selectTxtFile()
  - processBatchScan(txtPath, outputOption, outputFolder)

Main → Python:
  - batch_scanner.py <txt_path> <ocr_engine> <api_key> <output_option> <output_folder>

Python → Main:
  - JSON result with statistics, errors, and file list
```

### Return Format:
```json
{
  "success": true,
  "total_folders": 3,
  "valid_folders": 2,
  "skipped_folders_count": 1,
  "total_files": 10,
  "processed_files": 8,
  "error_count": 2,
  "skipped_folders": [
    {"folder": "C:\\Invalid", "reason": "Thư mục không tồn tại"}
  ],
  "errors": [
    {"file": "C:\\Scan\\bad.jpg", "error": "File corrupted"}
  ],
  "results": [
    {
      "original_path": "C:\\Scan\\file1.jpg",
      "new_path": "C:\\Scan\\HDCQ_file1.jpg",
      "short_code": "HDCQ",
      "doc_type": "Hợp đồng chuyển nhượng",
      "confidence": 0.92,
      "folder": "C:\\Scan"
    }
  ]
}
```

## 💡 Tips & Best Practices

1. **Test với file TXT nhỏ trước** (2-3 thư mục)
2. **Backup data** trước khi dùng "Đổi tên tại chỗ"
3. **Kiểm tra đường dẫn** trong file TXT (tránh lỗi gõ)
4. **Dùng "Copy" modes** để an toàn hơn (giữ nguyên file gốc)
5. **Monitor console logs** trong dev mode để debug

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra log trong console (dev mode)
2. Kiểm tra kết quả "Thư mục bị bỏ qua" và "Lỗi xử lý"
3. Test với 1 thư mục đơn lẻ trước

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: 90dayChonThanh Desktop App
