#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full test for batch_scanner.py
"""
import sys
import json
import os
import tempfile

print("🧪 Full batch scanner test...")

try:
    # Import batch_scanner
    print("📦 Importing batch_scanner...")
    from batch_scanner import process_batch_scan
    print("✅ Import successful")
    
    # Create a temp TXT file with test folders
    print("\n📄 Creating test TXT file...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("# Test folders\n")
        f.write("/nonexistent/folder1\n")
        f.write("/nonexistent/folder2\n")
        txt_path = f.name
    print(f"✅ Created: {txt_path}")
    
    # Run batch scan (should skip all folders)
    print("\n🚀 Running batch scan...")
    result = process_batch_scan(
        txt_path=txt_path,
        ocr_engine='tesseract',
        api_key=None,
        output_option='rename_in_place',
        output_folder=None
    )
    
    print("\n📊 Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Verify result
    assert result['success'] == True, "Should return success=True"
    assert result['total_folders'] == 2, "Should have 2 folders"
    assert result['skipped_folders_count'] == 2, "Should skip 2 folders"
    assert result['processed_files'] == 0, "Should process 0 files"
    
    # Clean up
    os.unlink(txt_path)
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
