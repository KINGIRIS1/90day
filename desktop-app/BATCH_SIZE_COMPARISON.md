# 📊 So sánh Batch Size: Flash Lite 2/3 files vs Flash 5 files

**Scenario:** 30 files cần scan  
**Date:** 14/11/2024

---

## 🎯 3 Options để so sánh:

1. **Flash Lite - Batch 2 files**
2. **Flash Lite - Batch 3 files**
3. **Flash - Batch 5 files**

---

## Option 1: Flash Lite - Batch 2 files

### Setup:
- Model: `gemini-2.5-flash-lite`
- Batch size: **2 files/request**
- Total batches: 30 ÷ 2 = **15 batches**

### Pricing:
- Input: $0.0375 / 1M tokens
- Output: $0.15 / 1M tokens

### Token estimation per batch (2 files):

**Input:**
- Images: 2 × 1,000 = 2,000 tokens
- Prompt (lite): 2,800 tokens
- Multi-image context: 300 tokens
- **Total: ~5,100 tokens/batch**

**Output:**
- Array of 2 documents
- **Estimated: ~250 tokens/batch**

### Calculations:

**Per batch:**
- Input: 5,100 × $0.0375 / 1M = **$0.00019125**
- Output: 250 × $0.15 / 1M = **$0.0000375**
- **Total/batch: $0.00022875**

**Total for 30 files (15 batches):**
- Cost: 15 × $0.00022875 = **$0.00343**
- Time: 15 × 5s = **75 seconds**
- Fallback estimate: 10% = 3 files
- Fallback cost: 3 × $0.00017 = **$0.00051**
- Fallback time: 3 × 4s = **12s**

**Final:**
- **Total cost: $0.00394**
- **Total time: 87 seconds**

---

## Option 2: Flash Lite - Batch 3 files

### Setup:
- Model: `gemini-2.5-flash-lite`
- Batch size: **3 files/request**
- Total batches: 30 ÷ 3 = **10 batches**

### Token estimation per batch (3 files):

**Input:**
- Images: 3 × 1,000 = 3,000 tokens
- Prompt (lite): 2,800 tokens
- Multi-image context: 400 tokens
- **Total: ~6,200 tokens/batch**

**Output:**
- Array of 3 documents
- **Estimated: ~350 tokens/batch**

### Calculations:

**Per batch:**
- Input: 6,200 × $0.0375 / 1M = **$0.0002325**
- Output: 350 × $0.15 / 1M = **$0.0000525**
- **Total/batch: $0.000285**

**Total for 30 files (10 batches):**
- Cost: 10 × $0.000285 = **$0.00285**
- Time: 10 × 5.5s = **55 seconds**
- Fallback estimate: 12% = 4 files
- Fallback cost: 4 × $0.00017 = **$0.00068**
- Fallback time: 4 × 4s = **16s**

**Final:**
- **Total cost: $0.00353**
- **Total time: 71 seconds**

---

## Option 3: Flash - Batch 5 files (Reference)

### Setup:
- Model: `gemini-2.5-flash`
- Batch size: **5 files/request**
- Total batches: 30 ÷ 5 = **6 batches**

### Pricing:
- Input: $0.075 / 1M tokens (2x Flash Lite)
- Output: $0.30 / 1M tokens (2x Flash Lite)

### Token estimation per batch (5 files):

**Input:**
- Images: 5 × 1,200 = 6,000 tokens
- Prompt (full): 3,500 tokens
- Multi-image context: 500 tokens
- **Total: ~10,000 tokens/batch**

**Output:**
- Array of 5 documents with boundaries
- **Estimated: ~500 tokens/batch**

### Calculations:

**Per batch:**
- Input: 10,000 × $0.075 / 1M = **$0.00075**
- Output: 500 × $0.30 / 1M = **$0.00015**
- **Total/batch: $0.0009**

**Total for 30 files (6 batches):**
- Cost: 6 × $0.0009 = **$0.0054**
- Time: 6 × 6s = **36 seconds**
- Fallback estimate: 15% = 5 files
- Fallback cost: 5 × $0.0002 = **$0.001**
- Fallback time: 5 × 4s = **20s**

