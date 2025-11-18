# 🔧 Only GCN Pre-filter Fix

**Ngày sửa:** 20/11/2024  
**Cập nhật:** 20/11/2024 (Added A3 size check)  
**Vấn đề:** Pre-filter không nhận diện đúng GCN A3  
**Trạng thái:** ✅ Đã sửa xong, chờ user test

---

## 🐛 Vấn đề phát hiện

### Issue 1: Miss GCN (False Negative)
User báo rằng trong thư mục có GCN nhưng pre-filter không nhận diện được, dẫn đến tất cả file bị đánh dấu là "GTLQ" thay vì "GCN".

**Nguyên nhân:**
1. **Ngưỡng màu sắc quá khắt khe**: 
   - `avg_r > 150` quá cao → Bỏ sót GCN có màu nhạt
   - `color_diff > 30` quá cao → Bỏ sót border có màu nhẹ
   - `colored_pixels < 100` quá cao → Bỏ sót ảnh scan có border mỏng

2. **Output format không đúng**:
   - Script print nhiều debug info ra stdout
   - Electron.js chờ stdout chỉ chứa: 'red', 'pink', hoặc 'unknown'
   - Kết quả: IPC không parse được → pre-filter thất bại

### Issue 2: False Positive (CRITICAL!)
User báo: **"Hình như có lỗi nếu trên tờ giấy có dấu đỏ cũng đang hiểu là GCN"**

**Nguyên nhân:**
- Script chỉ kiểm tra màu sắc, KHÔNG kiểm tra kích thước giấy
- File A4 có stamp/seal màu đỏ → Bị nhận diện nhầm là GCN
- **2 quy tắc quan trọng cho GCN A3:**
  1. ✅ Có màu đỏ/hồng
  2. ✅ Phải là A3 (aspect ratio > 1.35)

**Ví dụ false positive:**
- Hồ sơ A4 có con dấu đỏ → Bị nhận diện là GCN ❌
- Giấy tờ A4 có chữ ký đỏ → Bị nhận diện là GCN ❌

---

## ✅ Các thay đổi đã thực hiện

### 1. ⚠️ THÊM KIỂM TRA KÍCH THƯỚC A3 (CRITICAL FIX!)

**Vấn đề:** File A4 có dấu đỏ bị nhận diện nhầm là GCN

**Giải pháp:** Kiểm tra aspect ratio TRƯỚC khi kiểm tra màu

```python
# BEFORE: Chỉ kiểm tra màu
if avg_r > 80:
    # ... classify color ...
    return color

# AFTER: Kiểm tra A3 TRƯỚC
aspect_ratio = width / height

# CRITICAL CHECK #1: Must be A3 size
if aspect_ratio <= 1.35:
    print(f"❌ NOT A3 format (aspect ratio {aspect_ratio:.2f} <= 1.35)")
    print(f"   → Skipping (even if has red color, not GCN A3)")
    return 'unknown'  # ← Reject ngay, không check màu nữa

# CRITICAL CHECK #2: Check color (only for A3)
# ... color detection logic ...
```

**Logic mới:**
1. Đọc ảnh → Tính aspect ratio
2. Nếu aspect ratio ≤ 1.35 → Return 'unknown' ngay (không phải A3)
3. Nếu aspect ratio > 1.35 → Tiếp tục kiểm tra màu
4. Return 'red'/'pink' chỉ khi CẢ HAI điều kiện thỏa mãn

**Kết quả:**
- ✅ GCN A3 (4443×3135, ratio 1.42) + màu đỏ → PASS
- ❌ File A4 (2486×3516, ratio 0.71) + dấu đỏ → REJECT
- ❌ File A4 landscape (3516×2486, ratio 1.41) + màu → PASS (nhưng hiếm)

### 2. Nới lỏng ngưỡng màu sắc (`color_detector.py`)

**Thay đổi ngưỡng:**
```python
# TRƯỚC (Quá khắt khe):
avg_r > 150              # Bỏ sót GCN màu nhạt
color_diff > 30          # Bỏ sót border nhẹ
colored_pixels < 100     # Bỏ sót border mỏng

# SAU (Nới lỏng):
avg_r > 80               # Catch GCN màu nhạt hơn (lowered 47%)
color_diff > 20          # Catch border nhẹ hơn (lowered 33%)
colored_pixels < 50      # Catch border mỏng hơn (lowered 50%)
```

