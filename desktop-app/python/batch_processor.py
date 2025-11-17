#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Document Processor - Multi-Image Analysis
Supports 2 modes:
- Mode 1: Fixed batch size (5 images per batch)
- Mode 2: Smart batching (group by document boundaries)
"""

import sys
import os
import json
import base64
import re
import requests
from PIL import Image
import io

# Import centralized error handler
try:
    from error_handler import (
        handle_error, 
        handle_success, 
        get_error_type_from_status,
        print_error_response
    )
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    print("[WARNING] error_handler not available - using legacy error handling", file=sys.stderr)

# Import existing engines and prompts
from ocr_engine_gemini_flash import (
    resize_image_smart, 
    parse_gemini_response,
    get_classification_prompt,
    get_classification_prompt_lite
)

# Import Tesseract+Text classifier
try:
    from tesseract_text_classifier import process_image as tesseract_text_process
    TESSERACT_TEXT_AVAILABLE = True
except ImportError:
    TESSERACT_TEXT_AVAILABLE = False
    print("[WARNING] tesseract_text_classifier not available", file=sys.stderr)


def adapt_prompt_for_multi_image(single_image_prompt, batch_size):
    """
    Adapt single-image prompt to multi-image batch context
    
    Changes:
    1. Add multi-image context introduction
    2. Add document grouping instructions
    3. Change output format from single result to documents array
    4. Add page indexing (0-indexed)
    5. Emphasize MUST return ALL pages
    """
    
    # Use % formatting to avoid f-string issues with JSON examples
    multi_image_intro = """🎯 BATCH ANALYSIS - %d TRANG SCAN

Bạn đang phân tích %d trang scan tài liệu đất đai Việt Nam.
Các trang này có thể thuộc 1 hoặc nhiều tài liệu khác nhau.

🚨 QUAN TRỌNG NHẤT - BATCH MODE vs SINGLE-FILE MODE:
Trong BATCH MODE này, bạn KHÔNG phải single-file classifier!
- ❌ ĐỪNG trả về "UNKNOWN" cho continuation pages
- ✅ Bạn PHẢI tự GOM continuation pages vào document trước
- ✅ Bạn có context từ nhiều pages → Hãy tận dụng!

VÍ DỤ:
Page 0: "THÔNG BÁO THUẾ" → Start TBT document
Page 1: "ĐIỀU 1" → TBT continuation → ADD vào pages của TBT
Page 2: "III. TÍNH THUẾ" + bảng → TBT continuation → ADD vào pages của TBT

Result: {{"type": "TBT", "pages": [0,1,2]}} ✅

KHÔNG LÀM (single-file style):
Result: 
  {{"type": "TBT", "pages": [0]}},
  {{"type": "UNKNOWN", "pages": [1,2]}} ❌ SAI!

NHIỆM VỤ:
1. Xác định có BAO NHIÊU tài liệu khác nhau trong %d trang này
2. Nhóm các trang theo tài liệu (pages array)
3. Phân loại loại tài liệu của từng nhóm
4. Trích xuất metadata (ngày cấp cho GCN, màu sắc, v.v.)

DẤU HIỆU NHẬN BIẾT:

TRANG 1 CỦA TÀI LIỆU (New Document):
- Có TIÊU ĐỀ CHÍNH ở TOP 30%% (đầu trang)
- Cỡ chữ LỚN, IN HOA, căn giữa
- Có quốc huy (đối với GCN)
- Khác biệt rõ về format/màu sắc so với trang trước

TRANG TIẾP NỐI (Continuation - Trang 2, 3, 4...):
- KHÔNG có tiêu đề chính ở đầu
- Chỉ có section headers: "II.", "III.", "ĐIỀU 2", "PHẦN II"
- Cùng format/màu sắc với trang trước
- Nội dung liên tục (điều khoản, chữ ký, bảng biểu)

🚨 QUAN TRỌNG - NHẬN DIỆN CONTINUATION PAGES:
Các dấu hiệu sau = CONTINUATION (trang tiếp theo, KHÔNG phải document mới):
1. Section headers với số: "II.", "III.", "IV.", "V.", "ĐIỀU 2", "ĐIỀU 3", "PHẦN II", "MỤC III"
2. Bảng biểu với số phân cấp: "4.1", "4.2", "4.2.1", "4.2.2", "(1.1)", "(2.1.3)"
3. Text body tiếp nối: "...tiếp theo...", "...như sau:", danh sách bullet points
4. Chữ ký/con dấu ở cuối trang
5. Không có header chính thức (quốc huy, cơ quan ban hành)
6. **"LỜI CHỨNG CỦA CÔNG CHỨNG VIÊN"** → Trang chữ ký công chứng (cuối document)
7. **Danh sách người ký, con dấu công chứng** → Trang cuối document

🚨 ĐẶC BIỆT - TRANG CÔNG CHỨNG (KHÔNG phải document mới):
Nếu trang có:
- "LỜI CHỨNG CỦA CÔNG CHỨNG VIÊN"
- "CÔNG CHỨNG VIÊN"
- Con dấu công chứng (hồng/đỏ)
- Danh sách chữ ký các Ông/Bà
- Văn phòng công chứng

→ Đây là TRANG CUỐI (signature page) của document
→ KHÔNG phải document mới
→ GOM VÀO document trước (TTHGD, PCTSVC, HDCQ, HDUQ, v.v.)

VÍ DỤ ĐÚNG:
Page 0: "THỎA THUẬN HỘ GIA ĐÌNH" → TTHGD
Page 1-3: Nội dung thỏa thuận → TTHGD continuation
Page 4: "LỜI CHỨNG CỦA CÔNG CHỨNG VIÊN" + danh sách → TTHGD continuation (signature page)
Page 5: Con dấu, chữ ký → TTHGD continuation

Result: {{"type": "TTHGD", "pages": [0,1,2,3,4,5]}} ✅

KHÔNG LÀM:
  {{"type": "TTHGD", "pages": [0,1,2,3]}},
  {{"type": "GTLQ", "pages": [4,5]}}  ❌ SAI!

