# ✅ Gemini Flash - Complete 98 Document Types Integration

## 📅 Ngày cập nhật
**December 2024**

## 🎯 Objective
Cập nhật Gemini Flash prompt để bao gồm **TOÀN BỘ 98 loại tài liệu** với format dễ đọc, được chia thành 12 nhóm logic.

---

## 📊 BEFORE vs AFTER

### **Before:**
- ❌ Chỉ liệt kê ~20 loại tài liệu phổ biến nhất
- ❌ Không có nhóm phân loại
- ❌ Thiếu nhiều loại tài liệu quan trọng
- ❌ Format khó đọc (danh sách dài không có cấu trúc)

### **After:**
- ✅ **Đầy đủ 98 loại tài liệu**
- ✅ **Chia thành 12 nhóm logic** với emoji
- ✅ **Highlight các cặp dễ nhầm** (⚠️ DỄ NHẦM)
- ✅ **Format dễ đọc** (theo nhóm chức năng)
- ✅ **Consistency với rule_classifier.py** (EXACT_TITLE_MAPPING)

---

## 📋 12 NHÓM TÀI LIỆU

### **Nhóm 1: BẢN VẼ / BẢN ĐỒ** (5 loại)
```
BMT, HSKT, BVHC, BVN, SDTT
```
**Đặc điểm:** Tài liệu kỹ thuật, bản vẽ địa chính

### **Nhóm 2: BẢNG KÊ / DANH SÁCH** (4 loại)
```
BKKDT, DSCG, DS15, DSCK
```
**Đặc điểm:** Bảng liệt kê, danh sách thống kê

### **Nhóm 3: BIÊN BẢN** (10 loại)
```
BBBDG, BBGD, BBHDDK, BBNT, BBKTSS, BBKTHT, BBKTDC, KTCKCG, KTCKMG, BLTT
```
**Đặc điểm:** Biên bản xác nhận, ghi nhận sự kiện

### **Nhóm 4: GIẤY TỜ CÁ NHÂN** (4 loại)
```
CCCD, GKS, GKH, DICHUC
```
**Đặc điểm:** Giấy tờ định danh, hồ sơ cá nhân

### **Nhóm 5: GIẤY CHỨNG NHẬN** (9 loại)
```
GCNM, GCNC, GXNNVTC, GNT, GSND, GTLQ, GUQ, GXNDKLD, GPXD
```
**Đặc điểm:** Giấy chứng nhận quyền, xác nhận

### **Nhóm 6: HỢP ĐỒNG** ⚠️ DỄ NHẦM (7 loại)
```
HDCQ, HDUQ, HDTHC, HDTD, HDTCO, HDBDG, hoadon
```
**Đặc điểm:** Hợp đồng giao dịch (PHẢI phân biệt từ khóa)
- HDCQ: "CHUYỂN NHƯỢNG"
- HDUQ: "ỦY QUYỀN"
- HDTHC: "THẾ CHẤP"
- HDTD: "THUÊ ĐẤT"

### **Nhóm 7: ĐƠN** ⚠️ DỄ NHẦM (15 loại)
```
DDKBD, DDK, DCK, CHTGD, DCQDGD, DMG, DMD, DXN, DXCMD, DGH, DXGD, DXTHT, DXCD, DDCTH, DXNTH
```
**Đặc điểm:** Đơn đề nghị, đơn xin phép
- DDKBD: có "BIẾN ĐỘNG"
- DDK: không có "BIẾN ĐỘNG"

### **Nhóm 8: QUYẾT ĐỊNH** ⚠️ DỄ NHẦM (15 loại)
```
QDGTD, QDCMD, QDTH, QDGH, QDTT, QDCHTGD, QDDCGD, QDDCTH, QDHG, QDPDBT, QDDCQH, QDPDDG, QDTHA, QDHTSD, QDXP
```
**Đặc điểm:** Quyết định hành chính (PHẢI có từ khóa cụ thể)
- QDGTD: "GIAO ĐẤT"
- QDCMD: "CHO PHÉP CHUYỂN MỤC ĐÍCH"
- QDTH: "THU HỒI"
- QDGH: "GIA HẠN"

### **Nhóm 9: PHIẾU** (8 loại)
```
PCT, PKTHS, PLYKDC, PXNKQDD, DKTC, DKTD, DKXTC, QR
```
**Đặc điểm:** Phiếu yêu cầu, phiếu xác nhận

