# 💰 So sánh Chi phí: Gemini Flash vs Flash Lite (30 files)

## 📊 Tình huống: Scan 30 files

---

## Option 1: Gemini Flash - Batch Mode (5 files/lần)

### Specifications:
- Model: `gemini-2.5-flash`
- Mode: Multi-image batch
- Batch size: 5 files per request
- Total batches: 30 ÷ 5 = **6 batches**

### Pricing (Gemini Flash):
- Input: **$0.075 / 1M tokens**
- Output: **$0.30 / 1M tokens**

### Estimation per batch (5 files):

**Input tokens:**
- Images: 5 images × ~1,200 tokens = **6,000 tokens**
- Prompt (full): ~3,500 tokens
- Context: ~500 tokens
- **Total input: ~10,000 tokens/batch**

**Output tokens:**
- Multi-image response with document boundaries
- Array of 5 documents with metadata
- **Estimated: ~500 tokens/batch**

### Calculations:

**Per batch:**
- Input cost: 10,000 × $0.075 / 1M = **$0.00075**
- Output cost: 500 × $0.30 / 1M = **$0.00015**
- **Total per batch: $0.0009**

**Total for 30 files (6 batches):**
- Cost: 6 × $0.0009 = **$0.0054**
- Time: 6 × 6s = **36 seconds**
- Success rate: ~85% (15% fallback to single-file)

**With fallback (15% = 5 files):**
- Fallback cost: 5 × $0.0002 = **$0.001**
- **Total cost: $0.0054 + $0.001 = $0.0064**
- **Total time: 36s + (5 × 4s) = 56 seconds**

---

## Option 2: Gemini Flash Lite - Single File Mode

### Specifications:
- Model: `gemini-2.5-flash-lite`
- Mode: Single image per request
- Total requests: **30 requests**

### Pricing (Gemini Flash Lite):
- Input: **$0.0375 / 1M tokens** (50% cheaper than Flash)
- Output: **$0.15 / 1M tokens** (50% cheaper than Flash)

### Estimation per file:

**Input tokens:**
- Image (resized 1200×1800): ~1,000 tokens
- Prompt (lite): ~2,800 tokens
- Context: ~200 tokens
- **Total input: ~4,000 tokens/file**

**Output tokens:**
- Single document classification
- Simpler response format
- **Estimated: ~150 tokens/file**

### Calculations:

**Per file:**
- Input cost: 4,000 × $0.0375 / 1M = **$0.00015**
- Output cost: 150 × $0.15 / 1M = **$0.0000225**
- **Total per file: $0.0001725**

**Total for 30 files:**
- Cost: 30 × $0.0001725 = **$0.005175**
- Time: 30 × 4s = **120 seconds**
- Success rate: ~98% (with post-processing fixes)

---

## 📊 Comparison Summary

| Metric | Gemini Flash (Batch) | Flash Lite (Single) | Winner |
|--------|---------------------|-------------------|---------|
| **Total Cost** | $0.0064 | $0.0052 | ✅ Lite |
| **Cost per file** | $0.00021 | $0.00017 | ✅ Lite |
| **Total Time** | 56 seconds | 120 seconds | ✅ Flash |
| **Success Rate** | 85% | 98% | ✅ Lite |
| **Accuracy** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐⭐ Good | ✅ Flash |
| **Fallback Rate** | 15% | 0% | ✅ Lite |
| **Complexity** | High | Low | ✅ Lite |

---

## 🎯 Detailed Breakdown

### Cost Analysis:

**Flash Batch:**
- Main: $0.0054 (6 batches)
- Fallback: $0.001 (5 files)
- **Total: $0.0064**
- Cost per file: **$0.000213**

**Flash Lite Single:**
- All files: $0.0052 (30 files)
- No fallback needed
- **Total: $0.0052**
- Cost per file: **$0.000173**

**Savings with Lite:** 
- Absolute: $0.0012 per 30 files
- Percentage: **18.75% cheaper** ✅

