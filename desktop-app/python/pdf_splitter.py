#!/usr/bin/env python3
"""
PDF to Image Converter - Convert PDF pages to images for OCR
"""

import sys
import os
import tempfile
import subprocess
from PIL import Image
from pypdf import PdfReader

# Poppler path for Windows
POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"

def find_pdftoppm():
    """Find pdftoppm executable"""
    # Try common locations
    possible_paths = [
        os.path.join(POPPLER_PATH, 'pdftoppm.exe'),
        'pdftoppm.exe',  # In PATH
        'pdftoppm',  # Linux/Mac
    ]
    
    for path in possible_paths:
        try:
            # Test if command exists
            subprocess.run([path, '-h'], capture_output=True, timeout=5)
            return path
        except:
            continue
    
    return None

def split_pdf_to_images(pdf_path, dpi=200):
    """
    Convert PDF pages to JPEG images using pdftoppm directly
    
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
        
        # Get page count using pypdf
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            print(f"   Pages detected: {num_pages}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Could not read PDF: {e}", file=sys.stderr)
            return None
        
        # Find pdftoppm executable
        pdftoppm_path = find_pdftoppm()
        if not pdftoppm_path:
            print(f"❌ pdftoppm not found. Please install Poppler.", file=sys.stderr)
            return None
        
        print(f"   Using: {pdftoppm_path}", file=sys.stderr)
        
        # Create temp directory
        temp_dir = tempfile.gettempdir()
        
        # Copy PDF to temp with safe name (no spaces, no accents)
        import time
        import shutil
        temp_pdf_name = f"temp_pdf_{int(time.time())}.pdf"
        temp_pdf_path = os.path.join(temp_dir, temp_pdf_name)
        
        print(f"   Copying to temp: {temp_pdf_name}", file=sys.stderr)
        shutil.copy2(pdf_path, temp_pdf_path)
        
        # Generate output prefix (simple, no spaces)
        output_prefix = os.path.join(temp_dir, f"page_{int(time.time())}")
        
        # Call pdftoppm directly: pdftoppm -jpeg -r <dpi> input.pdf output_prefix
        # This will create: output_prefix-1.jpg, output_prefix-2.jpg, etc.
        cmd = [
            pdftoppm_path,
            '-jpeg',
            '-r', str(dpi),
            temp_pdf_path,
            output_prefix
        ]
        
        print(f"   Running pdftoppm...", file=sys.stderr)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Clean up temp PDF
        try:
            os.remove(temp_pdf_path)
        except:
            pass
        
        if result.returncode != 0:
            print(f"❌ pdftoppm failed (exit code {result.returncode}):", file=sys.stderr)
            if result.stdout:
                print(f"   stdout: {result.stdout}", file=sys.stderr)
            if result.stderr:
                print(f"   stderr: {result.stderr}", file=sys.stderr)
            return None
        
        print(f"   ✅ pdftoppm completed", file=sys.stderr)
        
        # Find generated images
        image_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for page_num in range(1, num_pages + 1):
            # pdftoppm generates files like: prefix-1.jpg, prefix-2.jpg, ...
            # Format depends on number of pages (more pages = more leading zeros)
            # Try different formats
            possible_formats = [
                f"{output_prefix}-{page_num}.jpg",
                f"{output_prefix}-{page_num:02d}.jpg",
                f"{output_prefix}-{page_num:03d}.jpg",
                f"{output_prefix}-{page_num:04d}.jpg",
            ]
            
            found_path = None
            for possible_path in possible_formats:
                if os.path.exists(possible_path):
                    found_path = possible_path
                    break
            
            if found_path:
                # Rename to friendly name with original PDF name
                friendly_name = f"{base_name}_page{page_num}.jpg"
                friendly_path = os.path.join(temp_dir, friendly_name)
                
                # If friendly_path already exists, use unique name
                if os.path.exists(friendly_path):
                    friendly_name = f"{base_name}_{int(time.time())}_page{page_num}.jpg"
                    friendly_path = os.path.join(temp_dir, friendly_name)
                
                try:
                    os.rename(found_path, friendly_path)
                    image_paths.append(friendly_path)
                    file_size = os.path.getsize(friendly_path) / 1024
                    print(f"   ✅ Page {page_num}/{num_pages} → {friendly_name} ({file_size:.1f} KB)", file=sys.stderr)
                except Exception as e:
                    print(f"   ⚠️ Could not rename page {page_num}: {e}", file=sys.stderr)
                    image_paths.append(found_path)
            else:
                print(f"   ⚠️ Page {page_num} not found", file=sys.stderr)
        
        if len(image_paths) != num_pages:
            print(f"   ⚠️ Warning: Expected {num_pages} pages, found {len(image_paths)}", file=sys.stderr)
        
        if not image_paths:
            print(f"❌ No images generated", file=sys.stderr)
            return None
        
        print(f"✅ PDF conversion complete: {len(image_paths)} images", file=sys.stderr)
        return image_paths
        
    except subprocess.TimeoutExpired:
        print(f"❌ PDF conversion timeout (5 minutes)", file=sys.stderr)
        return None
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
