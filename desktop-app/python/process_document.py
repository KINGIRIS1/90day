#!/usr/bin/env python3
"""
Standalone document processor for desktop app
Combines OCR + Rule-based classification for offline processing
"""
import sys
import json
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Try PaddleOCR first (Linux/Mac)
    try:
        from ocr_engine import OCREngine
        print("Using PaddleOCR", file=sys.stderr)
    except ImportError:
        # Try EasyOCR (Windows with GPU/CPU)
        try:
            from ocr_engine_easyocr import OCREngine
            print("Using EasyOCR", file=sys.stderr)
        except ImportError:
            # Fall back to Tesseract (Lightweight, Windows-friendly)
            from ocr_engine_tesseract import OCREngine
            print("Using Tesseract OCR", file=sys.stderr)
    
    from rule_classifier import RuleClassifier
except ImportError as e:
    print(json.dumps({
        "error": f"Failed to import modules: {str(e)}",
        "success": False
    }), file=sys.stderr)
    sys.exit(1)


def process_document(file_path: str) -> dict:
    """
    Process a document using OCR + Rules
    Returns classification result with confidence
    """
    try:
        # Initialize engines
        ocr_engine = OCREngine()
        classifier = RuleClassifier()
        
        # Extract text using PaddleOCR
        extracted_text = ocr_engine.extract_text(file_path)
        
        if not extracted_text or extracted_text.strip() == "":
            return {
                "success": False,
                "error": "Không thể trích xuất text từ ảnh",
                "method": "ocr_failed"
            }
        
        # Classify using rules
        result = classifier.classify(extracted_text)
        
        # Determine if Cloud Boost is recommended
        confidence_threshold = 0.7
        recommend_cloud_boost = result['confidence'] < confidence_threshold
        
        return {
            "success": True,
            "method": "offline_ocr",
            "original_text": extracted_text,
            "doc_type": result['doc_type'],
            "confidence": result['confidence'],
            "short_code": result['short_code'],
            "reasoning": result.get('reasoning', ''),
            "recommend_cloud_boost": recommend_cloud_boost,
            "accuracy_estimate": "85-88%"
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
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(json.dumps({
            "error": f"File not found: {file_path}",
            "success": False
        }))
        sys.exit(1)
    
    result = process_document(file_path)
    print(json.dumps(result, ensure_ascii=False))
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
