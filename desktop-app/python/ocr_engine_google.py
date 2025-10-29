#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Cloud Vision OCR Engine
Requires: pip install google-cloud-vision
"""

import sys
import os
import base64
import json
from pathlib import Path

def ocr_google_cloud_vision(image_path, api_key, crop_top_percent=0.35):
    """
    Perform OCR using Google Cloud Vision API with API key authentication
    
    Args:
        image_path: Path to image file
        api_key: Google Cloud Vision API key
        crop_top_percent: Percentage of top image to process (default 0.35 = 35%)
        
    Returns:
        tuple: (extracted_text, confidence_score)
    """
    try:
        import requests
        from PIL import Image
        import io
        
        # Read and crop image to top portion (where title/header usually is)
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Crop to top N% (default 35%)
            crop_height = int(height * crop_top_percent)
            cropped_img = img.crop((0, 0, width, crop_height))
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format=img.format or 'PNG')
            image_content = img_byte_arr.getvalue()
            
            print(f"🖼️ Image cropped: {width}x{height} → {width}x{crop_height} (top {int(crop_top_percent*100)}%)", file=sys.stderr)
        
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        # Prepare request
        url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
        
        payload = {
            'requests': [{
                'image': {
                    'content': encoded_image
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }],
                'imageContext': {
                    'languageHints': ['vi', 'en']  # Vietnamese and English
                }
            }]
        }
        
        # Make API call
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            return None, 0, f"Google Cloud Vision API error: {error_msg}"
        
        result = response.json()
        
        # Extract text
        if 'responses' in result and len(result['responses']) > 0:
            annotations = result['responses'][0]
            
            if 'fullTextAnnotation' in annotations:
                text = annotations['fullTextAnnotation']['text']
                
                # Calculate average confidence from pages
                total_confidence = 0
                word_count = 0
                
                for page in annotations['fullTextAnnotation'].get('pages', []):
                    for block in page.get('blocks', []):
                        for paragraph in block.get('paragraphs', []):
                            for word in paragraph.get('words', []):
                                confidence = word.get('confidence', 0)
                                total_confidence += confidence
                                word_count += 1
                
                avg_confidence = total_confidence / word_count if word_count > 0 else 0.9
                
                return text.strip(), avg_confidence, None
            
            elif 'textAnnotations' in annotations and len(annotations['textAnnotations']) > 0:
                # Fallback to textAnnotations
                text = annotations['textAnnotations'][0]['description']
                return text.strip(), 0.9, None  # Default confidence
        
        return None, 0, "No text detected in image"
        
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
        return None, 0, f"Missing library: {missing_lib}. Install: pip install {missing_lib}"
    except FileNotFoundError:
        return None, 0, f"Image file not found: {image_path}"
    except Exception as e:
        return None, 0, f"Google Cloud Vision error: {str(e)}"


def main():
    if len(sys.argv) < 3:
        result = {
            'success': False,
            'error': 'Usage: ocr_engine_google.py <image_path> <api_key>'
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    
    # Perform OCR
    text, confidence, error = ocr_google_cloud_vision(image_path, api_key)
    
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
            'engine': 'google_cloud_vision'
        }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
