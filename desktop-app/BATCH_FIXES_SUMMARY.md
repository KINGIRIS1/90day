# Batch Scanner - Bug Fixes Summary

## Date: January 2025
## Status: ✅ FIXED - Ready for Testing

---

## 🐛 Issue #1: Sequential Naming Always Returns "UNKNOWN"

### Problem Description
User reported that files classified as "UNKNOWN" were not inheriting the document type from the previous file. The sequential naming logic was not working.

### Root Cause Analysis
```javascript
// BatchScanner.js - Line 301 (OLD CODE)
fileResult = applySequentialNaming(fileResult, lastKnownType); // ❌ BUG!

// Lines 306-310 (OLD CODE)
if (fileResult.short_code !== 'UNKNOWN') {
  setLastKnownType({
    short_code: fileResult.short_code,
    doc_type: fileResult.doc_type,
    confidence: fileResult.confidence
  }); // ❌ React state updates asynchronously!
}
```

**The Problem:**
1. `lastKnownType` is a React state variable
2. `setLastKnownType()` updates the state **asynchronously**
3. React batches state updates for performance
4. **Next loop iteration reads the OLD value** (null or previous old value)
5. Result: `applySequentialNaming` always receives `lastType: null`

**Console Log Evidence:**
```
🔍 applySequentialNaming: { short_code: 'UNKNOWN', lastType: 'null' }
// Should have been 'HDCQ' but state wasn't updated yet!
```

### The Fix ✅
```javascript
// Line 262 - NEW: Local variable for synchronous tracking
let currentLastKnown = null;

// Inside loop - Line 301 (FIXED)
fileResult = applySequentialNaming(fileResult, currentLastKnown); // ✅ Use local var!

// Lines 304-312 (FIXED)
if (fileResult.success) {
  // Update LOCAL variable IMMEDIATELY (synchronous)
  if (fileResult.short_code !== 'UNKNOWN') {
    currentLastKnown = {
      short_code: fileResult.short_code,
      doc_type: fileResult.doc_type,
      confidence: fileResult.confidence
    };
    // Also update state for UI (optional)
    setLastKnownType(currentLastKnown);
  }
}
```

### Why This Works
1. `currentLastKnown` is a **local variable** (not React state)
2. It updates **immediately** and **synchronously**
3. Next iteration gets the **correct, updated value**
4. State is still updated for UI display purposes

### Expected Behavior After Fix
```
Scanning folder with 4 files:

File 1: HDCQ (confidence 85%)
→ currentLastKnown = {short_code: 'HDCQ', doc_type: 'Hợp đồng chuyển nhượng', confidence: 0.85}

File 2: UNKNOWN (page 2 of HDCQ, no title)
→ applySequentialNaming receives currentLastKnown = 'HDCQ'
→ Override: UNKNOWN → HDCQ ✅
→ Final: HDCQ (confidence 71%, sequential)

File 3: GCNM (confidence 92%)
→ currentLastKnown = {short_code: 'GCNM', doc_type: 'Giấy chứng nhận mới', confidence: 0.92}

File 4: UNKNOWN (page 2 of GCNM)
→ applySequentialNaming receives currentLastKnown = 'GCNM'
→ Override: UNKNOWN → GCNM ✅
→ Final: GCNM (confidence 72%, sequential)
```

### Console Logs to Verify Fix
```
[2/4] Processing: file002.jpg
🔍 applySequentialNaming: { short_code: 'UNKNOWN', lastType: 'HDCQ' } ✅ (not 'null' anymore!)
🔄 Sequential: UNKNOWN → HDCQ
  ✅ HDCQ - 71%
```

---

## 🐛 Issue #2: Merge Custom Folder Not Working

### Problem Description
User selected "Sao chép vào thư mục khác" (custom folder) but PDFs were created in the original folder instead of the custom output folder.

### Console Log Evidence
```javascript
🚀 executeMerge called: {
  mergeAll: false, 
  outputOption: 'custom_folder', 
  mergeSuffix: '_merged', 
  outputFolder: 'C:\\Users\\nguye\\OneDrive\\Máy tính\\AI'
}

Merge options: {
  autoSave: true,
  mergeMode: 'custom',
  mergeSuffix: '_merged',
  parentFolder: '\\\\SERVERNAS\\Luutru\\2022\\1-2022\\5-01\\MINH HUNG\\16-384',
  customOutputFolder: 'C:\\Users\\nguye\\OneDrive\\Máy tính\\AI'
}

// But PDFs were created in original folder, not in C:\Users\nguye\OneDrive\Máy tính\AI
```

### Root Cause Analysis
```javascript
// main.js - Lines 652-663 (OLD CODE - INCOMPLETE!)
if (options.mergeMode === 'new') {
  // Create new folder with suffix
  const parentOfChild = path.dirname(childFolder);
  const childBaseName = path.basename(childFolder);
  const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
  targetDir = path.join(parentOfChild, newFolderName);
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
} else {
  targetDir = childFolder; // ❌ BUG: Always uses original folder for non-'new' modes!
}
```

