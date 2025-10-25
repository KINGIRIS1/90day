# So sánh công nghệ quét tài liệu: Chi phí vs Độ chính xác

## 📊 Tổng quan

| Công nghệ | Chi phí | Độ chính xác | Khuyến nghị |
|-----------|---------|--------------|-------------|
| **GPT-4 Vision** (hiện tại) | $0.002/ảnh | 95-98% | ✅ Tốt nhất nhưng đắt |
| **Hybrid OCR + Rules** | $0 | 85-92% | ⭐ **KHUYẾN NGHỊ** |
| **Self-hosted LLM** | $0.0001/ảnh | 90-95% | ✅ Tốt cho scale lớn |
| **Azure Document AI** | $0.001/ảnh | 92-95% | ✅ Giá vừa, chính xác |
| **PaddleOCR + GPT (edge case)** | $0.0005/ảnh | 88-94% | ⭐ Cân bằng tốt |

---

## 🎯 Phương án khuyến nghị: HYBRID APPROACH

### **Chiến lược 3 tầng**

```
┌─────────────────────────────────────────┐
│  Tier 1: Traditional OCR (90% cases)   │
│  → FREE, xử lý văn bản rõ ràng         │
│  → Chi phí: $0                          │
└─────────────────────────────────────────┘
                ↓ (nếu confidence < 0.7)
┌─────────────────────────────────────────┐
│  Tier 2: Rule-based + Template Match   │
│  → FREE, dựa vào keywords Việt Nam     │
│  → Chi phí: $0                          │
└─────────────────────────────────────────┘
                ↓ (nếu vẫn không match)
┌─────────────────────────────────────────┐
│  Tier 3: GPT-4 Vision (10% cases)      │
│  → Chỉ dùng cho trường hợp khó         │
│  → Chi phí: $0.002 × 10% = $0.0002/ảnh │
└─────────────────────────────────────────┘

TỔNG CHI PHÍ: ~$0.0002/ảnh (GIẢM 90%!)
```

---

## 🔧 Chi tiết từng phương án

### 1. ⭐ **HYBRID: PaddleOCR + Rules + GPT (Edge case)** 

#### **Cách hoạt động**:

```python
# Step 1: OCR với PaddleOCR (FREE)
text = paddleocr.ocr(image)

# Step 2: Rule-based classification (FREE)
if "giấy chứng nhận" in text.lower():
    doc_type = "GCN"
elif "bản vẽ" in text.lower():
    doc_type = "HSKT"
elif "biên bản" in text.lower():
    doc_type = "BBGD"
# ... check 50+ keywords

# Step 3: Nếu confidence thấp → Gọi GPT
if confidence < 0.7:
    result = gpt4_vision(image)  # Chỉ 10% cases
```

#### **Ưu điểm**:
- ✅ Chi phí: ~**$0.0002/ảnh** (giảm 90%)
- ✅ Độ chính xác: **88-94%**
- ✅ Nhanh: OCR local < 1s
- ✅ Không phụ thuộc API bên ngoài cho 90% cases

#### **Nhược điểm**:
- ⚠️ Cần maintain rules (keywords)
- ⚠️ Độ chính xác thấp hơn 4-8% so với GPT-4 full

#### **Implementation**:

```python
# Install
pip install paddleocr paddlepaddle-gpu  # hoặc paddlepaddle (CPU)

# Code
from paddleocr import PaddleOCR
import re

ocr = PaddleOCR(use_angle_cls=True, lang='vi')

def classify_document_hybrid(image_path: str):
    # Step 1: OCR
    result = ocr.ocr(image_path, cls=True)
    text = ' '.join([line[1][0] for line in result[0]])
    
    # Step 2: Rule-based (Vietnamese document types)
    rules = {
        "GCN": ["giấy chứng nhận", "gcn quyền sử dụng", "cộng hòa xã hội"],
        "BMT": ["bản mô tả ranh giới", "mốc giới", "thửa đất"],
        "HSKT": ["bản vẽ", "trích lục", "đo tách", "chỉnh lý"],
        "BVHC": ["hoàn công", "công trình"],
        # ... 50+ rules
    }
    
    confidence = 0
    matched_type = "UNKNOWN"
    
    for doc_type, keywords in rules.items():
        for keyword in keywords:
            if keyword in text.lower():
                confidence = 0.8  # High confidence
                matched_type = doc_type
                break
        if confidence > 0.7:
            break
    
    # Step 3: Fallback to GPT if uncertain
    if confidence < 0.7:
        matched_type, confidence = gpt4_classify(image_path)
    
    return {
        "type": matched_type,
        "confidence": confidence,
        "method": "ocr" if confidence >= 0.7 else "gpt"
    }
```

