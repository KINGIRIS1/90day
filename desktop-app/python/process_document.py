#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone document processor for desktop app
Combines OCR + Rule-based classification for offline processing
"""
import sys
import json
import os
from pathlib import Path
import warnings

# Force UTF-8 encoding BEFORE any other imports
import io

# Reconfigure stdout/stderr for UTF-8
if sys.platform == 'win32':
    try:
        # Wrap binary buffers with UTF-8 text wrappers
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception as e:
        # Fallback - already wrapped or other issue
        pass

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['GLOG_minloglevel'] = '2'
os.environ['FLAGS_use_mkldnn'] = '0'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Always import Tesseract (required)
    from ocr_engine_tesseract import OCREngine as TesseractEngine
    from rule_classifier import RuleClassifier
    
    # Initialize Tesseract engine
    tesseract_engine = TesseractEngine()
    
    # Try to import and initialize VietOCR (optional)
    vietocr_engine = None
    VietOCREngine = None
    
    try:
        from ocr_engine_vietocr import OCREngine as VietOCREngine
        vietocr_engine = VietOCREngine()
        print("✅ VietOCR engine loaded", file=sys.stderr)
    except ImportError as viet_import_error:
        print(f"⚠️ VietOCR not installed: {viet_import_error}", file=sys.stderr)
    except Exception as viet_error:
        print(f"⚠️ VietOCR initialization failed: {viet_error}", file=sys.stderr)
    
    # Try to import and initialize EasyOCR (optional)
    easyocr_engine = None
    EasyOCREngine = None
    
    try:
        from ocr_engine_easyocr import OCREngine as EasyOCREngine
        easyocr_engine = EasyOCREngine()
        print("✅ EasyOCR engine loaded", file=sys.stderr)
    except ImportError as easy_import_error:
        print(f"⚠️ EasyOCR not installed: {easy_import_error}", file=sys.stderr)
    except Exception as easy_error:
        print(f"⚠️ EasyOCR initialization failed: {easy_error}", file=sys.stderr)
    
    # Summary of loaded engines
    engines_loaded = ["Tesseract"]
    if vietocr_engine:
        engines_loaded.append("VietOCR")
    if easyocr_engine:
        engines_loaded.append("EasyOCR")
    print(f"✅ OCR Engines loaded: {', '.join(engines_loaded)}", file=sys.stderr)
    
except ImportError as e:
    print(json.dumps({
        "error": f"Missing Tesseract OCR dependencies: {str(e)}",
        "success": False
    }, ensure_ascii=True), file=sys.stderr)
    sys.exit(1)


def extract_document_title_from_text(text: str) -> str:
    """
    Extract document title from OCR text using common patterns
    
    Vietnamese admin documents have titles like:
    - ĐƠN ĐĂNG KÝ BIẾN ĐỘNG...
    - HỢP ĐỒNG CHUYỂN NHƯỢNG...
    - GIẤY CHỨNG NHẬN...
    - GIẤY ỦY QUYỀN...
    
    Args:
        text: Full OCR text
        
    Returns:
        Extracted title or empty string if not found
    """
    import re
    
    # Common title patterns (case insensitive)
    title_patterns = [
        r'(ĐƠN\s+ĐĂNG\s+KÝ\s+BIẾN\s+ĐỘNG[^.]*)',
        r'(HỢP\s+ĐỒNG\s+CHUYỂN\s+NHƯỢNG[^.]*)',
        r'(HỢP\s+ĐỒNG\s+ỦY\s+QUYỀN[^.]*)',
        r'(GIẤY\s+CHỨNG\s+NHẬN\s+QUYỀN\s+SỬ\s+DỤNG\s+ĐẤT[^.]*)',
        r'(GIẤY\s+ỦY\s+QUYỀN[^.]*)',
        r'(QUYẾT\s+ĐỊNH[^.]*)',
        r'(ĐƠN\s+XIN[^.]*)',
        r'(BIÊN\s+BẢN[^.]*)',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Limit length to avoid capturing too much
            if len(title) < 200:
                return title
    
    return ""


def process_document(file_path: str, ocr_engine_type: str = 'tesseract') -> dict:
    """
    Process a document using OCR + Rules with font height detection
    
    Args:
        file_path: Path to the image file
        ocr_engine_type: 'tesseract' or 'vietocr' (default: 'tesseract')
    
    Returns classification result with confidence
    """
    try:
        # Select OCR engine based on preference
        if ocr_engine_type == 'vietocr' and vietocr_engine is not None:
            ocr_engine = vietocr_engine
            engine_name = "VietOCR"
            print(f"🔍 Using VietOCR engine", file=sys.stderr)
        elif ocr_engine_type == 'easyocr' and easyocr_engine is not None:
            ocr_engine = easyocr_engine
            engine_name = "EasyOCR"
            print(f"🔍 Using EasyOCR engine", file=sys.stderr)
        else:
            # Default to Tesseract or fallback
            ocr_engine = tesseract_engine
            engine_name = "Tesseract"
            
            # Show fallback message if non-Tesseract was requested
            if ocr_engine_type == 'vietocr' and vietocr_engine is None:
                print(f"⚠️ VietOCR requested but not available, falling back to Tesseract", file=sys.stderr)
            elif ocr_engine_type == 'easyocr' and easyocr_engine is None:
                print(f"⚠️ EasyOCR requested but not available, falling back to Tesseract", file=sys.stderr)
            else:
                print(f"🔍 Using Tesseract engine", file=sys.stderr)
        
        classifier = RuleClassifier()
        
        # Extract text using selected OCR engine (returns dict with full_text, title_text, avg_height)
        ocr_result = ocr_engine.extract_text(file_path)
        
        # Handle both old format (string) and new format (dict) for backward compatibility
        if isinstance(ocr_result, dict):
            extracted_text = ocr_result.get('full_text', '')
            title_text = ocr_result.get('title_text', '')
            avg_height = ocr_result.get('avg_height', 0)
        else:
            # Old format: just a string
            extracted_text = ocr_result
            title_text = extracted_text
            avg_height = 0
        
        if not extracted_text or extracted_text.strip() == "":
            return {
                "success": False,
                "error": "Không thể trích xuất text từ ảnh",
                "method": "ocr_failed"
            }
        
        # Debug: Print full extracted text to see what EasyOCR captured
        print(f"📝 Full text (first 500 chars): {extracted_text[:500]}", file=sys.stderr)
        
        # Try to extract real title from full text using patterns
        extracted_title = extract_document_title_from_text(extracted_text)
        
        if extracted_title:
            print(f"✅ Extracted title via pattern: {extracted_title[:80]}...", file=sys.stderr)
        else:
            print(f"⚠️ No title pattern found in full text", file=sys.stderr)
        
        # Priority:
        # 1. If we found a title via patterns → use it
        # 2. Otherwise use title_text from OCR
        if extracted_title:
            final_title = extracted_title
        else:
            final_title = title_text
        
        # Classify using rules with title text priority
        result = classifier.classify(extracted_text, title_text=final_title)
        
        # Determine if Cloud Boost is recommended
        confidence_threshold = 0.7
        recommend_cloud_boost = result['confidence'] < confidence_threshold
        
        # Add title boost indicator
        title_boost_info = ""
        if result.get('title_boost', False):
            title_boost_info = " [TITLE DETECTED ✓]"
        
        return {
            "success": True,
            "method": "offline_ocr",
            "ocr_engine": engine_name,
            "original_text": extracted_text,
            "title_text": final_title,  # Use final_title (pattern or OCR)
            "title_text_ocr": title_text,  # Original from OCR
            "title_extracted_via_pattern": bool(extracted_title),
            "avg_font_height": round(avg_height, 1),
            "doc_type": result['doc_type'],
            "confidence": result['confidence'],
            "short_code": result['short_code'],
            "reasoning": result.get('reasoning', '') + title_boost_info,
            "recommend_cloud_boost": recommend_cloud_boost,
            "accuracy_estimate": "88-91%" if result.get('title_boost') else "85-88%",
            "title_boost_applied": result.get('title_boost', False)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "method": "processing_failed"
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python process_document.py <file_path> [ocr_engine_type]",
            "success": False
        }, ensure_ascii=True))
        sys.exit(1)
    
    file_path = sys.argv[1]
    ocr_engine_type = sys.argv[2] if len(sys.argv) > 2 else 'tesseract'
    
    if not file_path or not os.path.exists(file_path):
        error_msg = json.dumps({
            "error": "File not found or invalid path",
            "success": False
        }, ensure_ascii=False)
        sys.stdout.write(error_msg)
        sys.stdout.write('\n')
        sys.stdout.flush()
        sys.exit(1)
    
    result = process_document(file_path, ocr_engine_type)
    
    # Output JSON with ASCII encoding (Unicode will be escaped like \uXXXX)
    # This ensures safe transmission through process pipes
    output = json.dumps(result, ensure_ascii=True, indent=None)
    
    # Write to stdout and flush immediately
    sys.stdout.write(output)
    sys.stdout.write('\n')
    sys.stdout.flush()
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
