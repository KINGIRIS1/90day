# 🔧 FIX: Sequential Naming Quá Cứng

## ❌ VẤN ĐỀ TRƯỚC ĐÂY

Logic sequential naming quá rộng, áp dụng cho TẤT CẢ files:

```javascript
// Logic CŨ (SAI):
const shouldUseSequential = 
  result.short_code === 'UNKNOWN' || 
  result.confidence < 0.7 ||           // ❌ QUÁ CAO!
  !result.title_text ||                // ❌ QUÁ STRICT!
  title_text.length < 10;              // ❌ QUÁ STRICT!
```

**Hậu quả:**
- File có confidence 0.6-0.7 (tốt) → Bị coi là UNKNOWN
- File có classification đúng → Vẫn lấy tên file trước
- **TẤT CẢ files đều lấy tên từ file đầu tiên!**

---

## ✅ GIẢI PHÁP MỚI

### 1. Thu hẹp điều kiện áp dụng sequential naming

**CHỈ áp dụng khi:**

```javascript
const shouldUseSequential = 
  result.short_code === 'UNKNOWN' ||                      // ✓ Thực sự UNKNOWN
  (result.confidence < 0.3 && result.short_code !== 'UNKNOWN'); // ✓ Confidence CỰC THẤP
```

**Giải thích:**
- `short_code === 'UNKNOWN'` → Không nhận dạng được gì → Lấy tên file trước ✓
- `confidence < 0.3` → Confidence cực thấp (< 30%) → Không tin tưởng được → Lấy tên file trước ✓
- `confidence >= 0.3` → Tin tưởng được → Dùng classification của file này ✓

---

### 2. Tăng threshold update currentLastKnown

**Trước:**
```javascript
if (confidence >= 0.5 && !applied_sequential_logic) {
  currentLastKnown = result;  // ❌ Quá thấp
}
```

**Sau:**
```javascript
if (confidence >= 0.6 && !applied_sequential_logic) {
  currentLastKnown = result;  // ✓ Chỉ track khi confident
}
```

**Lý do:** Chỉ lưu vào memory khi classification đủ tin cậy (>= 60%)

---

## 📊 SO SÁNH TRƯỚC VÀ SAU

### **Trước (Quá cứng):**

```
File 1: DDKBD (0.95) → Lưu memory: DDKBD
File 2: HDCQ  (0.65) → confidence < 0.7 → Lấy DDKBD ❌ (SAI!)
File 3: GCNM  (0.70) → confidence < 0.7 → Lấy DDKBD ❌ (SAI!)
File 4: CCCD  (0.60) → confidence < 0.7 → Lấy DDKBD ❌ (SAI!)

Kết quả: TẤT CẢ đều thành DDKBD!
```

---

### **Sau (Chính xác):**

```
File 1: DDKBD (0.95) → Lưu memory: DDKBD ✓
File 2: HDCQ  (0.65) → confidence >= 0.3 → Dùng HDCQ ✓ → Lưu memory
File 3: GCNM  (0.70) → confidence >= 0.3 → Dùng GCNM ✓ → Lưu memory
File 4: UNKNOWN (0.0) → Lấy GCNM ✓ (trang tiếp theo)
File 5: CCCD  (0.60) → confidence >= 0.3 → Dùng CCCD ✓ → Lưu memory

Kết quả: Mỗi file đúng classification riêng!
```

---

## 🎯 KHI NÀO ÁP DỤNG SEQUENTIAL?

### ✅ ÁP DỤNG (Chỉ 2 trường hợp):

1. **File THỰC SỰ UNKNOWN:**
   ```
   short_code: 'UNKNOWN'
   → Không nhận dạng được gì
   → Lấy tên file trước
   ```

2. **Confidence CỰC THẤP (< 30%):**
   ```
   short_code: 'HDCQ'
   confidence: 0.15  (15% - rất thấp)
   → Không tin tưởng được
   → Lấy tên file trước
   ```

