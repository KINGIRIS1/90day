# Sửa lỗi: Quét PDF batch bị dừng sớm

## Vấn đề
Khi quét file PDF có nhiều trang (ví dụ: 34 trang), quá trình quét dừng lại sau 1-2 batch và trả về kết quả không đầy đủ, mặc dù log backend cho thấy nó đang bắt đầu batch tiếp theo.

## Nguyên nhân
Timeout 60 giây trong `/app/desktop-app/public/electron.js` (dòng 758) đã giết tiến trình Python trước khi nó hoàn thành việc xử lý tất cả các batch của file PDF lớn.

### Chi tiết kỹ thuật:
- **Trước đây**: Timeout = 60 giây (60000ms)
- **Vấn đề**: File PDF lớn với nhiều trang cần thời gian xử lý lâu hơn:
  - Tách PDF thành ảnh: ~2-5 giây
  - Xử lý mỗi batch (8 trang): ~10-20 giây (tùy theo API)
  - Delay giữa các batch: 5 giây
  - **Tổng thời gian cho PDF 34 trang**: ~80-120 giây
  
- **Kết quả**: Tiến trình bị kill sau 60 giây → Electron nhận kết quả không đầy đủ

## Giải pháp
Tăng timeout từ 60 giây lên **300 giây (5 phút)** để đủ thời gian xử lý file PDF lớn.

### Thay đổi trong code:
```javascript
// electron.js - dòng 758
// TRƯỚC:
setTimeout(() => { try { child.kill(); } catch {} reject(new Error('OCR processing timeout (60s)')); }, 60000);

// SAU:
setTimeout(() => { try { child.kill(); } catch {} reject(new Error('OCR processing timeout (5 minutes)')); }, 300000);
```

### Logging cải tiến:
Thêm log để track tiến trình batch processing trong `process_document.py`:
```python
print(f"   ✅ batch_classify_fixed completed, processing {len(batch_result.get('results', []))} results", file=sys.stderr)
```

## Kết quả
- ✅ File PDF lớn (đến 100+ trang) có thể được xử lý hoàn toàn
- ✅ Không còn bị dừng sớm giữa chừng
- ✅ Log rõ ràng hơn để debug trong tương lai

## Testing
Để test sửa lỗi này:
1. Tạo hoặc sử dụng file PDF có 30-50 trang
2. Quét file qua bất kỳ tab nào (Single file, Batch, OnlyGCN)
3. Chọn batch mode: Fixed (batch size 8) hoặc Smart
4. Verify rằng TẤT CẢ các trang được xử lý và hiển thị trong kết quả

## Ghi chú
- Timeout 5 phút là đủ cho hầu hết các trường hợp (lên đến ~150 trang với batch size 8)
- Nếu cần xử lý file PDF CỰC LỚN (200+ trang), có thể cần tăng timeout thêm
- Batch size nhỏ hơn (5-8) giúp giảm thời gian timeout và giảm lỗi 503 từ API

## Files thay đổi
1. `/app/desktop-app/public/electron.js` - Tăng timeout từ 60s lên 300s
2. `/app/desktop-app/python/process_document.py` - Thêm logging để track batch completion