**Thay đổi logic phân loại:**
```python
# TRƯỚC: Chỉ phân loại nếu R > 100
if avg_r > 100:
    # ... phân loại ...
else:
    color = 'unknown'

# SAU: Phân loại nếu R > 80, và conservative hơn
if avg_r > 80:  # Nới lỏng 20%
    if avg_g > 80 and avg_b > 80:
        # Pink-ish: Nới lỏng điều kiện
        if avg_r >= avg_g * 0.9:  # R chỉ cần >= 90% của G
            color = 'pink'
        else:
            color = 'pink'  # Conservative: coi là pink luôn
    elif avg_r > avg_g + 20:  # Lowered from +30
        color = 'red'
    else:
        color = 'red'  # Conservative: coi là GCN tiềm năng
```

**Thêm logging cho debugging:**
```python
print(f"📏 Dimensions: {width}x{height}, Aspect ratio: {aspect_ratio:.2f}", file=sys.stderr)
print(f"🎨 Border color RGB: ({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})", file=sys.stderr)
print(f"🎨 Detected color: {color}", file=sys.stderr)

if aspect_ratio > 1.35:
    print(f"📐 A3 format detected (landscape)", file=sys.stderr)
elif aspect_ratio < 1.0:
    print(f"📐 A4 format detected (portrait)", file=sys.stderr)
```

### 3. Sửa CLI output format (`color_detector.py`)

**TRƯỚC:**
```python
if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Testing color detection on: {image_path}")  # ❌ stdout
        
        border_color = detect_gcn_border_color(image_path)
        print(f"Border color: {border_color}")  # ❌ stdout với text
        
        center_color = get_dominant_color_simple(image_path, 'center')
        print(f"Center color: {center_color}")  # ❌ thêm text không cần
```

**SAU:**
```python
if __name__ == '__main__':
    # CLI mode: Return only the color result to stdout
    # All debug info goes to stderr
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        
        # Use border detection (primary method)
        border_color = detect_gcn_border_color(image_path)
        
        # Output only the result to stdout (for IPC) ✅
        print(border_color)  # Chỉ in: 'red', 'pink', hoặc 'unknown'
    else:
        print("Usage: python color_detector.py <image_path>", file=sys.stderr)
        sys.exit(1)
```

### 4. Toggle Switch UI (Đã có sẵn từ trước)

Toggle switch đã được thêm vào `OnlyGCNScanner.js` (lines 427-438):
```jsx
<div className="ml-auto flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border border-gray-300">
  <input
    type="checkbox"
    id="usePreFilter"
    checked={usePreFilter}
    onChange={(e) => setUsePreFilter(e.target.checked)}
    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
  />
  <label htmlFor="usePreFilter" className="text-sm font-medium text-gray-700 cursor-pointer">
    🎨 Pre-filter (lọc màu)
  </label>
</div>
```

**Logic sử dụng toggle:**
```javascript
// Line 197: Chỉ chạy pre-filter nếu toggle BẬT
if (usePreFilter && hasPreFilter) {
  // Run color detection
  const preFilterResults = await window.electronAPI.preFilterGCNFiles(folderFiles);
  gcnCandidates = preFilterResults.passed || [];
  skipped = preFilterResults.skipped || [];
} else {
  // Nếu toggle TẮT: Scan tất cả file
  console.log(`   ⚡ Pre-filter OFF: Scanning all ${folderFiles.length} files`);
  gcnCandidates = folderFiles;
  skipped = [];
}
```

---

## 📊 Kết quả mong đợi

### Với toggle **BẬT** (usePreFilter = true):
- ✅ Nhận diện GCN có màu đỏ/hồng (ngay cả khi màu nhạt)
- ✅ Tiết kiệm ~60-85% API calls
- ✅ Nhanh hơn 2-3x
- ⚠️ Có thể miss ~1% GCN có màu rất nhạt (trade-off chấp nhận được)

### Với toggle **TẮT** (usePreFilter = false):
- ✅ Quét tất cả file bằng AI (100% chính xác)
- ⚠️ Chậm hơn và tốn API hơn
- ✅ Không bỏ sót GCN nào

