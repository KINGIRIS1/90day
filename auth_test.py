#!/usr/bin/env python3
"""
Test authentication setup
"""

import requests
import json

def test_auth():
    base_url = "https://viet-ocr-scan.preview.emergentagent.com/api"
    
    print("🔍 Testing setup-admin endpoint")
    
    try:
        response = requests.get(f"{base_url}/setup-admin", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Setup data: {json.dumps(data, indent=2)}")
            
            # Try login with returned credentials
            username = data.get('username', 'admin')
            password = data.get('password', 'admin123')
            
            print(f"\n🔍 Testing login with username: {username}, password: {password}")
            
            login_response = requests.post(f"{base_url}/auth/login", json={
                'username': username,
                'password': password
            }, timeout=10)
            
            print(f"Login status: {login_response.status_code}")
            print(f"Login response: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth()