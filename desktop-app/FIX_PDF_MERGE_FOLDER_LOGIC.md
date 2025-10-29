# ✅ FIX: Logic gộp PDF trong Quét Thư Mục

## ❌ VẤN ĐỀ TRƯỚC ĐÂY

### **Cấu trúc thư mục:**

```
📁 ParentFolder (Thư mục gốc - user chọn ban đầu)
├── 📁 ChildFolder1 (Thư mục con 1)
│   ├── 📄 image1.jpg → DDKBD
│   ├── 📄 image2.jpg → DDKBD
│   └── 📄 image3.jpg → HDCQ
│
└── 📁 ChildFolder2 (Thư mục con 2)
    ├── 📄 image4.jpg → GCNM
    └── 📄 image5.jpg → GCNM
```

---

### **Bug 1: Mode "Gộp vào thư mục gốc"**

**Code cũ (SAI):**
```javascript
if (mergeMode === 'root') {
  targetDir = parentFolder;  // ❌ Lưu vào ParentFolder
}
```

**Kết quả SAI:**
```
📁 ParentFolder
├── 📄 DDKBD.pdf  ❌ (Lưu ở đây - SAI!)
├── 📄 HDCQ.pdf   ❌ (Lưu ở đây - SAI!)
├── 📁 ChildFolder1
│   ├── 📄 image1.jpg
│   ├── 📄 image2.jpg
│   └── 📄 image3.jpg
```

**ĐÚNG phải là:**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg
    ├── 📄 image2.jpg
    ├── 📄 image3.jpg
    ├── 📄 DDKBD.pdf  ✓ (Trong ChildFolder1)
    └── 📄 HDCQ.pdf   ✓ (Trong ChildFolder1)
```

---

### **Bug 2: Mode "Tạo thư mục mới"**

**Code cũ (SAI):**
```javascript
if (mergeMode === 'new') {
  const parentDir = path.dirname(parentFolder);  // Cha của ParentFolder
  const newFolder = baseName + suffix;
  targetDir = path.join(parentDir, newFolder);  // ❌ Cùng cấp ParentFolder
}
```

**Kết quả SAI:**
```
📁 Desktop
├── 📁 ParentFolder
│   └── 📁 ChildFolder1
│       ├── 📄 image1.jpg
│       └── 📄 image2.jpg
│
└── 📁 ParentFolder_merged  ❌ (Cùng cấp - SAI!)
    ├── 📄 DDKBD.pdf
    └── 📄 HDCQ.pdf
```

**ĐÚNG phải là:**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg
    ├── 📄 image2.jpg
    └── 📁 ChildFolder1_merged  ✓ (TRONG ChildFolder1)
        ├── 📄 DDKBD.pdf
        └── 📄 HDCQ.pdf
```

---

## ✅ GIẢI PHÁP MỚI

### **Nguyên tắc QUAN TRỌNG:**

```
PDF luôn nằm trong THƯMỤC CON (child folder) chứa file ảnh gốc
```

### **Code mới (ĐÚNG):**

```javascript
// LUÔN dùng child folder (folder chứa file ảnh)
const childFolder = path.dirname(filePaths[0]); // Thư mục chứa file ảnh gốc

if (options.mergeMode === 'new') {
  // Tạo folder mới TRONG child folder
  const childBaseName = path.basename(childFolder);
  const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
  targetDir = path.join(childFolder, newFolderName);  // ✓ TRONG child folder
  
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
} else {
  // Mode 'root' hoặc default: Lưu trực tiếp vào child folder
  targetDir = childFolder;  // ✓ Trong child folder
}
```

---

## 📊 KẾT QUẢ SAU KHI FIX

### **Scenario 1: Gộp vào thư mục gốc (root)**

**Input:**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg → DDKBD
    ├── 📄 image2.jpg → DDKBD
    └── 📄 image3.jpg → HDCQ
```

**User chọn:** Gộp vào thư mục gốc

**Output (ĐÚNG):**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg
    ├── 📄 image2.jpg
    ├── 📄 image3.jpg
    ├── 📄 DDKBD.pdf  ✓ (2 images: image1 + image2)
    └── 📄 HDCQ.pdf   ✓ (1 image: image3)
```

**Giải thích:**
- PDF lưu **TRONG ChildFolder1** (nơi chứa ảnh gốc)
- Không lưu vào ParentFolder
- Gộp các file cùng short code thành 1 PDF

---

### **Scenario 2: Tạo thư mục mới**

**Input:**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg → DDKBD
    ├── 📄 image2.jpg → DDKBD
    └── 📄 image3.jpg → HDCQ
```

**User chọn:** Tạo thư mục mới + suffix "_merged"

**Output (ĐÚNG):**
```
📁 ParentFolder
└── 📁 ChildFolder1
    ├── 📄 image1.jpg
    ├── 📄 image2.jpg
    ├── 📄 image3.jpg
    └── 📁 ChildFolder1_merged  ✓ (Folder mới TRONG ChildFolder1)
        ├── 📄 DDKBD.pdf
        └── 📄 HDCQ.pdf
