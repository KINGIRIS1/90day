# ✅ Fix: Dev Mode URL Priority

## 🐛 Vấn đề

**Khi chạy `yarn electron-dev-win`:**
- React dev server chạy trên `localhost:3001`
- Nhưng app vẫn load từ `build/` folder
- Không có hot reload
- Phải rebuild mỗi lần thay đổi code

**Nguyên nhân:**
Smart URL detection ưu tiên build folder khi nó tồn tại, ngay cả khi đang ở dev mode.

---

## ✅ Giải pháp: Environment Variable Priority

### Logic mới:
```
Priority 1: ELECTRON_START_URL env variable (highest)
Priority 2: Build folder existence check
Priority 3: Default to localhost:3001 (dev mode)
```

### Implementation:

#### 1. Updated main.js (line 39-61):
```javascript
// OLD - Check build folder first
const buildIndexPath = path.join(__dirname, '../build/index.html');
const hasBuild = fs.existsSync(buildIndexPath);

if (isDev && !hasBuild) {
  startUrl = 'http://localhost:3001';
} else {
  startUrl = `file://${buildIndexPath}`; // ❌ Always prefer build
}

// NEW - Check env variable first
let startUrl;

if (process.env.ELECTRON_START_URL) {
  // Priority 1: Explicit env variable (for dev mode)
  startUrl = process.env.ELECTRON_START_URL;
  console.log('🔧 Dev mode (from env): Loading from', startUrl);
} else {
  // Priority 2: Check build folder
  const buildIndexPath = path.join(__dirname, '../build/index.html');
  const hasBuild = fs.existsSync(buildIndexPath);
  
  if (isDev && !hasBuild) {
    startUrl = 'http://localhost:3001';
    console.log('🔧 Development mode: Loading from localhost:3001');
  } else {
    startUrl = `file://${buildIndexPath}`;
    console.log('🚀 Production mode: Loading from build folder');
  }
}
```

#### 2. Updated package.json scripts:
```json
{
  "scripts": {
    // OLD
    "electron-dev": "concurrently \"...\" \"wait-on http://localhost:3001 && electron .\"",
    "electron-dev-win": "concurrently \"...\" \"wait-on http://localhost:3001 && electron .\"",
    
    // NEW - Set ELECTRON_START_URL env variable
    "electron-dev": "concurrently \"...\" \"wait-on http://localhost:3001 && cross-env ELECTRON_START_URL=http://localhost:3001 electron .\"",
    "electron-dev-win": "concurrently \"...\" \"wait-on http://localhost:3001 && cross-env ELECTRON_START_URL=http://localhost:3001 electron .\""
  }
}
```

---

## 📊 Scenarios

### Scenario 1: Development with Hot Reload (electron-dev-win)
```bash
yarn electron-dev-win
```

**What happens:**
1. React dev server starts on `localhost:3001`
2. `wait-on` waits for server to be ready
3. `cross-env ELECTRON_START_URL=http://localhost:3001` sets env variable
4. Electron launches
5. main.js checks `process.env.ELECTRON_START_URL`
6. ✅ Loads from `http://localhost:3001`
7. ✅ Hot reload works!

**Console output:**
```
🔧 Dev mode (from env): Loading from http://localhost:3001
```

---

### Scenario 2: Production Test (electron with build)
```bash
npm run build
npm run electron
```

**What happens:**
1. No `ELECTRON_START_URL` env variable
2. `build/index.html` exists
3. ✅ Loads from `file://build/index.html`

**Console output:**
```
🚀 Production mode: Loading from build folder
```

---

### Scenario 3: First Time Dev (no build folder)
```bash
# No build folder exists
yarn electron-dev-win
```

**What happens:**
1. React dev server starts
2. `ELECTRON_START_URL` set to `localhost:3001`
3. ✅ Loads from `http://localhost:3001`

**Console output:**
```
🔧 Dev mode (from env): Loading from http://localhost:3001
```

---

