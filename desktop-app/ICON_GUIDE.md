# 🎨 Hướng Dẫn Tạo Icon cho Installer

## ⚠️ Lưu Ý Quan Trọng

**Icon là TÙY CHỌN!** Installer vẫn build được mà không cần icon.

Hiện tại, dòng icon đã được comment out trong `installer.nsi`:
```nsis
; !define MUI_ICON "assets\icon.ico"  ; Comment out - icon optional
```

Nếu bạn muốn có custom icon cho installer, follow hướng dẫn dưới đây.

---

## 🔧 Option 1: Dùng Mặc Định (Recommended)

**Không làm gì cả!** 

Installer sẽ dùng icon mặc định của NSIS. Vẫn chạy tốt.

---

## 🎨 Option 2: Tạo Custom Icon

### Bước 1: Chuyển PNG sang ICO

Hiện có file: `desktop-app/assets/icon.png`

**Cách 1: Dùng Online Tool (Nhanh nhất)**
1. Vào: https://convertio.co/png-ico/
2. Upload file `assets/icon.png`
3. Convert to ICO
4. Download về
5. Đổi tên thành `icon.ico`
6. Copy vào folder `assets/`

**Cách 2: Dùng GIMP (Free software)**
1. Download GIMP: https://www.gimp.org/
2. Mở file `icon.png`
3. File → Export As
4. Chọn tên: `icon.ico`
5. Save

**Cách 3: Dùng ImageMagick (Command line)**
```bash
# Install ImageMagick first
# https://imagemagick.org/

# Convert
magick convert icon.png -resize 256x256 icon.ico
```

**Cách 4: Dùng Online ICO Maker**
- https://icoconvert.com/
- https://www.aconvert.com/icon/png-to-ico/
- https://cloudconvert.com/png-to-ico

### Bước 2: Đặt File Vào Đúng Chỗ

```
desktop-app/
└── assets/
    ├── icon.png        (có sẵn)
    └── icon.ico        ← TẠO FILE NÀY
```

### Bước 3: Uncomment Dòng Icon

Mở file `installer.nsi`, tìm dòng:
```nsis
; !define MUI_ICON "assets\icon.ico"  ; Comment out - icon optional
```

Xóa dấu `;` và comment:
```nsis
!define MUI_ICON "assets\icon.ico"
```

### Bước 4: Build Lại

```batch
build-allinone.bat
```

---

## 🔍 Yêu Cầu ICO File

**Format:** .ico  
**Size:** 256x256 pixels (recommended)  
**Bit depth:** 32-bit with alpha channel  
**Multiple sizes:** Optional (16x16, 32x32, 48x48, 256x256)

---

## ❌ Troubleshooting

### Lỗi: "can't open file icon.ico"

**Fix:**
1. Kiểm tra file `assets/icon.ico` tồn tại
2. Kiểm tra đường dẫn đúng (assets\icon.ico)
3. Hoặc comment lại dòng icon:
   ```nsis
   ; !define MUI_ICON "assets\icon.ico"
   ```

### Lỗi: "Invalid icon file"

**Fix:**
1. Recreate ICO với tool khác
2. Đảm bảo đúng format .ico
3. Thử dùng mặc định (comment dòng icon)

---

## 📝 Note

**Installer vẫn hoạt động 100% mà không cần custom icon.**

Icon chỉ là tùy chọn thẩm mỹ:
- ✅ Với icon: Installer có logo riêng
- ✅ Không icon: Installer dùng logo NSIS mặc định

Cả 2 đều OK!

---

## 🎯 Recommended Approach

**Cho lần build đầu tiên:**
- Không cần icon, để mặc định
- Focus vào test chức năng
- Build nhanh chóng

**Cho production release:**
- Tạo icon.ico nếu muốn branding
- Uncomment dòng icon trong installer.nsi
- Rebuild

---

**Hiện tại: Icon đã được comment → Có thể build ngay!** ✅