---

### ❌ KHÔNG ÁP DỤNG:

1. **Classification tốt (confidence >= 30%):**
   ```
   short_code: 'HDCQ'
   confidence: 0.65  (65% - tốt)
   → Tin tưởng được
   → Dùng HDCQ ✓
   ```

2. **Classification khá (confidence 30-60%):**
   ```
   short_code: 'GCNM'
   confidence: 0.45  (45% - khá)
   → Vẫn OK
   → Dùng GCNM ✓
   ```

---

## 📋 THRESHOLDS MỚI

| Metric | Threshold | Ý nghĩa |
|--------|-----------|---------|
| **Sequential naming** | `confidence < 0.3` | Chỉ áp dụng khi CỰC THẤP |
| **Update memory** | `confidence >= 0.6` | Chỉ lưu khi đủ tin cậy |
| **Trust result** | `confidence >= 0.3` | Tin tưởng classification |

---

## 🧪 TEST CASES

### Test 1: Mixed documents (confidence cao)

**Input:**
```
File 1: DDKBD (0.95)
File 2: HDCQ (0.85)
File 3: GCNM (0.70)
```

**Expected (SAU FIX):**
```
File 1: DDKBD ✓
File 2: HDCQ ✓
File 3: GCNM ✓
```

**Before (TRƯỚC FIX):**
```
File 1: DDKBD ✓
File 2: DDKBD ❌ (0.85 > 0.7 nhưng có check khác)
File 3: DDKBD ❌
```

---

### Test 2: Multi-page document

**Input:**
```
File 1: DDKBD (0.95) - Trang 1 có title
File 2: UNKNOWN (0.0) - Trang 2 không title
File 3: UNKNOWN (0.0) - Trang 3 không title
```

**Expected (VẪN ĐÚNG):**
```
File 1: DDKBD ✓
File 2: DDKBD ✓ (sequential)
File 3: DDKBD ✓ (sequential)
```

---

### Test 3: Low confidence (< 30%)

**Input:**
```
File 1: HDCQ (0.95)
File 2: GCNM (0.25) - Confidence cực thấp
File 3: CCCD (0.80)
```

**Expected:**
```
File 1: HDCQ ✓
File 2: HDCQ ✓ (sequential - không tin 0.25)
File 3: CCCD ✓
```

---

## 📂 FILES MODIFIED

- `/app/desktop-app/src/components/DesktopScanner.js`
  - `applySequentialNaming`: confidence threshold 0.7 → 0.3
  - `currentLastKnown` update: threshold 0.5 → 0.6
  - Removed title_text checks (quá strict)

---

## ✅ KẾT QUẢ

**Trước:**
- ❌ Tất cả files đều lấy tên file đầu tiên
- ❌ Files có classification tốt bị ghi đè
- ❌ Logic quá cứng, không flexible

**Sau:**
- ✅ Mỗi file có classification riêng (nếu confidence >= 30%)
- ✅ Chỉ áp dụng sequential khi THỰC SỰ cần
- ✅ Logic linh hoạt, chính xác hơn

---

## 🎓 LESSON LEARNED

1. **Conservative approach is better** - Chỉ can thiệp khi cần thiết
2. **Trust the classifier** - Nếu confidence >= 30%, đã đủ tin tưởng
3. **Test with real data** - Phải test với nhiều scenarios khác nhau
4. **Monitor thresholds** - Thresholds phải cân nhắc kỹ, không quá cao cũng không quá thấp

---

## 📝 SUMMARY

**Fix:** Sequential naming từ "quá cứng" → "vừa phải"

**Key changes:**
- Sequential threshold: 0.7 → 0.3 (chặt chẽ hơn)
- Memory threshold: 0.5 → 0.6 (tin cậy hơn)
- Removed title_text checks (quá strict)

**Result:** Mỗi file có classification riêng, chỉ kế thừa khi THỰC SỰ UNKNOWN hoặc confidence cực thấp.
