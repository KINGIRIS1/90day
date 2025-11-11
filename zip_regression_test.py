#!/usr/bin/env python3
"""
ZIP Folder Scan Regression Test
Tests that the original ZIP folder scan functionality still works
"""

import requests
import json
import time
import tempfile
import os
import zipfile
from io import BytesIO
from PIL import Image

class ZipFolderScanTester:
    def __init__(self):
        self.base_url = "https://land-doc-ai-1.preview.emergentagent.com/api"
        self.auth_headers = {}
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating...")
        
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
    
    def create_test_zip(self):
        """Create a test ZIP file with folder structure"""
        print("📦 Creating test ZIP file...")
        
        # Create temporary ZIP file
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create 2 test images in different folders
            for folder_idx in range(2):
                folder_name = f"test_folder_{folder_idx + 1}"
                
                for img_idx in range(2):
                    # Create a simple test image
                    img = Image.new('RGB', (100, 100), color=(50 + img_idx*50, 100, 150))
                    img_buffer = BytesIO()
                    img.save(img_buffer, format='JPEG', quality=80)
                    img_buffer.seek(0)
                    
                    # Add to ZIP
                    img_path = f"{folder_name}/test_image_{img_idx + 1}.jpg"
                    zip_file.writestr(img_path, img_buffer.getvalue())
        
        zip_buffer.seek(0)
        print(f"✅ Created test ZIP with 4 images in 2 folders")
        return zip_buffer.getvalue()
    
    def test_zip_folder_scan(self):
        """Test ZIP folder scan functionality"""
        print("\n📁 Testing ZIP Folder Scan...")
        
        # Create test ZIP
        zip_data = self.create_test_zip()
        
        # Upload ZIP file
        files = {'file': ('test_folder.zip', BytesIO(zip_data), 'application/zip')}
        
        try:
            response = requests.post(
                f"{self.base_url}/scan-folder",
                files=files,
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                status_url = result.get('status_url')
                
                print(f"✅ ZIP folder scan started successfully")
                print(f"   Job ID: {job_id}")
                print(f"   Status URL: {status_url}")
                
                return job_id
            else:
                print(f"❌ Failed to start ZIP folder scan: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting ZIP folder scan: {e}")
            return None
    
    def test_zip_scan_status_polling(self, job_id):
        """Test polling ZIP scan status until completion"""
        print(f"\n📊 Testing ZIP Status Polling for Job {job_id}...")
        
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(
                    f"{self.base_url}/folder-scan-status/{job_id}",
                    headers=self.auth_headers
                )
                
                if response.status_code == 200:
                    status = response.json()
                    current_status = status.get('status')
                    completed_folders = status.get('completed_folders', 0)
                    total_folders = status.get('total_folders', 0)
                    folder_results = status.get('folder_results', [])
                    
                    print(f"   Status: {current_status} ({completed_folders}/{total_folders} folders)")
                    
                    if current_status == 'completed':
                        print("✅ ZIP folder scan completed successfully")
                        print(f"   Folder results: {len(folder_results)} folders")
                        
                        # Check folder results structure
                        for folder_result in folder_results:
                            folder_name = folder_result.get('folder_name')
                            success_count = folder_result.get('success_count', 0)
                            error_count = folder_result.get('error_count', 0)
                            zip_download_url = folder_result.get('zip_download_url')
                            
                            print(f"   Folder '{folder_name}': {success_count} success, {error_count} errors")
                            if zip_download_url:
                                print(f"     ZIP URL: {zip_download_url}")
                        
                        return status
                        
                    elif current_status == 'error':
                        error_message = status.get('error_message', 'Unknown error')
                        print(f"❌ ZIP folder scan failed: {error_message}")
                        return None
                    
                    # Still processing, wait and retry
                    time.sleep(10)
                    attempt += 1
                    
                else:
                    print(f"❌ Failed to get ZIP status: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error polling ZIP status: {e}")
                return None
        
        print("❌ Timeout waiting for ZIP folder scan completion")
        return None
    
    def test_zip_download(self, folder_results):
        """Test downloading ZIP results"""
        print(f"\n📦 Testing ZIP Downloads...")
        
        if not folder_results:
            print("❌ No folder results provided")
            return False
        
        success_count = 0
        total_count = 0
        
        for folder_result in folder_results:
            zip_url = folder_result.get('zip_download_url')
            if zip_url:
                total_count += 1
                folder_name = folder_result.get('folder_name')
                print(f"   Testing ZIP download for folder '{folder_name}': {zip_url}")
                
                # Construct full URL
                full_url = f"https://land-doc-ai-1.preview.emergentagent.com{zip_url}"
                
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
        print(f"\n{'✅' if success else '❌'} ZIP Downloads: {success_count}/{total_count} successful")
        
        return success
    
    def run_regression_test(self):
        """Run the complete ZIP regression test"""
        print("🚀 Starting ZIP Folder Scan Regression Test")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        # Step 2: Start ZIP folder scan
        job_id = self.test_zip_folder_scan()
        if not job_id:
            print("❌ Failed to start ZIP folder scan - cannot continue")
            return False
        
        # Step 3: Poll status until completion
        final_status = self.test_zip_scan_status_polling(job_id)
        if not final_status:
            print("❌ ZIP folder scan did not complete successfully")
            return False
        
        # Step 4: Test ZIP downloads
        folder_results = final_status.get('folder_results', [])
        zip_success = self.test_zip_download(folder_results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ZIP REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        if zip_success:
            print("✅ ZIP folder scan regression test PASSED")
            print("   All original ZIP functionality is working correctly")
        else:
            print("❌ ZIP folder scan regression test FAILED")
            print("   Some ZIP functionality may be broken")
        
        return zip_success

def main():
    tester = ZipFolderScanTester()
    success = tester.run_regression_test()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())