# 📋 VÍ DỤ CỤ THỂ - LOGIC GỘP PDF

## 🎬 SCENARIO 1: MỘT THƯ MỤC CON

### **Cấu trúc ban đầu:**

```
C:\Users\Admin\Desktop\HoSoNha\
└── ThangA\
    ├── anh1.jpg  → Kết quả quét: DDKBD (Đơn đăng ký biến động)
    ├── anh2.jpg  → Kết quả quét: DDKBD (Đơn đăng ký biến động)
    ├── anh3.jpg  → Kết quả quét: HDCQ (Hợp đồng chuyển nhượng)
    └── anh4.jpg  → Kết quả quét: HDCQ (Hợp đồng chuyển nhượng)
```

**User làm:**
1. Quét thư mục: `C:\Users\Admin\Desktop\HoSoNha\`
2. App hiển thị 1 tab: "ThangA" với 4 files đã quét
3. User click "Gộp PDF" cho tab "ThangA"

---

### **CASE 1.1: Chọn "Gộp vào thư mục gốc"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
└── ThangA\
    ├── anh1.jpg
    ├── anh2.jpg
    ├── anh3.jpg
    ├── anh4.jpg
    ├── DDKBD.pdf  ✅ (Gộp từ anh1.jpg + anh2.jpg) - 2 trang
    └── HDCQ.pdf   ✅ (Gộp từ anh3.jpg + anh4.jpg) - 2 trang
```

**Giải thích:**
- PDF lưu **TRONG** `C:\Users\Admin\Desktop\HoSoNha\ThangA\`
- KHÔNG lưu vào `C:\Users\Admin\Desktop\HoSoNha\`
- 2 file cùng tên DDKBD → Gộp thành 1 PDF tên `DDKBD.pdf`
- 2 file cùng tên HDCQ → Gộp thành 1 PDF tên `HDCQ.pdf`

---

### **CASE 1.2: Chọn "Tạo thư mục mới" + Suffix: "_PDF"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
└── ThangA\
    ├── anh1.jpg
    ├── anh2.jpg
    ├── anh3.jpg
    ├── anh4.jpg
    └── ThangA_PDF\  ✅ (Thư mục mới tạo TRONG ThangA)
        ├── DDKBD.pdf  (2 trang từ anh1 + anh2)
        └── HDCQ.pdf   (2 trang từ anh3 + anh4)
```

**Giải thích:**
- Tạo thư mục mới: `ThangA_PDF` **TRONG** `ThangA\`
- Path đầy đủ: `C:\Users\Admin\Desktop\HoSoNha\ThangA\ThangA_PDF\`
- PDFs lưu trong thư mục mới này
- KHÔNG tạo `C:\Users\Admin\Desktop\HoSoNha\ThangA_PDF\` (cùng cấp)

---

### **CASE 1.3: Chọn "Tạo thư mục mới" + Suffix: "_GopLai"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
└── ThangA\
    ├── anh1.jpg
    ├── anh2.jpg
    ├── anh3.jpg
    ├── anh4.jpg
    └── ThangA_GopLai\  ✅ (Suffix "_GopLai")
        ├── DDKBD.pdf
        └── HDCQ.pdf
```

---

## 🎬 SCENARIO 2: NHIỀU THƯ MỤC CON

### **Cấu trúc ban đầu:**

```
C:\Users\Admin\Desktop\HoSoNha\
├── ThangA\
│   ├── anh1.jpg  → DDKBD
│   ├── anh2.jpg  → DDKBD
│   └── anh3.jpg  → HDCQ
│
├── ThangB\
│   ├── file1.jpg → GCNM (Giấy chứng nhận)
│   ├── file2.jpg → GCNM (Giấy chứng nhận)
│   └── file3.jpg → CCCD (Căn cước công dân)
│
└── ThangC\
    ├── doc1.jpg  → HDUQ (Hợp đồng ủy quyền)
    └── doc2.jpg  → HDUQ (Hợp đồng ủy quyền)
```