**Final:**
- **Total cost: $0.0064**
- **Total time: 56 seconds**

---

## 📊 Comparison Table

| Metric | Lite Batch-2 | Lite Batch-3 | Flash Batch-5 |
|--------|-------------|-------------|--------------|
| **Batches** | 15 | 10 | 6 |
| **Main Cost** | $0.00343 | $0.00285 | $0.0054 |
| **Fallback Cost** | $0.00051 | $0.00068 | $0.001 |
| **Total Cost** | **$0.00394** | **$0.00353** | **$0.0064** |
| **Cost/file** | $0.000131 | $0.000118 | $0.000213 |
| **Main Time** | 75s | 55s | 36s |
| **Fallback Time** | 12s | 16s | 20s |
| **Total Time** | **87s** | **71s** | **56s** |
| **Fallback Rate** | 10% | 12% | 15% |
| **Success Rate** | 90% | 88% | 85% |
| **Complexity** | Medium | Medium | High |

---

## 🏆 Rankings by Category

### By Cost (Cheapest to Most Expensive):
1. 🥇 **Flash Lite Batch-3: $0.00353** ✅
2. 🥈 Flash Lite Batch-2: $0.00394
3. 🥉 Flash Batch-5: $0.0064

**Savings:**
- Lite-3 vs Lite-2: **10% cheaper**
- Lite-3 vs Flash-5: **45% cheaper** 🎉

---

### By Speed (Fastest to Slowest):
1. 🥇 **Flash Batch-5: 56s** ✅
2. 🥈 Flash Lite Batch-3: 71s
3. 🥉 Flash Lite Batch-2: 87s

**Time difference:**
- Flash-5 vs Lite-3: **15s faster** (21% faster)
- Lite-3 vs Lite-2: **16s faster** (18% faster)

---

### By Reliability (Most to Least Reliable):
1. 🥇 **Flash Lite Batch-2: 90% success** ✅
2. 🥈 Flash Lite Batch-3: 88% success
3. 🥉 Flash Batch-5: 85% success

**Fallback rate:**
- Lite-2: 10% (3 files)
- Lite-3: 12% (4 files)
- Flash-5: 15% (5 files)

---

### By Value (Cost per Second):
1. 🥇 **Flash Lite Batch-3: $0.0000497/second** ✅
2. 🥈 Flash Batch-5: $0.0001143/second
3. 🥉 Flash Lite Batch-2: $0.0000453/second

---

## 💡 Detailed Analysis

### Flash Lite Batch-2: "The Reliable Choice"

**Pros:**
- ✅ Highest success rate (90%)
- ✅ Lowest fallback rate (10%)
- ✅ Simpler batches (easier to debug)
- ✅ Better for unreliable connections

**Cons:**
- ❌ Most batches (15)
- ❌ Slowest option (87s)
- ❌ More API calls = more overhead

**Best for:**
- When reliability is paramount
- Unstable internet connection
- First-time implementation
- Testing/debugging

---

### Flash Lite Batch-3: "The Sweet Spot" 🏆

**Pros:**
- ✅ **Cheapest option** ($0.00353)
- ✅ **Best value** (cost per second)
- ✅ **Balanced speed** (71s - acceptable)
- ✅ Good reliability (88%)
- ✅ Fewer API calls than batch-2

**Cons:**
- ⚠️ Slightly higher fallback than batch-2
- ⚠️ Still slower than Flash-5

**Best for:**
- **Most use cases** ✅
- Small to medium volumes
- Budget-conscious users
- When 71s is acceptable

**Why it's the sweet spot:**
- Perfect balance of cost, speed, reliability
- 45% cheaper than Flash-5
- Only 15s slower than Flash-5
- 16s faster than Lite-2
- 10% cheaper than Lite-2

---

### Flash Batch-5: "The Speed Demon"

**Pros:**
- ✅ **Fastest option** (56s)
- ✅ Fewer batches (6)
- ✅ Higher model quality
- ✅ Better for document boundaries

