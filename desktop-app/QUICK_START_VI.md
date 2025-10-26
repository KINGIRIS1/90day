# 🚀 Hướng Dẫn Nhanh - Desktop App

## 📥 Bước 1: Cài đặt (lần đầu tiên)

### 1.1. Cài đặt JavaScript dependencies
```bash
cd /app/desktop-app
yarn install
```
⏱️ Thời gian: ~2-3 phút

### 1.2. Cài đặt Python dependencies
```bash
cd /app/desktop-app/python
pip3 install -r requirements.txt
```
⏱️ Thời gian: ~5-10 phút (PaddleOCR khá nặng)

**Lưu ý quan trọng:**
- PaddleOCR cần Python 3.8+
- Trên Windows có thể cần Visual C++ Build Tools
- Nếu lỗi, thử cài từng package:
  ```bash
  pip3 install paddlepaddle
  pip3 install paddleocr
  pip3 install Pillow opencv-python-headless
  ```

## ▶️ Bước 2: Chạy ứng dụng (Development)

```bash
cd /app/desktop-app
yarn electron-dev
```

Lệnh này sẽ:
1. ✅ Khởi động React dev server (port 3000)
2. ✅ Mở cửa sổ Electron desktop app
3. ✅ Hot reload: tự động cập nhật khi sửa code

## 🎯 Bước 3: Sử dụng

### Quét với Offline OCR (Miễn phí)
1. Click **"📁 Chọn file"**
2. Chọn ảnh tài liệu đất đai
3. Click **"🔵 Offline OCR + Rules"**
4. Xem kết quả:
   - Loại tài liệu
   - Mã rút gọn
   - Độ tin cậy (85-88%)

### Dùng Cloud Boost (Nếu cần độ chính xác cao)
1. Vào **"⚙️ Cài đặt"**
2. Nhập Backend URL: `https://your-backend.com/api`
3. Lưu cài đặt
4. Quay lại tab quét, chọn **"☁️ Cloud Boost"**

## 📦 Bước 4: Đóng gói (Production Build)

### Build ứng dụng React
```bash
cd /app/desktop-app
yarn build
```

### Đóng gói cho platform hiện tại
```bash
yarn electron-build
```

Kết quả trong thư mục `dist/`:
- **Windows:** `Land Document Scanner Setup.exe`
- **macOS:** `Land Document Scanner.dmg`
- **Linux:** `Land Document Scanner.AppImage`

### Build cho nhiều platform
```bash
# Windows
yarn electron-build --win

# macOS  
yarn electron-build --mac

# Linux
yarn electron-build --linux
```

## 🧪 Test nhanh

### Test Python OCR engine
```bash
cd /app/desktop-app/python
python3 process_document.py /path/to/test-image.jpg
```

Kết quả mong đợi (JSON):
```json
{
  "success": true,
  "method": "offline_ocr",
  "doc_type": "Giấy chứng nhận quyền sử dụng đất",
  "short_code": "GCNQSD",
  "confidence": 0.85,
  "recommend_cloud_boost": false
}
```

## ❓ Troubleshooting

### Lỗi: Python không tìm thấy
```bash
# Kiểm tra
python3 --version  # Cần >= 3.8

# Hoặc
python --version
```

### Lỗi: Module paddleocr not found
```bash
# Cài lại
cd /app/desktop-app/python
pip3 install -r requirements.txt --force-reinstall
```

### Lỗi: Electron không mở
```bash
# Clear và cài lại
cd /app/desktop-app
rm -rf node_modules yarn.lock
yarn install
yarn electron-dev
```

### Lỗi: React không compile
```bash
# Kiểm tra port 3000 có bị chiếm không
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process nếu cần
```

## 📝 Development Tips

### Hot Reload
- **React code** (src/): Tự động reload
- **Electron main.js**: Cần restart `yarn electron-dev`
- **Python scripts**: Tự động load lại mỗi lần chạy

### Debug
- React DevTools: Tự động mở trong Electron
- Console logs: Xem trong Electron DevTools
- Python logs: In ra terminal

### Testing Flow
1. Sửa code React → Tự động reload
2. Test trong Electron window
3. Nếu ổn → commit
4. Build production để test cuối

## 🎓 Kiến trúc đơn giản

```
User clicks "Chọn file"
    ↓
Electron dialog.showOpenDialog()
    ↓
User chọn file
    ↓
User clicks "Offline OCR"
    ↓
Electron spawns Python script
    ↓
Python: PaddleOCR extract text
    ↓
Python: Rule Classifier classify
    ↓
Python: Return JSON result
    ↓
Electron receives result
    ↓
React displays result to user
```

## 📊 Performance

- **Offline OCR:** ~2-5 giây/ảnh (tùy kích thước)
- **Cloud Boost:** ~3-8 giây/ảnh (tùy network)
- **Batch processing:** Tuần tự, không parallel (tránh overload)

## 🔐 Bảo mật

- **Offline mode:** Dữ liệu 100% ở local
- **Cloud Boost:** Chỉ gửi ảnh khi user chọn
- **Config:** Lưu trong electron-store (encrypted)

## 📈 Roadmap Phase 2

- [ ] Parallel batch processing
- [ ] Progress bar chi tiết hơn
- [ ] Export results to Excel
- [ ] History management
- [ ] Custom rules UI
- [ ] Auto-update

---

**🎉 Xong! Desktop app đã sẵn sàng.**

Câu hỏi? Issues? → Tạo issue trên GitHub hoặc liên hệ team.
