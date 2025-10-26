# 📦 90dayChonThanh Desktop App - Distribution Package

## 🎯 Package Overview

This package contains the **all-in-one installer** for 90dayChonThanh Desktop App with automatic installation of all dependencies.

---

## 📥 What's Included

### Main File

**`90dayChonThanh-AllInOne-Setup.exe`** (~235 MB)

This single installer automatically installs:
- ✅ Python 3.11 (with pip)
- ✅ Tesseract OCR 5.3.3 (Vietnamese language pack)
- ✅ Python packages (pytesseract, Pillow)
- ✅ 90dayChonThanh Desktop Application

---

## 🚀 Installation Instructions

### For Users (Simple)

1. **Download** the installer file
2. **Double-click** `90dayChonThanh-AllInOne-Setup.exe`
3. **Click "Yes"** when Windows asks for permission
4. **Follow** the installation wizard:
   - Welcome → Next
   - License → I Agree
   - Install Location → Next (or choose custom)
   - Wait 5-10 minutes for installation
   - Finish
5. **Launch** the app from Desktop shortcut or Start Menu

**That's it!** All dependencies are installed automatically.

---

## ⚙️ System Requirements

### Minimum Requirements

- **OS:** Windows 10 (64-bit) or Windows 11
- **RAM:** 4 GB
- **Disk Space:** 1 GB free space
- **Internet:** Not required for installation (only for download)

### Recommended

- **OS:** Windows 11
- **RAM:** 8 GB
- **Disk Space:** 2 GB free space
- **Internet:** For Cloud Boost feature (optional)

---

## 📖 Quick Start Guide

### After Installation

1. **Open the app** from Desktop icon
2. **Click** "Scan Documents" tab
3. **Select** image file (JPG, PNG, PDF)
4. **Click** "Process Offline" (free, no internet needed)
5. **View** results:
   - Document type detected
   - Suggested filename
   - Confidence score
6. **Save** the result

### Features

#### 🔵 Offline Mode (Free)
- Process documents on your computer
- No internet required
- 85-88% accuracy
- Privacy: data stays on your computer

#### ☁️ Cloud Boost (Optional)
- Higher accuracy: 93%+
- Uses GPT-4 Vision
- Requires internet & API key
- Small fee per document

---

## 🔧 Configuration (Optional)

### Cloud Boost Setup

If you want to use Cloud Boost feature:

1. Go to **Settings** tab
2. Enter your **OpenAI API Key**
   - Get key from: https://platform.openai.com/api-keys
3. Click **Save Settings**

### Output Settings

- **Save Directory:** Choose where to save scanned documents
- **Naming Format:** Customize filename format
- **Auto-numbering:** Enable sequential numbering

---

## 🛠️ Troubleshooting

### Installation Issues

**Problem:** "Windows protected your PC" warning

**Solution:**
- Click "More info"
- Click "Run anyway"
- This is normal for non-Microsoft-signed installers

---

**Problem:** Installation takes too long (>15 minutes)

**Solution:**
- Check disk space (need 1GB+)
- Disable antivirus temporarily
- Close other programs
- Restart computer and try again

---

**Problem:** "Installation failed" error

**Solution:**
1. Right-click installer
2. Select "Run as administrator"
3. Try again

---

### App Issues

**Problem:** App won't open after installation

**Solution:**
- Restart your computer
- Check if Python and Tesseract installed:
  - Open Command Prompt
  - Type: `python --version`
  - Type: `tesseract --version`
- If not found, reinstall the app

---

**Problem:** OCR not working / no results

**Solution:**
- Check image file format (JPG, PNG supported)
- Ensure image quality is good (not too blurry)
- Try with a different image
- Check Tesseract installation: `tesseract --version`

---

**Problem:** "Python not found" error

**Solution:**
- Restart computer (PATH needs to refresh)
- Or logout and login again
- If still not working, reinstall app

---

## 📊 Performance Tips

### For Best Results

1. **Use high-quality images:**
   - Resolution: 300 DPI or higher
   - Format: JPG or PNG (not heavily compressed)
   - Color: Black & white or good color scan

2. **Ensure proper scanning:**
   - Document is straight (not rotated)
   - Full content visible
   - Good lighting (not too dark)
   - Clear text (not blurry)

3. **Batch processing:**
   - Select folder instead of single file
   - App will process all images automatically
   - Great for large volumes

---

## 🗑️ Uninstallation

### To Remove the App

**Method 1: Windows Settings**
1. Open **Settings** → **Apps**
2. Find **90dayChonThanh**
3. Click **Uninstall**

**Method 2: Control Panel**
1. Open **Control Panel**
2. Go to **Programs** → **Uninstall a program**
3. Select **90dayChonThanh**
4. Click **Uninstall**

### About Python and Tesseract

During uninstall, you'll be asked:
- "Do you want to remove Python and Tesseract?"

**Choose "No" if:**
- You use Python or Tesseract for other purposes
- You're not sure

**Choose "Yes" if:**
- You only installed them for this app
- You want to completely remove everything

---

## 📞 Support

### Need Help?

**Email:** support@90daychonthanh.com

**Website:** https://90daychonthanh.com

**When reporting issues, please provide:**
1. Windows version (Windows 10/11)
2. Screenshot of error (if any)
3. What you were trying to do
4. Sample image file (if related to OCR)

---

## 🔄 Updates

### Checking for Updates

Currently, updates need to be installed manually:
1. Download new installer
2. Run new installer (will upgrade existing installation)
3. Your settings and rules are preserved

### Version History

**v1.0.0** (Current)
- Initial release
- Tesseract OCR offline mode
- Cloud Boost with GPT-4 Vision
- Batch processing
- Rules Manager
- PDF export
- Auto keyword variants

---

## 📜 License

**MIT License**

Copyright (c) 2024 90dayChonThanh

This software is provided free of charge for personal and commercial use.

---

## 🎉 Thank You!

Thank you for using 90dayChonThanh Desktop App!

We hope this tool helps you process your land documents efficiently.

For questions, feedback, or feature requests, please contact us.

---

**Installation Package:**
- File: `90dayChonThanh-AllInOne-Setup.exe`
- Version: 1.0.0
- Size: ~235 MB
- Date: 2024
- Checksum: (will be added after build)

---

**Happy Scanning! 🚀**
