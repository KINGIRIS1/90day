# Fix: "Cannot identify image file" Error

## Lỗi gốc

```
share/5-3442 CN TRUONG QUANG LAM 3/GCN.pdf: cannot identify image file <_io.BytesIO object at 0x7f8f3ca13f10>
```

## Nguyên nhân

Khi người dùng upload folder trực tiếp, hệ thống cố gắng xử lý **TẤT CẢ các file** như hình ảnh, bao gồm:
- ✅ File ảnh (.jpg, .png, etc.) - OK
- ❌ **File PDF** (.pdf) - KHÔNG THỂ mở bằng PIL/Pillow
- ❌ File Word (.docx)
- ❌ File khác

Lỗi xảy ra tại dòng:
```python
img = Image.open(BytesIO(image_bytes))  # ← Lỗi khi file là PDF
```

PIL/Pillow chỉ hỗ trợ định dạng ảnh, KHÔNG hỗ trợ PDF.

---

## Giải pháp đã áp dụng

### 1. **Lọc file ngay khi upload** (Dòng 2134-2144)

Thêm kiểm tra extension trước khi xử lý:

```python
# Skip non-image files (PDF, docx, etc.)
file_ext = Path(rp_norm).suffix.lower()
valid_image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.heif'}
if file_ext not in valid_image_exts:
    logger.warning(f"Skipping non-image file: {rp_norm}")
    continue  # ← Bỏ qua file không phải ảnh
```

**Kết quả**: File PDF, Word, Excel sẽ bị bỏ qua ngay từ đầu.

---

### 2. **Xử lý lỗi cho file ảnh bị corrupt** (Dòng 2198-2217)

Thêm try/catch khi mở file ảnh:

```python
try:
    img = Image.open(BytesIO(image_bytes))
    w, h = img.size
except Exception as img_err:
    logger.warning(f"Cannot open as image: {rel_path} - {img_err}")
    grouped_results.append(FolderScanFileResult(
        relative_path=rel_path,
        original_filename=Path(rel_path).name,
        detected_full_name="Không phải file ảnh hợp lệ",
        short_code="INVALID",
        confidence_score=0.0,
        status="error",
        error_message=f"Cannot identify image file: {str(img_err)[:100]}",
        user_id=current_user.get("id") if current_user else None
    ))
    return  # ← Bỏ qua file này và tiếp tục
```

**Kết quả**: Nếu có file ảnh bị hỏng/corrupt, sẽ được đánh dấu lỗi thay vì crash toàn bộ quá trình.

---

## Lợi ích

✅ **Không crash deployment** khi có file PDF trong folder  
✅ **Log warning** để người dùng biết file nào bị bỏ qua  
✅ **Tiếp tục xử lý** các file ảnh hợp lệ khác  
✅ **Báo lỗi rõ ràng** cho từng file không xử lý được

---

## Test case

**Trường hợp 1**: Folder có cả ảnh và PDF
```
folder/
├── document1.jpg  ← ✅ Xử lý
├── document2.pdf  ← ⚠️ Bỏ qua (log warning)
└── document3.png  ← ✅ Xử lý
```

**Kết quả**: 
- 2 file ảnh được xử lý thành công
- File PDF được bỏ qua với log: `"Skipping non-image file: document2.pdf"`

**Trường hợp 2**: File .jpg nhưng bị corrupt
```
folder/
└── corrupt.jpg  ← ❌ Lỗi nhưng không crash
```

**Kết quả**:
- File được ghi nhận với status="error"
- Error message: "Cannot identify image file: ..."
- Quá trình tiếp tục xử lý file khác

---

## Files đã sửa

- `/app/backend/server.py`:
  - Dòng 2134-2144: Thêm file extension filter
  - Dòng 2198-2217: Thêm error handling cho PIL.Image.open()

---

## Kiểm tra

✅ Python syntax: OK  
✅ Linting: Passed  
✅ Backend restart: Thành công  
✅ No errors in logs

---

## Deployment

Fix này sẽ **giải quyết lỗi deployment bị treo** do xử lý file PDF.

Bây giờ deployment sẽ:
1. ✅ BUILD thành công (không còn crash)
2. ✅ Bỏ qua file non-image
3. ✅ Log cảnh báo thay vì crash
4. ✅ Tiếp tục xử lý các file hợp lệ

**Có thể deploy lại!** 🚀
