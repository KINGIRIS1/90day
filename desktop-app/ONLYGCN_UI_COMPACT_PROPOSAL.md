# 🎨 OnlyGCN UI Compact Proposal

## 📊 HIỆN TẠI vs ĐỀ XUẤT

### 1. MODE SELECTION (Hiện tại)
```
┌────────────────────────────────────────────────────────────┐
│  [📁 Quét thư mục]  [📋 Quét theo danh sách]  [✓ Pre-filter]│
│  💡 Quét tất cả file trong 1 thư mục                        │
│  • Pre-filter BẬT: Chỉ quét file có màu đỏ/hồng...        │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~80px**

### 1. MODE SELECTION (Đề xuất - Compact)
```
┌──────────────────────────────────────────────────┐
│ [Thư mục] [Danh sách]    [✓ Pre-filter]         │
└──────────────────────────────────────────────────┘
```
**Chiều cao: ~40px (-50%)**

---

### 2. CONTROLS (Hiện tại)
```
┌────────────────────────────────────────────────────────────┐
│  [📁 Chọn thư mục]  [▶️ Bắt đầu quét]  [📚 Gộp PDF]      │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~60px**

### 2. CONTROLS (Đề xuất - Compact)
```
┌────────────────────────────────────────────────────────────┐
│ [📁 Chọn]  [▶️ Quét]  [📚 Gộp]                            │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~40px (-33%)**

---

### 3. FOLDER LIST (Hiện tại)
```
┌────────────────────────────────────────────────────────────┐
│  📁 3 thư mục, 61 files                                     │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~50px** ✅ Đã gọn

---

### 4. PROGRESS (Hiện tại)
```
┌────────────────────────────────────────────────────────────┐
│  file.jpg                                        12/58      │
│  [████████████░░░░░░░░░░░░░░░░]                           │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~50px** ✅ Đã gọn

---

### 5. FOLDER TABS (Hiện tại)
```
┌────────────────────────────────────────────────────────────┐
│  [📂 Folder1 ✅ (58)]  [📂 Folder2 ✅ (61)]  [📂 Folder3]  │
└────────────────────────────────────────────────────────────┘
```
**Chiều cao: ~45px** ✅ OK

---

### 6. STATS (Hiện tại)
```
┌──────────┬──────────┬──────────┬──────────┐
│ 58 files │ 2 GCNC   │ 4 GCNM   │ 52 GTLQ  │
└──────────┴──────────┴──────────┴──────────┘
```
**Chiều cao: ~45px** ✅ Đã gọn

---

### 7. TABLE HEADERS (Hiện tại)
```
┌──┬────────┬───────────────┬─────────────┬─────────────┬────────┐
│# │ Folder │   File Name   │   AI Kết quả │  Phân loại  │ Score  │
└──┴────────┴───────────────┴─────────────┴─────────────┴────────┘
```
**Chiều cao: ~40px**

### 7. TABLE HEADERS (Đề xuất - Compact)
```
┌──┬───────┬──────────┬────┬────┬───┐
│# │ Folder│  File    │ AI │ GCN│ % │
└──┴───────┴──────────┴────┴────┴───┘
```
**Chiều cao: ~35px**

---

## 🎯 TỔNG HỢP THAY ĐỔI

### Buttons:
- **Text**: "📁 Chọn thư mục" → "📁 Chọn"
- **Text**: "▶️ Bắt đầu quét" → "▶️ Quét"
- **Text**: "📚 Gộp PDF" → "📚 Gộp"
- **Text**: "📋 Quét theo danh sách" → "Danh sách"
- **Size**: `px-4 py-2` → `px-3 py-1.5` (smaller padding)
- **Font**: `font-medium` → `text-sm` (smaller text)

### Mode Selector:
- **Remove**: Dòng chú thích dài "💡 Quét tất cả file..."
- **Remove**: Dòng thông báo pre-filter "• Pre-filter BẬT..."
- **Simplify**: Tooltip hover thay vì text luôn hiển thị

### Table:
- **Headers**: Rút gọn text
  - "File Name" → "File"
  - "AI Kết quả" → "AI"
  - "Phân loại" → "GCN"
  - "Score" → "%"
- **Font**: `text-sm` → `text-xs` cho headers
- **Padding**: `px-4 py-3` → `px-3 py-2` cho cells

---

## 📐 KÍCH THƯỚC ƯỚC TÍNH

**HIỆN TẠI:**
```
Mode selection:    80px
Controls:          60px
Folder list:       50px
Progress:          50px
Tabs:              45px
Stats:             45px
Table header:      40px
─────────────────────────
TOTAL:           370px (chưa có table rows)
```

**SAU KHI LÀM GỌN:**
```
Mode selection:    40px  (-40px, -50%)
Controls:          40px  (-20px, -33%)
Folder list:       50px  (giữ nguyên)
Progress:          50px  (giữ nguyên)
Tabs:              45px  (giữ nguyên)
Stats:             45px  (giữ nguyên)
Table header:      35px  (-5px, -12%)
─────────────────────────
TOTAL:           305px  (-65px, -17.5%)
```

**Tiết kiệm: ~65px chiều cao → Nhìn gọn hơn ~18%**

---

## 🎨 MOCKUP GIAO DIỆN COMPACT

```
┌─────────────────────────────────────────────────────────────┐
│ Only GCN Scanner                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Thư mục] [Danh sách]              [✓ Pre-filter]          │  ← 40px
│                                                              │
│ [📁 Chọn] [▶️ Quét] [⏹ Dừng] [📚 Gộp]                      │  ← 40px
│                                                              │
│ 📁 3 thư mục, 178 files                                     │  ← 50px
│                                                              │
│ [📂 Folder1 ✅ (58)] [📂 Folder2 ✅ (61)] [📂 Folder3 (59)] │  ← 45px
│                                                              │
│ [58 files] [2 GCNC] [4 GCNM] [52 GTLQ]                     │  ← 45px
│                                                              │
│ ┌──┬─────┬────────────┬────┬────┬───┐                      │
│ │# │Fldr │ File       │ AI │GCN │ % │                      │  ← 35px (header)
│ ├──┼─────┼────────────┼────┼────┼───┤                      │
│ │1 │F1   │20221026... │GCN │GCNC│95 │                      │  ← 32px (row)
│ │2 │F1   │20221026... │GCN │GCNM│92 │                      │
│ │3 │F1   │20221026... │GCN │GCNM│88 │                      │
│ │4 │F1   │S00001...   │GCN │GCNM│91 │                      │
│ │... (scroll)                           │                   │
│ └──┴─────┴────────────┴────┴────┴───┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Tổng chiều cao phần controls: 305px (giảm 17.5%)**

