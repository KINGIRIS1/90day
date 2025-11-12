# 💾 Vị Trí Lưu Trữ Auto Save

## Tổng Quan

App sử dụng **electron-store** để lưu trữ dữ liệu local. Có 2 stores riêng biệt:

1. **config** - Cấu hình app (settings)
2. **scan-history** - Auto save scan data

## 📁 Vị Trí Lưu Trữ

### Windows:
```
C:\Users\<YourUsername>\AppData\Roaming\90daychonhanh-desktop\
├── config.json           # Cấu hình app
└── scan-history.json     # Auto save data
```

**Đường dẫn đầy đủ:**
```
%APPDATA%\90daychonhanh-desktop\scan-history.json
```

### macOS:
```
~/Library/Application Support/90daychonhanh-desktop/
├── config.json
└── scan-history.json
```

**Đường dẫn đầy đủ:**
```
/Users/<YourUsername>/Library/Application Support/90daychonhanh-desktop/scan-history.json
```

### Linux:
```
~/.config/90daychonhanh-desktop/
├── config.json
└── scan-history.json
```

**Đường dẫn đầy đủ:**
```
/home/<YourUsername>/.config/90daychonhanh-desktop/scan-history.json
```

---

## 📋 Cấu Trúc Dữ Liệu

### scan-history.json

```json
{
  "scans": {
    "scan_1705123456789": {
      "scanId": "scan_1705123456789",
      "type": "folder_scan",
      "timestamp": 1705123456789,
      "parentFolder": "/path/to/folder",
      "childTabs": [
        {
          "name": "Folder1",
          "path": "/path/to/folder/Folder1",
          "count": 50,
          "status": "done",
          "results": [
            {
              "fileName": "file1.jpg",
              "filePath": "/path/to/file1.jpg",
              "short_code": "GCNC",
              "confidence": 0.95,
              "previewUrl": null
            }
          ]
        }
      ]
    },
    "scan_1705123456790": {
      "scanId": "scan_1705123456790",
      "type": "batch_scan",
      "timestamp": 1705123456790,
      "folderTabs": [...],
      "fileResults": [...]
    }
  }
}
```

---

## 🔍 Cách Xem File

### Windows:

**Method 1: Gõ trong Start Menu**
```
%APPDATA%\90daychonhanh-desktop
```

**Method 2: Run Dialog (Win + R)**
```
%APPDATA%\90daychonhanh-desktop
```

**Method 3: File Explorer**
1. Mở File Explorer
2. Dán vào address bar: `%APPDATA%\90daychonhanh-desktop`
3. Enter

### macOS:

**Method 1: Finder → Go → Go to Folder (Shift + Cmd + G)**
```
~/Library/Application Support/90daychonhanh-desktop
```

**Method 2: Terminal**
```bash
cd ~/Library/Application\ Support/90daychonhanh-desktop
ls -lh
```

### Linux:

**Terminal:**
```bash
cd ~/.config/90daychonhanh-desktop
ls -lh
```

---

## 📊 Kích Thước File

### config.json
- Size: ~1-10 KB
- Content: Settings, preferences, API keys (encrypted)

### scan-history.json
- Size: ~10 KB - 50 MB+
- Content: Auto save scan data
- **Lưu ý:** File này có thể rất lớn nếu có nhiều scan chưa hoàn thành

**Breakdown:**
```
Small scan (1 folder, 20 files):     ~500 KB
Medium scan (5 folders, 100 files):  ~5 MB
Large scan (20 folders, 500 files):  ~50 MB
```

---

## 🛠️ Quản Lý Storage

### Xem Dung Lượng

**Windows:**
```cmd
dir "%APPDATA%\90daychonhanh-desktop"
```

**macOS/Linux:**
```bash
du -sh ~/Library/Application\ Support/90daychonhanh-desktop/*  # macOS
du -sh ~/.config/90daychonhanh-desktop/*                       # Linux
```

### Xóa Auto Save Data

**⚠️ Warning:** Sẽ mất tất cả scan chưa hoàn thành!

**Method 1: Trong App**
- Mở Resume Dialog
- Click "🗑️ Xóa" cho mỗi scan

**Method 2: Xóa File Trực Tiếp**

