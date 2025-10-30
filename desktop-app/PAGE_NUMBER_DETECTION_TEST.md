# Page Number Detection - Testing Phase

## 📋 Summary

Added page number detection capability to Gemini Flash AI classification for testing. This will help identify continuation pages and enable smart sequential naming.

**Thêm khả năng detect số trang vào Gemini Flash AI để test. Sẽ giúp nhận diện continuation pages và enable smart sequential naming.**

---

## 🎯 Purpose

**Problem:**
- Continuation pages (page 2, 3, 4...) are classified as UNKNOWN
- No way to know which pages belong together
- Sequential naming is manual

**Solution:**
- Detect page number at bottom of page
- Use page number to assign previous pages to correct document
- Automatic sequential naming

---

## 🔧 Implementation (Testing Phase)

### **1. Updated Gemini Prompt**

Added new instruction:
```
8. 🆕 KIỂM TRA SỐ TRANG (nếu có):
   - Tìm số trang ở BOTTOM của trang (70-100% area)
   - Formats: "3", "Trang 3", "- 3 -", "Page 3"
   - NẾU tìm thấy số trang → Trả về trong field "page_number"
```

**Response format updated:**
```json
{
  "short_code": "UNKNOWN",
  "confidence": 0.1,
  "title_position": "none",
  "page_number": "3",  // NEW FIELD
  "reasoning": "No main title, but page 3 detected at bottom"
}
```

### **2. Parse Function Updated**

**File:** `/app/desktop-app/python/ocr_engine_gemini_flash.py`

```python
# Parse and validate page_number
page_number = result.get('page_number', None)
if page_number:
    # Extract digits only: "3" or "Trang 3" → "3"
    digit_match = re.search(r'\d+', str(page_number))
    if digit_match:
        page_number = digit_match.group(0)
        print(f"📄 Page number detected: {page_number}")
    else:
        page_number = None
```

### **3. Process Document Updated**

**File:** `/app/desktop-app/python/process_document.py`

```python
# Log page number in result
page_number = result.get('page_number', None)
page_info = f", page: {page_number}" if page_number else ""
print(f"⏱️ Result: ... {page_info}")

# Include in response
return {
    ...
    "page_number": result.get("page_number", None),
    ...
}
```

---

## 📊 Expected Detection Formats

Gemini should detect these formats:

### **Common Vietnamese formats:**
- `"3"` → page_number: "3"
- `"Trang 3"` → page_number: "3"
- `"- 3 -"` → page_number: "3"
- `"Trang 3/10"` → page_number: "3"

### **English formats:**
- `"Page 3"` → page_number: "3"
- `"3 / 10"` → page_number: "3"

### **Invalid formats (return null):**
- `"III"` (Roman numerals - not supported yet)
- `"ba"` (Vietnamese words)
- No page number → page_number: null

---

## 🧪 Testing Plan

### **Phase 1: Detection Accuracy**

Test with various documents:

**Test Case 1: Simple page number**
```
Document with "3" at bottom
Expected: page_number: "3"
```

**Test Case 2: "Trang 3" format**
```
Document with "Trang 3" at bottom
Expected: page_number: "3"
```

**Test Case 3: "- 3 -" format**
```
Document with "- 3 -" at bottom
Expected: page_number: "3"
```

**Test Case 4: No page number**
```
Document without page number
Expected: page_number: null
```

**Test Case 5: Page number with total**
```
Document with "Trang 3/10"
Expected: page_number: "3"
```

### **Phase 2: Position Verification**

Verify page numbers are in BOTTOM area:
- Page number at 70-100% → Valid
- Page number at 0-30% (TOP) → Likely false positive (might be date)
- Page number at 30-70% (MIDDLE) → Likely false positive

### **Phase 3: Success Rate**

Measure detection rate:
- Test with 20-30 documents
- Count: How many have page numbers?
- Count: How many detected correctly?
- Calculate: Success rate %

**Target:** >80% success rate for documents with page numbers

---

## 📝 Test Results Log

### **Format:**
```
Document: [filename]
Actual page number: [3 or null]
Detected page number: [3 or null]
Format: ["3", "Trang 3", "- 3 -", etc.]
Success: [✅ or ❌]
Notes: [any observations]
```

