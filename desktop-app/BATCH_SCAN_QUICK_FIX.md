# ⚡ Quick Fix: Lỗi API Batch Scan

## 🔴 Lỗi hiện tại

```
❌ Lỗi phân tích file: api.analyzeBatchFile is not a function
```

## ✅ Giải pháp (3 bước - 30 giây)

### Bước 1: Dừng app hiện tại
- **Nếu chạy từ terminal:** Nhấn `Ctrl + C`
- **Nếu chạy từ .exe:** Đóng cửa sổ app

### Bước 2: Xác nhận code đã đúng
```bash
# Check preload.js
grep "analyzeBatchFile" /app/desktop-app/electron/preload.js
# Phải thấy: analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),

# Check main.js
grep "analyze-batch-file" /app/desktop-app/electron/main.js
# Phải thấy: ipcMain.handle('analyze-batch-file', async (event, csvFilePath) => {
```

✅ Nếu cả 2 đều có output → Code đã đúng, chỉ cần restart!

### Bước 3: Restart app
```bash
cd /app/desktop-app
yarn start
```

**Chờ 10-20 giây** để app khởi động lại.

---

## 🧪 Kiểm tra sau khi restart

### Option 1: Dùng DevTools (Nhanh)
1. Mở app
2. Nhấn `F12` để mở DevTools
3. Gõ vào Console:
```javascript
console.log(typeof window.electronAPI.analyzeBatchFile);
```
4. Kết quả mong đợi: `function`

### Option 2: Dùng Check Tool (Chi tiết)
1. Mở file `CHECK_APIS.html` trong app
2. Xem danh sách APIs
3. Tất cả phải có ✅

---

## ❓ Vẫn lỗi sau khi restart?

### Xóa cache Electron:
```bash
rm -rf /app/desktop-app/node_modules/.cache
cd /app/desktop-app
yarn start
```

### Rebuild hoàn toàn:
```bash
cd /app/desktop-app
rm -rf node_modules
yarn install
yarn start
```

### Check port conflict:
```bash
# Kill process trên port 3001
lsof -i :3001
kill -9 $(lsof -t -i:3001)
```

---

## 🎯 Tại sao phải restart?

**Electron caching:**
- `preload.js` được load 1 lần khi app khởi động
- Thay đổi `preload.js` KHÔNG tự động reload
- Hot reload chỉ work cho React code, KHÔNG work cho Electron code

**API mới được thêm:**
- `selectFile` (line 9 trong preload.js)
- `analyzeBatchFile` (line 52 trong preload.js)

---

## ✅ Sau khi fix xong

Bạn sẽ thấy:
1. ✅ Tab "📋 Quét danh sách" hoạt động
2. ✅ Nút "Chọn file" hoạt động
3. ✅ Batch analysis hiển thị đúng
4. ✅ Pause/Resume/Stop buttons hoạt động

---

## 📞 Cần thêm hỗ trợ?

Xem chi tiết trong:
- `HOW_TO_RESTART_APP.md` - Hướng dẫn restart đầy đủ
- `BATCH_SCAN_GUIDE.md` - User guide
- `BATCH_SCAN_FEATURE.md` - Technical docs

---

**TL;DR: Ctrl+C → yarn start → Đợi 20s → Done! ✅**