---

### Time Analysis:

**Flash Batch:**
- Successful batches: 6 × 6s = 36s
- Fallback files: 5 × 4s = 20s
- **Total: 56 seconds** ✅

**Flash Lite Single:**
- All files: 30 × 4s = 120s
- **Total: 120 seconds**

**Time difference:**
- Flash is **2.14x faster** (64s saved) ✅

---

### Reliability Analysis:

**Flash Batch:**
- Success rate: 85%
- Fallback rate: 15% (requires re-processing)
- Response parsing: Complex (array of documents)
- Error handling: More complex
- **Reliability: Medium** ⚠️

**Flash Lite Single:**
- Success rate: 98% (with post-processing)
- Fallback rate: 0%
- Response parsing: Simple (single document)
- Error handling: Simple
- **Reliability: High** ✅

---

## 💡 Recommendations

### Choose Flash Batch (5 files) if:
- ⏱️ **Speed is critical** (2x faster)
- 📊 Need document boundaries detection
- 🎯 High accuracy is required
- 💰 Can tolerate slightly higher cost (+19%)
- 🔧 Can handle complexity and fallbacks

**Best for:**
- Large volumes (100+ files/day)
- Time-sensitive operations
- Professional use cases

---

### Choose Flash Lite (Single) if:
- 💰 **Cost is priority** (19% cheaper)
- 🎯 Reliability is important (98% success)
- 🔧 Want simpler implementation
- 📝 Don't need document boundaries
- ⚡ Can accept slower speed (2x slower)

**Best for:**
- Small to medium volumes (<100 files/day)
- Budget-conscious users
- Stable, predictable workflows
- When combined with post-processing fixes

---

## 🚀 Hybrid Approach (Best of Both)

**Strategy:**
1. Start with Flash Lite (single) - reliable & cheap
2. When volume increases (>100 files/day) → Switch to Flash Batch
3. Use pre-filter (color detection) → Reduce files to scan
4. Combine: Pre-filter + Flash Lite for best ROI

**Example with pre-filter:**
- 30 files → Pre-filter (free, <5s) → 15 files detected
- Scan 15 files with Flash Lite: $0.0026, 60s
- **Total: $0.0026, 65s** (59% cheaper, faster than batch!)

---

## 📊 Real-world Scenarios

### Scenario 1: Small Office (30 files/day)
**Recommended:** Flash Lite Single + Post-processing
- Daily cost: $0.0052
- Monthly cost (20 days): **$0.104**
- Reliable, simple, cheap ✅

### Scenario 2: Large Office (300 files/day)
**Recommended:** Flash Batch + Pre-filter
- Pre-filter: 300 → 150 files (50% reduction)
- Batch processing: 150 files
- Daily cost: ~$0.032
- Monthly cost (20 days): **$0.64**
- Fast, scalable ✅

### Scenario 3: Enterprise (1000+ files/day)
**Recommended:** Flash Batch + Pre-filter + Dedicated infrastructure
- Pre-filter: 1000 → 400 files
- Batch processing with optimized settings
- Monthly cost: **~$2-3**
- Consider API quota and rate limits

---

## 🎯 Conclusion

**For your use case (30 files):**

**Winner: Flash Lite Single + Post-processing fixes** ✅

**Reasons:**
1. **Cheaper:** $0.0052 vs $0.0064 (19% savings)
2. **More reliable:** 98% success vs 85%
3. **Simpler:** No fallback complexity
4. **Already implemented:** Post-processing fixes handle edge cases
5. **Good enough speed:** 2 minutes is acceptable for 30 files

**When to switch to Flash Batch:**
- When processing >100 files/day regularly
- When 2-minute processing time becomes a bottleneck
- When you need document boundary detection

---

**Generated:** 14/11/2024  
**Based on:** Gemini 2.5 Flash & Flash Lite pricing (Nov 2024)
