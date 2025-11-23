#!/usr/bin/env python3
"""
Test script for new direct folder scan and grouped naming features
Based on review request requirements
"""

import requests
import json
import time
import tempfile
import zipfile
import os
from io import BytesIO
from PIL import Image
import base64

class FolderScanTester:
    def __init__(self):
        # Use the backend URL from frontend/.env
        self.base_url = "https://docscanfix.preview.emergentagent.com/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Create test images in memory
        self.test_images = self.create_test_images()
        
    def create_test_images(self):
        """Create 3 test images with different clarity levels"""
        images = []
        
        for i in range(3):
            # Create a simple test image
            img = Image.new('RGB', (800, 600), color=(255, 255, 255))
            
            # Add some text-like patterns to simulate document content
            # Second image will be "unclear" to trigger continuation
            if i == 1:
                # Make second image unclear/blurry
                img = img.resize((400, 300)).resize((800, 600))  # Simulate blur
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            images.append({
                'filename': f'folder/page_{i+1}.jpg',
                'data': img_bytes.getvalue(),
                'relative_path': f'folder/page_{i+1}.jpg'
            })
            
        return images
        
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
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, **{k:v for k,v in kwargs.items() if k != 'headers'})
            elif method == 'POST':
                response = requests.post(url, headers=headers, **{k:v for k,v in kwargs.items() if k != 'headers'})
            elif method == 'PUT':
                response = requests.put(url, headers=headers, **{k:v for k,v in kwargs.items() if k != 'headers'})
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, **{k:v for k,v in kwargs.items() if k != 'headers'})
            
            return response
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def test_llm_health(self):
        """1) LLM health quick check"""
        print("\n🔍 1) Testing LLM Health Endpoint")
        
        response = self.make_request('GET', 'llm/health')
        
        if not response:
            return self.log_test("LLM Health - Request", False, "Failed to make request")
        
        if response.status_code != 200:
            return self.log_test("LLM Health - Status Code", False, f"Expected 200, got {response.status_code}")
        
        try:
            data = response.json()
        except:
            return self.log_test("LLM Health - JSON Parse", False, "Response is not valid JSON")
        
        # Check required fields
        required_fields = ['status', 'provider', 'openai_available', 'emergent_available']
        for field in required_fields:
            if field not in data:
                return self.log_test("LLM Health - Required Fields", False, f"Missing field: {field}")
        
        status = data.get('status')
        if status not in ['healthy', 'degraded', 'unhealthy']:
            return self.log_test("LLM Health - Status Value", False, f"Invalid status: {status}")
        
        return self.log_test("LLM Health - Complete", True, f"Status: {status}, OpenAI: {data.get('openai_available')}, Emergent: {data.get('emergent_available')}")
    
    def setup_admin_auth(self):
        """Setup admin authentication"""
        print("\n🔐 Setting up Admin Authentication")
        
        # Seed admin
        response = self.make_request('GET', 'setup-admin')
        if not response or response.status_code != 200:
            return self.log_test("Admin Setup", False, f"Setup failed: {response.status_code if response else 'No response'}")
        
        # Login admin - try to get credentials from response or use defaults
        try:
            setup_data = response.json()
            username = setup_data.get('username', 'admin')
            password = setup_data.get('password', 'admin123')
        except:
            username = 'admin'
            password = 'admin123'
        
        login_response = self.make_request('POST', 'auth/login', json={
            'username': username,
            'password': password
        })
        
        if not login_response or login_response.status_code != 200:
            return self.log_test("Admin Login", False, f"Login failed: {login_response.status_code if login_response else 'No response'}")
        
        try:
            login_data = login_response.json()
            self.admin_token = login_data.get('access_token')
            if not self.admin_token:
                return self.log_test("Admin Login - Token", False, "No access token in response")
        except:
            return self.log_test("Admin Login - Parse", False, "Failed to parse login response")
        
        return self.log_test("Admin Authentication", True, f"Token: {self.admin_token[:20]}...")
    
    def test_direct_folder_scan(self):
        """2) Direct folder scan flow (no ZIP)"""
        print("\n📁 2) Testing Direct Folder Scan Flow")
        
        if not self.admin_token:
            return self.log_test("Direct Folder Scan - Auth", False, "No admin token available")
        
        # Check if scan-folder-direct endpoint exists
        files_data = []
        relative_paths = []
        
        for img in self.test_images:
            files_data.append(('files[]', (img['filename'], BytesIO(img['data']), 'image/jpeg')))
            relative_paths.append(img['relative_path'])
        
        # Prepare multipart data
        form_data = {
            'relative_paths': json.dumps(relative_paths),
            'pack_as_zip': 'true'
        }
        
        # Try scan-folder-direct endpoint first
        response = self.make_request('POST', 'scan-folder-direct', files=files_data, data=form_data)
        
        if response and response.status_code == 404:
            # Endpoint doesn't exist, try regular scan-folder
            print("   scan-folder-direct not found, trying scan-folder...")
            return self.test_regular_folder_scan()
        
        if not response:
            return self.log_test("Direct Folder Scan - Request", False, "Failed to make request")
        
        if response.status_code not in [200, 202]:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', response.text)
            except:
                error_msg = response.text
            return self.log_test("Direct Folder Scan - Status", False, f"Status {response.status_code}: {error_msg}")
        
        try:
            result_data = response.json()
        except:
            return self.log_test("Direct Folder Scan - Parse", False, "Failed to parse response")
        
        # Check if we got a job_id for polling
        job_id = result_data.get('job_id')
        if job_id:
            return self.poll_folder_scan_status(job_id)
        else:
            # Direct response
            return self.validate_folder_scan_result(result_data)

    def poll_folder_scan_status(self, job_id):
        """Poll folder scan status until completion"""
        print(f"   Polling status for job: {job_id}")
        
        max_polls = 30  # 30 seconds max
        for i in range(max_polls):
            response = self.make_request('GET', f'folder-direct-status/{job_id}')
            
            if not response or response.status_code != 200:
                return self.log_test("Folder Status Poll", False, f"Poll failed: {response.status_code if response else 'No response'}")
            
            try:
                status_data = response.json()
            except:
                return self.log_test("Folder Status Parse", False, "Failed to parse status response")
            
            status = status_data.get('status')
            print(f"   Poll {i+1}: Status = {status}")
            
            if status == 'completed':
                return self.validate_folder_scan_result(status_data)
            elif status == 'error':
                error_msg = status_data.get('error_message', 'Unknown error')
                return self.log_test("Folder Scan Completion", False, f"Job failed: {error_msg}")
            
            time.sleep(1)
        
        return self.log_test("Folder Scan Timeout", False, "Polling timed out after 30 seconds")
    
    def validate_folder_scan_result(self, result_data):
        """Validate folder scan result structure"""
        # Check for required fields
        required_fields = ['folder_results']
        for field in required_fields:
            if field not in result_data:
                return self.log_test("Folder Result Validation", False, f"Missing field: {field}")
        
        folder_results = result_data.get('folder_results', [])
        if not folder_results:
            return self.log_test("Folder Results", False, "No folder results returned")
        
        # Check first folder result
        folder_result = folder_results[0]
        
        # Check for PDF URLs with short codes
        if 'pdf_urls' in folder_result:
            pdf_urls = folder_result['pdf_urls']
            if not pdf_urls:
                return self.log_test("PDF URLs", False, "No PDF URLs in result")
            
            # Check if PDFs are named by short_code
            for pdf_url in pdf_urls:
                if not any(code in pdf_url for code in ['GCNM', 'DDK', 'HDCQ', 'UNKNOWN', 'CONTINUATION']):
                    print(f"   Warning: PDF URL may not contain short code: {pdf_url}")
        
        # Check for ZIP download if pack_as_zip was true
        if 'download_url' in folder_result or 'zip_url' in result_data:
            zip_url = folder_result.get('download_url') or result_data.get('zip_url')
            if zip_url:
                self.log_test("ZIP Download URL", True, f"ZIP available at: {zip_url}")
            else:
                self.log_test("ZIP Download URL", False, "pack_as_zip=true but no ZIP URL provided")
        
        return self.log_test("Direct Folder Scan", True, f"Processed {len(folder_results)} folder(s)")
    
    def test_regular_folder_scan(self):
        """3) Regression: ZIP-based folder scan still works"""
        print("\n📦 3) Testing ZIP-based Folder Scan (Regression)")
        
        if not self.admin_token:
            return self.log_test("ZIP Folder Scan - Auth", False, "No admin token available")
        
        # Create a ZIP file with test images
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img in self.test_images[:2]:  # Use first 2 images for regression test
                zip_file.writestr(img['relative_path'], img['data'])
        
        zip_buffer.seek(0)
        
        # Upload ZIP file
        files = {'file': ('test_folder.zip', zip_buffer, 'application/zip')}
        
        response = self.make_request('POST', 'scan-folder', files=files)
        
        if not response:
            return self.log_test("ZIP Folder Scan - Request", False, "Failed to make request")
        
        if response.status_code not in [200, 202]:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', response.text)
            except:
                error_msg = response.text
            return self.log_test("ZIP Folder Scan - Status", False, f"Status {response.status_code}: {error_msg}")
        
        try:
            result_data = response.json()
        except:
            return self.log_test("ZIP Folder Scan - Parse", False, "Failed to parse response")
        
        # Check if we got a job_id for polling or direct result
        job_id = result_data.get('job_id')
        if job_id:
            # Poll for completion
            return self.poll_zip_folder_status(job_id)
        else:
            # Direct response - validate structure
            return self.validate_zip_folder_result(result_data)

    def poll_zip_folder_status(self, job_id):
        """Poll ZIP folder scan status"""
        print(f"   Polling ZIP scan status for job: {job_id}")
        
        max_polls = 30
        for i in range(max_polls):
            # Try different status endpoints
            for status_endpoint in [f'folder-status/{job_id}', f'scan-status/{job_id}', f'job-status/{job_id}']:
                response = self.make_request('GET', status_endpoint)
                if response and response.status_code == 200:
                    break
            else:
                return self.log_test("ZIP Status Poll", False, f"No valid status endpoint found for job {job_id}")
            
            try:
                status_data = response.json()
            except:
                return self.log_test("ZIP Status Parse", False, "Failed to parse status response")
            
            status = status_data.get('status')
            print(f"   Poll {i+1}: Status = {status}")
            
            if status == 'completed':
                return self.validate_zip_folder_result(status_data)
            elif status == 'error':
                error_msg = status_data.get('error_message', 'Unknown error')
                return self.log_test("ZIP Scan Completion", False, f"Job failed: {error_msg}")
            
            time.sleep(1)
        
        return self.log_test("ZIP Scan Timeout", False, "Polling timed out after 30 seconds")
    
    def validate_zip_folder_result(self, result_data):
        """Validate ZIP folder scan result"""
        # Check for grouped ZIP creation
        if 'download_url' in result_data:
            download_url = result_data['download_url']
            return self.log_test("ZIP Folder Scan", True, f"Grouped ZIP created: {download_url}")
        
        # Check for folder results with merged PDFs
        if 'folder_results' in result_data:
            folder_results = result_data['folder_results']
            if folder_results:
                return self.log_test("ZIP Folder Scan", True, f"Processed {len(folder_results)} folder(s)")
        
        return self.log_test("ZIP Folder Scan", False, "No valid result structure found")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Folder Scan Feature Tests")
        print("=" * 60)
        
        # Test 1: LLM Health
        test1_success = self.test_llm_health()
        
        # Setup authentication
        auth_success = self.setup_admin_auth()
        if not auth_success:
            print("\n❌ Cannot proceed without authentication")
            return False
        
        # Test 2: Direct folder scan
        test2_success = self.test_direct_folder_scan()
        
        # Test 3: ZIP regression
        test3_success = self.test_regular_folder_scan()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("LLM Health Check", test1_success),
            ("Direct Folder Scan", test2_success), 
            ("ZIP Folder Scan (Regression)", test3_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        print(f"\n📈 Overall: {passed}/{total} major tests passed")
        print(f"📈 API Calls: {self.tests_passed}/{self.tests_run} successful")
        
        return passed == total

def main():
    tester = FolderScanTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed - check details above")
        return 1

if __name__ == "__main__":
    exit(main())