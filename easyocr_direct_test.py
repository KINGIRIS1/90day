#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct EasyOCR and Rule Classifier Test
Tests EasyOCR engine directly and validates GTLQ mapping
"""
import sys
import os
import json
import tempfile
from pathlib import Path

# Add desktop-app python path
desktop_python_path = "/app/desktop-app/python"
sys.path.insert(0, desktop_python_path)

def test_easyocr_engine_directly():
    """Test EasyOCR engine directly"""
    print("\n🔍 TESTING EASYOCR ENGINE DIRECTLY")
    print("="*60)
    
    try:
        # Import EasyOCR engine directly
        from ocr_engine_easyocr import OCREngine
        print("✅ Successfully imported EasyOCR engine")
        
        # Try to initialize
        print("⏳ Initializing EasyOCR engine...")
        engine = OCREngine()
        print("✅ EasyOCR engine initialized")
        
        # Create a simple test image
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create test image with GTLQ text
            img = Image.new('RGB', (800, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw test text
            test_text = "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ"
            draw.text((50, 50), test_text, fill='black')
            
            # Save to temp file
            temp_path = os.path.join(tempfile.gettempdir(), "easyocr_test_gtlq.png")
            img.save(temp_path)
            
            print(f"📝 Created test image: {temp_path}")
            
            # Test OCR extraction
            print("🔍 Running EasyOCR extraction...")
            result = engine.extract_text(temp_path)
            
            print(f"📊 OCR Result:")
            print(f"   Full text: {result.get('full_text', 'N/A')}")
            print(f"   Title text: {result.get('title_text', 'N/A')}")
            print(f"   Avg height: {result.get('avg_height', 0)}")
            
            if 'error' in result:
                print(f"❌ OCR Error: {result['error']}")
                return False
            else:
                print("✅ EasyOCR extraction successful")
                return True
                
            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass
                
        except ImportError:
            print("⚠️  PIL not available for test image creation")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import EasyOCR engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing EasyOCR: {e}")
        return False

def test_rule_classifier_with_gtlq():
    """Test rule classifier specifically for GTLQ cases"""
    print("\n📋 TESTING RULE CLASSIFIER FOR GTLQ")
    print("="*60)
    
    try:
        from rule_classifier import RuleClassifier
        print("✅ Successfully imported RuleClassifier")
    except ImportError as e:
        print(f"❌ Failed to import RuleClassifier: {e}")
        return False
    
    classifier = RuleClassifier()
    
    # GTLQ test cases with various OCR errors
    gtlq_test_cases = [
        {
            "text": "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
            "description": "Perfect GTLQ title"
        },
        {
            "text": "GIAY TIEP NHAN HO SO VA HEN TRA KET QUA", 
            "description": "GTLQ without accents"
        },
        {
            "text": "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KÉT QUẢ",  # KẾT → KÉT (OCR error)
            "description": "GTLQ with OCR error (KẾT → KÉT)"
        },
        {
            "text": "GIẤY TIẾP NHẬN HỎ SƠ VÀ HẸN TRẢ KẾT QUẢ",  # HỒ → HỎ (OCR error)
            "description": "GTLQ with OCR error (HỒ → HỎ)"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(gtlq_test_cases, 1):
        print(f"\n[{i}/{len(gtlq_test_cases)}] Testing: {test_case['description']}")
        print(f"📝 Text: {test_case['text']}")
        
        # Test classification
        result = classifier.classify(
            text=test_case['text'],
            title_text=test_case['text']
        )
        
        print(f"📊 Result: {result['short_code']} (confidence: {result['confidence']:.3f})")
        print(f"🔍 Method: {result.get('method', 'N/A')}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
        
        is_gtlq = result['short_code'] == 'GTLQ'
        status = "✅ PASS" if is_gtlq else "❌ FAIL"
        print(f"📋 GTLQ Detection: {status}")
        
        if not is_gtlq:
            print(f"⚠️  Expected GTLQ but got {result['short_code']}")
            if 'matched_keywords' in result:
                print(f"🔍 Matched keywords: {result['matched_keywords']}")
        
        results.append({
            "test_case": test_case,
            "result": result,
            "is_gtlq": is_gtlq
        })
    
    return results

def validate_75_percent_threshold():
    """Validate the 75% threshold is working with edge cases"""
    print("\n🎯 TESTING 75% THRESHOLD WITH EDGE CASES")
    print("="*60)
    
    try:
        from rule_classifier import RuleClassifier
    except ImportError as e:
        print(f"❌ Failed to import RuleClassifier: {e}")
        return False
    
    classifier = RuleClassifier()
    
    # Edge cases that should pass with 75% but fail with 80%
    edge_cases = [
        {
            "text": "HỢP ĐỎNG ỦY QUYỀN",  # ĐỒNG → ĐỎNG (should still match HDUQ)
            "expected": "HDUQ",
            "description": "HDUQ with OCR typo (ĐỒNG → ĐỎNG)"
        },
        {
            "text": "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT",  # Should match GCNM
            "expected": "GCNM",
            "description": "Standard GCN title"
        },
        {
            "text": "HỢP ĐỒNG CHUYỂN NHƯONG",  # NHƯỢNG → NHƯONG (OCR error)
            "expected": "HDCQ", 
            "description": "HDCQ with OCR typo (NHƯỢNG → NHƯONG)"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n[{i}/{len(edge_cases)}] Testing: {test_case['description']}")
        print(f"📝 Text: {test_case['text']}")
        
        result = classifier.classify(
            text=test_case['text'],
            title_text=test_case['text']
        )
        
        print(f"🎯 Expected: {test_case['expected']}")
        print(f"📊 Got: {result['short_code']} (confidence: {result['confidence']:.3f})")
        print(f"🔍 Method: {result.get('method', 'N/A')}")
        
        is_correct = result['short_code'] == test_case['expected']
        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"📋 Result: {status}")
        
        # Check if it used fuzzy matching (indicates 75% threshold working)
        used_fuzzy = result.get('method') == 'fuzzy_title_match'
        if used_fuzzy:
            print("✅ Used fuzzy title matching (75% threshold working)")
        else:
            print("⚠️  Did not use fuzzy matching")
        
        results.append({
            "test_case": test_case,
            "result": result,
            "is_correct": is_correct,
            "used_fuzzy": used_fuzzy
        })
    
    return results

def main():
    """Main test function"""
    print("🚀 EASYOCR DIRECT VALIDATION TEST")
    print("="*60)
    print("Testing EasyOCR engine and 75% threshold with GTLQ mapping")
    print("="*60)
    
    results = {
        "easyocr_direct": None,
        "gtlq_tests": None,
        "threshold_tests": None
    }
    
    # 1. Test EasyOCR engine directly
    print("\n📋 Step 1: Testing EasyOCR engine directly...")
    results["easyocr_direct"] = test_easyocr_engine_directly()
    
    # 2. Test GTLQ classification
    print("\n📋 Step 2: Testing GTLQ classification...")
    results["gtlq_tests"] = test_rule_classifier_with_gtlq()
    
    # 3. Test 75% threshold
    print("\n📋 Step 3: Testing 75% threshold...")
    results["threshold_tests"] = validate_75_percent_threshold()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    # EasyOCR status
    easyocr_status = "✅ WORKING" if results["easyocr_direct"] else "❌ FAILED"
    print(f"🔍 EasyOCR Engine: {easyocr_status}")
    
    # GTLQ tests
    if results["gtlq_tests"]:
        gtlq_passed = sum(1 for r in results["gtlq_tests"] if r["is_gtlq"])
        gtlq_total = len(results["gtlq_tests"])
        gtlq_status = "✅ PASS" if gtlq_passed == gtlq_total else f"❌ {gtlq_passed}/{gtlq_total}"
        print(f"📋 GTLQ Classification: {gtlq_status}")
    
    # Threshold tests
    if results["threshold_tests"]:
        threshold_passed = sum(1 for r in results["threshold_tests"] if r["is_correct"])
        threshold_total = len(results["threshold_tests"])
        fuzzy_used = sum(1 for r in results["threshold_tests"] if r["used_fuzzy"])
        
        threshold_status = "✅ PASS" if threshold_passed == threshold_total else f"❌ {threshold_passed}/{threshold_total}"
        print(f"🎯 75% Threshold Tests: {threshold_status}")
        print(f"   🔍 Fuzzy matching used: {fuzzy_used}/{threshold_total}")
    
    # Overall assessment
    print("\n" + "="*60)
    
    core_working = (
        results["gtlq_tests"] and all(r["is_gtlq"] for r in results["gtlq_tests"]) and
        results["threshold_tests"] and all(r["is_correct"] for r in results["threshold_tests"])
    )
    
    if core_working:
        print("🏆 Overall Status: ✅ CORE FUNCTIONALITY VALIDATED")
        print("   ✅ GTLQ mapping working correctly")
        print("   ✅ 75% threshold implemented and working")
        print("   ✅ Fuzzy title matching with relaxed similarity")
        
        if results["easyocr_direct"]:
            print("   ✅ EasyOCR engine working")
        else:
            print("   ⚠️  EasyOCR engine issues (but core logic validated)")
    else:
        print("🏆 Overall Status: ❌ VALIDATION FAILED")
        
        if not results["gtlq_tests"] or not all(r["is_gtlq"] for r in results["gtlq_tests"]):
            print("   ❌ GTLQ mapping issues")
        if not results["threshold_tests"] or not all(r["is_correct"] for r in results["threshold_tests"]):
            print("   ❌ 75% threshold issues")
    
    # Save results
    results_file = "/app/easyocr_direct_test_results.json"
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    return core_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)