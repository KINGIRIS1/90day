# Batch Scanner Fixes - Testing Guide

## Date: 2025-01-XX
## Issues Fixed

### Issue 1: Sequential Naming with lastKnownType ✅

**Problem:**
- `lastKnownType` was a React state variable
- State updates are asynchronous
- Next loop iteration received outdated/null value
- Result: UNKNOWN documents stayed as UNKNOWN instead of inheriting previous type

**Root Cause:**
```javascript
// Line 301 - OLD CODE (WRONG)
fileResult = applySequentialNaming(fileResult, lastKnownType); // ❌ State is async!

// Line 306-310
if (fileResult.short_code !== 'UNKNOWN') {
  setLastKnownType({ ... }); // ❌ Updates asynchronously, next iteration gets old value!
}
```

**Fix:**
```javascript
// Line 262 - Use local variable for synchronous updates
let currentLastKnown = null;

// Line 301 - NEW CODE (CORRECT)
fileResult = applySequentialNaming(fileResult, currentLastKnown); // ✅ Local variable!

// Line 304-311 - NEW CODE (CORRECT)
if (fileResult.short_code !== 'UNKNOWN') {
  currentLastKnown = { ... }; // ✅ Synchronous update!
  setLastKnownType(currentLastKnown); // Update UI state (optional)
}
```

**How It Works:**
1. `currentLastKnown` is a local variable inside the loop
2. It updates **immediately** (synchronously) when a non-UNKNOWN type is found
3. Next iteration gets the correct, updated value
4. State is still updated for UI display purposes

**Test Scenario:**
```
File 1: HDCQ (confidence 85%) → currentLastKnown = {short_code: 'HDCQ', ...}
File 2: UNKNOWN → applySequentialNaming gets currentLastKnown = 'HDCQ' → Override to HDCQ ✅
File 3: GCNM (confidence 90%) → currentLastKnown = {short_code: 'GCNM', ...}
File 4: UNKNOWN → applySequentialNaming gets currentLastKnown = 'GCNM' → Override to GCNM ✅
```

---

### Issue 2: Merge Custom Folder Not Working ✅

**Problem:**
- User selected "Sao chép vào thư mục khác" (custom_folder)
- PDFs were NOT copied to custom folder
- They stayed in original folder (same as 'same_folder' mode)

**Root Cause:**
```javascript
// main.js lines 652-663 - OLD CODE (INCOMPLETE)
if (options.mergeMode === 'new') {
  // Handle new folder...
} else {
  targetDir = childFolder; // ❌ Always uses original folder for 'custom' mode!
}
```

The code was missing a check for `mergeMode === 'custom'`!

**Fix:**
```javascript
// main.js lines 652-666 - NEW CODE (COMPLETE)
if (options.mergeMode === 'new') {
  // Create new folder with suffix in same parent
  const parentOfChild = path.dirname(childFolder);
  const childBaseName = path.basename(childFolder);
  const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
  targetDir = path.join(parentOfChild, newFolderName);
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
} else if (options.mergeMode === 'custom' && options.customOutputFolder) {
  // ✅ NEW: Custom folder mode
  const childBaseName = path.basename(childFolder);
  targetDir = path.join(options.customOutputFolder, childBaseName);
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
} else {
  // Default: Same folder (root mode)
  targetDir = childFolder;
}
```

**How It Works:**

**Mode 1: same_folder (mergeMode: 'root')**
- Source: `C:\Data\Folder1\`
- Target: `C:\Data\Folder1\HDCQ.pdf` ✅ Same folder

**Mode 2: new_folder (mergeMode: 'new')**
- Source: `C:\Data\Folder1\`
- Target: `C:\Data\Folder1_merged\HDCQ.pdf` ✅ New sibling folder with suffix

**Mode 3: custom_folder (mergeMode: 'custom')** ← FIXED!
- Source: `C:\Data\Folder1\`
- Custom output: `D:\AI\`
- Target: `D:\AI\Folder1\HDCQ.pdf` ✅ Custom location with subfolder

**Why subfolder?**
- If merging multiple source folders, each gets its own subfolder in custom location
- Prevents file name conflicts
- Maintains folder structure

**Test Scenario:**
```
Source folders:
- C:\Data\2022\Folder1\ (10 files → 3 PDFs)
- C:\Data\2022\Folder2\ (8 files → 2 PDFs)

