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
# Keep reference to prevent garbage collection
_stdout = None
_stderr = None

if sys.platform == 'win32':
    _stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    _stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    sys.stdout = _stdout
    sys.stderr = _stderr

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import both OCR engines
    from ocr_engine_tesseract import OCREngine as TesseractEngine
    from ocr_engine_vietocr import OCREngine as VietOCREngine
    from rule_classifier import RuleClassifier
    
    # Initialize both engines
    tesseract_engine = TesseractEngine()
    vietocr_engine = None
    
    # Try to initialize VietOCR (may fail if not installed)
    try:
        vietocr_engine = VietOCREngine()
        print("✅ Both Tesseract and VietOCR engines loaded", file=sys.stderr)
    except Exception as viet_error:
        print(f"⚠️ VietOCR not available: {viet_error}", file=sys.stderr)
        print("✅ Tesseract OCR loaded (VietOCR disabled)", file=sys.stderr)
    
except ImportError as e:
    print(json.dumps({
        "error": f"Missing OCR dependencies: {str(e)}",
        "success": False
    }, ensure_ascii=True), file=sys.stderr)
    sys.exit(1)


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
        else:
            ocr_engine = tesseract_engine
            engine_name = "Tesseract"
            if ocr_engine_type == 'vietocr' and vietocr_engine is None:
                print(f"⚠️ VietOCR requested but not available, falling back to Tesseract", file=sys.stderr)
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
    
    if not file_path or not os.path.exists(file_path):
        error_msg = json.dumps({
            "error": "File not found or invalid path",
            "success": False
        }, ensure_ascii=False)
        sys.stdout.write(error_msg)
        sys.stdout.write('\n')
        sys.stdout.flush()
        sys.exit(1)
    
    result = process_document(file_path)
    
    # Output JSON with proper encoding
    output = json.dumps(result, ensure_ascii=False)
    
    # Write to stdout and flush immediately
    sys.stdout.write(output)
    sys.stdout.write('\n')
    sys.stdout.flush()
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
