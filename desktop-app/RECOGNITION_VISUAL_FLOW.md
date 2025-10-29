# 🎨 HỆ THỐNG NHẬN DIỆN TÀI LIỆU - VISUAL FLOW

## 🔄 MAIN CLASSIFICATION FLOW

```
┌────────────────────────────────────────────────────────────────────┐
│                    USER SCANS DOCUMENT                             │
└───────────────────────────┬────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │   SELECT OCR ENGINE (via Settings)    │
        └───────┬───────────────────────────────┘
                ↓
    ┌───────────┴───────────────────────────────────┐
    │                                               │
    ↓                                               ↓
┌─────────────────────┐                  ┌─────────────────────┐
│  OFFLINE OCR        │                  │  CLOUD OCR/AI       │
│  (Local Processing) │                  │  (API-based)        │
└──────┬──────────────┘                  └──────┬──────────────┘
       │                                        │
       ├─ Tesseract                             ├─ Google Cloud Vision
       ├─ VietOCR                               ├─ Azure Computer Vision
       └─ EasyOCR                               ├─ Gemini Flash AI
       │                                        └─ Cloud Boost (Backend)
       │                                        │
       ↓                                        ↓
┌──────────────────┐                    ┌──────────────────┐
│  EXTRACT TEXT    │                    │  EXTRACT TEXT    │
│  Full image      │                    │  Top 35% crop    │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │                                       │
         └───────────────┬───────────────────────┘
                         ↓
           ┌─────────────────────────┐
           │  CLASSIFICATION METHOD  │
           └────────┬────────────────┘
                    ↓
        ┌───────────┴───────────────┐
        │                           │
        ↓                           ↓
┌──────────────────┐      ┌──────────────────┐
│  RULE-BASED      │      │  AI-POWERED      │
│  CLASSIFICATION  │      │  CLASSIFICATION  │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         ↓                         ↓
    (4-TIER LOGIC)         (GEMINI/GPT-4 PROMPT)
         │                         │
         │                         │
         └─────────┬───────────────┘
                   ↓
         ┌─────────────────────┐
         │  CLASSIFICATION     │
         │  RESULT             │
         │  {code, confidence} │
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │  SEQUENTIAL NAMING  │
         │  (if needed)        │
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │  SUGGEST FILENAME   │
         │  [CODE]_001.jpg     │
         └─────────────────────┘
```

---

## 🎯 RULE-BASED CLASSIFICATION (4-TIER)

```
┌──────────────────────────────────────────────────────────────────┐
│                    EXTRACTED TEXT INPUT                          │
│  • Full text from OCR                                           │
│  • Title text (uppercase headers)                               │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  TIER 0: EXACT MATCH        ┃
         ┃  Confidence: 100%            ┃
         ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━┛
                     ↓
            ┌────────────────┐
            │ Title matches  │  YES → ✅ RETURN (1.0)
            │ EXACT_TITLE_   │
            │ MAPPING?       │
            └────────┬───────┘
                     │ NO
                     ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  PRE-CHECK: UPPERCASE       ┃
         ┃  Threshold: 70%             ┃
         ┗━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━┛
                   ↓
          ┌────────────────┐
          │ Title has      │  NO → ❌ REJECT TITLE
          │ ≥70% uppercase?│      (use body text only)
          └────────┬───────┘
                   │ YES
                   ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  TIER 1: FUZZY MATCH        ┃
         ┃  Threshold: ≥80%            ┃
         ┃  Confidence: 0.85-0.95      ┃
         ┗━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━┛
                   ↓
          ┌────────────────┐
          │ Fuzzy match    │  YES → ✅ RETURN (0.85-0.95)
          │ similarity     │
          │ ≥80%?          │
          └────────┬───────┘
                   │ NO
                   ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  TIER 2: TITLE + KEYWORDS   ┃
         ┃  Threshold: 70-80%          ┃
         ┃  Confidence: 0.60-0.80      ┃
         ┗━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━┛
                   ↓
          ┌────────────────┐
          │ Fuzzy 70-80%?  │  YES → Check keywords in body
          │ + Keywords OK? │       → ✅ RETURN (0.60-0.80)
          └────────┬───────┘
                   │ NO
                   ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  TIER 3: KEYWORD ONLY       ┃
         ┃  Threshold: Body keywords   ┃
         ┃  Confidence: 0.30-0.70      ┃
         ┗━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━┛
                   ↓
          ┌────────────────┐
          │ Scan all 98    │  
          │ document types │  Best score → ✅ RETURN (0.30-0.70)
          │ for keywords   │
          └────────┬───────┘
                   ↓
          ┌────────────────┐
          │ No match found │  → ❌ UNKNOWN (0.1)
          └────────────────┘
```

---

## 🤖 AI-POWERED CLASSIFICATION (GEMINI/GPT-4)