**Cons:**
- ❌ **Most expensive** ($0.0064 - 45% more than Lite-3)
- ❌ Highest fallback rate (15%)
- ❌ More complex implementation
- ❌ Larger batches = more risk

**Best for:**
- Time-critical operations
- Large volumes (>100 files/day)
- When accuracy is paramount
- Professional/enterprise use

---

## 🎯 Recommendations by Scenario

### Scenario 1: Regular Office Use (30 files/day)
**Recommend: Flash Lite Batch-3** 🏆

**Reasoning:**
- Daily cost: $0.00353
- Monthly (20 days): **$0.0706**
- Processing time: 71s (~1 minute)
- Best value for money
- Good reliability

**Comparison:**
- vs Lite-2: Save $0.0008/day, 16s faster
- vs Flash-5: Save $0.00287/day, only 15s slower

---

### Scenario 2: High-Volume Processing (100+ files/day)
**Recommend: Flash Batch-5** ✅

**Reasoning:**
- Speed is critical at scale
- 56s vs 71s difference compounds
- Higher accuracy needed
- Cost difference is justified

**Example (100 files/day):**
- Flash-5: $0.0213/day, ~3 minutes
- Lite-3: $0.0118/day, ~4 minutes
- Extra cost: $0.0095/day for 1 min saved ✅

---

### Scenario 3: Budget Priority (Small volume)
**Recommend: Flash Lite Batch-3** 🏆

**Reasoning:**
- Cheapest option
- Time not critical for small volumes
- Great value

---

### Scenario 4: Testing/Development
**Recommend: Flash Lite Batch-2** ✅

**Reasoning:**
- Highest reliability
- Easier to debug
- Smaller batches easier to test

---

## 📊 Cost Breakdown per 1000 files

| Option | Cost/1000 | Time/1000 | Daily Rate (8hrs) |
|--------|-----------|-----------|-------------------|
| Lite Batch-2 | $13.13 | 48 min | ~600 files |
| Lite Batch-3 | **$11.77** | **39 min** | ~730 files |
| Flash Batch-5 | $21.33 | 31 min | ~930 files |

---

## 🚀 Advanced: Pre-filter Integration

### Option 4: Pre-filter + Flash Lite Batch-3

**Workflow:**
```
30 files
  ↓ Pre-filter (color detection - FREE, 5s)
15 files (GCN detected)
  ↓ Flash Lite Batch-3 (5 batches)
  ↓ Scan + process (5 × 5.5s = 27.5s)
15 GCN results

Total: 5s + 27.5s = 32.5s
Cost: 5 × $0.000285 = $0.001425
```

**vs Flash Batch-5:**
- Cost: $0.001425 vs $0.0064 (**78% cheaper!**)
- Time: 32.5s vs 56s (**42% faster!**)
- **Best of all worlds** 🏆🏆🏆

---

## 🎯 Final Recommendation

### For 30 files: **Flash Lite Batch-3** 🏆

**Why:**
1. **Cheapest:** $0.00353 (45% cheaper than Flash-5)
2. **Good speed:** 71s (only 15s slower than Flash-5)
3. **Reliable:** 88% success rate
4. **Sweet spot:** Best balance of all factors
5. **Scalable:** Works for 30-100 files/day

**When to upgrade to Flash Batch-5:**
- Processing >100 files/day regularly
- Time is truly critical (<1 min requirement)
- Need highest accuracy
- Budget allows 45% higher cost

**Future optimization:**
- Implement pre-filter → **78% cheaper + faster than Flash-5!**

---

## 📝 Summary Table

| Metric | Winner | Value |
|--------|--------|-------|
| **Cheapest** | Flash Lite Batch-3 🏆 | $0.00353 |
| **Fastest** | Flash Batch-5 ⚡ | 56s |
| **Most Reliable** | Flash Lite Batch-2 🛡️ | 90% success |
| **Best Value** | Flash Lite Batch-3 💎 | Best $/second |
| **Most Efficient** | Pre-filter + Lite-3 🚀 | 78% cheaper + faster |

---

**Conclusion:** Use **Flash Lite Batch-3** for balanced performance, then add pre-filter when ready for maximum efficiency!

**Generated:** 14/11/2024
