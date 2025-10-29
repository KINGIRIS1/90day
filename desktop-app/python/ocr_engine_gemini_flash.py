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


def classify_document_gemini_flash(image_path, api_key, crop_top_percent=0.35):
    """
    Classify Vietnamese land document using Gemini Flash 2.0 AI
    
    Args:
        image_path: Path to image file
        api_key: Google API key (BYOK)
        crop_top_percent: Percentage of top image to process (default 0.35 = 35%)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning
    """
    try:
        import requests
        
        # Read and crop image to top portion (where title/header usually is)
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Crop to top N% (default 35%)
            crop_height = int(height * crop_top_percent)
            cropped_img = img.crop((0, 0, width, crop_height))
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format=img.format or 'PNG')
            image_content = img_byte_arr.getvalue()
            
            print(f"🖼️ Image cropped: {width}x{height} → {width}x{crop_height} (top {int(crop_top_percent*100)}%)", file=sys.stderr)
        
        # Encode to base64
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        # Use direct REST API - v1beta is the standard API version
        # Model: gemini-2.5-flash (latest stable Flash model)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Create request payload
        payload = {
            "contents": [{
                "parts": [
                    {"text": get_classification_prompt()},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_image
                        }
                    }
                ]
            }]
        }
        
        print(f"📡 Sending request to Gemini Flash...", file=sys.stderr)
        
        # Send request
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            error_msg = f"API error {response.status_code}: {response.text[:200]}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {
                "short_code": "ERROR",
                "confidence": 0,
                "reasoning": error_msg
            }
        
        result_data = response.json()
        
        # Extract text from response
        if 'candidates' in result_data and len(result_data['candidates']) > 0:
            candidate = result_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    result_text = parts[0]['text']
                    print(f"🤖 Gemini response: {result_text[:200]}...", file=sys.stderr)
                    
                    # Parse result
                    classification = parse_gemini_response(result_text)
                    return classification
        
        # No valid response
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse Gemini response"
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


def get_classification_prompt():
    """
    System prompt for Vietnamese document classification
    IMPORTANT: This prompt is aligned with OpenAI Vision backend prompt for consistency
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Hệ thống sẽ tự động gán là GCN
  - CHỈ KHI thấy tiêu đề MỚI khớp 100% → Mới đổi sang loại mới

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÁC CẶP DỄ NHẦM - PHẢI KHỚP CHÍNH XÁC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" không → "UNKNOWN"

2. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG")
   "Hợp đồng THUÊ" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   Nếu không rõ loại nào → "UNKNOWN"

3. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP")
   Nếu không thấy "CHO PHÉP" rõ ràng → "UNKNOWN"

4. "Hợp đồng chuyển nhượng, tặng cho" → HDCQ (có "chuyển nhượng")
   "Hợp đồng ủy quyền" → HDUQ (hoàn toàn khác!)
   ⚠️ PHẢI phân biệt rõ giữa HDCQ và HDUQ

VÍ DỤ:
- Thấy "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu..." (khớp 100%) → GCNM ✅
- Thấy "Giấy chứng nhận quyền sử dụng đất" (khớp 100%, không có "sở hữu") → GCNC ✅
- Thấy "Bản mô tả ranh giới" (khớp 100%) → BMT ✅
- Thấy "Hợp đồng" nhưng không rõ loại → UNKNOWN ❌
- Chỉ thấy nội dung, không có tiêu đề → UNKNOWN ❌

DANH SÁCH ĐẦY ĐỦ - CHỈ CHỌN KHI KHỚP CHÍNH XÁC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
BẢN VẼ HOÀN CÔNG → BVHC
BẢN VẼ NHÀ → BVN
BẢNG KÊ KHAI DIỆN TÍCH ĐANG SỬ DỤNG → BKKDT
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT, QUYỀN SỞ HỮU TÀI SẢN GẮN LIỀN VỚI ĐẤT → GCNM
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → GCNC
HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT → HDCQ
HỢP ĐỒNG ỦY QUYỀN → HDUQ
HỢP ĐỒNG THẾ CHẤP QUYỀN SỬ DỤNG ĐẤT → HDTHC
HỢP ĐỒNG THUÊ ĐẤT, ĐIỀU HỈNH HỢP ĐỒNG THUÊ ĐẤT → HDTD
ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDKBD
ĐƠN ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDK
PHIẾU YÊU CẦU ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT → DKTC
QUYẾT ĐỊNH GIAO ĐẤT, CHO THUÊ ĐẤT → QDGTD
QUYẾT ĐỊNH CHO PHÉP CHUYỂN MỤC ĐÍCH → QDCMD
QUYẾT ĐỊNH THU HỒI ĐẤT → QDTH
CĂN CƯỚC CÔNG DÂN → CCCD
DI CHÚC → DICHUC
GIẤY KHAI SINH → GKS
GIẤY CHỨNG NHẬN KẾT HÔN → GKH
(... và 84 loại khác - xem đầy đủ trong hệ thống)

⚠️ Nếu tiêu đề KHÔNG KHỚP CHÍNH XÁC với danh sách → Trả về UNKNOWN

QUY TRÌNH KIỂM TRA:
━━━━━━━━━━━━━━━━━━
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên CHÍNH XÁC 100%?
4. NẾU CÓ → Trả về mã chính xác, confidence: 0.9
5. NẾU KHÔNG → Trả về "UNKNOWN", confidence: 0.1

TRẢ VỀ JSON (BẮT BUỘC):
{
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.9 hoặc 0.1,
  "reasoning": "Giải thích ngắn gọn (1-2 câu)"
}

❗ NHẮC LẠI:
- CHỈ trả về mã khi khớp TOÀN BỘ tiêu đề
- KHÔNG khớp 1 nửa, vài chữ, hoặc gần giống
- Hệ thống sẽ tự xử lý việc gán trang tiếp theo
- LUÔN trả về JSON format"""


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
                return {
                    "short_code": result.get('short_code', 'UNKNOWN'),
                    "confidence": float(result.get('confidence', 0)),
                    "reasoning": result.get('reasoning', 'AI classification'),
                    "method": "gemini_flash_ai"
                }
        
        # If no JSON found, try to extract from text
        print(f"⚠️ No JSON found, parsing text response", file=sys.stderr)
        
        # Look for short_code pattern
        code_match = re.search(r'(?:short_code|code)[\s:]+["\']?([A-Z]+)["\']?', response_text, re.IGNORECASE)
        conf_match = re.search(r'(?:confidence)[\s:]+([0-9.]+)', response_text)
        
        if code_match:
            return {
                "short_code": code_match.group(1),
                "confidence": float(conf_match.group(1)) if conf_match else 0.7,
                "reasoning": "Parsed from text response",
                "method": "gemini_flash_ai"
            }
        
        # Fallback
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse AI response",
            "method": "gemini_flash_ai"
        }
        
    except Exception as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.2,
            "reasoning": f"Parse error: {str(e)}",
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
