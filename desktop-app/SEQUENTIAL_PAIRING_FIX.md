# 🔧 Sequential Pairing Logic Fix

## 📋 Tóm tắt
Đã sửa lỗi nghiêm trọng trong logic ghép cặp tuần tự (sequential pairing) khiến tất cả các file GCN hợp lệ bị đổi tên thành GTLQ.

---

## 🐛 Vấn đề (Bug)

### Triệu chứng
- Tất cả file GCN hợp lệ trong thư mục bị đổi tên thành `GTLQ`
- Chỉ file đầu tiên có thể giữ phân loại GCN đúng (nếu nó thực sự là GCN)
- Các file GCN sau đó đều bị "lây nhiễm" và đổi thành GTLQ

### Log lỗi người dùng báo cáo
```
File 1: HSKT → GTLQ ✅ (đúng)
File 2: GCN → GTLQ ❌ (sai - phải là GCN)
File 3: GCN → GTLQ ❌ (sai - phải là GCN)
File 4: GCN → GTLQ ❌ (sai - phải là GCN)
...
```

---

## 🔍 Nguyên nhân (Root Cause)

### Logic cũ (bị lỗi)
```javascript
// ❌ WRONG LOGIC
for (let i = 0; i < folderResults.length - 1; i++) {
  const current = folderResults[i];
  const next = folderResults[i + 1];
  
  if (current.newShortCode === 'GTLQ' && next.newShortCode === 'GCN') {
    next.newShortCode = 'GTLQ';  // Convert all GCN after GTLQ!
  }
}
```

### Tại sao sai?
1. **Không kiểm tra nguồn gốc**: Logic chỉ kiểm tra `newShortCode` (kết quả sau xử lý), không kiểm tra `originalShortCode` (phân loại ban đầu từ AI)
2. **Lan truyền lỗi**: Một khi file GCN đầu tiên bị đổi thành GTLQ, tất cả file GCN sau đó cũng bị đổi theo
3. **Không phân biệt loại tài liệu**: Logic giả định rằng mọi file GTLQ đều là tài liệu 2 trang, nhưng thực tế GTLQ có thể là:
   - Tài liệu 2 trang: HSKT, PCT, SDTT, GPXD, PLHS
   - Tài liệu 1 trang: Nhiều loại khác
   - File bị AI phân loại sai

### Kịch bản lỗi chi tiết
```
Giả sử thư mục có: [HSKT page1, HSKT page2, GCN1, GCN2]

Bước 1: Xử lý AI
- HSKT page1: originalShortCode=HSKT → newShortCode=GTLQ ✅
- HSKT page2: originalShortCode=HSKT → newShortCode=GTLQ ✅
- GCN1: originalShortCode=GCN → newShortCode=GCN ✅
- GCN2: originalShortCode=GCN → newShortCode=GCN ✅

Bước 2: Sequential Pairing (LOGIC CŨ)
- i=0: current=GTLQ(HSKT p1), next=GTLQ(HSKT p2)
  → Không làm gì (cả 2 đều GTLQ)
  
- i=1: current=GTLQ(HSKT p2), next=GCN(GCN1)
  → ❌ current là GTLQ, next là GCN → ĐỔI GCN1 THÀNH GTLQ (SAI!)
  
- i=2: current=GTLQ(GCN1-vừa đổi), next=GCN(GCN2)
  → ❌ current là GTLQ, next là GCN → ĐỔI GCN2 THÀNH GTLQ (SAI!)

→ Kết quả: TẤT CẢ đều thành GTLQ!
```

---

## ✅ Giải pháp (Solution)

### Logic mới (đúng)
```javascript
// ✅ CORRECT LOGIC
const twoPageDocTypes = ['HSKT', 'PCT', 'SDTT', 'GPXD', 'PLHS'];

for (let i = 0; i < folderResults.length - 1; i++) {
  const current = folderResults[i];
  const next = folderResults[i + 1];
  
  const currentIsMultiPage = twoPageDocTypes.includes(current.originalShortCode);
  const nextIsNotGcnByAI = !['GCNC', 'GCNM', 'GCN'].includes(next.originalShortCode);
  
  // Only pair if:
  // 1. Current was classified by AI as a 2-page doc (HSKT/PCT/etc)
  // 2. Current is now GTLQ
  // 3. Next was NOT classified by AI as GCN
  if (current.newShortCode === 'GTLQ' && currentIsMultiPage && 
      next.newShortCode === 'GCN' && nextIsNotGcnByAI) {
    next.newShortCode = 'GTLQ';
  }
}
```