#### **Chi phí breakdown**:

```
1000 ảnh/ngày:
- 900 ảnh qua OCR: FREE
- 100 ảnh qua GPT: 100 × $0.002 = $0.20/ngày

Chi phí tháng: $0.20 × 22 = $4.4/tháng
vs GPT-4 full: $43/tháng

TIẾT KIỆM: 90%! 🎉
```

---

### 2. **Self-hosted Open-Source LLM**

#### **Options**:

**A. Qwen2-VL (Alibaba)**
- Model size: 7B parameters
- Accuracy: ~90-93% (so với GPT-4 95%)
- Hardware: RTX 4090 (24GB VRAM)
- Cost: **$0** (chỉ trả điện + GPU)

**B. LLaVA (Meta)**
- Model size: 7B/13B
- Accuracy: ~88-92%
- Hardware: RTX 3090/4090
- Cost: **$0**

**C. CogVLM (Tsinghua University)**
- Model size: 17B
- Accuracy: ~92-95%
- Hardware: A100 40GB
- Cost: Cloud GPU ~$1/hour → $720/tháng

#### **Chi phí so sánh**:

```
Option 1: Mua GPU (1 lần)
- RTX 4090: $1,600 (one-time)
- Server: $1,000
- Setup: $500
Total: $3,100 upfront

Operating cost: $50/tháng (điện)

Break-even: 
- vs GPT-4: $43/tháng → 72 tháng (6 năm)
- vs Hybrid: $4/tháng → 775 tháng (không đáng)

Option 2: Cloud GPU
- RunPod RTX 4090: $0.50/hour
- 24/7: $360/tháng
- Đắt hơn GPT-4!

✅ Khuyến nghị: Chỉ self-host nếu > 5,000 ảnh/ngày
```

#### **Implementation**:

```python
# Install Qwen2-VL
pip install transformers torch pillow

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

def classify_with_qwen(image_path: str):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": "Classify this Vietnamese land document..."}
            ]
        }
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    output = model.generate(**inputs, max_new_tokens=200)
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return result
```

---

### 3. **Azure Document Intelligence** (Microsoft)

#### **Pricing**:
- $0.001/page (giá chuẩn)
- Custom model training: $40/1000 pages
- Rẻ hơn GPT-4 50%

#### **Ưu điểm**:
- ✅ Độ chính xác cao: 92-95%
- ✅ Support Vietnamese
- ✅ Trích xuất structured data tốt
- ✅ No maintenance

#### **Nhược điểm**:
- ⚠️ Cần training với Vietnamese land documents
- ⚠️ Vẫn tốn tiền (dù rẻ hơn)

```python
# Install
pip install azure-ai-formrecognizer

from azure.ai.formrecognizer import DocumentAnalysisClient

client = DocumentAnalysisClient(
    endpoint="https://<your-endpoint>.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<api-key>")
)

def classify_with_azure(image_path: str):
    with open(image_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout", document=f
        )
    result = poller.result()
    
    # Extract text
    text = ' '.join([line.content for page in result.pages for line in page.lines])
    
    # Apply rules (same as hybrid approach)
    doc_type = classify_by_rules(text)
    
    return doc_type
```

---

### 4. **AWS Textract**

Similar to Azure, pricing ~$0.0015/page

---

## 📊 So sánh chi tiết

### Chi phí (1000 ảnh/ngày):

| Method | Chi phí/ngày | Chi phí/tháng | Tiết kiệm |
|--------|--------------|---------------|-----------|
| **GPT-4 Vision** | $2 | $43 | Baseline |
| **Hybrid OCR+GPT** | $0.20 | **$4.4** | **90%** ⭐ |
| **Azure Document AI** | $1 | $22 | 50% |
| **Self-hosted (cloud GPU)** | $12 | $360 | -737% ❌ |
| **Self-hosted (own GPU)** | $1.5 | $50* | +16% |

*Tính điện + amortization

### Độ chính xác:

| Method | Accuracy | Latency | Maintenance |
|--------|----------|---------|-------------|
| **GPT-4 Vision** | 95-98% | 3s | Low |
| **Hybrid OCR+GPT** | 88-94% | 1.5s | **Medium** |
| **Azure Document AI** | 92-95% | 2s | Low |
| **Self-hosted Qwen2-VL** | 90-93% | 0.8s | **High** |

---

## 🎯 Khuyến nghị theo quy mô

