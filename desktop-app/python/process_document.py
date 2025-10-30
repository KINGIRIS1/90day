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
    except Exception:
        # Fallback - already wrapped or other issue
        pass

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['GLOG_minloglevel'] = '2'
os.environ['FLAGS_use_mkldnn'] = '0'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import rule classifier (always needed)
from rule_classifier import RuleClassifier

# Lazy import OCR engines only when needed
# This allows Google/Azure to work even if Tesseract dependencies are missing
tesseract_engine = None
vietocr_engine = None
easyocr_engine = None


def extract_document_title_from_text(text: str) -> str:
    """
    Extract document title from OCR text using common patterns
    
    Vietnamese admin documents have titles like:
    - ĐƠN ĐĂNG KÝ BIẾN ĐỘNG...
    - HỢP ĐỒNG CHUYỂN NHƯỢNG...
    - GIẤY CHỨNG NHẬN...
    - GIẤY ỦY QUYỀN...
    - GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ
    
    Args:
        text: Full OCR text
        
    Returns:
        Extracted title or empty string if not found
    """
    import re
    
    # Common title patterns (case insensitive, flexible with OCR errors)
    # IMPORTANT: Order matters! More specific patterns should come first
    # Vietnamese vowel variations (all tones):
    # E: [EÊÉÈẾỀỂỄỆ] - E, Ê + 5 tones
    # O: [OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ] - O, Ô, Ơ + all tones
    # U: [UƯÚÙỦŨỤỨỪỬỮỰ] - U, Ư + all tones
    title_patterns = [
        # GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ (GTLQ)
        # Chấp nhận lỗi OCR phổ biến: HỒ→HỎ, KẾT→KÉT, thiếu dấu
        r'(GI[AÁẤ]Y\s+TI[EÊÉÈẾỀỂỄỆ]P\s+NH[ẬAĂÂÁÀÃẠÂẤĂẮ]N\s+H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ][\s]*S[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]|GI[AÁẤ]Y\s+TI[EÊÉÈẾỀỂỄỆ]P\s+NH[ẬAĂÂÁÀÃẠÂẤĂẮ]N\s+HỎ\s*SƠ)\s+V[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]\s+HẸN\s+TRẢ\s+K[ÊE]T\s+QUẢ',
        
        # ĐƠN ĐĂNG KÝ BIẾN ĐỘNG
        r'(Đ[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]N\s+[ĐD][AĂ]NG\s+K[YÝ]\s+BI[EÊÉÈẾỀỂỄỆ]N\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG(?:\s+[ĐD][AÁẤ]T\s+[ĐD]AI)?(?:\s*,?\s*T[AÀ]I\s+S[AẢ]N)?(?:\s+G[AẮ]N\s+LI[EÊÉÈẾỀỂỄỆ]N\s+V[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]I\s+[ĐD][AÁẤ]T)?)',
        
        # HỢP ĐỒNG CHUYỂN NHƯỢNG (check FIRST - more specific than HDUQ)
        # CRITICAL: Must check BEFORE "HỢP ĐỒNG ỦY QUYỀN" to avoid false matches
        # "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT" should match HDCQ, not HDUQ
        r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+CHUY[EÊÉÈẾỀỂỄỆ]N\s+NH[UƯÚÙỦŨỤỨỪỬỮỰ][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG(?:\s+QUY[EÊÉÈẾỀỂỄỆ]N)?(?:\s+S[UƯÚÙỦŨỤỨỪỬỮỰ]\s+D[UỤ]NG\s+[ĐD][AÁẤ]T)?)',
        
        # HỢP ĐỒNG ỦY QUYỀN (check AFTER HDCQ)
        # Flexible with: ỦY (correct), UỶ (U+Ỷ OCR error), Ủ Y (with space), UY (no accents)
        r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+(?:[UỦ][\sỶ]*Y|U[ỶY])\s+QUY[EÊÉÈẾỀỂỄỆ]N)',
        
        # GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT
        r'(GI[AÁẤ]Y\s+CH[UƯÚÙỦŨỤỨỪỬỮỰ]NG\s+NH[AẬ]N\s+QUY[EÊÉÈẾỀỂỄỆ]N\s+S[UƯÚÙỦŨỤỨỪỬỮỰ]\s+D[UỤ]NG\s+[ĐD][AÁẤ]T)',
        
        # GIẤY ỦY QUYỀN
        # Flexible with: ỦY, UỶ (OCR error), Ủ Y, UY
        r'(GI[AÁẤ]Y\s+(?:[UỦ][\sỶ]*Y|U[ỶY])\s+QUY[EÊÉÈẾỀỂỄỆ]N)',
        
        # QUYẾT ĐỊNH
        r'(QUY[EÊÉÈẾỀỂỄỆ]T\s+[ĐD][IỊ]NH(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴĐÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸ]{1,30})?)',
        
        # ĐƠN XIN
        r'(Đ[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]N\s+XIN(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴĐÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸ]{1,30})?)',
        
        # BIÊN BẢN
        r'(BI[EÊÉÈẾỀỂỄỆ]N\s+B[AẢ]N(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴĐÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸ]{1,30})?)',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Debug: Log matched pattern for troubleshooting
            import sys
            print(f"🎯 Pattern matched: {pattern[:50]}... → Extracted: '{title[:80]}'", file=sys.stderr)
            
            # Clean up: remove trailing lowercase text or noise
            # Keep only the uppercase title part
            title = re.sub(r'\s+[a-zàáạảãâầấậẩẫăằắặẳẵđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ].*$', '', title)
            
            if title and len(title) < 200:
                return title
    
    return ""


