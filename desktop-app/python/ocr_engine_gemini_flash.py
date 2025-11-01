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


def classify_document_gemini_flash(image_path, api_key, crop_top_percent=1.0):
    """
    Classify Vietnamese land document using Gemini Flash 2.0 AI with position awareness
    
    Args:
        image_path: Path to image file
        api_key: Google API key (BYOK)
        crop_top_percent: Percentage of top image to process (default 1.0 = 100% for accurate position analysis)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning, title_position, and usage tokens
    """
    try:
        import requests
        
        # Read full image for position-aware analysis
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
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format=img.format or 'PNG')
            image_content = img_byte_arr.getvalue()
        
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
        
        # Send request (timeout 60s for large images)
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Increased from 30s to handle large image processing
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
        
        # Extract usage tokens (AI Studio returns usageMetadata)
        usage = result_data.get('usageMetadata') or {}
        prompt_tokens = int(usage.get('promptTokenCount', 0) or 0)
        output_tokens = int(usage.get('candidatesTokenCount', 0) or 0)
        total_tokens = int(usage.get('totalTokenCount', prompt_tokens + output_tokens) or 0)
        parsed_usage = {
            "input_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
        
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
                    # Attach usage tokens for cost estimation
                    classification['usage'] = parsed_usage
                    return classification
        
        # No valid response
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse Gemini response",
            "usage": parsed_usage
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
    UPDATED: More flexible matching (85-90% similarity acceptable)
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 PHÂN TÍCH VỊ TRÍ VĂN BẢN (POSITION-AWARE CLASSIFICATION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

... (prompt rút gọn cho brevity trong code) ...
"""


def parse_gemini_response(response_text):
    """
    Parse Gemini Flash response to extract classification
    """
    import json
    import re
    
    try:
        # Remove markdown code blocks
        clean_text = re.sub(r'```json\s*', '', response_text)
        clean_text = re.sub(r'```\s*$', '', clean_text)
        clean_text = clean_text.strip()
        
        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', clean_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            
            if 'short_code' in result and 'confidence' in result:
                short_code = str(result.get('short_code', 'UNKNOWN')).strip()
                invalid_codes = ['N/A', 'NA', 'N', 'NONE', 'NULL', 'UNDEFINED', '']
                if short_code.upper() in invalid_codes:
                    print(f"⚠️ Invalid short_code from Gemini: '{short_code}', using UNKNOWN", file=sys.stderr)
                    short_code = 'UNKNOWN'
                else:
                    original_code = short_code
                    short_code = re.sub(r'[^A-Z0-9_]', '', short_code.upper())
                    if short_code != original_code:
                        print(f"⚠️ Sanitized short_code: '{original_code}' → '{short_code}'", file=sys.stderr)
                    if not short_code or len(short_code) < 2:
                        print(f"⚠️ Short_code too short after sanitization: '{short_code}', using UNKNOWN", file=sys.stderr)
                        short_code = 'UNKNOWN'
                
                return {
                    "short_code": short_code,
                    "confidence": float(result.get('confidence', 0)),
                    "reasoning": result.get('reasoning', 'AI classification'),
                    "title_position": result.get('title_position', 'unknown'),
                    "method": "gemini_flash_ai"
                }
        
        # Fallback parse
        print(f"⚠️ No JSON found, parsing text response", file=sys.stderr)
        code_match = re.search(r'(?:short_code|code)[\s:]+["\']?([A-Z]+)["\']?', response_text, re.IGNORECASE)
        conf_match = re.search(r'(?:confidence)[\s:]+([0-9.]+)', response_text)
        if code_match:
            return {
                "short_code": code_match.group(1),
                "confidence": float(conf_match.group(1)) if conf_match else 0.7,
                "reasoning": "Parsed from text response",
                "title_position": "unknown",
                "method": "gemini_flash_ai"
            }
        
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
