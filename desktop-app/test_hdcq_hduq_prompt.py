#!/usr/bin/env python3
"""
Test script to verify HDCQ vs HDUQ distinction in Gemini prompts
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ocr_engine_gemini_flash import get_classification_prompt_lite

def test_prompt_contains_hduq_distinction():
    """Test if prompt clearly distinguishes HDCQ from HDUQ"""
    
    prompt = get_classification_prompt_lite()
    
    print("=" * 80)
    print("TESTING HDCQ vs HDUQ DISTINCTION IN GEMINI LITE PROMPT")
    print("=" * 80)
    
    # Check 1: Prompt mentions both HDCQ and HDUQ
    has_hdcq = "HDCQ" in prompt
    has_hduq = "HDUQ" in prompt
    
    print(f"\n✓ Prompt contains HDCQ: {has_hdcq}")
    print(f"✓ Prompt contains HDUQ: {has_hduq}")
    
    # Check 2: Prompt explains the difference
    has_chuyen_nhuong = "chuyển nhượng" in prompt.lower() or "CHUYỂN NHƯỢNG" in prompt
    has_uy_quyen = "ủy quyền" in prompt.lower() or "ỦY QUYỀN" in prompt
    
    print(f"\n✓ Prompt mentions 'chuyển nhượng': {has_chuyen_nhuong}")
    print(f"✓ Prompt mentions 'ủy quyền': {has_uy_quyen}")
    
    # Check 3: Look for explicit distinction
    has_distinction = "PHÂN BIỆT" in prompt or "khác" in prompt.lower()
    
    print(f"\n✓ Prompt has explicit distinction: {has_distinction}")
    
    # Check 4: Look for examples
    has_hdcq_example = "HỢP ĐỒNG CHUYỂN NHƯỢNG" in prompt
    has_hduq_example = "HỢP ĐỒNG ỦY QUYỀN" in prompt
    
    print(f"\n✓ Prompt has HDCQ example: {has_hdcq_example}")
    print(f"✓ Prompt has HDUQ example: {has_hduq_example}")
    
    # Extract relevant sections
    print("\n" + "=" * 80)
    print("RELEVANT SECTIONS FROM PROMPT:")
    print("=" * 80)
    
    lines = prompt.split('\n')
    in_contract_section = False
    in_example_section = False
    
    for i, line in enumerate(lines):
        if "NHÓM 2 - HỢP ĐỒNG" in line:
            in_contract_section = True
            print(f"\n>>> Found at line {i+1}:")
            
        if in_contract_section:
            print(line)
            if line.strip() == "" and i > 0 and lines[i-1].startswith("NHÓM"):
                in_contract_section = False
            if "NHÓM 3" in line:
                in_contract_section = False
                
        if "VÍ DỤ THỰC TẾ" in line or "✅ ĐÚNG:" in line:
            in_example_section = True
            
        if in_example_section and ("HDCQ" in line or "HDUQ" in line or "HỢP ĐỒNG" in line):
            print(f"\n>>> Example at line {i+1}:")
            # Print context
            for j in range(max(0, i-1), min(len(lines), i+4)):
                print(lines[j])
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_checks = [
        has_hdcq,
        has_hduq,
        has_chuyen_nhuong,
        has_uy_quyen,
        has_distinction,
        has_hdcq_example,
        has_hduq_example
    ]
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n✅ SUCCESS: Prompt properly distinguishes HDCQ from HDUQ!")
        return True
    else:
        print("\n❌ FAILURE: Prompt needs improvement!")
        return False

if __name__ == "__main__":
    success = test_prompt_contains_hduq_distinction()
    sys.exit(0 if success else 1)