**User làm:**
1. Quét thư mục: `C:\Users\Admin\Desktop\HoSoNha\`
2. App hiển thị 3 tabs: "ThangA", "ThangB", "ThangC"
3. User click "Gộp tất cả"
4. Chọn modal merge options

---

### **CASE 2.1: "Gộp vào thư mục gốc"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
├── ThangA\
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── anh3.jpg
│   ├── DDKBD.pdf  ✅ (2 trang: anh1 + anh2) - Trong ThangA
│   └── HDCQ.pdf   ✅ (1 trang: anh3) - Trong ThangA
│
├── ThangB\
│   ├── file1.jpg
│   ├── file2.jpg
│   ├── file3.jpg
│   ├── GCNM.pdf   ✅ (2 trang: file1 + file2) - Trong ThangB
│   └── CCCD.pdf   ✅ (1 trang: file3) - Trong ThangB
│
└── ThangC\
    ├── doc1.jpg
    ├── doc2.jpg
    └── HDUQ.pdf   ✅ (2 trang: doc1 + doc2) - Trong ThangC
```

**Giải thích:**
- Mỗi thư mục con có PDFs riêng của mình
- PDFs nằm **TRONG** thư mục con đó
- KHÔNG có PDF nào trong `C:\Users\Admin\Desktop\HoSoNha\` (thư mục gốc)

---

### **CASE 2.2: "Tạo thư mục mới" + Suffix: "_PDF"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
├── ThangA\
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── anh3.jpg
│   └── ThangA_PDF\  ✅ (Folder mới TRONG ThangA)
│       ├── DDKBD.pdf
│       └── HDCQ.pdf
│
├── ThangB\
│   ├── file1.jpg
│   ├── file2.jpg
│   ├── file3.jpg
│   └── ThangB_PDF\  ✅ (Folder mới TRONG ThangB)
│       ├── GCNM.pdf
│       └── CCCD.pdf
│
└── ThangC\
    ├── doc1.jpg
    ├── doc2.jpg
    └── ThangC_PDF\  ✅ (Folder mới TRONG ThangC)
        └── HDUQ.pdf
```

**Giải thích:**
- Mỗi thư mục con có folder mới riêng
- Tên folder: `{TênThưMụcCon}_PDF`
- PDFs lưu trong folders mới này
- Folders mới nằm **TRONG** thư mục con tương ứng

---

### **CASE 2.3: "Tạo thư mục mới" + Suffix: "_Merged_2025"**

**Kết quả SAU KHI GỘP:**

```
C:\Users\Admin\Desktop\HoSoNha\
├── ThangA\
│   ├── anh1.jpg
│   ├── anh2.jpg
│   ├── anh3.jpg
│   └── ThangA_Merged_2025\  ✅
│       ├── DDKBD.pdf
│       └── HDCQ.pdf
│
├── ThangB\
│   ├── file1.jpg
│   ├── file2.jpg
│   ├── file3.jpg
│   └── ThangB_Merged_2025\  ✅
│       ├── GCNM.pdf
│       └── CCCD.pdf
│
└── ThangC\
    ├── doc1.jpg
    ├── doc2.jpg
    └── ThangC_Merged_2025\  ✅
        └── HDUQ.pdf
```

---

## 🎬 SCENARIO 3: TRƯỜNG HỢP ĐẶC BIỆT

### **CASE 3.1: Files trùng tên short code**

**Input:**
```
ThangA\
├── page1.jpg → DDKBD
├── page2.jpg → DDKBD
├── page3.jpg → DDKBD
└── page4.jpg → DDKBD
```

**Kết quả GỘP (Mode: Root):**
```
ThangA\
├── page1.jpg
├── page2.jpg
├── page3.jpg
├── page4.jpg
└── DDKBD.pdf  ✅ (4 trang: page1 + page2 + page3 + page4)
```

---

### **CASE 3.2: Đã có file PDF trùng tên**

**Input:**
```
ThangA\
├── DDKBD.pdf  (Đã tồn tại từ trước)
├── anh1.jpg → DDKBD
└── anh2.jpg → DDKBD
```

**Kết quả GỘP (Mode: Root):**
```
ThangA\
├── DDKBD.pdf      (File cũ - không đổi)
├── DDKBD(1).pdf   ✅ (File mới - gộp từ anh1 + anh2)
├── anh1.jpg
└── anh2.jpg
```

**Giải thích:** Tự động thêm số `(1)`, `(2)`, ... nếu file đã tồn tại

---

### **CASE 3.3: Chỉ 1 file thuộc 1 short code**

**Input:**
```
ThangA\
├── anh1.jpg → DDKBD
├── anh2.jpg → HDCQ
└── anh3.jpg → GCNM
```

**Kết quả GỘP (Mode: Root):**
```
ThangA\
├── anh1.jpg
├── anh2.jpg
├── anh3.jpg
├── DDKBD.pdf  ✅ (1 trang: anh1)
├── HDCQ.pdf   ✅ (1 trang: anh2)
└── GCNM.pdf   ✅ (1 trang: anh3)
```