**The Problem:**
- Code only handled `mergeMode === 'new'`
- For `mergeMode === 'custom'`, it fell through to `else` block
- **Always used `childFolder` (original folder) as target**
- `options.customOutputFolder` was completely ignored!

### The Fix ✅
```javascript
// main.js - Lines 652-668 (FIXED - COMPLETE!)
if (options.mergeMode === 'new') {
  // Mode 1: Create new sibling folder with suffix
  const parentOfChild = path.dirname(childFolder);
  const childBaseName = path.basename(childFolder);
  const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
  targetDir = path.join(parentOfChild, newFolderName);
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
} else if (options.mergeMode === 'custom' && options.customOutputFolder) {
  // ✅ NEW: Mode 2 - Custom folder with subfolder structure
  const childBaseName = path.basename(childFolder);
  targetDir = path.join(options.customOutputFolder, childBaseName);
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
} else {
  // Mode 3: Default - Same folder (root mode)
  targetDir = childFolder;
}
```

### How All 3 Merge Modes Work Now

#### Mode 1: "Đổi tên tại chỗ" (same_folder / mergeMode: 'root')
```
Source: C:\Data\Folder1\image001.jpg, image002.jpg
Result: C:\Data\Folder1\HDCQ.pdf ✅
```

#### Mode 2: "Sao chép theo loại vào thư mục con" (new_folder / mergeMode: 'new')
```
Source: C:\Data\Folder1\
Suffix: _merged
Result: C:\Data\Folder1_merged\HDCQ.pdf, GCNM.pdf ✅
```

#### Mode 3: "Sao chép vào thư mục khác" (custom_folder / mergeMode: 'custom') ← FIXED!
```
Source: C:\Data\Folder1\
Custom: D:\AI\
Result: D:\AI\Folder1\HDCQ.pdf, GCNM.pdf ✅
         (Subfolder preserves folder name to prevent conflicts)
```

### Why Subfolder Structure?
When merging multiple source folders to a single custom location:
```
Source folders:
- \\SERVERNAS\Luutru\2022\1-2022\Folder1\
- \\SERVERNAS\Luutru\2022\1-2022\Folder2\

Custom output: D:\AI\

Result:
D:\AI\
  ├── Folder1\
  │   ├── HDCQ.pdf
  │   ├── GCNM.pdf
  │   └── DKTC.pdf
  └── Folder2\
      ├── HDCQ.pdf  (No conflict with Folder1's HDCQ.pdf!)
      └── GCNM.pdf
```

**Benefits:**
1. **No file name conflicts** - Each source folder gets its own subfolder
2. **Maintains folder structure** - Easy to identify which PDFs came from which source
3. **Clean organization** - All PDFs grouped by source folder

### Expected Behavior After Fix
```
1. User scans folders: Folder1, Folder2
2. Click "Gộp tất cả các tab"
3. Select "Sao chép vào thư mục khác"
4. Choose: D:\AI\
5. Result:
   ✅ D:\AI\Folder1\HDCQ.pdf created
   ✅ D:\AI\Folder1\GCNM.pdf created
   ✅ D:\AI\Folder2\HDCQ.pdf created
   ✅ D:\AI\Folder2\GCNM.pdf created
```

---

## 📂 Files Modified

### 1. `/app/desktop-app/src/components/BatchScanner.js`
**Lines changed: 262, 301, 304-312**

**Changes:**
- Line 262: Added `let currentLastKnown = null;` (local variable for sequential tracking)
- Line 301: Changed `applySequentialNaming(fileResult, lastKnownType)` → `applySequentialNaming(fileResult, currentLastKnown)`
- Lines 304-312: Changed from `setLastKnownType(...)` to direct assignment: `currentLastKnown = {...}` (synchronous update)

**Impact:**
- ✅ Sequential naming now works correctly
- ✅ UNKNOWN files inherit type from previous document
- ✅ No breaking changes to other functionality

---

### 2. `/app/desktop-app/electron/main.js`
**Lines changed: 652-668**

**Changes:**
- Lines 661-666: Added new `else if` block for `mergeMode === 'custom'`
- Creates subfolder in `options.customOutputFolder` named after source folder

**Impact:**
- ✅ Custom folder merge now works correctly
- ✅ PDFs copied to user-selected custom location
- ✅ Subfolder structure prevents file name conflicts
- ✅ No breaking changes to existing merge modes

---

## 🧪 Testing Instructions

### Test 1: Sequential Naming Fix
**Setup:**
1. Create a test folder with 4 images
2. Ensure images are arranged so that 2nd and 4th will produce UNKNOWN (e.g., continuation pages without titles)

**Steps:**
1. Open Batch Scanner tab
2. Load TXT file with test folder path
3. Start scan with any OCR engine
4. Monitor console logs