def process_document(file_path: str, ocr_engine_type: str = 'tesseract', cloud_api_key: str = None, cloud_endpoint: str = None) -> dict:
    """
    Process a document using OCR + Rules with font height detection
    
    Args:
        file_path: Path to the image file
        ocr_engine_type: 'tesseract', 'vietocr', 'easyocr', 'google', 'azure', or 'gemini-flash'
        cloud_api_key: API key for cloud OCR/AI (Google/Azure/Gemini)
        cloud_endpoint: Endpoint URL for Azure (optional for Google/Gemini)
    
    Returns classification result with confidence
    """
    try:
        # Handle Gemini Flash (AI classification) - POSITION-AWARE APPROACH
        if ocr_engine_type == 'gemini-flash':
            if not cloud_api_key:
                return {
                    "success": False,
                    "error": "Google API key is required for Gemini Flash",
                    "method": "config_error"
                }
            
            print("🤖 Using Gemini Flash AI with POSITION-AWARE classification", file=sys.stderr)
            
            # Import classification function
            from ocr_engine_gemini_flash import classify_document_gemini_flash
            from rule_classifier import classify_document_name_from_code
            import time
            
            # SINGLE SCAN with full image (position-aware)
            print("📸 Scanning FULL IMAGE with position-aware analysis...", file=sys.stderr)
            start_time = time.time()
            
            result = classify_document_gemini_flash(file_path, cloud_api_key, crop_top_percent=1.0)
            
            scan_time = time.time() - start_time
            print(f"⏱️ Result: {result.get('short_code')} (confidence: {result.get('confidence'):.2f}, position: {result.get('title_position', 'unknown')}, time: {scan_time:.1f}s)", file=sys.stderr)
            
            # Check for errors
            if result.get("short_code") == "ERROR":
                return {
                    "success": False,
                    "error": result.get("reasoning", "Gemini Flash error"),
                    "method": "gemini_flash_failed"
                }
            
            # Validate position-aware classification
            title_position = result.get("title_position", "unknown")
            short_code = result.get("short_code", "UNKNOWN")
            
            # If title found in middle/bottom (not top), it's likely a mention, not a title
            if title_position in ["middle", "bottom"] and short_code != "UNKNOWN":
                print(f"⚠️ Title found at {title_position} (not top), treating as mention", file=sys.stderr)
                # Override to UNKNOWN since title is not at top
                result["short_code"] = "UNKNOWN"
                result["confidence"] = 0.1
                result["reasoning"] = f"Text pattern found at {title_position}, not a main title"
            
            method_used = "gemini_position_aware"
                    'full_time': f"{full_time:.1f}s" if result_full.get("short_code") != "ERROR" else "N/A",
                    'total_time': f"{crop_time + full_time:.1f}s" if result_full.get("short_code") != "ERROR" else f"{crop_time:.1f}s",
                    'used_full': result_full.get("short_code") != "ERROR"
                }
            else:
                print(f"✅ High confidence ({confidence_crop:.2f}), using crop result only", file=sys.stderr)
                result = result_crop
                method_used = "gemini_crop_only"
                
                # Add statistics
                result['hybrid_stats'] = {
                    'crop_result': short_code_crop,
                    'crop_confidence': confidence_crop,
                    'crop_time': f"{crop_time:.1f}s",
                    'used_full': False
                }
            
            # Map Gemini result to rule_classifier format
            short_code = result.get("short_code", "UNKNOWN")
            doc_name = classify_document_name_from_code(short_code)
            
            return {
                "success": True,
                "type": short_code,
                "doc_type": doc_name,
                "short_code": short_code,
                "confidence": result.get("confidence", 0.5),
                "matched_keywords": [result.get("reasoning", "AI classification")],
                "title_boost_applied": True if short_code != "UNKNOWN" else False,
                "title_extracted_via_pattern": True if short_code != "UNKNOWN" else False,
                "reasoning": result.get("reasoning", ""),
                "method": method_used,
                "accuracy_estimate": f"{int(result.get('confidence', 0.5) * 100)}%",
                "recommend_cloud_boost": False,
                "avg_font_height": 0,
                "hybrid_stats": result.get('hybrid_stats', {})
            }
        
        # Handle Cloud OCR engines
        if ocr_engine_type == 'google':
            if not cloud_api_key:
                return {
                    "success": False,
                    "error": "Google Cloud Vision API key is required",
                    "method": "config_error"
                }
            
            print("☁️ Using Google Cloud Vision", file=sys.stderr)
            
            # Import and run Google OCR
            from ocr_engine_google import ocr_google_cloud_vision
            text, confidence, error = ocr_google_cloud_vision(file_path, cloud_api_key)
            
            if error:
                return {
                    "success": False,
                    "error": error,
                    "method": "cloud_ocr_failed"
                }
            
            engine_name = "Google Cloud Vision"
            extracted_text = text
            ocr_confidence = confidence
            
        elif ocr_engine_type == 'azure':
            if not cloud_api_key or not cloud_endpoint:
                return {
                    "success": False,
                    "error": "Azure Computer Vision API key and endpoint are required",
                    "method": "config_error"
                }
            
            print("☁️ Using Azure Computer Vision", file=sys.stderr)
            
            # Import and run Azure OCR
            from ocr_engine_azure import ocr_azure_computer_vision
            text, confidence, error = ocr_azure_computer_vision(file_path, cloud_api_key, cloud_endpoint)
            
            if error:
                return {
                    "success": False,
                    "error": error,
                    "method": "cloud_ocr_failed"
                }
            
            engine_name = "Azure Computer Vision"
            extracted_text = text
            ocr_confidence = confidence
            
        else:
            # Offline OCR engines - Lazy load on demand
            global tesseract_engine, vietocr_engine, easyocr_engine
            
            # Select OCR engine based on preference
            if ocr_engine_type == 'vietocr':
                # Lazy load VietOCR
                if vietocr_engine is None:
                    try:
                        from ocr_engine_vietocr import OCREngine as VietOCREngine
                        vietocr_engine = VietOCREngine()
                        print("✅ VietOCR engine loaded", file=sys.stderr)
                    except Exception as e:
                        print(f"⚠️ VietOCR load failed: {e}, falling back to Tesseract", file=sys.stderr)
                
                if vietocr_engine is not None:
                    ocr_engine = vietocr_engine
                    engine_name = "VietOCR"
                    print("🔍 Using VietOCR engine", file=sys.stderr)
                else:
                    # Fallback to Tesseract
                    if tesseract_engine is None:
                        from ocr_engine_tesseract import OCREngine as TesseractEngine
                        tesseract_engine = TesseractEngine()
                    ocr_engine = tesseract_engine
                    engine_name = "Tesseract"
                    
            elif ocr_engine_type == 'easyocr':
                # Lazy load EasyOCR
                if easyocr_engine is None:
                    try:
                        from ocr_engine_easyocr import OCREngine as EasyOCREngine
                        easyocr_engine = EasyOCREngine()
                        print("✅ EasyOCR engine loaded", file=sys.stderr)
                    except Exception as e:
                        print(f"⚠️ EasyOCR load failed: {e}, falling back to Tesseract", file=sys.stderr)
                
                if easyocr_engine is not None:
                    ocr_engine = easyocr_engine
                    engine_name = "EasyOCR"
                    print("🔍 Using EasyOCR engine", file=sys.stderr)
                else:
                    # Fallback to Tesseract
                    if tesseract_engine is None:
                        from ocr_engine_tesseract import OCREngine as TesseractEngine
                        tesseract_engine = TesseractEngine()
                    ocr_engine = tesseract_engine
                    engine_name = "Tesseract"
                    
            else:
                # Default to Tesseract
                if tesseract_engine is None:
                    try:
                        from ocr_engine_tesseract import OCREngine as TesseractEngine
                        tesseract_engine = TesseractEngine()
                        print("✅ Tesseract engine loaded", file=sys.stderr)
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Tesseract not available: {e}",
                            "method": "engine_load_failed"
                        }
                
                ocr_engine = tesseract_engine
                engine_name = "Tesseract"
                print("🔍 Using Tesseract engine", file=sys.stderr)
            
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
            
            ocr_confidence = None  # Not available for offline engines
        
        classifier = RuleClassifier()
        
        if not extracted_text or extracted_text.strip() == "":
            return {
                "success": False,
                "error": "Không thể trích xuất text từ ảnh",
                "method": "ocr_failed"
            }
        
        # Debug: Print full extracted text to see what OCR captured
        print(f"📝 Full text (first 500 chars): {extracted_text[:500]}", file=sys.stderr)
        
        # Try to extract real title from full text using patterns
        extracted_title = extract_document_title_from_text(extracted_text)
        
        if extracted_title:
            print(f"✅ Extracted title via pattern: {extracted_title[:80]}...", file=sys.stderr)
        else:
            print("⚠️ No title pattern found in full text", file=sys.stderr)
        
        # Priority:
        # 1. If we found a title via patterns → use it
        # 2. Otherwise use title_text from OCR (or full text for cloud)
        if extracted_title:
            final_title = extracted_title
        elif ocr_engine_type in ['google', 'azure']:
            # For cloud OCR, use extracted text (no separate title_text)
            final_title = extracted_text
        else:
            final_title = title_text
        
        # Classify using rules with title text priority
        # Pass engine type to classifier for smart title validation
        result = classifier.classify(extracted_text, title_text=final_title, ocr_engine=ocr_engine_type)
        
        # Handle case where classification completely fails (no doc_type found)
        if not result or 'doc_type' not in result:
            result = {
                'doc_type': 'Không xác định',
                'short_code': 'UNKNOWN',
                'confidence': 0.0,
                'reasoning': 'Không thể nhận diện loại tài liệu'
            }
        
        # Determine if Cloud Boost is recommended (only for offline engines)
        confidence_threshold = 0.7
        is_cloud = ocr_engine_type in ['google', 'azure']
        recommend_cloud_boost = not is_cloud and result['confidence'] < confidence_threshold
        
        # Add title boost indicator
        title_boost_info = ""
        if result.get('title_boost', False):
            title_boost_info = " [TITLE DETECTED ✓]"
        
        response = {
            "success": True,
            "method": "cloud_ocr" if is_cloud else "offline_ocr",
            "ocr_engine": engine_name,
            "original_text": extracted_text,
            "title_text": final_title,  # Use final_title (pattern or OCR)
            "title_extracted_via_pattern": bool(extracted_title),
            "doc_type": result['doc_type'],
            "confidence": result['confidence'],
            "short_code": result['short_code'],
            "reasoning": result.get('reasoning', '') + title_boost_info,
            "recommend_cloud_boost": recommend_cloud_boost,
            "title_boost_applied": result.get('title_boost', False)
        }
        
        # Add cloud-specific fields
        if is_cloud:
            response["ocr_confidence"] = float(ocr_confidence) if ocr_confidence else 0.9
            response["accuracy_estimate"] = "90-96%"
        else:
            # Offline engines
            response["title_text_ocr"] = title_text if 'title_text' in locals() else final_title
            response["avg_font_height"] = round(avg_height, 1) if 'avg_height' in locals() else 0
            response["accuracy_estimate"] = "88-91%" if result.get('title_boost') else "85-88%"
        
        return response
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ Error: {error_detail}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "method": "processing_failed"
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python process_document.py <file_path> [ocr_engine_type] [cloud_api_key] [cloud_endpoint]",
            "success": False
        }, ensure_ascii=True))
        sys.exit(1)
    
    file_path = sys.argv[1]
    ocr_engine_type = sys.argv[2] if len(sys.argv) > 2 else 'tesseract'
    cloud_api_key = sys.argv[3] if len(sys.argv) > 3 else None
    cloud_endpoint = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not file_path or not os.path.exists(file_path):
        error_msg = json.dumps({
            "error": "File not found or invalid path",
            "success": False
        }, ensure_ascii=False)
        sys.stdout.write(error_msg)
        sys.stdout.write('\n')
        sys.stdout.flush()
        sys.exit(1)
    
    result = process_document(file_path, ocr_engine_type, cloud_api_key, cloud_endpoint)
    
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
