# Hướng dẫn sử dụng tính năng "Quét theo danh sách"

## 📋 Tổng quan
Tính năng "Quét theo danh sách" cho phép bạn quét hàng loạt nhiều thư mục bằng cách upload file CSV hoặc Excel chứa danh sách đường dẫn thư mục.

## 🔧 Cài đặt

### Cài đặt thư viện Python (openpyxl) để đọc file Excel
```bash
pip install openpyxl
```

Hoặc nếu bạn dùng Python launcher trên Windows:
```bash
py -m pip install openpyxl
```

## 📝 Định dạng file đầu vào

### File CSV
Tạo file CSV với cột chứa đường dẫn thư mục. Tên cột có thể là:
- `folder_path`
- `path`
- `folder`
- `đường dẫn`
- `thu_muc`
- Hoặc bất kỳ tên nào (cột đầu tiên sẽ được dùng)

**Ví dụ file CSV (`folders.csv`):**
```csv
folder_path
D:\work\Documents\Folder A
D:\test\Hồ sơ 1
D:\test\Hồ sơ 2
E:\Land Documents\2024\January
```

### File Excel
Tạo file Excel (.xlsx hoặc .xls) với cột đầu tiên chứa đường dẫn thư mục.

**Ví dụ file Excel:**
| folder_path | (có thể có các cột khác) |
|-------------|--------------------------|
| D:\work\Documents\Folder A | ... |
| D:\test\Hồ sơ 1 | ... |
| D:\test\Hồ sơ 2 | ... |

**Lưu ý:**
- Dòng đầu tiên (header) sẽ bị bỏ qua
- Chỉ cột đầu tiên được đọc

## 🚀 Cách sử dụng

### Bước 1: Chuẩn bị file CSV/Excel
1. Tạo file CSV hoặc Excel chứa danh sách đường dẫn thư mục
2. Đảm bảo đường dẫn tồn tại và có quyền truy cập
3. Mỗi thư mục chỉ chứa file ảnh (.jpg, .jpeg, .png)

### Bước 2: Mở tab "Quét theo danh sách"
1. Mở ứng dụng 90dayChonThanh
2. Click vào tab **"📋 Quét danh sách"** ở menu trên cùng

### Bước 3: Chọn file CSV/Excel
1. Click nút **"📂 Chọn file"**
2. Chọn file CSV hoặc Excel đã chuẩn bị
3. App sẽ tự động phân tích và hiển thị:
   - Tổng số thư mục
   - Số thư mục hợp lệ
   - Số thư mục lỗi
   - Tổng số ảnh

### Bước 4: Chọn chế độ lưu kết quả
Có 3 chế độ:

#### 1. **Đổi tên tại chỗ** (Rename in place)
- File được đổi tên ngay tại thư mục gốc
- Ví dụ: `IMG_001.jpg` → `GCN_IMG_001.jpg`

#### 2. **Copy theo loại tài liệu** (Copy by document type)
- File được copy vào thư mục con theo loại tài liệu
- Ví dụ:
  ```
  D:\test\Hồ sơ 1\
    ├── GCN\
    │   ├── GCN_IMG_001.jpg
    │   └── GCN_IMG_002.jpg
    ├── HDCQ\
    │   └── HDCQ_IMG_003.jpg
  ```

#### 3. **Lưu vào thư mục khác** (Copy to custom folder)
- Tất cả file được copy vào 1 thư mục do bạn chọn
- Click **"Chọn thư mục"** để chọn thư mục đích

### Bước 5: Bắt đầu quét
1. Click nút **"🚀 Bắt đầu quét batch"**
2. Theo dõi tiến độ trên progress bar
3. Xem log để biết chi tiết quá trình xử lý

### Điều khiển trong quá trình quét

Khi đang quét, bạn có thể:

**⏸️ Tạm dừng (Pause):**
- Click nút "⏸️ Tạm dừng" để dừng tạm thời
- Progress bar chuyển sang màu cam
- File đang xử lý sẽ hoàn thành trước khi dừng
- Tiến độ được giữ nguyên

**▶️ Tiếp tục (Resume):**
- Click nút "▶️ Tiếp tục" để chạy lại
- Quá trình tiếp tục từ file tiếp theo
- Progress bar chuyển về màu xanh

**⏹️ Dừng (Stop):**
- Click nút "⏹️ Dừng" để dừng hoàn toàn
- Tất cả file đã xử lý vẫn được giữ lại
- Có thể bắt đầu lại từ đầu nếu muốn