### **Example:**
```
Document: VBTK_page3.png
Actual page number: 3
Detected page number: "3"
Format: "- 3 -"
Success: ✅
Notes: Detected correctly at bottom right
```

---

## 🎯 Next Steps (After Testing)

### **If detection works well (>80% accuracy):**

**Step 1: Implement Sequential Naming Logic**
```python
def assign_sequential_names(documents):
    for i, doc in enumerate(documents):
        if doc.page_number:
            page_num = int(doc.page_number)
            
            # Find base document (last non-UNKNOWN before this sequence)
            base_doc = find_base_doc(documents, i, page_num)
            
            # Assign names to previous pages
            for j in range(page_num - 1):
                prev_index = i - (page_num - 1 - j)
                if prev_index >= 0:
                    documents[prev_index].name = f"{base_doc.short_code}_{j+1}"
```

**Step 2: Handle Edge Cases**
- Multiple sequences (reset on new title)
- Non-sequential pages (gaps)
- Misdetections (validation)

**Step 3: User Option**
- Add toggle: "Use page numbers for naming"
- Default: ON (if detection >80%)

### **If detection doesn't work well (<80% accuracy):**

**Alternative approaches:**
- Use only GCNM continuation patterns (existing)
- Manual page assignment by user
- Distance-based grouping (consecutive UNKNOWNs)

---

## 💡 Benefits (If Successful)

1. **Automatic Sequential Naming:**
   ```
   Page 1: GCNM (title page)
   Page 2: UNKNOWN → Auto-named: GCNM_2
   Page 3: UNKNOWN → Auto-named: GCNM_3
   ```

2. **Better Batch Scanning:**
   - Handle mixed documents with confidence
   - Correct grouping even with title-less pages

3. **User Experience:**
   - Less manual intervention
   - Fewer classification errors

---

## ⚠️ Limitations

1. **Only works with printed page numbers**
   - Documents without page numbers: No benefit
   - Handwritten numbers: May not detect

2. **Requires BOTTOM area**
   - We scan 100% now, so covered
   - If cropping, must include bottom

3. **Potential false positives:**
   - Dates at bottom (15/03/2025)
   - Reference numbers
   - Need validation in logic

---

## 📅 Timeline

**Week 1 (Current):**
- ✅ Implement detection logic
- ✅ Update prompt and parser
- 🔄 Test with user's documents

**Week 2 (If successful):**
- Implement sequential naming logic
- Add edge case handling
- Deploy to production

**Week 2 (If unsuccessful):**
- Analyze failure cases
- Consider alternative approaches
- Document findings

---

## 📊 Success Metrics

**Detection Accuracy:**
- Target: >80% for documents with page numbers
- Acceptable: >70%
- Failed: <70% → Alternative approach

**False Positive Rate:**
- Target: <10%
- Acceptable: <20%
- Failed: >20% → Need validation logic

**User Feedback:**
- Positive: Reduces manual work
- Negative: Creates more errors than it solves

---

## 🔧 Files Modified

1. `/app/desktop-app/python/ocr_engine_gemini_flash.py`
   - Updated prompt (lines 1085-1115)
   - Updated parse function (lines 1160-1180)

2. `/app/desktop-app/python/process_document.py`
   - Updated logging (line 159)
   - Added page_number to response (line 203)

---

## 📝 Testing Instructions for User

**Please test and report:**

1. Scan some documents with visible page numbers
2. Check terminal output for: `📄 Page number detected: X`
3. Report back:
   - How many documents tested?
   - How many have page numbers?
   - How many detected correctly?
   - Any false positives (detected wrong number)?
   - Any false negatives (missed page number)?

**Format:**
```
Tested: 10 documents
With page numbers: 7
Detected correctly: 5/7 (71%)
False positives: 1 (detected "15" from date)
False negatives: 1 (missed "- 3 -" format)
```

---

## 📅 Date

**Implemented:** December 2024

**Status:** 🧪 TESTING PHASE

**Next Action:** Await user testing feedback to determine if feature should be fully implemented or abandoned.
