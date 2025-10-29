#!/usr/bin/env python3
"""
List available Gemini models for your API key
"""

import sys
import requests

def list_gemini_models(api_key):
    """List all available models"""
    
    print("=" * 80)
    print("📋 LISTING AVAILABLE GEMINI MODELS")
    print("=" * 80)
    print()
    
    # List models endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            if 'models' in data:
                models = data['models']
                
                print(f"✅ Found {len(models)} models:")
                print()
                
                # Filter models that support generateContent
                generate_models = []
                
                for model in models:
                    name = model.get('name', '')
                    display_name = model.get('displayName', '')
                    supported_methods = model.get('supportedGenerationMethods', [])
                    
                    # Check if generateContent is supported
                    if 'generateContent' in supported_methods:
                        generate_models.append({
                            'name': name,
                            'display_name': display_name
                        })
                
                if generate_models:
                    print(f"🎯 Models supporting generateContent ({len(generate_models)}):")
                    print()
                    
                    for i, model in enumerate(generate_models, 1):
                        # Extract model ID from full name (models/gemini-xxx)
                        model_id = model['name'].replace('models/', '')
                        print(f"{i}. {model_id}")
                        print(f"   Display: {model['display_name']}")
                        print()
                    
                    print("=" * 80)
                    print("💡 RECOMMENDED MODEL TO USE:")
                    print("=" * 80)
                    print()
                    
                    # Find best model
                    flash_models = [m for m in generate_models if 'flash' in m['name'].lower()]
                    pro_models = [m for m in generate_models if 'pro' in m['name'].lower()]
                    
                    if flash_models:
                        best_model = flash_models[0]['name'].replace('models/', '')
                        print(f"🌟 RECOMMENDED: {best_model}")
                        print()
                        print("Reasons:")
                        print("- Fast (Flash model)")
                        print("- Cost-effective")
                        print("- Supports images")
                        print()
                        print(f"Update code to use: {best_model}")
                    elif pro_models:
                        best_model = pro_models[0]['name'].replace('models/', '')
                        print(f"⭐ ALTERNATIVE: {best_model}")
                        print()
                        print("Reasons:")
                        print("- More capable (Pro model)")
                        print("- Supports images")
                        print()
                        print(f"Update code to use: {best_model}")
                    else:
                        print("⚠️ No Flash or Pro models found")
                        print()
                        print("Try the first available model:")
                        if generate_models:
                            print(f"- {generate_models[0]['name'].replace('models/', '')}")
                
                else:
                    print("❌ No models support generateContent!")
                    print()
                    print("This might mean:")
                    print("1. Generative Language API not enabled")
                    print("2. API key doesn't have proper permissions")
                
                return True
            else:
                print("❌ No models found in response")
                print()
                print(f"Response: {data}")
                return False
                
        elif response.status_code == 403:
            print("❌ FORBIDDEN (403)")
            print()
            print("API chưa được enable!")
            print()
            print("Fix:")
            print("1. https://console.cloud.google.com/apis/library")
            print("2. Search: 'Generative Language API'")
            print("3. Click 'ENABLE'")
            print()
            return False
            
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED (401)")
            print()
            print("API key không hợp lệ!")
            print()
            print("Fix:")
            print("1. https://console.cloud.google.com/apis/credentials")
            print("2. Tạo API key mới")
            print("3. Copy lại")
            print()
            return False
            
        else:
            print(f"❌ ERROR ({response.status_code})")
            print()
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python list_gemini_models.py <YOUR_API_KEY>")
        print()
        print("This will show all available Gemini models for your API key")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    success = list_gemini_models(api_key)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
