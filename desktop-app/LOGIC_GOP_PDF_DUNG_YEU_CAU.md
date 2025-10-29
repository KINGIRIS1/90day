# ✅ LOGIC GỘP PDF - ĐÚNG YÊU CẦU

## 🎯 NGUYÊN TẮC

### **File Scan:**
- PDF lưu **CÙNG FOLDER** với file ảnh gốc

### **Folder Scan:**
- **Mode "Root"**: Giống File Scan → Lưu cùng folder với ảnh
- **Mode "New"**: Tạo folder mới **CÙNG CẤP** với folder gốc

---

## 📖 VÍ DỤ CHI TIẾT

### **SCENARIO 1: FILE SCAN**

**Cấu trúc ban đầu:**
```
D:\HoSo\
└── ThangA\
    ├── anh1.jpg → DDKBD
    ├── anh2.jpg → DDKBD
    ├── anh3.jpg → HDCQ
    └── anh4.jpg → HDCQ
```

**User làm:**
1. Chọn 4 files trong `ThangA\`
2. Quét (File Scan)
3. Click "Gộp PDF"

**Kết quả:**
```
D:\HoSo\
└── ThangA\
    ├── anh1.jpg
    ├── anh2.jpg
    ├── anh3.jpg
    ├── anh4.jpg
    ├── DDKBD.pdf  ✅ (Cùng folder với ảnh)
    └── HDCQ.pdf   ✅ (Cùng folder với ảnh)
```

**Giải thích:**
- PDF lưu **TRONG** `ThangA\` (nơi chứa ảnh gốc)
- Gộp các file cùng short code thành 1 PDF

---

### **SCENARIO 2: FOLDER SCAN - Mode "Root"**

**Cấu trúc ban đầu:**
```
D:\HoSo\
└── ThangA\
    ├── anh1.jpg → DDKBD
    ├── anh2.jpg → DDKBD
    ├── anh3.jpg → HDCQ
    └── anh4.jpg → HDCQ
```

**User làm:**
1. Quét thư mục `D:\HoSo\`
2. App hiển thị tab "ThangA"
3. Click "Gộp PDF"
4. Chọn mode **"Gộp vào thư mục gốc"**

**Kết quả (GIỐNG FILE SCAN):**
```
D:\HoSo\
└── ThangA\
    ├── anh1.jpg
    ├── anh2.jpg
    ├── anh3.jpg
    ├── anh4.jpg
    ├── DDKBD.pdf  ✅ (Cùng folder với ảnh)
    └── HDCQ.pdf   ✅ (Cùng folder với ảnh)
```

**Giải thích:**
- Logic **GIỐNG HỆT** File Scan
- PDF lưu vào folder chứa ảnh (`ThangA\`)

---

### **SCENARIO 3: FOLDER SCAN - Mode "New"**

**Cấu trúc ban đầu:**
```
D:\HoSo\
└── ThangA\
    ├── anh1.jpg → DDKBD
    ├── anh2.jpg → DDKBD
    ├── anh3.jpg → HDCQ
    └── anh4.jpg → HDCQ
```

**User làm:**
1. Quét thư mục `D:\HoSo\`
2. App hiển thị tab "ThangA"
3. Click "Gộp PDF"
4. Chọn mode **"Tạo thư mục mới"** + Suffix: **"_PDF"**

**Kết quả:**
```
D:\HoSo\
├── ThangA\
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── anh3.jpg
│   └── anh4.jpg
│
└── ThangA_PDF\  ✅ (CÙNG CẤP với ThangA)
    ├── DDKBD.pdf
    └── HDCQ.pdf
```

**Giải thích:**
- Tạo folder mới: `ThangA_PDF`
- Vị trí: **CÙNG CẤP** với `ThangA\` (trong `D:\HoSo\`)
- PDFs lưu trong folder mới

---

### **SCENARIO 4: NHIỀU FOLDER CON - Mode "Root"**

**Cấu trúc ban đầu:**
```
D:\HoSo\
├── ThangA\
│   ├── anh1.jpg → DDKBD
│   └── anh2.jpg → HDCQ
│
├── ThangB\
│   ├── file1.jpg → GCNM
│   └── file2.jpg → GCNM
│
└── ThangC\
    ├── doc1.jpg → HDUQ
    └── doc2.jpg → HDUQ
```

**User làm:**
1. Quét thư mục `D:\HoSo\`
2. App hiển thị 3 tabs: ThangA, ThangB, ThangC
3. Click "Gộp tất cả"
4. Chọn mode **"Gộp vào thư mục gốc"**

**Kết quả:**
```
D:\HoSo\
├── ThangA\
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── DDKBD.pdf  ✅ (Trong ThangA)
│   └── HDCQ.pdf   ✅ (Trong ThangA)
│
├── ThangB\
│   ├── file1.jpg
│   ├── file2.jpg
│   └── GCNM.pdf   ✅ (Trong ThangB)
│
└── ThangC\
    ├── doc1.jpg
    ├── doc2.jpg
    └── HDUQ.pdf   ✅ (Trong ThangC)