VÍ DỤ CONTINUATION - PHẢI GOM VÀO DOCUMENT TRƯỚC:
✅ "III. TÍNH THUẾ CỦA CƠ QUAN THUẾ" + bảng 4.1, 4.2
   → Section header với số La Mã
   → Bảng biểu phân cấp
   → Đây là continuation của document trước (có thể là TBT, HDCQ, etc.)
   → KHÔNG classify thành UNKNOWN
   → GOM VÀO document có trang trước đó
   
   VÍ DỤ CỤ THỂ:
   Page 4 (index 4): "THÔNG BÁO THUẾ" (title) → TBT
   Page 5 (index 5): "ĐIỀU 1: ..." → TBT continuation
   Page 6 (index 6): "III. TÍNH THUẾ" + bảng 4.1 → TBT continuation ✅ (KHÔNG phải UNKNOWN)
   
   Result: {{"type": "TBT", "pages": [4, 5, 6], ...}}

✅ "ĐIỀU 2: NỘI DUNG THỎA THUẬN PHÂN CHIA"
   → Section header
   → Continuation của TTHGD hoặc PCTSVC
   → GOM VÀO document trước

✅ Trang chỉ có bảng biểu (không có title)
   → Continuation
   → GOM VÀO document trước

✅ Trang có "1.1 Trường hợp...", "1.2 Trường hợp..." (numbered list)
   → Continuation với structured content
   → GOM VÀO document trước

❌ SAI - Classify continuation thành UNKNOWN:
Page 5: "THÔNG BÁO THUẾ" (title)
Page 6: "III. TÍNH THUẾ" + bảng
→ AI classify:
  {{"type": "TBT", "pages": [5]}},
  {{"type": "UNKNOWN", "pages": [6]}}  ❌ SAI!
→ ĐÚNG:
  {{"type": "TBT", "pages": [5, 6]}}  ✅

RANH GIỚI GIỮA CÁC TÀI LIỆU:
- Thay đổi rõ rệt: màu giấy (hồng → trắng), format (có quốc huy → không có)
- Xuất hiện tiêu đề chính mới ở TOP
- Thay đổi hoàn toàn về layout

🎯 DẤU HIỆU VISUAL - CÙNG DOCUMENT (CỰC KỲ QUAN TRỌNG):

**1. DẤU GIÁP LAI (Overlapping Stamp):**
Nếu thấy CON DẤU ĐỎ/HỒNG bị CẮT NGANG qua nhiều pages:
- Page 1: Có PHẦN TRÊN của con dấu (top half)
- Page 2: Có PHẦN GIỮA của con dấu (middle)
- Page 3: Có PHẦN DƯỚI của con dấu (bottom half)

→ Đây là DẤU GIÁP LAI!
→ 3-4 pages này được đóng dấu CÙNG LÚC (giấy chồng lên nhau)
→ **BẮT BUỘC CÙNG 1 DOCUMENT**
→ PHẢI GOM TẤT CẢ pages có partial stamp vào 1 document

VÍ DỤ:
Page 0: "THỎA THUẬN HỘ GIA ĐÌNH" + phần trên con dấu đỏ (⬆️ top half)
Page 1: Text body + phần giữa con dấu đỏ (⬌ middle)
Page 2: Text body + phần giữa con dấu đỏ (⬌ middle)
Page 3: "LỜI CHỨNG..." + phần dưới con dấu đỏ (⬇️ bottom half)

→ **4 pages có cùng con dấu bị cắt** → CÙNG 1 DOCUMENT!
→ Result: {{"type": "TTHGD", "pages": [0,1,2,3]}} ✅

**2. DẤU HOÀN CHỈNH (Complete Stamp):**
Nếu page có con dấu HOÀN CHỈNH (full circle, không bị cắt):
→ Đây có thể là trang ĐỘC LẬP (single document)
→ HOẶC trang cuối của document

**3. KHÔNG CÓ DẤU:**
Nếu page không có con dấu:
→ Có thể là trang giữa document
→ Check title và continuation patterns

🚨 NGUYÊN TẮC DẤU GIÁP LAI:
- Partial stamp (bị cắt) = **STRONG SIGNAL** cùng document
- Ưu tiên cao hơn cả title/content analysis
- Nếu thấy dấu giáp lai → GOM NGAY, không cần nghi ngờ

---

""" % (batch_size, batch_size, batch_size)

    unknown_rules = """

⚠️ QUAN TRỌNG - KHI NÀO TRẢ VỀ "UNKNOWN":
CHỈ trả về "UNKNOWN" khi:
1. Trang thực sự không có tiêu đề VÀ không match continuation patterns
2. Title không thuộc 98 loại VÀ không phải continuation
3. Trang hoàn toàn trống hoặc không đọc được

❌ KHÔNG trả về "UNKNOWN" cho:
- Trang có section headers (III., ĐIỀU 2) → Continuation, gom vào doc trước
- Trang có bảng biểu structured → Continuation, gom vào doc trước
- Trang có text liên tục với trang trước → Continuation, gom vào doc trước

🎯 NGUYÊN TẮC: Khi nghi ngờ → Gom vào document trước (safer than creating new UNKNOWN doc)

⚠️ ĐẶC BIỆT - GOM CONTINUATION THAY VÌ TRẢ VỀ UNKNOWN:
NẾU trang không có title NHƯNG có dấu hiệu continuation:
- Section headers: "II.", "III.", "ĐIỀU X"
- Bảng biểu: tables với numbers
- Text body: tiếp tục content

→ KHÔNG tạo document UNKNOWN riêng
→ GOM VÀO document trước đó
→ Extend "pages" array của document trước

VÍ DỤ ĐÚNG:
Page 0: "THÔNG BÁO THUẾ" (title) → TBT
Page 1: "ĐIỀU 1: ..." (section) → TBT continuation
Page 2: "III. TÍNH THUẾ" + bảng (section + table) → TBT continuation

Result: {{"type": "TBT", "pages": [0, 1, 2], ...}} ✅

KHÔNG LÀM:
  {{"type": "TBT", "pages": [0, 1]}},
  {{"type": "UNKNOWN", "pages": [2]}}  ❌

