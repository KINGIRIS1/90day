#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Computer Vision OCR Engine
Requires: pip install requests
"""

import sys
import os
import json
import time

def ocr_azure_computer_vision(image_path, api_key, endpoint, crop_top_percent=0.35):
    """
    Perform OCR using Azure Computer Vision API
    
    Args:
        image_path: Path to image file
        api_key: Azure Computer Vision API key
        endpoint: Azure endpoint URL (e.g., https://xxx.cognitiveservices.azure.com/)
        crop_top_percent: Percentage of top image to process (default 0.35 = 35%)
        
    Returns:
        tuple: (extracted_text, confidence_score, error)
    """
    try:
        import requests
        from PIL import Image
        import io
        
        # Normalize endpoint (remove trailing slash)
        endpoint = endpoint.rstrip('/')
        
        # Read and crop image to top portion
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Crop to top N% (default 35%)
            crop_height = int(height * crop_top_percent)
            cropped_img = img.crop((0, 0, width, crop_height))
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format=img.format or 'PNG')
            image_data = img_byte_arr.getvalue()
            
            print(f"🖼️ Image cropped: {width}x{height} → {width}x{crop_height} (top {int(crop_top_percent*100)}%)", file=sys.stderr)
        
        # Step 1: Submit read request
        read_url = f'{endpoint}/vision/v3.2/read/analyze'
        
        headers = {
            'Ocp-Apim-Subscription-Key': api_key,
            'Content-Type': 'application/octet-stream'
        }
        
        params = {
            'language': 'vi',  # Vietnamese
            'model-version': 'latest'
        }
        
        response = requests.post(read_url, headers=headers, params=params, data=image_data, timeout=30)
        
        if response.status_code != 202:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            return None, 0, f"Azure API error: {error_msg}"
        
        # Step 2: Get operation location
        operation_location = response.headers.get('Operation-Location')
        if not operation_location:
            return None, 0, "No Operation-Location header in response"
        
        # Step 3: Poll for results (max 10 seconds)
        max_retries = 20
        retry_delay = 0.5
        
        for i in range(max_retries):
            time.sleep(retry_delay)
            
            result_response = requests.get(
                operation_location,
                headers={'Ocp-Apim-Subscription-Key': api_key},
                timeout=10
            )
            
            if result_response.status_code != 200:
                continue
            
            result = result_response.json()
            status = result.get('status')
            
            if status == 'succeeded':
                # Extract text from results
                analyze_result = result.get('analyzeResult', {})
                read_results = analyze_result.get('readResults', [])
                
                all_text = []
                total_confidence = 0
                word_count = 0
                
                for page in read_results:
                    for line in page.get('lines', []):
                        all_text.append(line.get('text', ''))
                        
                        # Calculate average confidence
                        for word in line.get('words', []):
                            confidence = word.get('confidence', 0)
                            total_confidence += confidence
                            word_count += 1
                
                final_text = '\n'.join(all_text)
                avg_confidence = total_confidence / word_count if word_count > 0 else 0.9
                
                return final_text.strip(), avg_confidence, None
            
            elif status == 'failed':
                error_msg = result.get('analyzeResult', {}).get('errors', [{}])[0].get('message', 'Unknown error')
                return None, 0, f"Azure OCR failed: {error_msg}"
        
        return None, 0, "Azure OCR timeout (operation did not complete in time)"
        
    except ImportError:
        return None, 0, "Missing 'requests' library. Install: pip install requests"
    except FileNotFoundError:
        return None, 0, f"Image file not found: {image_path}"
    except Exception as e:
        return None, 0, f"Azure Computer Vision error: {str(e)}"


def main():
    if len(sys.argv) < 4:
        result = {
            'success': False,
            'error': 'Usage: ocr_engine_azure.py <image_path> <api_key> <endpoint>'
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    endpoint = sys.argv[3]
    
    # Perform OCR
    text, confidence, error = ocr_azure_computer_vision(image_path, api_key, endpoint)
    
    if error:
        result = {
            'success': False,
            'error': error,
            'text': '',
            'confidence': 0
        }
    else:
        result = {
            'success': True,
            'text': text or '',
            'confidence': float(confidence),
            'engine': 'azure_computer_vision'
        }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
