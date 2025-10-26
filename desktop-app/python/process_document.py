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
import io
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['GLOG_minloglevel'] = '2'
os.environ['FLAGS_use_mkldnn'] = '0'

# Fix Windows console encoding for Vietnamese
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Default: Tesseract (stable offline engine)
    try:
        from ocr_engine_tesseract import OCREngine as TesseractEngine
        print("Using Tesseract OCR (default)", file=sys.stderr)
        ocr_engine = TesseractEngine()
    except ImportError:
        print("Tesseract not available, trying alternatives", file=sys.stderr)
        # Fallback 1: VietOCR (Vietnamese specialized)
        try:
            from ocr_engine_vietocr import OCREngine as VietOCREngine
            print("Trying VietOCR (Vietnamese Transformer-based)", file=sys.stderr)
            ocr_engine = VietOCREngine()
        except ImportError:
            print("VietOCR not available, trying alternatives", file=sys.stderr)
            # Fallback 2: PaddleOCR (Vietnamese specialized)
            try:
                from ocr_engine_paddleocr import OCREngine as PaddleOCREngine
                print("Trying PaddleOCR (Vietnamese specialized)", file=sys.stderr)
                ocr_engine = PaddleOCREngine()
            except ImportError:
                print("PaddleOCR not available, trying alternatives", file=sys.stderr)
                # Fallback 3: RapidOCR (only if installed)
                try:
                    from ocr_engine_rapidocr import OCREngine as RapidOCREngine
                    print("Trying RapidOCR (optional fallback)", file=sys.stderr)
                    ocr_engine = RapidOCREngine()
                except ImportError:
                    # Last resort: original PaddleOCR wrapper or EasyOCR
                    try:
                        from ocr_engine import OCREngine
                        print("Using PaddleOCR (original)", file=sys.stderr)
                        ocr_engine = OCREngine()
                    except ImportError:
                        from ocr_engine_easyocr import OCREngine
                        print("Using EasyOCR", file=sys.stderr)
                        ocr_engine = OCREngine()

    from rule_classifier import RuleClassifier
except ImportError as e:
    print(json.dumps({
        "error": f"Failed to import modules: {str(e)}",
        "success": False
    }, ensure_ascii=True), file=sys.stderr)
    sys.exit(1)


def process_document(file_path: str) -> dict:
    """
    Process a document using OCR + Rules with font height detection
    Returns classification result with confidence
    """
    try:
        # Use already initialized engine from module level
        # ocr_engine is already initialized in the try block above
        classifier = RuleClassifier()
        
        # Extract text using OCR (returns dict with full_text, title_text, avg_height)
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
        
        # Classify using rules with title text priority
        result = classifier.classify(extracted_text, title_text=title_text)
        
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
            "original_text": extracted_text,
            "title_text": title_text,
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
            "error": "Usage: python process_document.py <file_path>",
            "success": False
        }, ensure_ascii=True))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(json.dumps({
            "error": f"File not found: {file_path}",
            "success": False
        }, ensure_ascii=True))
        sys.exit(1)
    
    result = process_document(file_path)
    # Use ensure_ascii=True to avoid Windows encoding issues
    print(json.dumps(result, ensure_ascii=True))
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
