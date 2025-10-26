"""
OCR Engine using PaddleOCR for Vietnamese document processing
"""
import os
import logging

# Disable PaddleX initialization BEFORE importing PaddleOCR
os.environ['PADDLEX_DISABLE_INIT'] = '1'
os.environ['PADDLE_DISABLE_PDX'] = '1'

from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

# Singleton instance
_ocr_instance = None
_ocr_lock = None
_initialization_failed = False

def get_ocr_instance():
    """Get or create PaddleOCR singleton instance"""
    global _ocr_instance, _ocr_lock, _initialization_failed
    
    # If initialization failed before, don't retry
    if _initialization_failed:
        raise RuntimeError("PaddleOCR initialization failed previously. Cannot proceed.")
    
    if _ocr_instance is None:
        # Import threading here to avoid issues
        import threading
        if _ocr_lock is None:
            _ocr_lock = threading.Lock()
        
        with _ocr_lock:
            # Double-check locking pattern
            if _ocr_instance is None:
                try:
                    logger.info("🔧 Initializing PaddleOCR (first time only)...")
                    _ocr_instance = PaddleOCR(
                        use_angle_cls=True,
                        lang='vi',
                        show_log=False,
                        use_gpu=False,
                        enable_mkldnn=False,  # Disable to avoid conflicts
                        rec_model_dir=None,
                        det_model_dir=None,
                        cls_model_dir=None
                    )
                    logger.info("✅ PaddleOCR initialized successfully")
                except Exception as e:
                    _initialization_failed = True
                    logger.error(f"❌ Failed to initialize PaddleOCR: {e}")
                    raise RuntimeError(f"PaddleOCR initialization failed: {e}")
    
    return _ocr_instance

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using PaddleOCR
    
    Args:
        image_path: Path to image file
        
    Returns:
        Extracted text as string
    """
    try:
        ocr = get_ocr_instance()
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
        logger.error(f"OCR error for {image_path}: {e}")
        return ""
