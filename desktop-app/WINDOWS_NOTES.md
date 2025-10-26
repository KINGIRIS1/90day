# 🪟 Windows Setup Notes

## Encoding Fix Applied

✅ **Fixed:** UnicodeEncodeError trên Windows console

### Problem
Windows console mặc định dùng cp1252 encoding, không hỗ trợ Unicode tiếng Việt.

### Solution
Đã thêm encoding fix vào `rules_manager.py`:
```python
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## Windows Testing

### Test Commands

```powershell
# Test rules manager
cd desktop-app\python
python rules_manager.py get
python rules_manager.py folder

# Test với tiếng Việt
python rules_manager.py save TEST "{'keywords': ['giấy chứng nhận'], 'weight': 1.0, 'min_matches': 1}"
python rules_manager.py delete TEST
```

### Run Electron App

```powershell
cd desktop-app
yarn electron-dev
```

## Python Path on Windows

App tự động detect Python:
- **Dev mode:** Sử dụng `py` (Python Launcher for Windows)
- **Prod mode:** Bundled Python trong app package

Verify Python installation:
```powershell
py --version
# hoặc
python --version
```

## Tesseract on Windows

Download và cài đặt:
1. Tải từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Chọn **Vietnamese language pack** khi cài đặt
3. Thêm Tesseract vào PATH (installer hỏi)

Verify:
```powershell
tesseract --version
tesseract --list-langs | findstr vie
```

## Rules Location

Rules overrides được lưu tại:
```
C:\Users\<username>\.90daychonhanh\rules_overrides.json
```

Mở thư mục:
- Từ app: Click **📁 Mở Folder** trong tab Rules
- Hoặc chạy: `explorer %USERPROFILE%\.90daychonhanh`

## Common Issues

### Issue: `py is not recognized`

**Solution:**
1. Cài Python từ python.org
2. Chọn "Add Python to PATH" khi cài đặt
3. Hoặc dùng `python` thay vì `py`

### Issue: Tesseract not found

**Solution:**
1. Cài Tesseract (link ở trên)
2. Restart terminal sau khi cài
3. Verify với `tesseract --version`

### Issue: Permission denied khi save rules

**Solution:**
- Chạy app as Administrator
- Hoặc check quyền truy cập folder `%USERPROFILE%\.90daychonhanh`

## Performance Notes

- First scan có thể chậm (Tesseract loading models)
- Subsequent scans sẽ nhanh hơn
- Rules loading rất nhanh (~50ms)

## Build for Production (Windows)

```powershell
cd desktop-app
yarn build
yarn electron-build
```

Output: `dist\90dayChonThanh Setup 1.0.0.exe`

---

**Status:** ✅ Tested and working on Windows 10/11
