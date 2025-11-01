#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cost estimator for Gemini Flash OCR
Provides predictive cost estimation based on image dimensions
"""

def estimate_tokens_from_image_size(width, height, model_type='gemini-flash'):
    """
    Estimate input tokens based on image dimensions
    Gemini calculates tokens approximately based on pixels
    
    Formula (approximate):
    - Each ~750 pixels ≈ 1 token
    - Plus prompt tokens:
      * Flash: ~5600 tokens (comprehensive prompt)
      * Flash Lite: ~1000 tokens (simplified prompt)
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        model_type: 'gemini-flash' or 'gemini-flash-lite'
        
    Returns:
        dict: Estimated tokens breakdown
    """
    total_pixels = width * height
    
    # Image tokens: ~750 pixels per token (Gemini's approximate ratio)
    image_tokens = int(total_pixels / 750)
    
    # Prompt tokens: Different for Flash vs Flash Lite
    if model_type == 'gemini-flash-lite':
        prompt_tokens = 1000  # Simplified prompt
    else:
        prompt_tokens = 5600  # Full comprehensive prompt
    
    # Total input tokens
    input_tokens = image_tokens + prompt_tokens
    
    # Output tokens: typically 50-150 for JSON response
    # Average: ~100 tokens
    output_tokens = 100
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "image_tokens": image_tokens,
        "prompt_tokens": prompt_tokens,
        "total_pixels": total_pixels
    }


def calculate_cost(input_tokens, output_tokens, model_type='gemini-flash'):
    """
    Calculate cost in USD based on tokens and model type
    
    Pricing (per 1M tokens):
    - Flash: $0.30 input, $2.50 output
    - Flash Lite: $0.10 input, $0.40 output
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_type: 'gemini-flash' or 'gemini-flash-lite'
        
    Returns:
        float: Cost in USD
    """
    if model_type == 'gemini-flash-lite':
        input_rate = 0.10
        output_rate = 0.40
    else:
        input_rate = 0.30
        output_rate = 2.50
    
    cost = (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000
    return cost


def estimate_cost_per_page(width=3000, height=4000, model_type='gemini-flash', 
                           enable_resize=True, max_width=2000, max_height=2800):
    """
    Estimate cost for one page scan
    
    Args:
        width: Original image width (default: 3000 for typical scan)
        height: Original image height (default: 4000 for typical scan)
        model_type: 'gemini-flash' or 'gemini-flash-lite'
        enable_resize: Whether resize is enabled
        max_width: Max width for resize
        max_height: Max height for resize
        
    Returns:
        dict: Cost estimation breakdown
    """
    # Calculate resize if enabled
    final_width = width
    final_height = height
    resize_applied = False
    reduction_percent = 0
    
    if enable_resize and (width > max_width or height > max_height):
        ratio = min(max_width / width, max_height / height)
        final_width = int(width * ratio)
        final_height = int(height * ratio)
        resize_applied = True
        reduction_percent = (1 - (final_width * final_height) / (width * height)) * 100
    
    # Estimate tokens
    tokens = estimate_tokens_from_image_size(final_width, final_height)
    
    # Calculate cost
    cost = calculate_cost(tokens['input_tokens'], tokens['output_tokens'], model_type)
    
    # Calculate cost without resize for comparison
    cost_without_resize = None
    if resize_applied:
        tokens_no_resize = estimate_tokens_from_image_size(width, height)
        cost_without_resize = calculate_cost(
            tokens_no_resize['input_tokens'], 
            tokens_no_resize['output_tokens'], 
            model_type
        )
    
    return {
        "original_size": f"{width}x{height}",
        "final_size": f"{final_width}x{final_height}",
        "resize_applied": resize_applied,
        "reduction_percent": round(reduction_percent, 1),
        "input_tokens": tokens['input_tokens'],
        "output_tokens": tokens['output_tokens'],
        "cost_usd": round(cost, 6),
        "cost_without_resize": round(cost_without_resize, 6) if cost_without_resize else None,
        "savings_percent": round((1 - cost / cost_without_resize) * 100, 1) if cost_without_resize else 0,
        "model_type": model_type
    }


def generate_cost_table():
    """
    Generate cost comparison table for different scenarios
    
    Returns:
        list: Cost estimates for different scenarios
    """
    scenarios = [
        {"name": "Scan nhỏ (2000x2800)", "width": 2000, "height": 2800},
        {"name": "Scan trung bình (2500x3500)", "width": 2500, "height": 3500},
        {"name": "Scan lớn (3000x4000)", "width": 3000, "height": 4000},
        {"name": "Scan rất lớn (4000x5600)", "width": 4000, "height": 5600},
    ]
    
    results = []
    
    for scenario in scenarios:
        w, h = scenario['width'], scenario['height']
        
        # Flash with resize
        flash_resize = estimate_cost_per_page(w, h, 'gemini-flash', True, 2000, 2800)
        
        # Flash without resize
        flash_no_resize = estimate_cost_per_page(w, h, 'gemini-flash', False)
        
        # Flash Lite with resize
        lite_resize = estimate_cost_per_page(w, h, 'gemini-flash-lite', True, 2000, 2800)
        
        # Flash Lite without resize
        lite_no_resize = estimate_cost_per_page(w, h, 'gemini-flash-lite', False)
        
        results.append({
            "scenario": scenario['name'],
            "size": f"{w}x{h}",
            "flash_resize": flash_resize,
            "flash_no_resize": flash_no_resize,
            "lite_resize": lite_resize,
            "lite_no_resize": lite_no_resize
        })
    
    return results


if __name__ == "__main__":
    # Test the estimator
    print("=== DỰ TOÁN CHI PHÍ GEMINI OCR ===\n")
    
    # Typical scan: 3000x4000
    print("📄 1 TRANG SCAN ĐIỂN HÌNH (3000x4000 pixels):\n")
    
    scenarios = [
        ("Gemini Flash + Resize (2000x2800)", 'gemini-flash', True),
        ("Gemini Flash (không resize)", 'gemini-flash', False),
        ("Gemini Flash Lite + Resize (2000x2800)", 'gemini-flash-lite', True),
        ("Gemini Flash Lite (không resize)", 'gemini-flash-lite', False),
    ]
    
    for name, model, resize in scenarios:
        est = estimate_cost_per_page(3000, 4000, model, resize, 2000, 2800)
        print(f"{name}:")
        print(f"  • Kích thước: {est['original_size']} → {est['final_size']}")
        print(f"  • Tokens: {est['input_tokens']:,} input + {est['output_tokens']} output")
        print(f"  • Chi phí: ${est['cost_usd']:.6f} (~{est['cost_usd']*1000:.2f}₫)")
        if est['cost_without_resize']:
            print(f"  • Tiết kiệm: {est['savings_percent']}% (${est['cost_without_resize']-est['cost_usd']:.6f})")
        print()
    
    print("\n=== BẢNG SO SÁNH CHI PHÍ ===\n")
    table = generate_cost_table()
    
    for row in table:
        print(f"📊 {row['scenario']} ({row['size']}):")
        print(f"  Flash + Resize: ${row['flash_resize']['cost_usd']:.6f}")
        print(f"  Flash gốc:      ${row['flash_no_resize']['cost_usd']:.6f}")
        print(f"  Lite + Resize:  ${row['lite_resize']['cost_usd']:.6f}")
        print(f"  Lite gốc:       ${row['lite_no_resize']['cost_usd']:.6f}")
        print()