CHỈ TRẢ VỀ "UNKNOWN" KHI:
- Trang hoàn toàn lạ (không có title, không có continuation patterns)
- Title thực sự không thuộc 98 loại (VD: "BẢN GIẢI TRÌNH", "VĂN BẢN YÊU CẦU")
- Trang trống, scan lỗi, không đọc được

---

"""

    # GCN-specific metadata rules (CRITICAL!)
    gcn_metadata_rules = """

🚨 CỰC KỲ QUAN TRỌNG - GCN METADATA (BẮT BUỘC):

Khi classify bất kỳ page nào là "GCN", bạn PHẢI:

**1. TÌM MÀU SẮC (color):**
- Quan sát màu nền giấy
- Màu đỏ/cam (red/orange) → "color": "red"
- Màu hồng (pink) → "color": "pink"  
- Màu trắng hoặc không rõ → "color": "unknown"

**2. TÌM NGÀY CẤP (issue_date) - BẮT BUỘC:**
- ⚠️ KHÔNG BAO GIỜ bỏ qua bước này!
- Tìm ở trang 2 (nếu GCN A3) hoặc trang 1 bottom
- Text gần: "Ngày cấp", "Cấp ngày", "TM. UBND", chữ ký
- Có thể viết TAY (handwritten)

**Formats phổ biến:**
- "DD/MM/YYYY" → Return: "27/10/2021"
- "Ngày 25 tháng 8 năm 2010" → Convert & return: "25/8/2010"
- "MM/YYYY" (nếu mờ) → Return: "02/2012"
- "YYYY" (nếu rất mờ) → Return: "2012"
- Không tìm thấy → Return: null

**Confidence levels:**
- "full": Đọc được đầy đủ DD/MM/YYYY
- "partial": Chỉ MM/YYYY
- "year_only": Chỉ YYYY
- "not_found": Không tìm thấy

**3. METADATA RESPONSE - BẮT BUỘC:**

✅ VÍ DỤ ĐÚNG (Có ngày cấp):
{{
  "type": "GCN",
  "pages": [5, 6],
  "confidence": 0.98,
  "reasoning": "GCN màu hồng, quốc huy, ngày cấp 27/10/2021",
  "metadata": {{
    "color": "pink",
    "issue_date": "27/10/2021",
    "issue_date_confidence": "full"
  }}
}}

✅ VÍ DỤ ĐÚNG (Không tìm thấy date):
{{
  "type": "GCN",
  "pages": [0],
  "confidence": 0.95,
  "reasoning": "GCN trang 1, màu hồng, chưa có ngày cấp",
  "metadata": {{
    "color": "pink",
    "issue_date": null,
    "issue_date_confidence": "not_found"
  }}
}}

❌ SAI - THIẾU METADATA:
{{
  "type": "GCN",
  "pages": [5, 6],
  "metadata": {{}}  // ❌ EMPTY! Must have color & issue_date!
}}

❌ SAI - KHÔNG TÌM DATE:
{{
  "type": "GCN",
  "pages": [5, 6],
  "metadata": {{
    "color": "pink"
    // ❌ MISSING issue_date fields!
  }}
}}

⚠️ NHỚ: Mọi GCN document PHẢI có metadata với:
- "color": "red" | "pink" | "unknown"
- "issue_date": "DD/MM/YYYY" | null
- "issue_date_confidence": "full" | "partial" | "year_only" | "not_found"

---

"""

    output_format = f"""

---

🎯 OUTPUT FORMAT - BẮT BUỘC:

🚨🚨🚨 CRITICAL - MUST USE "documents" ARRAY 🚨🚨🚨
Your response MUST be a JSON object with a "documents" key containing an array.
DO NOT return a single document object at the root level!

CORRECT FORMAT (REQUIRED):
{{
  "documents": [
    {{
      "type": "HDCQ",
      "pages": [0, 1, 2, 3, 4],
      "confidence": 0.95,
      "reasoning": "5 trang đầu cùng format, trang 0 có tiêu đề 'HỢP ĐỒNG CHUYỂN NHƯỢNG', trang 1-4 là continuation pages với ĐIỀU 2, ĐIỀU 3",
      "metadata": {{}}
    }},
    {{
      "type": "GCN",
      "pages": [5, 6],
      "confidence": 0.98,
      "reasoning": "Trang 5-6 là GCN màu hồng, có quốc huy, tìm thấy ngày cấp ở trang 6",
      "metadata": {{
        "color": "pink",
        "issue_date": "27/10/2021",
        "issue_date_confidence": "full"
      }}
    }},
    {{
      "type": "UNKNOWN",
      "pages": [7, 8, 9],
      "confidence": 0.3,
      "reasoning": "3 trang cuối không rõ ràng, không có tiêu đề, không match 98 loại",
      "metadata": {{}}
    }}
  ]
}}

❌ WRONG FORMAT (DO NOT USE):
{{
  "type": "HDCQ",
  "pages": [0, 1, 2],
  "confidence": 0.95,
  "reasoning": "...",
  "metadata": {{}}
}}
This is WRONG! You must wrap it in "documents" array!

🚨 CỰC KỲ QUAN TRỌNG - BẮT BUỘC RETURN TẤT CẢ {batch_size} PAGES:
- Bạn PHẢI assign MỌI page (0 đến {batch_size-1}) vào 1 document
- Nếu page không rõ → assign vào document type "UNKNOWN"
- KHÔNG BAO GIỜ bỏ qua page nào
- Tổng số pages trong "pages" arrays = {batch_size}

VÍ DỤ ĐÚNG ({batch_size} pages):
- Document 1: pages [0,1,2,3,4] (5 pages)
- Document 2: pages [5,6,7,8] (4 pages)
- Document 3: pages [9,10,...,{batch_size-1}] ({batch_size-9} pages)
→ Total: {batch_size} pages ✅

VÍ DỤ SAI:
- Document 1: pages [0,1,2] (3 pages only)
- Document 2: pages [5,6] (2 pages, SKIP pages 3-4!)
→ Total: 5 pages ❌ (Missing pages 3,4,7,8,...,{batch_size-1})

