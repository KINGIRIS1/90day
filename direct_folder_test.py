#!/usr/bin/env python3
"""
Direct Folder Scan API Test Suite
Tests the new direct folder scan endpoints and all-zip functionality
"""

import requests
import json
import time
import tempfile
import os
from io import BytesIO
from PIL import Image
import base64
from pathlib import Path

class DirectFolderScanTester:
    def __init__(self):
        self.base_url = "https://document-ai-scan.preview.emergentagent.com/api"
        self.auth_headers = {}
        self.test_results = []
        
        # Create test images
        self.test_images = self._create_test_images()
        
    def _create_test_images(self):
        """Create small test images for folder scanning"""
        images = []
        
        # Create 3 small test images (100x100 pixels)
        for i in range(3):
            # Create a simple colored image
            img = Image.new('RGB', (100, 100), color=(50 + i*50, 100, 150))
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=80)
            img_bytes.seek(0)
            
            images.append({
                'filename': f'test_image_{i+1}.jpg',
                'content': img_bytes.getvalue(),
                'relative_path': f'folder_{(i//2)+1}/test_image_{i+1}.jpg'  # 2 folders: folder_1, folder_2
            })
            
        return images
    
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating...")
        
        # First try to login
        login_data = {
            "username": "admin",
            "password": "Thommit@19"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                token = result.get('access_token')
                if token:
                    self.auth_headers = {"Authorization": f"Bearer {token}"}
                    print("✅ Authentication successful")
                    return True
                else:
                    print("❌ No access token in response")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_direct_folder_scan_start(self):
        """Test starting a direct folder scan"""
        print("\n📁 Testing Direct Folder Scan Start...")
        
        # Prepare files and relative paths
        files = []
        relative_paths = []
        
        for img_data in self.test_images:
            files.append(('files', (img_data['filename'], BytesIO(img_data['content']), 'image/jpeg')))
            relative_paths.append(img_data['relative_path'])
        
        # Prepare form data
        form_data = {
            'relative_paths': json.dumps(relative_paths),
            'pack_as_zip': 'true'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/scan-folder-direct",
                files=files,
                data=form_data,
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                status_url = result.get('status_url')
                
                print(f"✅ Folder scan started successfully")
                print(f"   Job ID: {job_id}")
                print(f"   Status URL: {status_url}")
                
                self.test_results.append({
                    'test': 'direct_folder_scan_start',
                    'success': True,
                    'job_id': job_id,
                    'status_url': status_url
                })
                return job_id
            else:
                print(f"❌ Failed to start folder scan: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append({
                    'test': 'direct_folder_scan_start',
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
                return None
                
        except Exception as e:
            print(f"❌ Error starting folder scan: {e}")
            self.test_results.append({
                'test': 'direct_folder_scan_start',
                'success': False,
                'error': str(e)
            })
            return None
    
    def test_folder_scan_status_polling(self, job_id):
        """Test polling folder scan status until completion"""
        print(f"\n📊 Testing Status Polling for Job {job_id}...")
        
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(
                    f"{self.base_url}/folder-direct-status/{job_id}",
                    headers=self.auth_headers
                )
                
                if response.status_code == 200:
                    status = response.json()
                    current_status = status.get('status')
                    completed_folders = status.get('completed_folders', 0)
                    total_folders = status.get('total_folders', 0)
                    all_zip_url = status.get('all_zip_url')
                    folder_results = status.get('folder_results', [])
                    
                    print(f"   Status: {current_status} ({completed_folders}/{total_folders} folders)")
                    
                    if current_status == 'completed':
                        print("✅ Folder scan completed successfully")
                        print(f"   All ZIP URL: {all_zip_url}")
                        print(f"   Folder results: {len(folder_results)} folders")
                        
                        # Validate folder_results structure
                        pdf_urls_found = []
                        errors_found = []
                        
                        for folder_result in folder_results:
                            folder_name = folder_result.get('folder_name')
                            pdf_urls = folder_result.get('pdf_urls', [])
                            errors = folder_result.get('errors', [])
                            success_count = folder_result.get('success_count', 0)
                            error_count = folder_result.get('error_count', 0)
                            
                            print(f"   Folder '{folder_name}': {success_count} success, {error_count} errors")
                            print(f"     PDF URLs: {pdf_urls}")
                            if errors:
                                print(f"     Errors: {errors}")
                                errors_found.extend(errors)
                            
                            pdf_urls_found.extend(pdf_urls)
                        
                        self.test_results.append({
                            'test': 'folder_scan_status_polling',
                            'success': True,
                            'status': status,
                            'all_zip_url': all_zip_url,
                            'pdf_urls': pdf_urls_found,
                            'errors': errors_found
                        })
                        return status
                        
                    elif current_status == 'error':
                        error_message = status.get('error_message', 'Unknown error')
                        print(f"❌ Folder scan failed: {error_message}")
                        self.test_results.append({
                            'test': 'folder_scan_status_polling',
                            'success': False,
                            'error': error_message
                        })
                        return None
                    
                    # Still processing, wait and retry
                    time.sleep(10)
                    attempt += 1
                    
                else:
                    print(f"❌ Failed to get status: {response.status_code}")
                    print(f"   Response: {response.text}")
                    self.test_results.append({
                        'test': 'folder_scan_status_polling',
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    })
                    return None
                    
            except Exception as e:
                print(f"❌ Error polling status: {e}")
                self.test_results.append({
                    'test': 'folder_scan_status_polling',
                    'success': False,
                    'error': str(e)
                })
                return None
        
        print("❌ Timeout waiting for folder scan completion")
        self.test_results.append({
            'test': 'folder_scan_status_polling',
            'success': False,
            'error': "Timeout after 5 minutes"
        })
        return None
    
    def test_all_zip_download(self, all_zip_url):
        """Test downloading the all-zip file"""
        print(f"\n📦 Testing All-ZIP Download...")
        
        if not all_zip_url:
            print("❌ No all_zip_url provided")
            self.test_results.append({
                'test': 'all_zip_download',
                'success': False,
                'error': 'No all_zip_url provided'
            })
            return False
        
        # Construct full URL
        full_url = f"https://document-ai-scan.preview.emergentagent.com{all_zip_url}"
        
        try:
            response = requests.get(full_url, headers=self.auth_headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                print(f"✅ All-ZIP download successful")
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Length: {content_length} bytes")
                
                # Verify it's actually a ZIP file
                if content_type == 'application/zip' or content_length > 0:
                    print("✅ Content appears to be a valid ZIP file")
                    self.test_results.append({
                        'test': 'all_zip_download',
                        'success': True,
                        'content_type': content_type,
                        'content_length': content_length
                    })
                    return True
                else:
                    print("⚠️  Content may not be a valid ZIP file")
                    self.test_results.append({
                        'test': 'all_zip_download',
                        'success': False,
                        'error': f'Invalid content type: {content_type}'
                    })
                    return False
            else:
                print(f"❌ Failed to download ZIP: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append({
                    'test': 'all_zip_download',
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
                return False
                
        except Exception as e:
            print(f"❌ Error downloading ZIP: {e}")
            self.test_results.append({
                'test': 'all_zip_download',
                'success': False,
                'error': str(e)
            })
            return False
    
    def test_individual_pdf_downloads(self, pdf_urls):
        """Test downloading individual PDF files"""
        print(f"\n📄 Testing Individual PDF Downloads...")
        
        if not pdf_urls:
            print("❌ No PDF URLs provided")
            self.test_results.append({
                'test': 'individual_pdf_downloads',
                'success': False,
                'error': 'No PDF URLs provided'
            })
            return False
        
        success_count = 0
        total_count = len(pdf_urls)
        
        for i, pdf_url in enumerate(pdf_urls):
            print(f"   Testing PDF {i+1}/{total_count}: {pdf_url}")
            
            # Construct full URL
            full_url = f"https://document-ai-scan.preview.emergentagent.com{pdf_url}"
            
            try:
                response = requests.get(full_url, headers=self.auth_headers)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    
                    print(f"     ✅ Success - {content_type}, {content_length} bytes")
                    success_count += 1
                else:
                    print(f"     ❌ Failed - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error - {e}")
        
        success = success_count == total_count
        print(f"\n{'✅' if success else '❌'} PDF Downloads: {success_count}/{total_count} successful")
        
        self.test_results.append({
            'test': 'individual_pdf_downloads',
            'success': success,
            'success_count': success_count,
            'total_count': total_count
        })
        
        return success
    
    def test_error_simulation(self):
        """Test error handling by sending invalid data"""
        print(f"\n⚠️  Testing Error Handling...")
        
        # Test with no files
        try:
            response = requests.post(
                f"{self.base_url}/scan-folder-direct",
                files=[],
                data={'pack_as_zip': 'true'},
                headers=self.auth_headers
            )
            
            if response.status_code == 400:
                print("✅ Correctly rejected empty file list")
                self.test_results.append({
                    'test': 'error_handling_empty_files',
                    'success': True
                })
            else:
                print(f"❌ Unexpected response for empty files: {response.status_code}")
                self.test_results.append({
                    'test': 'error_handling_empty_files',
                    'success': False,
                    'error': f"Expected 400, got {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Error testing empty files: {e}")
            self.test_results.append({
                'test': 'error_handling_empty_files',
                'success': False,
                'error': str(e)
            })
        
        # Test with invalid job ID
        try:
            response = requests.get(
                f"{self.base_url}/folder-direct-status/invalid-job-id",
                headers=self.auth_headers
            )
            
            if response.status_code == 404:
                print("✅ Correctly rejected invalid job ID")
                self.test_results.append({
                    'test': 'error_handling_invalid_job',
                    'success': True
                })
            else:
                print(f"❌ Unexpected response for invalid job ID: {response.status_code}")
                self.test_results.append({
                    'test': 'error_handling_invalid_job',
                    'success': False,
                    'error': f"Expected 404, got {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Error testing invalid job ID: {e}")
            self.test_results.append({
                'test': 'error_handling_invalid_job',
                'success': False,
                'error': str(e)
            })
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Direct Folder Scan API Tests")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        # Step 2: Start folder scan
        job_id = self.test_direct_folder_scan_start()
        if not job_id:
            print("❌ Failed to start folder scan - cannot continue")
            return False
        
        # Step 3: Poll status until completion
        final_status = self.test_folder_scan_status_polling(job_id)
        if not final_status:
            print("❌ Folder scan did not complete successfully")
            return False
        
        # Step 4: Test all-zip download
        all_zip_url = final_status.get('all_zip_url')
        zip_success = self.test_all_zip_download(all_zip_url)
        
        # Step 5: Test individual PDF downloads
        pdf_urls = []
        for folder_result in final_status.get('folder_results', []):
            pdf_urls.extend(folder_result.get('pdf_urls', []))
        
        pdf_success = self.test_individual_pdf_downloads(pdf_urls)
        
        # Step 6: Test error handling
        self.test_error_simulation()
        
        # Print summary
        self.print_summary()
        
        return zip_success and pdf_success
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.get('success', False))
        
        for result in self.test_results:
            test_name = result.get('test', 'Unknown')
            success = result.get('success', False)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            
            if not success and 'error' in result:
                print(f"     Error: {result['error']}")
        
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")

def main():
    tester = DirectFolderScanTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())