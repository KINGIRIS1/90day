#!/usr/bin/env python3
"""
PDF to Image Converter - Convert PDF pages to images for OCR
Uses PyMuPDF (fitz) - No Poppler required!
"""

import sys
import os
import tempfile
from PIL import Image

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF not found. Installing...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF'])
    import fitz

def split_pdf_to_images(pdf_path, dpi=200):
    """
    Convert PDF pages to JPEG images using PyMuPDF (fitz)
    No Poppler required!
    
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
        print(f"   Using: PyMuPDF (fitz)", file=sys.stderr)
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(pdf_path)
        num_pages = len(pdf_document)
        
        print(f"   Pages detected: {num_pages}", file=sys.stderr)
        
        # Create temp directory
        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        image_paths = []
        
        # Calculate zoom factor for desired DPI
        # PyMuPDF default is 72 DPI, so zoom = target_dpi / 72
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        # Convert each page
        for page_num in range(num_pages):
            # Get page
            page = pdf_document[page_num]
            
            # Render page to pixmap (image)
            pix = page.get_pixmap(matrix=mat)
            
            # Generate output path
            import time
            friendly_name = f"{base_name}_page{page_num + 1}.jpg"
            output_path = os.path.join(temp_dir, friendly_name)
            
            # If file exists, use unique name
            if os.path.exists(output_path):
                friendly_name = f"{base_name}_{int(time.time())}_page{page_num + 1}.jpg"
                output_path = os.path.join(temp_dir, friendly_name)
            
            # Save as JPEG
            # PyMuPDF can save directly, but we use PIL for consistency
            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save as JPEG with quality 85
            img.save(output_path, 'JPEG', quality=85, optimize=True)
            
            image_paths.append(output_path)
            
            # Get file size
            file_size = os.path.getsize(output_path) / 1024
            print(f"   ✅ Page {page_num + 1}/{num_pages} → {friendly_name} ({file_size:.1f} KB)", file=sys.stderr)
        
        # Close PDF
        pdf_document.close()
        
        print(f"✅ PDF conversion complete: {len(image_paths)} images", file=sys.stderr)
        return image_paths
        
    except Exception as e:
        print(f"❌ Error converting PDF: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
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
