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
    Detect GCN A3 based on TWO criteria:
    1. Border color: Red or Pink
    2. Paper size: A3 (aspect ratio > 1.35, landscape)
    
    Returns: 'red', 'pink', or 'unknown'
    
    CRITICAL: Only returns 'red' or 'pink' if BOTH conditions met!
    - Has red/pink border
    - AND is A3 size (aspect ratio > 1.35)
    
    This prevents false positives from A4 documents with red stamps/seals.
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Get image dimensions
        height, width = img_array.shape[:2]
        aspect_ratio = width / height
        
        print(f"📏 Dimensions: {width}x{height}, Aspect ratio: {aspect_ratio:.2f}", file=sys.stderr)
        
        # ⚠️ CRITICAL CHECK #1: Must be A3 size (landscape)
        # GCN A3 has aspect ratio > 1.35 (example: 4443×3135 = 1.42)
        if aspect_ratio <= 1.35:
            print(f"❌ NOT A3 format (aspect ratio {aspect_ratio:.2f} <= 1.35)", file=sys.stderr)
            print(f"   → Skipping (even if has red color, not GCN A3)", file=sys.stderr)
            return 'unknown'
        
        print(f"✅ A3 format detected (landscape, aspect ratio > 1.35)", file=sys.stderr)
        
        # ✅ CRITICAL CHECK #2: Must have red/pink border
        # Sample ONLY outer edge (very thin border to avoid red stamps inside)
        # GCN has colored border on the outer edge, HSKT has black border
        border_thickness = int(min(width, height) * 0.005)  # 0.5% - Much thinner to avoid stamps
        border_thickness = max(border_thickness, 5)  # At least 5 pixels
        border_thickness = min(border_thickness, 20)  # Max 20 pixels
        
        print(f"   🔍 Sampling border: {border_thickness}px (outer edge only)", file=sys.stderr)
        
        # Extract OUTER EDGE only (very thin border)
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
        
        # Filter out white/gray/black pixels (background)
        # Only keep colored pixels (where at least one channel is significantly different)
        max_vals = all_borders.max(axis=1)
        min_vals = all_borders.min(axis=1)
        color_diff = max_vals - min_vals
        
        # Filter colored pixels
        colored_pixels = all_borders[color_diff > 20]
        
        total_border_pixels = len(all_borders)
        colored_ratio = len(colored_pixels) / total_border_pixels if total_border_pixels > 0 else 0
        
        print(f"   📊 Border analysis: {len(colored_pixels)}/{total_border_pixels} colored ({colored_ratio*100:.1f}%)", file=sys.stderr)
        
        # ⚠️ CRITICAL: Require MAJORITY of border to have color
        # GCN has colored border around entire edge (>40% colored pixels)
        # HSKT with red stamp inside has mostly black border (<10% colored)
        if colored_ratio < 0.40:  # Less than 40% colored
            print(f"❌ Not enough colored border ({colored_ratio*100:.1f}% < 40%)", file=sys.stderr)
            print(f"   → Likely black border with red stamp inside (HSKT)", file=sys.stderr)
            return 'unknown'
        
        if len(colored_pixels) < 50:
            print(f"⚠️ Too few colored pixels ({len(colored_pixels)})", file=sys.stderr)
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
            print(f"❌ No red/pink color detected (R={avg_r:.0f} too low)", file=sys.stderr)
        
        print(f"🎨 Detected color: {color}", file=sys.stderr)
        
        # Final result
        if color in ['red', 'pink']:
            print(f"✅ GCN A3 CANDIDATE: A3 size + {color} border", file=sys.stderr)
        else:
            print(f"❌ NOT GCN: A3 size but no red/pink border", file=sys.stderr)
        
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
