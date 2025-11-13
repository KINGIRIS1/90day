# Classification Prompts

Thư mục này chứa các prompt dùng cho Gemini AI để phân loại tài liệu đất đai Việt Nam.

## Files

### `classification_prompt_full.txt`
- **Mục đích**: Prompt đầy đủ cho Gemini Flash 2.5
- **Kích thước**: ~25,700 ký tự (~6,400 tokens)
- **Nội dung**: Bao gồm tất cả quy tắc, ví dụ chi tiết, và 66 loại tài liệu
- **Khi nào dùng**: Khi cần độ chính xác cao nhất, không quan tâm chi phí

### `classification_prompt_lite.txt`
- **Mục đích**: Prompt rút gọn cho Gemini Flash Lite 2.5
- **Kích thước**: ~8,300 ký tự (~2,100 tokens)
- **Giảm**: 67.6% so với bản full
- **Nội dung**: Giữ lại các quy tắc cốt lõi nhưng rút gọn ví dụ
- **Khi nào dùng**: Khi cần tiết kiệm chi phí, vẫn đảm bảo độ chính xác hợp lý

## Đồng bộ hóa

**Quan trọng**: Cả hai prompt phải được đồng bộ về mặt logic:

### Các quy tắc PHẢI có trong cả hai:
1. ✅ Quy tắc vị trí (TOP 20% / MIDDLE / BOTTOM)
2. ✅ Section headers (I., II., ĐIỀU, PHẦN)
3. ✅ Blacklist (Căn cứ, Theo, Kèm theo...)
4. ✅ Title độc lập (NẰM RIÊNG, không chung dòng)
5. ✅ Phân biệt REFERENCE vs TITLE
6. ✅ Quy tắc GCN đặc biệt (color + issue_date)
7. ✅ 66 loại tài liệu (danh sách đầy đủ)
8. ✅ Các cặp dễ nhầm (HDCQ vs HDUQ, TTHGD vs PCTSVC vs VBTK, etc.)
9. ✅ GCNM continuation patterns
10. ✅ Validation: Chỉ trả về 66 mã, không tự tạo mã mới

### Khác biệt:
- **Full**: Nhiều ví dụ cụ thể hơn, giải thích chi tiết hơn mỗi loại tài liệu
- **Lite**: Rút gọn ví dụ, tập trung vào quy tắc quan trọng nhất

## Cách chỉnh sửa

### Khi thêm quy tắc mới:
1. Thêm vào `classification_prompt_full.txt` đầy tiên
2. Nếu quy tắc quan trọng → thêm vào `classification_prompt_lite.txt` (rút gọn)
3. Test với cả hai prompt
4. Commit cả hai file

### Khi thêm loại tài liệu mới:
1. Thêm vào `VALID_DOCUMENT_CODES` trong `ocr_engine_gemini_flash.py`
2. Thêm vào cả hai prompt
3. Thêm ví dụ cụ thể (full) và ví dụ ngắn gọn (lite)

## Testing

```bash
# Test load prompts
python3 -c "
from ocr_engine_gemini_flash import get_classification_prompt_lite, get_classification_prompt
print(f'Lite: {len(get_classification_prompt_lite())} chars')
print(f'Full: {len(get_classification_prompt())} chars')
"

# Test classification
python3 ocr_engine_gemini_flash.py <image_path> <api_key>
```

## Chi phí ước tính (Gemini Flash 2.5)

### Input tokens (prompt):
- Full: ~6,400 tokens
- Lite: ~2,100 tokens
- Tiết kiệm: ~4,300 tokens/image (67.6%)

### Example: Batch 100 images
- Full: 640,000 input tokens
- Lite: 210,000 input tokens
- **Tiết kiệm**: ~430,000 tokens

*Note: Chưa tính tokens cho image (thường 200-800 tokens tùy kích thước)*

## Lịch sử thay đổi

### v2.0 (2025-01-XX)
- Tách prompt ra file riêng để dễ quản lý
- Đồng bộ hóa hoàn toàn prompt lite với full
- Thêm quy tắc TITLE độc lập
- Thêm quy tắc section headers chi tiết
- Thêm phân biệt VBTK vs TTHGD vs PCTSVC

### v1.0 (trước đó)
- Prompt nhúng trong code Python
- Lite và Full chưa đồng bộ hoàn toàn
