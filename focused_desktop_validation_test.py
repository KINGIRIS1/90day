#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Focused Desktop OCR Validation Test
Tests the rule change 80%→75% and GTLQ mapping validation
"""
import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

# Add desktop-app python path
desktop_python_path = "/app/desktop-app/python"
sys.path.insert(0, desktop_python_path)

def test_rule_classifier_directly():
    """Test RuleClassifier directly without importing process_document"""
    print("\n🧪 TESTING RULE CLASSIFIER DIRECTLY")
    print("="*60)
    
    try:
        from rule_classifier import RuleClassifier
        print("✅ Successfully imported RuleClassifier")
    except ImportError as e:
        print(f"❌ Failed to import RuleClassifier: {e}")
        return False
    
    classifier = RuleClassifier()
    
    # Test cases for GTLQ and rule changes
    test_cases = [
        {
            "title": "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
            "expected_type": "GTLQ",
            "description": "Perfect GTLQ title - should trigger fuzzy match with 75% threshold"
        },
        {
            "title": "GIAY TIEP NHAN HO SO VA HEN TRA KET QUA",
            "expected_type": "GTLQ", 
            "description": "GTLQ without accents - should match with relaxed threshold"
        },
        {
            "title": "HỢP ĐỒNG ỦY QUYỀN",
            "expected_type": "HDUQ",
            "description": "HDUQ should be prioritized over HDCQ"
        },
        {
            "title": "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT",
            "expected_type": "HDCQ",
            "description": "HDCQ full title"
        },
        {
            "title": "HỢP ĐỎNG ỦY QUYỀN",  # OCR error: ĐỒNG → ĐỎNG
            "expected_type": "HDUQ",
            "description": "HDUQ with OCR typo - should still match with 75% threshold"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing: {test_case['description']}")
        print(f"📝 Title: {test_case['title']}")
        
        # Test with title_text parameter
        result = classifier.classify(
            text=test_case['title'],  # Use title as full text too
            title_text=test_case['title']
        )
        
        print(f"🎯 Expected: {test_case['expected_type']}")
        print(f"📊 Got: {result['short_code']} (confidence: {result['confidence']:.3f})")
        print(f"🔍 Method: {result.get('method', 'N/A')}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
        
        # Check if result matches expectation
        is_correct = result['short_code'] == test_case['expected_type']
        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"📋 Result: {status}")
        
        if not is_correct:
            print(f"⚠️  Expected {test_case['expected_type']} but got {result['short_code']}")
            if 'matched_keywords' in result:
                print(f"🔍 Matched keywords: {result['matched_keywords']}")
        
        results.append({
            "test_case": test_case,
            "result": result,
            "is_correct": is_correct
        })
    
    return results

def validate_rule_changes():
    """Validate that the 80%→75% rule change is implemented"""
    print("\n🔧 RULE CHANGE VALIDATION: 80% → 75%")
    print("="*60)
    
    # Check the rule_classifier.py source code for the threshold
    rule_classifier_path = "/app/desktop-app/python/rule_classifier.py"
    
    try:
        with open(rule_classifier_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for similarity threshold
        found_75_threshold = False
        
        if "similarity_threshold = 0.75" in content:
            print("✅ Found similarity_threshold = 0.75 (75% threshold)")
            found_75_threshold = True
        
        # Look for the specific line in fuzzy matching
        if "0.75" in content and ("similarity_threshold" in content or "RELAXED threshold" in content):
            print("✅ Found 0.75 threshold with relaxed threshold comment")
            found_75_threshold = True
        
        # Search for threshold patterns
        import re
        threshold_patterns = re.findall(r'.*threshold.*?0\.\d+.*', content, re.IGNORECASE)
        print(f"\n🔍 Found {len(threshold_patterns)} threshold patterns:")
        for i, pattern in enumerate(threshold_patterns[:5], 1):  # Show first 5
            print(f"   {i}. {pattern.strip()}")
        
        # Look for GTLQ specifically
        gtlq_count = content.count("GTLQ")
        print(f"\n📋 GTLQ references found: {gtlq_count}")
        
        if gtlq_count > 0:
            print("✅ GTLQ mapping is present in rule_classifier.py")
        else:
            print("❌ GTLQ mapping not found in rule_classifier.py")
            
        return found_75_threshold and gtlq_count > 0
            
    except Exception as e:
        print(f"❌ Error reading rule_classifier.py: {e}")
        return False

def test_easyocr_availability():
    """Test if EasyOCR is available and can be initialized"""
    print("\n🔍 EASYOCR AVAILABILITY TEST")
    print("="*60)
    
    try:
        # Try to run the process_document.py with a dummy path to see initialization
        cmd = [sys.executable, "/app/desktop-app/python/process_document.py", "/nonexistent/path.jpg", "easyocr"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/app/desktop-app/python",
            timeout=30  # 30 second timeout
        )
        
        stderr_output = result.stderr
        stdout_output = result.stdout
        
        print(f"📄 STDERR output:\n{stderr_output}")
        print(f"📄 STDOUT output:\n{stdout_output}")
        
        # Check for EasyOCR initialization messages
        if "EasyOCR engine loaded" in stderr_output:
            print("✅ EasyOCR successfully initialized")
            return True
        elif "EasyOCR not installed" in stderr_output:
            print("⚠️  EasyOCR not installed but fallback working")
            return False
        elif "EasyOCR initialization failed" in stderr_output:
            print("❌ EasyOCR installation found but initialization failed")
            return False
        else:
            print("❓ EasyOCR status unclear from output")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ EasyOCR initialization timed out (may be downloading models)")
        return False
    except Exception as e:
        print(f"❌ Error testing EasyOCR: {e}")
        return False

def test_process_document_with_tesseract():
    """Test process_document.py with Tesseract (should always work)"""
    print("\n🔧 TESSERACT FALLBACK TEST")
    print("="*60)
    
    # Create a simple test image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple white image with black text
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw test text
        test_text = "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ"
        draw.text((50, 50), test_text, fill='black', font=font)
        
        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), "test_gtlq.png")
        img.save(temp_path)
        
        print(f"📝 Created test image: {temp_path}")
        
        # Test with Tesseract
        cmd = [sys.executable, "/app/desktop-app/python/process_document.py", temp_path, "tesseract"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/app/desktop-app/python",
            timeout=30
        )
        
        print(f"📊 Return code: {result.returncode}")
        print(f"📄 STDERR:\n{result.stderr}")
        print(f"📄 STDOUT:\n{result.stdout}")
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                output_data = json.loads(result.stdout.strip())
                print(f"✅ Successfully processed with Tesseract")
                print(f"📋 Result: {output_data.get('short_code', 'N/A')} (confidence: {output_data.get('confidence', 0):.3f})")
                return output_data
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON output: {e}")
                return None
        else:
            print(f"❌ Process failed")
            return None
            
        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
            
    except ImportError:
        print("⚠️  PIL not available, skipping image creation test")
        return None
    except Exception as e:
        print(f"❌ Error in Tesseract test: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 FOCUSED DESKTOP OCR VALIDATION TEST")
    print("="*60)
    print("Testing rule change 80%→75% and GTLQ mapping")
    print("="*60)
    
    all_results = {
        "rule_validation": None,
        "classifier_tests": None,
        "easyocr_available": None,
        "tesseract_test": None
    }
    
    # 1. Validate rule changes
    print("\n📋 Step 1: Validating rule changes...")
    all_results["rule_validation"] = validate_rule_changes()
    
    # 2. Test RuleClassifier directly
    print("\n📋 Step 2: Testing RuleClassifier directly...")
    all_results["classifier_tests"] = test_rule_classifier_directly()
    
    # 3. Test EasyOCR availability
    print("\n📋 Step 3: Testing EasyOCR availability...")
    all_results["easyocr_available"] = test_easyocr_availability()
    
    # 4. Test with Tesseract fallback
    print("\n📋 Step 4: Testing Tesseract fallback...")
    all_results["tesseract_test"] = test_process_document_with_tesseract()
    
    # 5. Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    # Rule validation
    rule_status = "✅ PASS" if all_results["rule_validation"] else "❌ FAIL"
    print(f"🔧 Rule Change (80%→75%) & GTLQ: {rule_status}")
    
    # Classifier tests
    if all_results["classifier_tests"]:
        classifier_passed = sum(1 for r in all_results["classifier_tests"] if r["is_correct"])
        classifier_total = len(all_results["classifier_tests"])
        classifier_status = "✅ PASS" if classifier_passed == classifier_total else f"⚠️  {classifier_passed}/{classifier_total}"
        print(f"🧪 RuleClassifier Tests: {classifier_status}")
        
        # Show GTLQ specific results
        gtlq_tests = [r for r in all_results["classifier_tests"] if r["test_case"]["expected_type"] == "GTLQ"]
        if gtlq_tests:
            gtlq_passed = sum(1 for r in gtlq_tests if r["is_correct"])
            gtlq_status = "✅ PASS" if gtlq_passed == len(gtlq_tests) else f"❌ {gtlq_passed}/{len(gtlq_tests)}"
            print(f"   📋 GTLQ Tests: {gtlq_status}")
        
        # Show HDUQ vs HDCQ results
        hduq_tests = [r for r in all_results["classifier_tests"] if r["test_case"]["expected_type"] in ["HDUQ", "HDCQ"]]
        if hduq_tests:
            hduq_passed = sum(1 for r in hduq_tests if r["is_correct"])
            hduq_status = "✅ PASS" if hduq_passed == len(hduq_tests) else f"❌ {hduq_passed}/{len(hduq_tests)}"
            print(f"   🔄 HDUQ/HDCQ Tests: {hduq_status}")
    
    # EasyOCR availability
    easyocr_status = "✅ AVAILABLE" if all_results["easyocr_available"] else "❌ NOT AVAILABLE"
    print(f"🔍 EasyOCR Engine: {easyocr_status}")
    
    # Tesseract test
    tesseract_status = "✅ WORKING" if all_results["tesseract_test"] else "❌ FAILED"
    print(f"🔧 Tesseract Fallback: {tesseract_status}")
    
    # Overall status
    print("\n" + "="*60)
    
    # Core requirements check
    core_success = (
        all_results["rule_validation"] and
        all_results["classifier_tests"] and
        all(r["is_correct"] for r in all_results["classifier_tests"])
    )
    
    if core_success:
        print("🏆 Overall Status: ✅ CORE VALIDATION PASSED")
        print("   ✅ Rule change 80%→75% implemented")
        print("   ✅ GTLQ mapping working")
        print("   ✅ Fuzzy title matching with relaxed similarity")
        print("   ✅ HDUQ prioritized over HDCQ")
    else:
        print("🏆 Overall Status: ❌ CORE VALIDATION FAILED")
        if not all_results["rule_validation"]:
            print("   ❌ Rule change validation failed")
        if not all_results["classifier_tests"] or not all(r["is_correct"] for r in all_results["classifier_tests"]):
            print("   ❌ Classifier tests failed")
    
    # Additional notes
    if not all_results["easyocr_available"]:
        print("   ⚠️  EasyOCR not available (fallback to Tesseract)")
    
    # Save detailed results
    results_file = "/app/focused_desktop_validation_results.json"
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    return core_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)