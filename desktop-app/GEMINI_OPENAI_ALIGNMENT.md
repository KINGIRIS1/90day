# Gemini Flash - OpenAI Vision Prompt Alignment

## 📅 Date
**December 2024**

## 🎯 Objective
Align Gemini Flash classification prompt with OpenAI Vision backend prompt to ensure **consistent classification quality** across Cloud Boost (backend) and Gemini Flash (desktop).

---

## 🔄 Changes Made

### Before: Basic Prompt
The original Gemini Flash prompt was simpler and less strict:
- Listed 98 document codes
- Basic rules for title detection
- Simple confidence thresholds
- Less emphasis on exact matching

### After: OpenAI-Aligned Prompt
**Updated to match backend OpenAI Vision prompt structure:**

#### ✅ Key Improvements:

1. **Strict 100% Exact Matching**
   - ❌ Old: "gần giống" (approximate matching)
   - ✅ New: ONLY accept 100% exact title matches
   - ✅ Return UNKNOWN if not confident

2. **Quốc Huy (National Emblem) Priority**
   - ✅ Prioritize detection of Vietnamese national emblem
   - ✅ Emblem = official government document

3. **Ignore Personal Photos**
   - ✅ Explicit instruction to ignore ID photos
   - ✅ Focus only on text and official stamps

4. **Easy-to-Confuse Pairs**
   - HDCQ vs HDUQ (chuyển nhượng vs ủy quyền)
   - DDKBD vs DDK (có "biến động" vs không)
   - HDCQ vs HDTD vs HDTHC (chuyển nhượng vs thuê vs thế chấp)
   - GCNM vs GCNC (có "sở hữu tài sản" vs không)

5. **Multi-Page Awareness**
   - Page 1: Has title → New document
   - Page 2+: No title → Continuation (handled by frontend)
   - Only switch to new type when seeing NEW 100% match

6. **2-Page Horizontal Documents**
   - Orange/yellow background with emblem on RIGHT → GCNC
   - Focus on RIGHT page for title reading

7. **Key Document Titles Listed**
   - Includes most common/important titles
   - Shows exact Vietnamese title → Code mapping
   - Emphasizes EXACT matching requirement

---

## 📊 Prompt Structure Comparison

| Aspect | Old Prompt | New Prompt (OpenAI-aligned) |
|--------|------------|----------------------------|
| **Length** | ~150 lines | ~180 lines |
| **Strictness** | Moderate | Very strict (100% match) |
| **Emblem Focus** | Mentioned | Prioritized |
| **Photo Handling** | Not mentioned | Explicit ignore instruction |
| **Confusing Pairs** | 3-4 examples | 5-6 detailed examples |
| **Multi-page** | Basic | Detailed explanation |
| **Title List** | Codes only | Full titles + codes |
| **Output Format** | JSON | JSON (strict) |

---

## 🎯 Expected Results

### Consistency with Backend
- ✅ Same classification logic as OpenAI Vision
- ✅ Same strictness (100% exact match)
- ✅ Same UNKNOWN threshold
- ✅ Same handling of edge cases

### Quality Improvements
- ✅ **Fewer false positives** - won't classify ambiguous docs
- ✅ **Better GCNM/GCNC distinction** - checks for "sở hữu tài sản"
- ✅ **Better HDCQ/HDUQ distinction** - checks exact keywords
- ✅ **More UNKNOWN results** - but more accurate when confident

---

## 🧪 Testing Recommendations

### Test Cases:
1. **GCNC** - 2-page horizontal, orange background
2. **GCNM** - Must have "quyền sở hữu tài sản gắn liền với đất"
3. **HDCQ** - Must have "chuyển nhượng"
4. **HDUQ** - Must have "ủy quyền"
5. **DDKBD** - Must have "biến động"
6. **DDK** - "đăng ký đất đai" but NO "biến động"
7. **Ambiguous doc** - Should return UNKNOWN
8. **Continuation page** - No title → Should return UNKNOWN (frontend handles)

### Expected Behavior:
- Clear titles → High confidence (0.9)
- Ambiguous titles → UNKNOWN (0.1)
- No guessing or approximation
- Consistent with backend Cloud Boost results

---

## 📝 Code Changes

### File: `/app/desktop-app/python/ocr_engine_gemini_flash.py`
**Function:** `get_classification_prompt()`

**Line count:**
- Before: ~65 lines
- After: ~180 lines

**Key additions:**
1. Safety instruction (ignore personal photos)
2. Quốc huy priority section
3. Strict 100% matching rules
4. Easy-to-confuse pairs with examples
5. Multi-page handling explanation
6. Common document titles with exact mapping
7. Step-by-step verification process

---

## 🔗 Related Files
- `ocr_engine_gemini_flash.py` - Updated prompt
- `/app/backend/server.py` - Original OpenAI Vision prompt (lines 594-677)
- `GEMINI_MODEL_UPDATE_COMPLETE.md` - Model version update
- `GEMINI_FLASH_SETUP_GUIDE.md` - User guide

---

## ✅ Status
**COMPLETE** ✅

**Ready for:**
- User testing with real Vietnamese documents
- Quality comparison with Cloud Boost
- Production deployment

---

## 💡 Future Enhancements

1. **Dynamic Title Loading**
   - Load full EXACT_TITLE_MAPPING from rule_classifier.py
   - Keep prompt in sync with backend rules

2. **Confidence Calibration**
   - Track Gemini Flash accuracy vs OpenAI Vision
   - Adjust confidence thresholds if needed

3. **Prompt A/B Testing**
   - Test variations to optimize for Gemini Flash specifically
   - May need different wording than OpenAI for best results

4. **Cost Optimization**
   - Current: 35% crop (inherited from Google Vision)
   - Consider: Different crop % for Gemini Flash

---

**Summary:**
Gemini Flash now uses the same strict, detailed prompt as OpenAI Vision backend, ensuring consistent classification quality between Cloud Boost (online) and Gemini Flash (desktop). The prompt emphasizes 100% exact matching, national emblem detection, and proper handling of easy-to-confuse document pairs.
