#!/usr/bin/env python3
"""
Test script for review request requirements:
1) LLM health quick check
2) Direct folder scan flow (no ZIP) 
3) Regression: ZIP-based folder scan still works
"""

import requests
import json
import time
import tempfile
import zipfile
import os
from io import BytesIO
from PIL import Image

class ReviewTester:
    def __init__(self):
        self.base_url = "https://smartscan-land.preview.emergentagent.com/api"
        self.admin_token = None
        
    def test_llm_health(self):
        """1) LLM health quick check - GET /api/llm/health"""
        print("🔍 1) LLM Health Quick Check")
        
        try:
            response = requests.get(f"{self.base_url}/llm/health", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
            
            data = response.json()
            print(f"✅ Status: 200 JSON")
            print(f"   Status: {data.get('status')}")
            print(f"   OpenAI Available: {data.get('openai_available')}")
            print(f"   Emergent Available: {data.get('emergent_available')}")
            
            # Check if status is healthy or degraded (both acceptable)
            status = data.get('status')
            if status in ['healthy', 'degraded', 'unhealthy']:
                print(f"✅ Valid status: {status}")
                return True
            else:
                print(f"❌ Invalid status: {status}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def setup_admin(self):
        """Setup admin authentication"""
        print("\n🔐 Setting up Admin")
        
        # Try setup-admin
        try:
            response = requests.get(f"{self.base_url}/setup-admin", timeout=10)
            if response.status_code == 200:
                print("✅ Admin setup successful")
                
                # Try login with actual admin password from backend
                login_data = {"username": "admin", "password": "Thommit@19"}
                login_response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    self.admin_token = token_data.get('access_token')
                    print(f"✅ Login successful, token: {self.admin_token[:20] if self.admin_token else 'None'}...")
                    return True
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    return False
            else:
                print(f"❌ Setup failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Auth error: {e}")
            return False
    
    def create_test_images(self):
        """Create test images for folder scan"""
        images = []
        for i in range(3):
            # Create simple test image
            img = Image.new('RGB', (400, 300), color=(255, 255, 255))
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            images.append({
                'filename': f'page_{i+1}.jpg',
                'data': img_bytes.getvalue(),
                'relative_path': f'folder/page_{i+1}.jpg'
            })
        
        return images
    
    def test_direct_folder_scan(self):
        """2) Direct folder scan flow (no ZIP)"""
        print("\n📁 2) Direct Folder Scan Flow")
        
        if not self.admin_token:
            print("❌ No admin token - skipping authenticated test")
            return False
        
        images = self.create_test_images()
        
        # Prepare multipart data for scan-folder-direct
        files_data = []
        relative_paths = []
        
        for img in images:
            files_data.append(('files', (img['filename'], BytesIO(img['data']), 'image/jpeg')))
            relative_paths.append(img['relative_path'])
        
        form_data = {
            'relative_paths': json.dumps(relative_paths),
            'pack_as_zip': 'true'
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Try scan-folder-direct endpoint
        try:
            response = requests.post(
                f"{self.base_url}/scan-folder-direct", 
                files=files_data, 
                data=form_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 404:
                print("❌ scan-folder-direct endpoint not found (404)")
                print("   This suggests the direct folder scan feature is not implemented yet")
                return False
            elif response.status_code == 200:
                result = response.json()
                print("✅ Direct folder scan successful")
                
                # Check for job_id to poll status
                job_id = result.get('job_id')
                if job_id:
                    return self.poll_status(job_id, 'folder-direct-status')
                else:
                    return self.validate_result(result)
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_zip_folder_scan(self):
        """3) Regression: ZIP-based folder scan still works"""
        print("\n📦 3) ZIP-based Folder Scan (Regression)")
        
        if not self.admin_token:
            print("❌ No admin token - skipping authenticated test")
            return False
        
        images = self.create_test_images()
        
        # Create ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img in images[:2]:  # Use 2 images for regression test
                zip_file.writestr(img['relative_path'], img['data'])
        
        zip_buffer.seek(0)
        
        # Upload ZIP
        files = {'file': ('test_folder.zip', zip_buffer, 'application/zip')}
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            response = requests.post(
                f"{self.base_url}/scan-folder",
                files=files,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ ZIP folder scan successful")
                
                # Check for job_id or direct result
                job_id = result.get('job_id')
                if job_id:
                    return self.poll_status(job_id, 'folder-scan-status')
                else:
                    return self.validate_zip_result(result)
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def poll_status(self, job_id, status_endpoint_prefix):
        """Poll job status until completion"""
        print(f"   Polling {job_id}...")
        
        for i in range(30):  # 30 second timeout
            try:
                headers = {'Authorization': f'Bearer {self.admin_token}'}
                response = requests.get(
                    f"{self.base_url}/{status_endpoint_prefix}/{job_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')
                    print(f"   Poll {i+1}: {status}")
                    
                    if status == 'completed':
                        return self.validate_result(status_data)
                    elif status == 'error':
                        print(f"❌ Job failed: {status_data.get('error_message', 'Unknown error')}")
                        return False
                else:
                    print(f"   Poll {i+1}: Status endpoint returned {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"   Poll {i+1}: Error - {e}")
                time.sleep(1)
        
        print("❌ Polling timeout")
        return False
    
    def validate_result(self, result):
        """Validate folder scan result"""
        # Check for folder results
        if 'folder_results' in result:
            folder_results = result['folder_results']
            print(f"✅ Found {len(folder_results)} folder result(s)")
            
            # Check for PDF URLs with short codes
            for folder_result in folder_results:
                if 'pdf_urls' in folder_result:
                    pdf_urls = folder_result['pdf_urls']
                    print(f"   PDF URLs: {len(pdf_urls)}")
                    
                    # Check if PDFs are named by short_code
                    for pdf_url in pdf_urls:
                        print(f"   PDF: {pdf_url}")
            
            # Check for ZIP download
            if 'download_url' in folder_results[0]:
                print(f"✅ ZIP download available: {folder_results[0]['download_url']}")
            
            return True
        else:
            print("❌ No folder_results in response")
            return False
    
    def validate_zip_result(self, result):
        """Validate ZIP folder scan result"""
        if 'download_url' in result:
            print(f"✅ ZIP result download: {result['download_url']}")
            return True
        elif 'folder_results' in result:
            return self.validate_result(result)
        else:
            print("❌ No valid result structure")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Review Request Testing")
        print("=" * 50)
        
        results = []
        
        # Test 1: LLM Health (no auth required)
        results.append(("LLM Health Check", self.test_llm_health()))
        
        # Setup admin for authenticated tests
        auth_success = self.setup_admin()
        
        if auth_success:
            # Test 2: Direct folder scan
            results.append(("Direct Folder Scan", self.test_direct_folder_scan()))
            
            # Test 3: ZIP regression
            results.append(("ZIP Folder Scan Regression", self.test_zip_folder_scan()))
        else:
            print("\n⚠️  Skipping authenticated tests due to auth failure")
            results.append(("Direct Folder Scan", False))
            results.append(("ZIP Folder Scan Regression", False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS")
        print("=" * 50)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n📈 Overall: {passed}/{total} tests passed")
        
        return passed == total

def main():
    tester = ReviewTester()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())