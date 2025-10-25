"""
OCR Engine using PaddleOCR for Vietnamese document processing
"""
from paddleocr import PaddleOCR
import logging

logger = logging.getLogger(__name__)

# Initialize PaddleOCR with Vietnamese language support
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='vi',
    show_log=False,
    use_gpu=False  # Set to True if GPU available
)

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using PaddleOCR
    
    Args:
        image_path: Path to image file
        
    Returns:
        Extracted text as string
    """
    try:
        result = ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return ""
        
        # Combine all detected text
        text_lines = []
        for line in result[0]:
            if len(line) >= 2 and len(line[1]) >= 1:
                text_lines.append(line[1][0])
        
        full_text = ' '.join(text_lines)
        return full_text
        
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""
