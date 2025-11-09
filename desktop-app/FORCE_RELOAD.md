# ⚠️ QUAN TRỌNG: Force Reload App

Nếu bạn gặp lỗi hoặc tính năng mới không hoạt động, vui lòng:

## Windows:

### Cách 1: Hard Reload
1. Mở app
2. Nhấn **Ctrl + Shift + R** (hoặc **Ctrl + F5**)
3. App sẽ reload và clear cache

### Cách 2: Clear Cache thủ công
1. Đóng app hoàn toàn
2. Xóa thư mục cache:
   ```
   %APPDATA%\90dayChonThanh\Cache
   %APPDATA%\90dayChonThanh\Code Cache
   ```
3. Mở lại app

### Cách 3: DevTools
1. Mở app
2. Nhấn **Ctrl + Shift + I** (DevTools)
3. Click phải vào nút refresh
4. Chọn **"Empty Cache and Hard Reload"**
5. Đóng DevTools

## Lỗi thường gặp:

### "process-batch-scan timeout"
→ Đây là handler cũ, app chưa reload đúng
→ Làm theo Cách 1 hoặc 2 ở trên

### "setResults is not defined"
→ Code mới chưa được load
→ Hard reload (Ctrl + Shift + R)

### Tính năng mới không thấy
→ Clear cache và restart app

---

**💡 Tip:** Sau mỗi lần update code, nên làm Hard Reload để đảm bảo code mới được load.
