# ⌨️ Test Keyboard Shortcuts - InlineShortCodeEditor

## Mục đích
Kiểm tra xem keyboard shortcuts (Enter, Esc) có hoạt động trong BatchScanner không.

## Điều kiện tiên quyết
1. ✅ Build app mới nhất: `npm run build`
2. ✅ Reload app / Restart app
3. ✅ Import đã có: `import InlineShortCodeEditor from './InlineShortCodeEditor';`

## Test Steps - BatchScanner

### Test 1: Enter để lưu (không dùng dropdown)
1. Mở BatchScanner
2. Quét/Resume một folder
3. Click edit mã của 1 file
4. Gõ "PCT" (không chọn từ dropdown)
5. **Bấm Enter**
6. ✅ Expected: Lưu thành công, input đóng
7. ❌ Nếu không: Input vẫn mở, không lưu

### Test 2: Enter chọn gợi ý
1. Click edit mã
2. Gõ "gc" → Dropdown xuất hiện
3. Bấm ↓ để chọn GCNC
4. **Bấm Enter**
5. ✅ Expected: Chọn GCNC, input còn mở
6. **Bấm Enter lần nữa**
7. ✅ Expected: Lưu GCNC, input đóng

### Test 3: Esc để hủy
1. Click edit mã
2. Gõ "ABC"
3. **Bấm Esc**
4. ✅ Expected (nếu dropdown mở): Đóng dropdown
5. **Bấm Esc lần nữa**
6. ✅ Expected: Hủy edit, quay về giá trị cũ

### Test 4: Ctrl+Enter force save
1. Click edit mã
2. Gõ "gc" → Dropdown xuất hiện
3. **Bấm Ctrl+Enter**
4. ✅ Expected: Lưu "gc" ngay (không chọn gợi ý)

## Troubleshooting

### Nếu keyboard không hoạt động:

#### Check 1: Component có render không?
```javascript
// Kiểm tra trong browser console
// Mở DevTools → Elements → Search for "InlineShortCodeEditor"
```

#### Check 2: Input có focus không?
```javascript
// Khi bấm edit, input phải được focus (có border xanh)
// Nếu không focus → click vào input trước khi bấm Enter/Esc
```

#### Check 3: Event listener có attached không?
```javascript
// Trong code, input có onKeyDown={handleKeyDown}
// Line 166: onKeyDown={handleKeyDown}
```

#### Check 4: Build có mới không?
```bash
# Check build time
ls -la /app/desktop-app/build/static/js/main.*.js

# Should show recent timestamp (today)
```

#### Check 5: Cache issue?
```bash
# Hard refresh trong browser
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)
```

## Debugging - Console Commands

### Check if component is mounted:
```javascript
// Open DevTools Console
document.querySelector('input[type="text"]').addEventListener('keydown', (e) => {
  console.log('Key pressed:', e.key, 'Ctrl:', e.ctrlKey);
});
```

### Force trigger save:
```javascript
// Get input element
const input = document.querySelector('input[type="text"]');
// Simulate Enter
input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
```

## Expected Behavior Summary

| Key | Dropdown Open + Has Suggestions | Dropdown Closed/Empty | Any Time |
|-----|-------------------------------|---------------------|----------|
| **Enter** | Select suggestion | Save | - |
| **Ctrl+Enter** | - | - | Force save |
| **Esc** | Close dropdown | Cancel edit | - |
| **Tab** | Select suggestion | - | - |
| **↑ / ↓** | Navigate | - | - |

## Common Issues

### Issue 1: "Bấm Enter không lưu"
**Possible causes:**
- Input không có focus → Click vào input trước
- Dropdown đang mở + có gợi ý → Enter chọn gợi ý, bấm Enter lần nữa để lưu
- Event bị prevent ở component khác

**Solution:**
- Dùng Ctrl+Enter để force save
- Đảm bảo dropdown đóng trước khi bấm Enter

### Issue 2: "Bấm Esc không hủy"
**Possible causes:**
- Dropdown đang mở → Esc đóng dropdown, bấm Esc lần nữa để hủy
- Input không có focus

**Solution:**
- Bấm Esc 2 lần (lần 1: đóng dropdown, lần 2: hủy)

### Issue 3: "Keyboard không hoạt động ở BatchScanner nhưng OK ở DesktopScanner"
**Possible causes:**
- Build không đồng bộ
- Cache issue

**Solution:**
```bash
# Rebuild
cd /app/desktop-app
npm run build

# Clear cache in browser
# Hard refresh: Ctrl+Shift+R
```

## Verification Checklist

- [ ] InlineShortCodeEditor được import trong BatchScanner.js (line 3)
- [ ] Component được render với props đầy đủ (onEditStart, onEditEnd)
- [ ] Input có autoFocus
- [ ] Input có onKeyDown handler
- [ ] handleKeyDown function có logic đầy đủ (Enter, Esc, Ctrl+Enter)
- [ ] Build timestamp là mới nhất
- [ ] Browser cache đã clear

## Kết luận

Nếu tất cả checks đều pass mà vẫn không hoạt động:
1. Check browser console có error không
2. Verify input element có event listener: `getEventListeners($0)` (DevTools)
3. Debug với breakpoint trong handleKeyDown function

---

**Last Updated**: 2025-01-12
**Version**: 1.3.0
