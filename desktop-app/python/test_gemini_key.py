#!/usr/bin/env python3
"""
Test Gemini Flash API key validity
Quick verification script
"""

import sys
import requests
import json

def test_gemini_api_key(api_key):
    """Test if Gemini API key is valid"""
    
    print("=" * 80)
    print("🧪 TESTING GEMINI FLASH API KEY")
    print("=" * 80)
    print()
    
    # Test endpoint - v1beta is standard
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Simple test request
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello, this is a test. Please respond with: TEST OK"
            }]
        }]
    }
    
    print(f"📡 Testing endpoint: {url[:80]}...")
    print()
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                # Extract response text
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        response_text = parts[0]['text']
                        
                        print("✅ API KEY HỢP LỆ!")
                        print()
                        print(f"🤖 Gemini response: {response_text[:200]}")
                        print()
                        print("=" * 80)
                        print("🎉 CÓ THỂ SỬ DỤNG GEMINI FLASH!")
                        print("=" * 80)
                        print()
                        print("✅ API key đã được verify thành công")
                        print("✅ Gemini API đã được enable")
                        print("✅ Model: gemini-2.0-flash")
                        print("✅ Cost: $0.16/1,000 images")
                        print("✅ Free tier: 45,000 requests/tháng")
                        return True
            
            print("❌ Response không hợp lệ")
            print(f"Full response: {json.dumps(data, indent=2)}")
            return False
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST (400)")
            print()
            print("Có thể do:")
            print("1. API key format không đúng")
            print("2. Request payload không hợp lệ")
            print()
            print(f"Response: {response.text[:500]}")
            return False
            
        elif response.status_code == 403:
            print("❌ FORBIDDEN (403)")
            print()
            print("Nguyên nhân:")
            print("1. ❌ Generative Language API chưa được ENABLE")
            print("2. ❌ API key bị restrict (không cho phép Gemini API)")
            print("3. ❌ API key không có permission")
            print()
            print("Cách fix:")
            print("1. Vào: https://console.cloud.google.com/apis/library")
            print("2. Search: 'Generative Language API'")
            print("3. Đảm bảo status: ✅ ENABLED (màu xanh)")
            print("4. Nếu chưa enable: Click 'ENABLE' button")
            print()
            print(f"Response: {response.text[:500]}")
            return False
            
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED (401)")
            print()
            print("Nguyên nhân:")
            print("1. ❌ API key không hợp lệ")
            print("2. ❌ API key đã bị revoke")
            print("3. ❌ API key không đúng format")
            print()
            print("Cách fix:")
            print("1. Vào: https://console.cloud.google.com/apis/credentials")
            print("2. Tạo API key mới")
            print("3. Copy lại key (format: AIzaSy...)")
            print()
            print(f"Response: {response.text[:500]}")
            return False
            
        else:
            print(f"❌ ERROR ({response.status_code})")
            print()
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR")
        print()
        print("API request quá lâu (>10s)")
        print("Kiểm tra internet connection")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print()
        print("Không thể kết nối đến Gemini API")
        print("Kiểm tra:")
        print("1. Internet connection")
        print("2. Firewall settings")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_gemini_key.py <YOUR_API_KEY>")
        print()
        print("Example:")
        print("  python test_gemini_key.py AIzaSyABC123xyz789...")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Validate format
    if not api_key.startswith('AIza'):
        print("⚠️ WARNING: API key không bắt đầu bằng 'AIza'")
        print("Google API keys thường có format: AIzaSy...")
        print()
    
    success = test_gemini_api_key(api_key)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
