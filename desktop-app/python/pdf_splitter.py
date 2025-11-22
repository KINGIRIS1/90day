#!/usr/bin/env python3
"""
PDF to Image Converter - Convert PDF pages to images for OCR
"""

import sys
import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image

def split_pdf_to_pages(pdf_path):
    """
    Split a multi-page PDF into separate single-page PDF files
    
    Args:
        pdf_path: Path to the input PDF file
        
    Returns:
        List of paths to the split PDF pages
        
    Example:
        input.pdf (3 pages) → [input_page1.pdf, input_page2.pdf, input_page3.pdf]
    """
    try:
        print(f"📄 Splitting PDF: {pdf_path}", file=sys.stderr)
        
        # Read the PDF
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        print(f"   Pages: {num_pages}", file=sys.stderr)
        
        # Create temp directory for split pages
        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        split_pages = []
        
        # Extract each page as a separate PDF
        for page_num in range(num_pages):
            # Create a new PDF writer for this page
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            # Generate output path
            output_path = os.path.join(temp_dir, f"{base_name}_page{page_num + 1}.pdf")
            
            # Write the single-page PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            split_pages.append(output_path)
            print(f"   ✅ Page {page_num + 1}/{num_pages} → {os.path.basename(output_path)}", file=sys.stderr)
        
        print(f"✅ PDF split complete: {num_pages} pages", file=sys.stderr)
        return split_pages
        
    except Exception as e:
        print(f"❌ Error splitting PDF: {e}", file=sys.stderr)
        return None


def cleanup_split_pages(page_paths):
    """
    Clean up temporary split page files
    
    Args:
        page_paths: List of paths to split pages
    """
    try:
        for page_path in page_paths:
            if os.path.exists(page_path):
                os.remove(page_path)
        print(f"🧹 Cleaned up {len(page_paths)} temporary files", file=sys.stderr)
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
    
    # Split PDF
    pages = split_pdf_to_pages(pdf_file)
    
    if pages:
        print(f"\nSplit pages:")
        for page in pages:
            print(f"  - {page}")
        
        # Optional: Clean up
        input("\nPress Enter to clean up temporary files...")
        cleanup_split_pages(pages)
    else:
        print("Failed to split PDF")
        sys.exit(1)
