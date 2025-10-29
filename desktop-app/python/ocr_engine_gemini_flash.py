#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash 2.0 - AI Document Classification Engine
Using emergentintegrations library for multimodal AI
"""

import sys
import base64
import asyncio
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
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
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
        
        # Create Gemini Flash chat instance
        chat = LlmChat(
            api_key=api_key,
            session_id="gemini-flash-doc-classify",
            system_message=get_classification_prompt()
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create message with image
        image_attachment = ImageContent(image_base64=encoded_image)
        
        user_message = UserMessage(
            text="Classify this Vietnamese land document. Return JSON with: short_code, confidence (0-1), reasoning",
            file_contents=[image_attachment]
        )
        
        # Run async classification
        result = asyncio.run(chat.send_message(user_message))
        
        print(f"🤖 Gemini Flash response: {result[:200]}...", file=sys.stderr)
        
        # Parse result
        classification = parse_gemini_response(result)
        
        return classification
        
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "emergentintegrations"
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Missing library: {missing_lib}. Run: pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/"
        }
    except Exception as e:
        print(f"❌ Gemini Flash error: {e}", file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Error: {str(e)}"
        }


def get_classification_prompt():
    """
    System prompt for Vietnamese document classification
    """
    return """Bạn là chuyên gia phân loại tài liệu đất đai Việt Nam.

🎯 NHIỆM VỤ:
Phân tích ảnh tài liệu và trả về JSON với:
{
  "short_code": "CODE",
  "confidence": 0.95,
  "reasoning": "Giải thích ngắn gọn"
}

📋 DANH SÁCH 98 LOẠI TÀI LIỆU:
BMT, HSKT, BVHC, BVN, BKKDT, DSCG, BBBDG, BBGD, BBHDDK, BBNT, BBKTSS, 
BBKTHT, BBKTDC, KTCKCG, KTCKMG, BLTT, CCCD, DS15, DSCK, DICHUC, DCK, 
DDKBD, DDK, CHTGD, DCQDGD, DMG, DMD, DXN, DXCMD, DGH, DXGD, DXTHT, 
DXCD, DDCTH, DXNTH, GKH, GCNM, GCNC, GXNNVTC, GKS, GNT, GSND, GTLQ, 
GUQ, GXNDKLD, GPXD, hoadon, HTBTH, HDCQ, HDBDG, HDTHC, HDTCO, HDTD, 
HDUQ, PCT, PKTHS, PLYKDC, PXNKQDD, DKTC, DKTD, DKXTC, QR, QDCMD, QDTT, 
QDCHTGD, QDDCGD, QDDCTH, QDGH, QDGTD, QDHG, QDPDBT, QDDCQH, QDPDDG, 
QDTHA, QDTH, QDHTSD, QDXP, SDTT, TBCNBD, CKDC, TBT, TBMG, TBCKCG, 
TBCKMG, HTNVTC, TKT, TTr, TTCG, CKTSR, VBCTCMD, VBDNCT, PDPASDD, VBTK, 
TTHGD, CDLK, HCLK, VBTC, PCTSVC

🔍 QUY TẮC PHÂN TÍCH:

1. **NHẬN DIỆN QUỐC HUY** (ưu tiên cao):
   - Quốc huy Việt Nam (ngôi sao vàng, búa liềm) → Tài liệu chính thức
   - Màu vàng/cam background → Thường là GCNC

2. **ĐỌC TIÊU ĐỀ** (chính xác):
   - "HỢP ĐỒNG CHUYỂN NHƯỢNG..." → HDCQ
   - "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT, QUYỀN SỞ HỮU TÀI SẢN..." → GCNM (DÀI)
   - "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT" (KHÔNG có "quyền sở hữu") → GCNC (NGẮN)
   - "PHIẾU YÊU CẦU ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM..." → DKTC
   - "QUYẾT ĐỊNH GIAO ĐẤT..." → QDGTD
   - "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG..." → DDKBD (PHẢI có "BIẾN ĐỘNG")
   - "ĐƠN ĐĂNG KÝ ĐẤT ĐAI..." (KHÔNG có "BIẾN ĐỘNG") → DDK

3. **LAYOUT & CONTEXT**:
   - 2 trang ngang (landscape) + màu cam → GCNC
   - Có chữ ký, con dấu → Hợp đồng (HDCQ, HDUQ, HDTD...)
   - Có header "UBND" + "QUYẾT ĐỊNH" → QD* types

4. **CÁC CẶP DỄ NHẦM**:
   - GCNM vs GCNC: Check "quyền sở hữu tài sản" (có = GCNM, không = GCNC)
   - DDKBD vs DDK: Check "biến động" (có = DDKBD, không = DDK)
   - HDCQ vs HDTD vs HDTHC: Check "chuyển nhượng" / "thuê" / "thế chấp"

5. **NẾU KHÔNG RÕ RÀNG**:
   - confidence < 0.5
   - short_code: "UNKNOWN"
   - reasoning: Giải thích tại sao không chắc chắn

⚠️ QUAN TRỌNG:
- LUÔN trả về JSON format chính xác
- confidence: 0.0 - 1.0
- reasoning: Tiếng Việt, ngắn gọn (1-2 câu)
- Nếu không thấy title rõ ràng: "UNKNOWN"

VÍ DỤ RESPONSE:
{
  "short_code": "HDCQ",
  "confidence": 0.92,
  "reasoning": "Có quốc huy VN + tiêu đề 'HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT' rõ ràng"
}"""


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