```

**Giải thích:**
- Tạo folder mới **TRONG ChildFolder1**
- Tên folder: `ChildFolder1` + `_merged`
- PDF lưu trong folder mới này
- Không tạo folder cùng cấp ParentFolder

---

### **Scenario 3: Nhiều thư mục con**

**Input:**
```
📁 ParentFolder
├── 📁 ChildFolder1
│   ├── 📄 image1.jpg → DDKBD
│   └── 📄 image2.jpg → HDCQ
│
└── 📁 ChildFolder2
    ├── 📄 image3.jpg → GCNM
    └── 📄 image4.jpg → GCNM
```

**User chọn:** Gộp tất cả + Tạo thư mục mới + suffix "_PDF"

**Output (ĐÚNG):**
```
📁 ParentFolder
├── 📁 ChildFolder1
│   ├── 📄 image1.jpg
│   ├── 📄 image2.jpg
│   └── 📁 ChildFolder1_PDF  ✓ (TRONG ChildFolder1)
│       ├── 📄 DDKBD.pdf
│       └── 📄 HDCQ.pdf
│
└── 📁 ChildFolder2
    ├── 📄 image3.jpg
    ├── 📄 image4.jpg
    └── 📁 ChildFolder2_PDF  ✓ (TRONG ChildFolder2)
        └── 📄 GCNM.pdf
```

**Giải thích:**
- Mỗi child folder có folder mới riêng
- Tên: `{ChildFolderName}_PDF`
- PDF từ files trong child folder → Lưu trong folder mới của chính child folder đó

---

## 🎯 LOGIC MỚI - SUMMARY

### **Key Changes:**

1. **Không dùng `parentFolder` nữa**
   - Trước: `targetDir = parentFolder` ❌
   - Sau: `targetDir = childFolder` ✓

2. **Luôn base trên child folder**
   - `childFolder = path.dirname(filePaths[0])`
   - Tất cả operations base trên childFolder

3. **Mode "new": Tạo TRONG child folder**
   - Trước: Cùng cấp parent ❌
   - Sau: Trong child folder ✓

4. **Mode "root": Lưu TRONG child folder**
   - Trước: Lưu vào parent ❌
   - Sau: Lưu vào child ✓

---

## 🧪 TEST CASES

### Test 1: Single child folder, root mode

**Setup:**
```
ParentFolder/ChildFolder1/ với 3 images (2 DDKBD, 1 HDCQ)
```

**Action:** Gộp vào thư mục gốc

**Expected:**
```
ParentFolder/ChildFolder1/
  ├── DDKBD.pdf ✓
  └── HDCQ.pdf ✓
```

---

### Test 2: Single child folder, new mode

**Setup:**
```
ParentFolder/ChildFolder1/ với 3 images
```

**Action:** Tạo thư mục mới + suffix "_merged"

**Expected:**
```
ParentFolder/ChildFolder1/ChildFolder1_merged/
  ├── DDKBD.pdf ✓
  └── HDCQ.pdf ✓
```

---

### Test 3: Multiple child folders, new mode

**Setup:**
```
ParentFolder/
  ├── Folder1/ (2 images)
  └── Folder2/ (2 images)
```

**Action:** Gộp tất cả + Tạo thư mục mới + suffix "_PDF"

**Expected:**
```
ParentFolder/
  ├── Folder1/Folder1_PDF/ (PDFs từ Folder1) ✓
  └── Folder2/Folder2_PDF/ (PDFs từ Folder2) ✓
```

---

## 📂 FILES MODIFIED

1. `/app/desktop-app/electron/main.js`
   - Function: `ipcMain.handle('merge-by-short-code')`
   - Line ~400-430

2. `/app/desktop-app/public/electron.js`
   - Function: `ipcMain.handle('merge-by-short-code')`
   - Line ~415-445

---

## ✅ VERIFICATION

**Để verify fix hoạt động:**

1. Quét 1 thư mục có subfolders
2. Mỗi subfolder có nhiều ảnh khác short code
3. Click "Gộp PDF"
4. Chọn mode "Gộp vào thư mục gốc"
5. **Check:** PDFs phải nằm TRONG mỗi subfolder ✓

6. Chọn mode "Tạo thư mục mới" + suffix "_merged"
7. **Check:** Folders mới phải nằm TRONG mỗi subfolder ✓
8. **Check:** PDFs phải nằm trong folders mới này ✓

---

## 💡 WHY THIS FIX?

**User expectation:**
- "Gộp vào thư mục gốc" = Gộp vào **thư mục đang chứa ảnh** (child folder)
- "Tạo thư mục mới" = Tạo folder mới **TRONG** thư mục đang chứa ảnh

**Logic:**
- Files ảnh ở đâu → PDF ở đó (hoặc subfolder của đó)
- KHÔNG di chuyển lên parent folder
- Giữ structure gọn gàng, logical

---

## 📝 SUMMARY

**Trước:**
- ❌ PDF lưu vào parent folder (sai vị trí)
- ❌ Folder mới tạo cùng cấp parent (sai structure)

**Sau:**
- ✅ PDF luôn nằm trong child folder (đúng vị trí)
- ✅ Folder mới tạo TRONG child folder (đúng structure)
- ✅ Logic rõ ràng, dễ hiểu
- ✅ Đúng với mong đợi của user

**Files được gộp đúng tên, đúng vị trí!** 🎯
