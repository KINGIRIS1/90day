# 🚀 Quick Test Guide - Rules Manager

## Đã sửa lỗi

✅ **Fixed:** `getPythonPath is not defined` error
- Đã thêm helper function `getPythonPath()` vào `electron/main.js`

✅ **Fixed:** `UnicodeEncodeError` on Windows
- Đã thêm UTF-8 encoding fix cho Windows console trong `rules_manager.py`
- Hỗ trợ đầy đủ tiếng Việt có dấu trên Windows

> **Note for Windows users:** Xem thêm `WINDOWS_NOTES.md` để biết chi tiết về setup và troubleshooting

## Test Python Backend (✅ All Passed)

```bash
cd /app/desktop-app
./test-rules-manager.sh
```

Kết quả: **7/7 tests passed** ✅

## Test Electron App

### Bước 1: Start app

```bash
cd /app/desktop-app
yarn electron-dev
```

### Bước 2: Test Rules Manager UI

1. **Mở tab Rules:**
   - Click vào tab **📋 Rules** trên thanh menu

2. **Test Get Rules:**
   - Kiểm tra xem có hiển thị 95-98 rules không
   - Thử search một rule (ví dụ: "GCNM")

3. **Test View Rule:**
   - Click vào bất kỳ rule nào (ví dụ: GCNM)
   - Xem chi tiết: weight, min_matches, keywords

4. **Test Edit Rule:**
   - Click nút **✏️ Sửa**
   - Thay đổi weight (ví dụ: 1.5 → 1.6)
   - Thêm keyword mới: "sổ đỏ"
   - Click **💾 Lưu**
   - Verify: Reload lại rules để xem thay đổi

5. **Test Delete Rule:**
   - Chọn rule vừa edit
   - Click **🗑️ Xóa**
   - Confirm trong dialog
   - Verify: Rule quay về mặc định

6. **Test Export:**
   - Click **📤 Export JSON**
   - Chọn nơi lưu file
   - Verify: Mở file JSON để xem nội dung

7. **Test Import:**
   - Click **📥 Import (Merge)**
   - Chọn file JSON vừa export
   - Verify: Rules được load lại

8. **Test Reset:**
   - Click **🔄 Reset Tất Cả**
   - Confirm trong dialog
   - Verify: Tất cả rules về mặc định

9. **Test Open Folder:**
   - Click **📁 Mở Folder**
   - Verify: File explorer mở thư mục `~/.90daychonhanh/`

## Expected Results

- ✅ Tab Rules hiển thị đúng
- ✅ Có thể view/edit/delete rules
- ✅ Export/Import hoạt động
- ✅ Reset về default thành công
- ✅ Open folder mở đúng đường dẫn
- ✅ Notifications hiển thị sau mỗi action

## Files Location

**Rules overrides file:**
- Linux/Mac: `~/.90daychonhanh/rules_overrides.json`
- Windows: `C:\Users\<username>\.90daychonhanh\rules_overrides.json`

## Troubleshooting

**Nếu tab Rules không hiển thị:**
1. Check console (F12) xem có lỗi React không
2. Verify `RulesManager.js` đã được import trong `App.js`

**Nếu Python errors:**
1. Check Python path: `which python3` (Linux/Mac) hoặc `where py` (Windows)
2. Test script: `python3 rules_manager.py get`

**Nếu IPC errors:**
1. Check `electron/main.js` có function `getPythonPath()`
2. Check `electron/preload.js` expose đủ APIs

## Integration Test với OCR

Sau khi chỉnh sửa rules:

1. Edit rule GCNM, thêm keyword "sổ đỏ"
2. Save
3. Chuyển sang tab Scanner
4. Scan một ảnh GCNM có chữ "sổ đỏ"
5. Verify: Confidence tăng lên so với trước

## Success Criteria

✅ Backend tests: 7/7 passed
✅ UI loads without errors
✅ Can edit and save rules
✅ Rules persist after app restart
✅ OCR uses updated rules

---

**Status:** Ready for testing ✅
**Last Updated:** 2025-01-15
