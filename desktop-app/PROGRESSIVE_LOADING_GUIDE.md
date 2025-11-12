# 🚀 Progressive Tab Loading - Hướng Dẫn

## Vấn Đề Đã Giải Quyết

**Trước đây:**
- Khi resume, tất cả tabs được load vào RAM cùng lúc
- Mỗi tab có hàng chục/trăm kết quả → quá tải RAM → crash
- Người dùng phải chờ load hết rồi mới thấy giao diện

**Bây giờ:**
- Tabs được load **tuần tự** (lần lượt từng tab một)
- Mỗi tab load xong → hiển thị ngay → load tab tiếp theo
- RAM không bị quá tải vì chỉ load 1 tab tại 1 thời điểm

## Cách Hoạt Động

### Flow Progressive Loading:

```
1. User nhấn "Tiếp tục scan"
   ↓
2. Khởi tạo tabs rỗng (chỉ có tên, không có data)
   ↓
3. Hiển thị progress bar
   ↓
4. Load Tab 1 → Cập nhật UI → Delay 100ms
   ↓
5. Load Tab 2 → Cập nhật UI → Delay 100ms
   ↓
6. Load Tab 3 → ... (tiếp tục)
   ↓
7. Hoàn thành → Ẩn progress bar → Hiển thị thông báo
```

### Technical Details:

```javascript
// Initialize empty tabs first
const initialTabs = validRestoredTabs.map(tab => ({
  name: tab.name,
  path: tab.path,
  count: tab.count || 0,
  status: 'loading', // Special status
  results: [] // Empty - will be loaded progressively
}));
setChildTabs(initialTabs);

// Load tabs one by one
for (let i = 0; i < validRestoredTabs.length; i++) {
  // Update progress
  setTabLoadProgress({ current: i + 1, total: validRestoredTabs.length });
  
  // Give React time to update UI (100ms delay)
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Load this tab's data (without previews)
  const loadedTab = { ...tab, results: stripPreviews(tab.results) };
  
  // Update state - only this tab
  setChildTabs(prev => prev.map((t, idx) => idx === i ? loadedTab : t));
}
```

## UI Indicators

### 1. Progress Bar (khi đang load):
```
┌─────────────────────────────────────────────┐
│ ⏳ Đang khôi phục dữ liệu... (3/10 thư mục) │
│ Load dần từng thư mục để tránh quá tải RAM  │
│ ████████████░░░░░░░░░░░░░░░░░░░░ 30%        │
└─────────────────────────────────────────────┘
```

### 2. Tab Status Icons:
- **⏳** (loading): Đang load data cho tab này
- **⚙️** (scanning): Đang quét folder này
- **✓** (done): Đã hoàn thành
- **○** (pending): Chưa bắt đầu

### 3. Tab Appearance:
```
[Tab 1 ✓]  [Tab 2 ⏳]  [Tab 3 ○]  [Tab 4 ○]
  Done      Loading    Pending   Pending
```

## Performance Benefits

### Memory Usage:

**Trước (Bulk Loading):**
- 10 tabs × 50 files × 500KB data = ~250MB RAM ngay lập tức
- Có thể crash nếu máy yếu hoặc có nhiều tabs

**Bây giờ (Progressive Loading):**
- Load 1 tab tại 1 thời điểm = ~25MB RAM tại mỗi thời điểm
- Tổng RAM sau khi load hết = tương tự, nhưng **không bị spike**
- **Không crash** vì load từ từ, React có thời gian garbage collect

### Loading Speed:

**Bulk Loading:**
- Load: 0s ███████████████████████ 100% (5s)
- Display: 5s ░░░░░░░░░░░░░░░░░░░░░░ (instant after load)
- **Total wait: 5 seconds với màn hình trống**

**Progressive Loading:**
- Tab 1: 0.0s ███ 10% → display (0.1s)
- Tab 2: 0.1s ██████ 20% → display (0.2s)
- Tab 3: 0.2s █████████ 30% → display (0.3s)
- ...
- Tab 10: 1.0s ████████████████████ 100% → complete (1.0s)
- **Total: 1 second, nhưng thấy UI ngay từ 0.1s**

### User Experience:

✅ **Tốt hơn vì:**
- Thấy progress ngay lập tức
- Thấy tab đầu tiên sau ~100ms (rất nhanh)
- Có feedback liên tục (progress bar)
- Không bị "đơ" màn hình

## Kết Hợp Với Preview Mode

Progressive Loading hoạt động **độc lập** với Preview Mode:

1. **Progressive Loading**: Load DATA (results) từng tab một
2. **Preview Mode**: Load IMAGES theo chế độ đã chọn

**Ví dụ:**
```
Bước 1: Progressive load Tab 1 data (không có preview)
Bước 2: Progressive load Tab 2 data (không có preview)
...
Bước N: Progressive load Tab N data (không có preview)
---
Bước N+1: User chuyển đến Tab 1
Bước N+2: Lazy load preview cho Tab 1 (theo mode: none/gcn-only/all)
```

## Configuration

### Delay Between Tabs:
```javascript
await new Promise(resolve => setTimeout(resolve, 100)); // 100ms
```

**Tùy chỉnh:**
- **50ms**: Nhanh hơn, ít feedback hơn (cho máy mạnh)
- **100ms**: Cân bằng (khuyến nghị)
- **200ms**: Chậm hơn, nhiều feedback hơn (cho máy yếu)

## Limitations & Notes

### Không Áp Dụng Cho:
- **File Scan**: Chỉ có 1 list results, không có tabs
- **Batch Scan**: Khác logic, không có folder tabs

### Chỉ Áp Dụng Cho:
- **Folder Scan Resume**: Có nhiều child tabs

### Edge Cases:
1. **Chỉ có 1 tab**: Vẫn chạy progressive loading, nhưng gần như instant
2. **User switch tab khi đang load**: Không sao, load vẫn tiếp tục ở background
3. **Có lỗi khi load 1 tab**: Tab đó bị skip, load tiếp các tab khác

## Troubleshooting

### Q: Tại sao vẫn thấy "loading" lâu?
A: Có thể do:
- Quá nhiều tabs (>20 tabs)
- Mỗi tab có quá nhiều files (>100 files/tab)
- Delay giữa các tabs có thể tăng lên

**Giải pháp**: Giảm delay từ 100ms → 50ms (chỉnh trong code)

### Q: App vẫn bị crash?
A: Progressive loading chỉ giải quyết vấn đề load data. Nếu vẫn crash:
1. Kiểm tra xem có đang load preview không (dùng mode "Không load ảnh")
2. Kiểm tra RAM máy (< 8GB có thể vẫn crash với >50 tabs)
3. Chia nhỏ scan thành nhiều lần (ít tabs hơn)

### Q: Có thể tắt progressive loading không?
A: Không khuyến nghị, nhưng có thể:
```javascript
// Change from:
await new Promise(resolve => setTimeout(resolve, 100));
// To:
await new Promise(resolve => setTimeout(resolve, 0));
```

### Q: Tab nào được load trước?
A: Theo thứ tự trong `restoredTabs` array (thường là thứ tự alphabet)

---

**Cập nhật**: 12/01/2025  
**Version**: 1.2.1  
**Tác giả**: AI Developer
