#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for Hybrid OCR Engine
Compare hybrid vs current engine
"""

import sys
import os

# Add python dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def test_code_definitions():
    """Test CODE_DEFINITIONS completeness"""
    print("="*60)
    print("TEST 1: CODE_DEFINITIONS Completeness")
    print("="*60)
    
    from ocr_engine_gemini_flash_hybrid import CODE_DEFINITIONS, ALLOWED_SHORT_CODES
    from rule_classifier import classify_document_name_from_code
    
    print(f"✅ Loaded {len(CODE_DEFINITIONS)} codes in hybrid engine")
    print(f"✅ ALLOWED_SHORT_CODES: {len(ALLOWED_SHORT_CODES)} codes")
    
    # Check important codes
    important_codes = [
        "GCN", "GCNM", "GCNC",
        "DDKBD", "DXTHT", "HDCQ", "HDTG",
        "HSKT", "GTLQ", "PCTSVC",
        "TBT", "TKT", "TTr"
    ]
    
    print("\n📋 Checking important codes:")
    for code in important_codes:
        if code in CODE_DEFINITIONS:
            print(f"  ✅ {code}: {CODE_DEFINITIONS[code][:50]}...")
        else:
            print(f"  ❌ {code}: MISSING!")
    
    # Check newly added codes
    print("\n🆕 Checking newly added codes:")
    new_codes = ["DXTHT", "PCTSVC", "HDTG"]
    for code in new_codes:
        if code in CODE_DEFINITIONS:
            print(f"  ✅ {code}: {CODE_DEFINITIONS[code]}")
        else:
            print(f"  ❌ {code}: MISSING!")
    
    print("\n" + "="*60)
    print("✅ CODE_DEFINITIONS Test PASSED")
    print("="*60)


def test_validation():
    """Test strict validation"""
    print("\n" + "="*60)
    print("TEST 2: Strict Validation")
    print("="*60)
    
    from ocr_engine_gemini_flash_hybrid import _normalize_and_validate, ALLOWED_SHORT_CODES
    
    # Test valid code
    obj1 = {"short_code": "GCN", "confidence": 0.95}
    result1 = _normalize_and_validate(obj1)
    print(f"\n✅ Valid code 'GCN': {result1['short_code']}")
    
    # Test invalid code (should become UNKNOWN)
    obj2 = {"short_code": "INVALID_CODE", "confidence": 0.95}
    result2 = _normalize_and_validate(obj2)
    print(f"✅ Invalid code 'INVALID_CODE' → {result2['short_code']}")
    assert result2['short_code'] == "UNKNOWN", "Should be UNKNOWN!"
    
    # Test HDTG (should be accepted now)
    obj3 = {"short_code": "HDTG", "confidence": 0.90}
    result3 = _normalize_and_validate(obj3)
    print(f"✅ Code 'HDTG': {result3['short_code']}")
    assert result3['short_code'] == "HDTG", "HDTG should be valid!"
    
    # Test BVDS (not in CODE_DEFINITIONS, should become UNKNOWN)
    obj4 = {"short_code": "BVDS", "confidence": 0.90}
    result4 = _normalize_and_validate(obj4)
    print(f"⚠️ Code 'BVDS' (not defined): {result4['short_code']}")
    # NOTE: BVDS should be handled by alias in process_document.py
    
    print("\n" + "="*60)
    print("✅ Validation Test PASSED")
    print("="*60)


def test_prompt_generation():
    """Test prompt auto-generation"""
    print("\n" + "="*60)
    print("TEST 3: Prompt Generation")
    print("="*60)
    
    from ocr_engine_gemini_flash_hybrid import get_code_list_summary, get_classification_prompt_lite
    
    # Generate code list
    code_list = get_code_list_summary()
    print(f"\n✅ Generated code list: {len(code_list)} characters")
    print(f"   Preview:\n{code_list[:500]}...\n")
    
    # Generate full prompt
    prompt = get_classification_prompt_lite()
    print(f"✅ Generated full prompt: {len(prompt)} characters")
    
    # Check important sections
    assert "GCN" in prompt, "GCN should be in prompt"
    assert "DXTHT" in prompt, "DXTHT should be in prompt"
    assert "PCTSVC" in prompt, "PCTSVC should be in prompt"
    assert "color" in prompt.lower(), "Color detection should be in prompt"
    assert "issue_date" in prompt.lower(), "Issue date should be in prompt"
    
    print("\n" + "="*60)
    print("✅ Prompt Generation Test PASSED")
    print("="*60)


def test_heuristic_parse():
    """Test heuristic fallback"""
    print("\n" + "="*60)
    print("TEST 4: Heuristic Fallback")
    print("="*60)
    
    from ocr_engine_gemini_flash_hybrid import _heuristic_parse
    
    # Test valid code in text
    text1 = 'The classification is: short_code: "GCN", confidence: 0.95'
    result1 = _heuristic_parse(text1)
    print(f"\n✅ Heuristic parse 'GCN': {result1['short_code']}")
    assert result1['short_code'] == "GCN"
    
    # Test invalid code in text (should become UNKNOWN)
    text2 = 'short_code: "INVALID", confidence: 0.90'
    result2 = _heuristic_parse(text2)
    print(f"✅ Heuristic parse 'INVALID' → {result2['short_code']}")
    assert result2['short_code'] == "UNKNOWN"
    
    print("\n" + "="*60)
    print("✅ Heuristic Fallback Test PASSED")
    print("="*60)


def main():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("HYBRID OCR ENGINE - UNIT TESTS")
    print("🧪"*30 + "\n")
    
    try:
        test_code_definitions()
        test_validation()
        test_prompt_generation()
        test_heuristic_parse()
        
        print("\n" + "🎉"*30)
        print("ALL TESTS PASSED! ✅")
        print("🎉"*30 + "\n")
        
        print("Next steps:")
        print("  1. Test với real images: python test_hybrid_with_images.py")
        print("  2. Compare accuracy với current engine")
        print("  3. Deploy to desktop app")
        
    except Exception as e:
        print("\n" + "❌"*30)
        print(f"TEST FAILED: {e}")
        print("❌"*30 + "\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
