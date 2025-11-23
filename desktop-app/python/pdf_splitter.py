#!/usr/bin/env python3
"""
PDF to Image Converter - Convert PDF pages to images for OCR
"""

import sys
import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image

# Poppler path for Windows
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"

def split_pdf_to_images(pdf_path, dpi=200):
    """
    Convert PDF pages to JPEG images
    
    Args:
        pdf_path: Path to the input PDF file
        dpi: Resolution for conversion (default 200, good balance between quality and size)
        
    Returns:
        List of paths to the converted image files
        
    Example:
        input.pdf (3 pages) → [input_page1.jpg, input_page2.jpg, input_page3.jpg]
    """
    try:
        print(f"📄 Converting PDF to images: {pdf_path}", file=sys.stderr)
        print(f"   DPI: {dpi} (higher = better quality but larger files)", file=sys.stderr)
        
        # Convert PDF pages to PIL images
        # Try with poppler_path first (Windows), fallback to system PATH
        try:
            if os.path.exists(POPPLER_PATH):
                images = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)
            else:
                images = convert_from_path(pdf_path, dpi=dpi)
        except:
            # Fallback: try without poppler_path
            images = convert_from_path(pdf_path, dpi=dpi)
        
        num_pages = len(images)
        
        print(f"   Pages: {num_pages}", file=sys.stderr)
        
        # Create temp directory for images
        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        image_paths = []
        
        # Save each page as JPEG
        for page_num, image in enumerate(images):
            # Generate output path
            output_path = os.path.join(temp_dir, f"{base_name}_page{page_num + 1}.jpg")
            
            # Convert to RGB if needed (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Save as JPEG with quality 85 (good balance)
            image.save(output_path, 'JPEG', quality=85, optimize=True)
            
            # Get file size for logging
            file_size = os.path.getsize(output_path) / 1024  # KB
            
            image_paths.append(output_path)
            print(f"   ✅ Page {page_num + 1}/{num_pages} → {os.path.basename(output_path)} ({file_size:.1f} KB)", file=sys.stderr)
        
        print(f"✅ PDF conversion complete: {num_pages} images", file=sys.stderr)
        return image_paths
        
    except Exception as e:
        print(f"❌ Error converting PDF: {e}", file=sys.stderr)
        print(f"   Make sure poppler-utils is installed:", file=sys.stderr)
        print(f"   - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases", file=sys.stderr)
        print(f"   - Mac: brew install poppler", file=sys.stderr)
        print(f"   - Linux: sudo apt-get install poppler-utils", file=sys.stderr)
        return None


# Backward compatibility - keep old function name
def split_pdf_to_pages(pdf_path):
    """
    Backward compatibility wrapper
    Converts PDF to images instead of splitting to PDFs
    """
    return split_pdf_to_images(pdf_path)


def cleanup_split_pages(page_paths):
    """
    Clean up temporary image files
    
    Args:
        page_paths: List of paths to temporary image files
    """
    if not page_paths:
        return
        
    try:
        cleaned = 0
        for page_path in page_paths:
            if os.path.exists(page_path):
                os.remove(page_path)
                cleaned += 1
        if cleaned > 0:
            print(f"🧹 Cleaned up {cleaned} temporary image file(s)", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}", file=sys.stderr)


# Test function
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_splitter.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"Error: File not found: {pdf_file}")
        sys.exit(1)
    
    # Convert PDF to images
    print("\n" + "="*60)
    print("Testing PDF to Image Conversion")
    print("="*60)
    
    images = split_pdf_to_images(pdf_file, dpi=200)
    
    if images:
        print(f"\n✅ Conversion successful!")
        print(f"\nConverted images:")
        total_size = 0
        for img_path in images:
            size = os.path.getsize(img_path) / 1024
            total_size += size
            print(f"  - {os.path.basename(img_path)} ({size:.1f} KB)")
        print(f"\nTotal size: {total_size:.1f} KB")
        
        # Optional: Clean up
        input("\nPress Enter to clean up temporary files...")
        cleanup_split_pages(images)
        print("✅ Cleanup complete")
    else:
        print("❌ Failed to convert PDF")
        sys.exit(1)
