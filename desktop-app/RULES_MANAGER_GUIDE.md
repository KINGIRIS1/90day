# 📋 Rules Manager - Hướng Dẫn Sử Dụng

## Giới thiệu

Rules Manager cho phép bạn tùy chỉnh các quy tắc phân loại tài liệu đất đai. Bạn có thể:
- ✏️ Chỉnh sửa keywords cho từng loại tài liệu
- ⚖️ Điều chỉnh trọng số (weight) và số keyword tối thiểu
- 📤 Export/Import rules dưới dạng JSON
- 🔄 Reset về rules mặc định
- 📁 Mở thư mục chứa file rules

## Cách sử dụng

### 1. Truy cập Rules Manager

Từ ứng dụng desktop, click vào tab **📋 Rules** trên thanh menu.

### 2. Xem danh sách Rules

- Tất cả 95 loại tài liệu sẽ hiển thị dạng lưới (grid)
- Mỗi card hiển thị:
  - Mã tài liệu (ví dụ: GCNM, BMT, HSKT...)
  - Trọng số (weight)
  - Số lượng keywords

### 3. Xem chi tiết Rule

Click vào bất kỳ card nào để xem chi tiết:
- Weight (trọng số): Độ quan trọng của rule này
- Min Matches: Số keyword tối thiểu phải match
- Danh sách tất cả keywords

### 4. Tạo Rule Mới ⭐

**Bước 1:** Click nút **➕ Thêm Rule Mới**

**Bước 2:** Điền thông tin:
- **Mã Tài Liệu (Doc Type)**: Mã ngắn gọn (VD: GCNM, BMT, HDMB...)
  - Chữ hoa, không dấu, không khoảng trắng
  - Không trùng với mã đã có
- **Weight**: Trọng số ưu tiên (khuyến nghị: 0.8 - 1.5)
- **Min Matches**: Số keyword tối thiểu (khuyến nghị: 1-3)
- **Keywords**: Danh sách từ khóa đặc trưng
  - Thêm cả variants: có dấu, không dấu, chữ hoa
  - Thêm typo thường gặp từ OCR

**Bước 3:** Click **💾 Tạo Rule**

> **Lưu ý:** Rule mới sẽ được lưu vào `rules_overrides.json` và có hiệu lực ngay lập tức.

### 5. Chỉnh sửa Rule

**Bước 1:** Click nút **✏️ Sửa** khi đang xem chi tiết rule

**Bước 2:** Chỉnh sửa:
- **Weight**: Tăng để rule này được ưu tiên hơn (khuyến nghị: 0.5 - 2.0)
- **Min Matches**: Số keyword tối thiểu phải xuất hiện trong văn bản
- **Keywords**: 
  - Thêm keyword mới bằng ô input và click **➕ Thêm**
  - Xóa keyword bằng nút **✖** bên cạnh mỗi keyword

**Bước 3:** Click **💾 Lưu** để lưu thay đổi

> **Lưu ý:** Rule đã chỉnh sửa sẽ được lưu vào file `rules_overrides.json` và có ưu tiên cao hơn rule mặc định.

### 6. Xóa Rule (Revert về Default)

Click nút **🗑️ Xóa** để xóa rule tùy chỉnh và quay về rule mặc định.

> **Lưu ý:** Nếu là rule mới (tự tạo), xóa sẽ loại bỏ hoàn toàn rule đó.

### 7. Export Rules

Click **📤 Export JSON** để xuất toàn bộ rules ra file JSON. Bạn có thể:
- Backup rules hiện tại
- Share rules với người khác
- Chỉnh sửa rules bằng text editor

### 8. Import Rules

Có 2 cách import:

**📥 Import (Merge):** Gộp rules từ file JSON vào rules hiện tại
- Rules trùng mã sẽ được ghi đè
- Rules mới sẽ được thêm vào

**📥 Import (Replace):** Thay thế toàn bộ rules bằng file JSON
- ⚠️ Cẩn thận: Sẽ xóa tất cả rules tùy chỉnh hiện tại

### 9. Reset Tất Cả

Click **🔄 Reset Tất Cả** để xóa toàn bộ rules tùy chỉnh và quay về mặc định.

