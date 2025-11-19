#!/usr/bin/env python3
"""
Local color detection for GCN documents
Detects border color (red vs pink) without AI
"""

from PIL import Image
import numpy as np
import sys

def detect_gcn_border_color(image_path):
    """
    NEW STRATEGY: Only check A3 size, let AI classify the document type
    
    Returns: 'pass' or 'unknown'
    
    Pre-filter only checks:
    - A3 size (aspect ratio > 1.35)
    
    AI will classify:
    - GCN → Keep as GCN
    - HSKT/PCT/SDTT/etc → Convert to GTLQ in post-processing
    
    This prevents:
    - Missing faded GCN (loose color check)
    - Still filters out A4 documents
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Get image dimensions
        height, width = img_array.shape[:2]
        aspect_ratio = width / height
        
        print(f"📏 Dimensions: {width}x{height}, Aspect ratio: {aspect_ratio:.2f}", file=sys.stderr)
        
        # ONLY CHECK: Must be A3 size (landscape)
        # GCN A3 has aspect ratio > 1.35 (example: 4443×3135 = 1.42)
        if aspect_ratio <= 1.35:
            print(f"❌ NOT A3 format (aspect ratio {aspect_ratio:.2f} <= 1.35)", file=sys.stderr)
            return 'unknown'
        
        print(f"✅ A3 format detected → PASS to AI", file=sys.stderr)
        print(f"   AI will classify: GCN, HSKT, PCT, etc.", file=sys.stderr)
        
        # Return 'pass' to indicate this A3 should be scanned by AI
        return 'pass'
        
    except Exception as e:
        print(f"❌ Detection error: {e}", file=sys.stderr)
        return 'unknown'


def get_dominant_color_simple(image_path, sample_region='center'):
    """
    Get dominant color from a region of the image
    
    Args:
        image_path: Path to image
        sample_region: 'center', 'top', 'border'
    
    Returns:
        Color name string or 'unknown'
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        height, width = img_array.shape[:2]
        
        # Sample different regions based on parameter
        if sample_region == 'center':
            # Sample center 20%
            y_start = int(height * 0.4)
            y_end = int(height * 0.6)
            x_start = int(width * 0.4)
            x_end = int(width * 0.6)
            sample = img_array[y_start:y_end, x_start:x_end, :]
            
        elif sample_region == 'top':
            # Sample top 30%
            sample = img_array[:int(height * 0.3), :, :]
            
        elif sample_region == 'border':
            return detect_gcn_border_color(image_path)
        
        else:
            sample = img_array
        
        # Flatten and get average color
        sample_flat = sample.reshape(-1, 3)
        avg_color = sample_flat.mean(axis=0)
        
        r, g, b = avg_color
        
        print(f"🎨 Dominant color RGB: ({r:.0f}, {g:.0f}, {b:.0f})", file=sys.stderr)
        
        # Simple color classification
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r > 150 and g < 100 and b < 100:
            return 'red'
        elif r > 150 and g > 130 and b > 130:
            return 'pink'
        else:
            return 'unknown'
            
    except Exception as e:
        print(f"❌ Color detection error: {e}", file=sys.stderr)
        return 'unknown'


if __name__ == '__main__':
    # CLI mode: Return only the color result to stdout
    # All debug info goes to stderr
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        
        # Use border detection (primary method)
        border_color = detect_gcn_border_color(image_path)
        
        # Output only the result to stdout (for IPC)
        print(border_color)
    else:
        print("Usage: python color_detector.py <image_path>", file=sys.stderr)
        sys.exit(1)
