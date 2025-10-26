# Land Document Scanner - Desktop App

Ứng dụng Desktop để quét và phân loại tài liệu đất đai với khả năng xử lý offline và tùy chọn cloud boost.

## ✨ Tính năng

### 🔵 Offline OCR (Mặc định)
- ✅ Xử lý hoàn toàn offline trên máy tính
- ✅ Không cần kết nối internet
- ✅ Hoàn toàn miễn phí
- ✅ Bảo mật: Dữ liệu không rời khỏi máy tính
- ✅ Độ chính xác: **85-88%**
- ✅ Sử dụng Tesseract OCR + Rule-based classification

### ☁️ Cloud Boost (Tùy chọn)
- ✅ Độ chính xác cao hơn: **93%+**
- ✅ Sử dụng GPT-4 Vision API
- ⚠️ Cần kết nối internet
- ⚠️ Có phí (theo API usage)
- ⚠️ Cần cấu hình Backend URL

## 🚀 Cài đặt & Chạy

### Yêu cầu hệ thống
- Node.js 16+ và Yarn
- Python 3.8+
- Windows, macOS hoặc Linux

### Bước 1: Cài đặt dependencies JavaScript

```bash
cd desktop-app
yarn install
```

### Bước 2: Cài đặt dependencies Python

**Cài đặt Tesseract OCR Binary:**

- **Windows:** Download và cài từ [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Đảm bảo chọn Vietnamese language pack khi cài đặt.
- **macOS:** `brew install tesseract tesseract-lang`
- **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-vie`

**Cài đặt Python packages:**

```bash
cd python
pip install -r requirements.txt
```

**Lưu ý:** Cài đặt rất nhanh, chỉ cần 2 packages nhẹ (pytesseract + Pillow).

### Bước 3: Chạy ở chế độ development

```bash
yarn electron-dev
```

Lệnh này sẽ:
1. Khởi động React development server
2. Mở ứng dụng Electron
3. Hot reload cho cả React và Electron

## 📦 Đóng gói ứng dụng

### Build cho platform hiện tại

```bash
yarn build
yarn electron-build
```

Ứng dụng sẽ được tạo trong thư mục `dist/`:
- **Windows:** `.exe` installer
- **macOS:** `.dmg` file
- **Linux:** `.AppImage` file

### Build cho platform cụ thể

```bash
# Windows
yarn electron-build --win

# macOS
yarn electron-build --mac

# Linux
yarn electron-build --linux
```

## 📖 Hướng dẫn sử dụng

### 1. Quét tài liệu với Offline OCR

1. Click **"Chọn file"** hoặc **"Chọn thư mục"**
2. Chọn các file ảnh hoặc PDF cần quét
3. Click **"Offline OCR + Rules"**
4. Xem kết quả với:
   - Loại tài liệu
   - Mã rút gọn
   - Độ tin cậy (confidence)

### 2. Sử dụng Cloud Boost

#### Cấu hình Backend URL (chỉ làm 1 lần)
1. Vào tab **"⚙️ Cài đặt"**
2. Nhập Backend URL (ví dụ: `https://your-backend.com/api`)
3. Click **"💾 Lưu cài đặt"**

#### Quét với Cloud Boost
1. Chọn file như bình thường
2. Click **"☁️ Cloud Boost (GPT-4)"**
3. Hệ thống sẽ gửi request lên backend để xử lý

### 3. Khi nào dùng Cloud Boost?

💡 **Gợi ý:**
- Dùng **Offline OCR** cho hầu hết các trường hợp
- Nếu độ tin cậy < 70%, ứng dụng sẽ hiện cảnh báo
- Dùng **Cloud Boost** cho các file quan trọng hoặc độ tin cậy thấp

## 🏗️ Kiến trúc

```
desktop-app/
├── electron/              # Electron main & preload
│   ├── main.js           # Main process
│   └── preload.js        # Preload script (IPC bridge)
├── python/               # Python OCR engine
│   ├── ocr_engine_tesseract.py  # Tesseract OCR wrapper
│   ├── rule_classifier.py       # Rule-based classification
│   └── process_document.py      # Main processing script
├── src/                  # React app
│   ├── components/
│   │   ├── DesktopScanner.js
│   │   └── Settings.js
│   ├── App.js
│   └── index.js
└── build/                # Production build (after yarn build)
```

## 🔧 Cấu trúc IPC

Electron sử dụng IPC (Inter-Process Communication) để giao tiếp:

### Renderer → Main Process

```javascript
// Chọn file
const filePaths = await window.electronAPI.selectFiles();

// Xử lý offline
const result = await window.electronAPI.processDocumentOffline(filePath);

// Lưu/đọc config
await window.electronAPI.setBackendUrl(url);
const url = await window.electronAPI.getBackendUrl();
```

### Main Process → Python

```javascript
// Spawn Python process
const pythonProcess = spawn('python3', ['process_document.py', filePath]);
```

## 🐛 Troubleshooting

### Python không tìm thấy
```bash
# Kiểm tra Python
python3 --version

# Hoặc trên Windows
python --version
```

### Tesseract OCR không hoạt động
```bash
# Kiểm tra Tesseract đã cài chưa
tesseract --version

# Nếu chưa có:
# Windows: Download từ https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract tesseract-lang
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### Electron không mở được
```bash
# Clear cache và rebuild
rm -rf node_modules
yarn install
yarn electron-dev
```

## 📊 So sánh Offline vs Cloud Boost

| Tiêu chí | Offline OCR | Cloud Boost |
|----------|-------------|-------------|
| Độ chính xác | 85-88% | 93%+ |
| Chi phí | Miễn phí | Có phí |
| Internet | Không cần | Cần |
| Bảo mật | Dữ liệu ở local | Gửi lên server |
| Tốc độ | Nhanh (local) | Chậm hơn (network) |

## 🎯 Roadmap

- [ ] Hỗ trợ quét batch thư mục lớn
- [ ] Export kết quả ra Excel/CSV
- [ ] History: lưu lịch sử quét
- [ ] Auto-update mechanism
- [ ] Multi-language support
- [ ] Custom rules configuration UI

## 📝 License

MIT License

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.
