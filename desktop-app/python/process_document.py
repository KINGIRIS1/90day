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
    """
    import re

    title_patterns = [
        # GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ (GTLQ)
        r'(GI[AÁẤ]Y\s+TI[EÊÉÈẾỀỂỄỆ]P\s+NH[ẬAĂÂÁÀÃẠÂẤĂẮ]N\s+H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ][\s]*S[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]|GI[AÁẤ]Y\s+TI[EÊÉÈẾỀỂỄỆ]P\s+NH[ẬAĂÂÁÀÃẠÂẤĂẮ]N\s+HỎ\s*SƠ)\s+V[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]\s+HẸN\s+TRẢ\s+K[ÊE]T\s+QUẢ',
        # ĐƠN ĐĂNG KÝ BIẾN ĐỘNG
        r'(Đ[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]N\s+[ĐD][AĂ]NG\s+K[YÝ]\s+BI[EÊÉÈẾỀỂỄỆ]N\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG(?:\s+[ĐD][AÁẤ]T\s+[ĐD]AI)?(?:\s*,?\s*T[AÀ]I\s+S[AẢ]N)?(?:\s+G[AẮ]N\s+LI[EÊÉÈẾỀỂỄỆ]N\s+V[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]I\s+[ĐD][AÁẤ]T)?)',
        # HỢP ĐỒNG CHUYỂN NHƯỢNG
        r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+CHUY[EÊÉÈẾỀỂỄỆ]N\s+NH[UƯÚÙỦŨỤỨỪỬỮỰ][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG(?:\s+QUY[EÊÉÈẾỀỂỄỆ]N)?(?:\s+S[UƯÚÙỦŨỤỨỪỬỮỰ]\s+D[UỤ]NG\s+[ĐD][AÁẤ]T)?)',
        # HỢP ĐỒNG ỦY QUYỀN
        r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+(?:[UỦ][\sỶ]*Y|U[ỶY])\s+QUY[EÊÉÈẾỀỂỄỆ]N)',
        # GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT
        r'(GI[AÁẤ]Y\s+CH[UƯÚÙỦŨỤỨỪỬỮỰ]NG\s+NH[AẬ]N\s+QUY[EÊÉÈẾỀỂỄỆ]N\s+S[UƯÚÙỦŨỤỨỪỬỮỰ]\s+D[UỤ]NG\s+[ĐD][AÁẤ]T)',
        # GIẤY ỦY QUYỀN
        r'(GI[AÁẤ]Y\s+(?:[UỦ][\sỶ]*Y|U[ỶY])\s+QUY[EÊÉÈẾỀỂỄỆ]N)',
        # QUYẾT ĐỊNH (khái quát)
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
            # Keep only the uppercase title part
            title = re.sub(r'\s+[a-zàáạảãâầấậẩẫăằắặẳẵđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ].*$', '', title)
            if title and len(title) < 200:
                return title
    return ""


def process_document(file_path: str, ocr_engine_type: str = 'tesseract', cloud_api_key: str = None, cloud_endpoint: str = None) -> dict:
    """
    Process a document using OCR + Rules with font height detection
    """
    try:
        # Handle Gemini Flash Hybrid (Two-Tier AI classification)
        if ocr_engine_type == 'gemini-flash-hybrid':
            if not cloud_api_key:
                return {
                    "success": False,
                    "error": "Google API key is required for Gemini Flash Hybrid",
                    "method": "config_error"
                }

            print(f"🔄 Using Gemini Flash HYBRID (Two-Tier) classification", file=sys.stderr)

            from ocr_engine_gemini_flash_hybrid import classify_document_gemini_flash_hybrid
            from rule_classifier import classify_document_name_from_code
            import time

            # Get resize settings from environment (set by Electron)
            enable_resize = os.environ.get('ENABLE_RESIZE', 'true').lower() == 'true'
            max_width = int(os.environ.get('MAX_WIDTH', '1500'))
            max_height = int(os.environ.get('MAX_HEIGHT', '2100'))
            
            # Get confidence threshold from environment (default: 0.80)
            confidence_threshold = float(os.environ.get('HYBRID_CONFIDENCE_THRESHOLD', '0.80'))

            print(f"📸 Two-Tier strategy:", file=sys.stderr)
            print(f"   ├─ Tier 1: Flash Lite (60% crop) for easy documents", file=sys.stderr)
            print(f"   ├─ Tier 2: Flash Full (100% image) if confidence < {confidence_threshold:.0%} or complex doc", file=sys.stderr)
            print(f"   └─ Smart resize: max {max_width}x{max_height}px", file=sys.stderr)
            
            start_time = time.time()

            # Call hybrid engine
            result = classify_document_gemini_flash_hybrid(
                image_path=file_path, 
                api_key=cloud_api_key, 
                confidence_threshold=confidence_threshold,
                complex_doc_types=['GCN', 'GCNM', 'GCNC'],
                enable_resize=enable_resize,
                max_width=max_width,
                max_height=max_height
            )

            scan_time = time.time() - start_time
            tier_used = result.get('tier_used', 'unknown')
            print(f"⏱️ Result: {result.get('short_code')} (confidence: {result.get('confidence'):.2f}, tier: {tier_used}, time: {scan_time:.1f}s)", file=sys.stderr)
            
            method_used = "gemini_hybrid_two_tier"
            
            # Check for errors
            if result.get("short_code") == "ERROR":
                return {
                    "success": False,
                    "error": result.get("reasoning", "Gemini Hybrid error"),
                    "method": "gemini_hybrid_failed"
                }
            
            # Common processing for all Gemini modes (hybrid + flash + lite)
            from rule_classifier import classify_document_name_from_code, EXACT_TITLE_MAPPING, DOCUMENT_RULES
            
            short_code = result.get("short_code", "UNKNOWN")
            
            # ✅ CODE ALIAS MAPPING: Map alternate codes to standard codes
            CODE_ALIASES = {
                "HDTG": "HDCQ",  # Hợp đồng tặng cho → Hợp đồng chuyển nhượng, tặng cho
                "BVDS": "HSKT",  # Bản vẽ đo sơ / Bản đồ địa chính → Hồ sơ kỹ thuật
            }
            
            # Apply alias mapping if needed
            if short_code in CODE_ALIASES:
                original_code = short_code
                short_code = CODE_ALIASES[short_code]
                result["short_code"] = short_code
                print(f"🔄 Mapped code '{original_code}' → '{short_code}'", file=sys.stderr)
            
            # ✅ VALIDATE: Gemini sometimes creates invalid codes (e.g., "LCHO" not in our 98 valid codes)
            # Get all valid codes from rule_classifier
            VALID_CODES = set(EXACT_TITLE_MAPPING.values())
            VALID_CODES.update(DOCUMENT_RULES.keys())
            
            # If Gemini returns invalid code, force to UNKNOWN
            if short_code not in VALID_CODES and short_code != "UNKNOWN":
                print(f"⚠️ Gemini Hybrid returned INVALID code '{short_code}' (not in 98 valid codes). Forcing to UNKNOWN.", file=sys.stderr)
                print(f"   Original reasoning: {result.get('reasoning', 'N/A')}", file=sys.stderr)
                result["short_code"] = "UNKNOWN"
                result["confidence"] = 0.1
                result["reasoning"] = f"AI returned invalid code '{short_code}' (not in system). Original: {result.get('reasoning', '')}"
                short_code = "UNKNOWN"
            
            doc_name = classify_document_name_from_code(short_code)

            # Extract color, issue_date and issue_date_confidence for GCN documents
            color = result.get("color", None)
            issue_date = result.get("issue_date", None)
            issue_date_confidence = result.get("issue_date_confidence", None)
            
            # Tier-specific metadata for hybrid mode
            tier1_confidence = result.get('tier1_confidence', 0)
            tier2_confidence = result.get('tier2_confidence', None)
            escalation_reason = result.get('escalation_reason', 'none')
            
            return {
                "success": True,
                "type": short_code,
                "doc_type": doc_name,
                "short_code": short_code,
                "confidence": result.get("confidence", 0.5),
                "matched_keywords": [result.get("reasoning", "Hybrid AI classification")],
                "title_boost_applied": True if short_code != "UNKNOWN" else False,
                "title_extracted_via_pattern": True if short_code != "UNKNOWN" else False,
                "reasoning": result.get("reasoning", ""),
                "color": color,
                "issue_date": issue_date,
                "issue_date_confidence": issue_date_confidence,
                "method": method_used,
                "accuracy_estimate": f"{int(result.get('confidence', 0.5) * 100)}%",
                "recommend_cloud_boost": False,
                "avg_font_height": 0,
                # Hybrid-specific stats
                "tier_used": tier_used,
                "tier1_confidence": tier1_confidence,
                "tier2_confidence": tier2_confidence,
                "escalation_reason": escalation_reason,
                "cost_estimate": result.get('cost_estimate', 'medium'),
                "usage": {},  # Hybrid mode doesn't expose token counts directly
                "estimated_cost_usd": 0  # Could be calculated based on tier_used
            }

        # Handle OpenAI GPT-4o mini Vision (AI classification)
        elif ocr_engine_type == 'openai-gpt4o-mini':
            if not cloud_api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key is required for GPT-4o mini",
                    "method": "config_error"
                }

            print(f"🤖 Using OpenAI GPT-4o mini Vision AI classification", file=sys.stderr)

            from ocr_engine_openai_vision import classify_document_openai_vision
            from rule_classifier import classify_document_name_from_code
            import time

            # Get resize settings from environment (set by Electron)
            enable_resize = os.environ.get('ENABLE_RESIZE', 'true').lower() == 'true'
            max_width = int(os.environ.get('MAX_WIDTH', '1500'))
            max_height = int(os.environ.get('MAX_HEIGHT', '2100'))

            if enable_resize:
                print(f"💰 Smart resize enabled: max {max_width}x{max_height}px", file=sys.stderr)
            start_time = time.time()

            # Call OpenAI Vision classifier
            result = classify_document_openai_vision(
                file_path, 
                cloud_api_key,
                enable_resize=enable_resize,
                max_width=max_width,
                max_height=max_height
            )

            scan_time = time.time() - start_time
            print(f"⏱️ Result: {result.get('short_code')} (confidence: {result.get('confidence'):.2f}, time: {scan_time:.1f}s)", file=sys.stderr)

            if result.get("short_code") == "ERROR":
                return {
                    "success": False,
                    "error": result.get("reasoning", "OpenAI Vision error"),
                    "method": "openai_vision_failed"
                }

            method_used = "openai_gpt4o_mini_vision"
            short_code = result.get("short_code", "UNKNOWN")

            # Code alias mapping (same as Gemini)
            from rule_classifier import EXACT_TITLE_MAPPING, DOCUMENT_RULES
            CODE_ALIASES = {
                "HDTG": "HDCQ",
                "BVDS": "HSKT",
            }
            
            if short_code in CODE_ALIASES:
                original_code = short_code
                short_code = CODE_ALIASES[short_code]
                result["short_code"] = short_code
                print(f"🔄 Mapped code '{original_code}' → '{short_code}'", file=sys.stderr)
            
            # Validate code
            VALID_CODES = set(EXACT_TITLE_MAPPING.values())
            VALID_CODES.update(DOCUMENT_RULES.keys())
            
            if short_code not in VALID_CODES and short_code != "UNKNOWN":
                print(f"⚠️ OpenAI returned INVALID code '{short_code}'. Forcing to UNKNOWN.", file=sys.stderr)
                result["short_code"] = "UNKNOWN"
                result["confidence"] = 0.1
                result["reasoning"] = f"AI returned invalid code '{short_code}'. Original: {result.get('reasoning', '')}"
                short_code = "UNKNOWN"
            
            doc_name = classify_document_name_from_code(short_code)

            # Extract GCN metadata
            color = result.get("color", None)
            issue_date = result.get("issue_date", None)
            issue_date_confidence = result.get("issue_date_confidence", None)
            
            # Calculate cost (OpenAI pricing)
            usage = result.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            
            # GPT-4o mini pricing (as of Jan 2025)
            # Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
            cost_usd = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
            
            return {
                "success": True,
                "type": short_code,
                "doc_type": doc_name,
                "short_code": short_code,
                "confidence": result.get("confidence", 0.5),
                "matched_keywords": [result.get("reasoning", "OpenAI AI classification")],
                "title_boost_applied": True if short_code != "UNKNOWN" else False,
                "title_extracted_via_pattern": True if short_code != "UNKNOWN" else False,
                "reasoning": result.get("reasoning", ""),
                "color": color,
                "issue_date": issue_date,
                "issue_date_confidence": issue_date_confidence,
                "method": method_used,
                "accuracy_estimate": f"{int(result.get('confidence', 0.5) * 100)}%",
                "recommend_cloud_boost": False,
                "avg_font_height": 0,
                "usage": usage,
                "estimated_cost_usd": cost_usd
            }

        # Handle Gemini Flash & Tesseract+Text (AI classification) - POSITION-AWARE APPROACH
        elif ocr_engine_type in ['gemini-flash', 'gemini-flash-lite', 'gemini-flash-hybrid', 'gemini-flash-text']:
            if not cloud_api_key:
                return {
                    "success": False,
                    "error": "Google API key is required for Gemini Flash",
                    "method": "config_error"
                }

            # Check if Tesseract+Text mode
            if ocr_engine_type == 'gemini-flash-text':
                print(f"🔬 Using Tesseract + Gemini Text mode (sequential)", file=sys.stderr)
                from tesseract_text_classifier import process_image as tesseract_text_process
                import time
                
                start_time = time.time()
                result = tesseract_text_process(file_path, cloud_api_key)
                scan_time = time.time() - start_time
                
                print(f"⏱️ Result: {result.get('short_code')} (confidence: {result.get('confidence'):.2f}, time: {scan_time:.1f}s)", file=sys.stderr)
                
                if result.get("short_code") == "ERROR":
                    return {
                        "success": False,
                        "error": result.get("reasoning", "Tesseract+Text error"),
                        "method": "tesseract_text_failed"
                    }
                
                method_used = "tesseract_text"
                short_code = result.get("short_code", "UNKNOWN")
            else:
                # Standard Gemini Vision mode
                model_type = 'Lite' if ocr_engine_type == 'gemini-flash-lite' else 'Flash'
                if ocr_engine_type == 'gemini-flash-hybrid':
                    model_type = 'Hybrid'
                print(f"🤖 Using Gemini {model_type} AI with POSITION-AWARE classification", file=sys.stderr)

                from ocr_engine_gemini_flash import classify_document_gemini_flash
                from rule_classifier import classify_document_name_from_code
                import time

                # Get resize settings from environment (set by Electron)
                enable_resize = os.environ.get('ENABLE_RESIZE', 'true').lower() == 'true'
                max_width = int(os.environ.get('MAX_WIDTH', '2000'))
                max_height = int(os.environ.get('MAX_HEIGHT', '2800'))

                print("📸 Scanning FULL IMAGE with position-aware analysis...", file=sys.stderr)
                if enable_resize:
                    print(f"💰 Smart resize enabled: max {max_width}x{max_height}px", file=sys.stderr)
                start_time = time.time()

                # Pass model type and resize settings to classifier
                result = classify_document_gemini_flash(
                    file_path, 
                    cloud_api_key, 
                    crop_top_percent=1.0, 
                    model_type=ocr_engine_type,
                    enable_resize=enable_resize,
                    max_width=max_width,
                    max_height=max_height
                )

                scan_time = time.time() - start_time
                print(f"⏱️ Result: {result.get('short_code')} (confidence: {result.get('confidence'):.2f}, position: {result.get('title_position', 'unknown')}, time: {scan_time:.1f}s)", file=sys.stderr)

                if result.get("short_code") == "ERROR":
                    return {
                        "success": False,
                        "error": result.get("reasoning", "Gemini Flash error"),
                        "method": "gemini_flash_failed"
                    }

                title_position = result.get("title_position", "unknown")
                short_code = result.get("short_code", "UNKNOWN")
                if title_position in ["middle", "bottom"] and short_code != "UNKNOWN":
                    print(f"⚠️ Title found at {title_position} (not top), treating as mention", file=sys.stderr)
                    result["short_code"] = "UNKNOWN"
                    result["confidence"] = 0.1
                    result["reasoning"] = f"Text pattern found at {title_position}, not a main title"

                method_used = "gemini_position_aware"

                # Map Gemini result to rule_classifier format
                short_code = result.get("short_code", "UNKNOWN")
            
            # ✅ CODE ALIAS MAPPING: Map alternate codes to standard codes
            CODE_ALIASES = {
                "HDTG": "HDCQ",  # Hợp đồng tặng cho → Hợp đồng chuyển nhượng, tặng cho
                "BVDS": "HSKT",  # Bản vẽ đo sơ / Bản đồ địa chính → Hồ sơ kỹ thuật
            }
            
            # Apply alias mapping if needed
            if short_code in CODE_ALIASES:
                original_code = short_code
                short_code = CODE_ALIASES[short_code]
                result["short_code"] = short_code
                print(f"🔄 Mapped code '{original_code}' → '{short_code}'", file=sys.stderr)
            
            # ✅ VALIDATE: Gemini sometimes creates invalid codes (e.g., "LCHO" not in our 98 valid codes)
            # Get all valid codes from rule_classifier
            from rule_classifier import EXACT_TITLE_MAPPING, DOCUMENT_RULES
            VALID_CODES = set(EXACT_TITLE_MAPPING.values())
            VALID_CODES.update(DOCUMENT_RULES.keys())
            
            # If Gemini returns invalid code, force to UNKNOWN
            if short_code not in VALID_CODES and short_code != "UNKNOWN":
                print(f"⚠️ Gemini returned INVALID code '{short_code}' (not in 98 valid codes). Forcing to UNKNOWN.", file=sys.stderr)
                print(f"   Original reasoning: {result.get('reasoning', 'N/A')}", file=sys.stderr)
                result["short_code"] = "UNKNOWN"
                result["confidence"] = 0.1
                result["reasoning"] = f"AI returned invalid code '{short_code}' (not in system). Original: {result.get('reasoning', '')}"
                short_code = "UNKNOWN"
            
            doc_name = classify_document_name_from_code(short_code)

            # Usage tokens for cost estimation
            usage = result.get('usage') or {}
            input_tokens = int(usage.get('input_tokens', 0) or 0)
            output_tokens = int(usage.get('output_tokens', 0) or 0)

            # Pricing (USD per 1,000,000 tokens) - configurable via env
            # Defaults aligned with AI Studio typical pricing; override via env when needed
            INPUT_RATE_PER_M = float(os.environ.get('GEMINI_INPUT_RATE_PER_M', '0.30') or 0)
            OUTPUT_RATE_PER_M = float(os.environ.get('GEMINI_OUTPUT_RATE_PER_M', '2.50') or 0)
            estimated_cost_usd = (input_tokens * INPUT_RATE_PER_M + output_tokens * OUTPUT_RATE_PER_M) / 1_000_000.0

            # Extract color, issue_date and issue_date_confidence for GCN documents
            color = result.get("color", None)
            issue_date = result.get("issue_date", None)
            issue_date_confidence = result.get("issue_date_confidence", None)
            
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
                "color": color,
                "issue_date": issue_date,
                "issue_date_confidence": issue_date_confidence,
                "method": method_used,
                "accuracy_estimate": f"{int(result.get('confidence', 0.5) * 100)}%",
                "recommend_cloud_boost": False,
                "avg_font_height": 0,
                "hybrid_stats": result.get('hybrid_stats', {}),
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": int(usage.get('total_tokens', input_tokens + output_tokens) or 0)
                },
                "estimated_cost_usd": round(estimated_cost_usd, 6)
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
                    if tesseract_engine is None:
                        from ocr_engine_tesseract import OCREngine as TesseractEngine
                        tesseract_engine = TesseractEngine()
                    ocr_engine = tesseract_engine
                    engine_name = "Tesseract"

            elif ocr_engine_type == 'easyocr':
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
                    if tesseract_engine is None:
                        from ocr_engine_tesseract import OCREngine as TesseractEngine
                        tesseract_engine = TesseractEngine()
                    ocr_engine = tesseract_engine
                    engine_name = "Tesseract"

            else:
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

            # Extract text
            ocr_result = ocr_engine.extract_text(file_path)
            if isinstance(ocr_result, dict):
                extracted_text = ocr_result.get('full_text', '')
                title_text = ocr_result.get('title_text', '')
                avg_height = ocr_result.get('avg_height', 0)
            else:
                extracted_text = ocr_result
                title_text = extracted_text
                avg_height = 0

            ocr_confidence = None

        classifier = RuleClassifier()

        if not extracted_text or extracted_text.strip() == "":
            return {
                "success": False,
                "error": "Không thể trích xuất text từ ảnh",
                "method": "ocr_failed"
            }

        print(f"📝 Full text (first 500 chars): {extracted_text[:500]}", file=sys.stderr)

        extracted_title = extract_document_title_from_text(extracted_text)
        if extracted_title:
            print(f"✅ Extracted title via pattern: {extracted_title[:80]}...", file=sys.stderr)
        else:
            print("⚠️ No title pattern found in full text", file=sys.stderr)

        if extracted_title:
            final_title = extracted_title
        elif ocr_engine_type in ['google', 'azure']:
            final_title = extracted_text
        else:
            final_title = title_text

        result = classifier.classify(extracted_text, title_text=final_title, ocr_engine=ocr_engine_type)
        if not result or 'doc_type' not in result:
            result = {
                'doc_type': 'Không xác định',
                'short_code': 'UNKNOWN',
                'confidence': 0.0,
                'reasoning': 'Không thể nhận diện loại tài liệu'
            }

        confidence_threshold = 0.7
        is_cloud = ocr_engine_type in ['google', 'azure']
        recommend_cloud_boost = not is_cloud and result['confidence'] < confidence_threshold

        title_boost_info = ""
        if result.get('title_boost', False):
            title_boost_info = " [TITLE DETECTED ✓]"

        response = {
            "success": True,
            "method": "cloud_ocr" if is_cloud else "offline_ocr",
            "ocr_engine": engine_name,
            "original_text": extracted_text,
            "title_text": final_title,
            "title_extracted_via_pattern": bool(extracted_title),
            "doc_type": result['doc_type'],
            "confidence": result['confidence'],
            "short_code": result['short_code'],
            "reasoning": result.get('reasoning', '') + title_boost_info,
            "recommend_cloud_boost": recommend_cloud_boost,
            "title_boost_applied": result.get('title_boost', False)
        }

        if is_cloud:
            response["ocr_confidence"] = float(ocr_confidence) if ocr_confidence else 0.9
            response["accuracy_estimate"] = "90-96%"
        else:
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

    output = json.dumps(result, ensure_ascii=True, indent=None)
    sys.stdout.write(output)
    sys.stdout.write('\n')
    sys.stdout.flush()

    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
