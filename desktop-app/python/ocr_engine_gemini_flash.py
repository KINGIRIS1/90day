#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash 2.0 - AI Document Classification Engine
Using direct REST API (no async, no emergentintegrations)
"""

import sys
import base64
from PIL import Image
import io

# Valid document codes - MUST match rule_classifier.py
# Total: 98 valid codes (95 from classifier + GCNC + GCNM + GCN)
# NOTE: "GCN" is a TEMPORARY code used during batch processing
#       It will be post-processed to GCNC (old) or GCNM (new) based on issue date
VALID_DOCUMENT_CODES = {
    'BBBDG', 'BBGD', 'BBHDDK', 'BBKTDC', 'BBKTHT', 'BBKTSS', 'BBNT',
    'BKKDT', 'BLTT', 'BMT', 'BVHC', 'BVN', 'CCCD', 'CDLK', 'CHTGD',
    'CKDC', 'CKTSR', 'DCK', 'DCQDGD', 'DDCTH', 'DDK', 'DDKBD', 'DGH',
    'DICHUC', 'DKTC', 'DKTD', 'DKXTC', 'DMD', 'DMG', 'DSCG', 'DSCK',
    'DXCD', 'DXCMD', 'DXGD', 'DXN', 'DXNTH', 'DXTHT',
    'GCN',   # TEMPORARY - will be post-processed to GCNC or GCNM
    'GCNC',  # GCN old (red/brown certificate)
    'GCNM',  # GCN new (pink certificate)
    'GKH', 'GKS', 'GNT', 'GPXD', 'GSND', 'GTLQ', 'GUQ', 'GXNDKLD',
    'GXNNVTC', 'HCLK', 'HDBDG', 'HDCQ', 'HDTCO', 'HDTD', 'HDTHC', 'HDUQ',
    'HSKT', 'HTBTH', 'HTNVTC', 'KTCKCG', 'KTCKMG', 'PCT', 'PCTSVC',
    'PDPASDD', 'PKTHS', 'PLYKDC', 'PXNKQDD', 'QDCHTGD', 'QDCMD', 'QDDCGD',
    'QDDCQH', 'QDDCTH', 'QDGH', 'QDGTD', 'QDHG', 'QDHTSD', 'QDPDBT',
    'QDPDDG', 'QDTH', 'QDTHA', 'QDTT', 'QDXP', 'QR', 'SDTT', 'TBCKCG',
    'TBCKMG', 'TBCNBD', 'TBMG', 'TBT', 'TKT', 'TTCG', 'TTHGD', 'UNKNOWN',
    'VBCTCMD', 'VBDNCT', 'VBTC', 'VBTK', 'hoadon'  # hoadon is lowercase in classifier
}


def resize_image_smart(img, max_width=1500, max_height=2100):
    """
    Smart resize: Only resize if image exceeds max dimensions
    Maintains aspect ratio
    
    Args:
        img: PIL Image object
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        
    Returns:
        PIL Image object (resized or original)
        dict: Resize info
    """
    width, height = img.size
    
    # Check if resize is needed
    if width <= max_width and height <= max_height:
        return img, {
            "resized": False,
            "original_size": f"{width}x{height}",
            "final_size": f"{width}x{height}",
            "reduction_percent": 0
        }
    
    # Calculate resize ratio (maintain aspect ratio)
    ratio_w = max_width / width
    ratio_h = max_height / height
    ratio = min(ratio_w, ratio_h)
    
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    
    # Use LANCZOS for high quality resize
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    reduction = (1 - (new_width * new_height) / (width * height)) * 100
    
    print(f"🔽 Image resized: {width}x{height} → {new_width}x{new_height} (-{reduction:.1f}% pixels)", file=sys.stderr)
    
    return resized_img, {
        "resized": True,
        "original_size": f"{width}x{height}",
        "final_size": f"{new_width}x{new_height}",
        "reduction_percent": round(reduction, 1)
    }


def classify_document_gemini_flash(image_path, api_key, crop_top_percent=1.0, model_type='gemini-flash', enable_resize=True, max_width=1500, max_height=2100):
    """
    Classify Vietnamese land document using Gemini Flash 2.0 AI with position awareness
    
    Args:
        image_path: Path to image file
        api_key: Google API key (BYOK)
        crop_top_percent: Percentage of top image to process (default 1.0 = 100% for accurate position analysis)
        model_type: 'gemini-flash' or 'gemini-flash-lite' (default: 'gemini-flash')
        enable_resize: Enable smart resizing to reduce costs (default: True)
        max_width: Maximum width for resize (default: 2000)
        max_height: Maximum height for resize (default: 2800)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning, title_position
    """
    try:
        import requests
        
        
        # Determine model name
        model_name = 'gemini-2.5-flash-lite' if model_type == 'gemini-flash-lite' else 'gemini-2.5-flash'
        # Read full image for position-aware analysis
        resize_info = {}
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Process full image or crop if specified
            if crop_top_percent < 1.0:
                crop_height = int(height * crop_top_percent)
                processed_img = img.crop((0, 0, width, crop_height))
                print(f"🖼️ Image cropped: {width}x{height} → {width}x{crop_height} (top {int(crop_top_percent*100)}%)", file=sys.stderr)
            else:
                processed_img = img
                print(f"🖼️ Processing full image: {width}x{height} (position-aware mode)", file=sys.stderr)
            
            # Apply smart resize if enabled
            if enable_resize:
                processed_img, resize_info = resize_image_smart(processed_img, max_width, max_height)
            
            # Convert to base64 (use JPEG with quality 85 for better compression)
            img_byte_arr = io.BytesIO()
            # Convert to RGB if needed (for JPEG)
            if processed_img.mode in ('RGBA', 'LA', 'P'):
                processed_img = processed_img.convert('RGB')
            processed_img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            image_content = img_byte_arr.getvalue()
        
        # Encode to base64
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        # Use direct REST API - v1beta is the standard API version
        # Model: gemini-2.5-flash or gemini-2.5-flash-lite
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        print(f"📡 Sending request to {model_name}...", file=sys.stderr)
        if resize_info.get('resized'):
            print(f"💰 Cost savings: ~{resize_info['reduction_percent']:.0f}% fewer tokens", file=sys.stderr)
        
        # Create request payload with appropriate prompt
        # Use simplified prompt for Flash Lite
        prompt_text = get_classification_prompt_lite() if model_type == 'gemini-flash-lite' else get_classification_prompt()
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for consistent, deterministic output
                "topP": 0.8,         # Slightly lower top_p for more focused responses
                "topK": 10,          # Limit to top 10 tokens for consistency
                "maxOutputTokens": 2000  # Increased for GCN with issue_date extraction (needs more output)
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        }
        
        print(f"📡 Sending request to {model_name}...", file=sys.stderr)
        
        # Send request with retry logic
        max_retries = 3
        retry_delay = 10
        response = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                # Check for retryable errors
                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⚠️ 503 Service Unavailable, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 60 * (2 ** attempt)
                        print(f"⚠️ 429 Rate Limit, retry {attempt + 1}/{max_retries} in {wait_time}s...", file=sys.stderr)
                        import time
                        time.sleep(wait_time)
                        continue
                
                # Success or non-retryable error
                break
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ Timeout, retry {attempt + 1}/{max_retries}...", file=sys.stderr)
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    raise
        
        print(f"📊 Response status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            error_text = response.text[:500]
            
            # Handle specific error cases
            if response.status_code == 429:
                # Rate limit exceeded
                error_msg = "⚠️ VƯỢT QUÁ GIỚI HẠN REQUEST!\n\n"
                
                if "RATE_LIMIT_EXCEEDED" in error_text:
                    error_msg += "🔥 Rate Limit: Quá nhiều requests trong thời gian ngắn\n"
                    error_msg += "📌 Giải pháp:\n"
                    error_msg += "  • Đợi 1-2 phút rồi thử lại\n"
                    error_msg += "  • Giảm tốc độ scan (scan từng trang)\n"
                elif "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
                    error_msg += "📊 Free Tier hết quota (1,500 requests/ngày)\n"
                    error_msg += "📌 Giải pháp:\n"
                    error_msg += "  1. Đợi đến ngày mai (quota reset)\n"
                    error_msg += "  2. Upgrade lên Paid tier tại: https://aistudio.google.com/\n"
                    error_msg += "  3. Tạo API key mới với Gmail khác\n"
                    error_msg += "  4. Dùng OCR offline (Tesseract/VietOCR) tạm thời\n"
                else:
                    error_msg += f"Chi tiết: {error_text}\n"
                
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    "short_code": "ERROR",
                    "confidence": 0,
                    "reasoning": error_msg,
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            
            elif response.status_code == 403:
                error_msg = "🔐 API KEY KHÔNG HỢP LỆ hoặc BỊ KHÓA!\n"
                error_msg += "📌 Giải pháp:\n"
                error_msg += "  • Kiểm tra API key trong Settings\n"
                error_msg += "  • Tạo API key mới tại: https://aistudio.google.com/\n"
                error_msg += "  • Enable Generative Language API\n"
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    "short_code": "ERROR",
                    "confidence": 0,
                    "reasoning": error_msg,
                    "error_code": "INVALID_API_KEY"
                }
            
            else:
                # Generic error
                error_msg = f"API error {response.status_code}: {error_text}"
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    "short_code": "ERROR",
                    "confidence": 0,
                    "reasoning": error_msg,
                    "error_code": f"HTTP_{response.status_code}"
                }
        
        result_data = response.json()
        
        # Extract usage metadata
        usage_metadata = result_data.get('usageMetadata', {})
        usage_info = {
            "input_tokens": usage_metadata.get('promptTokenCount', 0),
            "output_tokens": usage_metadata.get('candidatesTokenCount', 0),
            "total_tokens": usage_metadata.get('totalTokenCount', 0)
        }
        
        print(f"📊 Tokens: input={usage_info['input_tokens']}, output={usage_info['output_tokens']}", file=sys.stderr)
        
        # Check for safety ratings or finish reason (why output=0)
        if 'candidates' in result_data and len(result_data['candidates']) > 0:
            candidate = result_data['candidates'][0]
            
            # Check finish reason
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            if finish_reason != 'STOP':
                print(f"⚠️ Gemini finish reason: {finish_reason}", file=sys.stderr)
                
                # Check safety ratings
                if 'safetyRatings' in candidate:
                    print(f"🛡️ Safety ratings: {candidate['safetyRatings']}", file=sys.stderr)
            
            # Extract text from response
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    result_text = parts[0]['text']
                    print(f"🤖 Gemini response: {result_text[:200]}...", file=sys.stderr)
                    
                    # Parse result
                    classification = parse_gemini_response(result_text)
                    # Add usage and resize info
                    classification['usage'] = usage_info
                    classification['resize_info'] = resize_info
                    return classification
                else:
                    print(f"⚠️ No text in response parts. Candidate: {candidate}", file=sys.stderr)
            else:
                print(f"⚠️ No content in candidate. Full candidate: {candidate}", file=sys.stderr)
        else:
            print(f"⚠️ No candidates in response. Full response: {result_data}", file=sys.stderr)
        
        # No valid response - construct detailed error message
        error_reason = "Could not parse Gemini response"
        if 'candidates' in result_data and len(result_data['candidates']) > 0:
            candidate = result_data['candidates'][0]
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            if finish_reason == 'SAFETY':
                error_reason = "Response blocked by safety filters"
            elif finish_reason == 'MAX_TOKENS':
                error_reason = "Response exceeded max tokens"
            elif finish_reason == 'RECITATION':
                error_reason = "Response blocked due to recitation"
            else:
                error_reason = f"Response incomplete (finish reason: {finish_reason})"
        
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": error_reason,
            "usage": usage_info,
            "resize_info": resize_info
        }
        
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Missing library: {missing_lib}. Install: pip install {missing_lib}"
        }
    except Exception as e:
        print(f"❌ Gemini Flash error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Error: {str(e)}"
        }


def get_classification_prompt_lite():
    """
    OPTIMIZED prompt for Flash Lite with critical special cases
    Balances simplicity with accuracy for edge cases
    Target: ~1500-2000 tokens (60-65% reduction from full)
    """
    return """🎯 NHIỆM VỤ: Phân loại tài liệu đất đai Việt Nam

📋 QUY TẮC PHÂN LOẠI (QUAN TRỌNG):

🔍 1. VỊ TRÍ TIÊU ĐỀ (STRICT TOP 20% ONLY!):
✅ CHỈ PHÂN LOẠI NẾU ĐẦY ĐỦ TẤT CẢ CÁC ĐIỀU KIỆN:
- Text LỚN NHẤT, căn giữa
- 🔒 **BẮT BUỘC: NẰM Ở TOP 20% CỦA TRANG** (NOT middle, NOT 30-40%)
- NẰM ĐỘC LẬP (không có text khác cùng dòng)
- VD đúng: "HỢP ĐỒNG CHUYỂN NHƯỢNG", "PHIẾU THẨM TRA", "GIẤY CHỨNG NHẬN"

