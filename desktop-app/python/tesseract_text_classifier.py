"""
Tesseract OCR + Gemini Text Classification
Approach: Extract text locally with Tesseract, then use Gemini Text API for classification
Benefits: Faster, cheaper, smaller requests, less 503 errors
"""

import sys
import json
import os
import base64
from PIL import Image
import pytesseract
import google.generativeai as genai
from io import BytesIO

# Configure Tesseract path (Windows)
if os.name == 'nt':
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Tesseract-OCR', 'tesseract.exe')
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def extract_text_tesseract(image_path):
    """Extract text from image using Tesseract OCR"""
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # OCR with Vietnamese language
        text = pytesseract.image_to_string(img, lang='vie+eng', config='--psm 3')
        
        # Get confidence score
        data = pytesseract.image_to_data(img, lang='vie+eng', output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': text.strip(),
            'confidence': avg_confidence / 100,  # 0-1 scale
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    except Exception as e:
        print(f"[ERROR] Tesseract OCR failed: {e}", file=sys.stderr)
        return None

def classify_with_gemini_text(text_data, api_key):
    """Classify document using Gemini Text API based on OCR text"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build classification prompt
        prompt = f"""Bạn là chuyên gia phân loại tài liệu địa chính Việt Nam.

Dựa trên TEXT được OCR từ tài liệu dưới đây, hãy phân loại tài liệu.

TEXT OCR (độ tin cậy: {text_data['confidence']*100:.1f}%):
\"\"\"
{text_data['text'][:3000]}
\"\"\"

DANH SÁCH LOẠI TÀI LIỆU:
- GCN: Giấy chứng nhận quyền sử dụng đất
- HDCQ: Hợp đồng chuyển nhượng
- HDUQ: Hợp đồng ủy quyền
- TTHGD: Thỏa thuận hộ gia đình
- DDKBD: Đơn đăng ký biến động
- BCCQ: Biên chế chuyển quyền
- UNKNOWN: Không xác định được

QUY TẮC:
1. Tìm các TỪ KHÓA chính: "giấy chứng nhận", "hợp đồng", "chuyển nhượng", "ủy quyền", "thỏa thuận"
2. Nếu text quá ngắn (< 50 ký tự) hoặc confidence < 50% → UNKNOWN
3. Ưu tiên độ chính xác hơn đoán mò

TRẢ VỀ JSON (không có markdown, chỉ JSON thuần):
{{
  "type": "GCN hoặc HDCQ hoặc ...",
  "short_code": "GCN hoặc HDCQ hoặc ...",
  "confidence": 0.0-1.0,
  "reasoning": "Giải thích ngắn gọn",
  "key_phrases": ["từ khóa 1", "từ khóa 2"]
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
        
        result = json.loads(response_text)
        
        # Add metadata
        result['method'] = 'tesseract_text'
        result['ocr_confidence'] = text_data['confidence']
        result['text_length'] = text_data['char_count']
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse error: {e}", file=sys.stderr)
        print(f"[ERROR] Response text: {response_text}", file=sys.stderr)
        return {
            'type': 'UNKNOWN',
            'short_code': 'UNKNOWN',
            'confidence': 0.0,
            'reasoning': f'JSON parse error: {str(e)}',
            'method': 'tesseract_text',
            'error': str(e)
        }
    except Exception as e:
        print(f"[ERROR] Gemini classification failed: {e}", file=sys.stderr)
        return {
            'type': 'UNKNOWN',
            'short_code': 'UNKNOWN',
            'confidence': 0.0,
            'reasoning': f'Classification error: {str(e)}',
            'method': 'tesseract_text',
            'error': str(e)
        }

def process_image(image_path, api_key):
    """
    Full pipeline: Tesseract OCR → Gemini Text Classification
    """
    print(f"[Tesseract+Text] Processing: {image_path}", file=sys.stderr)
    
    # Step 1: Extract text with Tesseract
    text_data = extract_text_tesseract(image_path)
    
    if not text_data or not text_data['text']:
        print(f"[ERROR] No text extracted from image", file=sys.stderr)
        return {
            'type': 'UNKNOWN',
            'short_code': 'UNKNOWN',
            'confidence': 0.0,
            'reasoning': 'Tesseract failed to extract text',
            'method': 'tesseract_text',
            'error': 'No text extracted'
        }
    
    print(f"[Tesseract] Extracted {text_data['word_count']} words (confidence: {text_data['confidence']*100:.1f}%)", file=sys.stderr)
    
    # Step 2: Classify with Gemini Text API
    result = classify_with_gemini_text(text_data, api_key)
    
    print(f"[Classification] {result['short_code']} (confidence: {result['confidence']*100:.1f}%)", file=sys.stderr)
    
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'error': 'Usage: python tesseract_text_classifier.py <image_path> <api_key>'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    
    result = process_image(image_path, api_key)
    print(json.dumps(result, ensure_ascii=False))
