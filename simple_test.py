#!/usr/bin/env python3
"""
Simple test for the review request requirements
"""

import requests
import json

def test_llm_health():
    """Test LLM health endpoint"""
    print("🔍 Testing LLM Health")
    
    try:
        response = requests.get(
            "https://docsort-pro.preview.emergentagent.com/api/llm/health", 
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ['status', 'provider', 'openai_available', 'emergent_available']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            
            status = data.get('status')
            if status in ['healthy', 'degraded', 'unhealthy']:
                print(f"✅ LLM Health Check PASSED - Status: {status}")
                return True
            else:
                print(f"❌ Invalid status: {status}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_endpoints_exist():
    """Test if the required endpoints exist"""
    print("\n🔍 Testing Endpoint Existence")
    
    endpoints = [
        "setup-admin",
        "auth/login", 
        "scan-folder-direct",
        "scan-folder"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            # Use HEAD request to check if endpoint exists without processing
            response = requests.head(
                f"https://docsort-pro.preview.emergentagent.com/api/{endpoint}",
                timeout=10
            )
            
            # 405 Method Not Allowed means endpoint exists but doesn't support HEAD
            # 401 Unauthorized means endpoint exists but requires auth
            # 422 Unprocessable Entity means endpoint exists but missing required data
            if response.status_code in [200, 401, 405, 422]:
                results[endpoint] = "✅ EXISTS"
            elif response.status_code == 404:
                results[endpoint] = "❌ NOT FOUND"
            else:
                results[endpoint] = f"? STATUS {response.status_code}"
                
        except Exception as e:
            results[endpoint] = f"❌ ERROR: {e}"
    
    for endpoint, result in results.items():
        print(f"  {endpoint}: {result}")
    
    # Check if key endpoints exist
    key_endpoints = ["scan-folder-direct", "scan-folder"]
    existing_key_endpoints = [ep for ep in key_endpoints if "EXISTS" in results.get(ep, "")]
    
    if len(existing_key_endpoints) == len(key_endpoints):
        print("✅ All key endpoints exist")
        return True
    else:
        print(f"❌ Missing key endpoints: {set(key_endpoints) - set(existing_key_endpoints)}")
        return False

def main():
    print("🚀 Simple Review Test")
    print("=" * 40)
    
    # Test 1: LLM Health
    health_result = test_llm_health()
    
    # Test 2: Endpoint existence
    endpoints_result = test_endpoints_exist()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 RESULTS")
    print("=" * 40)
    
    tests = [
        ("LLM Health Check", health_result),
        ("Required Endpoints", endpoints_result)
    ]
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    exit(0 if main() else 1)