---

## ✅ DANH SÁCH THAY ĐỔI CỤ THỂ

### 1. Mode Selection Box
```javascript
// OLD
className="mb-4 bg-gray-50 rounded-lg p-4 border"
"px-4 py-2 rounded-lg font-medium"
"📁 Quét thư mục"
"📋 Quét theo danh sách"
+ Dòng chú thích dài

// NEW
className="mb-3 bg-gray-50 rounded-lg p-2 border"
"px-3 py-1.5 rounded-lg text-sm"
"Thư mục"
"Danh sách"
- Remove chú thích
```

### 2. Controls Box
```javascript
// OLD
className="mb-6 bg-white rounded-lg shadow-sm p-4"
"px-4 py-2 ... font-medium"
"📁 Chọn thư mục"
"▶️ Bắt đầu quét"
"📚 Gộp PDF"

// NEW
className="mb-3 bg-white rounded-lg shadow-sm p-3"
"px-3 py-1.5 text-sm"
"📁 Chọn"
"▶️ Quét"
"📚 Gộp"
```

### 3. Table Headers
```javascript
// OLD
<th className="px-4 py-3 text-left text-xs font-medium">
  File Name
</th>

// NEW
<th className="px-3 py-2 text-left text-xs font-medium">
  File
</th>
```

### 4. Table Cells
```javascript
// OLD
<td className="px-4 py-3 text-sm">

// NEW
<td className="px-3 py-2 text-xs">
```

---

## 🤔 CÂU HỎI CHO USER

1. **Button text**: Bạn có muốn rút gọn text buttons không?
   - "Chọn thư mục" → "Chọn" ✅
   - "Bắt đầu quét" → "Quét" ✅
   - "Gộp PDF" → "Gộp" ✅

2. **Chú thích**: Có bỏ các dòng chú thích dài không?
   - "💡 Quét tất cả file..." → Bỏ ✅
   - "• Pre-filter BẬT..." → Bỏ ✅

3. **Table**: Có rút gọn table headers không?
   - "File Name" → "File" ✅
   - "AI Kết quả" → "AI" ✅
   - "Phân loại" → "GCN" ✅

4. **Font size**: Có giảm kích chữ buttons/table không?
   - Buttons: `font-medium` → `text-sm` ✅
   - Table: `text-sm` → `text-xs` ✅

**Nếu đồng ý tất cả → Tiết kiệm ~18% chiều cao UI!**

