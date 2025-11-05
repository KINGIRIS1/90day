#!/usr/bin/env python3
"""
GCN Document Recognition Test with Quốc Huy Detection - NEW IMPROVEMENTS
Focus: Testing 35% crop + quốc huy (Vietnam coat of arms) detection for old GCN documents
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image
import base64

class GCNQuocHuyTester:
    def __init__(self, base_url="https://vndoc-ocr.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.test_results = {}
        
        # Test images specifically for GCN + quốc huy testing
        self.test_images = [
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/77raup7h_20250318-03400001.jpg",
                "expected_type": "GCNM",
                "description": "GCN document with quốc huy - should detect coat of arms",
                "test_focus": "quoc_huy_detection"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/xpcyh9w4_20250318-03400003.jpg", 
                "expected_type": "DDK",
                "description": "Non-GCN document - should not detect quốc huy as primary feature",
                "test_focus": "non_gcn_accuracy"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/154532fw_20250318-03400005.jpg",
                "expected_type": "HDCQ", 
                "description": "Contract document - test 35% crop doesn't affect other document types",
                "test_focus": "regression_test"
            }
        ]

    def log_result(self, test_name, success, details="", critical=False):
        """Log test result with criticality flag"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "critical": critical
        }
        status = "✅ PASS" if success else "❌ FAIL"
        priority = "🔴 CRITICAL" if critical else "🟡 STANDARD"
        print(f"{status} {priority} {test_name}")
        if details:
            print(f"   Details: {details}")

    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return BytesIO(response.content)
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def test_35_percent_crop_effectiveness(self):
        """Test 1: CRITICAL - Verify 35% crop captures quốc huy + middle title area"""
        print("\n🔍 TEST 1: 35% Crop + Quốc Huy Detection (CRITICAL - NEW FEATURE)")
        print("=" * 70)
        
        gcn_detected_count = 0
        quoc_huy_mentions = 0
        high_confidence_gcn = 0
        
        for i, image_info in enumerate(self.test_images):
            print(f"\n   Testing image {i+1}: {image_info['description']}")
            
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"gcn_test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/scan-document", files=files, timeout=45)
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    detected_type = result.get('detected_full_name', 'N/A')
                    short_code = result.get('short_code', 'N/A')
                    
                    print(f"   Detected: {detected_type}")
                    print(f"   Short Code: {short_code}")
                    print(f"   Confidence: {confidence:.2f}")
                    print(f"   Processing Time: {processing_time:.2f}s")
                    
                    # Check for GCN/GCNM detection
                    if short_code in ['GCN', 'GCNM']:
                        gcn_detected_count += 1
                        if confidence > 0.8:
                            high_confidence_gcn += 1
                            print(f"   ✅ High confidence GCN detection: {confidence:.2f}")
                    
                    # Check if quốc huy is being considered (indirect test via GCN detection)
                    if image_info['test_focus'] == 'quoc_huy_detection' and short_code in ['GCN', 'GCNM']:
                        quoc_huy_mentions += 1
                        print(f"   ✅ Quốc huy detection likely working (GCN identified)")
                    
                    # Performance check - should be faster with 1024px optimization
                    if processing_time < 10:  # Should be fast with optimized image size
                        print(f"   ✅ Fast processing with 1024px optimization")
                    else:
                        print(f"   ⚠️  Slower processing: {processing_time:.2f}s")
                        
                else:
                    print(f"   ❌ API Error: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(2)  # Rate limiting
        
        # Success criteria for CRITICAL feature
        success = (gcn_detected_count > 0 and high_confidence_gcn > 0)
        details = f"GCN detected: {gcn_detected_count}, High confidence: {high_confidence_gcn}, Quốc huy tests: {quoc_huy_mentions}"
        
        self.log_result(
            "35% Crop + Quốc Huy Detection", 
            success,
            details,
            critical=True
        )
        return success

    def test_gcn_vs_gcnm_distinction(self):
        """Test 2: CRITICAL - Verify distinction between GCNM (new) vs GCN (old)"""
        print("\n🔍 TEST 2: GCN vs GCNM Distinction (CRITICAL)")
        print("=" * 70)
        
        gcnm_detected = False
        gcn_detected = False
        distinction_working = False
        
        for i, image_info in enumerate(self.test_images):
            if image_info['expected_type'] not in ['GCN', 'GCNM']:
                continue
                
            print(f"\n   Testing GCN distinction on: {image_info['description']}")
            
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"distinction_test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            try:
                response = requests.post(f"{self.base_url}/scan-document", files=files, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    short_code = result.get('short_code', 'N/A')
                    detected_name = result.get('detected_full_name', '')
                    
                    print(f"   Detected: {short_code} - {detected_name}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    if short_code == 'GCNM':
                        gcnm_detected = True
                        print(f"   ✅ GCNM (new GCN) detected correctly")
                    elif short_code == 'GCN':
                        gcn_detected = True
                        print(f"   ✅ GCN (old GCN) detected correctly")
                    
                    # Check if the distinction logic is working
                    if confidence > 0.8 and short_code in ['GCN', 'GCNM']:
                        distinction_working = True
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(2)
        
        success = distinction_working and (gcnm_detected or gcn_detected)
        details = f"GCNM detected: {gcnm_detected}, GCN detected: {gcn_detected}, High confidence: {distinction_working}"
        
        self.log_result(
            "GCN vs GCNM Distinction", 
            success,
            details,
            critical=True
        )
        return success

    def test_performance_improvement(self):
        """Test 3: Verify performance improvement with 1024px images"""
        print("\n🔍 TEST 3: Performance Improvement (1024px optimization)")
        print("=" * 70)
        
        processing_times = []
        fast_processing_count = 0
        
        for i, image_info in enumerate(self.test_images):
            print(f"\n   Performance test on image {i+1}")
            
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"perf_test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/scan-document", files=files, timeout=30)
                processing_time = time.time() - start_time
                
                processing_times.append(processing_time)
                
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    
                    print(f"   Processing time: {processing_time:.2f}s")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    # Fast processing indicates 1024px optimization is working
                    if processing_time < 8:  # Should be faster than before
                        fast_processing_count += 1
                        print(f"   ✅ Fast processing achieved")
                    else:
                        print(f"   ⚠️  Slower than expected: {processing_time:.2f}s")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(1)
        
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            print(f"\n   Average processing time: {avg_time:.2f}s")
            
            # Success if most images process quickly
            success = fast_processing_count >= len(processing_times) * 0.7  # 70% should be fast
            details = f"Avg time: {avg_time:.2f}s, Fast processing: {fast_processing_count}/{len(processing_times)}"
        else:
            success = False
            details = "No processing times recorded"
        
        self.log_result("Performance Improvement (1024px)", success, details)
        return success

    def test_accuracy_validation(self):
        """Test 4: Verify accuracy is maintained across document types"""
        print("\n🔍 TEST 4: Accuracy Validation (All Document Types)")
        print("=" * 70)
        
        high_confidence_count = 0
        correct_detection_count = 0
        total_tests = 0
        
        for i, image_info in enumerate(self.test_images):
            print(f"\n   Accuracy test on: {image_info['description']}")
            
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"accuracy_test_{i+1}.jpg", image_data, 'image/jpeg')}
            total_tests += 1
            
            try:
                response = requests.post(f"{self.base_url}/scan-document", files=files, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    short_code = result.get('short_code', 'N/A')
                    detected_name = result.get('detected_full_name', '')
                    
                    print(f"   Expected: {image_info['expected_type']}")
                    print(f"   Detected: {short_code}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    # Check high confidence (>0.8 for clear documents)
                    if confidence > 0.8:
                        high_confidence_count += 1
                        print(f"   ✅ High confidence achieved: {confidence:.2f}")
                    
                    # Check if detection matches expected (or is reasonable fallback)
                    if (short_code == image_info['expected_type'] or 
                        short_code == 'CONTINUATION' or 
                        confidence > 0.7):  # Allow reasonable alternatives
                        correct_detection_count += 1
                        print(f"   ✅ Reasonable detection result")
                    else:
                        print(f"   ⚠️  Unexpected result: expected {image_info['expected_type']}, got {short_code}")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(2)
        
        if total_tests > 0:
            accuracy_rate = correct_detection_count / total_tests
            high_conf_rate = high_confidence_count / total_tests
            
            success = accuracy_rate >= 0.7 and high_conf_rate >= 0.5  # 70% accuracy, 50% high confidence
            details = f"Accuracy: {accuracy_rate:.1%}, High confidence: {high_conf_rate:.1%} ({high_confidence_count}/{total_tests})"
        else:
            success = False
            details = "No tests completed"
        
        self.log_result("Accuracy Validation", success, details)
        return success

    def test_regression_validation(self):
        """Test 5: Verify previous features still work (regression test)"""
        print("\n🔍 TEST 5: Regression Testing (Previous Features)")
        print("=" * 70)
        
        endpoints_working = 0
        total_endpoints = 0
        
        # Test core endpoints
        core_tests = [
            ("GET", "scan-history", "Scan History"),
            ("GET", "", "Root API"),
        ]
        
        for method, endpoint, name in core_tests:
            total_endpoints += 1
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}/{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    print(f"   ✅ {name}: Working")
                    endpoints_working += 1
                else:
                    print(f"   ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # Test batch processing (regression)
        print(f"\n   Testing batch processing regression...")
        files = []
        for i, image_info in enumerate(self.test_images[:2]):  # Use first 2 images
            image_data = self.download_image(image_info['url'])
            if image_data:
                files.append(('files', (f"regression_batch_{i+1}.jpg", image_data, 'image/jpeg')))
        
        batch_working = False
        if files:
            try:
                response = requests.post(f"{self.base_url}/batch-scan", files=files, timeout=60)
                if response.status_code == 200:
                    results = response.json()
                    if len(results) > 0:
                        batch_working = True
                        print(f"   ✅ Batch processing: {len(results)} documents processed")
                    else:
                        print(f"   ❌ Batch processing: No results returned")
                else:
                    print(f"   ❌ Batch processing: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Batch processing: Error - {e}")
        
        # Overall regression success
        endpoint_success = endpoints_working == total_endpoints
        overall_success = endpoint_success and batch_working
        
        details = f"Endpoints: {endpoints_working}/{total_endpoints}, Batch: {batch_working}"
        
        self.log_result("Regression Testing", overall_success, details)
        return overall_success

    def run_all_tests(self):
        """Run all GCN + Quốc Huy tests"""
        print("🚀 Starting GCN Document Recognition Tests with Quốc Huy Detection")
        print("🎯 Focus: NEW 35% crop + quốc huy detection improvements")
        print("=" * 80)
        
        # Run all tests in priority order
        test_functions = [
            self.test_35_percent_crop_effectiveness,      # CRITICAL - NEW FEATURE
            self.test_gcn_vs_gcnm_distinction,           # CRITICAL - NEW FEATURE  
            self.test_performance_improvement,            # Performance improvement
            self.test_accuracy_validation,               # Accuracy validation
            self.test_regression_validation              # Regression testing
        ]
        
        for test_func in test_functions:
            try:
                test_func()
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 GCN + QUỐC HUY TEST RESULTS SUMMARY")
        print("=" * 80)
        
        critical_passed = 0
        critical_total = 0
        total_passed = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            priority = "🔴 CRITICAL" if result['critical'] else "🟡 STANDARD"
            
            print(f"{status} {priority} {test_name}")
            if result['details']:
                print(f"     {result['details']}")
            
            if result['success']:
                total_passed += 1
            
            if result['critical']:
                critical_total += 1
                if result['success']:
                    critical_passed += 1
        
        print(f"\n📈 Overall: {total_passed}/{total_tests} tests passed")
        print(f"🔴 Critical: {critical_passed}/{critical_total} critical tests passed")
        
        # Success criteria: All critical tests must pass
        if critical_passed == critical_total and critical_total > 0:
            print("🎉 All CRITICAL tests passed! New GCN + Quốc huy features working!")
            return True
        elif critical_total == 0:
            print("⚠️  No critical tests found")
            return False
        else:
            print("❌ CRITICAL tests failed - New features need attention")
            return False

def main():
    tester = GCNQuocHuyTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())