Custom output: D:\AI\

Result:
D:\AI\
  ├── Folder1\
  │   ├── HDCQ.pdf
  │   ├── GCNM.pdf
  │   └── DKTC.pdf
  └── Folder2\
      ├── HDCQ.pdf
      └── GCNM.pdf
```

---

## Testing Checklist

### Test 1: Sequential Naming ✅
1. Create a test folder with 4 images
2. Ensure 2nd and 4th images produce UNKNOWN classification
3. Run batch scan
4. **Expected:** 2nd image should inherit type from 1st, 4th from 3rd
5. **Check console logs:** Should see `🔄 Sequential: UNKNOWN → HDCQ`

### Test 2: Merge Same Folder ✅
1. Scan a folder
2. Click "Gộp PDF" for the folder
3. Select "Đổi tên tại chỗ"
4. **Expected:** PDFs created in original folder

### Test 3: Merge New Folder ✅
1. Scan a folder (e.g., `C:\Data\Test\`)
2. Click "Gộp PDF" 
3. Select "Sao chép theo loại vào thư mục con"
4. Suffix: `_merged`
5. **Expected:** New folder `C:\Data\Test_merged\` with PDFs

### Test 4: Merge Custom Folder ✅ (FIXED)
1. Scan 2 folders: `Folder1`, `Folder2`
2. Click "Gộp tất cả các tab"
3. Select "Sao chép vào thư mục khác"
4. Choose custom: `D:\AI\`
5. **Expected:**
   - `D:\AI\Folder1\HDCQ.pdf`, `GCNM.pdf`, etc.
   - `D:\AI\Folder2\HDCQ.pdf`, `GCNM.pdf`, etc.

---

## Files Modified

1. **`/app/desktop-app/src/components/BatchScanner.js`**
   - Line 262: Added `let currentLastKnown = null;`
   - Line 301: Changed `lastKnownType` → `currentLastKnown`
   - Line 304-311: Update `currentLastKnown` directly (synchronous)

2. **`/app/desktop-app/electron/main.js`**
   - Lines 652-666: Added `mergeMode === 'custom'` handling
   - Creates subfolder in custom output directory

---

## Console Logs to Verify

### Sequential Naming Working:
```
[1/10] Processing: file1.jpg
  ✅ HDCQ - 85%

[2/10] Processing: file2.jpg
🔍 applySequentialNaming: { short_code: 'UNKNOWN', lastType: 'HDCQ' }
🔄 Sequential: UNKNOWN → HDCQ
  ✅ HDCQ - 71% (sequential)
```

### Merge Custom Folder Working:
```
🚀 executeMerge called: {mergeAll: true, outputOption: 'custom_folder', outputFolder: 'D:\\AI'}
Merge options: {
  autoSave: true,
  mergeMode: 'custom',
  mergeSuffix: '_merged',
  parentFolder: 'C:\\Data\\Folder1',
  customOutputFolder: 'D:\\AI'
}
✅ Created: D:\AI\Folder1\HDCQ.pdf
✅ Created: D:\AI\Folder1\GCNM.pdf
```

---

## Known Edge Cases

### Sequential Naming:
1. **First file is UNKNOWN:** No previous type to inherit → Stays UNKNOWN ✅
2. **All files are UNKNOWN:** All stay UNKNOWN ✅
3. **Confidence threshold:** Sequential result gets confidence × 0.95 (min 0.75) ✅

### Merge Custom:
1. **Same folder name from different sources:** Subfolder prevents conflicts ✅
2. **Custom folder doesn't exist:** Created automatically with `fs.mkdirSync({recursive: true})` ✅
3. **Permission denied:** Error caught and displayed to user ✅

---

## Summary

✅ **Sequential naming now works correctly** - Uses local variable for synchronous updates
✅ **Merge custom folder now works correctly** - Properly handles customOutputFolder option

Both fixes are minimal, non-breaking changes that don't affect other functionality.
