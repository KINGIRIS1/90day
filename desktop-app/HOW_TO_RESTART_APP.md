# Cách Restart Ứng Dụng Để Load API Mới

## ⚠️ Khi nào cần restart?

Khi bạn thấy lỗi:
- `api.analyzeBatchFile is not a function`
- `api.selectFile is not a function`
- Hoặc bất kỳ API nào "is not a function"

## 🔄 Cách restart

### Nếu đang chạy từ Development (yarn start):

1. **Stop server:**
   - Mở terminal đang chạy `yarn start`
   - Nhấn `Ctrl + C` để dừng

2. **Restart:**
   ```bash
   cd /app/desktop-app
   yarn start
   ```

3. **Chờ app mở lại** (khoảng 10-20 giây)

### Nếu đang chạy từ file .exe (Packaged app):

1. **Đóng app:**
   - Click nút X để đóng cửa sổ
   - Hoặc Right-click trên taskbar → Close

2. **Mở lại:**
   - Double-click file `.exe` để mở lại app

## 🛠️ Development Commands

### Start Development Server:
```bash
cd /app/desktop-app
yarn start
```

### Kill tất cả process Electron (nếu bị treo):
```bash
# Windows
taskkill /F /IM electron.exe

# Linux/Mac
pkill -9 electron
```

### Rebuild app hoàn toàn:
```bash
cd /app/desktop-app
yarn build
```

## ✅ Xác nhận API đã load

Sau khi restart, mở DevTools (F12) và chạy:
```javascript
console.log('analyzeBatchFile:', typeof window.electronAPI.analyzeBatchFile);
console.log('selectFile:', typeof window.electronAPI.selectFile);
```

Kết quả mong đợi:
```
analyzeBatchFile: function
selectFile: function
```

Nếu vẫn hiển thị `undefined`, có vấn đề với preload.js.

## 🐛 Troubleshooting

### Lỗi vẫn còn sau khi restart?

**Kiểm tra 1: preload.js có đúng không?**
```bash
grep "analyzeBatchFile" /app/desktop-app/electron/preload.js
```
Phải có output: `analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),`

**Kiểm tra 2: main.js có IPC handler không?**
```bash
grep "analyze-batch-file" /app/desktop-app/electron/main.js
```
Phải có output: `ipcMain.handle('analyze-batch-file', async (event, csvFilePath) => {`

**Kiểm tra 3: Electron cache**
Xóa cache Electron:
```bash
rm -rf /app/desktop-app/node_modules/.cache
```

### App không mở được?

**Check port conflict:**
```bash
# Check if port 3001 is in use
lsof -i :3001

# Kill process on port 3001
kill -9 $(lsof -t -i:3001)
```

**Check logs:**
```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log

# Frontend logs (if applicable)
tail -f /var/log/supervisor/frontend.err.log
```

## 📝 Notes

- **Hot reload không áp dụng cho preload.js** - Bắt buộc phải restart
- **API mới luôn cần restart** - Không có cách nào khác
- **Rebuild app nếu deploy** - File .exe mới sẽ có API mới

## 🚀 Quick Restart Script (Optional)

Tạo file `restart.sh`:
```bash
#!/bin/bash
echo "Stopping Electron..."
pkill -9 electron
sleep 2
echo "Starting app..."
cd /app/desktop-app
yarn start
```

Chạy:
```bash
chmod +x restart.sh
./restart.sh
```

---

**Lưu ý quan trọng:** Mỗi lần thêm API mới vào preload.js, **BẮT BUỘC** phải restart app!
