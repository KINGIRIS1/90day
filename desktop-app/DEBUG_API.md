# Debug API Issue - Step by Step

## 🔴 Problem
Files are correct but app still says: `api.analyzeBatchFile is not a function`

## 🎯 Root Cause
**Electron cached the OLD preload.js in memory!**

Even though you have the NEW files, Electron is still running with OLD code in memory.

## ✅ Solutions (Try in order)

### Solution 1: Force Clean Restart (RECOMMENDED)

```cmd
force-clean-restart.bat
```

This will:
- Kill ALL processes
- Delete ALL cache (project + AppData)
- Rebuild node_modules from scratch
- Start completely fresh

**Time:** 5 minutes

---

### Solution 2: Manual Kill + Clean

**Step 1: Kill processes**
```cmd
taskkill /F /IM electron.exe /T
taskkill /F /IM node.exe /T
```

**Step 2: Clean AppData cache**
```cmd
rmdir /S /Q "%APPDATA%\Electron"
rmdir /S /Q "%LOCALAPPDATA%\Electron"
```

**Step 3: Clean project cache**
```cmd
rmdir /S /Q node_modules\.cache
rmdir /S /Q build
```

**Step 4: Restart**
```cmd
yarn electron-dev-win
```

---

### Solution 3: Restart Computer (Nuclear option)

If nothing works:
1. Save all work
2. Restart Windows
3. Open terminal
4. `cd C:\desktop-app`
5. `yarn electron-dev-win`

This clears ALL memory cache.

---

## 🧪 Debug: Check if preload.js is loaded

### When app opens, press F12 → Console:

**Test 1: Check if electronAPI exists**
```javascript
console.log(window.electronAPI);
```

**Expected:** Object with many functions
**If undefined:** Preload.js not loaded at all!

**Test 2: Check specific API**
```javascript
console.log(window.electronAPI.analyzeBatchFile);
```

**Expected:** `function`
**If undefined:** Old preload.js is cached!

**Test 3: List all APIs**
```javascript
Object.keys(window.electronAPI);
```

**Expected:** Should include "analyzeBatchFile"
**If missing:** Definitely cached old version!

---

## 🔍 Verify preload.js is correct

**Open file:** `electron\preload.js`

**Search for (Ctrl+F):** `analyzeBatchFile`

**Should find (line ~52):**
```javascript
  analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),
```

**If found:** File is correct ✅
**If not found:** File is wrong ❌

---

## 🚨 Common Issues

### Issue 1: Multiple Electron processes
**Symptom:** Killing one doesn't work
**Solution:** 
```cmd
tasklist | findstr electron
# Kill all PIDs shown
taskkill /F /PID xxxx
```

### Issue 2: Process won't die
**Symptom:** "Access denied" or process keeps restarting
**Solution:** 
- Open Task Manager (Ctrl+Shift+Esc)
- Find "Electron" and "Node.js"
- Right-click → End Task
- Check "Background processes" tab too

### Issue 3: App starts but no UI
**Symptom:** App window opens but blank
**Solution:**
- F12 → Console → Check errors
- Likely port 3001 conflict
- Kill process on port 3001:
```cmd
netstat -ano | findstr :3001
taskkill /F /PID xxxx
```

### Issue 4: "Cannot find module"
**Symptom:** App crashes with module error
**Solution:**
```cmd
rmdir /S /Q node_modules
yarn install
```

---

## 🎯 Expected Flow

### Correct startup flow:
1. `yarn electron-dev-win` runs
2. React dev server starts on port 3001
3. Electron loads main.js
4. main.js loads preload.js (NEW version!)
5. preload.js exposes APIs to renderer
6. React app has access to `window.electronAPI.analyzeBatchFile`

### Where it breaks:
- Step 4: Electron loads OLD preload.js from cache
- Step 6: React app only sees OLD APIs

---

## ✅ Verification Checklist

After running `force-clean-restart.bat`:

- [ ] All Electron processes killed
- [ ] All Node processes killed
- [ ] AppData\Electron deleted
- [ ] LocalAppData\Electron deleted
- [ ] node_modules\.cache deleted
- [ ] build folder deleted
- [ ] node_modules rebuilt
- [ ] App starts successfully
- [ ] F12 → `window.electronAPI.analyzeBatchFile` → "function"
- [ ] Can click "Chọn file" without error

---

## 🔧 Alternative: Use Development Mode

If packaged app has cache issues, try dev mode:

**Option A: Direct node command**
```cmd
npm run start
# In separate terminal:
npm run electron-dev
```

**Option B: Clear cache flag**
```cmd
electron . --no-sandbox --disable-http-cache
```

---

## 📞 Still Not Working?

If after `force-clean-restart.bat` it still fails:

**Last resort options:**

1. **Reinstall Node.js**
   - Uninstall Node.js
   - Delete `C:\Program Files\nodejs`
   - Reinstall latest Node.js
   - `npm install -g yarn`
   - Try again

2. **Fresh folder**
   - Rename `C:\desktop-app` to `C:\desktop-app-old`
   - Copy again from server
   - `yarn install`
   - `yarn electron-dev-win`

3. **Different machine**
   - Test on another Windows computer
   - Verify if issue is machine-specific

---

**Bottom line: Run `force-clean-restart.bat` - it will fix 95% of cases!**
