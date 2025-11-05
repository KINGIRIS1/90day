#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GCN Date-Based Classification
Verify that Gemini prompts request issue_date extraction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from ocr_engine_gemini_flash import get_classification_prompt_lite, get_classification_prompt

def test_prompts():
    print("=" * 80)
    print("Testing GCN Date-Based Classification Prompts")
    print("=" * 80)
    
    # Test lite prompt
    print("\n1. Testing get_classification_prompt_lite()...")
    lite_prompt = get_classification_prompt_lite()
    
    # Check for issue_date mentions
    checks = [
        ("issue_date", "issue_date field"),
        ("ngày cấp", "Vietnamese 'ngày cấp' (issue date)"),
        ("issue_date_confidence", "issue_date_confidence field"),
        ("DD/MM/YYYY", "Full date format"),
        ("MM/YYYY", "Partial date format"),
        ("YYYY", "Year-only format"),
        ("not_found", "not_found confidence level"),
        ("viết tay", "handwriting mention")
    ]
    
    print("\n✅ Lite Prompt Checks:")
    for keyword, description in checks:
        if keyword in lite_prompt:
            print(f"  ✅ Found: {description}")
        else:
            print(f"  ❌ Missing: {description}")
    
    # Test full prompt
    print("\n2. Testing get_classification_prompt()...")
    full_prompt = get_classification_prompt()
    
    print("\n✅ Full Prompt Checks:")
    for keyword, description in checks:
        if keyword in full_prompt:
            print(f"  ✅ Found: {description}")
        else:
            print(f"  ❌ Missing: {description}")
    
    # Verify old certificate_number is removed or commented
    print("\n3. Checking for old certificate_number mentions...")
    
    if "certificate_number" in lite_prompt:
        # Count occurrences - should only be in examples/context, not as primary extraction
        count = lite_prompt.count("certificate_number")
        print(f"  ⚠️ Found {count} mention(s) of certificate_number in lite prompt")
        print(f"     (This is OK if only in examples/context, NOT as primary extraction)")
    else:
        print(f"  ✅ certificate_number removed from lite prompt")
    
    if "certificate_number" in full_prompt:
        count = full_prompt.count("certificate_number")
        print(f"  ⚠️ Found {count} mention(s) of certificate_number in full prompt")
        print(f"     (This is OK if only in examples/context, NOT as primary extraction)")
    else:
        print(f"  ✅ certificate_number removed from full prompt")
    
    # Test example response format
    print("\n4. Checking example response format...")
    
    example_checks = [
        ('"short_code": "GCN"', "GCN short_code in example"),
        ('"issue_date": "01/01/2012"', "issue_date example"),
        ('"issue_date_confidence": "full"', "issue_date_confidence example"),
        ('"issue_date": null', "null issue_date example (trang 1)"),
        ('"issue_date_confidence": "not_found"', "not_found confidence example")
    ]
    
    for keyword, description in example_checks:
        if keyword in lite_prompt or keyword in full_prompt:
            print(f"  ✅ Found: {description}")
        else:
            print(f"  ❌ Missing: {description}")
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    print("\nNOTE: This test only verifies that prompts contain the correct keywords.")
    print("Full testing requires real GCN images with handwritten dates.")
    print("\n📋 Next Steps:")
    print("  1. Test with real GCN trang 2 images (with handwritten dates)")
    print("  2. Verify JSON response includes issue_date and issue_date_confidence")
    print("  3. Test frontend pairing and date comparison logic")

if __name__ == "__main__":
    test_prompts()
