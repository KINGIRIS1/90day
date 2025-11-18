# 📋 Tổng hợp TẤT CẢ quy tắc GCN

**Ngày tạo:** 20/11/2024  
**Mục đích:** Checklist đầy đủ các quy tắc GCN để đảm bảo OnlyGCNScanner xử lý giống BatchScanner & DesktopScanner

---

## 🎯 QUY TẮC 1: Pre-filter (Lọc trước khi quét AI)

### 1.1. Kiểm tra kích thước A3
**Nguồn:** `color_detector.py`

```python
aspect_ratio = width / height

if aspect_ratio <= 1.35:
    return 'unknown'  # Không phải A3, bỏ qua
```

**Logic:**
- GCN A3 có aspect ratio > 1.35 (landscape)
- VD: 4443×3135 = 1.42
- File A4 (2486×3516 = 0.71) → Reject

**Status trong OnlyGCNScanner:**
- ✅ **ĐÃ CÓ** (đã implement trong session này)

---

### 1.2. Kiểm tra màu sắc border
**Nguồn:** `color_detector.py`

```python
if avg_r > 80:
    if avg_g > 80 and avg_b > 80:
        return 'pink'
    else:
        return 'red'
```

**Logic:**
- Red/Orange border → Có thể là GCN
- Pink border → Có thể là GCN
- Không có màu → Reject

**Status trong OnlyGCNScanner:**
- ✅ **ĐÃ CÓ** (đã implement)

---

## 🎯 QUY TẮC 2: GCN Continuation (Trang 2 GCNM)

### 2.1. Nhận diện trang 2 GCNM
**Nguồn:** `classification_prompt_full.txt` (lines 336-386)

**⚠️ ĐẶC BIỆT:** Trang GCN continuation có thể đứng RIÊNG hoặc sau giấy tờ khác!

**Logic nhận diện:**

**Case 1: Có CẢ HAI sections (phải có đủ 2)**
```
1️⃣ "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ"
   +
   "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN"
   
   → GCNM (confidence: 0.85)
```

**Case 2: Có section standalone**
```
2️⃣ "THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"
   → GCNM (confidence: 0.85)
```

**Case 3: Có sections với số thứ tự (phải có đủ 2)**
```
3️⃣ "II. NỘI DUNG THAY ĐỔI"
   +
   "III. XÁC NHẬN CỦA CƠ QUAN"
   
   → GCNM (confidence: 0.85)
```

**⚠️ CỰC KỲ QUAN TRỌNG:**
- Phải có CẢ HAI sections (Case 1 hoặc 3)
- HOẶC có section standalone (Case 2)
- Nếu CHỈ CÓ MỘT trong hai sections → UNKNOWN

**Ví dụ:**
```
✅ ĐÚNG: Có cả "II. NỘI DUNG THAY ĐỔI" + "III. XÁC NHẬN" → GCNM
✅ ĐÚNG: Có "Thửa đất, nhà ở..." → GCNM
❌ SAI: Chỉ có "II. NỘI DUNG THAY ĐỔI" → UNKNOWN
❌ SAI: Chỉ có "III. XÁC NHẬN" → UNKNOWN
```

**Status trong OnlyGCNScanner:**
- ⚠️ **PHẦN AI**: AI đã được train (có trong prompt)
- ❌ **PHẦN FRONTEND**: CHƯA XỬ LÝ đặc biệt (coi như file độc lập)

---

## 🎯 QUY TẮC 3: GCN Pairing (Ghép cặp 2 trang)

### 3.1. Pairing logic
**Nguồn:** `BatchScanner.js` (lines 1485-1600)

**Logic:**
1. Group GCN theo màu: red, pink, unknown
2. Pair trong mỗi color group: 2 file liên tiếp = 1 cặp
3. Extract date từ pair (prefer page2, fallback page1)

**Ví dụ:**
```
Folder có 6 file GCN:
- File 1: GCN red (page 1)
- File 2: GCN red (page 2) → Pair 1 (red)
- File 3: GCN pink (page 1)
- File 4: GCN pink (page 2) → Pair 2 (pink)
- File 5: GCN red (page 1)
- File 6: GCN red (page 2) → Pair 3 (red)

Result: 3 pairs
```