### **Nhóm 10: THÔNG BÁO** (8 loại)
```
TBT, TBMG, TBCKCG, TBCKMG, HTNVTC, TBCNBD, CKDC, HTBTH
```
**Đặc điểm:** Thông báo hành chính, xác nhận

### **Nhóm 11: TỜ KHAI / TỜ TRÌNH** (3 loại)
```
TKT, TTr, TTCG
```
**Đặc điểm:** Tờ khai thuế, tờ trình đề xuất

### **Nhóm 12: VĂN BẢN** (10 loại)
```
CKTSR, VBCTCMD, VBDNCT, PDPASDD, VBTK, TTHGD, CDLK, HCLK, VBTC, PCTSVC
```
**Đặc điểm:** Văn bản thỏa thuận, cam kết

---

## 🎯 CÁC CẶP DỄ NHẦM - HIGHLIGHTED

### **1. HỢP ĐỒNG (Contract Types)**

```
Priority Order (Check in this sequence):

1. HDCQ - "CHUYỂN NHƯỢNG"
   ↓ (if not found)
2. HDUQ - "ỦY QUYỀN"
   ↓ (if not found)
3. HDTHC - "THẾ CHẤP"
   ↓ (if not found)
4. HDTD - "THUÊ"
   ↓ (if not found)
5. HDTCO - "THI CÔNG"
   ↓ (if not found)
6. HDBDG - "MUA BÁN"
   ↓ (if none found)
7. UNKNOWN
```

**Lý do:** Nếu title có "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT"
- Contains both "CHUYỂN NHƯỢNG" and "QUYỀN" (might confuse with ỦY QUYỀN)
- **Solution:** Check HDCQ FIRST → Match → Return HDCQ ✅

### **2. ĐƠN ĐĂNG KÝ (Application Types)**

```
DDKBD vs DDK:

Title: "ĐƠN ĐĂNG KÝ [???] ĐẤT ĐAI"
         ↓
    Check [???]
         ↓
┌────────┴────────┐
│                 │
"BIẾN ĐỘNG"    (empty)
    ↓              ↓
  DDKBD          DDK
```

**Critical:** Must have explicit "BIẾN ĐỘNG" keyword → DDKBD
Without it → DDK

### **3. GIẤY vs HỢP ĐỒNG ỦY QUYỀN**

```
GUQ vs HDUQ:

"GIẤY ỦY QUYỀN" → GUQ (standalone authorization letter)
"HỢP ĐỒNG ỦY QUYỀN" → HDUQ (contract-based authorization)

MUST distinguish by checking for "HỢP ĐỒNG" prefix!
```

### **4. QUYẾT ĐỊNH (Decision Types)**

```
All start with "QUYẾT ĐỊNH" → Must check next keyword:

QUYẾT ĐỊNH + ?
    ↓
    ├─ "GIAO ĐẤT" → QDGTD
    ├─ "CHO PHÉP" → QDCMD
    ├─ "THU HỒI" → QDTH
    ├─ "GIA HẠN" → QDGH
    ├─ "TÁCH, HỢP" → QDTT
    └─ (other) → Check full list
```

### **5. GCNM vs GCNC**

```
Title: "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT [???]"
                                          ↓
                                    Check [???]
                                          ↓
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
        "QUYỀN SỞ HỮU TÀI SẢN GẮN LIỀN VỚI ĐẤT"              (empty)
                    ↓                                           ↓
                  GCNM                                        GCNC
            (New format, full)                        (Old format, short)
```

---

## 📝 PROMPT STRUCTURE

### **Section 1: Safety & Context** (Lines 1-25)
- Safety warning (ignore personal photos)
- Quốc huy priority
- 2-page horizontal document handling

### **Section 2: Strict Rules** (Lines 26-50)
- 100% exact matching requirement
- No guessing policy
- Multi-page awareness
- UNKNOWN threshold

### **Section 3: Easy-to-Confuse Pairs** (Lines 51-80)
- 5 detailed confusing pairs
- Decision trees for each
- Priority order for checking

### **Section 4: Complete Document List** (Lines 81-230)
- **12 groups** with emoji headers
- **98 document types** with full Vietnamese titles
- Short codes clearly mapped
- ⚠️ markers for confusing groups

### **Section 5: Process & Output** (Lines 231-250)
- Step-by-step verification process
- JSON output format
- Final reminders

---

## 🎨 FORMAT IMPROVEMENTS

### **Before:**
```
BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → GCNC
HỢP ĐỒNG CHUYỂN NHƯỢNG → HDCQ
...
(84 more mixed together without structure)
```

