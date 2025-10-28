#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop OCR Validation Test
Tests the rule change 80%→75% and GTLQ mapping validation
"""
import sys
import os
import json
import subprocess
import tempfile
import requests
from pathlib import Path

# Add desktop-app python path
desktop_python_path = "/app/desktop-app/python"
sys.path.insert(0, desktop_python_path)

try:
    from rule_classifier import RuleClassifier
    from process_document import process_document
except ImportError as e:
    print(f"❌ Failed to import desktop modules: {e}")
    sys.exit(1)

def download_sample_image(url: str, filename: str) -> str:
    """Download sample image from URL"""
    try:
        print(f"📥 Downloading sample image: {filename}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {temp_path}")
        return temp_path
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return None

def test_process_document_with_easyocr(image_path: str) -> dict:
    """Test process_document.py with EasyOCR engine"""
    try:
        print(f"\n🔍 Testing process_document.py with EasyOCR on: {os.path.basename(image_path)}")
        
        # Run process_document.py with EasyOCR
        cmd = [sys.executable, "/app/desktop-app/python/process_document.py", image_path, "easyocr"]
        
        print(f"📝 Command: {' '.join(cmd)}")
        
        # Capture both stdout and stderr
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/app/desktop-app/python"
        )
        
        print(f"📊 Return code: {result.returncode}")
        print(f"📄 STDERR (logs):\n{result.stderr}")
        print(f"📄 STDOUT (result):\n{result.stdout}")
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                output_data = json.loads(result.stdout.strip())
                return output_data
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON output: {e}")
                return {"error": "Invalid JSON output", "raw_output": result.stdout}
        else:
            return {
                "error": f"Process failed with code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }
            
    except Exception as e:
        print(f"❌ Error running process_document.py: {e}")
        return {"error": str(e)}

def test_synthetic_titles():
    """Test RuleClassifier.classify on synthetic titles"""
    print("\n" + "="*60)
    print("🧪 SYNTHETIC TITLE TESTS")
    print("="*60)
    
    classifier = RuleClassifier()
    
    # Test cases for GTLQ
    test_cases = [
        {
            "title": "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
            "expected_type": "GTLQ",
            "description": "Perfect GTLQ title"
        },
        {
            "title": "GIAY TIEP NHAN HO SO VA HEN TRA KET QUA",
            "expected_type": "GTLQ", 
            "description": "GTLQ without accents"
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
        print(f"📊 Got: {result['short_code']} (confidence: {result['confidence']:.2f})")
        print(f"🔍 Method: {result.get('method', 'N/A')}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
        
        # Check if result matches expectation
        is_correct = result['short_code'] == test_case['expected_type']
        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"📋 Result: {status}")
        
        results.append({
            "test_case": test_case,
            "result": result,
            "is_correct": is_correct
        })
    
    return results

def test_regression_hduq_vs_hdcq():
    """Regression test for HỢP ĐỒNG ỦY QUYỀN vs HDCQ prioritization"""
    print("\n" + "="*60)
    print("🔄 REGRESSION TEST: HDUQ vs HDCQ")
    print("="*60)
    
    classifier = RuleClassifier()
    
    test_cases = [
        {
            "title": "HỢP ĐỒNG ỦY QUYỀN",
            "expected": "HDUQ",
            "description": "Pure HDUQ title"
        },
        {
            "title": "HỢP ĐỒNG UỶ QUYỀN", 
            "expected": "HDUQ",
            "description": "HDUQ with OCR typo (UỶ)"
        },
        {
            "title": "HỢP ĐỒNG CHUYỂN NHƯỢNG",
            "expected": "HDCQ", 
            "description": "Pure HDCQ title"
        },
        {
            "title": "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT",
            "expected": "HDCQ",
            "description": "Full HDCQ title"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test_case['description']}")
        print(f"📝 Title: {test_case['title']}")
        
        result = classifier.classify(
            text=test_case['title'],
            title_text=test_case['title']
        )
        
        print(f"🎯 Expected: {test_case['expected']}")
        print(f"📊 Got: {result['short_code']} (confidence: {result['confidence']:.2f})")
        
        is_correct = result['short_code'] == test_case['expected']
        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"📋 Result: {status}")
        
        if not is_correct:
            print(f"⚠️  Expected {test_case['expected']} but got {result['short_code']}")
            print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
        
        results.append({
            "test_case": test_case,
            "result": result,
            "is_correct": is_correct
        })
    
    return results

def validate_rule_changes():
    """Validate that the 80%→75% rule change is implemented"""
    print("\n" + "="*60)
    print("🔧 RULE CHANGE VALIDATION: 80% → 75%")
    print("="*60)
    
    # Check the rule_classifier.py source code for the threshold
    rule_classifier_path = "/app/desktop-app/python/rule_classifier.py"
    
    try:
        with open(rule_classifier_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for similarity threshold
        if "similarity_threshold = 0.75" in content:
            print("✅ Found similarity_threshold = 0.75 (75% threshold)")
            return True
        elif "0.75" in content and "threshold" in content.lower():
            print("✅ Found 0.75 threshold in code")
            return True
        else:
            print("❌ Could not find 75% threshold in rule_classifier.py")
            print("🔍 Searching for threshold patterns...")
            
            # Search for threshold patterns
            import re
            threshold_patterns = re.findall(r'threshold.*?=.*?0\.\d+', content, re.IGNORECASE)
            for pattern in threshold_patterns:
                print(f"   Found: {pattern}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error reading rule_classifier.py: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 DESKTOP OCR VALIDATION TEST")
    print("="*60)
    print("Testing rule change 80%→75% and GTLQ mapping")
    print("="*60)
    
    # Sample image URLs (public URLs for testing)
    sample_images = [
        {
            "url": "https://via.placeholder.com/800x600/ffffff/000000?text=GIAY+TIEP+NHAN+HO+SO+VA+HEN+TRA+KET+QUA",
            "filename": "gtlq_sample.png",
            "description": "GTLQ sample image"
        }
    ]
    
    all_results = {
        "rule_validation": None,
        "synthetic_tests": None,
        "regression_tests": None,
        "easyocr_tests": []
    }
    
    # 1. Validate rule changes
    print("\n📋 Step 1: Validating rule changes...")
    all_results["rule_validation"] = validate_rule_changes()
    
    # 2. Test synthetic titles
    print("\n📋 Step 2: Testing synthetic titles...")
    all_results["synthetic_tests"] = test_synthetic_titles()
    
    # 3. Regression tests
    print("\n📋 Step 3: Running regression tests...")
    all_results["regression_tests"] = test_regression_hduq_vs_hdcq()
    
    # 4. Test with EasyOCR (if available)
    print("\n📋 Step 4: Testing EasyOCR integration...")
    
    # Try to test with sample images
    for sample in sample_images:
        print(f"\n🖼️  Testing with {sample['description']}")
        
        # Try to download sample image
        image_path = download_sample_image(sample["url"], sample["filename"])
        
        if image_path and os.path.exists(image_path):
            # Test with EasyOCR
            easyocr_result = test_process_document_with_easyocr(image_path)
            all_results["easyocr_tests"].append({
                "image": sample["description"],
                "result": easyocr_result
            })
            
            # Clean up
            try:
                os.remove(image_path)
            except:
                pass
        else:
            print(f"⚠️  Skipping EasyOCR test - could not download sample image")
            all_results["easyocr_tests"].append({
                "image": sample["description"],
                "result": {"error": "Could not download sample image"}
            })
    
    # 5. Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    # Rule validation
    rule_status = "✅ PASS" if all_results["rule_validation"] else "❌ FAIL"
    print(f"🔧 Rule Change (80%→75%): {rule_status}")
    
    # Synthetic tests
    if all_results["synthetic_tests"]:
        synthetic_passed = sum(1 for r in all_results["synthetic_tests"] if r["is_correct"])
        synthetic_total = len(all_results["synthetic_tests"])
        synthetic_status = "✅ PASS" if synthetic_passed == synthetic_total else f"⚠️  {synthetic_passed}/{synthetic_total}"
        print(f"🧪 Synthetic Tests: {synthetic_status}")
        
        # Show GTLQ specific results
        gtlq_tests = [r for r in all_results["synthetic_tests"] if r["test_case"]["expected_type"] == "GTLQ"]
        if gtlq_tests:
            gtlq_passed = sum(1 for r in gtlq_tests if r["is_correct"])
            print(f"   📋 GTLQ Tests: {gtlq_passed}/{len(gtlq_tests)} passed")
    
    # Regression tests
    if all_results["regression_tests"]:
        regression_passed = sum(1 for r in all_results["regression_tests"] if r["is_correct"])
        regression_total = len(all_results["regression_tests"])
        regression_status = "✅ PASS" if regression_passed == regression_total else f"⚠️  {regression_passed}/{regression_total}"
        print(f"🔄 Regression Tests: {regression_status}")
    
    # EasyOCR tests
    easyocr_success = sum(1 for r in all_results["easyocr_tests"] if "success" in r["result"] and r["result"]["success"])
    easyocr_total = len(all_results["easyocr_tests"])
    if easyocr_total > 0:
        easyocr_status = "✅ PASS" if easyocr_success > 0 else "❌ FAIL"
        print(f"🔍 EasyOCR Tests: {easyocr_status} ({easyocr_success}/{easyocr_total} successful)")
    else:
        print(f"🔍 EasyOCR Tests: ⚠️  SKIPPED (no sample images)")
    
    # Overall status
    print("\n" + "="*60)
    overall_success = (
        all_results["rule_validation"] and
        (not all_results["synthetic_tests"] or all(r["is_correct"] for r in all_results["synthetic_tests"])) and
        (not all_results["regression_tests"] or all(r["is_correct"] for r in all_results["regression_tests"]))
    )
    
    overall_status = "✅ ALL TESTS PASSED" if overall_success else "❌ SOME TESTS FAILED"
    print(f"🏆 Overall Status: {overall_status}")
    
    # Save detailed results
    results_file = "/app/desktop_ocr_validation_results.json"
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)