## 📊 Hiểu kết quả

### Log Messages
- ✅ **Màu xanh**: Thành công
- ⚠️ **Màu vàng**: Cảnh báo (có thể tiếp tục)
- ❌ **Màu đỏ**: Lỗi
- ℹ️ **Màu xám**: Thông tin

### Thông báo lỗi thường gặp

#### "Folder does not exist"
- **Nguyên nhân**: Đường dẫn thư mục không tồn tại
- **Giải pháp**: Kiểm tra lại đường dẫn trong file CSV/Excel

#### "Permission denied"
- **Nguyên nhân**: Không có quyền truy cập thư mục
- **Giải pháp**: Chạy app với quyền Administrator hoặc kiểm tra quyền thư mục

#### "No folder paths found in file"
- **Nguyên nhân**: File CSV/Excel không có dữ liệu hoặc format sai
- **Giải pháp**: Kiểm tra lại format file (xem phần "Định dạng file đầu vào")

## 💡 Tips & Tricks

### 1. Test với thư mục nhỏ trước
Trước khi quét hàng loạt, hãy test với 2-3 thư mục nhỏ để đảm bảo mọi thứ hoạt động đúng.

### 2. Sao lưu dữ liệu
Luôn backup dữ liệu quan trọng trước khi quét hàng loạt, đặc biệt khi dùng chế độ "Đổi tên tại chỗ".

### 3. Đường dẫn tuyệt đối
Luôn dùng đường dẫn tuyệt đối (full path), không dùng đường dẫn tương đối.

**✅ Đúng:**
```
D:\work\Documents\Folder A
```

**❌ Sai:**
```
.\Folder A
../Documents/Folder A
```

### 4. Tránh ký tự đặc biệt
Tránh dùng các ký tự đặc biệt trong tên thư mục như: `|`, `<`, `>`, `:`, `*`, `?`, `"`, `\`, `/`

### 5. Thư mục con (sub-folders)
App **KHÔNG** quét đệ quy vào thư mục con. Nếu bạn muốn quét thư mục con, hãy thêm đường dẫn của chúng vào file CSV/Excel.

## 🔍 Xử lý lỗi

### Thư mục bị skip
- App tự động skip thư mục lỗi (không tồn tại, không có quyền truy cập)
- Log sẽ ghi lại chi tiết lỗi
- Quá trình quét tiếp tục với các thư mục còn lại

### Lỗi OCR
- Nếu OCR thất bại với một file, file đó được ghi lại trong results với `success: false`
- Các file khác vẫn được xử lý bình thường

## 📈 Hiệu suất

### Thời gian xử lý
- Mỗi ảnh mất khoảng 2-5 giây (tùy độ phức tạp)
- Với 100 ảnh: khoảng 3-8 phút
- Với 1000 ảnh: khoảng 30-80 phút

### Tối ưu hóa
- Đóng các ứng dụng không cần thiết
- Sử dụng ảnh có độ phân giải vừa phải (không cần quá cao)
- Tránh quét khi máy đang chạy task nặng khác

## ❓ Câu hỏi thường gặp (FAQ)

### Q: Tôi có thể quét file PDF không?
**A:** Hiện tại chỉ hỗ trợ file ảnh (.jpg, .jpeg, .png). File PDF sẽ bị bỏ qua.

### Q: Nếu tên file trùng thì sao?
**A:** App sẽ báo lỗi "Tên file đã tồn tại" và skip file đó.

### Q: Tôi có thể dừng hoặc tạm dừng quá trình quét không?
**A:** Có! Khi đang quét, bạn sẽ thấy 2 nút:
- **⏸️ Tạm dừng**: Dừng tạm thời, có thể tiếp tục sau
- **⏹️ Dừng**: Dừng hoàn toàn (dữ liệu đã xử lý vẫn được giữ lại)

### Q: Làm sao để quét thư mục con?
**A:** Thêm đường dẫn của từng thư mục con vào file CSV/Excel.

### Q: File CSV có thể có nhiều cột không?
**A:** Có, nhưng chỉ cột đầu tiên (chứa đường dẫn) được đọc.

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra log để xem lỗi cụ thể
2. Đảm bảo đã cài đặt đủ thư viện Python (openpyxl)
3. Kiểm tra định dạng file CSV/Excel
4. Liên hệ support nếu vấn đề vẫn tiếp diễn

---

**Phiên bản:** 1.0  
**Cập nhật lần cuối:** November 2024