❌ TUYỆT ĐỐI BỎ QUA NẾU (BLACKLIST - QUAN TRỌNG):
- Text ở giữa/cuối trang (MIDDLE/BOTTOM) - NGAY CẢ NẾU text lớn!
- Text có SECTION NUMBER (I., II., III., IV., 1., 2., 3.) → Đây là section heading, KHÔNG phải title chính
- Có từ: "căn cứ", "theo", "kèm theo", "số...", "ngày...", "về việc"
- NẰM CHUNG với text khác trên cùng dòng
- Nằm trong câu văn

🚨 SECTION HEADERS - KHÔNG BAO GIỜ LÀ TITLE CHÍNH (REJECT):
Nếu text có SECTION NUMBER ở đầu → KHÔNG PHẢI title chính → Trả về UNKNOWN:
- "I. ...", "II. ...", "III. ...", "IV. ...", "V. ..."
- "1. ...", "2. ...", "3. ...", "4. ..."
- "1.1 ...", "2.1 ...", "3.1 ..."
- VD SAI: "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG..." → KHÔNG phải title (là section header!)
- VD SAI: "I. THÔNG TIN CHUNG" → KHÔNG phải title (là section header!)

🚨 BLACKLIST - KHÔNG BAO GIỜ LÀ TITLE CHÍNH (REJECT NGAY):
Nếu text BẮT ĐẦU bằng các từ sau → KHÔNG PHẢI title → Trả về UNKNOWN:
- "Người..." (ví dụ: "Người lập văn bản", "Người đại diện")
- "Phiếu..." khi viết chữ hoa đầu (ví dụ: "Phiếu đánh giá", "Phiếu xác nhận")
- "Giấy..." khi viết chữ hoa đầu (ví dụ: "Giấy xác nhận", "Giấy ủy quyền")
- "Biên..." (ví dụ: "Biên bản họp")
- "Đơn..." (ví dụ: "Đơn xin phép")
- "Văn bản..." (ví dụ: "Văn bản cam kết")
- "Bản..." (ví dụ: "Bản kê khai")

⚠️ QUAN TRỌNG - POSITION VERIFICATION:
- Nếu có text LỚN nhưng ở giữa trang (30-60% từ top) → KHÔNG phải title → UNKNOWN
- Nếu có text LỚN có section number (I., II., III.) → KHÔNG phải title → UNKNOWN
- CHỈ ACCEPT text ở TOP 20% CỦA TRANG (0-20% from top)

👁️ 2. VISUAL INDICATORS (QUAN TRỌNG):
✅ QUỐC HUY (National Emblem):
- Có QUỐC HUY ở top center → GCNC (Giấy chứng nhận CŨ - màu cam/vàng)
- Có QUỐC HUY + "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" → Giấy tờ chính thức
- Không có quốc huy + tiêu đề dài "quyền sở hữu nhà ở..." → GCNM (MỚI)

✅ LAYOUT RECOGNITION:
- CERTIFICATE: Có quốc huy, serial number, filled data, formal layout
- FORM: Có blank fields, ô trống, checkbox, table để điền
- MAP: Có sơ đồ, ranh giới, coordinates, visual diagram
- NOTICE: Header quan, footer chữ ký, structured sections

⚠️ NGOẠI LỆ - GCNM CONTINUATION:
NẾU THẤY các section SAU (đứng riêng, không có tiêu đề chính):
- "III. THÔNG TIN VỀ THỬA ĐẤT"
- "IV. THÔNG TIN VỀ TÀI SẢN GẮN LIỀN VỚI ĐẤT"
- "V. THÔNG TIN VỀ HẠN CHẾ VỀ QUYỀN" + bảng
→ Trả về GCNM (trang tiếp theo của GCN)

✅ 98 LOẠI TÀI LIỆU (CHỈ DÙNG CÁC MÃ SAU):

NHÓM 1 - GIẤY CHỨNG NHẬN:
🚨 GCN = Giấy chứng nhận quyền sử dụng đất (BẤT KỲ VARIANT) 🚨
  • Title: "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT..." (dài hoặc ngắn)
  • ❌ TUYỆT ĐỐI KHÔNG trả về "GCNM" hoặc "GCNC" ❌
  • ✅ CHỈ trả về "GCN" (generic)
  
  • 🔒 QUY TẮC CỨNG (HARD RULE) - PHẢI CÓ ÍT NHẤT MỘT TRONG HAI:
    1. **QUỐC HUY** ở top center (national emblem với ngôi sao, búa liềm)
       - Phải thấy rõ quốc huy hoặc chỗ trống hình tròn/oval dành cho quốc huy
       - VD: Có hình tròn ở top center + "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" bên trên
    
    2. **CÁC DÒNG ĐẶC TRƯNG** ở top (PHẢI có đủ cả 3 dòng theo thứ tự):
       - Dòng 1: "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"
       - Dòng 2: "Độc lập - Tự do - Hạnh phúc" (có thể có gạch chân/underline)
       - Dòng 3: "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT..." (title chính)
    
    ⚠️ NẾU THIẾU BẤT KỲ YẾU TỐ NÀO → TUYỆT ĐỐI KHÔNG PHẢI GCN!
    
    ❌ VÍ DỤ KHÔNG PHẢI GCN (DÙ CÓ TITLE TƯƠNG TỰ):
    - "PHIẾU THẨM TRA" → Không có quốc huy, không có 3 dòng → PKTHS
    - "PHIẾU ĐÁNH GIÁ TÀI SẢN" → Không có quốc huy → GTK
    - "Giấy xác nhận quyền sử dụng đất" → Chữ thường + không có quốc huy → GXN
    - Form có blank fields + title "Đơn đăng ký..." → DDKBD
    - Notice có "VĂN PHÒNG ĐĂNG KÝ ĐẤT ĐAI" nhưng không có quốc huy → BVDS/PKTHS
    
  • ❌ KHÔNG PHẢI GCN nếu chỉ có:
    - Title "giấy chứng nhận" nhưng không có quốc huy/3 dòng → Có thể là copy/scan không rõ
    - Title tương tự nhưng là form trống (có blank fields) → DDKBD
    - Title tương tự nhưng là notice/trích lục → BVDS hoặc HSKT
  
  • ⚠️ BẮT BUỘC 1: Xác định MÀU SẮC của giấy (COLOR DETECTION - QUAN TRỌNG NHẤT)
    - Màu ĐỎ/CAM (red/orange): GCN cũ → color: "red"
    - Màu HỒNG (pink): GCN mới → color: "pink"
    - Không xác định được: color: "unknown"
    - Ví dụ: Nếu thấy màu nền đỏ cam → color: "red", nếu màu hồng → color: "pink"
  
  • ⚠️ BẮT BUỘC 2: Tìm NGÀY CẤP (có thể ở trang 1 hoặc trang 2, có thể viết tay)
    - GCN A3 (2 trang lớn): Ngày cấp thường ở trang 2
    - GCN A4 (1 trang nhỏ): Ngày cấp thường ở trang 1 (bottom)
    - Các format có thể gặp:
      * Format 1: "DD/MM/YYYY" (ví dụ: "14/04/2025", "27/10/2021")
      * Format 2: "Ngày DD tháng MM năm YYYY" (ví dụ: "Ngày 25 tháng 8 năm 2010")
      * Format 3: "DD.MM.YYYY" hoặc "DD-MM-YYYY"
    - Nếu mờ: MM/YYYY (ví dụ: "02/2012") hoặc YYYY (ví dụ: "2012")
    - Tìm text gần: "Ngày cấp", "Cấp ngày", "Ngày...tháng...năm", "TM. UBND"
    - ⚠️ Quan trọng: Nếu thấy format "Ngày XX tháng YY năm ZZZZ" → chuyển thành "XX/YY/ZZZZ"
    - Ví dụ: "Ngày 25 tháng 8 năm 2010" → trả về "25/08/2010" hoặc "25/8/2010"
  
  • Response: "GCN" + color + issue_date + issue_date_confidence
  • Lý do: Frontend sẽ phân loại theo:
    1. Ưu tiên 1: Màu sắc (red = GCNC, pink = GCNM)
    2. Ưu tiên 2: Ngày cấp (nếu không detect được màu)

  • ✅ ĐÚNG (GCN đỏ/cam - cũ, format DD/MM/YYYY):
    {
      "short_code": "GCN",
      "color": "red",
      "issue_date": "27/10/2021",
      "issue_date_confidence": "full",
      "confidence": 0.95,
      "reasoning": "Giấy chứng nhận màu đỏ/cam (cũ), ngày cấp 27/10/2021"
    }
  • ✅ ĐÚNG (GCN hồng - mới, format DD/MM/YYYY):
    {
      "short_code": "GCN",
      "color": "pink",
      "issue_date": "14/04/2025",
      "issue_date_confidence": "full",
      "confidence": 0.95,
      "reasoning": "Giấy chứng nhận màu hồng (mới), ngày cấp 14/04/2025"
    }
  • ✅ ĐÚNG (GCN format "Ngày...tháng...năm"):
    {
      "short_code": "GCN",
      "color": "pink",
      "issue_date": "25/8/2010",
      "issue_date_confidence": "full",
      "confidence": 0.95,
      "reasoning": "Giấy chứng nhận màu hồng, ngày cấp 25/8/2010 (từ 'Ngày 25 tháng 8 năm 2010')"
    }
  • ✅ ĐÚNG (không detect được màu):
    {
      "short_code": "GCN",
      "color": "unknown",
      "issue_date": "01/01/2012",
      "issue_date_confidence": "full",
      "confidence": 0.9,
      "reasoning": "Giấy chứng nhận, không xác định được màu, ngày cấp 01/01/2012"
    }
  • ✅ ĐÚNG (không tìm thấy ngày):
    {
      "short_code": "GCN",
      "color": "pink",
      "issue_date": null,
      "issue_date_confidence": "not_found",
      "confidence": 0.9,
      "reasoning": "Giấy chứng nhận màu hồng, không tìm thấy ngày cấp (có thể trang 1 hoặc trang 2)"
    }
  • ❌ SAI (không bao giờ làm):
    {
      "short_code": "GCNM",  // ❌ Phải là "GCN"
      ...
    }
GCNB = Giấy chứng nhận bản sao
GCNL = Giấy chứng nhận lãnh sự

NHÓM 2 - HỢP ĐỒNG (QUAN TRỌNG - PHÂN BIỆT RÕ):
⚠️ PHÂN BIỆT CHÍNH XÁC:
HDCQ = Hợp đồng chuyển nhượng, tặng cho quyền sử dụng đất
  • Tiêu đề CHÍNH XÁC: "HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT"
  • Hoặc: "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT"
  • Keywords: "chuyển nhượng", "tặng cho", "bán đất", "mua đất", "quyền sử dụng đất"
  • Nội dung: Chuyển quyền sở hữu đất từ A sang B (bán/tặng)
  • ✅ VD ĐÚNG: Title có "CHUYỂN NHƯỢNG" → HDCQ

HDUQ = Hợp đồng ủy quyền
  • Tiêu đề CHÍNH XÁC: "HỢP ĐỒNG ỦY QUYỀN"
  • Keywords: "ủy quyền", "người ủy quyền", "người được ủy quyền", "thay mặt"
  • Nội dung: A ủy quyền cho B làm thủ tục (KHÔNG chuyển quyền sở hữu)
  • ✅ VD ĐÚNG: Title có "ỦY QUYỀN" (KHÔNG có "chuyển nhượng") → HDUQ
  • 🚨 QUAN TRỌNG: Nếu title là "HỢP ĐỒNG ỦY QUYỀN" → BẮT BUỘC trả về HDUQ (KHÔNG phải HDCQ)

HDGO = Hợp đồng góp vốn
HDMB = Hợp đồng mua bán
HDSD = Hợp đồng sử dụng
HDTH = Hợp đồng cho thuê
HDTC = Hợp đồng thế chấp
HDTL = Hợp đồng tặng cho

NHÓM 3 - ĐƠN (APPLICATION FORMS):
DDKBD = Đơn đăng ký biến động đất đai, tài sản gắn liền với đất
  • Title: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI"
  • Keywords: "biến động", "nội dung biến động", "nhận chuyển nhượng"
  • Form có sections: thông tin người dùng đất, nội dung biến động, giấy tờ kèm theo
  • ⚠️ KHÔNG dùng cho đơn tách/hợp thửa (dùng DXTHT)
DXTHT = Đơn xin (đề nghị) tách thửa đất, hợp thửa đất
  • Title: "ĐƠN ĐỀ NGHỊ TÁCH THỪA ĐẤT, HỢP THỪA ĐẤT" hoặc "ĐƠN XIN TÁCH THỬA"
  • Keywords: "tách thửa", "hợp thửa", "tách", "hợp"
  • ⚠️ Ưu tiên DXTHT nếu có từ "tách" hoặc "hợp" trong title