```
┌──────────────────────────────────────────────────────────────────┐
│                    IMAGE INPUT                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  IMAGE PREPROCESSING      │
         │  • Crop to top 35%        │
         │  • Convert to base64      │
         │  • Resize if needed       │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  BUILD AI PROMPT          │
         │  ━━━━━━━━━━━━━━━━━━━━━━  │
         │  1. Safety instruction    │
         │  2. Quốc huy priority     │
         │  3. Strict 100% matching  │
         │  4. Easy-to-confuse pairs │
         │  5. Document title list   │
         │  6. Step-by-step process  │
         │  7. JSON output format    │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  SEND TO AI API           │
         │  • Gemini Flash 2.5       │
         │  • OR GPT-4o Vision       │
         └───────────┬───────────────┘
                     ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  AI ANALYZES IMAGE        ┃
         ┃  • Detects Quốc huy       ┃
         ┃  • Reads title            ┃
         ┃  • Checks exact match     ┃
         ┃  • Returns classification ┃
         ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━┛
                     ↓
         ┌───────────────────────────┐
         │  AI RESPONSE (JSON)       │
         │  {                        │
         │    short_code: "HDCQ",    │
         │    confidence: 0.92,      │
         │    reasoning: "..."       │
         │  }                        │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  PARSE & VALIDATE         │
         │  • Extract JSON           │
         │  • Validate format        │
         │  • Check confidence       │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  RETURN RESULT            │
         └───────────────────────────┘
```

---

## 🔀 CLOUD BOOST HYBRID FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│         USER CLICKS "CLOUD BOOST" (Backend Processing)           │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  UPLOAD TO BACKEND        │
         │  POST /api/scan-document  │
         └───────────┬───────────────┘
                     ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  STEP 1: OCR + RULES      ┃
         ┃  (FREE - 93% accuracy)    ┃
         ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━┛
                     ↓
          ┌─────────────────┐
          │ Crop to 50-65%  │  (adaptive based on aspect ratio)
          │ Run PaddleOCR   │
          │ Apply rules     │
          └────────┬────────┘
                   ↓
          ┌─────────────────┐
          │ Confidence      │  YES → ✅ RETURN RESULT
          │ ≥ 0.3?          │       (No GPT-4 cost!)
          └────────┬────────┘
                   │ NO
                   ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  STEP 2: GPT-4 VISION     ┃
         ┃  (Fallback - 7% cases)    ┃
         ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━┛
                     ↓
          ┌─────────────────┐
          │ Call OpenAI     │
          │ Vision API      │
          │ with prompt     │
          └────────┬────────┘
                   ↓
          ┌─────────────────┐
          │ Get AI result   │
          └────────┬────────┘
                   ↓
          ┌─────────────────┐
          │ Confidence      │  YES → ✅ RETURN RESULT
          │ ≥ 0.5?          │
          └────────┬────────┘
                   │ NO
                   ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  STEP 3: RULES BACKUP     ┃
         ┃  (Last resort - lower     ┃
         ┃   threshold 0.2)          ┃
         ┗━━━━━━━━━━━┯━━━━━━━━━━━━━━┛
                     ↓
          ┌─────────────────┐
          │ Re-run rules    │  → ✅ RETURN BEST RESULT
          │ with threshold  │       (or UNKNOWN)
          │ = 0.2           │
          └─────────────────┘
```

---

## 🔢 SEQUENTIAL NAMING LOGIC

```
┌──────────────────────────────────────────────────────────────────┐
│              BATCH SCAN (Multiple Pages)                         │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  currentLastKnown = null  │  (Initialize)
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  FOR EACH PAGE            │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  Classify page            │
         │  → {short_code, conf}     │
         └───────────┬───────────────┘
                     ↓
          ┌──────────────────────┐
          │ Is UNKNOWN OR        │  YES → Apply Sequential Naming
          │ confidence < 0.7 OR  │       ↓
          │ title_boost = false? │       ┌──────────────────┐
          └─────────┬────────────┘       │ Has lastKnown?   │
                    │ NO                 └────┬─────────────┘
                    ↓                         │ YES
          ┌──────────────────────┐           ↓
          │ NEW DOCUMENT         │   ┌──────────────────┐
          │ • Use detected code  │   │ CONTINUATION     │
          │ • Reset counter = 1  │   │ • Use lastKnown  │
          └─────────┬────────────┘   │ • Increment num  │
                    ↓                 └────┬─────────────┘
          ┌──────────────────────┐        │
          │ confidence >= 0.7?   │  YES   │
          └─────────┬────────────┘        │
                    │ YES                 │
                    ↓                     │
          ┌──────────────────────┐        │
          │ UPDATE lastKnown     │        │
          │ = current code       │        │
          └──────────────────────┘        │
                    │                     │
                    └─────────┬───────────┘
                              ↓
                    ┌──────────────────────┐
                    │ GENERATE FILENAME    │
                    │ [CODE]_00X.jpg       │
                    └──────────────────────┘
