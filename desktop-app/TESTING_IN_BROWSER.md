# Testing Batch Scan trong Browser (Development)

## ⚠️ Giới hạn

Khi test trong browser (không phải Electron app):
- ❌ Không có `window.electronAPI`
- ❌ Không thể chọn files qua Electron dialog
- ❌ Không thể chạy Python scripts
- ❌ Không thể process documents
- ✅ Có thể xem UI
- ✅ Có thể test layout
- ✅ Có thể test buttons (nhưng sẽ lỗi khi click)

## 🌐 Access Browser Version

1. App đang chạy tại: **http://localhost:3001**
2. Click tab **"📋 Quét danh sách"**
3. Xem UI (buttons, layout, colors)

## 🖥️ Test đầy đủ trên Windows Desktop

Để test **đầy đủ** tính năng Batch Scan, bạn cần:

### Bước 1: Build installer
```bash
cd /app/desktop-app
yarn build
yarn dist:win
```

### Bước 2: Copy installer sang Windows
File installer sẽ ở: `/app/desktop-app/dist/`

### Bước 3: Cài đặt và chạy trên Windows
- Install app
- Chạy app
- Test tính năng Batch Scan

## 🔧 Workaround: Mock Electron APIs (Development)

Để test UI logic trong browser, thêm mock:

```javascript
// Thêm vào BatchScanner.js (tạm thời)
useEffect(() => {
  if (!window.electronAPI) {
    console.warn('⚠️ Running in browser mode - Electron APIs not available');
    // Mock APIs for testing
    window.electronAPI = {
      selectFile: async () => {
        alert('Mock: File selection (browser mode)');
        return { success: false, error: 'Browser mode' };
      },
      analyzeBatchFile: async () => {
        alert('Mock: Batch analysis (browser mode)');
        return { 
          success: true, 
          total_folders: 2,
          valid_folders: 2,
          invalid_folders: 0,
          total_images: 10,
          folders: [
            { path: '/test/folder1', valid: true, image_count: 5, images: [] },
            { path: '/test/folder2', valid: true, image_count: 5, images: [] }
          ]
        };
      },
      getConfig: async () => null,
      setConfig: async () => true,
      selectFolder: async () => ({ success: false }),
      processDocumentOffline: async () => ({ 
        success: true, 
        short_code: 'GCN', 
        confidence: 0.95 
      }),
      renameFile: async () => ({ success: true, newPath: '/test/renamed.jpg' })
    };
  }
}, []);
```

---

**Kết luận:** Bạn đang ở môi trường Linux server, không thể test đầy đủ Electron app. Cần build và test trên Windows desktop!