DCK = Đơn cam kết, Giấy cam kết
  • Title: "GIẤY CAM KẾT" hoặc "ĐƠN CAM KẾT" (PHẢI TOÀN BỘ IN HOA)
  • Variants: "GIẤY CAM KẾT\n(V/v chọn thửa đất...)", "ĐƠN CAM KẾT"
  • Keywords: "cam kết", "xin cam kết"
  • ❌ REJECT: "Người lập văn bản cam kết" (không phải title chính, chỉ là mô tả người lập)
  • ❌ REJECT: "Giấy cam kết" (chữ hoa đầu dòng, không phải in hoa toàn bộ)
DXGCN = Đơn xin cấp giấy chứng nhận
DXCMG = Đơn xin cấp lại giấy chứng nhận mất
DXCHS = Đơn xin cấp lại giấy chứng nhận hỏng/sai
DXDLT = Đơn xin điều lệ tổ chức
DXMTQ = Đơn xin miễn thuế
DXCMD = Đơn xin chuyển mục đích
DXGD = Đơn xin giao đất
DXTT = Đơn xin thuê đất
DXTDSD = Đơn xin gia hạn thời hạn sử dụng đất

NHÓM 4 - QUYẾT ĐỊNH:
QDGD = Quyết định giao đất
QDTT = Quyết định cho thuê đất
QDCMD = Quyết định cho phép chuyển mục đích
QDPH = Quyết định phê duyệt
QDCG = Quyết định công nhận/cấp giấy
QDTD = Quyết định thu hồi đất
QDGT = Quyết định giá trị
QDBT = Quyết định bồi thường

NHÓM 5 - GIẤY:
GUQ = Giấy ủy quyền
GTLQ = Giấy tiếp nhận hồ sơ và hẹn trả kết quả
  • Title: "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ"
  • Hoặc "PHIẾU KIỂM SOÁT QUÁ TRÌNH GIẢI QUYẾT HỒ SƠ"
  • Keywords: "hồ sơ", "hẹn trả", "kiểm soát quá trình"
  • Có bảng tracking hồ sơ
GNT = Giấy nộp tiền vào ngân sách nhà nước
  • Title: "GIẤY NỘP TIỀN VÀO NGÂN SÁCH NHÀ NƯỚC"
  • Form ngân hàng (VietinBank, etc)
  • Keywords: "ngân sách", "nộp tiền", "kho bạc"
GBD = Giấy biên nhận
GCN = Giấy chứng nhận khác
GTD = Giấy tờ đề nghị
GXN = Giấy xác nhận
GTK = Giấy tờ khác
GCC = Giấy chứng tử (Chết)

NHÓM 6 - BIÊN BẢN:
BBND = Biên bản nghiệm thu
BBKS = Biên bản kiểm kê
BBTK = Biên bản thống kê
BBTH = Biên bản tổng hợp
BBDN = Biên bản định giá
BBDG = Biên bản đo đạc
BBGH = Biên bản giao nhận
BBBT = Biên bản bàn giao
BBHOP = Biên bản họp
BBKTHT = Biên bản kiểm tra, xác minh hiện trạng
  • Title: "BIÊN BẢN" + "Xác minh thực địa..." hoặc "Kiểm tra xác minh hiện trạng..."
  • Variants: "xác minh thực địa", "xác minh hiện trạng"
BBKK = Biên bản khác

NHÓM 7 - BẢN:
BVDS = Bản vẽ
BSDD = Bản sao (duplicate)
BCC = Bản cam đoan
BDK = Bản đăng ký
BKDK = Bản kê khai đất
HSKT = Bản vẽ (Trích lục, đo tách, chỉnh lý, bản đồ địa chính)
  • Title: "BẢN VẼ" hoặc "TRÍCH LỤC BẢN ĐỒ ĐỊA CHÍNH" hoặc "ĐỒ ĐẠC CHÍNH LÝ BẢN ĐỒ ĐỊA CHÍNH"
  • Map extract, technical drawings, cadastral maps with scale (TỈ LỆ 1:500, etc.)
  • KHÔNG phải GCNM (certificate)
BVDS = Bản vẽ đo sơ / Bản đồ địa chính (alias của HSKT, có thể dùng cả 2)
BGTVN = Bản giao thừa kế Việt Nam
BGNNN = Bản giao thừa kế nước ngoài

NHÓM 8 - SƠ ĐỒ:
SDPT = Sơ đồ phân tích
SDHV = Sơ đồ hiện trạng

NHÓM 9 - PHIẾU:
PKTHS = Phiếu kiểm tra hồ sơ
  • Title: "PHIẾU KIỂM TRA HỒ SƠ" hoặc "PHIẾU TRÌNH KÝ HỒ SƠ CẤP GIẤY CHỨNG NHẬN"
  • Keywords: "kiểm tra hồ sơ", "trình ký", "cấp giấy chứng nhận"
  • KHÔNG phải "Phiếu kiểm soát" (→ GTLQ)
PLYKDC = Phiếu lấy ý kiến dân cư
PXNKQDD = Phiếu xác nhận kết quả đo đạc
  • Title: "PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC HIỆN TRẠNG THỬA ĐẤT"
  • PHẢI CÓ quốc huy + 3 dòng ("CỘNG HÒA...", "Độc lập...", title)
  • Nội dung: Thông tin đo đạc đất (tọa độ, diện tích, bản vẽ thửa đất)
  • Keywords: "đo đạc", "thửa đất", "tọa độ", "diện tích", "bản vẽ"
  • ⚠️ PHÂN BIỆT với PKTHS: PXNKQDD có quốc huy + nội dung về đo đạc/tọa độ, PKTHS KHÔNG có quốc huy
PCT = Phiếu chuyển thông tin để xác định nghĩa vụ tài chính
  • Title: "PHIẾU CHUYỂN THÔNG TIN ĐỂ XÁC ĐỊNH NGHĨA VỤ TÀI CHÍNH"
  • Từ Văn phòng đăng ký đất đai gửi Cơ quan thuế
DKTC = Phiếu yêu cầu đăng ký biện pháp bảo đảm
DKTD = Phiếu yêu cầu đăng ký thay đổi biện pháp bảo đảm
DKXTC = Phiếu yêu cầu xóa đăng ký biện pháp bảo đảm
QR = Quét mã QR

NHÓM 10 - THÔNG BÁO:
TBT = Thông báo thuế
  • Title: "THÔNG BÁO THUẾ" hoặc "THÔNG BÁO NỘP TIỀN"
  • Về thuế trước bạ, TNCN, tiền sử dụng đất, nộp tiền
  • Keywords: "thuế", "nộp tiền", "nghĩa vụ tài chính", "trước bạ"
  ⚠️ Đặc điểm: Nhiều trang với bảng biểu tính thuế (4.1, 4.2, III. TÍNH THUẾ...)
  ⚠️ Continuation pages: Có section headers (III., IV.) và bảng biểu
  ⚠️ Phải gom TẤT CẢ pages có bảng tính thuế vào cùng TBT document
TBMG = Thông báo mất giấy
TBCKCG = Thông báo công khai cấp giấy
TBCKMG = Thông báo công khai mất giấy
HTNVTC = Thông báo xác nhận hoàn thành nghĩa vụ tài chính
TBCNBD = Thông báo cập nhật biến động
CKDC = Thông báo công bố công khai di chúc
HTBTH = Hoàn thành bồi thường hỗ trợ

NHÓM 11 - TỜ:
TKT = Tờ khai thuế
TTr = Tờ trình về giao đất (⚠️ "TTr" với "r" viết thường)
TTCG = Tờ trình về đăng ký đất đai

NHÓM 12 - VĂN BẢN:
CKTSR = Văn bản cam kết tài sản riêng
VBCTCMD = Văn bản chấp thuận chuyển mục đích
VBDNCT = Văn bản đề nghị chấp thuận chuyển nhượng
PDPASDD = Văn bản đề nghị thẩm định phương án
VBTK = Văn bản thỏa thuận phân chia di sản thừa kế
TTHGD = Văn bản thỏa thuận hộ gia đình (Keyword: HỘ GIA ĐÌNH)
CDLK = Văn bản chấm dứt quyền hạn chế đất liền kề
HCLK = Văn bản xác lập quyền hạn chế đất liền kề
VBTC = Văn bản từ chối nhận di sản
PCTSVC = Văn bản phân chia tài sản vợ chồng (Keyword: VỢ CHỒNG)

⚠️ DỄ NHẦM (CỰC KỲ QUAN TRỌNG):

1. DDKBD vs GCNM (QUAN TRỌNG NHẤT):
   ❌ SAI: Nhầm "Đơn đăng ký biến động" thành GCNM
   ✅ ĐÚNG:
   - DDKBD: Title "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI"
     • Là FORM đăng ký (có blank fields)
     • Keywords: "Nội dung biến động", "Giấy tờ kèm theo"
     • Layout: Form với các ô trống điền thông tin
   - GCNM: Title "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT..."
     • Là CERTIFICATE (đã fill sẵn thông tin)
     • Có QUỐC HUY, serial number
     • Layout: Giấy tờ chính thức, không có ô trống

1b. HSKT vs GCNM (DỄ NHẦM):
   ❌ SAI: Nhầm "Trích lục bản đồ" thành GCNM
   ✅ ĐÚNG:
   - HSKT: Title "BẢN VẼ" hoặc "TRÍCH LỤC BẢN ĐỒ ĐỊA CHÍNH"
     • Là MAP/DRAWING (bản vẽ, trích lục, đo tách)
     • Visual: Có sơ đồ, ranh giới, tọa độ
     • Keywords: "bản vẽ", "trích lục", "đo tách", "chỉnh lý"
   - GCNM: Là text document, không phải map

2. GCNM vs GCNC (QUỐC HUY LÀ KEY):
   ✅ GCNC (CŨ - có quốc huy):
   - Có QUỐC HUY rõ ràng ở top center
   - Nền màu cam/vàng/vintage
   - Tiêu đề NGẮN: "Giấy chứng nhận quyền sử dụng đất"
   - Layout: Classic, older style
   
   ✅ GCNM (MỚI - KHÔNG có quốc huy):
   - KHÔNG có quốc huy (hoặc quốc huy rất nhỏ)
   - Nền trắng/modern
   - Tiêu đề DÀI: "...quyền sử dụng đất, quyền sở hữu nhà ở và tài sản gắn liền với đất"
   - Layout: Modern, detailed sections

3. TTHGD vs PCTSVC vs VBTK:
   - TTHGD: Có "HỘ GIA ĐÌNH" (không có "vợ chồng", không có "di sản")
   - PCTSVC: Có "VỢ CHỒNG" (không có "hộ gia đình")
   - VBTK: Có "DI SẢN THỪA KẾ" (về inheritance)

4. GTLQ vs PKTHS (QUAN TRỌNG):
   ❌ SAI: Nhầm "Phiếu kiểm soát" với "Phiếu kiểm tra/trình ký"
   ✅ ĐÚNG:
   - GTLQ: "PHIẾU KIỂM SOÁT QUÁ TRÌNH" hoặc "GIẤY TIẾP NHẬN HỒ SƠ"
     • Keywords: "hẹn trả", "kiểm soát quá trình", "giải quyết hồ sơ"
     • Có bảng tracking với chữ ký
   - PKTHS: "PHIẾU KIỂM TRA HỒ SƠ" hoặc "PHIẾU TRÌNH KÝ HỒ SƠ"
     • Keywords: "kiểm tra", "trình ký", "cấp giấy chứng nhận", "hồ sơ đầy đủ"
     • Form inspection/review để trình ký

5. REFERENCE vs TITLE:
   ❌ REFERENCE (BỎ QUA):
   - "Căn cứ Giấy chứng nhận số..."
   - "Theo hợp đồng chuyển nhượng số..."
   - "...đã từ chối nhận di sản theo văn bản từ chối..."
   
   ✅ TITLE (DÙNG):
   - "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG" (đứng riêng, IN HOA)
   - "HỢP ĐỒNG CHUYỂN NHƯỢNG" (đứng riêng, IN HOA)
   - "VĂN BẢN TỪ CHỐI NHẬN DI SẢN" (đứng riêng, title case)

🔍 QUY TRÌNH:
1. Kiểm tra vị trí: Text ở TOP 30%?
2. Kiểm tra độc lập: NẰM RIÊNG hay chung với text khác?
3. Kiểm tra reference: Có "căn cứ/theo/số" không?
4. NẾU pass 3 bước → Khớp với 98 loại
5. NẾU KHÔNG khớp → Kiểm tra GCNM continuation
6. NẾU vẫn không → Trả về "UNKNOWN"

📤 TRẢ VỀ JSON:
{
  "short_code": "MÃ_CHÍNH_XÁC",
  "confidence": 0.9,
  "title_position": "top",
  "reasoning": "Giải thích ngắn gọn"
}

🎯 VÍ DỤ THỰC TẾ:

✅ ĐÚNG:
- Trang có "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI" ở top
  → {short_code: "DDKBD", title_position: "top", confidence: 0.95}
  → Reasoning: "Đơn form, có blank fields, keyword 'biến động'"

- Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở top, chữ lớn
  → {short_code: "HDCQ", title_position: "top", confidence: 0.95}
  → Reasoning: "Hợp đồng chuyển nhượng đất, title rõ ràng"

- Trang có "HỢP ĐỒNG ỦY QUYỀN" ở top, chữ lớn
  → {short_code: "HDUQ", title_position: "top", confidence: 0.95}
  → Reasoning: "Hợp đồng ủy quyền (KHÔNG phải chuyển nhượng), title rõ ràng"
  → 🚨 QUAN TRỌNG: "ỦY QUYỀN" ≠ "CHUYỂN NHƯỢNG" → HDUQ (KHÔNG phải HDCQ)

- Trang có QUỐC HUY rõ + nền cam + "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT"
  → {short_code: "GCNC", confidence: 0.95}
  → Reasoning: "Classic certificate với quốc huy, nền màu, tiêu đề ngắn"

- Trang có tiêu đề dài "...quyền sở hữu nhà ở...", KHÔNG có quốc huy rõ
  → {short_code: "GCNM", confidence: 0.95}
  → Reasoning: "Modern certificate, tiêu đề dài, no prominent emblem"

- Trang có section "III. THÔNG TIN VỀ THỬA ĐẤT", không có tiêu đề
  → {short_code: "GCNM", reasoning: "GCN continuation page"}

❌ SAI:
- Trang có "...theo hợp đồng chuyển nhượng số..."
  → {short_code: "UNKNOWN", reasoning: "Reference only, not title"}

- Trang có "HỢP ĐỒNG" ở giữa trang (middle)
  → {short_code: "UNKNOWN", title_position: "middle"}

- Trang là form "ĐƠN ĐĂNG KÝ" nhưng classify thành GCNM
  → ❌ SAI! Phải là DDKBD (form khác certificate)

- Trang có title "HỢP ĐỒNG ỦY QUYỀN" nhưng classify thành HDCQ
  → ❌ SAI! Title rõ ràng là "ỦY QUYỀN" → Phải là HDUQ (KHÔNG phải HDCQ)
  → 🚨 LƯU Ý: Đọc kỹ title, "ỦY QUYỀN" khác hoàn toàn với "CHUYỂN NHƯỢNG"

- Trang có title "Người lập văn bản cam kết về tài sản" ở top, chữ lớn
  → ❌ SAI! "Người lập..." là chữ hoa đầu dòng, không phải IN HOA toàn bộ
  → Phải là {short_code: "UNKNOWN", reasoning: "Title không phải in hoa toàn bộ"}

- Trang có "PHIẾU THẨM TRA" nhưng classify thành GCN
  → ❌ SAI! Không có quốc huy, không có 3 dòng đặc trưng của GCN
  → Phải là PKTHS (KHÔNG phải GCN)

- Trang có "Giấy xác nhận" (chữ hoa đầu dòng) ở top
  → ❌ SAI! Phải là {short_code: "UNKNOWN"} vì không phải in hoa toàn bộ
  → Nếu là "GIẤY XÁC NHẬN" (toàn bộ in hoa) → GXN

- Trang có "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG..." ở giữa trang (middle), chữ lớn
  → ❌ SAI! Có section number "III." → Đây là section header, KHÔNG phải title chính
  → Phải là {short_code: "UNKNOWN", reasoning: "Section header ở middle, not title"}
  
- Trang có "I. THÔNG TIN CHUNG" ở 30% từ top
  → ❌ SAI! (1) Có section number "I.", (2) Không ở top 20%
  → Phải là {short_code: "UNKNOWN"}

- Trang có "PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC" + quốc huy + "CỘNG HÒA..." nhưng classify thành PKTHS
  → ❌ SAI! Có quốc huy + 3 dòng + nội dung về đo đạc → Phải là PXNKQDD (KHÔNG phải PKTHS)
  → PKTHS không có quốc huy, PXNKQDD CÓ quốc huy

❌ KHÔNG TỰ TẠO MÃ MỚI - CHỈ DÙNG 98 MÃ TRÊN!

📋 VÍ DỤ RESPONSE FORMAT:

✅ Example 1 - GCN Document (màu đỏ/cam - cũ):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "color": "red",
  "reasoning": "Giấy chứng nhận màu đỏ/cam (cũ), ngày cấp 27/10/2021",
  "issue_date": "27/10/2021",
  "issue_date_confidence": "full"
}

✅ Example 2 - GCN Document (màu hồng - mới):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "color": "pink",
  "reasoning": "Giấy chứng nhận màu hồng (mới), ngày cấp 14/04/2025",
  "issue_date": "14/04/2025",
  "issue_date_confidence": "full"
}

✅ Example 3 - HDCN Document:
{
  "short_code": "HDCN",
  "confidence": 0.92,
  "title_position": "top",
  "reasoning": "Hợp đồng chuyển nhượng quyền sử dụng đất",
  "issue_date": null,
  "issue_date_confidence": null
}

✅ Example 4 - HDUQ Document (HỢP ĐỒNG ỦY QUYỀN):
{
  "short_code": "HDUQ",
  "confidence": 0.98,
  "title_position": "top",
  "reasoning": "Hợp đồng ủy quyền - tiêu đề lớn ở top",
  "issue_date": null,
  "issue_date_confidence": null
}

✅ Example 5 - Unknown Document:
{
  "short_code": "UNKNOWN",
  "confidence": 0.3,
  "title_position": "middle",
  "reasoning": "Không khớp với bất kỳ mã nào trong danh sách 98 loại",
  "issue_date": null,
  "issue_date_confidence": null
}"""


def get_classification_prompt():
    """
    System prompt for Vietnamese document classification
    IMPORTANT: This prompt is aligned with OpenAI Vision backend prompt for consistency
    UPDATED: More flexible matching (85-90% similarity acceptable)
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 PHÂN TÍCH VỊ TRÍ VĂN BẢN (POSITION-AWARE CLASSIFICATION)

⚠️ CỰC KỲ QUAN TRỌNG: CHỈ PHÂN LOẠI DỰA VÀO TEXT Ở PHẦN ĐẦU TRANG!

📍 QUY TẮC VỊ TRÍ:

1️⃣ **PHẦN ĐẦU TRANG (TOP 30%)**
   - Đây là vùng TIÊU ĐỀ CHÍNH
   - CHỈ text ở đây MỚI được dùng để phân loại
   - Cỡ chữ LỚN, IN HOA, căn giữa
   - VD: "HỢP ĐỒNG CHUYỂN NHƯỢNG", "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG"

2️⃣ **PHẦN GIỮA TRANG (MIDDLE 30-70%)**
   - Đây là BODY CONTENT
   - ❌ KHÔNG được phân loại dựa vào text ở đây
   - Có thể có mentions của document types khác
   - VD: "...theo hợp đồng chuyển nhượng đã ký..."
   - → CHỈ LÀ MENTION, KHÔNG PHẢI TIÊU ĐỀ!

3️⃣ **PHẦN CUỐI TRANG (BOTTOM 70-100%)**
   - Đây là CHỮ KÝ, CON DẤU, GHI CHÚ
   - ❌ KHÔNG được phân loại dựa vào text ở đây

🔍 CÁCH PHÂN TÍCH:

BƯỚC 1: Nhìn vào ảnh, ước lượng vị trí của các đoạn text
- TOP 30%: Vùng tiêu đề
- MIDDLE 30-70%: Vùng body
- BOTTOM 70-100%: Vùng chữ ký

BƯỚC 2: Tìm tiêu đề chính (PHẢI Ở TOP 30%)
- Cỡ chữ lớn nhất
- IN HOA
- Căn giữa hoặc nổi bật
- Ở gần đầu trang

BƯỚC 3: Phân loại dựa vào tiêu đề TOP
- NẾU tìm thấy tiêu đề khớp ở TOP → Phân loại theo đó
- NẾU KHÔNG có tiêu đề ở TOP → Kiểm tra NGOẠI LỆ (GCN continuation)
- NẾU thấy mentions ở MIDDLE/BOTTOM → BỎ QUA

VÍ DỤ ĐÚNG:

✅ ĐÚNG:
Trang có text "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở TOP 20% (gần đầu trang, chữ lớn)
→ title_position: "top"
→ short_code: "HDCQ"
→ confidence: 0.9

✅ ĐÚNG:
Trang có text "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI" ở TOP 15%
→ title_position: "top"
→ short_code: "DDKBD"
→ confidence: 0.9

VÍ DỤ SAI:

❌ SAI - REFERENCE/MENTION (không phải title):
Trang có "Mẫu số 17C..." ở TOP, trong body có "...theo Giấy chứng nhận quyền sử dụng đất số..."
→ Đây là REFERENCE/MENTION, KHÔNG phải title
→ "theo Giấy chứng nhận..." = Căn cứ/Tham chiếu
→ Form 17C = TTHGD (Thỏa thuận hộ gia đình)
→ short_code: "TTHGD"
→ reasoning: "Form 17C, mentions to GCN are references only"

❌ SAI - MENTION trong body:
Trang có "Giấy chứng nhận" ở TOP, nhưng ở MIDDLE có text "...theo hợp đồng chuyển nhượng..."
→ KHÔNG phân loại là HDCQ
→ Chỉ mention trong body, không phải title
→ short_code: "GCNM" (dựa vào title ở TOP)
→ title_position: "top"

❌ SAI - Text ở MIDDLE:
Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở MIDDLE (giữa trang)
→ Đây KHÔNG phải tiêu đề chính
→ title_position: "middle"
→ short_code: "UNKNOWN"
→ reasoning: "Text found in middle of page, not a main title"

❌ SAI - LOWERCASE REFERENCE trong body (QUAN TRỌNG):
Trang có danh sách người thừa kế, trong body có "...đã từ chối nhận di sản theo văn bản từ chối nhận di sản số..."
→ "văn bản từ chối" = lowercase, trong câu văn, có "theo" → REFERENCE
→ KHÔNG có title chính ở TOP
→ Đây là danh sách / continuation page
→ short_code: "UNKNOWN" hoặc "GTLQ"
→ reasoning: "No main title at top, 'văn bản từ chối' is lowercase reference in body text"

✅ ĐÚNG - Nếu có TITLE thực sự:
Trang có "VĂN BẢN TỪ CHỐI NHẬN DI SẢN" ở TOP (chữ lớn, IN HOA)
→ Đây là TITLE chính thức
→ title_position: "top"
→ short_code: "VBTC"
→ reasoning: "Main title at top in uppercase"

⚠️ QUAN TRỌNG - PHÂN BIỆT REFERENCE vs TITLE:

❌ REFERENCES (bỏ qua khi classify):
- "Căn cứ Giấy chứng nhận..."
- "Theo Giấy chứng nhận số..."
- "Kèm theo hợp đồng..."
- "Theo quyết định..."
- "...do...cấp ngày..."
- "...theo văn bản từ chối..." (lowercase, trong body)
- "...đã từ chối nhận di sản theo văn bản từ chối..." (reference)

✅ ACTUAL TITLES (dùng để classify):
- "GIẤY CHỨNG NHẬN" (ở đầu trang, chữ lớn, không có "căn cứ/theo")
- "HỢP ĐỒNG CHUYỂN NHƯỢNG" (ở đầu trang, chữ lớn)
- "ĐƠN ĐĂNG KÝ..." (ở đầu trang, chữ lớn)
- "VĂN BẢN TỪ CHỐI NHẬN DI SẢN" (ở đầu trang, chữ lớn, title case/uppercase)

🔍 DẤU HIỆU NHẬN BIẾT REFERENCE:
- Có từ "căn cứ", "theo", "kèm theo", "do...cấp", "đã từ chối...theo"
- Có số văn bản kèm theo (số AN..., số CS..., số công chứng...)
- Nằm trong câu văn dài, không standalone
- Cỡ chữ BÌNH THƯỜNG, không nổi bật
- Viết thường (lowercase): "văn bản từ chối" thay vì "VĂN BẢN TỪ CHỐI"
- **NẰM CHUNG với các từ khác trên cùng dòng** (VD: "theo Giấy chứng nhận...", "...theo văn bản...")

🎯 DẤU HIỆU NHẬN BIẾT TITLE (CỰC KỲ QUAN TRỌNG):

✅ TITLE phải NẰM ĐỘC LẬP:
- **Mỗi dòng CHỈ có text của title, KHÔNG có text khác**
- Có thể xuống dòng:
  * Dòng 1: "VĂN BẢN"
  * Dòng 2: "PHÂN CHIA TÀI SẢN..."
  * → ĐỘC LẬP, mỗi dòng chỉ có title
  
- Hoặc một dòng duy nhất:
  * "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT"
  * → ĐỘC LẬP, không có text khác

