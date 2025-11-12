# 🖼️ Hướng Dẫn Sử Dụng Preview Mode

## Tính Năng Mới: Tùy Chọn Hiển Thị Ảnh Preview

Khi tiếp tục scan từ lần trước (Resume), bạn có thể chọn cách hiển thị ảnh preview để tối ưu hiệu suất và tiết kiệm RAM.

## 3 Chế Độ Preview:

### 1. 🚀 Không Load Ảnh
- **Ưu điểm**: Nhanh nhất, tiết kiệm RAM tối đa
- **Nhược điểm**: Không thể xem trước ảnh tài liệu
- **Phù hợp cho**: 
  - Máy có RAM thấp (< 8GB)
  - Quét thư mục có rất nhiều file (> 100 files)
  - Chỉ cần kết quả phân loại, không cần xem ảnh

### 2. ⭐ Chỉ Load Ảnh GCN (Khuyến Nghị)
- **Ưu điểm**: Cân bằng giữa hiệu suất và tiện lợi
- **Nhược điểm**: Không xem được ảnh của các tài liệu khác (PCT, CCCD, v.v.)
- **Phù hợp cho**: 
  - Hầu hết trường hợp sử dụng
  - Tập trung vào tài liệu GCN (quan trọng nhất)
  - Máy có RAM trung bình (8-16GB)

### 3. 📸 Load Tất Cả Ảnh
- **Ưu điểm**: Đầy đủ, xem được tất cả ảnh preview
- **Nhược điểm**: Có thể chậm, tốn RAM nếu có quá nhiều file
- **Phù hợp cho**: 
  - Máy có RAM cao (> 16GB)
  - Quét ít file (< 50 files)
  - Cần kiểm tra chi tiết tất cả tài liệu

## Cách Sử Dụng:

### Khi Resume Scan:
1. Mở app → Xuất hiện dialog "Tiếp Tục Scan?"
2. Chọn một trong 3 options:
   - ⚪ Không load ảnh
   - 🟢 Chỉ load ảnh GCN (mặc định - khuyến nghị)
   - ⚪ Load tất cả ảnh
3. Nhấn "▶️ Tiếp Tục Scan"

### Trong Quá Trình Xem Kết Quả:
- Nếu chọn "Không load ảnh" hoặc "Chỉ load ảnh GCN", bạn sẽ thấy badge màu xanh ở trên cùng
- Nhấn nút "Đổi chế độ" để chuyển sang chế độ khác:
  - Không load → Chỉ GCN → Tất cả → Không load (vòng tròn)

## Lưu Ý Quan Trọng:

### Về Lazy Loading:
- Preview chỉ được load **khi bạn chuyển đến tab đó**
- Tab chưa mở = chưa load preview → tiết kiệm RAM
- Khi đổi chế độ, preview sẽ được load lại theo chế độ mới

### Về Performance:
- **"Không load ảnh"**: App có thể xử lý hàng trăm files mà không bị crash
- **"Chỉ load ảnh GCN"**: Thường chỉ load 10-30% số ảnh (GCN chiếm ~20-30% tài liệu)
- **"Load tất cả"**: Có thể crash nếu có quá nhiều file (> 200 files với nhiều tabs)

### Best Practices:
1. **Lần đầu resume**: Chọn "Chỉ load ảnh GCN" (mặc định)
2. **Nếu cần xem ảnh khác**: Đổi sang "Load tất cả" sau khi resume
3. **Nếu bị lag**: Đổi về "Không load ảnh" hoặc "Chỉ GCN"
4. **Máy yếu**: Luôn dùng "Không load ảnh" hoặc "Chỉ GCN"

## Technical Details:

### Memory Impact:
- Mỗi ảnh base64: ~200-500KB RAM
- 100 ảnh = ~20-50MB RAM
- 10 tabs × 50 ảnh = ~100-250MB RAM (có thể gây crash)

### Lazy Loading Mechanism:
- Preview được load **on-demand** khi user chuyển tab
- Chỉ tab active được load preview
- Preview được cache sau khi load (không load lại)

### Preview Mode Logic:
```javascript
// none: Không load preview nào
// gcn-only: Chỉ load nếu short_code = 'GCNC' || 'GCNM' || 'GCN'
// all: Load tất cả preview
```

## Troubleshooting:

### Q: Tôi đã chọn "Load tất cả" nhưng không thấy ảnh?
A: Chuyển sang tab khác rồi chuyển lại. Preview được load theo từng tab.

### Q: App vẫn bị lag/crash?
A: 
1. Đổi về chế độ "Không load ảnh"
2. Giảm số lượng file hiển thị (dùng pagination)
3. Xóa các tab không cần thiết

### Q: Làm sao để load lại preview?
A: Đổi chế độ → chuyển sang tab khác → chuyển lại về tab cũ

### Q: Tại sao không load tất cả ảnh từ đầu như trước?
A: Để tránh crash khi có quá nhiều tabs/files. Lazy loading giúp app ổn định hơn.

---

**Cập nhật**: 12/01/2025  
**Version**: 1.2.0  
**Tác giả**: AI Developer
