#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT-4o Mini Vision - AI Document Classification Engine
Using direct REST API for vision-based OCR
"""

import sys
import base64
import os
from PIL import Image
import io

# Valid document codes - MUST match with Gemini engine
VALID_DOCUMENT_CODES = {
    'BBBDG', 'BBKTHT', 'BBNT',
    'BMT', 'CCCD', 'CDLK', 'CHTGD',
    'CKDC', 'CKTSR', 'DCK', 'DCQDGD', 'DDK', 'DDKBD', 'DGH',
    'DICHUC', 'DMG', 'DSCK',
    'DXCD', 'DXCMD', 'DXGD', 'DXN', 'DXTHT',
    'GCN',   # TEMPORARY - will be post-processed to GCNC or GCNM
    'GCNC',  # GCN old (red/brown certificate)
    'GCNM',  # GCN new (pink certificate)
    'GKH', 'GKS', 'GNT', 'GPXD', 'GTLQ', 'GUQ', 'GXNDKLD',
    'GXNNVTC', 'HCLK', 'HDBDG', 'HDCQ', 'HDTHC', 'HDUQ',
    'HSKT', 'HTBTH', 'HTNVTC', 'KTCKCG', 'KTCKMG', 'PCT', 'PCTSVC',
    'PKTHS', 'PLYKDC', 'PXNKQDD', 'QDCHTGD', 'QDCMD', 'QDDCGD',
    'QDDCTH', 'QDGH', 'QDGTD', 'QDHG', 'QDPDBT',
    'QDTH', 'SDTT', 'TBCKCG',
    'TBCKMG', 'TBCNBD', 'TBMG', 'TBT', 'TKT', 'TTCG', 'TTHGD', 'UNKNOWN',
    'VBCTCMD', 'VBTC', 'VBTK', 'hoadon'
}


def resize_image_smart(img, max_width=1200, max_height=1800):
    """
    Smart resize: Only resize if image exceeds max dimensions
    Maintains aspect ratio
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


def get_classification_prompt():
    """
    Load classification prompt - LITE version for cost optimization
    OpenAI charges per token, so we use lite prompt to reduce costs
    """
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'classification_prompt_lite.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ Prompt file not found: {prompt_path}, using fallback", file=sys.stderr)
        # Fallback to full if lite not found
        prompt_path_full = os.path.join(os.path.dirname(__file__), 'prompts', 'classification_prompt_full.txt')
        try:
            with open(prompt_path_full, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return """Phân loại tài liệu đất đai Việt Nam. Trả về JSON với short_code, confidence, reasoning."""


def classify_document_openai_vision(image_path, api_key, enable_resize=True, max_width=1500, max_height=2100):
    """
    Classify Vietnamese land document using OpenAI GPT-4o mini Vision
    
    Args:
        image_path: Path to image file
        api_key: OpenAI API key (BYOK)
        enable_resize: Enable smart resizing to reduce costs (default: True)
        max_width: Maximum width for resize (default: 1500)
        max_height: Maximum height for resize (default: 2100)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning
    """
    try:
        import requests
        
        # Read and process image
        resize_info = {}
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"🖼️ Processing image: {width}x{height}", file=sys.stderr)
            
            # Apply smart resize if enabled
            if enable_resize:
                img, resize_info = resize_image_smart(img, max_width, max_height)
            
            # Convert to base64 (use JPEG with quality 85)
            img_byte_arr = io.BytesIO()
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            image_content = img_byte_arr.getvalue()
        
        # Encode to base64
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        # OpenAI Vision API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        print(f"📡 Sending request to OpenAI GPT-4o mini...", file=sys.stderr)
        if resize_info.get('resized'):
            print(f"💰 Cost savings: ~{resize_info['reduction_percent']:.0f}% fewer tokens", file=sys.stderr)
        
        # Get classification prompt
        prompt_text = get_classification_prompt()
        
        # Create request payload
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Send request with retry logic
        max_retries = 3
        retry_delay = 10
        response = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
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
            if response.status_code == 401:
                error_msg = "🔐 API KEY KHÔNG HỢP LỆ!\n"
                error_msg += "📌 Giải pháp:\n"
                error_msg += "  • Kiểm tra API key trong Settings\n"
                error_msg += "  • Tạo API key mới tại: https://platform.openai.com/api-keys\n"
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    "short_code": "ERROR",
                    "confidence": 0,
                    "reasoning": error_msg,
                    "error_code": "INVALID_API_KEY"
                }
            
            elif response.status_code == 429:
                error_msg = "⚠️ VƯỢT QUÁ GIỚI HẠN REQUEST!\n"
                error_msg += "📌 Giải pháp:\n"
                error_msg += "  • Đợi 1-2 phút rồi thử lại\n"
                error_msg += "  • Kiểm tra quota tại: https://platform.openai.com/usage\n"
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    "short_code": "ERROR",
                    "confidence": 0,
                    "reasoning": error_msg,
                    "error_code": "RATE_LIMIT_EXCEEDED"
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
        usage_metadata = result_data.get('usage', {})
        usage_info = {
            "input_tokens": usage_metadata.get('prompt_tokens', 0),
            "output_tokens": usage_metadata.get('completion_tokens', 0),
            "total_tokens": usage_metadata.get('total_tokens', 0)
        }
        
        print(f"📊 Tokens: input={usage_info['input_tokens']}, output={usage_info['output_tokens']}", file=sys.stderr)
        
        # Extract text from response
        if 'choices' in result_data and len(result_data['choices']) > 0:
            choice = result_data['choices'][0]
            
            if 'message' in choice and 'content' in choice['message']:
                result_text = choice['message']['content']
                print(f"🤖 OpenAI response: {result_text[:200]}...", file=sys.stderr)
                
                # Parse result (reuse Gemini parser)
                from ocr_engine_gemini_flash import parse_gemini_response
                classification = parse_gemini_response(result_text)
                # Add usage and resize info
                classification['usage'] = usage_info
                classification['resize_info'] = resize_info
                classification['method'] = "openai_gpt4o_mini_vision"
                return classification
            else:
                print(f"⚠️ No content in message. Choice: {choice}", file=sys.stderr)
        else:
            print(f"⚠️ No choices in response. Full response: {result_data}", file=sys.stderr)
        
        # No valid response
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse OpenAI response",
            "usage": usage_info,
            "resize_info": resize_info,
            "method": "openai_gpt4o_mini_vision"
        }
        
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Missing library: {missing_lib}. Install: pip install {missing_lib}"
        }
    except Exception as e:
        print(f"❌ OpenAI Vision error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Error: {str(e)}"
        }


if __name__ == '__main__':
    # Test
    if len(sys.argv) < 3:
        print("Usage: python ocr_engine_openai_vision.py <image_path> <api_key>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    
    result = classify_document_openai_vision(image_path, api_key)
    print(f"\nResult: {result}")