❌ KHÔNG PHẢI TITLE nếu:
- NẰM CHUNG với text khác: "theo Giấy chứng nhận quyền sử dụng đất số..."
  * "Giấy chứng nhận" KHÔNG độc lập
  * Có "theo" và "số..." trên cùng dòng/câu
  * → Đây là REFERENCE, không phải TITLE

- NẰM CHUNG với text khác: "...đã từ chối nhận di sản theo văn bản từ chối nhận di sản số..."
  * "văn bản từ chối" KHÔNG độc lập
  * Có nhiều từ khác trên cùng dòng
  * → Đây là REFERENCE, không phải TITLE

VÍ DỤ PHÂN BIỆT:

✅ TITLE (độc lập):
```
                VĂN BẢN
        PHÂN CHIA TÀI SẢN CHUNG
           CỦA HỘ GIA ĐÌNH
```
→ Mỗi dòng ĐỘC LẬP, chỉ có title
→ Classify: TTHGD

❌ REFERENCE (không độc lập):
```
2. Ông Nguyễn Văn A đã từ chối nhận di sản theo văn bản từ chối nhận di sản số 123...
```
→ "văn bản từ chối" NẰM CHUNG với "đã từ chối", "theo", "số 123"
→ KHÔNG classify theo "văn bản từ chối"
→ Classify: UNKNOWN hoặc GTLQ

❌ SECTION HEADERS (không phải title):
```
ĐIỀU 2
NỘI DUNG THỎA THUẬN PHÂN CHIA
```
→ "ĐIỀU 1:", "ĐIỀU 2:", "ĐIỀU 3:" = SECTION HEADERS, không phải MAIN TITLE
→ Đây là continuation page (trang 2+)
→ KHÔNG classify dựa vào section headers
→ Classify: UNKNOWN (hoặc GTLQ nếu là supporting doc)

⚠️ QUAN TRỌNG - BỎ QUA SECTION HEADERS:
- "ĐIỀU 1:", "ĐIỀU 2:", "Điều 3:", "I.", "II.", "III." = Section numbering
- "PHẦN I:", "PHẦN II:", "Chương 1:", "Chương 2:" = Part/Chapter headers
- Đây KHÔNG phải main title
- CHỈ classify dựa vào MAIN TITLE (không có số thứ tự, không có "Điều", "Phần")

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🚨 QUY TẮC CỰC KỲ QUAN TRỌNG - GIẤY CHỨNG NHẬN (GCN)

❌ TUYỆT ĐỐI KHÔNG BAO GIỜ TRẢ VỀ "GCNM" HOẶC "GCNC" ❌

⚠️ NẾU thấy Giấy chứng nhận (quốc huy + màu hồng/đỏ + "GIẤY CHỨNG NHẬN"):
   → Trả về: short_code = "GCN" (generic, không phải GCNM/GCNC)
   → BẮT BUỘC: Tìm NGÀY CẤP (thường ở trang 2, có thể viết tay)

📋 TÌM NGÀY CẤP (ISSUE DATE):
   • Vị trí: 
     - A3 (2 trang lớn): Thường ở trang 2, gần cuối trang
     - A4 (1 trang nhỏ): Thường ở trang 1, bottom
   • Text gần: "Ngày cấp", "Cấp ngày", "Ngày...tháng...năm", "TM. UBND"
   • Các format có thể gặp:
     - Format 1: "DD/MM/YYYY" (ví dụ: "01/01/2012", "15/03/2013", "14/04/2025")
     - Format 2: "Ngày DD tháng MM năm YYYY" (ví dụ: "Ngày 25 tháng 8 năm 2010")
       → PHẢI chuyển thành "DD/MM/YYYY" (ví dụ: "25/8/2010" hoặc "25/08/2010")
     - Format 3: "DD.MM.YYYY" hoặc "DD-MM-YYYY"
     - Nếu mờ: MM/YYYY hoặc YYYY
   • ⚠️ QUAN TRỌNG: Nếu thấy format "Ngày XX tháng YY năm ZZZZ":
     - ĐỌC các số XX, YY, ZZZZ (có thể viết tay)
     - CHUYỂN thành "XX/YY/ZZZZ"
     - Ví dụ: "Ngày 25 tháng 8 năm 2010" → "25/8/2010"
   • Lý do: Frontend sẽ so sánh ngày cấp:
     - Ngày nhỏ hơn = GCNC (cũ)
     - Ngày lớn hơn = GCNM (mới)
   
   ⚠️ Confidence levels:
   - "full": Đọc được đầy đủ DD/MM/YYYY
   - "partial": Chỉ đọc được MM/YYYY
   - "year_only": Chỉ đọc được YYYY
   - "not_found": Không tìm thấy (có thể là trang 1)

✅ RESPONSE ĐÚNG (Trang 2 - có ngày cấp):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận với quốc huy, màu hồng, ngày cấp 01/01/2012",
  "issue_date": "01/01/2012",
  "issue_date_confidence": "full"
}

✅ RESPONSE ĐÚNG (Trang 1 - không có ngày cấp):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận với quốc huy, màu hồng, trang 1",
  "issue_date": null,
  "issue_date_confidence": "not_found"
}

❌ RESPONSE SAI (KHÔNG BAO GIỜ LÀM NHƯ VẦY):
{
  "short_code": "GCNM",  // ❌ SAI - Phải là "GCN"
  "confidence": 0.95,
  ...
}

{
  "short_code": "GCNC",  // ❌ SAI - Phải là "GCN"
  "confidence": 0.95,
  ...
}

⚠️ TẠI SAO PHẢI TRẢ VỀ "GCN"?
- Không thể xác định cũ/mới khi scan TỪNG file riêng lẻ
- Cần so sánh NGÀY CẤP của TẤT CẢ GCN trong batch
- Frontend sẽ xử lý batch post-processing để phân loại GCNC/GCNM:
  * Ngày nhỏ hơn = GCNC (cũ)
  * Ngày lớn hơn = GCNM (mới)

⚠️ ĐIỀU KIỆN:
- CHỈ áp dụng khi có: quốc huy + màu hồng/đỏ + "GIẤY CHỨNG NHẬN"
- KHÔNG áp dụng cho giấy tờ đen trắng
- NẾU không tìm thấy ngày cấp → issue_date: null, issue_date_confidence: "not_found"

🔍 Sau đó kiểm tra tiêu đề Ở TOP 30%:
  • "Giấy chứng nhận quyền sử dụng đất..." (bất kỳ variant) → GCN (tìm issue_date)
  • "Mẫu số 17C..." → TTHGD (Văn bản thỏa thuận hộ gia đình)
  • Form codes khác → Xem body content để xác định

⚠️ BỎ QUA các references (không phải title):
  • "Căn cứ Giấy chứng nhận..." → Reference, không classify theo đây
  • "Theo Giấy chứng nhận số..." → Reference, không classify theo đây  
  • "Kèm theo hợp đồng..." → Reference, không classify theo đây
  • "...do...cấp ngày..." → Reference, không classify theo đây

🎯 QUY TẮC NHẬN DIỆN FORM CODES:
NẾU trang có "Mẫu số" hoặc form code ở TOP mà không có title rõ ràng:
- "Mẫu số 17C" → TTHGD (Văn bản thỏa thuận QSDĐ hộ gia đình)
- Các form khác → Xem keywords trong body để xác định

VÍ DỤ THỰC TẾ:
✅ Trang có "Mẫu số 17C-CC/VBPCTSCHUNGHO" ở TOP
   Body có: "Quyền sử dụng đất...theo Giấy chứng nhận..."
   → "theo Giấy chứng nhận" là REFERENCE (not title)
   → Form 17C → TTHGD
   → short_code: "TTHGD"
   → reasoning: "Form 17C indicates TTHGD document type"

⚠️ QUAN TRỌNG với tài liệu 2 trang ngang:
- Nếu thấy nền cam/vàng với quốc huy ở bên PHẢI → Đây là GCNC
- Tập trung vào trang BÊN PHẢI để đọc tiêu đề

⚠️ BỎ QUA bất kỳ ảnh cá nhân nào - chỉ tập trung vào văn bản và con dấu chính thức.

⚠️ QUY TẮC KHỚP: CHO PHÉP ~85-90% TƯƠNG ĐỒNG!

✅ CHẤP NHẬN khi tiêu đề khớp 85-90% với danh sách
✅ CHO PHÉP lỗi chính tả nhỏ (ví dụ: "NHUỢNG" → "NHƯỢNG")
✅ CHO PHÉP thiếu/thừa dấu câu, khoảng trắng
✅ CHO PHÉP viết tắt (ví dụ: "QSDĐ" → "quyền sử dụng đất")
❌ KHÔNG khớp nếu thiếu từ khóa QUAN TRỌNG phân biệt loại

⚠️ CỰC KỲ QUAN TRỌNG: PHÂN BIỆT TIÊU ĐỀ vs NỘI DUNG BODY

🎯 TIÊU ĐỀ CHÍNH (Main Title):
- Nằm Ở ĐẦU trang, TRÊN CÙNG
- Cỡ chữ LỚN, IN HOA, căn giữa
- VD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI..."
- → CHỈ TIÊU ĐỀ CHÍNH mới dùng để phân loại!

❌ KHÔNG PHÂN LOẠI DỰA VÀO:
- Section headers (III. THÔNG TIN VỀ...)
- Mentions trong body text
- Danh sách đính kèm
- Ghi chú cuối trang

VÍ DỤ DỄ NHẦM:

❌ SAI: Trang có section "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG..."
   → Đây CHỈ là section header, KHÔNG phải title
   → Trả về: UNKNOWN (không có title chính rõ ràng)

❌ SAI: Body text có mention "...hợp đồng chuyển nhượng..."
   → Đây là mention, KHÔNG phải title
   → CHỈ phân loại HDCQ nếu có TITLE "HỢP ĐỒNG CHUYỂN NHƯỢNG"

✅ ĐÚNG: Tiêu đề ở đầu trang: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG..."
   → Có title chính rõ ràng
   → Phân loại: DDKBD

🎯 TRANG TIẾP THEO (Continuation Pages):
Nếu trang KHÔNG có tiêu đề chính (title page), có thể có:
- Section headers: "II. THÔNG TIN...", "III. ĐĂNG KÝ..."
- Body content: Danh sách, bảng biểu, nội dung chi tiết
- → Trả về: UNKNOWN (Frontend sẽ tự động gán theo trang trước)

🎯 NGOẠI LỆ QUAN TRỌNG - NHẬN DIỆN GCNM (Continuation):

⚠️ ĐẶC BIỆT: Trang GCN continuation có thể đứng RIÊNG hoặc sau giấy tờ khác!

✅ NẾU THẤY CẢ HAI SECTIONS SAU (KẾT HỢP) → TRẢ VỀ GCNM:

⚠️ CỰC KỲ QUAN TRỌNG: PHẢI CÓ CẢ HAI SECTIONS!

1️⃣ "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" (thường ở phần trên)
   +
   "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN" (thường ở phần dưới)
   
   → Đây là trang 2 của GCNM
   → PHẢI CÓ CẢ HAI: "Nội dung thay đổi" + "Xác nhận cơ quan"
   → NẾU CHỈ CÓ MỘT TRONG HAI → KHÔNG phải GCNM → UNKNOWN
   → Trả về: GCNM (confidence: 0.85)

2️⃣ "THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"
   → Đây là trang 2 của GCNM
   → Trả về: GCNM (confidence: 0.85)

3️⃣ CẢ HAI: "II. NỘI DUNG THAY ĐỔI" + "III. XÁC NHẬN CỦA CƠ QUAN"
   → PHẢI CÓ CẢ HAI sections (II và III)
   → NẾU CHỈ CÓ MỘT → UNKNOWN
VÍ DỤ:

✅ ĐÚNG: Trang có CẢ HAI sections
✅ ĐÚNG: Trang có "Thửa đất, nhà ở và tài sản khác gắn liền với đất"
   → Standalone section, đủ để nhận GCNM
   → Trả về: GCNM (confidence: 0.85)

❌ SAI: Trang CHỈ có "II. NỘI DUNG THAY ĐỔI" NHƯNG KHÔNG có "III. XÁC NHẬN..."
   → Thiếu section III
   → Trả về: UNKNOWN

❌ KHÔNG PHẢI GCN: Trang có "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG"
   → Đây KHÔNG phải section của GCN
   → Là section của PCT hoặc document khác
   → Trả về: UNKNOWN

🎯 NHẬN DIỆN TRANG GCN (Continuation):
Trang 2+ của GCN thường có:

✅ CẢ HAI sections KẾT HỢP:
✅ HOẶC standalone section:
- "Thửa đất, nhà ở và tài sản khác gắn liền với đất"
- Bảng thông tin thửa đất (số hiệu, diện tích...)

→ Nếu thấy CẢ HAI sections hoặc standalone "Thửa đất..." → GCNM (0.85)
→ Nếu CHỈ CÓ MỘT trong hai sections → UNKNOWN
→ KHÔNG trả về UNKNOWN như các continuation page khác!