**Windows:**
```cmd
del "%APPDATA%\90daychonhanh-desktop\scan-history.json"
```

**macOS:**
```bash
rm ~/Library/Application\ Support/90daychonhanh-desktop/scan-history.json
```

**Linux:**
```bash
rm ~/.config/90daychonhanh-desktop/scan-history.json
```

### Backup Auto Save Data

**Windows:**
```cmd
copy "%APPDATA%\90daychonhanh-desktop\scan-history.json" "D:\backup\scan-history-backup.json"
```

**macOS/Linux:**
```bash
cp ~/Library/Application\ Support/90daychonhanh-desktop/scan-history.json ~/Desktop/scan-history-backup.json
```

### Restore Backup

**Windows:**
```cmd
copy "D:\backup\scan-history-backup.json" "%APPDATA%\90daychonhanh-desktop\scan-history.json"
```

**macOS/Linux:**
```bash
cp ~/Desktop/scan-history-backup.json ~/Library/Application\ Support/90daychonhanh-desktop/scan-history.json
```

---

## 🔧 Troubleshooting

### Issue 1: "Không tìm thấy file scan-history.json"

**Cause:** Chưa có scan nào được save.

**Solution:** File sẽ được tạo tự động khi có scan đầu tiên.

### Issue 2: "File quá lớn"

**Cause:** Nhiều scan chưa hoàn thành lưu lại.

**Solution:**
1. Xóa các scan cũ không cần thiết
2. Hoàn thành các scan đang pending
3. Hoặc xóa file `scan-history.json` (mất data)

### Issue 3: "Không load được scan"

**Possible causes:**
- File bị corrupt
- JSON không hợp lệ
- File bị lock bởi process khác

**Solution:**
1. Check file có mở được bằng text editor không
2. Validate JSON: https://jsonlint.com/
3. Backup và xóa file cũ, để app tạo mới

### Issue 4: "Auto save không hoạt động"

**Check:**
1. App có quyền ghi file không?
2. Disk có đủ dung lượng không?
3. Check console log có error không?

**Debug:**
```javascript
// Open DevTools Console
console.log('Save path:', await window.electronAPI.getConfigPath());
```

---

## 📖 API Reference

### Save Scan State
```javascript
await window.electronAPI.saveScanState({
  scanId: 'scan_1705123456789',
  type: 'folder_scan',
  timestamp: Date.now(),
  // ... other data
});
```

### Get Incomplete Scans
```javascript
const scans = await window.electronAPI.getIncompleteScans();
// Returns: [{ scanId, type, timestamp, ... }]
```

### Load Scan State
```javascript
const result = await window.electronAPI.loadScanState(scanId);
// Returns: { success: true, data: {...} }
```

### Delete Scan State
```javascript
await window.electronAPI.deleteScanState(scanId);
```

### Mark Scan Complete
```javascript
await window.electronAPI.markScanComplete(scanId);
```

---

## 🔐 Security & Privacy

### Data Stored:
- ✅ File paths (local)
- ✅ Scan results (classifications)
- ✅ Timestamps
- ❌ NO file contents
- ❌ NO images (only paths)
- ❌ NO sensitive personal data

### Encryption:
- Config: Encrypted (API keys)
- Scan history: Plain JSON (file paths only)

### Permissions:
- Read/Write: `%APPDATA%\90daychonhanh-desktop`
- Read: File paths trong scan folders

---

## 📝 Notes

1. **Preview URLs:**
   - KHÔNG được lưu trong auto save (quá lớn)
   - Set to `null` khi save
   - Load lại on-demand khi resume

2. **File Paths:**
   - Lưu absolute paths
   - Nếu file bị di chuyển/xóa → preview không load được
   - Scan results vẫn có thể dùng (có data)

3. **Storage Limits:**
   - electron-store: No hard limit
   - Limited by disk space
   - Recommend: < 100 MB per file

4. **Auto Cleanup:**
   - App KHÔNG tự động xóa old scans
   - User phải manually delete
   - Consider adding auto-cleanup feature (future)

---

**Last Updated:** 12/01/2025  
**Version:** 1.3.0  
**App Name:** 90daychonhanh-desktop
