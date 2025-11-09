#!/usr/bin/env python3
"""
LLM Health and Scan Testing Script
Tests the specific requirements from the review request:
1. LLM health endpoint
2. Auth + scan flow 
3. Rules endpoint sanity check
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import sys

class LLMHealthTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://landoc-scanner-1.preview.emergentagent.com/api"
        self.token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append((test_name, success, details))
        
    def create_test_image(self):
        """Create a small test PNG image"""
        # Create a simple 100x100 white image with some text-like pattern
        img = Image.new('RGB', (100, 100), color='white')
        
        # Add some simple patterns to make it look like a document
        pixels = img.load()
        for i in range(10, 90):
            for j in range(20, 30):
                pixels[i, j] = (0, 0, 0)  # Black line
        for i in range(10, 90):
            for j in range(40, 50):
                pixels[i, j] = (0, 0, 0)  # Another black line
                
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    def test_llm_health(self):
        """Test 1: LLM Health endpoint"""
        print("\n🔍 Testing LLM Health Endpoint...")
        
        try:
            url = f"{self.base_url}/llm/health"
            response = requests.get(url)
            
            print(f"   URL: {url}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                # Check required fields
                required_fields = ['status', 'openai_available', 'provider', 'model']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("LLM Health - Required Fields", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values based on environment
                expected_status = "healthy"  # Since OPENAI_API_KEY is present
                expected_openai = True
                expected_provider = "openai"
                expected_model = "gpt-4o-mini"
                
                checks = [
                    (data.get('status') == expected_status, f"status: expected '{expected_status}', got '{data.get('status')}'"),
                    (data.get('openai_available') == expected_openai, f"openai_available: expected {expected_openai}, got {data.get('openai_available')}"),
                    (data.get('provider') == expected_provider, f"provider: expected '{expected_provider}', got '{data.get('provider')}'"),
                    (data.get('model') == expected_model, f"model: expected '{expected_model}', got '{data.get('model')}'")
                ]
                
                all_passed = True
                for check_passed, check_msg in checks:
                    if not check_passed:
                        print(f"   ❌ {check_msg}")
                        all_passed = False
                    else:
                        print(f"   ✅ {check_msg}")
                
                self.log_result("LLM Health Endpoint", all_passed, f"Status: {data.get('status')}, OpenAI: {data.get('openai_available')}")
                return all_passed
            else:
                self.log_result("LLM Health Endpoint", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("LLM Health Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_setup_admin(self):
        """Test 2a: Setup admin user"""
        print("\n🔍 Testing Admin Setup...")
        
        try:
            url = f"{self.base_url}/setup-admin"
            response = requests.get(url)
            
            print(f"   URL: {url}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                self.log_result("Admin Setup", True, "Admin user ensured")
                return True
            else:
                self.log_result("Admin Setup", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Admin Setup", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_login(self):
        """Test 2b: Authentication login"""
        print("\n🔍 Testing Authentication Login...")
        
        try:
            url = f"{self.base_url}/auth/login"
            login_data = {
                "username": "admin",
                "password": "Thommit@19"
            }
            
            response = requests.post(url, json=login_data)
            
            print(f"   URL: {url}")
            print(f"   Login Data: {login_data}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                # Extract token
                self.token = data.get('access_token')
                if self.token:
                    print(f"   ✅ Token extracted: {self.token[:20]}...")
                    self.log_result("Authentication Login", True, "Token obtained successfully")
                    return True
                else:
                    self.log_result("Authentication Login", False, "No access_token in response")
                    return False
            else:
                self.log_result("Authentication Login", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Login", False, f"Exception: {str(e)}")
            return False
    
    def test_scan_document(self):
        """Test 2c: Document scan with authentication"""
        print("\n🔍 Testing Document Scan with Auth...")
        
        if not self.token:
            self.log_result("Document Scan", False, "No authentication token available")
            return False
        
        try:
            url = f"{self.base_url}/scan-document"
            
            # Create test image
            image_data = self.create_test_image()
            
            # Prepare file upload
            files = {
                'file': ('test_document.png', image_data, 'image/png')
            }
            
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            response = requests.post(url, files=files, headers=headers)
            
            print(f"   URL: {url}")
            print(f"   File: test_document.png ({len(image_data)} bytes)")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response fields: {list(data.keys())}")
                
                # Check required fields
                required_fields = ['detected_full_name', 'short_code', 'confidence_score']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Document Scan", False, f"Missing fields: {missing_fields}")
                    return False
                
                detected_name = data.get('detected_full_name', '')
                short_code = data.get('short_code', '')
                confidence = data.get('confidence_score', 0)
                
                print(f"   ✅ Detected: {detected_name}")
                print(f"   ✅ Short Code: {short_code}")
                print(f"   ✅ Confidence: {confidence}")
                
                self.log_result("Document Scan", True, f"Detected: {short_code} (confidence: {confidence})")
                return True
            else:
                self.log_result("Document Scan", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Document Scan", False, f"Exception: {str(e)}")
            return False
    
    def test_rules_endpoint(self):
        """Test 3: Rules endpoint sanity check"""
        print("\n🔍 Testing Rules Endpoint...")
        
        try:
            url = f"{self.base_url}/rules"
            response = requests.get(url)
            
            print(f"   URL: {url}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ Rules count: {len(data)}")
                    
                    # Check first rule structure
                    if data:
                        first_rule = data[0]
                        required_fields = ['id', 'full_name', 'short_code']
                        missing_fields = [field for field in required_fields if field not in first_rule]
                        
                        if missing_fields:
                            self.log_result("Rules Endpoint", False, f"Missing fields in rule: {missing_fields}")
                            return False
                        
                        print(f"   ✅ Sample rule: {first_rule.get('full_name')} -> {first_rule.get('short_code')}")
                    
                    self.log_result("Rules Endpoint", True, f"Retrieved {len(data)} rules successfully")
                    return True
                else:
                    self.log_result("Rules Endpoint", False, "Empty or invalid rules array")
                    return False
            else:
                self.log_result("Rules Endpoint", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Rules Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting LLM Health and Scan Testing")
        print("=" * 60)
        
        # Test 1: Health endpoint
        health_ok = self.test_llm_health()
        
        # Test 2: Auth + scan flow
        admin_ok = self.test_setup_admin()
        login_ok = self.test_auth_login() if admin_ok else False
        scan_ok = self.test_scan_document() if login_ok else False
        
        # Test 3: Rules endpoint
        rules_ok = self.test_rules_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if details and not success:
                print(f"     {details}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        # Report failures with status codes and bodies
        failures = [(name, details) for name, success, details in self.test_results if not success]
        if failures:
            print("\n❌ FAILURES REPORT:")
            for name, details in failures:
                print(f"   • {name}: {details}")
        
        return passed_tests == total_tests

def main():
    tester = LLMHealthTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())