> ⚠️ **Cảnh báo:** Thao tác này không thể hoàn tác!

### 10. Mở Folder Rules

Click **📁 Mở Folder** để mở thư mục chứa file `rules_overrides.json`. Bạn có thể:
- Xem file rules trực tiếp
- Backup thủ công
- Chỉnh sửa file JSON (nâng cao)

## Cấu trúc Rule

Mỗi rule gồm 3 thành phần chính:

```json
{
  "GCNM": {
    "keywords": [
      "giấy chứng nhận",
      "quyền sử dụng đất",
      "..."
    ],
    "weight": 1.5,
    "min_matches": 1
  }
}
```

- **keywords**: Danh sách từ khóa để nhận diện loại tài liệu
- **weight**: Trọng số (cao hơn = ưu tiên hơn khi nhiều rules match)
- **min_matches**: Số keyword tối thiểu phải xuất hiện

## Tips & Best Practices

### ✅ Nên làm:

1. **Backup trước khi chỉnh sửa nhiều:**
   - Export rules ra file trước khi thay đổi lớn

2. **Test từng rule một:**
   - Chỉnh sửa 1-2 rules, test scan, rồi tiếp tục

3. **Thêm typo variants:**
   - OCR thường đọc sai: "chứng nhận" → "chứng nhan"
   - Thêm cả variants không dấu: "chung nhan"

4. **Điều chỉnh weight hợp lý:**
   - Rules quan trọng: 1.2 - 1.5
   - Rules ít gặp: 0.8 - 1.0

### ❌ Không nên:

1. **Thêm quá nhiều keywords:**
   - Có thể gây false positive
   - Nên thêm keywords đặc trưng, không chung chung

2. **Weight quá cao:**
   - Không đặt weight > 2.0
   - Có thể làm rule này "át" tất cả rules khác

3. **Min_matches quá cao:**
   - Nếu set quá cao, rule sẽ khó match
   - Khuyến nghị: 1-3 cho hầu hết rules

## Vị trí File

- **Rules mặc định:** Nằm trong code `rule_classifier.py`
- **Rules tùy chỉnh:** 
  - Windows: `C:\Users\<username>\.90daychonhanh\rules_overrides.json`
  - macOS/Linux: `~/.90daychonhanh/rules_overrides.json`

## Troubleshooting

**Q: Rules không áp dụng sau khi chỉnh sửa?**
A: Thử quét lại document, hoặc restart app.

**Q: Import bị lỗi?**
A: Kiểm tra file JSON có đúng format không. Xem ví dụ bằng cách Export rules hiện tại.

**Q: Muốn về rules gốc hoàn toàn?**
A: Click **🔄 Reset Tất Cả** hoặc xóa file `rules_overrides.json`.

**Q: Có thể thêm loại tài liệu mới?**
A: ✅ Có! Click **➕ Thêm Rule Mới** để tạo loại tài liệu tùy chỉnh.

## Ví dụ Thực Tế

### Tạo rule cho loại tài liệu mới: "Hợp đồng Mua Bán"

1. Click **➕ Thêm Rule Mới**
2. Điền thông tin:
   - **Mã:** HDMB
   - **Weight:** 1.1
   - **Min Matches:** 2
   - **Keywords:** (thêm từng cái)
     - "hợp đồng mua bán"
     - "hop dong mua ban"
     - "HOP DONG MUA BAN"
     - "người mua"
     - "người bán"
     - "bên a"
     - "bên b"
3. Click **💾 Tạo Rule**
4. Test bằng cách scan một ảnh hợp đồng mua bán

### Tăng độ chính xác cho GCNM

1. Mở rule **GCNM**
2. Click **✏️ Sửa**
3. Thêm keywords:
   - "sổ đỏ"
   - "so do"
   - "giấy cnqsd"
4. Tăng weight lên **1.6**
5. Click **💾 Lưu**

### Export backup hàng tuần

1. Click **📤 Export JSON**
2. Lưu file: `rules-backup-2025-01-15.json`
3. Lưu vào thư mục backup riêng

---

**🎯 Mục tiêu:** Tăng độ chính xác nhận diện từ 85-88% lên 90%+ bằng cách fine-tune rules!