**Status trong OnlyGCNScanner:**
- ❌ **CHƯA CÓ** (mỗi file xử lý độc lập)

---

### 3.2. Classification sau khi pairing
**Nguồn:** `BatchScanner.js` (lines 1562-1650)

**Case 1: Mixed colors (red + pink)**
```
Red pairs → GCNC
Pink pairs → GCNM
```

**Case 2: Same color → Classify by date**
```
Parse date từ mỗi pair
Sort by date
Oldest pair → GCNC
Newer pairs → GCNM
```

**Case 3: No dates / only 1 pair**
```
First/only pair → GCNC (default oldest)
```

**Status trong OnlyGCNScanner:**
- ⚠️ **PHẦN ĐANG CÓ**: Post-process by color/date (NHƯNG theo file, không theo pair)
- ❌ **THIẾU**: Không ghép cặp trước khi classify

---

## 🎯 QUY TẮC 4: Sequential Naming (Đặt tên theo file trước)

### 4.1. Rule 1: UNKNOWN → Use last known
**Nguồn:** `DesktopScanner.js` (lines 607-619)

```javascript
if (result.short_code === 'UNKNOWN' && lastType) {
  return {
    short_code: lastType.short_code,
    note: `📄 Trang tiếp theo của ${lastType.short_code}`
  };
}
```

**Status trong OnlyGCNScanner:**
- ❌ **CHƯA CÓ**

---

### 4.2. Rule 2: No title → Use last known
**Nguồn:** `DesktopScanner.js` (lines 622-638)

```javascript
if (!result.title_boost_applied && lastType) {
  return {
    short_code: lastType.short_code,
    note: `📄 Trang tiếp theo (no title)`
  };
}
```

**Status trong OnlyGCNScanner:**
- ❌ **CHƯA CÓ**

---

### 4.3. Rule 3: Title not at top + low confidence → Use last known
**Nguồn:** `DesktopScanner.js` (lines 641-655)

```javascript
if (result.title_position !== 'top' && result.confidence < 0.85 && lastType) {
  return {
    short_code: lastType.short_code,
    note: `📄 Trang tiếp theo (title at ${result.title_position})`
  };
}
```

**Status trong OnlyGCNScanner:**
- ❌ **CHƯA CÓ**

---

## 🎯 QUY TẮC 5: GCN Post-processing (GCNC/GCNM Classification)

### 5.1. Normalize GCN
**Nguồn:** `BatchScanner.js` (lines 1340-1346)

```javascript
if (r.short_code === 'GCNM' || r.short_code === 'GCNC') {
  return { ...r, short_code: 'GCN' };
}
```

**Status trong OnlyGCNScanner:**
- ✅ **ĐÃ CÓ** (đã implement trong session này)

---

### 5.2. Group by metadata (color + issue_date)
**Nguồn:** `BatchScanner.js` (lines 1375-1397)

```javascript
const groupKey = `${color}_${issueDate || 'null'}`;
gcnGroups.set(groupKey, { files, color, issueDate, parsedDate });
```

**Status trong OnlyGCNScanner:**
- ✅ **ĐÃ CÓ** (đã implement)

---

### 5.3. Classify by color or date
**Nguồn:** `BatchScanner.js` (lines 1408-1450)

**Mixed colors:**
```javascript
if (hasRedAndPink) {
  red/orange → GCNC
  pink → GCNM
}
```

**Same color:**
```javascript
else {
  Sort by date
  oldest → GCNC
  newer → GCNM
}
```

**Status trong OnlyGCNScanner:**
- ✅ **ĐÃ CÓ** (đã implement)

---

## 📊 CHECKLIST TỔNG HỢP

