#!/usr/bin/env python3
"""
Folder Scanning Feature Test Suite
Tests the new ZIP upload and folder structure preservation functionality
"""

import requests
import sys
import json
import time
import zipfile
import tempfile
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO

class FolderScanTester:
    def __init__(self, base_url="https://smartdocscan-3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_zip_path = "/tmp/test_structure.zip"
        
    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        return success

    def test_zip_structure_validation(self):
        """Test 1: Validate test ZIP structure"""
        print("\n🔍 Test 1: ZIP Structure Validation")
        
        try:
            if not os.path.exists(self.test_zip_path):
                return self.log_test("ZIP file exists", False, f"File not found: {self.test_zip_path}")
            
            with zipfile.ZipFile(self.test_zip_path, 'r') as z:
                files = z.namelist()
                
            expected_files = [
                'test_zip/folder1/test_1.jpg',
                'test_zip/folder1/test_2.jpg', 
                'test_zip/folder2/subfolder/test_3.jpg'
            ]
            
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
            
            if len(image_files) != 3:
                return self.log_test("ZIP contains 3 images", False, f"Found {len(image_files)} images")
            
            for expected in expected_files:
                if expected not in files:
                    return self.log_test("ZIP structure correct", False, f"Missing: {expected}")
            
            return self.log_test("ZIP structure validation", True, f"Found {len(image_files)} images in correct structure")
            
        except Exception as e:
            return self.log_test("ZIP structure validation", False, f"Error: {str(e)}")

    def test_folder_scan_endpoint(self):
        """Test 2: Basic folder scan functionality"""
        print("\n🔍 Test 2: Folder Scan Endpoint")
        
        try:
            url = f"{self.base_url}/scan-folder"
            
            # Prepare file upload
            with open(self.test_zip_path, 'rb') as f:
                files = {'file': ('test_structure.zip', f, 'application/zip')}
                
                print(f"   Uploading to: {url}")
                response = requests.post(url, files=files, timeout=120)  # 2 minute timeout
            
            if response.status_code != 200:
                return self.log_test("Folder scan request", False, 
                                   f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            try:
                result = response.json()
            except json.JSONDecodeError:
                return self.log_test("Folder scan response format", False, 
                                   f"Invalid JSON response: {response.text[:200]}")
            
            # Store result for later tests
            self.scan_result = result
            
            return self.log_test("Folder scan request", True, 
                               f"Processed {result.get('processed_files', 0)} files")
            
        except requests.exceptions.Timeout:
            return self.log_test("Folder scan request", False, "Request timeout (>2 minutes)")
        except Exception as e:
            return self.log_test("Folder scan request", False, f"Error: {str(e)}")

    def test_response_validation(self):
        """Test 3: Validate response structure and counts"""
        print("\n🔍 Test 3: Response Validation")
        
        if not hasattr(self, 'scan_result'):
            return self.log_test("Response validation", False, "No scan result available")
        
        result = self.scan_result
        
        # Check required fields
        required_fields = ['scan_id', 'total_files', 'processed_files', 'success_count', 
                          'processing_time_seconds', 'files', 'download_url']
        
        for field in required_fields:
            if field not in result:
                return self.log_test("Response structure", False, f"Missing field: {field}")
        
        # Validate counts
        total_files = result.get('total_files', 0)
        processed_files = result.get('processed_files', 0)
        success_count = result.get('success_count', 0)
        
        if total_files != 3:
            return self.log_test("Total files count", False, f"Expected 3, got {total_files}")
        
        if processed_files != 3:
            return self.log_test("Processed files count", False, f"Expected 3, got {processed_files}")
        
        # Check files array
        files = result.get('files', [])
        if len(files) != 3:
            return self.log_test("Files array length", False, f"Expected 3 files, got {len(files)}")
        
        # Validate file structure preservation
        expected_paths = [
            'test_zip/folder1/test_1.jpg',
            'test_zip/folder1/test_2.jpg',
            'test_zip/folder2/subfolder/test_3.jpg'
        ]
        
        found_paths = [f.get('relative_path', '') for f in files]
        
        for expected_path in expected_paths:
            if expected_path not in found_paths:
                return self.log_test("Folder structure preservation", False, 
                                   f"Missing path: {expected_path}")
        
        # Check processing time is reasonable
        processing_time = result.get('processing_time_seconds', 0)
        if processing_time <= 0 or processing_time > 300:  # Should be between 0 and 5 minutes
            return self.log_test("Processing time reasonable", False, 
                               f"Processing time: {processing_time}s")
        
        return self.log_test("Response validation", True, 
                           f"All fields valid, {success_count}/{total_files} successful")

    def test_file_results_validation(self):
        """Test 4: Validate individual file results"""
        print("\n🔍 Test 4: File Results Validation")
        
        if not hasattr(self, 'scan_result'):
            return self.log_test("File results validation", False, "No scan result available")
        
        files = self.scan_result.get('files', [])
        
        for i, file_result in enumerate(files):
            # Check required fields for each file
            required_file_fields = ['relative_path', 'original_filename', 'detected_full_name', 
                                  'short_code', 'confidence_score', 'status']
            
            for field in required_file_fields:
                if field not in file_result:
                    return self.log_test(f"File {i+1} structure", False, f"Missing field: {field}")
            
            # Validate confidence score
            confidence = file_result.get('confidence_score', 0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                return self.log_test(f"File {i+1} confidence", False, 
                                   f"Invalid confidence: {confidence}")
            
            # Check status
            status = file_result.get('status', '')
            if status not in ['success', 'error', 'skipped']:
                return self.log_test(f"File {i+1} status", False, f"Invalid status: {status}")
            
            print(f"   File {i+1}: {file_result.get('relative_path')} -> {file_result.get('short_code')} "
                  f"(confidence: {confidence:.2f}, status: {status})")
        
        return self.log_test("File results validation", True, f"All {len(files)} file results valid")

    def test_download_result(self):
        """Test 5: Download result ZIP"""
        print("\n🔍 Test 5: Download Result ZIP")
        
        if not hasattr(self, 'scan_result'):
            return self.log_test("Download test", False, "No scan result available")
        
        download_url = self.scan_result.get('download_url')
        if not download_url:
            return self.log_test("Download URL present", False, "No download_url in response")
        
        try:
            # Extract filename from download_url
            if '/download-folder-result/' in download_url:
                filename = download_url.split('/download-folder-result/')[-1]
                full_download_url = f"{self.base_url}/download-folder-result/{filename}"
            else:
                full_download_url = download_url
            
            print(f"   Downloading from: {full_download_url}")
            response = requests.get(full_download_url, timeout=60)
            
            if response.status_code != 200:
                return self.log_test("Download request", False, 
                                   f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            # Check if response is a ZIP file
            if not response.content.startswith(b'PK'):
                return self.log_test("Download content type", False, "Response is not a ZIP file")
            
            # Save and validate ZIP structure
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip.write(response.content)
                temp_zip_path = temp_zip.name
            
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as z:
                    result_files = z.namelist()
                
                # Check for PDF files in correct structure
                pdf_files = [f for f in result_files if f.endswith('.pdf')]
                
                if len(pdf_files) == 0:
                    return self.log_test("Result ZIP contains PDFs", False, "No PDF files found")
                
                # Validate folder structure is preserved
                expected_folders = ['test_zip/folder1/', 'test_zip/folder2/subfolder/']
                
                for folder in expected_folders:
                    folder_pdfs = [f for f in pdf_files if f.startswith(folder)]
                    if not folder_pdfs:
                        return self.log_test("Folder structure preserved", False, 
                                           f"No PDFs found in folder: {folder}")
                
                return self.log_test("Download result ZIP", True, 
                                   f"Downloaded {len(response.content)} bytes, {len(pdf_files)} PDFs")
                
            finally:
                # Clean up temp file
                os.unlink(temp_zip_path)
                
        except requests.exceptions.Timeout:
            return self.log_test("Download request", False, "Download timeout")
        except Exception as e:
            return self.log_test("Download result ZIP", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Test 6: Error handling with invalid files"""
        print("\n🔍 Test 6: Error Handling")
        
        # Test 6a: Non-ZIP file
        try:
            url = f"{self.base_url}/scan-folder"
            
            # Create a fake text file
            fake_file = BytesIO(b"This is not a ZIP file")
            files = {'file': ('fake.txt', fake_file, 'text/plain')}
            
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 400:
                success_6a = self.log_test("Non-ZIP file rejection", True, 
                                         "Correctly rejected non-ZIP file")
            else:
                success_6a = self.log_test("Non-ZIP file rejection", False, 
                                         f"Expected 400, got {response.status_code}")
        except Exception as e:
            success_6a = self.log_test("Non-ZIP file rejection", False, f"Error: {str(e)}")
        
        # Test 6b: Empty ZIP file
        try:
            # Create empty ZIP
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w') as z:
                    pass  # Create empty ZIP
                
                with open(temp_zip.name, 'rb') as f:
                    files = {'file': ('empty.zip', f, 'application/zip')}
                    response = requests.post(url, files=files, timeout=30)
                
                os.unlink(temp_zip.name)
            
            if response.status_code == 400:
                success_6b = self.log_test("Empty ZIP rejection", True, 
                                         "Correctly rejected empty ZIP")
            else:
                success_6b = self.log_test("Empty ZIP rejection", False, 
                                         f"Expected 400, got {response.status_code}")
        except Exception as e:
            success_6b = self.log_test("Empty ZIP rejection", False, f"Error: {str(e)}")
        
        return success_6a and success_6b

    def run_all_tests(self):
        """Run all folder scanning tests"""
        print("🚀 Starting Folder Scanning Feature Tests")
        print("=" * 60)
        
        test_results = []
        
        # Run tests in sequence
        test_results.append(("ZIP Structure Validation", self.test_zip_structure_validation()))
        test_results.append(("Folder Scan Endpoint", self.test_folder_scan_endpoint()))
        test_results.append(("Response Validation", self.test_response_validation()))
        test_results.append(("File Results Validation", self.test_file_results_validation()))
        test_results.append(("Download Result ZIP", self.test_download_result()))
        test_results.append(("Error Handling", self.test_error_handling()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FOLDER SCANNING TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All folder scanning tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

def main():
    """Main test runner"""
    tester = FolderScanTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())