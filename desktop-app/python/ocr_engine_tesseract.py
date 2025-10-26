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
    
    def extract_text(self, image_path: str) -> dict:
        """
        Extract text from image using Tesseract with font height detection
        Only scan top 40% of image for better accuracy
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with:
                - full_text: All extracted text
                - title_text: Text with large font (likely titles/headers)
                - avg_height: Average font height in pixels
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Get image dimensions
            width, height = image.size
            
            # Crop to top 40% of image (where document title/type is)
            crop_height = int(height * 0.4)  # Top 40%
            cropped_image = image.crop((0, 0, width, crop_height))
            
            # Extract text with TSV format to get font height data
            tsv_data = pytesseract.image_to_data(
                cropped_image, 
                lang='vie+eng',
                output_type=pytesseract.Output.DICT
            )
            
            # Collect all text and font heights
            full_text_parts = []
            text_with_heights = []
            
            for i in range(len(tsv_data['text'])):
                text = tsv_data['text'][i].strip()
                if text:
                    conf = int(tsv_data['conf'][i])
                    # Only consider text with reasonable confidence
                    if conf > 30:
                        full_text_parts.append(text)
                        font_height = tsv_data['height'][i]
                        text_with_heights.append({
                            'text': text,
                            'height': font_height,
                            'conf': conf
                        })
            
            full_text = ' '.join(full_text_parts)
            
            # Calculate average height
            if text_with_heights:
                avg_height = sum(item['height'] for item in text_with_heights) / len(text_with_heights)
                
                # Title threshold: 1.5x average height
                title_threshold = avg_height * 1.5
                
                # Extract title text (large font only)
                title_parts = [
                    item['text'] for item in text_with_heights 
                    if item['height'] >= title_threshold
                ]
                title_text = ' '.join(title_parts)
            else:
                avg_height = 0
                title_text = full_text
            
            return {
                'full_text': full_text.strip(),
                'title_text': title_text.strip(),
                'avg_height': avg_height
            }
            
        except Exception as e:
            print(f"Error in Tesseract extraction: {e}", file=sys.stderr)
            return {
                'full_text': '',
                'title_text': '',
                'avg_height': 0
            }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_engine_tesseract.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    engine = OCREngine()
    text = engine.extract_text(image_path)
    print(f"Extracted text: {text}")
