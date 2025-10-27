#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for EasyOCR
Kiểm tra xem EasyOCR có hoạt động với Vietnamese không
"""
import sys
import time
import os

print("=" * 60)
print("🔍 EASYOCR TEST SCRIPT")
print("=" * 60)

# Step 1: Check if EasyOCR is installed
print("\n[1/5] Checking EasyOCR installation...")
try:
    import easyocr
    print(f"✅ EasyOCR installed: version {easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"❌ EasyOCR not installed: {e}")
    print("\n📦 To install EasyOCR, run:")
    print("   py -m pip install easyocr")
    print("\nNote: First installation will download Vietnamese model (~100MB)")
    sys.exit(1)

# Step 2: Check dependencies
print("\n[2/5] Checking dependencies...")
try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
except ImportError:
    print("⚠️ PyTorch not found (EasyOCR will install it)")

try:
    from PIL import Image
    print(f"✅ Pillow installed")
except ImportError:
    print("❌ Pillow not installed (required)")
    sys.exit(1)

# Step 3: Initialize EasyOCR Reader
print("\n[3/5] Initializing EasyOCR Reader for Vietnamese...")
print("⏳ This may take 1-2 minutes on first run (downloading model)...")

start_init = time.time()
try:
    # Initialize reader for Vietnamese
    # gpu=False to ensure compatibility (no CUDA required)
    reader = easyocr.Reader(['vi'], gpu=False, verbose=False)
    init_time = time.time() - start_init
    print(f"✅ Reader initialized successfully in {init_time:.2f}s")
except Exception as e:
    print(f"❌ Failed to initialize reader: {e}")
    sys.exit(1)

# Step 4: Test with image if provided
print("\n[4/5] Testing OCR...")
if len(sys.argv) > 1:
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"📄 Processing: {image_path}")
    
    start_ocr = time.time()
    try:
        # Run OCR
        result = reader.readtext(image_path)
        ocr_time = time.time() - start_ocr
        
        print(f"✅ OCR completed in {ocr_time:.2f}s")
        print(f"\n📊 Results ({len(result)} text regions found):")
        print("-" * 60)
        
        full_text = []
        for idx, detection in enumerate(result, 1):
            bbox, text, confidence = detection
            full_text.append(text)
            print(f"{idx}. Text: {text}")
            print(f"   Confidence: {confidence:.2%}")
            print()
        
        print("-" * 60)
        print("\n📝 FULL EXTRACTED TEXT:")
        print("-" * 60)
        print("\n".join(full_text))
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("⚠️ No image provided for testing")
    print("   Usage: python test_easyocr.py <image_path>")
    print("\n💡 You can test with:")
    print('   python test_easyocr.py "D:\\test\\sample.jpg"')

# Step 5: Performance summary
print("\n[5/5] Summary:")
print("=" * 60)
print(f"✅ EasyOCR is working correctly!")
print(f"📊 Initialization time: {init_time:.2f}s (cached after first run)")
if len(sys.argv) > 1:
    print(f"⚡ OCR processing time: {ocr_time:.2f}s")
    print(f"📝 Text regions detected: {len(result)}")
print("\n🎉 EasyOCR is ready for integration!")
print("=" * 60)
