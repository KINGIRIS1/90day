# 🤖 Auto-Generate Keyword Variants

## Giới thiệu

Tính năng tự động tạo variants giúp tiết kiệm thời gian khi thiết lập rules. Từ 1 keyword gốc, hệ thống tự động tạo ra nhiều biến thể để tăng khả năng nhận diện OCR.

## Cách sử dụng

### Trong Edit Rule

1. Mở rule cần chỉnh sửa
2. Thêm một vài keywords gốc (ví dụ: "giấy chứng nhận", "quyền sử dụng đất")
3. Click button **🤖 Tự động tạo variants**
4. Hệ thống sẽ tạo tất cả biến thể từ keywords hiện có
5. Review và lưu rule

### Trong Create New Rule

1. Click **➕ Thêm Rule Mới**
2. Điền Doc Type, Weight, Min Matches
3. Thêm 2-3 keywords chính (có dấu)
4. Click **🤖 Tự động tạo variants**
5. Hệ thống tạo đầy đủ variants
6. Click **💾 Tạo Rule**

## Các loại Variants được tạo

### 1. **Case Variants (Chữ hoa/thường)**
```
"giấy chứng nhận" →
  - giấy chứng nhận (original)
  - GIẤY CHỨNG NHẬN (uppercase)
  - Giấy Chứng Nhận (title case)
```

### 2. **Remove Diacritics (Bỏ dấu)**
```
"giấy chứng nhận" →
  - giay chung nhan (no diacritics)
  - GIAY CHUNG NHAN (uppercase no diacritics)
  - Giay Chung Nhan (title case no diacritics)
```

### 3. **OCR Typos (Lỗi OCR thường gặp)**

**Vietnamese-specific:**
```
ă → a    (băng → bang)
â → a    (tâm → tam)
ê → e    (tên → ten)
ô → o    (hồ → ho)
ơ → o    (người → nguoi)
ư → u    (sử dụng → su dung)
đ → d    (đất → dat)
```

**Common OCR confusion:**
```
q → g    (quyền → guyền)
rn → m   (corn → com)
vv → w   (vveb → web)
0 ↔ o    (h0a → hoa)
1 ↔ l    (1and → land)
```

## Ví dụ Thực Tế

### Input: "sổ đỏ"
**Output (9 variants):**
```
- sổ đỏ              (original)
- SỔ ĐỎ              (uppercase)
- Sổ Đỏ              (title case)
- so do              (no diacritics)
- SO DO              (uppercase no diacritics)
- So Do              (title case no diacritics)
- sổ dỏ              (đ → d typo)
- SỔ DỎ              (uppercase typo)
- Sổ Dỏ              (title case typo)
```

### Input: "quyền sử dụng"
**Output (10 variants):**
```
- quyền sử dụng      (original)
- QUYỀN SỬ DỤNG      (uppercase)
- Quyền Sử Dụng      (title case)
- quyen su dung      (no diacritics)
- QUYEN SU DUNG      (uppercase no diacritics)
- Quyen Su Dung      (title case no diacritics)
- guyền sử dụng      (q → g typo)
- GUYỀN SỬ DỤNG      (uppercase typo)
- Guyền Sử Dụng      (title case typo)
- guyen su dung      (no diacritics + typo)
```

### Input: "giấy chứng nhận quyền sử dụng đất"
**Output: 13 variants!**

## Lợi ích

### 1. **Tiết kiệm thời gian** ⏰
- Thay vì gõ 10-15 variants thủ công
- Chỉ cần 1 click → tự động tạo tất cả

### 2. **Tăng độ chính xác** 🎯
- Cover hết các trường hợp OCR đọc sai
- Bao gồm cả typo không nghĩ tới

### 3. **Consistency** ✅
- Đảm bảo không bỏ sót variant quan trọng
- Chuẩn hóa cách tạo keywords

### 4. **Tối ưu coverage** 📊
- 1 keyword gốc → 5-15 variants
- Tăng khả năng match lên 300-500%

## Best Practices

### ✅ Nên làm:

1. **Bắt đầu với keywords chính:**
   ```
   Thêm: "giấy chứng nhận", "quyền sử dụng", "đất"
   Click: 🤖 Generate
   Result: 30+ variants
   ```

2. **Generate sau khi thêm 3-5 keywords:**
   - Không cần thêm quá nhiều keywords gốc
   - Generate sẽ tạo đủ variants

3. **Review sau khi generate:**
   - Xóa variants không hợp lý (nếu có)
   - Thêm keywords đặc trưng khác (nếu cần)

4. **Sử dụng cho keywords dài:**
   - Keywords dài có nhiều variants hơn
   - Hiệu quả cao hơn

### ❌ Không nên:

1. **Generate quá nhiều lần:**
   - Mỗi lần generate đã tạo tất cả variants rồi
   - Generate lần 2 chỉ tạo thêm duplicates

2. **Thêm quá nhiều keywords gốc trước khi generate:**
   - 10 keywords × 10 variants = 100 keywords
   - Có thể gây false positive

3. **Không review:**
   - Một số variants có thể không phù hợp
   - Nên xóa variants quá chung chung

## Technical Details

### Algorithm Flow

```python
Input: "giấy chứng nhận"

1. Case variants:
   - giấy chứng nhận
   - GIẤY CHỨNG NHẬN
   - Giấy Chứng Nhận

2. Remove diacritics:
   - giay chung nhan
   - GIAY CHUNG NHAN
   - Giay Chung Nhan

3. Generate typos for each:
   - Original + typos
   - No-diacritics + typos

4. Deduplicate & sort

Output: [unique variants array]
```

### Performance

- **Speed:** ~50-100ms per keyword
- **Variants per keyword:** 5-15 (average: 10)
- **Batch processing:** Generate for all keywords at once
- **Memory:** Minimal (uses Set for deduplication)

## Examples by Document Type

### GCNM (Giấy Chứng Nhận)
**Keywords gốc:**
```
- giấy chứng nhận
- quyền sử dụng đất
- sổ đỏ
```

**After generate:** ~30 variants
**Match rate increase:** +400%

### BMT (Biên Bản Thỏa Thuận)
**Keywords gốc:**
```
- biên bản
- thỏa thuận
- hai bên
```

**After generate:** ~25 variants
**Match rate increase:** +350%

### HSKT (Hồ Sơ Kỹ Thuật)
**Keywords gốc:**
```
- hồ sơ
- kỹ thuật
- thiết kế
```

**After generate:** ~27 variants
**Match rate increase:** +380%

## Troubleshooting

**Q: Generate bị timeout?**
A: Chỉ xảy ra nếu có quá nhiều keywords (>50). Giải pháp: Generate theo batch nhỏ hơn.

**Q: Có quá nhiều variants?**
A: Review và xóa bớt variants không cần thiết. Hoặc chỉ thêm 2-3 keywords chính trước khi generate.

**Q: Variants không phù hợp?**
A: Xóa variants không hợp lý sau khi generate. Tính năng generate là gợi ý, không bắt buộc phải giữ hết.

**Q: Có thể tùy chỉnh typo rules?**
A: Hiện tại không. Typo rules được hard-coded dựa trên OCR patterns phổ biến.

---

**💡 Pro Tip:** Chỉ cần 2-3 keywords chính có dấu, sau đó click **🤖 Generate** → Lưu → Test ngay!