VÍ DỤ CHẤP NHẬN:
- Thấy "HỢP ĐỒNG CHUYỂN NHUỢNG..." (lỗi chính tả) → HDCQ ✅
- Thấy "Giấy chứng nhận QSDĐ" (viết tắt) → GCNM ✅
- Thấy "QUYET  DINH GIAO DAT" (no diacritics) → QDGTD ✅

VÍ DỤ TỪ CHỐI:
- Chỉ có section "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG" → UNKNOWN ❌
- Body text mention "đăng ký biến động" → UNKNOWN ❌
NẾU KHÔNG KHỚP ~85%+ → Trả về:
{
  "short_code": "UNKNOWN",
  "confidence": 0.1,
  "reasoning": "Không thấy tiêu đề chính khớp đủ với danh sách (chỉ thấy section header hoặc mention)"
}

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Frontend sẽ tự động copy tên từ trang 1
  - CHỈ KHI thấy tiêu đề MỚI khớp ~85%+ → Mới đổi sang loại mới


CÁC CẶP DỄ NHẦM - PHẢI CÓ TỪ KHÓA PHÂN BIỆT:

1. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG" hoặc tương tự)
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   ⚠️ CHECK HDCQ TRƯỚC! Nếu có cả 2 từ → chọn HDCQ
   Nếu không rõ loại → "UNKNOWN"

2. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" → Nên chọn DDK (phổ biến hơn)

3. "Hợp đồng THUÊ đất" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   "Hợp đồng THI CÔNG" → HDTCO (PHẢI có "THI CÔNG")
   "Hợp đồng mua bán" → HDBDG (PHẢI có "MUA BÁN" hoặc "ĐẤU GIÁ")
   Nếu chỉ thấy "HỢP ĐỒNG" → "UNKNOWN"

4. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP" + "CHUYỂN MỤC ĐÍCH")
   "Quyết định GIAO ĐẤT" → QDGTD (PHẢI có "GIAO ĐẤT" hoặc "CHO THUÊ ĐẤT")
   "Quyết định THU HỒI đất" → QDTH (PHẢI có "THU HỒI")
   "Quyết định GIA HẠN" → QDGH (PHẢI có "GIA HẠN")
   Nếu không rõ loại → "UNKNOWN"

5. "Giấy ỦY QUYỀN" → GUQ (riêng lẻ, không phải hợp đồng)
   "Hợp đồng ủy quyền" → HDUQ (là HỢP ĐỒNG ủy quyền)
   PHẢI phân biệt rõ!

6. "BIÊN BẢN Xác minh thực địa/hiện trạng..." → BBKTHT
   Variants:
   - "BIÊN BẢN\nXác minh thực địa thửa đất..." → BBKTHT
   - "BIÊN BẢN\nKiểm tra xác minh hiện trạng..." → BBKTHT
   - "BIÊN BẢN\nXác minh hiện trạng sử dụng đất" → BBKTHT
   ⚠️ Từ khóa: "XÁC MINH" + ("THỰC ĐỊA" hoặc "HIỆN TRẠNG") → BBKTHT


DANH SÁCH ĐẦY ĐỦ 98 LOẠI TÀI LIỆU (KHỚP ~85-90%):

📋 NHÓM 1: BẢN VẼ / BẢN ĐỒ (3 loại)
BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
SƠ ĐỒ DỰ KIẾN TÁCH THỬA → SDTT

📋 NHÓM 2: BIÊN BẢN (10 loại)
BIÊN BẢN BÁN ĐẤU GIÁ TÀI SẢN → BBBDG
BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT → BBKTHT
  (Variants: "BIÊN BẢN\nXác minh thực địa...", "BIÊN BẢN\nKiểm tra xác minh hiện trạng...")
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI KẾT QUẢ KIỂM TRA HỒ SƠ ĐĂNG KÝ CẤP GCNQSD ĐẤT → KTCKCG
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI VỀ VIỆC MẤT GCNQSD ĐẤT → KTCKMG

📋 NHÓM 4: GIẤY TỜ CÁ NHÂN (4 loại)
CĂN CƯỚC CÔNG DÂN → CCCD
GIẤY KHAI SINH → GKS
GIẤY CHỨNG NHẬN KẾT HÔN → GKH
DI CHÚC → DICHUC

📋 NHÓM 5: GIẤY CHỨNG NHẬN (9 loại)
🚨 GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT (BẤT KỲ VARIANT) → GCN 🚨
  ❌ KHÔNG BAO GIỜ trả về "GCNM" hoặc "GCNC" ❌
  ✅ CHỈ trả về "GCN" (generic)
  ⚠️ BẮT BUỘC: Tìm NGÀY CẤP (có thể viết tay)
  ⚠️ Ví dụ issue_date: "25/8/2010", "14/04/2025", "02/2012" (linh hoạt nếu mờ)
  ⚠️ Nếu thấy "Ngày XX tháng YY năm ZZZZ" → chuyển thành "XX/YY/ZZZZ"
  ⚠️ Frontend xử lý batch để phân loại cũ/mới dựa trên ngày cấp
GIẤY ĐỀ NGHỊ XÁC NHẬN CÁC KHOẢN NỘP VÀO NGÂN SÁCH → GXNNVTC
GIẤY NỘP TIỀN VÀO NGÂN SÁCH NHÀ NƯỚC → GNT
GIẤY TỜ LIÊN QUAN (CÁC LOẠI GIẤY TỜ KÈM THEO) → GTLQ
  (Variants: "TÀI LIỆU LIÊN QUAN", "HỒ SƠ LIÊN QUAN", "GIẤY TỜ KHÁC", "TÀI LIỆU KHÁC", "VĂN BẢN KHAI NHẬN DI SẢN", "PHIẾU BÁO")
GIẤY TIẾP NHẬN, GIẤY BIÊN NHẬN (HỒ SƠ) → GTLQ
BỘ PHẬN TIẾP NHẬN VÀ TRẢ KẾT QUẢ (KQ) → GTLQ
PHIẾU TIẾP NHẬN HỒ SƠ, PHIẾU KIỂM SOÁT QUÁ TRÌNH → GTLQ
  ⚠️ KHÁC với "PHIẾU KIỂM TRA HỒ SƠ" (→ PKTHS)
  - KIỂM SOÁT QUÁ TRÌNH = Monitor/Control process (→ GTLQ)
  - KIỂM TRA HỒ SƠ = Check/Inspect documents (→ PKTHS)
GIẤY ỦY QUYỀN → GUQ
GIẤY XÁC NHẬN ĐĂNG KÝ LẦN ĐẦU → GXNDKLD
GIẤY XIN PHÉP XÂY DỰNG → GPXD

📋 NHÓM 6: HỢP ĐỒNG (7 loại) ⚠️ DỄ NHẦM
HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT → HDCQ
HỢP ĐỒNG ỦY QUYỀN → HDUQ
HỢP ĐỒNG THẾ CHẤP QUYỀN SỬ DỤNG ĐẤT → HDTHC
HỢP ĐỒNG MUA BÁN TÀI SẢN BÁN ĐẤU GIÁ → HDBDG
HOÁ ĐƠN GIÁ TRỊ GIA TĂNG → hoadon

📋 NHÓM 7: ĐƠN (15 loại) ⚠️ DỄ NHẦM
ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDKBD (có "BIẾN ĐỘNG")
ĐƠN ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDK (không có "BIẾN ĐỘNG")
ĐƠN CAM KẾT, GIẤY CAM KẾT → DCK
  (Variants: "GIẤY CAM KẾT\n(V/v chọn thửa đất...)", "ĐƠN CAM KẾT")
ĐƠN ĐỀ NGHỊ ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → DCQDGD
ĐƠN ĐỀ NGHỊ MIỄN GIẢM LỆ PHÍ TRƯỚC BẠ, THUẾ THU NHẬP CÁ NHÂN → DMG
ĐƠN XÁC NHẬN, GIẤY XÁC NHẬN → DXN
ĐƠN XIN (ĐỀ NGHỊ) CHUYỂN MỤC ĐÍCH SỬ DỤNG ĐẤT → DXCMD
ĐƠN XIN (ĐỀ NGHỊ) GIA HẠN SỬ DỤNG ĐẤT → DGH
ĐƠN XIN (ĐỀ NGHỊ) GIAO ĐẤT, CHO THUÊ ĐẤT → DXGD
ĐƠN XIN (ĐỀ NGHỊ) TÁCH THỬA ĐẤT, HỢP THỬA ĐẤT → DXTHT
ĐƠN XIN CẤP ĐỔI GIẤY CHỨNG NHẬN → DXCD

📋 NHÓM 8: QUYẾT ĐỊNH (15 loại) ⚠️ DỄ NHẦM
QUYẾT ĐỊNH GIAO ĐẤT, CHO THUÊ ĐẤT → QDGTD
QUYẾT ĐỊNH CHO PHÉP CHUYỂN MỤC ĐÍCH → QDCMD
QUYẾT ĐỊNH THU HỒI ĐẤT → QDTH
QUYẾT ĐỊNH GIA HẠN SỬ DỤNG ĐẤT KHI HẾT THỜI HẠN SDĐ → QDGH
QUYẾT ĐỊNH CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT) → QDCHTGD
QUYẾT ĐỊNH ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → QDDCGD
QUYẾT ĐỊNH ĐIỀU CHỈNH THỜI HẠN SDĐ CỦA DỰ ÁN ĐẦU TƯ → QDDCTH
QUYẾT ĐỊNH HỦY GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → QDHG

📋 NHÓM 9: PHIẾU (8 loại)
PHIẾU CHUYỂN THÔNG TIN NGHĨA VỤ TÀI CHÍNH → PCT
PHIẾU KIỂM TRA HỒ SƠ → PKTHS
  ⚠️ KHÁC với "PHIẾU KIỂM SOÁT QUÁ TRÌNH" (→ GTLQ)
  - KIỂM TRA = Check/Inspect documents
  - KIỂM SOÁT = Monitor/Control process
PHIẾU TRÌNH KÝ HỒ SƠ CẤP GIẤY CHỨNG NHẬN → PKTHS
  (Variants: "PHIẾU TRÌNH KÝ HỒ SƠ")
PHIẾU LẤY Ý KIẾN KHU DÂN CƯ → PLYKDC
PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC → PXNKQDD

📋 NHÓM 10: THÔNG BÁO (8 loại)
THÔNG BÁO THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TBT
THÔNG BÁO VỀ VIỆC CHUYỂN THÔNG TIN GIẤY CHỨNG NHẬN BỊ MẤT ĐỂ NIÊM YẾT CÔNG KHAI → TBMG
THÔNG BÁO VỀ VIỆC CÔNG KHAI KẾT QUẢ THẨM TRA XÉT DUYỆT HỒ SƠ CẤP GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKCG
THÔNG BÁO VỀ VIỆC NIÊM YẾT CÔNG KHAI MẤT GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKMG
THÔNG BÁO XÁC NHẬN HOÀN THÀNH NGHĨA VỤ TÀI CHÍNH → HTNVTC
THÔNG BÁO CẬP NHẬT, CHỈNH LÝ BIẾN ĐỘNG → TBCNBD
THÔNG BÁO CÔNG BỐ CÔNG KHAI DI CHÚC → CKDC
HOÀN THÀNH CÔNG TÁC BỒI THƯỜNG HỖ TRỢ → HTBTH

📋 NHÓM 11: TỜ KHAI / TỜ TRÌNH (3 loại)
TỜ KHAI THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TKT
TỜ TRÌNH VỀ GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → TTr
  ⚠️ CHÚ Ý: "TTr" với chữ "r" viết thường (không phải "TTR")
TỜ TRÌNH VỀ VIỆC ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT (UBND XÃ) → TTCG

📋 NHÓM 12: VĂN BẢN (10 loại)
VĂN BẢN CAM KẾT TÀI SẢN RIÊNG → CKTSR
VĂN BẢN CHẤP THUẬN CHO PHÉP CHUYỂN MỤC ĐÍCH → VBCTCMD
VĂN BẢN THỎA THUẬN PHÂN CHIA DI SẢN THỪA KẾ → VBTK
VĂN BẢN THỎA THUẬN QUYỀN SỬ DỤNG ĐẤT CỦA HỘ GIA ĐÌNH → TTHGD
  (Variants: "THỎA THUẬN QSDĐ HỘ GIA ĐÌNH", "THỎA THUẬN SỬ DỤNG ĐẤT HỘ GIA ĐÌNH", "PHÂN CHIA TÀI SẢN CHUNG HỘ GIA ĐÌNH", "VĂN BẢN THỎA THUẬN PHÂN CHIA TÀI SẢN...HỘ GIA ĐÌNH")