INDEXING:
- pages dùng 0-indexed (trang đầu tiên = 0, trang cuối = {batch_size-1})
- Nếu chỉ có 1 document → vẫn trả về array với 1 phần tử
"""

    # Combine: intro + original rules + unknown rules + GCN metadata + output format
    full_multi_prompt = multi_image_intro + single_image_prompt + unknown_rules + gcn_metadata_rules + output_format
    
    return full_multi_prompt


def get_multi_image_prompt_full(batch_size):
    """Get FULL prompt (Flash Full rules) for multi-image batch"""
    single_prompt = get_classification_prompt()
    return adapt_prompt_for_multi_image(single_prompt, batch_size)


def get_multi_image_prompt_lite(batch_size):
    """Get LITE prompt (Flash Lite rules) for multi-image batch"""
    single_prompt = get_classification_prompt_lite()
    return adapt_prompt_for_multi_image(single_prompt, batch_size)


def encode_image_base64(image_path, max_width=1500, max_height=2100):
    """Encode image to base64 with smart resize"""
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize
        resized_img, resize_info = resize_image_smart(img, max_width, max_height)
        
        # Encode to base64 with quality 85 (balance between size and OCR accuracy)
        buffer = io.BytesIO()
        resized_img.save(buffer, format='JPEG', quality=85, optimize=True)
        img_bytes = buffer.getvalue()
        encoded = base64.b64encode(img_bytes).decode('utf-8')
        
        return encoded, resize_info
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}", file=sys.stderr)
        return None, None


def batch_classify_tesseract_text(image_paths, api_key, last_known_type=None):
    """
    NEW MODE: Tesseract OCR + Gemini Text Classification
    
    Approach:
    1. Extract text from each image using Tesseract (local, fast)
    2. Send only text to Gemini Text API for classification
    
    Benefits:
    - Faster: No need to upload large base64 images
    - Cheaper: Text API is 10-20x cheaper than Vision API
    - Less 503 errors: Smaller requests
    - Can handle larger batches: 20-30 files instead of 5
    
    Args:
        image_paths: List of image file paths
        api_key: Gemini API key
        last_known_type: Not used in this mode (each file processed independently)
    
    Returns:
        List of classification results
    """
    if not TESSERACT_TEXT_AVAILABLE:
        print("[ERROR] Tesseract+Text mode not available. Install pytesseract.", file=sys.stderr)
        return [{
            'type': 'UNKNOWN',
            'short_code': 'UNKNOWN',
            'confidence': 0.0,
            'error': 'Tesseract not available',
            'method': 'error'
        } for _ in image_paths]
    
    print(f"\n[Tesseract+Text Mode] Processing {len(image_paths)} images...", file=sys.stderr)
    
    results = []
    
    for i, img_path in enumerate(image_paths):
        try:
            print(f"[{i+1}/{len(image_paths)}] Processing: {os.path.basename(img_path)}", file=sys.stderr)
            
            # Process with Tesseract + Gemini Text
            result = tesseract_text_process(img_path, api_key)
            
            # Add pages info (each image is a separate "document" in this mode)
            result['pages'] = [i]
            
            results.append(result)
            
            print(f"  ✅ Result: {result['short_code']} (confidence: {result['confidence']*100:.1f}%)", file=sys.stderr)
            
        except Exception as e:
            print(f"  ❌ Error: {e}", file=sys.stderr)
            results.append({
                'type': 'UNKNOWN',
                'short_code': 'UNKNOWN',
                'confidence': 0.0,
                'pages': [i],
                'error': str(e),
                'method': 'tesseract_text'
            })
    
    print(f"\n[Tesseract+Text Mode] Completed {len(results)}/{len(image_paths)} classifications", file=sys.stderr)
    
    return results




def batch_classify_fixed(image_paths, api_key, engine_type='gemini-flash', batch_size=8, last_known_type=None):
    """
    Phương án 1: Fixed Batch Size với SEQUENTIAL METADATA
    
    Args:
        image_paths: List of file paths
        api_key: Google API key
        engine_type: 'gemini-flash', 'gemini-flash-lite', or 'gemini-flash-hybrid'
        batch_size: Files per batch
        last_known_type: Metadata từ file cuối batch trước {short_code, confidence, has_title}
    
    Strategy:
        - Batch 1: Process files 0-4, return lastKnown từ file 4
        - Batch 2: Process files 5-9 WITH lastKnown từ file 4
          * File 5 có title → Bỏ qua lastKnown, dùng title mới
          * File 5 không có title → Áp dụng sequential từ lastKnown
        - No overlap needed → 0% overhead!
    """
    
    # Determine model and prompt based on engine type
    if engine_type == 'gemini-flash-lite':
        model_name = 'gemini-2.5-flash-lite'
        prompt_getter = get_multi_image_prompt_lite
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"⚡ BATCH MODE: Fixed ({batch_size} files, NO overlap) + Flash LITE", file=sys.stderr)
        print(f"   Model: {model_name}", file=sys.stderr)
        print("   Prompt: Lite (simplified, 60% crop rules)", file=sys.stderr)
        print("   Metadata: Sequential naming from previous batch", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
    elif engine_type == 'gemini-flash-hybrid':
        model_name = 'gemini-2.5-flash-lite'  # Start with Lite for hybrid
        prompt_getter = get_multi_image_prompt_lite
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"🔄 BATCH MODE: Fixed ({batch_size} files, NO overlap) + HYBRID", file=sys.stderr)
        print("   Strategy: Two-tier (Lite → Full if low confidence)", file=sys.stderr)
        print(f"   Model (Tier 1): {model_name}", file=sys.stderr)
        print("   Metadata: Sequential naming from previous batch", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
    else:  # gemini-flash (default)
        model_name = 'gemini-2.5-flash'
        prompt_getter = get_multi_image_prompt_full
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"🤖 BATCH MODE: Fixed ({batch_size} files, NO overlap) + Flash FULL", file=sys.stderr)
        print(f"   Model: {model_name}", file=sys.stderr)
        print("   Prompt: Full (complete 98-rule classification)", file=sys.stderr)
        print("   Metadata: Sequential naming from previous batch", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
    
    if last_known_type:
        print(f"\n📌 Received lastKnown from previous batch:", file=sys.stderr)
        print(f"   Type: {last_known_type.get('short_code')}", file=sys.stderr)
        print(f"   Confidence: {last_known_type.get('confidence', 0):.0%}", file=sys.stderr)
        print(f"   Has title: {last_known_type.get('has_title', False)}", file=sys.stderr)
    
    all_results = []
    processed_files = set()
    batch_num = 0
    current_idx = 0
    current_last_known = last_known_type  # Start with provided lastKnown
    
    while current_idx < len(image_paths):
        batch_num += 1
        
        # Calculate batch range WITHOUT overlap
        batch_start = current_idx
        batch_end = min(len(image_paths), current_idx + batch_size)
        batch_paths = image_paths[batch_start:batch_end]
        
        print(f"\n📦 Batch {batch_num}: Files {batch_start}-{batch_end-1} ({len(batch_paths)} images)", file=sys.stderr)
        
        for i, path in enumerate(batch_paths):
            print(f"   [{i}] {os.path.basename(path)}", file=sys.stderr)
        
        # Encode all images in batch
        print(f"🖼️ Encoding {len(batch_paths)} images...", file=sys.stderr)
        encoded_images = []
        for path in batch_paths:
            encoded, resize_info = encode_image_base64(path)
            if encoded:
                encoded_images.append(encoded)
                print(f"   ✅ {os.path.basename(path)}: {resize_info.get('original_size', 'N/A')} → {resize_info.get('new_size', 'N/A')}", file=sys.stderr)
            else:
                print(f"   ❌ Failed to encode {os.path.basename(path)}", file=sys.stderr)
        
        if not encoded_images:
            print(f"❌ No valid images in batch {batch_num}", file=sys.stderr)
            continue
        
        # Build multi-image payload
        parts = [{"text": prompt_getter(len(batch_paths))}]
        for img_data in encoded_images:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_data
                }
            })
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "topK": 10,
                "maxOutputTokens": 8000,  # Large enough for 20 documents × 400 tokens each
                "responseMimeType": "application/json"  # Force JSON output
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
        }
        
        # Call Gemini API with retry logic
        print(f"📡 Sending batch request to {model_name}...", file=sys.stderr)
        print(f"   Batch size: {len(batch_paths)} files", file=sys.stderr)
        # Calculate approximate request size
        import json
        payload_size_mb = len(json.dumps(payload)) / (1024 * 1024)
        print(f"   Request size: ~{payload_size_mb:.2f} MB", file=sys.stderr)
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        max_retries = 3
        retry_delay = 10  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(api_url, json=payload, timeout=120)
                response.raise_for_status()
                result_data = response.json()
                
                # Reset all error counters on success
                if ERROR_HANDLER_AVAILABLE:
                    handle_success()
                
                break  # Success, exit retry loop
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                error_type = get_error_type_from_status(status_code) if ERROR_HANDLER_AVAILABLE else str(status_code)
                
                if ERROR_HANDLER_AVAILABLE:
                    # Use centralized error handler
                    context = {
                        "batch_num": batch_num,
                        "batch_size": batch_size,
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    }
                    error_info = handle_error(error_type, e, context)
                    
                    # Check if should stop
                    if error_info["should_stop"]:
                        print(f"❌ Stopping due to critical error: {status_code}", file=sys.stderr)
                        if error_info["error_response"]:
                            print_error_response(error_info["error_response"])
                        sys.exit(1)
                    
                    # Check if should retry
                    if error_info["should_retry"] and attempt < max_retries - 1:
                        wait_time = error_info["wait_time"]
                        print(f"   Retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        if batch_size > 5 and status_code in [500, 503]:
                            print(f"   💡 Tip: Try reducing Smart batch size to 5-8 in Settings", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries reached or should not retry
                        if error_info["is_critical"] and error_info["error_response"]:
                            print_error_response(error_info["error_response"])
                            sys.exit(1)
                        raise
                else:
                    # Legacy error handling (fallback)
                    if status_code in [500, 503]:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2 ** attempt)
                            print(f"⚠️ {status_code} Server Error, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            raise
                    elif status_code == 429:
                        if attempt < max_retries - 1:
                            wait_time = 60 * (2 ** attempt)
                            print(f"⚠️ 429 Rate Limit, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            raise
                    else:
                        print(f"❌ HTTP {status_code} Error: {e}", file=sys.stderr)
                        raise
            except requests.exceptions.Timeout as e:
                # Timeout error
                if ERROR_HANDLER_AVAILABLE:
                    context = {"batch_num": batch_num, "batch_size": batch_size, "attempt": attempt + 1}
                    error_info = handle_error("timeout", e, context)
                    
                    if error_info["should_retry"] and attempt < max_retries - 1:
                        wait_time = error_info["wait_time"]
                        print(f"   Retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        if error_info["error_response"]:
                            print_error_response(error_info["error_response"])
                        raise
                else:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⚠️ Timeout error, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
            except requests.exceptions.RequestException as e:
                # Network errors
                if ERROR_HANDLER_AVAILABLE:
                    context = {"batch_num": batch_num, "batch_size": batch_size, "attempt": attempt + 1}
                    error_info = handle_error("network", e, context)
                    
                    if error_info["should_retry"] and attempt < max_retries - 1:
                        wait_time = error_info["wait_time"]
                        print(f"   Retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        if error_info["error_response"]:
                            print_error_response(error_info["error_response"])
                        raise
                else:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⚠️ Network error, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
        
        # Add delay between batches to avoid rate limiting
        if batch_num < ((len(image_paths) + batch_size - 1) // batch_size):
            import time
            inter_batch_delay = 5  # 5 seconds between batches
            print(f"⏸️ Waiting {inter_batch_delay}s before next batch...", file=sys.stderr)
            time.sleep(inter_batch_delay)
        
        try:
            
            print(f"📊 Response status: {response.status_code}", file=sys.stderr)
            
            # Debug: Check finish reason and safety
            if 'candidates' in result_data and len(result_data['candidates']) > 0:
                candidate = result_data['candidates'][0]
                finish_reason = candidate.get('finishReason', 'UNKNOWN')
                print(f"🔍 Finish reason: {finish_reason}", file=sys.stderr)
                
                if finish_reason == 'MAX_TOKENS':
                    print("⚠️ WARNING: Response truncated due to MAX_TOKENS!", file=sys.stderr)
                    print("   Some pages may be missing from response", file=sys.stderr)
            
            # Parse response
            if 'candidates' in result_data and len(result_data['candidates']) > 0:
                candidate = result_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        response_text = parts[0]['text']
                        
                        print(f"📄 Raw response preview: {response_text[:200]}...", file=sys.stderr)
                        
                        # DEBUG: Log full response to understand parsing issues
                        print(f"\n🔍 DEBUG - Full response length: {len(response_text)} chars", file=sys.stderr)
                        if len(response_text) < 500:
                            print(f"📄 Full response (short):", file=sys.stderr)
                            print(response_text, file=sys.stderr)
                        
                        # Check for common issues
                        has_documents = '"documents"' in response_text
                        has_json_markers = '```json' in response_text
                        starts_with_brace = response_text.strip().startswith('{')
                        
                        print(f"   Has 'documents' key: {has_documents}", file=sys.stderr)
                        print(f"   Has ```json markers: {has_json_markers}", file=sys.stderr)
                        print(f"   Starts with brace: {starts_with_brace}", file=sys.stderr)
                        
                        # Extract JSON from response - try multiple patterns
                        json_match = re.search(r'\{[\s\S]*"documents"[\s\S]*\}', response_text)
                        if not json_match:
                            # Try finding JSON with triple backticks
                            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text)
                            if json_match:
                                response_text = json_match.group(1)
                            else:
                                # Try finding any JSON object
                                json_match = re.search(r'(\{[\s\S]*\})', response_text)
                                if json_match:
                                    response_text = json_match.group(1)
                        else:
                            response_text = json_match.group(0)
                        
                        if response_text:
                            try:
                                batch_result = json.loads(response_text)
                                
                                # Check if documents key exists
                                if 'documents' not in batch_result or not isinstance(batch_result.get('documents'), list):
                                    print(f"⚠️ Batch {batch_num} WARNING: No 'documents' array in response!", file=sys.stderr)
                                    print(f"   Response keys: {list(batch_result.keys())}", file=sys.stderr)
                                    
                                    # FALLBACK: Check if response is a single document (LLM returned wrong format)
                                    if 'type' in batch_result and 'pages' in batch_result:
                                        print(f"   🔄 Auto-fixing: LLM returned single document format instead of array", file=sys.stderr)
                                        print(f"   Wrapping into documents array...", file=sys.stderr)
                                        batch_result = {
                                            'documents': [batch_result]
                                        }
                                    else:
                                        print(f"   ❌ Cannot auto-fix: Response format unrecognized", file=sys.stderr)
                                        print(f"   This batch will fallback to individual processing", file=sys.stderr)
                                        raise ValueError("Missing 'documents' array in response")
                            
                                print(f"✅ Batch {batch_num} complete:", file=sys.stderr)
                                
                                # Validate: Check if all pages are covered
                                total_pages_in_batch = len(batch_paths)
                                pages_returned = set()
                                
                                for doc in batch_result.get('documents', []):
                                    doc_type = doc.get('type', 'UNKNOWN')
                                    pages = doc.get('pages', [])
                                    confidence = doc.get('confidence', 0)
                                    print(f"   📄 {doc_type}: {len(pages)} pages, confidence {confidence:.0%}", file=sys.stderr)
                                    
                                    # Collect all page indices
                                    for p in pages:
                                        pages_returned.add(p)
                                
                                # Check for missing pages
                                expected_pages = set(range(total_pages_in_batch))
                                missing_pages = expected_pages - pages_returned
                                
                                if missing_pages:
                                    print(f"   ⚠️ WARNING: AI didn't return {len(missing_pages)} pages: {sorted(missing_pages)}", file=sys.stderr)
                                    print("      These files will be processed by fallback", file=sys.stderr)
                                else:
                                    print(f"   ✅ All {total_pages_in_batch} pages accounted for", file=sys.stderr)
                                
                                # Map results back to original file paths WITH sequential naming
                                batch_results_with_sequential = []
                                
                                for doc in batch_result.get('documents', []):
                                    doc_type = doc.get('type', 'UNKNOWN')
                                    doc_confidence = doc.get('confidence', 0.5)
                                    doc_reasoning = doc.get('reasoning', '')
                                    doc_metadata = doc.get('metadata', {})
                                    
                                    # DEBUG: Log metadata for GCN
                                    if doc_type == 'GCN':
                                        print(f"\n🔍 DEBUG - GCN Metadata:", file=sys.stderr)
                                        print(f"   Type: {doc_type}", file=sys.stderr)
                                        print(f"   Metadata: {doc_metadata}", file=sys.stderr)
                                        print(f"   Has color: {'color' in doc_metadata}", file=sys.stderr)
                                        print(f"   Has issue_date: {'issue_date' in doc_metadata}", file=sys.stderr)
                                        if doc_metadata:
                                            print(f"   color value: {doc_metadata.get('color', 'MISSING')}", file=sys.stderr)
                                            print(f"   issue_date value: {doc_metadata.get('issue_date', 'MISSING')}", file=sys.stderr)
                                        print(f"\n", file=sys.stderr)
                                    
                                    for page_idx in doc.get('pages', []):
                                        if page_idx < len(batch_paths):
                                            file_path = batch_paths[page_idx]
                                            file_name = os.path.basename(file_path)
                                            
                                            # Determine if this file has title (high confidence, not UNKNOWN)
                                            has_title = (doc_confidence >= 0.8 and doc_type != 'UNKNOWN')
                                            
                                            # Apply sequential naming logic
                                            final_type = doc_type
                                            final_confidence = doc_confidence
                                            applied_sequential = False
                                            
                                            # If file is UNKNOWN or low confidence AND we have lastKnown
                                            if (doc_type == 'UNKNOWN' or doc_confidence < 0.5) and current_last_known:
                                                final_type = current_last_known['short_code']
                                                final_confidence = current_last_known['confidence']
                                                applied_sequential = True
                                                print(f"   🔄 Sequential: {file_name} ({doc_type} {doc_confidence:.0%}) → {final_type}", file=sys.stderr)
                                            
                                            # Update lastKnown if this file has good classification
                                            if doc_type != 'UNKNOWN' and doc_confidence >= 0.7 and has_title:
                                                current_last_known = {
                                                    'short_code': doc_type,
                                                    'confidence': doc_confidence,
                                                    'has_title': True
                                                }
                                                print(f"   📌 Updated lastKnown: {doc_type} ({doc_confidence:.0%})", file=sys.stderr)
                                            
                                            processed_files.add(file_path)
                                            batch_results_with_sequential.append({
                                                'file_path': file_path,
                                                'file_name': file_name,
                                                'short_code': final_type,
                                                'confidence': final_confidence,
                                                'reasoning': doc_reasoning,
                                                'metadata': doc_metadata,
                                                'method': 'batch_fixed',
                                                'batch_num': batch_num,
                                                'applied_sequential': applied_sequential,
                                                'original_classification': doc_type if applied_sequential else None
                                            })
                                
                                all_results.extend(batch_results_with_sequential)
                            except json.JSONDecodeError as je:
                                print(f"⚠️ JSON decode error in batch {batch_num}: {je}", file=sys.stderr)
                                print(f"   Response text: {response_text[:500]}...", file=sys.stderr)
                        else:
                            print(f"⚠️ No valid JSON in response for batch {batch_num}", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Batch {batch_num} error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        # Move to next batch (increment by batch_size, not batch_end)
        current_idx += batch_size
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✅ BATCH MODE 1 COMPLETE: {len(all_results)} files processed", file=sys.stderr)
    
    # Detect missing files
    all_input_files = set(image_paths)
    missing_files = all_input_files - processed_files
    
    if missing_files:
        print(f"⚠️ WARNING: {len(missing_files)} files were NOT processed by AI:", file=sys.stderr)
        for missing_file in sorted(missing_files):
            print(f"   ❌ {os.path.basename(missing_file)}", file=sys.stderr)
        print("   Possible causes: AI didn't return page indices, JSON parsing error", file=sys.stderr)
        print(f"\n🔄 FALLBACK: Processing {len(missing_files)} missing files individually...", file=sys.stderr)
        
        # Fallback: Process missing files with single-file tier1 scan
        for missing_file in sorted(missing_files):
            try:
                print(f"   🔄 Processing {os.path.basename(missing_file)}...", file=sys.stderr)
                result = quick_scan_tier1(missing_file, api_key)
                all_results.append({
                    'file_path': missing_file,
                    'file_name': os.path.basename(missing_file),
                    'short_code': result.get('short_code', 'UNKNOWN'),
                    'confidence': result.get('confidence', 0.5),
                    'reasoning': result.get('reasoning', 'Fallback single-file scan'),
                    'metadata': result.get('metadata', {}),
                    'method': 'batch_fallback',
                    'batch_num': 'fallback'
                })
                print(f"      ✅ {result.get('short_code', 'UNKNOWN')} ({result.get('confidence', 0):.0%})", file=sys.stderr)
            except Exception as e:
                print(f"      ❌ Error: {e}", file=sys.stderr)
                # Add as UNKNOWN if fallback also fails
                all_results.append({
                    'file_path': missing_file,
                    'file_name': os.path.basename(missing_file),
                    'short_code': 'UNKNOWN',
                    'confidence': 0.0,
                    'reasoning': f'Fallback failed: {str(e)}',
                    'metadata': {},
                    'method': 'batch_fallback_failed',
                    'batch_num': 'fallback'
                })
        
        print(f"✅ Fallback complete: {len(all_results)} total results (original + fallback)", file=sys.stderr)
    else:
        print(f"✅ All {len(all_input_files)} input files were successfully processed", file=sys.stderr)
    
    print(f"{'='*80}", file=sys.stderr)
    
    # Return results AND lastKnown for next batch
    return {
        'results': all_results,
        'last_known_type': current_last_known
    }


def quick_scan_tier1(image_path, api_key):
    """Quick scan với Tier 1 để detect document boundaries"""
    from ocr_engine_gemini_flash import classify_document_gemini_flash
    
    try:
        result = classify_document_gemini_flash(
            image_path=image_path,
            api_key=api_key,
            crop_top_percent=0.60,
            model_type='gemini-flash-lite',
            enable_resize=True,
            max_width=1500,
            max_height=2100
        )
        
        # ✅ POST-PROCESSING FIXES (same as process_document.py)
        short_code = result.get('short_code', 'UNKNOWN')
        reasoning_text = result.get('reasoning', '').upper()
        
        # Fix #1: PKTHS → GTLQ (when "KIỂM SOÁT" detected)
        if short_code == "PKTHS" and ("KIỂM SOÁT" in reasoning_text or "KIEM SOAT" in reasoning_text):
            print(f"🔧 Post-processing fix: PKTHS → GTLQ (detected 'KIỂM SOÁT')", file=sys.stderr)
            result['short_code'] = "GTLQ"
            result['reasoning'] = f"[AUTO-FIXED: PKTHS→GTLQ] {result.get('reasoning', '')}"
        
        # Fix #2: UNKNOWN → GTLQ (when GTLQ keywords detected)
        elif short_code == "UNKNOWN":
            gtlq_keywords = ["PHIẾU XIN LỖI", "HẸN LẠI NGÀY TRẢ KẾT QUẢ", "PHIẾU KIỂM SOÁT", 
                            "BỘ PHẬN TIẾP NHẬN", "GIẤY TIẾP NHẬN HỒ SƠ"]
            for keyword in gtlq_keywords:
                if keyword in reasoning_text:
                    print(f"🔧 Post-processing fix: UNKNOWN → GTLQ (detected '{keyword}')", file=sys.stderr)
                    result['short_code'] = "GTLQ"
                    result['confidence'] = 0.95
                    result['reasoning'] = f"[AUTO-FIXED: UNKNOWN→GTLQ] {result.get('reasoning', '')}"
                    break
        
        # Fix #3: BMT → HSKT (when "TRÍCH LỤC" or "BẢN ĐỒ" detected)
        elif short_code == "BMT":
            hskt_keywords = ["TRÍCH LỤC", "BẢN ĐỒ ĐỊA CHÍNH", "ĐO TÁCH", "CHỈNH LÝ"]
            for keyword in hskt_keywords:
                if keyword in reasoning_text:
                    print(f"🔧 Post-processing fix: BMT → HSKT (detected '{keyword}')", file=sys.stderr)
                    result['short_code'] = "HSKT"
                    result['reasoning'] = f"[AUTO-FIXED: BMT→HSKT] {result.get('reasoning', '')}"
                    break
        
        return result
    except Exception as e:
        print(f"Quick scan error for {image_path}: {e}", file=sys.stderr)
        return {'short_code': 'ERROR', 'confidence': 0}


def group_by_document(quick_results, file_paths):
    """
    Nhóm files thành documents dựa trên quick scan results
    Returns: List of document groups [[0,1,2], [3,4], [5,6,7,8], ...]
    """
    print("\n🧠 Analyzing document boundaries...", file=sys.stderr)
    
    groups = []
    current_group = [0]
    last_type = quick_results[0].get('short_code', 'UNKNOWN')
    
    for i in range(1, len(quick_results)):
        result = quick_results[i]
        short_code = result.get('short_code', 'UNKNOWN')
        confidence = result.get('confidence', 0)
        reasoning = result.get('reasoning', '').lower()
        
        # Check if this is a new document
        is_new_document = False
        
        # High confidence with clear title → New document
        if confidence >= 0.8 and short_code != 'UNKNOWN':
            is_new_document = True
            print(f"   📄 [{i}] New document detected: {short_code} ({confidence:.0%})", file=sys.stderr)
        
        # Low confidence + continuation indicators → Same document
        elif confidence < 0.5 and any(kw in reasoning for kw in ['section header', 'ii.', 'iii.', 'thửa đất']):
            is_new_document = False
            print(f"   ➡️ [{i}] Continuation page: {short_code} ({confidence:.0%})", file=sys.stderr)
        
        # Borderline case - use confidence
        else:
            is_new_document = (confidence >= 0.7)
            print(f"   ❓ [{i}] Borderline: {short_code} ({confidence:.0%}) → {'New' if is_new_document else 'Continue'}", file=sys.stderr)
        
        if is_new_document:
            # Start new group
            groups.append(current_group)
            current_group = [i]
            last_type = short_code
        else:
            # Continue current group
            current_group.append(i)
    
    # Add last group
    if current_group:
        groups.append(current_group)
    
    print(f"\n✅ Grouped into {len(groups)} documents:", file=sys.stderr)
    for g_idx, group in enumerate(groups):
        print(f"   Document {g_idx + 1}: {len(group)} pages {group}", file=sys.stderr)
    
    return groups


def batch_classify_smart(image_paths, api_key, engine_type='gemini-flash', last_known_type=None, max_batch_size=8):
    """
    Phương án 2: Smart Batching với SEQUENTIAL METADATA
    
    Args:
        max_batch_size: Maximum files per batch (default 15, can be reduced if needed)
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print("🧠 BATCH MODE 2: Smart Batching (AI Document Detection)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    total_files = len(image_paths)
    
    # Smart batch size strategy WITH user-configurable max
    if total_files <= max_batch_size:
        batch_size = total_files
        print(f"📊 Strategy: Send ALL {total_files} files in 1 batch (max={max_batch_size})", file=sys.stderr)
    else:
        batch_size = max_batch_size
        print(f"📊 Strategy: Send {batch_size} files per batch (user configured max={max_batch_size})", file=sys.stderr)
    
    print("   Sequential metadata: Pass lastKnown between batches (0% overhead)", file=sys.stderr)
    
    # Use fixed batch with smart size + sequential metadata
    return batch_classify_fixed(image_paths, api_key, engine_type=engine_type, batch_size=batch_size, last_known_type=last_known_type)


# CLI interface for testing
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python batch_processor.py <mode> <engine_type> <api_key> <image1> <image2> ...", file=sys.stderr)
        print("Modes: fixed, smart", file=sys.stderr)
        print("Engine types: gemini-flash, gemini-flash-lite, gemini-flash-hybrid", file=sys.stderr)
        print("Example: python batch_processor.py smart gemini-flash-hybrid AIza... img1.jpg img2.jpg img3.jpg", file=sys.stderr)
        sys.exit(1)
    
    mode = sys.argv[1]
    engine_type = sys.argv[2]
    api_key = sys.argv[3]
    image_paths = sys.argv[4:]
    
    print(f"🔍 Batch processing {len(image_paths)} images in '{mode}' mode with '{engine_type}'", file=sys.stderr)
    
    if mode == 'fixed':
        batch_data = batch_classify_fixed(image_paths, api_key, engine_type=engine_type, batch_size=5, last_known_type=None)
    elif mode == 'smart':
        # Check for optional max_batch_size env variable
        env_value = os.environ.get('SMART_MAX_BATCH_SIZE', '10')
        print(f"🔍 DEBUG: SMART_MAX_BATCH_SIZE env = '{env_value}'", file=sys.stderr)
        max_batch_size = int(env_value)
        print(f"📊 Smart mode max_batch_size: {max_batch_size}", file=sys.stderr)
        batch_data = batch_classify_smart(image_paths, api_key, engine_type=engine_type, last_known_type=None, max_batch_size=max_batch_size)
    elif mode == 'tesseract_text':
        # NEW MODE: Tesseract OCR + Gemini Text Classification
        print(f"⚡ [NEW MODE] Using Tesseract + Gemini Text approach", file=sys.stderr)
        batch_data = batch_classify_tesseract_text(image_paths, api_key, last_known_type=None)
    else:
        print(f"❌ Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
    
    # Extract results
    results = batch_data['results'] if isinstance(batch_data, dict) else batch_data
    
    # Output JSON to stdout for IPC
    print(json.dumps(results, ensure_ascii=False))
    
    print(f"\n📊 BATCH COMPLETE: {len(results)} files processed", file=sys.stderr)
