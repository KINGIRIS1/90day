# 🔧 Only GCN Logic Fix - Align with BatchScanner

## 📋 Tóm tắt
Đã loại bỏ logic "convert to GTLQ" không cần thiết trong tab "Only GCN" để đồng bộ với logic của BatchScanner.

---

## 🐛 Vấn đề (Bug)

### Triệu chứng
- File GCN hợp lệ bị AI phân loại SAI là HSKT → Bị đổi thành GTLQ (mất mát thông tin)
- File "Trích lục bản đồ" (không phải GCN) bị AI phân loại SAI là GCN → Vẫn được giữ là GCN
- Tab "Only GCN" cho kết quả khác với tab "Batch Mode" mặc dù chỉ khác logic pre-filter A3

### Log lỗi người dùng báo cáo
```
File: S00001 (1).jpg
- Thực tế: GCN trang 1 (màu hồng)
- AI phân loại: HSKT ❌
- OnlyGCN result: GTLQ ❌ (SAI - mất thông tin GCN)

File: 20221026-102061.jpg
- Thực tế: "Trích lục bản đồ địa chính" (không phải GCN)
- AI phân loại: GCN ❌
- OnlyGCN result: GCN/GCNM ❌ (SAI - không phải GCN)
```

---

## 🔍 Nguyên nhân (Root Cause)

### So sánh logic giữa BatchScanner vs OnlyGCNScanner

#### BatchScanner (ĐÚNG)
```javascript
// Map batch results to BatchScanner format
mappedResults.push({
  filePath: filePath,
  fileName: fileName,
  short_code: batchItem.short_code || 'UNKNOWN',  // ✅ Accept AI result directly
  doc_type: batchItem.short_code || 'UNKNOWN',
  confidence: batchItem.confidence || 0.5,
  // ... other fields
});
```

#### OnlyGCNScanner (SAI - Logic cũ)
```javascript
// ❌ WRONG: Force convert non-GCN to GTLQ
let newShortCode = 'GTLQ';  // Default to GTLQ
let newDocType = 'Giấy tờ liên quan';
const shortCode = batchItem.short_code || '';

if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
  newShortCode = 'GCN';
  newDocType = 'Giấy chứng nhận';
} else if (shortCode) {
  // ❌ Convert ALL non-GCN to GTLQ
  console.log(`⚠️ ${fileName}: AI says ${shortCode} → Converting to GTLQ`);
  newShortCode = 'GTLQ';
  newDocType = 'Giấy tờ liên quan';
}
```

### Tại sao logic cũ sai?

**Vấn đề 1: Không tôn trọng kết quả AI**
- Logic giả định rằng mọi file "đã qua pre-filter A3" đều phải là GCN
- Nếu AI phân loại là HSKT/PCT/etc → Bị force convert thành GTLQ
- Điều này làm MẤT THÔNG TIN phân loại gốc từ AI

**Vấn đề 2: Pre-filter A3 không hoàn hảo**
- Pre-filter chỉ lọc theo aspect ratio (khổ A3)
- Nhiều loại tài liệu khác cũng có khổ A3: HSKT, PCT, Trích lục bản đồ, etc.
- Không thể giả định "A3 = GCN"

**Vấn đề 3: Không xử lý được lỗi AI**
- Khi AI phân loại SAI (ví dụ: GCN → HSKT), logic "convert to GTLQ" sẽ làm tình hình tệ hơn
- Người dùng không thể biết AI đã phân loại gì ban đầu

**Vấn đề 4: Khác biệt với BatchScanner**
- BatchScanner chấp nhận kết quả AI trực tiếp → Hoạt động tốt
- OnlyGCNScanner cố gắng "sửa" kết quả AI → Gây lỗi
- Người dùng không hiểu tại sao 2 tab cho kết quả khác nhau

---

## ✅ Giải pháp (Solution)

### Logic mới (đúng)
```javascript
// ✅ CORRECT: Accept AI classification directly (same as BatchScanner)
const shortCode = batchItem.short_code || 'UNKNOWN';
let newShortCode = shortCode;
let newDocType = batchItem.doc_type || shortCode;
```

### Thay đổi chính

