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
    Detect GCN border color locally without AI
    Returns: 'red', 'pink', or 'unknown'
    
    GCN characteristics:
    - Border color: Red (R>150, G<100, B<100) or Pink (R>150, G>130, B>130)
    - A3 GCN: aspect ratio > 1.35 (landscape)
    - A4 GCN: aspect ratio < 1.0 (portrait)
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Get image dimensions
        height, width = img_array.shape[:2]
        aspect_ratio = width / height
        
        print(f"📏 Dimensions: {width}x{height}, Aspect ratio: {aspect_ratio:.2f}", file=sys.stderr)
        
        # Sample border regions (top, bottom, left, right)
        border_thickness = int(min(width, height) * 0.02)  # 2% of smaller dimension
        
        # Extract border pixels
        top_border = img_array[:border_thickness, :, :]
        bottom_border = img_array[-border_thickness:, :, :]
        left_border = img_array[:, :border_thickness, :]
        right_border = img_array[:, -border_thickness:, :]
        
        # Combine all borders
        all_borders = np.vstack([
            top_border.reshape(-1, 3),
            bottom_border.reshape(-1, 3),
            left_border.reshape(-1, 3),
            right_border.reshape(-1, 3)
        ])
        
        # Filter out white/gray pixels (background)
        # Only keep colored pixels (where at least one channel is significantly different)
        max_vals = all_borders.max(axis=1)
        min_vals = all_borders.min(axis=1)
        color_diff = max_vals - min_vals
        
        # LOWERED threshold to catch more colored pixels
        colored_pixels = all_borders[color_diff > 20]  # Lowered from 30 to 20
        
        if len(colored_pixels) < 50:  # Lowered from 100 to 50
            print(f"⚠️ Not enough colored border pixels found ({len(colored_pixels)})", file=sys.stderr)
            return 'unknown'
        
        # Calculate average RGB of colored pixels
        avg_r = np.mean(colored_pixels[:, 0])
        avg_g = np.mean(colored_pixels[:, 1])
        avg_b = np.mean(colored_pixels[:, 2])
        
        print(f"🎨 Border color RGB: ({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f})", file=sys.stderr)
        
        # Classify based on RGB values
        # Red GCN: High R, Low G, Low B
        # Pink GCN: High R, High G, High B (but R > G,B)
        
        # VERY RELAXED THRESHOLDS - Catch all potential GCN
        # Better to have false positives than miss real GCN
        if avg_r > 80:  # Red component present (lowered from 100)
            if avg_g > 80 and avg_b > 80:
                # Pink-ish: All channels relatively high
                # Be more lenient with pink detection
                if avg_r >= avg_g * 0.9:  # R should be at least 90% of G
                    color = 'pink'
                else:
                    # Still could be faded pink, be conservative
                    color = 'pink'
            elif avg_r > avg_g + 20 and avg_r > avg_b + 20:  # Lowered from 30
                # Red: R significantly higher than G and B
                color = 'red'
            else:
                # Could be orange, light red, faded pink - PASS to be safe
                color = 'red'  # Conservative: consider as potential GCN
        else:
            color = 'unknown'
        
        print(f"🎨 Detected color: {color}", file=sys.stderr)
        
        # Additional logging for debugging
        if aspect_ratio > 1.35:
            print(f"📐 A3 format detected (landscape)", file=sys.stderr)
        elif aspect_ratio < 1.0:
            print(f"📐 A4 format detected (portrait)", file=sys.stderr)
        
        return color
        
    except Exception as e:
        print(f"❌ Color detection error: {e}", file=sys.stderr)
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
    # Test
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Testing color detection on: {image_path}")
        
        border_color = detect_gcn_border_color(image_path)
        print(f"Border color: {border_color}")
        
        center_color = get_dominant_color_simple(image_path, 'center')
        print(f"Center color: {center_color}")
    else:
        print("Usage: python color_detector.py <image_path>")
