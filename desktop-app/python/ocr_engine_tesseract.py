#!/usr/bin/env python3
"""
Ultra-lightweight OCR using Tesseract (Windows-friendly)
No heavy dependencies like PyTorch
"""
import sys
import os

try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Install with: pip install pytesseract pillow", file=sys.stderr)
    print("Also install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki", file=sys.stderr)
    sys.exit(1)


class OCREngine:
    """
    Lightweight OCR using Tesseract
    Very easy to install on Windows
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCREngine, cls).__new__(cls)
            # Set Tesseract path for Windows
            # Auto-detect common installation paths
            import os
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        return cls._instance
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text string
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Extract text with Vietnamese language
            # lang='vie' for Vietnamese, 'eng' for English
            text = pytesseract.image_to_string(image, lang='vie+eng')
            
            return text.strip()
            
        except Exception as e:
            print(f"Error in Tesseract extraction: {e}", file=sys.stderr)
            return ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_engine_tesseract.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    engine = OCREngine()
    text = engine.extract_text(image_path)
    print(f"Extracted text: {text}")
