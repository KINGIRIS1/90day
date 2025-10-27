# 🔐 SỬA LỖI: Cannot Create Symbolic Link (Privilege Error)

## ❌ Lỗi Gặp Phải

```
ERROR: Cannot create symbolic link : A required privilege is not held by the client.
C:\Users\nguye\AppData\Local\electron-builder\Cache\winCodeSign\...
```

**Nguyên nhân:**
- Electron-builder đang cố tạo symbolic links
- Windows yêu cầu quyền Administrator để tạo symbolic links
- Lỗi xảy ra khi extract winCodeSign tools

---

## ✅ ĐÃ SỬA

### Thay đổi trong `package.json`

**Thêm config skip code signing:**

```json
"win": {
  "target": ["nsis"],
  "icon": "assets/icon.png",
  "sign": null,                    // ← MỚI: Skip code signing
  "signingHashAlgorithms": null    // ← MỚI: Skip hash algorithms
}
```

**Giải thích:**
- `"sign": null` → Không sign code
- Code signing chỉ cần cho production releases
- Development build không cần sign
- Tránh cần quyền admin

---

## 🚀 CHẠY LẠI (Chọn 1 trong 2 cách)

### Cách 1: Chạy Lại Bình Thường (RECOMMENDED)

Config đã được sửa, chạy lại:

```batch
cd C:\desktop-app
yarn electron-pack
```

**Lần này sẽ không cần quyền admin!** ✅

---

### Cách 2: Chạy Với Quyền Admin (Nếu cách 1 vẫn lỗi)

1. **Đóng** Command Prompt hiện tại

2. **Mở Command Prompt as Administrator:**
   - Click phải Start Menu
   - Gõ "cmd"
   - Click phải "Command Prompt"
   - Chọn "**Run as administrator**"

3. **Chạy lại:**
   ```batch
   cd C:\desktop-app
   yarn electron-pack
   ```

---

## 🔍 Verify Kết Quả

**Sau khi chạy thành công, kiểm tra:**

```batch
cd C:\desktop-app
dir dist\win-unpacked
```

**Phải thấy:**
- ✅ File `90dayChonThanh.exe` (~150MB+)
- ✅ Folder `locales\`
- ✅ Folder `resources\`
- ✅ Nhiều .dll files

**Ví dụ output:**
```
Directory of C:\desktop-app\dist\win-unpacked

90dayChonThanh.exe       150,234,567 bytes
chrome_100_percent.pak     5,234,123 bytes
locales\                 <DIR>
resources\               <DIR>
...
```

---

## 📊 Kích Thước Dự Kiến

| File/Folder | Size |
|------------|------|
| 90dayChonThanh.exe | ~150 MB |
| locales\ | ~30 MB |
| resources\ | ~50 MB |
| DLL files | ~20 MB |
| **TOTAL** | **~250 MB** |

---

## ⏭️ BƯỚC TIẾP THEO

**Nếu electron-pack THÀNH CÔNG:**

```batch
# Build NSIS installer
cd C:\desktop-app
build-allinone.bat
```

**Sẽ tạo ra:** `90dayChonThanh-AllInOne-Setup.exe` (~235 MB)

---

## 🎯 Về Code Signing

### Code Signing là gì?

**Code signing** = Ký số cho executable file
- Windows sẽ tin tưởng app
- Không hiện cảnh báo "Unknown publisher"
- Cần certificate (có phí, ~$200-400/năm)

### Có cần không?

**Cho development/testing:** ❌ KHÔNG CẦN
- Skip để build nhanh
- Không cần quyền admin
- Vẫn chạy được bình thường

**Cho production release:** ✅ NÊN CÓ
- User tin tưởng hơn
- Ít cảnh báo từ Windows/Antivirus
- Chuyên nghiệp hơn

### Khi nào cần code signing?

**Không cần:**
- ✅ Development build
- ✅ Testing
- ✅ Internal use
- ✅ Small distribution

**Nên có:**
- ✅ Public release
- ✅ Large distribution
- ✅ Commercial software
- ✅ Enterprise deployment

---

## ⚠️ Lưu Ý

### 1. Windows SmartScreen Warning

**Nếu không sign code, user sẽ thấy:**
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting
```

**User cần làm:**
- Click "More info"
- Click "Run anyway"

**Cách khắc phục:** Code sign (production release)

---

### 2. Antivirus False Positive

Một số antivirus có thể báo virus cho unsigned app.

**Đây là FALSE POSITIVE** vì:
- App không sign
- Antivirus cẩn thận quá mức
- Bình thường với development builds

**Cách xử lý:**
- Add exception trong antivirus
- Hoặc code sign cho production

---

## 📝 Files Đã Thay Đổi

1. ✅ `package.json` - Added `"sign": null` to skip code signing
2. ✅ `FIX_PRIVILEGE_ERROR.md` - This file

---

## 🎯 TÓM TẮT

**Vấn đề:** Symbolic link privilege error  
**Nguyên nhân:** Electron-builder cần admin để extract winCodeSign  
**Giải pháp:** Skip code signing (không cần cho dev build)  
**Kết quả:** Build được mà không cần admin rights  

---

## 🚀 NEXT STEPS

### Checklist:

- [x] Sửa package.json (skip code signing)
- [ ] **Chạy `yarn electron-pack`** ← BẠN Ở ĐÂY
- [ ] Verify dist/win-unpacked có .exe
- [ ] Chạy `build-allinone.bat`
- [ ] Test installer

---

**Chạy `yarn electron-pack` ngay và báo kết quả!** 🚀

**Nếu vẫn lỗi về symbolic links:**
→ Chạy Command Prompt as Administrator
→ Hoặc cho tôi biết error message mới
