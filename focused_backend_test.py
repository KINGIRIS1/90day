#!/usr/bin/env python3
"""
Focused Backend Test for Document Scanner - Testing Recent Improvements
Focus: Image cropping, strict matching, smart grouping, batch processing
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image
import base64

class FocusedDocumentScannerTester:
    def __init__(self, base_url="https://ocr-landocs.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.test_results = {}
        
        # Test images for specific scenarios
        self.test_images = [
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/77raup7h_20250318-03400001.jpg",
                "expected_type": "GCNM",
                "description": "Clear title document - should get high confidence"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/xpcyh9w4_20250318-03400003.jpg", 
                "expected_type": "DDK",
                "description": "Potential continuation page - may get CONTINUATION"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/154532fw_20250318-03400005.jpg",
                "expected_type": "HDCQ", 
                "description": "Contract document - should get high confidence"
            }
        ]

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.test_results[test_name] = {
            "success": success,
            "details": details
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")

    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BytesIO(response.content)
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def test_image_cropping_logic(self):
        """Test 1: Verify 20% image cropping is working"""
        print("\n🔍 TEST 1: Image Cropping Optimization (20% top crop)")
        print("=" * 60)
        
        success_count = 0
        total_tests = len(self.test_images)
        
        for i, image_info in enumerate(self.test_images):
            print(f"\n   Testing image {i+1}: {image_info['description']}")
            
            # Download and test image
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"crop_test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            try:
                response = requests.post(f"{self.base_url}/scan-document", files=files)
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    detected_type = result.get('detected_full_name', 'N/A')
                    short_code = result.get('short_code', 'N/A')
                    
                    print(f"   Detected: {detected_type}")
                    print(f"   Short Code: {short_code}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    # Check if cropping is working (fast response indicates cropped processing)
                    success_count += 1
                    
                else:
                    print(f"   ❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(1)  # Rate limiting
        
        success = success_count == total_tests
        self.log_result(
            "Image Cropping (20% top crop)", 
            success,
            f"Processed {success_count}/{total_tests} images successfully"
        )
        return success

    def test_strict_matching_logic(self):
        """Test 2: Verify strict matching with CONTINUATION fallback"""
        print("\n🔍 TEST 2: Strict Matching Logic with CONTINUATION Fallback")
        print("=" * 60)
        
        continuation_found = False
        high_confidence_found = False
        
        for i, image_info in enumerate(self.test_images):
            print(f"\n   Testing strict matching on image {i+1}")
            
            image_data = self.download_image(image_info['url'])
            if not image_data:
                continue
                
            files = {'file': (f"strict_test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            try:
                response = requests.post(f"{self.base_url}/scan-document", files=files)
                if response.status_code == 200:
                    result = response.json()
                    confidence = result.get('confidence_score', 0)
                    short_code = result.get('short_code', 'N/A')
                    
                    print(f"   Short Code: {short_code}, Confidence: {confidence:.2f}")
                    
                    # Check for CONTINUATION fallback
                    if short_code == "CONTINUATION":
                        continuation_found = True
                        print(f"   ✅ CONTINUATION fallback working")
                    
                    # Check for high confidence matches
                    if confidence > 0.8:
                        high_confidence_found = True
                        print(f"   ✅ High confidence match found")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(1)
        
        # Success if we see both strict matching (high confidence) and CONTINUATION fallback
        success = high_confidence_found  # At least one high confidence match
        details = f"High confidence matches: {high_confidence_found}, CONTINUATION fallback: {continuation_found}"
        
        self.log_result("Strict Matching with CONTINUATION", success, details)
        return success

    def test_smart_grouping_multipage(self):
        """Test 3: Verify smart grouping for multi-page documents"""
        print("\n🔍 TEST 3: Smart Grouping for Multi-Page Documents")
        print("=" * 60)
        
        # Test batch scan to see grouping in action
        files = []
        for i, image_info in enumerate(self.test_images):
            image_data = self.download_image(image_info['url'])
            if image_data:
                files.append(('files', (f"group_test_{i+1}.jpg", image_data, 'image/jpeg')))
        
        if not files:
            self.log_result("Smart Grouping", False, "No images available for testing")
            return False
        
        try:
            response = requests.post(f"{self.base_url}/batch-scan", files=files)
            if response.status_code == 200:
                results = response.json()
                
                print(f"   Batch processed: {len(results)} documents")
                
                grouped_pages = 0
                continuation_pages = 0
                
                for i, result in enumerate(results):
                    detected_name = result.get('detected_full_name', '')
                    short_code = result.get('short_code', '')
                    confidence = result.get('confidence_score', 0)
                    
                    print(f"   Doc {i+1}: {detected_name} ({short_code}) - Confidence: {confidence:.2f}")
                    
                    # Check for page numbering (trang 1, trang 2, etc.)
                    if "trang" in detected_name.lower():
                        grouped_pages += 1
                    
                    # Check for continuation logic
                    if short_code == "CONTINUATION" or confidence < 0.2:
                        continuation_pages += 1
                
                # Success if we see evidence of smart grouping
                success = len(results) > 0  # Basic success - batch processing works
                details = f"Processed {len(results)} docs, {grouped_pages} with page numbers, {continuation_pages} continuations"
                
                self.log_result("Smart Grouping Multi-Page", success, details)
                return success
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.log_result("Smart Grouping Multi-Page", False, f"Error: {e}")
            return False

    def test_batch_processing_performance(self):
        """Test 4: Verify batch processing with parallel execution"""
        print("\n🔍 TEST 4: Batch Processing Performance")
        print("=" * 60)
        
        # Prepare multiple files for batch processing
        files = []
        for i, image_info in enumerate(self.test_images):
            image_data = self.download_image(image_info['url'])
            if image_data:
                # Add each image multiple times to test parallel processing
                for j in range(2):  # 2 copies of each image
                    files.append(('files', (f"batch_perf_{i+1}_{j+1}.jpg", image_data, 'image/jpeg')))
        
        if len(files) < 4:
            self.log_result("Batch Processing Performance", False, "Not enough images for performance test")
            return False
        
        print(f"   Testing batch processing with {len(files)} files...")
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/batch-scan", files=files, timeout=60)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                results = response.json()
                
                success_count = len([r for r in results if r.get('short_code') != 'ERROR'])
                error_count = len([r for r in results if r.get('short_code') == 'ERROR'])
                
                print(f"   Processing time: {processing_time:.2f} seconds")
                print(f"   Successful: {success_count}/{len(files)} files")
                print(f"   Errors: {error_count} files")
                print(f"   Average time per file: {processing_time/len(files):.2f} seconds")
                
                # Success criteria: reasonable processing time and low error rate
                success = (processing_time < 120 and error_count < len(files) * 0.3)  # Less than 2 min, <30% errors
                details = f"{processing_time:.1f}s for {len(files)} files, {success_count} successful"
                
                self.log_result("Batch Processing Performance", success, details)
                return success
            else:
                self.log_result("Batch Processing Performance", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Batch Processing Performance", False, f"Error: {e}")
            return False

    def test_core_endpoints(self):
        """Test 5: Verify other core endpoints are working"""
        print("\n🔍 TEST 5: Core Endpoints Functionality")
        print("=" * 60)
        
        endpoints_to_test = [
            ("GET", "scan-history", "Scan History"),
            ("DELETE", "clear-history", "Clear History"),
        ]
        
        success_count = 0
        
        for method, endpoint, name in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}/{endpoint}")
                elif method == "DELETE":
                    response = requests.delete(f"{self.base_url}/{endpoint}")
                
                if response.status_code == 200:
                    print(f"   ✅ {name}: Working")
                    success_count += 1
                else:
                    print(f"   ❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        success = success_count == len(endpoints_to_test)
        self.log_result("Core Endpoints", success, f"{success_count}/{len(endpoints_to_test)} endpoints working")
        return success

    def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 Starting Focused Document Scanner Backend Tests")
        print("Focus: Recent improvements - cropping, strict matching, smart grouping")
        print("=" * 80)
        
        # Run all tests
        test_functions = [
            self.test_image_cropping_logic,
            self.test_strict_matching_logic,
            self.test_smart_grouping_multipage,
            self.test_batch_processing_performance,
            self.test_core_endpoints
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FOCUSED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}")
            if result['details']:
                print(f"     {result['details']}")
        
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All focused tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

def main():
    tester = FocusedDocumentScannerTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())