| Thành phần | Trước đây | Bây giờ |
|------------|-----------|---------|
| **Default value** | `newShortCode = 'GTLQ'` | `newShortCode = shortCode` |
| **Logic xử lý** | Convert non-GCN → GTLQ | Accept AI result as-is |
| **Sequential pairing** | Pair HSKT page 2 | Removed (không cần) |
| **Header description** | "GCN A3 → GCN \| File khác → GTLQ" | "Pre-filter A3 → Phân loại tự động" |
| **Stats logging** | "X GCNC, Y GCNM, Z GTLQ" | "X GCNC, Y GCNM, Z other docs" |

### Files đã sửa

**File: `/app/desktop-app/src/components/OnlyGCNScanner.js`**

1. **Batch processing logic** (lines ~496-510)
   - Removed: Convert to GTLQ logic
   - Added: Direct AI result acceptance

2. **Single-file processing logic** (lines ~570-583)
   - Removed: Convert to GTLQ logic
   - Added: Direct AI result acceptance

3. **Sequential pairing logic** (lines ~627-653)
   - Removed: Entire pairing logic
   - Reason: Not needed when accepting AI results directly

4. **UI Header** (line ~788)
   - Updated description to reflect new behavior

5. **Console logging** (lines ~646-660)
   - Changed from "GTLQ count" to "other docs count"

---

## 📊 Kết quả

### Trước khi sửa
```
Input:  [GCN (AI says HSKT), GCN, Trích lục (AI says GCN)]
Output: [GTLQ ❌, GCN ✅, GCNM ❌]
```

### Sau khi sửa
```
Input:  [GCN (AI says HSKT), GCN, Trích lục (AI says GCN)]
Output: [HSKT (AI result), GCN ✅, GCN (AI result)]
→ Người dùng có thể thấy AI đã phân loại gì
→ Có thể edit manual nếu AI sai
```

---

## 🎯 Benefits

### ✅ Consistency
- OnlyGCN giờ hoạt động GIỐNG BatchScanner
- Người dùng không bị confuse bởi kết quả khác nhau

### ✅ Transparency
- Người dùng thấy được phân loại GỐC từ AI
- Dễ dàng phát hiện khi AI phân loại sai

### ✅ Flexibility
- Người dùng có thể edit manual thông qua UI
- Không bị ép buộc phải chấp nhận "GTLQ" cho mọi non-GCN

### ✅ Simplicity
- Code đơn giản hơn (ít logic hơn)
- Dễ maintain và debug hơn

---

## 🧪 Test Cases

### Test Case 1: GCN hợp lệ
```
Input:  GCN files with pink color
AI says: GCN
Expected: GCNC/GCNM (based on date)
```

### Test Case 2: HSKT trong thư mục
```
Input:  HSKT files (A3 size, passed pre-filter)
AI says: HSKT
Expected: HSKT (not GTLQ)
```

### Test Case 3: AI phân loại sai
```
Input:  GCN file
AI says: HSKT (wrong!)
Expected: HSKT (show AI result, user can edit)
```

### Test Case 4: Mixed documents
```
Input:  [GCN, HSKT, PCT, Trích lục bản đồ]
AI says: [GCN, HSKT, PCT, GCN (wrong!)]
Expected: [GCNC/GCNM, HSKT, PCT, GCN]
→ User can see and fix AI mistakes
```

---

## 🔮 Future Improvements

### Option 1: Improve AI Accuracy
- Tune AI prompt to better distinguish document types
- Add examples of "Trích lục bản đồ" to training

### Option 2: Add Rule-based Post-processing
- Check for keywords: "Trích lục bản đồ" → Force to specific type
- Validate GCN structure (must have certain fields)

### Option 3: Upgrade AI Model
- Use stronger model (gemini-flash instead of gemini-flash-lite)
- Consider hybrid approach with multiple models

---

## 📝 Notes

**Why not keep "convert to GTLQ" logic?**
- Pre-filter A3 is NOT perfect → Many non-GCN docs are also A3
- AI classification is the SOURCE OF TRUTH
- If AI is wrong, better to show the mistake than hide it

**What about "Only GCN" purpose?**
- Original purpose: Focus on GCN classification
- New approach: Pre-filter A3 to reduce workload, then trust AI
- Users can filter GCN in UI if needed (already implemented)

---

**Status**: ✅ Fixed
**Build**: ✅ Successful (106.41 kB, -319 B)
**Testing**: ⏳ Awaiting User Verification
