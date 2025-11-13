# 🧪 Test OCR Mode - Tesseract + Text

## Cách test chế độ mới:

### 1. Kiểm tra Settings đã save chưa

Mở DevTools Console (F12) → Application → Storage → electron-store → Tìm key `ocrMode`

**Nên thấy:**
```json
{
  "ocrMode": "tesseract_text"
}
```

Nếu không có hoặc = `"vision"` → Settings chưa save đúng!

---

### 2. Kiểm tra Logs khi scan

Khi bấm scan, check Console logs:

**✅ Đúng (đang dùng Tesseract+Text):**
```
📦 Batch Process: mode=smart, images=5, engine=gemini-flash
⚡ OCR Mode: tesseract_text
🔄 [OCR MODE] Overriding: smart → tesseract_text
   Reason: User selected Tesseract+Text mode in Settings
🐍 Calling Python batch processor:
   Mode: tesseract_text
   Engine: gemini-flash
   Images: 5

[Tesseract+Text Mode] Processing 5 images...
[Tesseract] Extracted 150 words (confidence: 87.3%)
```

**❌ Sai (vẫn dùng Vision):**
```
📦 Batch Process: mode=smart, images=5, engine=gemini-flash
⚡ OCR Mode: vision
   Using original mode: smart (ocrMode=vision)
🐍 Calling Python batch processor:
   Mode: smart
   ...
```

---

### 3. Test thủ công qua CLI

Test Python script trực tiếp:

```bash
cd /app/desktop-app/python

# Test Tesseract+Text mode
python3 batch_processor.py tesseract_text gemini-flash YOUR_API_KEY /path/to/image1.jpg /path/to/image2.jpg
```

**Kết quả mong đợi:**
```
⚡ [NEW MODE] Using Tesseract + Gemini Text approach
[Tesseract+Text Mode] Processing 2 images...
[1/2] Processing: image1.jpg
[Tesseract] Extracted 120 words (confidence: 89.2%)
  ✅ Result: GCN (confidence: 92.5%)
[2/2] Processing: image2.jpg
...
```

---

### 4. So sánh tốc độ

**Vision Mode:**
- 5 files: ~15-20 giây
- Request size: ~2-5 MB

**Tesseract+Text Mode:**
- 5 files: ~5-8 giây (nhanh hơn 2-3x)
- Request size: ~5-10 KB

---

### 5. Troubleshooting

**Vấn đề:** Settings đã chọn nhưng vẫn không apply

**Giải pháp:**
1. Đóng app hoàn toàn (Task Manager kill process)
2. Mở lại app
3. Vào Settings → Kiểm tra radio button đã checked chưa
4. Nếu chưa → Click lại và Save
5. Scan và check logs

**Vấn đề:** Lỗi "Tesseract not available"

**Giải pháp:**
```bash
# Check Tesseract installed
tesseract --version

# Check Python can import
python3 -c "import pytesseract; print('OK')"
```

**Vấn đề:** Accuracy thấp (~60-70%)

**Nguyên nhân:** Ảnh chất lượng kém
**Giải pháp:** Quay lại Vision mode cho files này

---

## Debug Checklist

- [ ] Settings đã save (`ocrMode: "tesseract_text"`)
- [ ] Console log hiển thị "Overriding: ... → tesseract_text"
- [ ] Python log hiển thị "[Tesseract+Text Mode] Processing..."
- [ ] Thời gian xử lý nhanh hơn (~5-8s thay vì 15-20s)
- [ ] Kết quả classification vẫn chính xác (check random samples)

---

## Khi nào nên dùng mode nào?

### ✅ Dùng **Tesseract+Text** khi:
- Ảnh chất lượng tốt (scan rõ nét, không mờ)
- Batch lớn (50-100+ files)
- Cần nhanh
- Gặp nhiều lỗi 503
- Tiết kiệm chi phí

### ✅ Dùng **Vision** khi:
- Ảnh chất lượng kém (mờ, xiêng, nhàu)
- Cần accuracy cao nhất (~95%+)
- Batch nhỏ (<10 files)
- Không quan tâm tốc độ/chi phí
