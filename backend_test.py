import requests
import sys
import json
import time
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64

class DocumentScannerAPITester:
    def __init__(self, base_url="https://smartdocscan-4.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.scan_results = []
        
        # Sample image URLs provided by user
        self.sample_images = [
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/77raup7h_20250318-03400001.jpg",
                "expected_type": "GCNM",
                "description": "Giấy chứng nhận quyền sử dụng đất"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/xpcyh9w4_20250318-03400003.jpg", 
                "expected_type": "DDK",
                "description": "Đơn đăng ký biến động đất đai"
            },
            {
                "url": "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/154532fw_20250318-03400005.jpg",
                "expected_type": "HDCQ", 
                "description": "Hợp đồng chuyển nhượng"
            }
        ]

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, response_type='json'):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        if files is None and data is not None:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                if response_type == 'json' and response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                else:
                    return success, response.content
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def download_image_as_file(self, image_url, filename):
        """Download image from URL and return as file-like object"""
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                return BytesIO(response.content)
            else:
                print(f"Failed to download image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET", 
            "",
            200
        )
        return success

    def test_single_scan(self):
        """Test single document scan"""
        print("\n📄 Testing Single Document Scan...")
        
        for i, image_info in enumerate(self.sample_images):
            print(f"\n   Testing image {i+1}: {image_info['description']}")
            
            # Download image
            image_data = self.download_image_as_file(image_info['url'], f"test_{i+1}.jpg")
            if not image_data:
                print(f"❌ Failed to download image {i+1}")
                continue
            
            # Prepare file for upload
            files = {'file': (f"test_{i+1}.jpg", image_data, 'image/jpeg')}
            
            success, response = self.run_test(
                f"Single Scan - Image {i+1}",
                "POST",
                "scan-document",
                200,
                files=files
            )
            
            if success and response:
                print(f"   Detected: {response.get('detected_full_name', 'N/A')}")
                print(f"   Short Code: {response.get('short_code', 'N/A')}")
                print(f"   Confidence: {response.get('confidence_score', 0):.2f}")
                
                # Check if confidence is reasonable
                confidence = response.get('confidence_score', 0)
                if confidence > 0.7:
                    print(f"   ✅ Good confidence score: {confidence:.2f}")
                else:
                    print(f"   ⚠️  Low confidence score: {confidence:.2f}")
                
                self.scan_results.append(response)
            
            # Wait between API calls to avoid rate limiting
            time.sleep(2)
        
        return len(self.scan_results) > 0

    def test_batch_scan(self):
        """Test batch document scan"""
        print("\n📄 Testing Batch Document Scan...")
        
        files = []
        for i, image_info in enumerate(self.sample_images):
            image_data = self.download_image_as_file(image_info['url'], f"batch_{i+1}.jpg")
            if image_data:
                files.append(('files', (f"batch_{i+1}.jpg", image_data, 'image/jpeg')))
        
        if not files:
            print("❌ No images available for batch scan")
            return False
        
        success, response = self.run_test(
            "Batch Scan - All Images",
            "POST",
            "batch-scan", 
            200,
            files=files
        )
        
        if success and response:
            print(f"   Batch processed: {len(response)} documents")
            for i, result in enumerate(response):
                print(f"   Document {i+1}: {result.get('short_code', 'N/A')} (confidence: {result.get('confidence_score', 0):.2f})")
            
            # Store results for later tests
            self.scan_results.extend(response)
        
        return success

    def test_scan_history(self):
        """Test getting scan history"""
        success, response = self.run_test(
            "Get Scan History",
            "GET",
            "scan-history",
            200
        )
        
        if success and response:
            print(f"   History contains: {len(response)} documents")
        
        return success

    def test_update_filename(self):
        """Test updating filename"""
        if not self.scan_results:
            print("❌ No scan results available for filename update test")
            return False
        
        # Use first scan result
        scan_result = self.scan_results[0]
        original_code = scan_result.get('short_code', 'TEST')
        new_code = f"{original_code}_UPDATED"
        
        success, response = self.run_test(
            "Update Filename",
            "PUT",
            "update-filename",
            200,
            data={
                "id": scan_result.get('id'),
                "new_short_code": new_code
            }
        )
        
        if success:
            print(f"   Updated: {original_code} → {new_code}")
        
        return success

    def test_export_single_pdf(self):
        """Test exporting individual PDFs"""
        if not self.scan_results:
            print("❌ No scan results available for PDF export test")
            return False
        
        scan_ids = [result.get('id') for result in self.scan_results[:2]]  # Test with first 2
        
        success, response = self.run_test(
            "Export Single PDFs",
            "POST",
            "export-pdf-single",
            200,
            data={"scan_ids": scan_ids},
            response_type='binary'
        )
        
        if success:
            print(f"   Exported ZIP file size: {len(response)} bytes")
        
        return success

    def test_export_merged_pdf(self):
        """Test exporting merged PDF"""
        if not self.scan_results:
            print("❌ No scan results available for merged PDF export test")
            return False
        
        scan_ids = [result.get('id') for result in self.scan_results[:2]]  # Test with first 2
        
        success, response = self.run_test(
            "Export Merged PDF",
            "POST", 
            "export-pdf-merged",
            200,
            data={"scan_ids": scan_ids},
            response_type='binary'
        )
        
        if success:
            print(f"   Exported PDF file size: {len(response)} bytes")
        
        return success

    def test_clear_history(self):
        """Test clearing scan history"""
        success, response = self.run_test(
            "Clear History",
            "DELETE",
            "clear-history",
            200
        )
        
        if success and response:
            print(f"   Cleared: {response.get('message', 'N/A')}")
        
        return success

def main():
    print("🚀 Starting Document Scanner API Tests")
    print("=" * 50)
    
    tester = DocumentScannerAPITester()
    
    # Run all tests
    test_results = []
    
    print("\n1️⃣ Testing Basic Connectivity...")
    test_results.append(("Root Endpoint", tester.test_root_endpoint()))
    
    print("\n2️⃣ Testing Document Scanning...")
    test_results.append(("Single Document Scan", tester.test_single_scan()))
    test_results.append(("Batch Document Scan", tester.test_batch_scan()))
    
    print("\n3️⃣ Testing Data Management...")
    test_results.append(("Scan History", tester.test_scan_history()))
    test_results.append(("Update Filename", tester.test_update_filename()))
    
    print("\n4️⃣ Testing PDF Export...")
    test_results.append(("Export Single PDFs", tester.test_export_single_pdf()))
    test_results.append(("Export Merged PDF", tester.test_export_merged_pdf()))
    
    print("\n5️⃣ Testing Cleanup...")
    test_results.append(("Clear History", tester.test_clear_history()))
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
    print(f"📈 API Calls: {tester.tests_passed}/{tester.tests_run} successful")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())