```

**Giải thích:**
- Mỗi folder con có PDFs riêng
- PDFs lưu **TRONG** folder con tương ứng
- Logic giống File Scan

---

### **SCENARIO 5: NHIỀU FOLDER CON - Mode "New"**

**Cấu trúc ban đầu:** (Giống Scenario 4)

**User làm:**
1. Quét thư mục `D:\HoSo\`
2. App hiển thị 3 tabs
3. Click "Gộp tất cả"
4. Chọn mode **"Tạo thư mục mới"** + Suffix: **"_PDF"**

**Kết quả:**
```
D:\HoSo\
├── ThangA\
│   ├── anh1.jpg
│   └── anh2.jpg
│
├── ThangA_PDF\  ✅ (CÙNG CẤP ThangA)
│   ├── DDKBD.pdf
│   └── HDCQ.pdf
│
├── ThangB\
│   ├── file1.jpg
│   └── file2.jpg
│
├── ThangB_PDF\  ✅ (CÙNG CẤP ThangB)
│   └── GCNM.pdf
│
├── ThangC\
│   ├── doc1.jpg
│   └── doc2.jpg
│
└── ThangC_PDF\  ✅ (CÙNG CẤP ThangC)
    └── HDUQ.pdf
```

**Giải thích:**
- Tạo 3 folders mới: `ThangA_PDF`, `ThangB_PDF`, `ThangC_PDF`
- Tất cả **CÙNG CẤP** với folders gốc (trong `D:\HoSo\`)
- Mỗi folder mới chứa PDFs từ folder tương ứng

---

### **SCENARIO 6: THỰC TẾ - TÊN FOLDER CÓ DẤU CÁCH**

**Cấu trúc ban đầu:**
```
D:\Documents\
└── HoSoNha - ThangA\
    ├── page1.jpg → DDKBD
    ├── page2.jpg → DDKBD
    └── page3.jpg → HDCQ
```

**User làm:**
1. Quét thư mục `D:\Documents\`
2. Tab: "HoSoNha - ThangA"
3. Click "Gộp PDF"
4. Mode **"Tạo thư mục mới"** + Suffix: **"_PDF"**

**Kết quả:**
```
D:\Documents\
├── HoSoNha - ThangA\
│   ├── page1.jpg
│   ├── page2.jpg
│   └── page3.jpg
│
└── HoSoNha - ThangA_PDF\  ✅ (Giữ nguyên tên + thêm _PDF)
    ├── DDKBD.pdf
    └── HDCQ.pdf
```

**Giải thích:**
- Tên folder: `HoSoNha - ThangA` + `_PDF` = `HoSoNha - ThangA_PDF`
- Giữ nguyên dấu cách và ký tự đặc biệt
- Folder mới **CÙNG CẤP** với `HoSoNha - ThangA\`

---

### **SCENARIO 7: SUFFIX TỰY CHỈNH**

**User chọn suffix:** `_GopLai_2025`

**Kết quả:**
```
D:\Documents\
├── HoSoNha - ThangA\
│   └── (ảnh gốc)
│
└── HoSoNha - ThangA_GopLai_2025\  ✅
    └── (PDFs)
```

**User chọn suffix:** ` (merged)`

**Kết quả:**
```
D:\Documents\
├── HoSoNha - ThangA\
│   └── (ảnh gốc)
│
└── HoSoNha - ThangA (merged)\  ✅
    └── (PDFs)
```

---

## 📊 SO SÁNH

### **Trước (SAI):**

**Mode "New":**
```
HoSo\
└── ThangA\
    └── ThangA_PDF\  ❌ (TRONG ThangA - SAI!)
        └── PDFs
```

**Sau (ĐÚNG):**
```
HoSo\
├── ThangA\
│   └── (ảnh gốc)
│
└── ThangA_PDF\  ✅ (CÙNG CẤP ThangA)
    └── PDFs
```

---

## 🎯 LOGIC CODE

```javascript
const childFolder = path.dirname(filePaths[0]); // Folder chứa ảnh

if (options.mergeMode === 'new') {
  // Tạo folder mới CÙNG CẤP với child folder
  const parentOfChild = path.dirname(childFolder);  // Lên 1 cấp
  const childBaseName = path.basename(childFolder); // Tên folder gốc
  const newFolderName = childBaseName + suffix;     // Thêm suffix
  targetDir = path.join(parentOfChild, newFolderName); // CÙNG CẤP
} else {
  // Mode "Root" hoặc File Scan: Lưu cùng folder với ảnh
  targetDir = childFolder;
}
```

**Ví dụ:**
```
childFolder = "D:\HoSo\ThangA"
parentOfChild = "D:\HoSo"
childBaseName = "ThangA"
newFolderName = "ThangA_PDF"
targetDir = "D:\HoSo\ThangA_PDF"  ✅ CÙNG CẤP
```

---

## ✅ CHECKLIST

### **File Scan:**
```
☐ PDF lưu cùng folder với ảnh gốc
☐ Không có options để tạo folder mới
```

### **Folder Scan - Mode "Root":**
```
☐ PDF lưu TRONG folder con (nơi chứa ảnh)
☐ Logic giống hệt File Scan
☐ Không tạo folder mới
```

### **Folder Scan - Mode "New":**
```
☐ Folder mới tạo CÙNG CẤP với folder gốc
☐ Tên: {TênFolderGốc} + {Suffix}
☐ PDFs lưu trong folder mới
☐ Folder gốc không bị thay đổi
```

---

## 💡 TÓM TẮT

```
FILE SCAN:
  → PDF cùng folder với ảnh

FOLDER SCAN "ROOT":
  → Giống File Scan
  → PDF cùng folder với ảnh

FOLDER SCAN "NEW":
  → Tạo folder mới CÙNG CẤP
  → ThangA → ThangA_PDF (cùng cấp)
  → PDF trong folder mới
```

**ĐÚNG YÊU CẦU!** ✅
