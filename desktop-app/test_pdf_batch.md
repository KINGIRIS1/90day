# Test Plan: PDF Batch Processing

## Mục đích
Verify rằng sửa lỗi timeout đã hoạt động và file PDF lớn có thể được xử lý hoàn toàn.

## Test Cases

### Test 1: PDF nhỏ (5-10 trang)
**Mục tiêu**: Verify rằng sửa lỗi không ảnh hưởng đến xử lý file nhỏ
- Tạo hoặc sử dụng PDF 5-10 trang
- Quét qua bất kỳ tab nào
- **Expected**: Hoàn thành trong <30 giây, tất cả trang được xử lý

### Test 2: PDF trung bình (20-34 trang) - MAIN TEST CASE
**Mục tiêu**: Verify rằng PDF 34 trang (case của user) được xử lý đầy đủ
- Sử dụng PDF 20-34 trang
- Chọn batch mode: Fixed (batch size 8)
- **Expected**: 
  - Batch 1 (0-7): Hoàn thành
  - Batch 2 (8-15): Hoàn thành
  - Batch 3 (16-23): Hoàn thành
  - Batch 4 (24-31): Hoàn thành
  - Batch 5 (32-33): Hoàn thành
  - Tổng thời gian: 60-120 giây
  - TẤT CẢ 34 trang xuất hiện trong kết quả

### Test 3: PDF lớn (50-100 trang)
**Mục tiêu**: Verify giới hạn trên của timeout mới
- Sử dụng PDF 50-100 trang
- **Expected**: Hoàn thành trong <5 phút, tất cả trang được xử lý

## Cách kiểm tra kết quả

### 1. Kiểm tra trong UI
- Đếm số lượng kết quả hiển thị
- Verify rằng số lượng = số trang trong PDF

### 2. Kiểm tra logs (nếu chạy từ terminal)
```bash
# Mở app và xem logs trong console
# Tìm các dòng:
📦 Batch 1: Files 0-7 (8 images)
✅ Batch 1 complete: X documents
...
📦 Batch N: Files ...
✅ Batch N complete: X documents
✅ PDF processing complete: 34 page(s)
```

### 3. Kiểm tra timeout không xảy ra
- Nếu timeout 60s vẫn xảy ra, sẽ thấy error: "OCR processing timeout (60s)"
- Sau sửa lỗi, không còn thấy error này nữa
- Nếu vượt quá 5 phút, sẽ thấy: "OCR processing timeout (5 minutes)" (rất hiếm)

## Expected Timing (với batch size 8, Gemini Flash)

| PDF Pages | Batches | Estimated Time | Status |
|-----------|---------|----------------|--------|
| 8 pages   | 1       | 15-25s         | ✅ OK (trước và sau fix) |
| 16 pages  | 2       | 35-50s         | ✅ OK (trước và sau fix) |
| 34 pages  | 5       | 80-120s        | ❌ FAIL trước → ✅ OK sau fix |
| 64 pages  | 8       | 140-200s       | ❌ FAIL trước → ✅ OK sau fix |
| 100 pages | 13      | 220-280s       | ❌ FAIL trước → ✅ OK sau fix |

## Regression Testing

Verify rằng các tính năng khác vẫn hoạt động:
- ✅ Quét file ảnh đơn lẻ (JPG, PNG)
- ✅ Quét folder nhiều ảnh
- ✅ OnlyGCN tab với PDF
- ✅ Batch scanner với PDF
- ✅ Sequential mode với PDF

## Troubleshooting

### Nếu vẫn bị timeout sau 60s:
1. Kiểm tra xem frontend đã restart chưa: `sudo supervisorctl status frontend`
2. Kiểm tra xem file electron.js đã được sửa đúng chưa: `grep -n "300000" /app/desktop-app/public/electron.js`
3. Clear cache và restart app

### Nếu timeout sau 5 phút:
1. PDF quá lớn (>150 trang) hoặc API chậm
2. Giải pháp:
   - Giảm batch size xuống 5 (thay vì 8)
   - Hoặc tăng timeout lên 600000 (10 phút)
   - Hoặc chia PDF thành nhiều file nhỏ hơn

### Nếu kết quả vẫn thiếu trang:
1. Kiểm tra log Python để xem batch nào failed
2. Có thể do:
   - API error (500, 503) → Retry hoặc giảm batch size
   - JSON parsing error → Check log chi tiết
   - Missing pages in AI response → Check prompt và validation

## Success Criteria

Fix được coi là thành công khi:
- ✅ PDF 34 trang được xử lý hoàn toàn (34/34 trang)
- ✅ Không có timeout error
- ✅ Thời gian xử lý hợp lý (80-120s)
- ✅ Tất cả batch hoàn thành theo log
- ✅ Không regression trên các tính năng khác
