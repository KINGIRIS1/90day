# 📦 Installers Folder

This folder contains the dependency installers needed for the all-in-one build.

## 📥 Required Downloads

### 1. Python Installer (Required)

**File:** `python-3.11.8-amd64.exe`  
**Size:** ~30 MB  
**Download:** https://www.python.org/downloads/windows/

Direct link: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe

**After download:**
- Place in this folder: `installers/python-3.11.8-amd64.exe`

---

### 2. Tesseract OCR Installer (Required)

**File:** `tesseract-ocr-w64-setup-5.3.3.exe`  
**Size:** ~50 MB  
**Download:** https://github.com/UB-Mannheim/tesseract/wiki

Direct link: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

**After download:**
- Rename to: `tesseract-ocr-w64-setup-5.3.3.exe`
- Place in this folder: `installers/tesseract-ocr-w64-setup-5.3.3.exe`

---

## ✅ Checklist

Before running `build-allinone.bat`, ensure:

- [ ] `installers/python-3.11.8-amd64.exe` exists (~30MB)
- [ ] `installers/tesseract-ocr-w64-setup-5.3.3.exe` exists (~50MB)
- [ ] NSIS installed on your system
- [ ] Node.js and Yarn installed

---

## 📁 Expected Structure

```
desktop-app/
├── installers/                              ← This folder
│   ├── README.md                           ← This file
│   ├── python-3.11.8-amd64.exe            ← Download this
│   └── tesseract-ocr-w64-setup-5.3.3.exe  ← Download this
├── installer.nsi                           ← NSIS script
└── build-allinone.bat                      ← Build script
```

---

## 🚀 Build Process

Once both files are downloaded:

```batch
cd desktop-app
build-allinone.bat
```

The script will:
1. ✅ Check NSIS installation
2. ✅ Verify Python installer exists
3. ✅ Verify Tesseract installer exists
4. ✅ Build Electron app
5. ✅ Create all-in-one installer

**Output:** `90dayChonThanh-AllInOne-Setup.exe` (~235MB)

---

## 🔍 Troubleshooting

### File not found error

**Problem:** Build script says installer not found

**Solution:**
1. Check files are in correct location
2. Check exact file names match
3. Re-download if file is corrupted

### Wrong version

**Problem:** You have different Python/Tesseract version

**Solution:**
1. Update `installer.nsi` with new filenames
2. Or download the exact versions listed above

---

## 📝 Alternative Versions

If you want to use different versions:

### Different Python version

Update in `installer.nsi`:
```nsis
File "installers\python-3.X.X-amd64.exe"
ExecWait '"$TEMP\python-3.X.X-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1'
```

### Different Tesseract version

Update in `installer.nsi`:
```nsis
File "installers\tesseract-ocr-w64-setup-X.X.X.exe"
ExecWait '"$TEMP\tesseract-ocr-w64-setup-X.X.X.exe" /S /L vie'
```

---

## ⚠️ Important Notes

1. **File size:** Installers total ~80MB, final output ~235MB
2. **Antivirus:** Some AVs may flag installers - normal for bundled installers
3. **Admin rights:** Installation requires admin privileges
4. **Internet:** Not required for installation once downloaded
5. **Clean machine:** Test on VM without Python/Tesseract installed

---

## 🎯 What Gets Installed

When users run the all-in-one installer:

1. **Python 3.11**
   - Silent install
   - Added to PATH
   - pip included

2. **Tesseract OCR 5.3.3**
   - Silent install
   - Vietnamese language pack
   - Added to PATH

3. **Python packages**
   - pytesseract
   - Pillow

4. **90dayChonThanh App**
   - Desktop shortcut
   - Start menu entry
   - Uninstaller

**Total install time:** 5-10 minutes

---

## 💡 Tips

- Download both files before starting build
- Verify file sizes to ensure complete downloads
- Keep installers for future builds
- Test final installer on clean Windows VM
- Use Windows Defender exclusions if needed during build

---

**For more details, see:** `BUILD_ALLINONE.md` in parent folder
