# 🔧 BYOK FEATURE - INSTALLATION & SETUP GUIDE

## 📦 STEP 1: Install Dependencies

### Trong thư mục `/app/desktop-app/`:

```bash
# Install Google Cloud Vision SDK
npm install @google-cloud/vision

# Install Azure Computer Vision SDK  
npm install @azure/cognitiveservices-computervision @azure/ms-rest-js

# Verify installation
npm list @google-cloud/vision @azure/cognitiveservices-computervision
```

**Kích thước:**
- @google-cloud/vision: ~15MB
- @azure packages: ~5MB
- Total: ~20MB added to node_modules

---

## 📝 IMPLEMENTATION CHECKLIST

### ✅ Phase 1: Backend (Electron Main Process)
- [x] Setup electron-store with encryption
- [ ] Create IPC handlers: save-api-key, get-api-key, delete-api-key
- [ ] Create IPC handler: test-api-key (Google)
- [ ] Create IPC handler: test-api-key (Azure)
- [ ] Create IPC handler: cloud-boost-google
- [ ] Create IPC handler: cloud-boost-azure
- [ ] Update preload.js với new APIs

### ✅ Phase 2: Frontend (React)
- [ ] Create Settings.js component
- [ ] Add route cho Settings page
- [ ] Update DesktopScanner để chọn OCR engine
- [ ] Add notification cho API key errors
- [ ] Add loading states

### ✅ Phase 3: Documentation
- [ ] Hướng dẫn lấy Google Cloud Vision API key
- [ ] Hướng dẫn lấy Azure Vision API key
- [ ] User guide trong app
- [ ] Troubleshooting guide

### ✅ Phase 4: Testing
- [ ] Test Google Vision integration
- [ ] Test Azure Vision integration
- [ ] Test API key validation
- [ ] Test error handling
- [ ] Test với user scenarios

---

## 🔒 SECURITY NOTES

### API Key Encryption:

```javascript
// electron-store với encryption
const Store = require('electron-store');

const store = new Store({
  name: 'user-settings',
  encryptionKey: 'your-32-char-encryption-key-here!', // CHANGE THIS!
  defaults: {
    ocrEngine: 'offline-tesseract',
    apiKeys: {}
  }
});
```

**⚠️ QUAN TRỌNG:**
- Thay đổi `encryptionKey` thành key riêng của anh
- Key phải 32 characters
- Không commit key vào git

---

## 📊 ARCHITECTURE

```
User Input API Key
      ↓
  Frontend (Settings.js)
      ↓
  IPC: saveApiKey()
      ↓
  Electron Main Process
      ↓
  electron-store (encrypted)
      ↓
  Saved to disk

---

User Scans Image
      ↓
  Frontend: Chọn engine
      ↓
  IPC: cloudBoostGoogle() hoặc cloudBoostAzure()
      ↓
  Main Process: Load API key
      ↓
  Call Google/Azure API với user's key
      ↓
  Return result
      ↓
  Frontend: Display
```

---

## 🚀 DEPLOYMENT NOTE

Khi build app:
```bash
# Dependencies sẽ được bundle vào app
npm run electron-build

# Kiểm tra bundle size
# Google Cloud Vision SDK khá lớn (~15MB)
# Có thể tăng app size từ 150MB → 170MB
```

---

## 💡 NEXT STEPS

Sau khi install dependencies:
1. Em sẽ tạo Settings component
2. Update Electron main.js với IPC handlers
3. Integrate Google Cloud Vision
4. Integrate Azure Vision
5. Test toàn bộ flow

Anh confirm đã chạy `npm install` chưa?
