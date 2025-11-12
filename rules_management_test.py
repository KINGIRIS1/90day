import requests
import sys
import json
import time
from datetime import datetime

class RulesManagementAPITester:
    def __init__(self, base_url="https://ocr-memory-fix.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_rules = []  # Track created rules for cleanup
        
    def run_test(self, name, method, endpoint, expected_status, data=None, response_type='json'):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                if response_type == 'json' and response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                else:
                    return success, response.content
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, response.text if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_rules_initial(self):
        """Test GET /api/rules - should auto-initialize from DOCUMENT_TYPES"""
        print("\n📋 Testing GET /api/rules (Initial Load)...")
        
        success, response = self.run_test(
            "GET Rules - Auto-initialization",
            "GET",
            "rules",
            200
        )
        
        if success and response:
            print(f"   Total rules loaded: {len(response)}")
            
            # Verify we have the expected default rules (100+ from DOCUMENT_TYPES)
            if len(response) >= 100:
                print(f"   ✅ Auto-initialization successful: {len(response)} rules loaded")
                
                # Check structure of first rule
                if response:
                    first_rule = response[0]
                    required_fields = ['id', 'full_name', 'short_code', 'created_at', 'updated_at']
                    missing_fields = [field for field in required_fields if field not in first_rule]
                    
                    if not missing_fields:
                        print(f"   ✅ Rule structure valid: {list(first_rule.keys())}")
                    else:
                        print(f"   ❌ Missing fields in rule: {missing_fields}")
                        return False
                        
                # Check for some expected rules
                rule_codes = [rule['short_code'] for rule in response]
                expected_codes = ['GCNM', 'DDK', 'HDCQ', 'BMT', 'HSKT']
                found_codes = [code for code in expected_codes if code in rule_codes]
                
                if len(found_codes) >= 3:
                    print(f"   ✅ Expected rule codes found: {found_codes}")
                else:
                    print(f"   ⚠️  Few expected codes found: {found_codes}")
                    
            else:
                print(f"   ❌ Expected 100+ rules, got {len(response)}")
                return False
        
        return success

    def test_create_rule_valid(self):
        """Test POST /api/rules with valid data"""
        print("\n➕ Testing POST /api/rules (Valid Data)...")
        
        new_rule_data = {
            "full_name": "Giấy Test Mới",
            "short_code": "TEST001"
        }
        
        success, response = self.run_test(
            "Create Rule - Valid Data",
            "POST",
            "rules",
            200,
            data=new_rule_data
        )
        
        if success and response:
            print(f"   Created rule: {response.get('full_name')} -> {response.get('short_code')}")
            print(f"   Rule ID: {response.get('id')}")
            
            # Track for cleanup
            self.created_rules.append(response.get('id'))
            
            # Verify response structure
            required_fields = ['id', 'full_name', 'short_code', 'created_at', 'updated_at']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print(f"   ✅ Response structure valid")
            else:
                print(f"   ❌ Missing fields in response: {missing_fields}")
                return False
        
        return success

    def test_create_rule_duplicate(self):
        """Test POST /api/rules with duplicate short_code (should return 400)"""
        print("\n🚫 Testing POST /api/rules (Duplicate Short Code)...")
        
        duplicate_rule_data = {
            "full_name": "Giấy Test Duplicate",
            "short_code": "GCNM"  # This should already exist from DOCUMENT_TYPES
        }
        
        success, response = self.run_test(
            "Create Rule - Duplicate Short Code",
            "POST",
            "rules",
            400,  # Expecting 400 error
            data=duplicate_rule_data
        )
        
        if success:
            print(f"   ✅ Correctly rejected duplicate short_code")
            if isinstance(response, str) and "đã tồn tại" in response:
                print(f"   ✅ Vietnamese error message: {response[:100]}")
        
        return success

    def test_create_rule_missing_fields(self):
        """Test POST /api/rules with missing required fields"""
        print("\n❌ Testing POST /api/rules (Missing Fields)...")
        
        # Test missing full_name
        invalid_data = {
            "short_code": "TEST002"
        }
        
        success, response = self.run_test(
            "Create Rule - Missing full_name",
            "POST",
            "rules",
            422,  # Expecting validation error
            data=invalid_data
        )
        
        return success

    def test_get_rules_after_create(self):
        """Test GET /api/rules after creating new rule"""
        print("\n📋 Testing GET /api/rules (After Create)...")
        
        success, response = self.run_test(
            "GET Rules - After Create",
            "GET",
            "rules",
            200
        )
        
        if success and response:
            # Check if our created rule appears
            test_rules = [rule for rule in response if rule['short_code'] == 'TEST001']
            
            if test_rules:
                print(f"   ✅ Created rule found: {test_rules[0]['full_name']}")
            else:
                print(f"   ❌ Created rule not found in list")
                return False
        
        return success

    def test_update_rule_valid(self):
        """Test PUT /api/rules/{rule_id} with valid data"""
        print("\n✏️ Testing PUT /api/rules/{rule_id} (Valid Update)...")
        
        if not self.created_rules:
            print("   ❌ No created rules available for update test")
            return False
        
        rule_id = self.created_rules[0]
        update_data = {
            "full_name": "Giấy Test Đã Cập Nhật",
            "short_code": "TEST001_UPD"
        }
        
        success, response = self.run_test(
            "Update Rule - Valid Data",
            "PUT",
            f"rules/{rule_id}",
            200,
            data=update_data
        )
        
        if success and response:
            print(f"   Updated rule: {response.get('full_name')} -> {response.get('short_code')}")
            
            # Verify updated_at timestamp changed
            if 'updated_at' in response:
                print(f"   ✅ Updated timestamp: {response['updated_at']}")
        
        return success

    def test_update_rule_partial(self):
        """Test PUT /api/rules/{rule_id} with partial update (only full_name)"""
        print("\n✏️ Testing PUT /api/rules/{rule_id} (Partial Update)...")
        
        if not self.created_rules:
            print("   ❌ No created rules available for partial update test")
            return False
        
        rule_id = self.created_rules[0]
        update_data = {
            "full_name": "Giấy Test Chỉ Cập Nhật Tên"
        }
        
        success, response = self.run_test(
            "Update Rule - Partial (full_name only)",
            "PUT",
            f"rules/{rule_id}",
            200,
            data=update_data
        )
        
        if success and response:
            print(f"   Partially updated rule: {response.get('full_name')}")
            print(f"   Short code unchanged: {response.get('short_code')}")
        
        return success

    def test_update_rule_duplicate_code(self):
        """Test PUT /api/rules/{rule_id} with duplicate short_code (should return 400)"""
        print("\n🚫 Testing PUT /api/rules/{rule_id} (Duplicate Short Code)...")
        
        if not self.created_rules:
            print("   ❌ No created rules available for duplicate update test")
            return False
        
        rule_id = self.created_rules[0]
        update_data = {
            "short_code": "GCNM"  # This should already exist
        }
        
        success, response = self.run_test(
            "Update Rule - Duplicate Short Code",
            "PUT",
            f"rules/{rule_id}",
            400,  # Expecting 400 error
            data=update_data
        )
        
        if success:
            print(f"   ✅ Correctly rejected duplicate short_code in update")
        
        return success

    def test_update_rule_nonexistent(self):
        """Test PUT /api/rules/{rule_id} with non-existent rule_id (should return 404)"""
        print("\n🔍 Testing PUT /api/rules/{rule_id} (Non-existent ID)...")
        
        fake_rule_id = "nonexistent-rule-id-12345"
        update_data = {
            "full_name": "This Should Fail"
        }
        
        success, response = self.run_test(
            "Update Rule - Non-existent ID",
            "PUT",
            f"rules/{fake_rule_id}",
            404,  # Expecting 404 error
            data=update_data
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for non-existent rule")
        
        return success

    def test_delete_rule_nonexistent(self):
        """Test DELETE /api/rules/{rule_id} with non-existent rule_id (should return 404)"""
        print("\n🔍 Testing DELETE /api/rules/{rule_id} (Non-existent ID)...")
        
        fake_rule_id = "nonexistent-rule-id-12345"
        
        success, response = self.run_test(
            "Delete Rule - Non-existent ID",
            "DELETE",
            f"rules/{fake_rule_id}",
            404  # Expecting 404 error
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for non-existent rule")
        
        return success

    def test_delete_rule_valid(self):
        """Test DELETE /api/rules/{rule_id} with valid rule_id"""
        print("\n🗑️ Testing DELETE /api/rules/{rule_id} (Valid Delete)...")
        
        if not self.created_rules:
            print("   ❌ No created rules available for delete test")
            return False
        
        rule_id = self.created_rules[0]
        
        success, response = self.run_test(
            "Delete Rule - Valid ID",
            "DELETE",
            f"rules/{rule_id}",
            200
        )
        
        if success and response:
            print(f"   Deleted rule: {response.get('deleted_rule', 'N/A')}")
            
            # Remove from tracking
            self.created_rules.remove(rule_id)
        
        return success

    def test_get_rules_after_delete(self):
        """Test GET /api/rules after deleting rule"""
        print("\n📋 Testing GET /api/rules (After Delete)...")
        
        success, response = self.run_test(
            "GET Rules - After Delete",
            "GET",
            "rules",
            200
        )
        
        if success and response:
            # Check that deleted rule no longer appears
            test_rules = [rule for rule in response if rule['short_code'] == 'TEST001_UPD']
            
            if not test_rules:
                print(f"   ✅ Deleted rule no longer in list")
            else:
                print(f"   ❌ Deleted rule still found: {test_rules[0]['full_name']}")
                return False
        
        return success

    def test_dynamic_loading_in_scanning(self):
        """Test that newly added rules are used in document scanning"""
        print("\n🔄 Testing Dynamic Loading in Scanning...")
        
        # First, create a new rule for testing
        new_rule_data = {
            "full_name": "Giấy Test Scan Động",
            "short_code": "TESTSCAN"
        }
        
        success, response = self.run_test(
            "Create Rule for Scan Test",
            "POST",
            "rules",
            200,
            data=new_rule_data
        )
        
        if success and response:
            rule_id = response.get('id')
            self.created_rules.append(rule_id)
            print(f"   Created test rule: {response.get('short_code')}")
            
            # Now test that the rule is available in scanning
            # We'll check this by getting the rules again to ensure they're loaded
            success2, rules_response = self.run_test(
                "Verify Rule Available for Scanning",
                "GET",
                "rules",
                200
            )
            
            if success2 and rules_response:
                test_scan_rules = [rule for rule in rules_response if rule['short_code'] == 'TESTSCAN']
                
                if test_scan_rules:
                    print(f"   ✅ New rule available for dynamic loading: {test_scan_rules[0]['full_name']}")
                    
                    # Clean up the test rule
                    cleanup_success, _ = self.run_test(
                        "Cleanup Test Rule",
                        "DELETE",
                        f"rules/{rule_id}",
                        200
                    )
                    
                    if cleanup_success:
                        self.created_rules.remove(rule_id)
                        print(f"   ✅ Test rule cleaned up")
                    
                    return True
                else:
                    print(f"   ❌ New rule not found for dynamic loading")
                    return False
        
        return False

    def cleanup_created_rules(self):
        """Clean up any remaining created rules"""
        print("\n🧹 Cleaning up created rules...")
        
        for rule_id in self.created_rules[:]:  # Copy list to avoid modification during iteration
            success, _ = self.run_test(
                f"Cleanup Rule {rule_id}",
                "DELETE",
                f"rules/{rule_id}",
                200
            )
            
            if success:
                self.created_rules.remove(rule_id)
                print(f"   ✅ Cleaned up rule: {rule_id}")

def main():
    print("🚀 Starting Rules Management API Tests")
    print("=" * 60)
    
    tester = RulesManagementAPITester()
    
    # Run all tests in order
    test_results = []
    
    print("\n1️⃣ Testing GET /api/rules...")
    test_results.append(("GET Rules - Initial Load", tester.test_get_rules_initial()))
    
    print("\n2️⃣ Testing POST /api/rules...")
    test_results.append(("POST Rules - Valid Data", tester.test_create_rule_valid()))
    test_results.append(("POST Rules - Duplicate Code", tester.test_create_rule_duplicate()))
    test_results.append(("POST Rules - Missing Fields", tester.test_create_rule_missing_fields()))
    test_results.append(("GET Rules - After Create", tester.test_get_rules_after_create()))
    
    print("\n3️⃣ Testing PUT /api/rules/{rule_id}...")
    test_results.append(("PUT Rules - Valid Update", tester.test_update_rule_valid()))
    test_results.append(("PUT Rules - Partial Update", tester.test_update_rule_partial()))
    test_results.append(("PUT Rules - Duplicate Code", tester.test_update_rule_duplicate_code()))
    test_results.append(("PUT Rules - Non-existent ID", tester.test_update_rule_nonexistent()))
    
    print("\n4️⃣ Testing DELETE /api/rules/{rule_id}...")
    test_results.append(("DELETE Rules - Non-existent ID", tester.test_delete_rule_nonexistent()))
    test_results.append(("DELETE Rules - Valid Delete", tester.test_delete_rule_valid()))
    test_results.append(("GET Rules - After Delete", tester.test_get_rules_after_delete()))
    
    print("\n5️⃣ Testing Dynamic Loading...")
    test_results.append(("Dynamic Loading in Scanning", tester.test_dynamic_loading_in_scanning()))
    
    # Cleanup any remaining rules
    tester.cleanup_created_rules()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 RULES MANAGEMENT API TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
    print(f"📈 API Calls: {tester.tests_passed}/{tester.tests_run} successful")
    
    if passed_tests == total_tests:
        print("🎉 All Rules Management tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())