#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for v1.1.0 improvements
- Smart crop detection
- Enhanced title extraction
- Improved classification
"""
import sys
import os
import time
from pathlib import Path

# Add python folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def test_improvements(image_path):
    """Test all improvements on a single image"""
    
    print("=" * 80)
    print("🧪 TESTING v1.1.0 IMPROVEMENTS")
    print("=" * 80)
    print(f"📁 Image: {image_path}")
    print()
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found: {image_path}")
        return
    
    # Import after path setup
    try:
        from process_document import process_document
        from PIL import Image
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install pillow easyocr opencv-python")
        return
    
    # Step 1: Analyze image format
    print("─" * 80)
    print("STEP 1: SMART CROP ANALYSIS")
    print("─" * 80)
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        aspect_ratio = width / height
        
        print(f"📐 Image size: {width}x{height}")
        print(f"📊 Aspect ratio: {aspect_ratio:.2f}")
        
        if aspect_ratio > 1.35:
            crop_type = "2-page/wide format"
            crop_percent = "65%"
            print(f"✅ Detected: {crop_type} → Using {crop_percent} crop")
        else:
            crop_type = "Single page portrait"
            crop_percent = "50%"
            print(f"✅ Detected: {crop_type} → Using {crop_percent} crop")
        
        print()
    except Exception as e:
        print(f"⚠️ Could not analyze image: {e}")
        print()
    
    # Step 2: Process with improvements
    print("─" * 80)
    print("STEP 2: OCR + CLASSIFICATION (with timeout tracking)")
    print("─" * 80)
    
    start_time = time.time()
    
    try:
        # Test with EasyOCR (the one with improvements)
        print("🔍 Running with EasyOCR engine (improved)...")
        result = process_document(image_path, 'easyocr')
        
        elapsed = time.time() - start_time
        print(f"⏱️  Processing time: {elapsed:.2f}s (timeout: 60s)")
        
        if elapsed > 60:
            print("❌ TIMEOUT! (>60s)")
        elif elapsed > 30:
            print("⚠️  SLOW but within 60s timeout")
        else:
            print("✅ FAST (< 30s)")
        
        print()
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Results analysis
    print("─" * 80)
    print("STEP 3: RESULTS ANALYSIS")
    print("─" * 80)
    
    if not result.get('success'):
        print(f"❌ Processing failed: {result.get('error')}")
        return
    
    # Classification results
    print(f"📄 Document Type: {result.get('doc_type', 'N/A')}")
    print(f"🏷️  Short Code: {result.get('short_code', 'N/A')}")
    print(f"📊 Confidence: {result.get('confidence', 0):.1%}")
    print(f"🎯 Accuracy Estimate: {result.get('accuracy_estimate', 'N/A')}")
    print(f"🔧 OCR Engine: {result.get('ocr_engine', 'N/A')}")
    print()
    
    # Title extraction
    print("─" * 80)
    print("STEP 4: TITLE EXTRACTION")
    print("─" * 80)
    
    title_text = result.get('title_text', '')
    title_via_pattern = result.get('title_extracted_via_pattern', False)
    
    if title_text:
        print(f"✅ Title extracted: {title_text[:100]}...")
        print(f"📌 Extraction method: {'Regex Pattern' if title_via_pattern else 'OCR Title Area'}")
    else:
        print("⚠️  No title extracted")
    
    print()
    
    # Full text preview
    print("─" * 80)
    print("STEP 5: FULL TEXT PREVIEW")
    print("─" * 80)
    
    full_text = result.get('original_text', '')
    if full_text:
        print(f"📝 Text length: {len(full_text)} characters")
        print(f"📄 First 300 chars:\n{full_text[:300]}...")
    else:
        print("⚠️  No text extracted")
    
    print()
    
    # Recommendations
    print("─" * 80)
    print("STEP 6: RECOMMENDATIONS")
    print("─" * 80)
    
    confidence = result.get('confidence', 0)
    
    if confidence >= 0.8:
        print("✅ HIGH CONFIDENCE - Classification looks good!")
    elif confidence >= 0.6:
        print("⚠️  MEDIUM CONFIDENCE - May need review")
    else:
        print("❌ LOW CONFIDENCE - Consider using Cloud Boost")
    
    if result.get('recommend_cloud_boost'):
        print("💡 Recommendation: Try Cloud Boost for better accuracy")
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test-improvements.py <image_path>")
        print()
        print("Example:")
        print('  python test-improvements.py "C:\\path\\to\\image.jpg"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_improvements(image_path)
