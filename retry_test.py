#!/usr/bin/env python3
"""
Test retry-scan endpoint functionality
"""

import requests
import json
from io import BytesIO

def test_retry_scan():
    base_url = "https://landoc-scanner-1.preview.emergentagent.com/api"
    
    print("🔍 Testing Retry Scan Endpoint")
    print("=" * 40)
    
    # First, create a scan that might fail or need retry
    test_image_url = "https://customer-assets.emergentagent.com/job_ef830caa-23a0-46b8-a003-8e3441b772e0/artifacts/77raup7h_20250318-03400001.jpg"
    
    try:
        # Download test image
        img_response = requests.get(test_image_url)
        if img_response.status_code != 200:
            print("❌ Failed to download test image")
            return False
        
        # Upload for scanning
        files = {'file': ('test_retry.jpg', BytesIO(img_response.content), 'image/jpeg')}
        scan_response = requests.post(f"{base_url}/scan-document", files=files)
        
        if scan_response.status_code != 200:
            print("❌ Failed to create initial scan")
            return False
        
        scan_result = scan_response.json()
        scan_id = scan_result.get('id')
        
        print(f"✅ Created scan with ID: {scan_id}")
        print(f"   Initial result: {scan_result.get('short_code')} (confidence: {scan_result.get('confidence_score', 0):.2f})")
        
        # Test retry endpoint (even if original scan was successful)
        retry_response = requests.post(f"{base_url}/retry-scan?scan_id={scan_id}")
        
        if retry_response.status_code == 200:
            retry_result = retry_response.json()
            print(f"✅ Retry successful")
            print(f"   Retry result: {retry_result.get('short_code')} (confidence: {retry_result.get('confidence', 0):.2f})")
            return True
        elif retry_response.status_code == 400:
            # This is expected if the document is not in error state
            print(f"✅ Retry endpoint working (document not in error state)")
            return True
        else:
            print(f"❌ Retry failed: {retry_response.status_code} - {retry_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing retry: {e}")
        return False

if __name__ == "__main__":
    success = test_retry_scan()
    exit(0 if success else 1)