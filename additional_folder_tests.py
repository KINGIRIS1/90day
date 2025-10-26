#!/usr/bin/env python3
"""
Additional edge case tests for folder scanning feature
"""

import requests
import sys
import json
import tempfile
import zipfile
import os
from io import BytesIO
from PIL import Image

class AdditionalFolderTests:
    def __init__(self, base_url="https://docscan-desktop.preview.emergentagent.com/api"):
        self.base_url = base_url
        
    def create_test_image(self, width=100, height=100, color=(255, 255, 255)):
        """Create a simple test image"""
        img = Image.new('RGB', (width, height), color)
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=80)
        return img_bytes.getvalue()
    
    def test_large_folder_structure(self):
        """Test with deeper folder structure"""
        print("\n🔍 Testing Large Folder Structure...")
        
        try:
            # Create ZIP with deeper structure
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w') as z:
                    # Create test images in various folders
                    folders = [
                        'level1/level2/level3/',
                        'documents/2024/january/',
                        'scans/batch1/',
                        'archive/old_docs/'
                    ]
                    
                    for i, folder in enumerate(folders):
                        img_data = self.create_test_image()
                        z.writestr(f'{folder}test_{i+1}.jpg', img_data)
                
                # Upload the ZIP
                with open(temp_zip.name, 'rb') as f:
                    files = {'file': ('large_structure.zip', f, 'application/zip')}
                    response = requests.post(f"{self.base_url}/scan-folder", files=files, timeout=120)
                
                os.unlink(temp_zip.name)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Large structure test passed - processed {result.get('processed_files', 0)} files")
                return True
            else:
                print(f"❌ Large structure test failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Large structure test error: {str(e)}")
            return False
    
    def test_mixed_file_types(self):
        """Test ZIP with mixed file types (should only process images)"""
        print("\n🔍 Testing Mixed File Types...")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w') as z:
                    # Add images
                    img_data = self.create_test_image()
                    z.writestr('images/document1.jpg', img_data)
                    z.writestr('images/document2.png', img_data)
                    
                    # Add non-image files (should be ignored)
                    z.writestr('documents/readme.txt', b'This is a text file')
                    z.writestr('documents/data.pdf', b'%PDF-1.4 fake pdf')
                    z.writestr('documents/spreadsheet.xlsx', b'fake excel file')
                
                with open(temp_zip.name, 'rb') as f:
                    files = {'file': ('mixed_files.zip', f, 'application/zip')}
                    response = requests.post(f"{self.base_url}/scan-folder", files=files, timeout=120)
                
                os.unlink(temp_zip.name)
            
            if response.status_code == 200:
                result = response.json()
                total_files = result.get('total_files', 0)
                processed_files = result.get('processed_files', 0)
                
                # Should only process 2 image files, ignore others
                if total_files == 2 and processed_files == 2:
                    print(f"✅ Mixed file types test passed - correctly processed only {processed_files} image files")
                    return True
                else:
                    print(f"❌ Mixed file types test failed - Expected 2 images, got {total_files} total, {processed_files} processed")
                    return False
            else:
                print(f"❌ Mixed file types test failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Mixed file types test error: {str(e)}")
            return False
    
    def test_file_size_limits(self):
        """Test file size validation"""
        print("\n🔍 Testing File Size Limits...")
        
        try:
            # Create a ZIP that's close to but under the limit
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w') as z:
                    # Add a reasonable number of small images
                    for i in range(10):  # 10 images should be well under limits
                        img_data = self.create_test_image(200, 200)  # Slightly larger images
                        z.writestr(f'batch/image_{i+1:03d}.jpg', img_data)
                
                with open(temp_zip.name, 'rb') as f:
                    files = {'file': ('size_test.zip', f, 'application/zip')}
                    response = requests.post(f"{self.base_url}/scan-folder", files=files, timeout=120)
                
                os.unlink(temp_zip.name)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File size test passed - processed {result.get('processed_files', 0)} files")
                return True
            else:
                print(f"❌ File size test failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ File size test error: {str(e)}")
            return False
    
    def test_unicode_filenames(self):
        """Test with Unicode/Vietnamese filenames"""
        print("\n🔍 Testing Unicode Filenames...")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                with zipfile.ZipFile(temp_zip.name, 'w') as z:
                    img_data = self.create_test_image()
                    
                    # Vietnamese filenames
                    z.writestr('tài_liệu/giấy_chứng_nhận.jpg', img_data)
                    z.writestr('hồ_sơ/đơn_đăng_ký.jpg', img_data)
                    z.writestr('văn_bản/hợp_đồng_chuyển_nhượng.jpg', img_data)
                
                with open(temp_zip.name, 'rb') as f:
                    files = {'file': ('unicode_test.zip', f, 'application/zip')}
                    response = requests.post(f"{self.base_url}/scan-folder", files=files, timeout=120)
                
                os.unlink(temp_zip.name)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Unicode filenames test passed - processed {result.get('processed_files', 0)} files")
                return True
            else:
                print(f"❌ Unicode filenames test failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Unicode filenames test error: {str(e)}")
            return False
    
    def run_additional_tests(self):
        """Run all additional tests"""
        print("🚀 Running Additional Folder Scanning Tests")
        print("=" * 50)
        
        tests = [
            ("Large Folder Structure", self.test_large_folder_structure),
            ("Mixed File Types", self.test_mixed_file_types),
            ("File Size Limits", self.test_file_size_limits),
            ("Unicode Filenames", self.test_unicode_filenames)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} - Exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 ADDITIONAL TEST RESULTS")
        print("=" * 50)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📈 Additional Tests: {passed}/{total} passed")
        
        return passed == total

def main():
    tester = AdditionalFolderTests()
    success = tester.run_additional_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())