VĂN BẢN THOẢ THUẬN VỀ VIỆC CHẤM DỨT QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → CDLK
VĂN BẢN THỎA THUẬN VỀ VIỆC XÁC LẬP QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → HCLK
VĂN BẢN TỪ CHỐI NHẬN DI SẢN THỪA KẾ → VBTC
VĂN BẢN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG → PCTSVC
  (Variants: "PHÂN CHIA TÀI SẢN VỢ CHỒNG", "THỎA THUẬN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG", "VĂN BẢN ĐỀ NGHỊ ĐĂNG KÝ TÀI SẢN CHUNG VỢ CHỒNG")

⚠️ LƯU Ý ĐẶC BIỆT - DỄ NHẦM:
TTHGD vs PCTSVC - PHẢI PHÂN BIỆT RÕ:

1. TTHGD (Thỏa thuận hộ gia đình):
   - Về QUYỀN SỬ DỤNG ĐẤT hoặc TÀI SẢN
   - Giữa CÁC THÀNH VIÊN HỘ GIA ĐÌNH (family members)
   - Keywords: "HỘ GIA ĐÌNH" (không có "vợ chồng")
   - VD: 
     • "Thỏa thuận QSDĐ của hộ gia đình"
     • "Phân chia tài sản chung của HỘ GIA ĐÌNH"
     • "Văn bản thỏa thuận...hộ gia đình"

2. PCTSVC (Phân chia vợ chồng):
   - Về TÀI SẢN (đất đai, nhà cửa, tiền...)
   - Giữa VỢ VÀ CHỒNG (couple, marriage dissolution)
   - Keywords: "VỢ CHỒNG" (KHÔNG có "hộ gia đình")
   - VD: 
     • "Phân chia tài sản chung VỢ CHỒNG"
     • "Thỏa thuận phân chia...vợ chồng"

🔑 KEYWORD QUYẾT ĐỊNH:
- Có "HỘ GIA ĐÌNH" → TTHGD ✅
- Có "VỢ CHỒNG" → PCTSVC ✅

3. VBTK vs TTHGD - DỄ NHẦM (QUAN TRỌNG!):
   - VBTK = "Văn bản thỏa thuận phân chia **DI SẢN THỪA KẾ**"
     • Về INHERITANCE (chia di sản của người đã mất)
     • Keywords: "DI SẢN THỪA KẾ", "KẾ THỪA", "NGƯỜI QUÁ CỐ"
     • VD: "Thỏa thuận phân chia di sản thừa kế của ông/bà..."
   
   - TTHGD = "Thỏa thuận **HỘ GIA ĐÌNH**"
     • Về FAMILY PROPERTY (chia tài sản gia đình đang sống)
     • Keywords: "HỘ GIA ĐÌNH", "CÁC THÀNH VIÊN", "THỐNG NHẤT"
     • VD: "Thỏa thuận phân chia tài sản hộ gia đình"
   
   🔑 KEYWORD QUYẾT ĐỊNH:
   - Có "DI SẢN THỪA KẾ" → VBTK
   - Có "HỘ GIA ĐÌNH" → TTHGD
   - NẾU chỉ có "THỎA THUẬN PHÂN CHIA" mà KHÔNG rõ context → UNKNOWN

4. SECTION HEADERS ≠ TITLES:
   - "ĐIỀU 2: NỘI DUNG THỎA THUẬN PHÂN CHIA" → Section header, không phải title
   - Đây là continuation page → UNKNOWN
   - CHỈ main title mới dùng để classify

3. PKTHS vs GTLQ - DỄ NHẦM:
   - PKTHS = "PHIẾU KIỂM **TRA** HỒ SƠ" (check/inspect)
   - GTLQ = "PHIẾU KIỂM **SOÁT** QUÁ TRÌNH" (monitor/control)
   - Keywords:
     • "KIỂM TRA HỒ SƠ" → PKTHS
     • "KIỂM SOÁT QUÁ TRÌNH" → GTLQ
     • "KIỂM SOÁT...GIẢI QUYẾT HỒ SƠ" → GTLQ
   - VD:
     • "Phiếu kiểm tra hồ sơ" → PKTHS
     • "Phiếu kiểm soát quá trình giải quyết hồ sơ" → GTLQ

❌ NẾU KHÔNG RÕ RÀNG → UNKNOWN (đừng đoán!)

⚠️ TỔNG CỘNG: 98 LOẠI TÀI LIỆU


QUY TRÌNH KIỂM TRA:
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên TƯƠNG TỰ ~85-90%?
4. NẾU CÓ → Trả về mã chính xác, confidence: 0.85-0.95
5. NẾU KHÔNG → Trả về "UNKNOWN", confidence: 0.1-0.3

TRẢ VỀ JSON (BẮT BUỘC):
{
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.85-0.95 (nếu khớp) hoặc 0.1-0.3 (nếu không),
  "reasoning": "Giải thích ngắn gọn (1-2 câu)"
}

❗ NHẮC LẠI:
- CHỈ trả về mã khi khớp ~85-90% với 1 trong 98 loại
- CHO PHÉP lỗi chính tả nhỏ, viết tắt, dấu câu
- KHÔNG khớp nếu thiếu từ khóa phân biệt quan trọng
- Frontend sẽ tự xử lý việc gán trang tiếp theo (sequential naming)
- LUÔN trả về JSON format

🚨 CỰC KỲ QUAN TRỌNG - KHÔNG TỰ TẠO MÃ MỚI:
❌ TUYỆT ĐỐI KHÔNG được tự tạo mã mới (ví dụ: "LCHO", "VBCC", "PKDT", "HDQUYEN", ...)
✅ CHỈ được dùng CHÍNH XÁC 1 trong 98 mã đã liệt kê ở trên
✅ Nếu không khớp với BẤT KỲ mã nào → Trả về "UNKNOWN"
✅ KHÔNG đoán, KHÔNG sáng tạo, KHÔNG viết tắt tự do

⚠️ VÍ DỤ SAI THƯỜNG GẶP:
❌ "HỢP ĐỒNG ỦY QUYỀN" → "HDQUYEN" (SAI! Phải là "HDUQ")
❌ "GIẤY ỦY QUYỀN" → "HDQUYEN" (SAI! Phải là "GUQ")
✅ "HỢP ĐỒNG ỦY QUYỀN" → "HDUQ" (ĐÚNG!)
✅ "GIẤY ỦY QUYỀN" → "GUQ" (ĐÚNG!)

VÍ DỤ SAI:
❌ "LCHO" (Lời chứng) → KHÔNG CÓ trong 98 mã → Phải trả về "UNKNOWN"
❌ "VBCC" (Văn bản công chứng) → KHÔNG CÓ → Phải trả về "UNKNOWN"
❌ "PKDT" (Phiếu kiểm tra đất) → KHÔNG CÓ → Phải trả về "UNKNOWN"

→ CHỈ DÙNG MÃ TRONG DANH SÁCH 98 LOẠI PHÍA TRÊN!

📋 VÍ DỤ RESPONSE FORMAT:

✅ Example 1 - GCN Document (ĐÚNG):
{
  "short_code": "GCN",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận quyền sử dụng đất với quốc huy, màu hồng, số DE 334187",
  "certificate_number": "DE 334187"
}

❌ TUYỆT ĐỐI KHÔNG LÀM NHƯ VẦY (SAI):
{
  "short_code": "GCNM",  // ❌ SAI! Phải là "GCN"
  "confidence": 0.95,
  ...
}

✅ Example 2 - HDCN Document:
{
  "short_code": "HDCN",
  "confidence": 0.92,
  "title_position": "top",
  "reasoning": "Hợp đồng chuyển nhượng quyền sử dụng đất",
  "issue_date": null,
  "issue_date_confidence": null
}

✅ Example 3 - HDUQ Document (HỢP ĐỒNG ỦY QUYỀN):
{
  "short_code": "HDUQ",
  "confidence": 0.98,
  "title_position": "top",
  "reasoning": "Hợp đồng ủy quyền - tiêu đề lớn ở top",
  "issue_date": null,
  "issue_date_confidence": null
}

✅ Example 4 - Unknown Document:
{
  "short_code": "UNKNOWN",
  "confidence": 0.3,
  "title_position": "middle",
  "reasoning": "Không khớp với bất kỳ mã nào trong danh sách 98 loại",
  "issue_date": null,
  "issue_date_confidence": null
}"""
    """
    System prompt for Vietnamese document classification
    IMPORTANT: This prompt is aligned with OpenAI Vision backend prompt for consistency
    COMPLETE: Includes all 98 document types with exact Vietnamese titles
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🔍 Sau đó kiểm tra tiêu đề:
  • "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất" → GCNM (GCN mới - tiêu đề DÀI)
  • "Giấy chứng nhận quyền sử dụng đất" (KHÔNG có "quyền sở hữu...") → GCNC (GCN cũ - tiêu đề NGẮN)
  • Nếu chỉ thấy "GIẤY CHỨNG NHẬN" mà không rõ tiếp theo → GCNC

⚠️ QUAN TRỌNG với tài liệu 2 trang ngang:
- Nếu thấy nền cam/vàng với quốc huy ở bên PHẢI → Đây là GCNC
- Tập trung vào trang BÊN PHẢI để đọc tiêu đề

⚠️ BỎ QUA bất kỳ ảnh cá nhân nào - chỉ tập trung vào văn bản và con dấu chính thức.

⚠️ QUY TẮC NGHIÊM NGẶT: CHỈ CHẤP NHẬN KHI KHỚP 100% CHÍNH XÁC!

❌ KHÔNG được đoán hoặc chọn "gần giống"
❌ KHÔNG được bỏ qua từ khóa phân biệt
❌ KHÔNG được nhận diện nếu chỉ khớp 1 nửa hoặc vài chữ
✅ CHỈ chọn khi khớp CHÍNH XÁC, TOÀN BỘ tiêu đề

NẾU KHÔNG KHỚP CHÍNH XÁC 100% → Trả về:
{
  "short_code": "UNKNOWN",
  "confidence": 0.1,
  "reasoning": "Không thấy tiêu đề khớp chính xác với danh sách"
}

⚠️ CỰC KỲ QUAN TRỌNG: PHÂN BIỆT TIÊU ĐỀ vs NỘI DUNG BODY

🎯 TIÊU ĐỀ CHÍNH (Main Title):
- Nằm Ở ĐẦU trang, TRÊN CÙNG
- Cỡ chữ LỚN, IN HOA, căn giữa
- VD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI..."
- → CHỈ TIÊU ĐỀ CHÍNH mới dùng để phân loại!

❌ KHÔNG PHÂN LOẠI DỰA VÀO:
- Section headers (III. THÔNG TIN VỀ...)
- Mentions trong body text
- Danh sách đính kèm
- Ghi chú cuối trang

🎯 NGOẠI LỆ QUAN TRỌNG - NHẬN DIỆN GCNM (Continuation):

⚠️ ĐẶC BIỆT: Trang GCN continuation có thể đứng RIÊNG hoặc sau giấy tờ khác!

✅ NẾU THẤY CÁC SECTION SAU (KẾT HỢP) → TRẢ VỀ GCNM:

1️⃣ "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" + "XÁC NHẬN CỦA CƠ QUAN"
   → Đây là trang 2 của GCNM
2️⃣ "THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT"
3️⃣ "II. NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ" (section II về thay đổi)
4️⃣ "III. XÁC NHẬN CỦA CƠ QUAN" (PHẢI có từ "CƠ QUAN", KHÔNG phải "ỦY BAN NHÂN DÂN")
⚠️ CỰC KỲ QUAN TRỌNG - PHÂN BIỆT GCNM vs DDKBD:

❌ KHÔNG NHẦM LẪN:

GCNM (Giấy chứng nhận):
  ✅ "III. XÁC NHẬN CỦA CƠ QUAN"