### Điều kiện ghép cặp mới
Logic chỉ ghép cặp (pair) khi **TẤT CẢ** các điều kiện sau đều đúng:

| Điều kiện | Mô tả | Lý do |
|-----------|-------|-------|
| `current.newShortCode === 'GTLQ'` | File trước đó đã được chuyển thành GTLQ | Đảm bảo đang xét file không phải GCN |
| `currentIsMultiPage` | AI phân loại file trước là HSKT/PCT/SDTT/GPXD/PLHS | Chỉ các loại này mới có 2 trang |
| `next.newShortCode === 'GCN'` | File tiếp theo đang là GCN | Tránh đổi file đã là GTLQ |
| `nextIsNotGcnByAI` | AI KHÔNG phân loại file tiếp theo là GCN | Bảo vệ GCN thực sự |

### Kịch bản sau khi sửa
```
Giả sử thư mục có: [HSKT page1, HSKT page2, GCN1, GCN2]

Bước 2: Sequential Pairing (LOGIC MỚI)
- i=0: current=GTLQ(HSKT p1), next=GTLQ(HSKT p2)
  → Không làm gì
  
- i=1: current=GTLQ(HSKT p2), next=GCN(GCN1)
  ✅ Check: currentIsMultiPage? YES (HSKT)
  ✅ Check: nextIsNotGcnByAI? NO (AI says GCN)
  → Không đổi! GCN1 vẫn là GCN ✅
  
- i=2: current=GCN(GCN1), next=GCN(GCN2)
  → current không phải GTLQ → Không làm gì

→ Kết quả: HSKT → GTLQ, GCN → GCN ✅
```

---

## 📊 Kết quả

### Trước khi sửa
```
Input:  [HSKT, HSKT, GCN, GCN, GCN]
Output: [GTLQ, GTLQ, GTLQ, GTLQ, GTLQ] ❌
```

### Sau khi sửa
```
Input:  [HSKT, HSKT, GCN, GCN, GCN]
Output: [GTLQ, GTLQ, GCN, GCN, GCN] ✅
```

---

## 🧪 Test Cases

### Test Case 1: GCN hợp lệ không bị ảnh hưởng
```
Input:  [GCN-pink, GCN-pink, GCN-red, GCN-red]
Expected: [GCNM, GCNM, GCNC, GCNC]
```

### Test Case 2: HSKT 2 trang được xử lý đúng
```
Input:  [HSKT-page1, HSKT-page2, GCN]
AI says: [HSKT, HSKT, GCN]
Expected: [GTLQ, GTLQ, GCN/GCNC/GCNM]
```

### Test Case 3: AI phân loại sai (GCN thật nhưng AI says HSKT)
```
Input:  [GCN-actually, GCN-actually]
AI says: [HSKT, HSKT]
Expected: [GTLQ, GTLQ]  (Follow AI classification)
```

### Test Case 4: Mixed documents
```
Input:  [HSKT, HSKT, GCN, PCT, PCT, GCN]
AI says: [HSKT, HSKT, GCN, PCT, PCT, GCN]
Expected: [GTLQ, GTLQ, GCN, GTLQ, GTLQ, GCN]
```

---

## 📁 Files Modified
- `/app/desktop-app/src/components/OnlyGCNScanner.js` (lines 648-676)

## 🎯 Impact
- ✅ Sửa lỗi BLOCKER khiến chức năng "Only GCN" hoàn toàn không dùng được
- ✅ Bảo vệ tất cả file GCN hợp lệ khỏi bị đổi tên nhầm
- ✅ Vẫn giữ chức năng ghép cặp trang 2 cho các tài liệu 2 trang (HSKT, PCT, etc.)
- ✅ Thêm logging chi tiết để debug dễ dàng hơn

## 🚀 Next Steps
1. ✅ Code đã được sửa
2. ✅ Build thành công
3. ⏳ Chờ user testing để xác nhận fix
4. 🔜 Nếu OK → Proceed to Issue #2 (GCN page 1-2 pairing for date sync)

---

**Status**: ✅ Fixed, ⏳ Awaiting User Verification
**Build**: ✅ Successful (106.72 kB)