### **After:**
```
📋 NHÓM 1: BẢN VẼ / BẢN ĐỒ (5 loại)
BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
...

📋 NHÓM 5: GIẤY CHỨNG NHẬN (9 loại)
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → GCNC
...

📋 NHÓM 6: HỢP ĐỒNG (7 loại) ⚠️ DỄ NHẦM
HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT → HDCQ
HỢP ĐỒNG ỦY QUYỀN → HDUQ
...
```

**Benefits:**
- ✅ Easier for AI to scan by category
- ✅ Visual separation with emoji headers
- ✅ Warning markers for confusing groups
- ✅ Logical grouping helps pattern recognition

---

## 📊 COMPARISON WITH RULE_CLASSIFIER.PY

| Aspect | rule_classifier.py | Gemini Flash Prompt |
|--------|-------------------|---------------------|
| **Total Types** | 98 | 98 ✅ |
| **Exact Titles** | EXACT_TITLE_MAPPING | Full list ✅ |
| **Grouping** | No grouping | 12 groups ✅ |
| **Confusing Pairs** | Handled in code | Explicitly listed ✅ |
| **Format** | Python dict | Structured text ✅ |
| **Consistency** | Source of truth | 100% aligned ✅ |

---

## 🚀 EXPECTED IMPROVEMENTS

### **Accuracy:**
- ✅ Better recognition of rare document types
- ✅ Fewer "UNKNOWN" for valid documents
- ✅ More accurate handling of confusing pairs

### **Coverage:**
- ✅ All 98 types now explicitly known to AI
- ✅ No more "I don't see this type in the list"
- ✅ Complete Vietnamese title → Code mapping

### **Consistency:**
- ✅ 100% alignment with rule-based classifier
- ✅ Same results as OpenAI Vision (same prompt structure)
- ✅ Predictable behavior across all document types

---

## 🧪 TESTING RECOMMENDATIONS

### **Test with each group:**

1. **Nhóm 1-5:** Test 1-2 samples from each
2. **Nhóm 6 (HỢP ĐỒNG):** Test ALL types (easy to confuse)
3. **Nhóm 7 (ĐƠN):** Focus on DDKBD vs DDK
4. **Nhóm 8 (QUYẾT ĐỊNH):** Test 3-4 common types
5. **Nhóm 9-12:** Spot check 1-2 per group

### **Confusing pairs test:**
- [ ] HDCQ vs HDUQ with ambiguous titles
- [ ] DDKBD vs DDK with/without "biến động"
- [ ] GUQ vs HDUQ
- [ ] QDGTD vs QDCMD vs QDTH
- [ ] GCNM vs GCNC

### **Edge cases:**
- [ ] Document with no title (should return UNKNOWN)
- [ ] Document with partial title (should return UNKNOWN)
- [ ] 2-page horizontal GCNC
- [ ] Document with both "chuyển nhượng" and "ủy quyền"

---

## 📚 RELATED FILES

### **Updated:**
- `python/ocr_engine_gemini_flash.py` - Prompt updated

### **Reference:**
- `python/rule_classifier.py` - EXACT_TITLE_MAPPING (source of truth)
- `backend/server.py` - OpenAI Vision prompt (alignment reference)

### **Documentation:**
- `GEMINI_OPENAI_ALIGNMENT.md` - Prompt alignment
- `DOCUMENT_RECOGNITION_DETAILS.md` - Complete system overview
- `RECOGNITION_VISUAL_FLOW.md` - Visual diagrams

---

## ✅ STATUS

**COMPLETE** ✅

**Changes:**
- ✅ Prompt updated with all 98 types
- ✅ Grouped into 12 logical categories
- ✅ Confusing pairs highlighted
- ✅ Format improved for readability
- ✅ 100% aligned with rule_classifier.py

**Ready for:**
- User testing with real documents
- Accuracy comparison with rule-based classifier
- Production deployment

---

## 💡 FUTURE ENHANCEMENTS

1. **Dynamic Prompt Generation**
   - Load EXACT_TITLE_MAPPING from file
   - Auto-generate grouped list
   - Keep prompt in sync with rule updates

2. **Prompt Optimization**
   - A/B test different groupings
   - Test shorter vs longer descriptions
   - Optimize for Gemini Flash specifically

3. **Localization**
   - Test with different Vietnamese regional variations
   - Handle OCR errors in title recognition

---

**Summary:**
Gemini Flash prompt now includes **complete 98-document-type coverage** with structured format, grouped into 12 categories, and explicit handling of confusing pairs. 100% aligned with rule_classifier.py for consistency.
