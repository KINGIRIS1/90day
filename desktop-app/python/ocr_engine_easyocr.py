#!/usr/bin/env python3
"""
Alternative OCR engine using EasyOCR (Windows-compatible)
Replaces PaddleOCR for Windows users
"""
import sys
import os

try:
    import easyocr
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Install with: pip install easyocr pillow", file=sys.stderr)
    sys.exit(1)


class OCREngine:
    """
    OCR Engine using EasyOCR (Windows-compatible)
    Vietnamese text recognition
    """
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCREngine, cls).__new__(cls)
        return cls._instance
    
    def _get_reader(self):
        """Lazy initialization of EasyOCR reader"""
        if self._reader is None:
            print("Initializing EasyOCR (first time may take 1-2 minutes)...", file=sys.stderr)
            # Support Vietnamese and English
            self._reader = easyocr.Reader(['vi', 'en'], gpu=False)
            print("EasyOCR initialized successfully!", file=sys.stderr)
        return self._reader
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using EasyOCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text string
        """
        try:
            # Get reader instance
            reader = self._get_reader()
            
            # Read image
            result = reader.readtext(image_path)
            
            # Extract text from results
            # EasyOCR returns list of (bbox, text, confidence)
            texts = [text for (bbox, text, conf) in result]
            
            # Join all text
            full_text = ' '.join(texts)
            
            return full_text
            
        except Exception as e:
            print(f"Error in EasyOCR extraction: {e}", file=sys.stderr)
            return ""


# Test if run directly
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_engine_easyocr.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    engine = OCREngine()
    text = engine.extract_text(image_path)
    print(f"Extracted text: {text}")