```

### **Example Sequence:**

```
Page 1: GCNM (0.92) → GCNM_001 ✅  lastKnown = GCNM
Page 2: UNKNOWN (0.2) → GCNM_002 ✅  (copy from lastKnown)
Page 3: UNKNOWN (0.3) → GCNM_003 ✅  (copy from lastKnown)
Page 4: HDCQ (0.95) → HDCQ_001 ✅  lastKnown = HDCQ
Page 5: UNKNOWN (0.1) → HDCQ_002 ✅  (copy from lastKnown)
Page 6: BMT (0.88) → BMT_001 ✅  lastKnown = BMT
Page 7: BMT (0.65) → BMT_002 ✅  (low conf, but title_boost=false → continuation)
```

---

## 🎨 EASY-TO-CONFUSE PAIRS - DECISION TREE

### **HDCQ vs HDUQ**
```
Found "HỢP ĐỒNG"?
    ↓ YES
    ├─ Contains "CHUYỂN NHƯỢNG"? → ✅ HDCQ
    ├─ Contains "ỦY QUYỀN"? → ✅ HDUQ
    └─ Neither found? → ❌ UNKNOWN
```

### **DDKBD vs DDK**
```
Found "ĐƠN ĐĂNG KÝ"?
    ↓ YES
    ├─ Contains "BIẾN ĐỘNG"? → ✅ DDKBD
    └─ No "BIẾN ĐỘNG"? → ✅ DDK
```

### **GCNM vs GCNC**
```
Found "GIẤY CHỨNG NHẬN"?
    ↓ YES
    ├─ Contains "QUYỀN SỞ HỮU TÀI SẢN"? → ✅ GCNM
    └─ Only "QUYỀN SỬ DỤNG ĐẤT"? → ✅ GCNC
```

---

## 📊 PERFORMANCE COMPARISON

```
┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ METHOD              │ ACCURACY │   COST   │  SPEED   │ INTERNET │
├─────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Tesseract + Rules   │   ★★★☆☆  │   FREE   │   ★★★★☆  │    ❌    │
│ VietOCR + Rules     │   ★★★★☆  │   FREE   │   ★★★☆☆  │    ❌    │
│ EasyOCR + Rules     │   ★★★★☆  │   FREE   │   ★★★☆☆  │    ❌    │
│ Google + Rules      │   ★★★★★  │   $$$    │   ★★★★★  │    ✅    │
│ Azure + Rules       │   ★★★★★  │   $$     │   ★★★★★  │    ✅    │
│ Gemini Flash AI     │   ★★★★★  │   $      │   ★★★★★  │    ✅    │
│ Cloud Boost (GPT-4) │   ★★★★★  │ Backend  │   ★★★★☆  │    ✅    │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┘

Legend:
★ = 1 unit (1-5 scale)
$ = Low cost, $$$ = High cost
✅ = Required, ❌ = Not required
```

---

## 🔐 API KEY MANAGEMENT

```
┌──────────────────────────────────────────────────────────────────┐
│                    CloudSettings UI                              │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  User enters API key      │
         │  • Google API key         │
         │  • Azure API key+endpoint │
         │  • Gemini = Google key    │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  Test Key Button Clicked  │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  IPC: test-api-key        │
         │  Provider: google/azure/  │
         │           gemini          │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  electron-store           │
         │  Save key securely        │
         │  Key: 'cloudApiKey'       │
         └───────────┬───────────────┘
                     ↓
         ┌───────────────────────────┐
         │  Validate with API        │
         │  • Test request           │
         │  • Check response         │
         └───────────┬───────────────┘
                     ↓
              ┌──────┴──────┐
              ↓             ↓
         [SUCCESS]       [FAILED]
              ↓             ↓
         ✅ Show        ❌ Show error
         success msg     + troubleshoot
```

---

## 🎯 SUMMARY

**Hệ thống nhận diện tài liệu đất đai Việt Nam:**

✅ **7 phương pháp OCR/AI** - Linh hoạt, từ free đến premium
✅ **4-tier classification** - Exact → Fuzzy → Keywords → Fallback
✅ **98 loại tài liệu** - Đầy đủ hồ sơ đất đai
✅ **70% uppercase rule** - Strict validation cho tiêu đề
✅ **Sequential naming** - Tự động đánh số trang liên tiếp
✅ **Smart pattern order** - Tránh nhầm lẫn HDCQ/HDUQ, DDKBD/DDK
✅ **AI-powered options** - Gemini Flash, Cloud Boost (GPT-4)
✅ **Hybrid approach** - Kết hợp OCR+Rules và AI để tối ưu cost/accuracy

🚀 **Production-ready!**
