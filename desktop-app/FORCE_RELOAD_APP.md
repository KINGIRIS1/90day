# FORCE RELOAD APP - Clear Electron Cache

## Vấn Đề
Merge custom folder không hoạt động sau nhiều lần fix. Logs từ main.js KHÔNG xuất hiện.

**Có thể do:** Electron cache outdated code!

---

## ✅ Giải Pháp: Force Reload

### Option 1: Hard Reload (RECOMMENDED)

**Steps:**
1. **Đóng app hoàn toàn** (không chỉ minimize!)
2. **Open Terminal/Command Prompt**
3. **Run:**
   ```bash
   cd /path/to/desktop-app
   npm start
   ```
   
   Hoặc (Windows):
   ```cmd
   cd C:\path\to\desktop-app
   npm start
   ```

4. **App sẽ start fresh** → Code mới được load

**Verify:**
- Press `Ctrl + Shift + I` (DevTools)
- Try merge → Should see logs từ main.js

---

### Option 2: Clear Electron Cache Manually

**Windows:**
```powershell
# Close app first!

# Clear Electron cache
Remove-Item -Path "$env:APPDATA\[YourAppName]\*" -Recurse -Force

# Or clear all Electron caches
Remove-Item -Path "$env:APPDATA\Electron\*" -Recurse -Force
```

**Then restart app**

---

### Option 3: Reload trong DevTools

**Steps:**
1. Mở app
2. Press `Ctrl + Shift + I` (DevTools)
3. Right-click on reload button (⟳)
4. Select "**Empty Cache and Hard Reload**"
5. App sẽ reload với cache cleared

**Note:** Chỉ clear renderer cache, không clear main process!

---

## 🧪 Verify Logs

**Sau khi reload, try merge:**

**Expected logs (Main Console):**
```
📡 PRELOAD.JS: mergeByShortCode called  ← NEW!
   Items: 15
   Options: {mergeMode: 'custom', ...}

================================================================================
🚀 MERGE HANDLER CALLED IN MAIN.JS  ← MUST SEE THIS!
📦 Items count: 15
⚙️ Options: {...}
================================================================================
```

**Nếu vẫn không thấy logs:**
→ Có vấn đề khác (không phải cache)
→ Cần debug IPC chain

---

## 🔍 Alternative: Check Logs Location

**Logs có thể ở:**

**1. Terminal nơi run app:**
```bash
npm start
# Logs từ main.js sẽ xuất hiện ở đây
```

**2. Electron DevTools:**
- Press `Ctrl + Shift + I`
- Console tab
- Select "Electron" từ dropdown (không phải "top")

**3. Windows Event Viewer:**
- Nếu app crash mà không log
- Windows Key + X → Event Viewer
- Application logs

---

## 📋 Full Debug Checklist

### Step 1: Close App Completely
- [x] Close app window
- [x] Check Task Manager → No Electron process
- [x] Kill if needed: `taskkill /F /IM electron.exe`

### Step 2: Clear Cache
- [x] Delete `%APPDATA%\[AppName]`
- [x] Or run `npm start` fresh

### Step 3: Open DevTools FIRST
- [x] Start app
- [x] Immediately press `Ctrl + Shift + I`
- [x] Keep DevTools open

### Step 4: Test Merge
- [x] Scan 1 small folder (5 files)
- [x] Merge → Custom → `C:\Temp\` (simple path!)
- [x] Watch console carefully

### Step 5: Verify Logs
```
Expected:
✅ 📡 PRELOAD.JS: mergeByShortCode called
✅ 🚀 MERGE HANDLER CALLED IN MAIN.JS
✅ 📁 Creating custom folder: C:\Temp\...
✅ ✅ PDF written successfully

If missing any:
❌ Check which step fails
❌ Copy full console logs
❌ Share with developer
```

---

## 💡 Pro Tip: Watch Main Process Logs

**Best way to see main.js logs:**

```bash
# Run app from terminal (not from installed app)
cd /path/to/desktop-app
npm start

# All main.js console.log will appear here!
```

**Benefits:**
- See all logs in real-time
- No need to find DevTools dropdown
- Easier to copy/paste logs

---

## 🚨 If Still Not Working

**After force reload, if merge still fails:**

1. **Share FULL console output** (từ terminal `npm start`)
2. **Include:**
   - All logs từ "🚀 executeMerge" (renderer)
   - All logs từ "🚀 MERGE HANDLER" (main)
   - Any error messages
3. **Test info:**
   - App run method: npm start? Installed app?
   - Folder path: Local (C:\) hay network (\\SERVER\)?
   - Custom output: Exists? Writable?

---

## 📦 Quick Command Summary

```bash
# Windows
cd C:\path\to\desktop-app
npm start

# Linux/Mac
cd /path/to/desktop-app
npm start

# In app:
# Ctrl + Shift + I (DevTools)
# Ctrl + R (Reload)
# Ctrl + Shift + R (Hard reload)
```

---

Cảm ơn! 🇻🇳