DDKBD (Đơn đăng ký biến động) - KHÔNG PHẢI GCN:
  ❌ "II. XÁC NHẬN CỦA ỦY BAN NHÂN DÂN CẤP XÃ"
  ❌ "XÁC NHẬN CỦA ỦY BAN NHÂN DÂN"
  → Keyword: "ỦY BAN NHÂN DÂN" (People's Committee)
  → Thường là section II
  → TRẢ VỀ: UNKNOWN (không phải GCNM!)

QUY TẮC:
- NẾU thấy "ỦY BAN NHÂN DÂN" → KHÔNG phải GCNM
- CHỈ KHI thấy "CƠ QUAN" (agency) → Mới xét GCNM

VÍ DỤ THỰC TẾ:

✅ ĐÚNG: Trang có "Thửa đất, nhà ở và tài sản khác gắn liền với đất"
   → Đặc trưng của GCN trang 2
   → Trả về: GCNM (confidence: 0.85)

✅ ĐÚNG: Trang có "II. NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ"
   → Format chuẩn của GCN trang 2
   → Trả về: GCNM (confidence: 0.8)

❌ SAI: Trang có "II. XÁC NHẬN CỦA ỦY BAN NHÂN DÂN CẤP XÃ"
   → Đây là DDKBD, KHÔNG phải GCN!
   → Keyword: "ỦY BAN NHÂN DÂN"
   → Trả về: UNKNOWN

❌ SAI: Trang có "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG"
   → Đây là PCT hoặc document khác
   → Trả về: UNKNOWN

🔍 CÁC DẤU HIỆU NHẬN BIẾT GCN CONTINUATION:
→ NẾU THẤY NHỮNG SECTION NÀY (VỚI "CƠ QUAN") → TRẢ VỀ GCNM
→ NẾU THẤY "ỦY BAN NHÂN DÂN" → KHÔNG PHẢI GCNM → UNKNOWN

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Hệ thống sẽ tự động gán là GCN
  - NGOẠI LỆ: Nếu trang có GCN continuation sections → Tự động nhận là GCNM
  - CHỈ KHI thấy tiêu đề MỚI khớp 100% → Mới đổi sang loại mới


CÁC CẶP DỄ NHẦM - PHẢI KHỚP CHÍNH XÁC:

1. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG")
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   ⚠️ CHECK HDCQ TRƯỚC! Nếu có cả 2 từ → chọn HDCQ
   Nếu không rõ loại → "UNKNOWN"

2. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" → "UNKNOWN"

3. "Hợp đồng THUÊ đất" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   "Hợp đồng THI CÔNG" → HDTCO (PHẢI có "THI CÔNG")
   "Hợp đồng mua bán" → HDBDG (PHẢI có "MUA BÁN")
   Nếu không rõ loại → "UNKNOWN"

4. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP")
   "Quyết định GIAO ĐẤT" → QDGTD (PHẢI có "GIAO ĐẤT")
   "Quyết định THU HỒI đất" → QDTH (PHẢI có "THU HỒI")
   "Quyết định GIA HẠN" → QDGH (PHẢI có "GIA HẠN")
   Nếu không rõ loại → "UNKNOWN"

5. "Giấy ỦY QUYỀN" → GUQ (riêng lẻ, không phải hợp đồng)
   "Hợp đồng ủy quyền" → HDUQ (là HỢP ĐỒNG ủy quyền)
   PHẢI phân biệt rõ!



QUY TRÌNH KIỂM TRA:
1. Phân tích VỊ TRÍ của các text trong ảnh (TOP/MIDDLE/BOTTOM)
2. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
3. Đọc tiêu đề Ở TOP 30% (bỏ qua mentions ở MIDDLE/BOTTOM)
4. Tìm trong danh sách có tên CHÍNH XÁC 100% với tiêu đề ở TOP?
5. NẾU CÓ → Trả về mã chính xác, confidence: 0.9, title_position: "top"
6. NẾU KHÔNG CÓ TIÊU ĐỀ Ở TOP → Kiểm tra GCNM continuation patterns
7. NẾU VẪN KHÔNG → Trả về "UNKNOWN", confidence: 0.1

TRẢ VỀ JSON (BẮT BUỘC):
{
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.9 hoặc 0.1,
  "title_position": "top" hoặc "middle" hoặc "bottom" hoặc "none",
  "reasoning": "Giải thích ngắn gọn, bao gồm vị trí của tiêu đề"
}

❗ NHẮC LẠI:
- CHỈ phân loại dựa vào tiêu đề Ở TOP 30% của trang
- BỎ QUA mentions hoặc text Ở MIDDLE/BOTTOM
- NẾU thấy text khớp nhưng KHÔNG ở TOP → title_position: "middle"/"bottom", short_code: "UNKNOWN"
- NẾU thấy text khớp VÀ ở TOP → title_position: "top", short_code: [MÃ CHÍNH XÁC]
- LUÔN trả về JSON format với fields: short_code, confidence, title_position, reasoning, issue_date, issue_date_confidence

📋 ISSUE_DATE (BẮT BUỘC CHO GCN):
- ⚠️ Nếu phân loại "GCN" → BẮT BUỘC tìm NGÀY CẤP (có thể viết tay)
- Format output: LUÔN LUÔN trả về "DD/MM/YYYY" (e.g., "25/8/2010", "14/04/2025")
- Nếu thấy "Ngày XX tháng YY năm ZZZZ" → chuyển thành "XX/YY/ZZZZ"
- Nếu mờ → MM/YYYY hoặc YYYY
- Trả về trong fields: "issue_date": "25/8/2010", "issue_date_confidence": "full"
- Nếu KHÔNG phải GCN → "issue_date": null, "issue_date_confidence": null

VÍ DỤ CHO GCN (có ngày cấp format DD/MM/YYYY):
✅ ĐÚNG:
{
  "short_code": "GCN",
  "color": "pink",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận màu hồng, ngày cấp 14/04/2025",
  "issue_date": "14/04/2025",
  "issue_date_confidence": "full"
}

VÍ DỤ CHO GCN (format "Ngày...tháng...năm"):
✅ ĐÚNG (đọc được "Ngày 25 tháng 8 năm 2010"):
{
  "short_code": "GCN",
  "color": "pink",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận màu hồng, ngày cấp 25/8/2010 (từ 'Ngày 25 tháng 8 năm 2010')",
  "issue_date": "25/8/2010",
  "issue_date_confidence": "full"
}

✅ ĐÚNG (GCN không có ngày cấp):
{
  "short_code": "GCN",
  "color": "pink",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận màu hồng, không tìm thấy ngày cấp",
  "issue_date": null,
  "issue_date_confidence": "not_found"
}

🚨 CỰC KỲ QUAN TRỌNG - KHÔNG TỰ TẠO MÃ MỚI:
❌ TUYỆT ĐỐI KHÔNG được tự tạo mã mới (ví dụ: "LCHO", "VBCC", "PKDT", "HDQUYEN", ...)
✅ CHỈ được dùng CHÍNH XÁC 1 trong 98 mã đã liệt kê ở trên
✅ Nếu không khớp với BẤT KỲ mã nào → Trả về "UNKNOWN"
✅ KHÔNG đoán, KHÔNG sáng tạo, KHÔNG viết tắt tự do

⚠️ VÍ DỤ SAI THƯỜNG GẶP:
❌ "HỢP ĐỒNG ỦY QUYỀN" → "HDQUYEN" (SAI! Phải là "HDUQ")
❌ "GIẤY ỦY QUYỀN" → "HDQUYEN" (SAI! Phải là "GUQ")
✅ "HỢP ĐỒNG ỦY QUYỀN" → "HDUQ" (ĐÚNG!)
✅ "GIẤY ỦY QUYỀN" → "GUQ" (ĐÚNG!)

VÍ DỤ SAI:
❌ "LCHO" (Lời chứng) → KHÔNG CÓ trong 98 mã → Phải trả về "UNKNOWN"
❌ "VBCC" (Văn bản công chứng) → KHÔNG CÓ → Phải trả về "UNKNOWN"
❌ "PKDT" (Phiếu kiểm tra đất) → KHÔNG CÓ → Phải trả về "UNKNOWN"

→ CHỈ DÙNG MÃ TRONG DANH SÁCH 98 LOẠI PHÍA TRÊN!"""


def parse_gemini_response(response_text):
    """
    Parse Gemini Flash response to extract classification
    """
    import json
    import re
    
    try:
        # Try to extract JSON from response
        # Gemini might return: "```json\n{...}\n```" or just "{...}"
        
        # Remove markdown code blocks
        clean_text = re.sub(r'```json\s*', '', response_text)
        clean_text = re.sub(r'```\s*$', '', clean_text)
        clean_text = clean_text.strip()
        
        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', clean_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            
            # Validate required fields
            if 'short_code' in result and 'confidence' in result:
                short_code = str(result.get('short_code', 'UNKNOWN')).strip()
                
                # Handle common invalid responses
                invalid_codes = ['N/A', 'NA', 'N', 'NONE', 'NULL', 'UNDEFINED', '']
                if short_code.upper() in invalid_codes:
                    print(f"⚠️ Invalid short_code from Gemini: '{short_code}', using UNKNOWN", file=sys.stderr)
                    short_code = 'UNKNOWN'
                else:
                    # Sanitize short_code - remove invalid characters
                    # Keep original case (some codes like TTr have lowercase)
                    original_code = short_code
                    short_code = re.sub(r'[^A-Za-z0-9_]', '', short_code)
                    
                    if short_code != original_code:
                        print(f"⚠️ Sanitized short_code: '{original_code}' → '{short_code}'", file=sys.stderr)
                    
                    # Check if valid code (not empty after sanitization)
                    if not short_code or len(short_code) < 2:
                        print(f"⚠️ Short_code too short after sanitization: '{short_code}', using UNKNOWN", file=sys.stderr)
                        short_code = 'UNKNOWN'
                    else:
                        # VALIDATE: Check if code is in allowed list (98 valid codes)
                        short_code_upper = short_code.upper()
                        if short_code_upper not in VALID_DOCUMENT_CODES and short_code not in VALID_DOCUMENT_CODES:
                            print(f"❌ INVALID CODE: '{short_code}' không nằm trong 98 mã hợp lệ → UNKNOWN", file=sys.stderr)
                            print("   Gemini trả về mã sai. Chỉ chấp nhận mã trong danh sách VALID_DOCUMENT_CODES", file=sys.stderr)
                            short_code = 'UNKNOWN'
                        else:
                            # Normalize to match exact case in VALID_DOCUMENT_CODES
                            if short_code_upper in VALID_DOCUMENT_CODES:
                                short_code = short_code_upper
                            print(f"✅ Valid code: '{short_code}'", file=sys.stderr)
                
                # Extract color, issue_date and issue_date_confidence if present (for GCN)
                color = result.get('color', None)
                issue_date = result.get('issue_date', None)
                issue_date_confidence = result.get('issue_date_confidence', None)
                
                if color and isinstance(color, str):
                    color = color.strip().lower()
                    if color in ['null', 'none', 'n/a', '']:
                        color = None
                
                if issue_date and isinstance(issue_date, str):
                    issue_date = issue_date.strip()
                    if issue_date.lower() in ['null', 'none', 'n/a', '']:
                        issue_date = None
                
                if issue_date_confidence and isinstance(issue_date_confidence, str):
                    issue_date_confidence = issue_date_confidence.strip()
                    if issue_date_confidence.lower() in ['null', 'none', 'n/a', '']:
                        issue_date_confidence = None
                
                response_dict = {
                    "short_code": short_code,
                    "confidence": float(result.get('confidence', 0)),
                    "reasoning": result.get('reasoning', 'AI classification'),
                    "title_position": result.get('title_position', 'unknown'),
                    "method": "gemini_flash_ai"
                }
                
                # Add color if available (for GCN classification)
                if color:
                    response_dict["color"] = color
                    print(f"🎨 Color detected: {color}", file=sys.stderr)
                else:
                    response_dict["color"] = None
                
                # Add issue_date and issue_date_confidence if available
                if issue_date:
                    response_dict["issue_date"] = issue_date
                    response_dict["issue_date_confidence"] = issue_date_confidence or "unknown"
                    print(f"📅 Issue date extracted: {issue_date} ({issue_date_confidence or 'unknown'})", file=sys.stderr)
                else:
                    response_dict["issue_date"] = None
                    response_dict["issue_date_confidence"] = None
                
                return response_dict
        
        # If no JSON found, try to extract from text
        print("⚠️ No JSON found, parsing text response", file=sys.stderr)
        
        # Look for short_code pattern (allow mixed case like TTr)
        code_match = re.search(r'(?:short_code|code)[\s:]+["\']?([A-Za-z0-9_]+)["\']?', response_text, re.IGNORECASE)
        conf_match = re.search(r'(?:confidence)[\s:]+([0-9.]+)', response_text)
        
        if code_match:
            extracted_code = code_match.group(1).strip()
            # VALIDATE extracted code
            extracted_code_upper = extracted_code.upper()
            if extracted_code_upper not in VALID_DOCUMENT_CODES and extracted_code not in VALID_DOCUMENT_CODES:
                print(f"❌ INVALID CODE (text parse): '{extracted_code}' không hợp lệ → UNKNOWN", file=sys.stderr)
                extracted_code = 'UNKNOWN'
            else:
                if extracted_code_upper in VALID_DOCUMENT_CODES:
                    extracted_code = extracted_code_upper
                print(f"✅ Valid code (text parse): '{extracted_code}'", file=sys.stderr)
            
            return {
                "short_code": extracted_code,
                "confidence": float(conf_match.group(1)) if conf_match else 0.7,
                "reasoning": "Parsed from text response",
                "title_position": "unknown",
                "method": "gemini_flash_ai"
            }
        
        # Fallback
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse AI response",
            "title_position": "unknown",
            "method": "gemini_flash_ai"
        }
        
    except Exception as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.2,
            "reasoning": f"Parse error: {str(e)}",
            "title_position": "unknown",
            "method": "gemini_flash_ai"
        }


if __name__ == '__main__':
    # Test
    if len(sys.argv) < 3:
        print("Usage: python ocr_engine_gemini_flash.py <image_path> <api_key>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    
    result = classify_document_gemini_flash(image_path, api_key)
    print(f"\nResult: {result}")