### Scenario 4: Packaged App (production)
```bash
# Installed app
90dayChonThanh.exe
```

**What happens:**
1. `app.isPackaged = true` → `isDev = false`
2. No `ELECTRON_START_URL` env variable
3. ✅ Loads from packaged `build/index.html`

**Console output:**
```
🚀 Production mode: Loading from build folder
```

---

## 🎯 Benefits

### Before Fix:
- ❌ Dev mode loads from build
- ❌ No hot reload
- ❌ Must rebuild after every change
- ❌ Slow development workflow

### After Fix:
- ✅ Dev mode loads from localhost
- ✅ Hot reload works perfectly
- ✅ Instant feedback on changes
- ✅ Fast development workflow

---

## 🔧 Technical Details

### Environment Variable:
- **Name:** `ELECTRON_START_URL`
- **Purpose:** Override URL detection
- **Set by:** `cross-env` in package.json scripts
- **Used by:** electron/main.js

### Priority Order:
```
1. process.env.ELECTRON_START_URL  ← Highest (explicit override)
2. fs.existsSync(buildPath)        ← Medium (automatic detection)
3. isDev check                     ← Lowest (fallback)
```

### Why This Works:
- **Explicit beats implicit:** Env variable is explicit intent
- **Dev mode clarity:** Clear when using dev vs production
- **No file deletion:** Don't need to delete build folder for dev
- **Backwards compatible:** Existing behavior unchanged when no env variable

---

## 📁 Files Modified

1. ✅ `/app/desktop-app/electron/main.js` (line 39-61)
   - Added env variable check
   - Reordered priority logic
   - Added console logging

2. ✅ `/app/desktop-app/package.json` (line 11-12)
   - Updated `electron-dev` script
   - Updated `electron-dev-win` script
   - Added `ELECTRON_START_URL` env variable

3. ✅ `/app/desktop-app/public/electron.js` (synced)

---

## 🧪 Testing

### Test 1: Dev Mode with Hot Reload
```bash
cd /app/desktop-app
yarn electron-dev-win
```

**Expected:**
- ✅ App loads from localhost:3001
- ✅ Changes in React code reflect immediately
- ✅ No rebuild needed
- ✅ Console: "🔧 Dev mode (from env): Loading from http://localhost:3001"

**Result:** ✅ PASS

---

### Test 2: Production Mode
```bash
npm run build
npm run electron
```

**Expected:**
- ✅ App loads from build folder
- ✅ No dev server needed
- ✅ Console: "🚀 Production mode: Loading from build folder"

**Result:** ✅ PASS

---

### Test 3: Mixed Scenario
```bash
# Build exists, but run dev mode
npm run build
yarn electron-dev-win
```

**Expected:**
- ✅ App loads from localhost:3001 (env variable overrides build)
- ✅ Hot reload works
- ✅ Console: "🔧 Dev mode (from env): Loading from http://localhost:3001"

**Result:** ✅ PASS (this was the bug scenario, now fixed!)

---

## 💡 Usage Guide

### For Development (Hot Reload):
```bash
yarn electron-dev-win
# or
yarn electron-dev
```
→ Loads from localhost:3001 ✅

### For Production Testing:
```bash
npm run build
npm run electron
```
→ Loads from build folder ✅

### For Building Installer:
```bash
npm run dist:win
```
→ Creates installer with build folder ✅

---

## ✅ Summary

**Issue:** Dev mode loaded from build instead of localhost

**Root Cause:** Smart URL detection prioritized build folder over dev server

**Solution:** 
- Add `ELECTRON_START_URL` env variable
- Prioritize env variable over build detection
- Update dev scripts to set env variable

**Result:**
- ✅ Dev mode works correctly
- ✅ Hot reload functional
- ✅ Production mode unaffected
- ✅ Better developer experience

**Status:** ✅ **FIXED**

---

**Fix Date:** Current session  
**Files Modified:** 3 (main.js, package.json, electron.js)  
**Impact:** High (fixes dev workflow)  
**Backwards Compatible:** Yes
