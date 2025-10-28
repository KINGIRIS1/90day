# Low Quality Title Detection Rule

## Overview
Automatically detect when OCR extracts poor quality title text and recommend using the previous page's classification instead.

## Rule Logic (TIER 0 - Pre-Check)

Vietnamese administrative document titles are **ALWAYS uppercase** (70-100% uppercase ratio).

### Trigger Conditions
The rule activates when **BOTH** conditions are met:
1. **Low Uppercase Ratio**: `title_uppercase_ratio < 40%`
2. **Poor Match**: `similarity_score < 40%`

When triggered, the classifier returns:
- `short_code: "USE_PREVIOUS"`
- `use_previous_classification: true`
- `confidence: 0.0`
- Method: `low_quality_title_fallback`

### Rationale
If the title area contains mostly lowercase text and doesn't match any known templates well, it's likely:
- Page continuation text (e.g., "trang 2", "nội dung tiếp theo")
- Body text incorrectly detected as title
- OCR failure in the title region

In these cases, using the previous page's classification is more accurate than guessing based on poor data.

## Implementation

### Backend (`rule_classifier.py`)
- Added TIER 0 check before fuzzy matching
- Returns special `USE_PREVIOUS` code with flag
- Calculates uppercase ratio for title text

### Frontend (`DesktopScanner.js`)
- Modified `applySequentialNaming()` to check `use_previous_classification` flag
- Uses previous classification with 95% confidence (higher than normal fallback's 90%)
- Does not update `currentLastKnown` when using fallback
- Adds note: "Tiêu đề chất lượng thấp → Sử dụng phân loại trang trước"

## Examples

### Page 1: Good Title
```
Title: "HỢP ĐỒNG CHUYỂN NHƯỢNG"
Uppercase: 100%
Result: HDCQ (100% confidence)
Method: fuzzy_title_match
```

### Page 2: Low Quality Title
```
Title: "Trang tiếp"
Uppercase: 11%
Similarity: 29%
Result: USE_PREVIOUS → HDCQ (95% confidence)
Method: low_quality_title_fallback
Note: "Tiêu đề chất lượng thấp → Sử dụng phân loại trang trước"
```

## Benefits

1. **Improved Multi-Page Accuracy**: Pages 2+ of documents maintain correct classification even with poor OCR on continuation pages
2. **Confidence Preservation**: Previous classification confidence is maintained (95% vs dropping to unknown)
3. **Clear Indicators**: Frontend can show users when fallback was applied
4. **Administrative Standards**: Leverages the Vietnamese document convention of uppercase titles

## Edge Cases

- If first page has low quality title: No previous classification exists, will fall through to keyword matching
- If similarity is exactly 40% or above: Rule doesn't trigger (assumes some genuine match)
- New document starts (good title): Breaks the chain and starts fresh classification

## Testing Results

✅ Correctly identifies low quality titles (0-35% uppercase, <40% match)
✅ Uses previous classification with high confidence (95%)
✅ Doesn't break classification chain for continuation pages
✅ Allows new documents to start fresh classification
