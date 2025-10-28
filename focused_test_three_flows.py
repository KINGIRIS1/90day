#!/usr/bin/env python3
"""
Focused Backend Testing for Three Specific Flows:
1. GET /api/llm/health
2. Direct folder scan: POST /api/scan-folder-direct with multipart files
3. ZIP folder scan regression: POST /api/scan-folder with ZIP file

As requested in the review, includes response codes and concise bodies/errors.
Uses admin login as before.
"""

import requests
import json
import time
import zipfile
import tempfile
import os
from io import BytesIO
from PIL import Image
import base64

class ThreeFlowTester:
    def __init__(self, base_url="https://docsort-pro.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
        # Test images - create small test images
        self.test_images = []
        
    def create_test_image(self, width=100, height=100, color=(255, 0, 0), filename="test.jpg"):
        """Create a small test image"""
        img = Image.new('RGB', (width, height), color)
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=80)
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    def setup_admin_auth(self):
        """Setup admin authentication"""
        print("🔐 Setting up admin authentication...")
        
        # First, setup admin if needed
        try:
            setup_response = self.session.get(f"{self.base_url}/setup-admin")
            print(f"   Setup admin response: {setup_response.status_code}")
        except Exception as e:
            print(f"   Setup admin error (may be normal): {e}")
        
        # Login as admin
        login_data = {
            "username": "admin",
            "password": "Thommit@19"
        }
        
        try:
            login_response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            print(f"   Login response: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.auth_token = login_result.get('access_token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    print("   ✅ Admin authentication successful")
                    return True
                else:
                    print("   ❌ No access token in login response")
                    return False
            else:
                print(f"   ❌ Login failed: {login_response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    def test_llm_health(self):
        """Test 1: GET /api/llm/health"""
        print("\n🔍 TEST 1: LLM Health Endpoint")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/llm/health")
            print(f"Response Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response Body:")
                    print(json.dumps(data, indent=2))
                    
                    # Validate required fields
                    required_fields = ['status', 'provider', 'openai_available', 'emergent_available']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        return False
                    else:
                        print("✅ All required fields present")
                        return True
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"Raw response: {response.text[:200]}")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def test_direct_folder_scan(self):
        """Test 2: Direct folder scan with multipart files"""
        print("\n🔍 TEST 2: Direct Folder Scan (scan-folder-direct)")
        print("=" * 50)
        
        # Create 2-3 tiny test images
        test_files = []
        relative_paths = []
        
        for i in range(3):
            img_data = self.create_test_image(50, 50, (255, i*80, i*100), f"test_{i+1}.jpg")
            test_files.append(('files', (f"test_{i+1}.jpg", BytesIO(img_data), 'image/jpeg')))
            relative_paths.append(f"folder1/subfolder{i}/test_{i+1}.jpg")
        
        # Prepare multipart data
        form_data = {
            'relative_paths': json.dumps(relative_paths),
            'pack_as_zip': 'true'
        }
        
        try:
            print("Sending POST /api/scan-folder-direct...")
            response = self.session.post(
                f"{self.base_url}/scan-folder-direct",
                files=test_files,
                data=form_data
            )
            
            print(f"Response Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response Body:")
                    print(json.dumps(data, indent=2))
                    
                    job_id = data.get('job_id')
                    if job_id:
                        print(f"✅ Got job_id: {job_id}")
                        
                        # Poll status
                        return self.poll_folder_direct_status(job_id)
                    else:
                        print("❌ No job_id in response")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"Raw response: {response.text[:200]}")
                    return False
            else:
                print(f"❌ Request failed with status: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def poll_folder_direct_status(self, job_id):
        """Poll /api/folder-direct-status/{job_id}"""
        print(f"\n📊 Polling status for job_id: {job_id}")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/folder-direct-status/{job_id}")
                print(f"   Attempt {attempt + 1}: Status {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        status = data.get('status', 'unknown')
                        print(f"   Job status: {status}")
                        
                        if status == 'completed':
                            print("✅ Job completed successfully")
                            print("Response Body:")
                            print(json.dumps(data, indent=2))
                            
                            # Test PDF URLs and pack_as_zip if available
                            return self.test_pdf_urls_and_zip(data)
                            
                        elif status == 'error':
                            print(f"❌ Job failed: {data.get('error_message', 'Unknown error')}")
                            return False
                            
                        elif status == 'processing':
                            print("   Still processing, waiting...")
                            time.sleep(2)
                            continue
                        else:
                            print(f"   Unknown status: {status}")
                            time.sleep(2)
                            continue
                            
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Invalid JSON: {e}")
                        return False
                        
                elif response.status_code == 404:
                    print(f"   ❌ Job not found: {response.text[:100]}")
                    return False
                else:
                    print(f"   ❌ Unexpected status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Polling error: {e}")
                return False
        
        print("❌ Polling timeout - job did not complete")
        return False
    
    def test_pdf_urls_and_zip(self, job_data):
        """Test PDF URLs and pack_as_zip functionality"""
        print("\n📄 Testing PDF URLs and ZIP download...")
        
        # Look for download URLs in the response
        download_url = job_data.get('download_url')
        folder_results = job_data.get('folder_results', [])
        
        success = True
        
        # Test main download URL if available
        if download_url:
            try:
                print(f"Testing main download URL: {download_url}")
                if download_url.startswith('/'):
                    full_url = f"{self.base_url.replace('/api', '')}{download_url}"
                else:
                    full_url = download_url
                    
                dl_response = self.session.get(full_url)
                print(f"   Download response: {dl_response.status_code}")
                
                if dl_response.status_code == 200:
                    print(f"   ✅ Downloaded {len(dl_response.content)} bytes")
                else:
                    print(f"   ❌ Download failed: {dl_response.text[:100]}")
                    success = False
                    
            except Exception as e:
                print(f"   ❌ Download error: {e}")
                success = False
        
        # Test individual folder ZIP URLs
        for i, folder_result in enumerate(folder_results):
            zip_url = folder_result.get('zip_download_url')
            if zip_url:
                try:
                    print(f"Testing folder {i+1} ZIP URL: {zip_url}")
                    if zip_url.startswith('/'):
                        full_url = f"{self.base_url.replace('/api', '')}{zip_url}"
                    else:
                        full_url = zip_url
                        
                    zip_response = self.session.get(full_url)
                    print(f"   Folder {i+1} ZIP response: {zip_response.status_code}")
                    
                    if zip_response.status_code == 200:
                        print(f"   ✅ Downloaded folder {i+1} ZIP: {len(zip_response.content)} bytes")
                    else:
                        print(f"   ❌ Folder {i+1} ZIP download failed: {zip_response.text[:100]}")
                        success = False
                        
                except Exception as e:
                    print(f"   ❌ Folder {i+1} ZIP error: {e}")
                    success = False
        
        return success
    
    def test_zip_folder_scan_regression(self):
        """Test 3: ZIP folder scan regression"""
        print("\n🔍 TEST 3: ZIP Folder Scan Regression (scan-folder)")
        print("=" * 50)
        
        # Create a small ZIP file with 1 folder, 2 images
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Create folder structure with 2 images
            for i in range(2):
                img_data = self.create_test_image(60, 60, (0, i*120, 255-i*100), f"image_{i+1}.jpg")
                zipf.writestr(f"test_folder/image_{i+1}.jpg", img_data)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()
        
        try:
            print(f"Sending ZIP file ({len(zip_data)} bytes) to POST /api/scan-folder...")
            
            files = {'file': ('test_folder.zip', BytesIO(zip_data), 'application/zip')}
            
            response = self.session.post(
                f"{self.base_url}/scan-folder",
                files=files
            )
            
            print(f"Response Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response Body:")
                    print(json.dumps(data, indent=2))
                    
                    job_id = data.get('job_id')
                    if job_id:
                        print(f"✅ Got job_id: {job_id}")
                        
                        # Poll status for ZIP scan
                        return self.poll_zip_folder_status(job_id)
                    else:
                        print("❌ No job_id in response")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"Raw response: {response.text[:200]}")
                    return False
            else:
                print(f"❌ Request failed with status: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def poll_zip_folder_status(self, job_id):
        """Poll /api/folder-scan-status/{job_id} for ZIP scan"""
        print(f"\n📊 Polling ZIP scan status for job_id: {job_id}")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/folder-scan-status/{job_id}")
                print(f"   Attempt {attempt + 1}: Status {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        status = data.get('status', 'unknown')
                        print(f"   Job status: {status}")
                        
                        if status == 'completed':
                            print("✅ ZIP scan completed successfully")
                            print("Response Body:")
                            print(json.dumps(data, indent=2))
                            
                            # Test result ZIP download
                            return self.test_zip_result_download(data)
                            
                        elif status == 'error':
                            print(f"❌ ZIP scan failed: {data.get('error_message', 'Unknown error')}")
                            return False
                            
                        elif status == 'processing':
                            print("   Still processing ZIP scan, waiting...")
                            time.sleep(2)
                            continue
                        else:
                            print(f"   Unknown status: {status}")
                            time.sleep(2)
                            continue
                            
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Invalid JSON: {e}")
                        return False
                        
                elif response.status_code == 404:
                    print(f"   ❌ ZIP scan job not found: {response.text[:100]}")
                    return False
                else:
                    print(f"   ❌ Unexpected status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ ZIP polling error: {e}")
                return False
        
        print("❌ ZIP polling timeout - job did not complete")
        return False
    
    def test_zip_result_download(self, job_data):
        """Test downloading the result ZIP from ZIP folder scan"""
        print("\n📦 Testing ZIP result download...")
        
        download_url = job_data.get('download_url')
        
        if not download_url:
            print("❌ No download_url in job data")
            return False
        
        try:
            print(f"Testing ZIP result download: {download_url}")
            
            if download_url.startswith('/'):
                full_url = f"{self.base_url.replace('/api', '')}{download_url}"
            else:
                full_url = download_url
                
            dl_response = self.session.get(full_url)
            print(f"   ZIP download response: {dl_response.status_code}")
            
            if dl_response.status_code == 200:
                print(f"   ✅ Downloaded result ZIP: {len(dl_response.content)} bytes")
                
                # Verify it's a valid ZIP
                try:
                    zip_test = zipfile.ZipFile(BytesIO(dl_response.content))
                    file_list = zip_test.namelist()
                    print(f"   ✅ Valid ZIP with {len(file_list)} files: {file_list}")
                    zip_test.close()
                    return True
                except zipfile.BadZipFile:
                    print("   ❌ Downloaded file is not a valid ZIP")
                    return False
            else:
                print(f"   ❌ ZIP download failed: {dl_response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"   ❌ ZIP download error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all three tests"""
        print("🚀 Starting Three-Flow Backend Testing")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_admin_auth():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run the three tests
        results = []
        
        # Test 1: LLM Health
        results.append(("LLM Health Endpoint", self.test_llm_health()))
        
        # Test 2: Direct Folder Scan
        results.append(("Direct Folder Scan", self.test_direct_folder_scan()))
        
        # Test 3: ZIP Folder Scan Regression
        results.append(("ZIP Folder Scan Regression", self.test_zip_folder_scan_regression()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 THREE-FLOW TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📈 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All three flows working correctly!")
            return True
        else:
            print("⚠️  Some flows failed - check details above")
            return False

def main():
    tester = ThreeFlowTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())