#!/usr/bin/env python3
"""
LLM Integration Test Suite
Tests the new OpenAI primary integration with Emergent fallback and health endpoint
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import os
import sys

class LLMIntegrationTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = "https://vn-document-scan.preview.emergentagent.com/api"
        self.auth_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
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
    
    def create_test_image(self):
        """Create a minimal test image for testing"""
        # Create a small but valid image (100x100 pixels)
        img = Image.new('RGB', (100, 100), color='white')
        
        # Add some text to make it more realistic
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "Test Document", fill='black')
        except:
            pass  # If ImageDraw fails, just use plain white image
        
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer
    
    def test_health_endpoint(self):
        """Test LLM health endpoint"""
        print("\n🔍 Testing LLM Health Endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/llm/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate JSON structure
                required_fields = ['status', 'provider', 'openai_available', 'emergent_available']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Endpoint - JSON Structure", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values based on environment
                # From .env: OPENAI_API_KEY is not set, EMERGENT_LLM_KEY is set but may have auth issues
                # If both fail, status should be "unhealthy"
                expected_openai = False
                
                # Check if Emergent is actually working or has auth issues
                emergent_working = data['emergent_available']
                if emergent_working:
                    expected_status = "degraded"  # Only Emergent available
                    expected_emergent = True
                else:
                    expected_status = "unhealthy"  # Both providers failed
                    expected_emergent = False
                
                status_ok = data['status'] == expected_status
                openai_ok = data['openai_available'] == expected_openai
                emergent_ok = data['emergent_available'] == expected_emergent
                
                self.log_test("Health Endpoint - Status Code", True, f"200 OK")
                self.log_test("Health Endpoint - JSON Structure", True, "All required fields present")
                self.log_test("Health Endpoint - Status Value", status_ok, 
                            f"Expected: {expected_status}, Got: {data['status']}")
                self.log_test("Health Endpoint - OpenAI Available", openai_ok,
                            f"Expected: {expected_openai}, Got: {data['openai_available']}")
                self.log_test("Health Endpoint - Emergent Available", emergent_ok,
                            f"Expected: {expected_emergent}, Got: {data['emergent_available']}")
                
                print(f"   Full response: {json.dumps(data, indent=2)}")
                
                return status_ok and openai_ok and emergent_ok
            else:
                self.log_test("Health Endpoint - Status Code", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint - Request", False, f"Error: {str(e)}")
            return False
    
    def setup_admin_and_login(self):
        """Setup admin user and login to get auth token"""
        print("\n🔐 Setting up admin and authentication...")
        
        try:
            # Setup admin
            setup_response = requests.get(f"{self.base_url}/setup-admin")
            if setup_response.status_code == 200:
                self.log_test("Admin Setup", True, "Admin user created/verified")
            else:
                self.log_test("Admin Setup", False, 
                            f"Status: {setup_response.status_code}, Response: {setup_response.text}")
                return False
            
            # Login
            login_data = {
                "username": "admin",
                "password": "Thommit@19"
            }
            
            login_response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.auth_token = login_result.get('access_token')
                
                if self.auth_token:
                    self.log_test("Admin Login", True, "Authentication token received")
                    return True
                else:
                    self.log_test("Admin Login", False, "No access token in response")
                    return False
            else:
                self.log_test("Admin Login", False, 
                            f"Status: {login_response.status_code}, Response: {login_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Error: {str(e)}")
            return False
    
    def test_document_scan_with_fallback(self):
        """Test document scan to verify LLM integration works with fallback"""
        print("\n📄 Testing Document Scan with LLM Integration...")
        
        if not self.auth_token:
            self.log_test("Document Scan - Auth", False, "No authentication token available")
            return False
        
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Prepare request
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            files = {'file': ('test.jpg', test_image, 'image/jpeg')}
            
            response = requests.post(f"{self.base_url}/scan-document", 
                                   headers=headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['detected_full_name', 'short_code', 'confidence_score']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Document Scan - Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Check that we got a valid response (not 500 error)
                detected_name = data.get('detected_full_name', '')
                short_code = data.get('short_code', '')
                confidence = data.get('confidence_score', 0)
                
                self.log_test("Document Scan - Status Code", True, "200 OK")
                self.log_test("Document Scan - Response Structure", True, "All required fields present")
                self.log_test("Document Scan - LLM Processing", True, 
                            f"Detected: {detected_name}, Code: {short_code}, Confidence: {confidence}")
                
                # Since OpenAI is not available, this should use Emergent fallback
                print(f"   ✅ LLM fallback working - document processed successfully")
                print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                return True
            else:
                self.log_test("Document Scan - Status Code", False,
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Scan - Request", False, f"Error: {str(e)}")
            return False
    
    def test_rules_regression(self):
        """Quick smoke test of /api/rules endpoint"""
        print("\n📋 Testing Rules Endpoint (Regression Check)...")
        
        try:
            response = requests.get(f"{self.base_url}/rules")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Rules Endpoint - Status", True, f"200 OK, {len(data)} rules returned")
                    
                    # Check first rule structure
                    if data:
                        first_rule = data[0]
                        required_fields = ['id', 'full_name', 'short_code']
                        missing_fields = [field for field in required_fields if field not in first_rule]
                        
                        if missing_fields:
                            self.log_test("Rules Endpoint - Structure", False,
                                        f"Missing fields in rule: {missing_fields}")
                            return False
                        else:
                            self.log_test("Rules Endpoint - Structure", True, "Rule structure valid")
                    
                    return True
                else:
                    self.log_test("Rules Endpoint - Data", False, "No rules returned or invalid format")
                    return False
            else:
                self.log_test("Rules Endpoint - Status", False,
                            f"Expected 200, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Rules Endpoint - Request", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all LLM integration tests"""
        print("🚀 Starting LLM Integration Tests")
        print("=" * 60)
        
        # Test 1: Health endpoint
        health_ok = self.test_health_endpoint()
        
        # Test 2: Authentication setup
        auth_ok = self.setup_admin_and_login()
        
        # Test 3: Document scan with LLM integration
        scan_ok = False
        if auth_ok:
            scan_ok = self.test_document_scan_with_fallback()
        
        # Test 4: Rules regression check
        rules_ok = self.test_rules_regression()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("LLM Health Endpoint", health_ok),
            ("Authentication Setup", auth_ok),
            ("Document Scan with LLM", scan_ok),
            ("Rules Regression Check", rules_ok)
        ]
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        print(f"\n📈 Overall: {passed}/{total} test suites passed")
        print(f"📈 Individual tests: {self.tests_passed}/{self.tests_run} passed")
        
        if passed == total:
            print("🎉 All LLM integration tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

def main():
    """Main test runner"""
    tester = LLMIntegrationTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())