### < 1,000 ảnh/ngày (Startup)
```
✅ DÙNG: Hybrid OCR + Rules + GPT fallback
- Chi phí: $4-5/tháng
- ROI: Rất cao
- Implementation: 2-3 ngày
```

### 1,000 - 5,000 ảnh/ngày (SMB)
```
✅ DÙNG: Hybrid OCR + Azure Document AI fallback
- Chi phí: $10-25/tháng
- ROI: Cao
- Maintenance: Thấp
```

### > 5,000 ảnh/ngày (Enterprise)
```
✅ DÙNG: Self-hosted Qwen2-VL + GPU
- Chi phí upfront: $3,000 (GPU)
- Chi phí monthly: $50 (điện)
- ROI: Tốt sau 6-12 tháng
- Unlimited usage
```

---

## 🔧 Implementation Plan cho Hybrid Approach

### Phase 1: Setup PaddleOCR (1 ngày)

```bash
pip install paddleocr paddlepaddle-gpu
```

```python
# /app/backend/ocr_engine.py
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)

def extract_text(image_path: str) -> str:
    result = ocr.ocr(image_path, cls=True)
    if not result or not result[0]:
        return ""
    text = ' '.join([line[1][0] for line in result[0]])
    return text
```

### Phase 2: Rule-based Classifier (1 ngày)

```python
# /app/backend/rule_classifier.py
DOCUMENT_RULES = {
    "GCN": [
        "giấy chứng nhận quyền sử dụng đất",
        "cộng hòa xã hội chủ nghĩa việt nam",
        "quyền sở hữu nhà ở"
    ],
    "BMT": [
        "bản mô tả ranh giới",
        "mốc giới thửa đất",
        "vị trí ranh giới"
    ],
    # ... 50+ types
}

def classify_by_rules(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    
    for doc_type, keywords in DOCUMENT_RULES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[doc_type] = score / len(keywords)
    
    if not scores:
        return {"type": "UNKNOWN", "confidence": 0.0}
    
    best_type = max(scores, key=scores.get)
    confidence = scores[best_type]
    
    return {
        "type": best_type,
        "confidence": confidence,
        "method": "rules"
    }
```

### Phase 3: Integrate với hiện tại (1 ngày)

```python
# /app/backend/server.py
from ocr_engine import extract_text
from rule_classifier import classify_by_rules

async def analyze_document_hybrid(image_base64: str):
    # Step 1: Try OCR + Rules (FREE)
    image_bytes = base64.b64decode(image_base64)
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.write(image_bytes)
    temp_file.close()
    
    try:
        # OCR
        text = extract_text(temp_file.name)
        
        # Rules
        result = classify_by_rules(text)
        
        # Step 2: Fallback to GPT if low confidence
        if result["confidence"] < 0.7:
            result = await analyze_document_with_vision(image_base64)
            result["method"] = "gpt_fallback"
        
        return result
    finally:
        os.unlink(temp_file.name)
```

---

## 💰 Cost Savings Projection

### Scenario: Văn phòng 500 hồ sơ/ngày

**Hiện tại (GPT-4 full)**:
```
500 hồ sơ × 10 ảnh = 5,000 ảnh/ngày
5,000 × $0.002 = $10/ngày
$10 × 22 = $220/tháng
```

**Sau khi dùng Hybrid**:
```
4,500 ảnh qua OCR: FREE
500 ảnh qua GPT: 500 × $0.002 = $1/ngày
$1 × 22 = $22/tháng

TIẾT KIỆM: $198/tháng (90%)
Tiết kiệm năm: $2,376 🎉
```

---

## 🎯 Kết luận

### Khuyến nghị #1: **HYBRID APPROACH** ⭐

**Lý do**:
1. ✅ Tiết kiệm 90% chi phí
2. ✅ Độ chính xác vẫn cao (88-94%)
3. ✅ Implementation đơn giản (3 ngày)
4. ✅ Không phụ thuộc hoàn toàn API bên ngoài
5. ✅ Scalable

**Chi phí**:
- < 1K ảnh/ngày: $4-5/tháng
- 1-5K ảnh/ngày: $10-25/tháng
- > 5K ảnh/ngày: Consider self-host

### Roadmap:

```
Week 1: Implement PaddleOCR + Rule-based
Week 2: Testing & tuning rules
Week 3: Deploy và monitor
Week 4: Fine-tune rules dựa vào real data

Expected savings: 85-90%
Expected accuracy: 88-94% (vs 95-98% hiện tại)
Trade-off: Acceptable!
```

Bạn có muốn tôi implement phương án Hybrid này không? 🚀
