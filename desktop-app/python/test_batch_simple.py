#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for batch_scanner.py
"""
import sys
import json

print("🧪 Test starting...")

try:
    # Test 1: Can we import?
    print("📦 Importing batch_scanner...")
    from batch_scanner import read_txt_file, validate_folder
    print("✅ Import successful")
    
    # Test 2: Test read_txt_file with sample
    print("📄 Testing read_txt_file...")
    test_txt = "/app/desktop-app/test_folders.txt"
    folders = read_txt_file(test_txt)
    print(f"✅ Read {len(folders)} folders")
    for f in folders:
        print(f"  - {f}")
    
    # Test 3: Validate a folder (will fail but should not crash)
    print("📁 Testing validate_folder...")
    result = validate_folder("/nonexistent/path")
    print(f"✅ Validation result: {result}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
