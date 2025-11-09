#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test batch scanner with PDF merging
"""
import sys
import json
import os
import tempfile
from PIL import Image

print("🧪 Testing batch scanner with PDF merge...")

try:
    # Import batch_scanner
    print("📦 Importing batch_scanner...")
    from batch_scanner import merge_images_to_pdf
    print("✅ Import successful")
    
    # Create temp images
    print("\n🖼️  Creating test images...")
    temp_dir = tempfile.mkdtemp()
    img_paths = []
    
    for i in range(3):
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img_path = os.path.join(temp_dir, f'test_{i}.jpg')
        img.save(img_path)
        img_paths.append(img_path)
        print(f"   Created: {img_path}")
    
    # Test merge
    print("\n📚 Testing merge_images_to_pdf...")
    pdf_path = os.path.join(temp_dir, 'merged.pdf')
    success = merge_images_to_pdf(img_paths, pdf_path)
    
    if success:
        print(f"✅ Merge successful: {pdf_path}")
        print(f"   PDF size: {os.path.getsize(pdf_path)} bytes")
        
        # Verify PDF exists
        assert os.path.exists(pdf_path), "PDF file should exist"
        assert os.path.getsize(pdf_path) > 0, "PDF should not be empty"
        
        print("\n✅ All tests passed!")
    else:
        print("❌ Merge failed")
        sys.exit(1)
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