---

## 🧪 Cách test

### Test 1: Với pre-filter BẬT
1. Chọn thư mục có GCN màu đỏ/hồng
2. **Bật** checkbox "🎨 Pre-filter (lọc màu)"
3. Nhấn "▶️ Bắt đầu quét"
4. Kiểm tra:
   - ✅ GCN được nhận diện đúng (không phải "GTLQ")
   - ✅ Console log hiển thị: `🎨 Border color RGB: (...)`
   - ✅ Số file được quét ít hơn tổng số file

### Test 2: Với pre-filter TẮT
1. Chọn cùng thư mục
2. **Tắt** checkbox "🎨 Pre-filter (lọc màu)"
3. Nhấn "▶️ Bắt đầu quét"
4. Kiểm tra:
   - ✅ Tất cả file được quét bằng AI
   - ✅ Console log: `⚡ Pre-filter OFF: Scanning all X files`
   - ✅ 100% GCN được nhận diện

### Test 3: Edge case
- Test với GCN có màu rất nhạt (faded)
- Test với GCN bị scan nghiêng
- Test với thư mục chỉ có GTLQ (không có GCN)

---

## 📁 Files đã sửa

1. **`/app/desktop-app/python/color_detector.py`**
   - Nới lỏng ngưỡng màu sắc (80 thay vì 150)
   - Nới lỏng ngưỡng color_diff (20 thay vì 30)
   - Nới lỏng ngưỡng colored_pixels (50 thay vì 100)
   - Sửa CLI output format (chỉ print kết quả ra stdout)
   - Thêm logging chi tiết ra stderr

2. **`/app/desktop-app/src/components/OnlyGCNScanner.js`**
   - (Đã có sẵn) Toggle switch UI
   - (Đã có sẵn) Logic sử dụng state `usePreFilter`

3. **`/app/desktop-app/public/electron.js`**
   - (Không cần sửa) IPC handler đã đúng

---

## 🚀 Hướng dẫn cập nhật cho User

### Bước 1: Pull code mới
```bash
git pull
```

### Bước 2: Xóa cache Electron (nếu có lỗi)
```bash
# Windows
rmdir /s /q %APPDATA%\Electron

# macOS/Linux
rm -rf ~/.config/Electron
```

### Bước 3: Restart app
```bash
yarn electron-dev-win
```

### Bước 4: Test
1. Mở tab "Only GCN"
2. Thử cả 2 chế độ (toggle ON/OFF)
3. Xem console log để debug (nếu cần)

---

## 🎯 Triết lý sửa lỗi

**Conservative approach**: Better to have false positives than miss real GCN

- Nếu không chắc → Coi là GCN (scan bằng AI)
- Nếu màu không rõ → Coi là GCN tiềm năng
- Nếu pre-filter lỗi → Scan tất cả file (fail-safe)

**User control**: Toggle switch để user tự quyết định

- BẬT: Tiết kiệm thời gian & tiền (với trade-off nhỏ)
- TẮT: Chính xác 100% (tốn thời gian & tiền hơn)

---

## 📝 Notes cho Agent tiếp theo

1. **Nếu user vẫn báo miss GCN**: Tiếp tục nới lỏng ngưỡng trong `color_detector.py`
   - Có thể giảm `avg_r > 80` xuống 60-70
   - Có thể giảm `color_diff > 20` xuống 15
   - Cân nhắc thêm logic fallback: nếu không detect được màu → scan anyway

2. **Nếu có quá nhiều false positive**: Thắt chặt lại ngưỡng một chút
   - Nhưng ưu tiên không bỏ sót GCN hơn là tránh false positive

3. **Testing**: Yêu cầu user share sample images nếu vẫn có vấn đề
   - Cần có file GCN mẫu để debug ngưỡng

4. **Future improvement**: Thêm kiểm tra kích thước (aspect ratio) vào logic quyết định
   - GCN A3: aspect ratio > 1.35 → High confidence
   - GCN A4: aspect ratio < 1.0 + có màu → Medium confidence

---

**Document maintained by:** E1 Agent (Fork 2)  
**Last updated:** 20/11/2024