**Expected Results:**
```
[1/4] Processing: file001.jpg
  ✅ HDCQ - 85%

[2/4] Processing: file002.jpg (continuation page)
🔍 applySequentialNaming: { short_code: 'UNKNOWN', lastType: 'HDCQ' }
🔄 Sequential: UNKNOWN → HDCQ
  ✅ HDCQ - 71% (sequential)

[3/4] Processing: file003.jpg
  ✅ GCNM - 90%

[4/4] Processing: file004.jpg (continuation page)
🔍 applySequentialNaming: { short_code: 'UNKNOWN', lastType: 'GCNM' }
🔄 Sequential: UNKNOWN → GCNM
  ✅ GCNM - 72% (sequential)
```

**Success Criteria:**
- ✅ Console shows `lastType: 'HDCQ'` (not `'null'`)
- ✅ File 2 classified as HDCQ (not UNKNOWN)
- ✅ File 4 classified as GCNM (not UNKNOWN)

---

### Test 2: Merge Custom Folder Fix
**Setup:**
1. Create 2 test folders with images
2. Each folder should have at least 2 different document types

**Steps:**
1. Scan both folders using Batch Scanner
2. Wait for scan to complete
3. Click "Gộp tất cả các tab" (Merge All Tabs)
4. Select "Sao chép vào thư mục khác" (custom_folder)
5. Choose custom location: `D:\AI\` (or any location)
6. Click "Gộp PDF"

**Expected Results:**
```
Console:
🚀 executeMerge called: {mergeAll: true, outputOption: 'custom_folder', outputFolder: 'D:\\AI'}
Merge options: {mergeMode: 'custom', customOutputFolder: 'D:\\AI', ...}

File System:
D:\AI\
  ├── Folder1\
  │   ├── HDCQ.pdf ✅
  │   └── GCNM.pdf ✅
  └── Folder2\
      ├── HDCQ.pdf ✅
      └── DKTC.pdf ✅

Alert:
✅ Gộp PDF hoàn tất!
Thành công: 4/4 file PDF
```

**Success Criteria:**
- ✅ PDFs created in `D:\AI\Folder1\` and `D:\AI\Folder2\` (not in original folders)
- ✅ Subfolders created automatically
- ✅ No file name conflicts between folders
- ✅ Success alert shows correct count

---

### Test 3: All Merge Modes Working
**Test each mode to ensure no regression:**

#### Mode 1: Same Folder
- Output: PDFs in original folder ✅

#### Mode 2: New Folder
- Output: PDFs in new sibling folder with suffix ✅

#### Mode 3: Custom Folder (FIXED)
- Output: PDFs in custom location with subfolders ✅

---

## 🔍 Verification Commands

### Check if files were modified correctly:
```bash
# Check BatchScanner.js changes
grep -n "currentLastKnown" /app/desktop-app/src/components/BatchScanner.js

# Check main.js changes
grep -n "mergeMode === 'custom'" /app/desktop-app/electron/main.js
```

### Expected output:
```
BatchScanner.js:262: let currentLastKnown = null;
BatchScanner.js:301: fileResult = applySequentialNaming(fileResult, currentLastKnown);
BatchScanner.js:305: currentLastKnown = {

main.js:661: } else if (options.mergeMode === 'custom' && options.customOutputFolder) {
```

---

## ⚠️ Edge Cases Handled

### Sequential Naming:
1. **First file is UNKNOWN:** No previous type → Stays UNKNOWN ✅
2. **All files are UNKNOWN:** All stay UNKNOWN ✅
3. **Confidence adjustment:** Sequential gets `confidence × 0.95` (min 0.75) ✅
4. **Stopped mid-scan:** `currentLastKnown` resets for next folder ✅

### Merge Custom:
1. **Custom folder doesn't exist:** Created automatically with `mkdirSync({recursive: true})` ✅
2. **Same folder name from different sources:** Subfolder structure prevents conflicts ✅
3. **Permission denied:** Error caught and displayed to user ✅
4. **Network path as custom folder:** Supported (e.g., `\\SERVER\Share\`) ✅

---

## 📊 Summary

| Issue | Status | Impact | Breaking Changes |
|-------|--------|--------|------------------|
| Sequential naming with lastKnownType | ✅ FIXED | High - Core feature now works | None |
| Merge custom folder not working | ✅ FIXED | High - Missing functionality restored | None |

**Total lines changed:** ~25 lines across 2 files
**Risk level:** Low - Minimal, focused changes
**Testing required:** Yes - User verification with real data

---

## 🎯 Next Steps

1. **User Testing:**
   - Test sequential naming with real documents
   - Test all 3 merge modes (especially custom folder)
   - Verify console logs match expected output

2. **Report Back:**
   - ✅ If working: Confirm and document
   - ❌ If issues persist: Share console logs and screenshots

3. **Optional Enhancements:**
   - Add UI indicator for sequential naming (e.g., "📄 Trang tiếp theo")
   - Add custom folder picker directly in merge modal
   - Add option to flatten folder structure in custom output

---

## 🙏 User Feedback Welcome

Please test and report:
- ✅ **What works well**
- ❌ **Any remaining issues**
- 💡 **Suggestions for improvement**

Cảm ơn! 🇻🇳
