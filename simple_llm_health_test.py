#!/usr/bin/env python3
"""
Simple LLM Health Test - Focus on the specific review request
"""

import requests
import json

def test_llm_health():
    """Test the LLM health endpoint as requested in the review"""
    print("🔍 Testing LLM Health Endpoint")
    print("=" * 50)
    
    try:
        # Use the URL from frontend .env
        url = "https://docusmart-vn.preview.emergentagent.com/api/llm/health"
        print(f"Calling: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n📊 LLM Health Response:")
            print(json.dumps(data, indent=2))
            
            # Extract key information
            status = data.get('status', 'unknown')
            provider = data.get('provider', 'unknown')
            model = data.get('model', 'unknown')
            openai_available = data.get('openai_available', False)
            emergent_available = data.get('emergent_available', False)
            details = data.get('details', 'No details')
            
            print(f"\n🎯 Key Information:")
            print(f"Status: {status}")
            print(f"Provider: {provider}")
            print(f"Model: {model}")
            print(f"OpenAI Available: {openai_available}")
            print(f"Emergent Available: {emergent_available}")
            print(f"Details: {details}")
            
            # Analysis based on review request expectations
            print(f"\n📋 Analysis:")
            
            if status == "healthy" and openai_available:
                print("✅ EXPECTED: OpenAI is working - system is healthy")
                result = "SUCCESS"
            elif status == "degraded" and not openai_available and emergent_available:
                print("✅ EXPECTED: OpenAI rate-limited, Emergent working - degraded mode")
                result = "SUCCESS"
            elif status == "unhealthy" and not openai_available and not emergent_available:
                print("❌ BOTH PROVIDERS DOWN: System is unhealthy")
                result = "BOTH_DOWN"
            else:
                print("⚠️  UNEXPECTED STATUS COMBINATION")
                result = "UNEXPECTED"
            
            # Check for specific error patterns
            if "429" in details or "Rate limit" in details:
                print("📊 Rate limit detected in OpenAI")
            if "401" in details or "unauthorized" in details or "AuthenticationError" in details:
                print("🔑 Authentication error detected")
            
            return True, data, result
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, {}, "HTTP_ERROR"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, {}, "EXCEPTION"

def main():
    print("🚀 Simple LLM Health Test")
    print("Focus: Re-checking after EMERGENT_LLM_KEY update")
    print("=" * 60)
    
    success, data, result = test_llm_health()
    
    print(f"\n" + "=" * 60)
    print("🎯 FINAL RESULT")
    print("=" * 60)
    
    if success:
        print("✅ LLM Health endpoint is accessible")
        print(f"Result: {result}")
        
        if result == "SUCCESS":
            print("🎉 System is working as expected!")
        elif result == "BOTH_DOWN":
            print("❌ Both LLM providers are down")
        elif result == "UNEXPECTED":
            print("⚠️  Unexpected status combination")
            
        return 0
    else:
        print("❌ Failed to access LLM Health endpoint")
        return 1

if __name__ == "__main__":
    exit(main())