**Giải thích:** Mỗi short code đều tạo 1 PDF riêng, dù chỉ có 1 file

---

## 🎬 SCENARIO 4: THỰC TẾ - HỒ SƠ NHÀ ĐẤT

### **Cấu trúc thực tế:**

```
D:\HoSoNhaDat_NguyenVanA\
├── 01_GiayChungNhan\
│   ├── trang1.jpg → GCNM
│   ├── trang2.jpg → GCNM
│   └── trang3.jpg → GCNM
│
├── 02_HopDong\
│   ├── hopdong_1.jpg → HDCQ
│   ├── hopdong_2.jpg → HDCQ
│   ├── hopdong_3.jpg → HDCQ
│   └── hopdong_4.jpg → HDCQ
│
├── 03_GiayToKhac\
│   ├── cccd_1.jpg → CCCD
│   ├── cccd_2.jpg → CCCD
│   ├── soho_1.jpg → SHGD
│   └── soho_2.jpg → SHGD
│
└── 04_BanVe\
    ├── banve1.jpg → HSKT
    ├── banve2.jpg → HSKT
    └── banve3.jpg → HSKT
```

---

### **User chọn: "Gộp tất cả" + "Tạo thư mục mới" + Suffix: "_PDFs"**

**Kết quả:**

```
D:\HoSoNhaDat_NguyenVanA\
├── 01_GiayChungNhan\
│   ├── trang1.jpg
│   ├── trang2.jpg
│   ├── trang3.jpg
│   └── 01_GiayChungNhan_PDFs\  ✅
│       └── GCNM.pdf (3 trang)
│
├── 02_HopDong\
│   ├── hopdong_1.jpg
│   ├── hopdong_2.jpg
│   ├── hopdong_3.jpg
│   ├── hopdong_4.jpg
│   └── 02_HopDong_PDFs\  ✅
│       └── HDCQ.pdf (4 trang)
│
├── 03_GiayToKhac\
│   ├── cccd_1.jpg
│   ├── cccd_2.jpg
│   ├── soho_1.jpg
│   ├── soho_2.jpg
│   └── 03_GiayToKhac_PDFs\  ✅
│       ├── CCCD.pdf (2 trang)
│       └── SHGD.pdf (2 trang)
│
└── 04_BanVe\
    ├── banve1.jpg
    ├── banve2.jpg
    ├── banve3.jpg
    └── 04_BanVe_PDFs\  ✅
        └── HSKT.pdf (3 trang)
```

**Tổng kết:**
- 4 thư mục con → 4 folders mới (mỗi folder trong thư mục con tương ứng)
- Tổng: 6 PDFs được tạo
- Tất cả PDFs nằm trong folders mới, không lẫn với ảnh gốc

---

## ✅ CHECKLIST KIỂM TRA

### **Để verify logic đúng:**

**Test 1: Mode "Root"**
```
☐ PDFs nằm TRONG thư mục con (child folder)
☐ PDFs KHÔNG nằm trong thư mục gốc (parent folder)
☐ Files cùng short code được gộp thành 1 PDF
☐ File trùng tên → Tự động thêm (1), (2), ...
```

**Test 2: Mode "New"**
```
☐ Folder mới tạo TRONG thư mục con (child folder)
☐ Folder mới KHÔNG tạo cùng cấp parent folder
☐ Tên folder: {TênThưMụcCon} + {Suffix}
☐ PDFs nằm trong folder mới
```

**Test 3: Multiple folders**
```
☐ Mỗi thư mục con xử lý độc lập
☐ PDFs của ThangA nằm trong ThangA (không lẫn ThangB)
☐ Tất cả folders đều được process
```

---

## 💡 TÓM TẮT LOGIC

```
NGUYÊN TẮC:
  PDF luôn ở GẦN file ảnh gốc nhất có thể

MODE "ROOT":
  PDF → Lưu trực tiếp vào thư mục con chứa ảnh

MODE "NEW":
  PDF → Tạo folder mới TRONG thư mục con → Lưu vào đó

KHÔNG BAO GIỜ:
  ❌ Lưu PDF vào parent folder
  ❌ Tạo folder mới cùng cấp parent
  ❌ Di chuyển file ra ngoài cấu trúc gốc
```

Anh thấy logic này đúng chưa ạ? 😊