| Quy tắc | BatchScanner | DesktopScanner | OnlyGCNScanner | Status |
|---------|--------------|----------------|----------------|--------|
| **1. Pre-filter** | | | | |
| 1.1. Kiểm tra A3 size | ✅ | ✅ | ✅ | **ĐÃ CÓ** |
| 1.2. Kiểm tra màu sắc | ✅ | ✅ | ✅ | **ĐÃ CÓ** |
| **2. GCN Continuation** | | | | |
| 2.1. Nhận diện trang 2 GCNM | ✅ (AI) | ✅ (AI) | ✅ (AI) | **AI có, Frontend chưa** |
| **3. GCN Pairing** | | | | |
| 3.1. Ghép cặp 2 trang | ✅ | ✅ | ❌ | **THIẾU** |
| 3.2. Classify pairs | ✅ | ✅ | ❌ | **THIẾU** |
| **4. Sequential Naming** | | | | |
| 4.1. UNKNOWN → last known | ✅ | ✅ | ❌ | **THIẾU** |
| 4.2. No title → last known | ✅ | ✅ | ❌ | **THIẾU** |
| 4.3. Title position → last known | ✅ | ✅ | ❌ | **THIẾU** |
| **5. Post-processing** | | | | |
| 5.1. Normalize GCN | ✅ | ✅ | ✅ | **ĐÃ CÓ** |
| 5.2. Group by metadata | ✅ | ✅ | ✅ | **ĐÃ CÓ** |
| 5.3. Classify by color/date | ✅ | ✅ | ✅ | **ĐÃ CÓ** |

---

## 🎯 THIẾU GÌ TRONG OnlyGCNScanner?

### ❌ THIẾU 1: GCN Pairing Logic
**Impact:** HIGH  
**Mô tả:** Không ghép cặp 2 trang GCN → Phân loại sai

**Ví dụ vấn đề:**
```
Folder có 4 file GCN:
- File 1: Red page 1
- File 2: Red page 2
- File 3: Pink page 1  
- File 4: Pink page 2

HIỆN TẠI (SAI):
- Post-process: 2 red, 2 pink → Mixed colors → Red=GCNC, Pink=GCNM
- Result: 2 GCNC + 2 GCNM ❌

ĐÚNG (với pairing):
- Pair: 1 red pair, 1 pink pair → Mixed colors → Red pair=GCNC, Pink pair=GCNM
- Result: 1 GCNC (2 files) + 1 GCNM (2 files) ✅
```

---

### ❌ THIẾU 2: Sequential Naming
**Impact:** MEDIUM  
**Mô tả:** File UNKNOWN hoặc no title không kế thừa tên file trước

**Ví dụ vấn đề:**
```
File 1: GCNC (có tiêu đề)
File 2: UNKNOWN (trang 2 của GCNC, không có tiêu đề)

HIỆN TẠI (SAI):
- File 2 → GTLQ ❌

ĐÚNG (với sequential naming):
- File 2 → GCNC (kế thừa từ file 1) ✅
```

---

## 🛠️ KHUYẾN NGHỊ

### Mức độ ưu tiên:

1. **P0 - CRITICAL:** Thêm GCN Pairing Logic
   - Ảnh hưởng lớn đến độ chính xác
   - Cần cho việc phân loại GCNC/GCNM đúng

2. **P1 - HIGH:** Thêm Sequential Naming
   - Giải quyết trường hợp UNKNOWN/no title
   - Cải thiện trải nghiệm người dùng

3. **P2 - MEDIUM:** Xử lý đặc biệt cho GCN Continuation
   - AI đã nhận diện được
   - Frontend cần xử lý logic riêng

---

## 📝 IMPLEMENTATION NOTES

**Nếu thêm GCN Pairing:**
- Copy logic từ `BatchScanner.js` (lines 1485-1650)
- Adapt cho OnlyGCNScanner workflow
- Test với folder có nhiều GCN (4-6 files)

**Nếu thêm Sequential Naming:**
- Copy logic từ `DesktopScanner.js` (lines 605-655)
- Maintain `lastKnownType` state
- Apply sau khi AI scan, trước post-processing

**Nếu xử lý GCN Continuation:**
- Không cần thay đổi AI prompt (đã có)
- Frontend xử lý đặc biệt khi thấy GCNM continuation
- Có thể kết hợp với Sequential Naming

---

**Document maintained by:** E1 Agent (Fork 2)  
**Last updated:** 20/11/2024
