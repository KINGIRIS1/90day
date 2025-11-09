#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Scanner for Desktop App
Reads TXT file with folder paths and processes all images in each folder
"""
import sys
import json
import os
from pathlib import Path
import shutil
import warnings

# Suppress warnings FIRST
warnings.filterwarnings('ignore')
os.environ['GLOG_minloglevel'] = '2'
os.environ['FLAGS_use_mkldnn'] = '0'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import subprocess

try:
    from pypdf import PdfWriter, PdfReader
    from PIL import Image
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️  Warning: pypdf or PIL not found. PDF merging disabled.")

def merge_images_to_pdf(image_paths: list, output_path: str) -> bool:
    """
    Merge multiple images into a single PDF file
    """
    if not HAS_PDF:
        print("❌ Cannot merge to PDF: pypdf or PIL not installed")
        return False
    
    try:
        pdf_writer = PdfWriter()
        
        for img_path in image_paths:
            # Convert image to PDF page
            img = Image.open(img_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to temp PDF
            temp_pdf = img_path + '.temp.pdf'
            img.save(temp_pdf, 'PDF', resolution=100.0)
            
            # Add to writer
            pdf_reader = PdfReader(temp_pdf)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Clean up temp
            try:
                os.remove(temp_pdf)
            except:
                pass
        
        # Write final PDF
        with open(output_path, 'wb') as f:
            pdf_writer.write(f)
        
        return True
    except Exception as e:
        print(f"❌ Failed to merge PDF: {e}")
        return False

def process_document(file_path: str, ocr_engine: str, api_key: str = None) -> dict:
    """
    Call process_document.py as subprocess to avoid stdio conflicts
    """
    try:
        script_dir = os.path.dirname(__file__)
        script_path = os.path.join(script_dir, 'process_document.py')
        
        # Build command
        cmd = [sys.executable, script_path, file_path, ocr_engine]
        if api_key:
            cmd.append(api_key)
        
        # Run subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60,
            cwd=script_dir
        )
        
        if result.returncode == 0:
            # Parse JSON from last line
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{'):
                    return json.loads(line)
            
            # No JSON found
            return {
                "success": False,
                "error": "No JSON output from process_document.py",
                "short_code": "UNKNOWN",
                "doc_type": "Unknown",
                "confidence": 0
            }
        else:
            # Error
            return {
                "success": False,
                "error": f"process_document.py failed: {result.stderr[:200]}",
                "short_code": "UNKNOWN",
                "doc_type": "Unknown",
                "confidence": 0
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "process_document.py timeout (60s)",
            "short_code": "UNKNOWN",
            "doc_type": "Unknown",
            "confidence": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call process_document.py: {str(e)}",
            "short_code": "UNKNOWN",
            "doc_type": "Unknown",
            "confidence": 0
        }


def read_txt_file(txt_path: str) -> list:
    """
    Read TXT file and return list of folder paths (one per line)
    Ignores comment lines starting with #
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Clean up lines: strip whitespace, remove empty lines and comments
        folders = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                folders.append(line)
        return folders
    except Exception as e:
        print(f"❌ Error reading TXT file: {e}")
        return []


def validate_folder(folder_path: str) -> dict:
    """
    Validate folder exists and contains image files
    Returns: {"valid": bool, "image_files": list, "error": str}
    """
    if not os.path.exists(folder_path):
        return {"valid": False, "image_files": [], "error": "Thư mục không tồn tại"}
    
    if not os.path.isdir(folder_path):
        return {"valid": False, "image_files": [], "error": "Đường dẫn không phải là thư mục"}
    
    # List all image files (JPG, JPEG, PNG only, NO sub-folders)
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = []
    
    try:
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isfile(entry_path):
                ext = os.path.splitext(entry)[1].lower()
                if ext in image_extensions:
                    image_files.append(entry_path)
    except Exception as e:
        return {"valid": False, "image_files": [], "error": f"Lỗi đọc thư mục: {str(e)}"}
    
    if not image_files:
        return {"valid": False, "image_files": [], "error": "Không có file ảnh (JPG, JPEG, PNG)"}
    
    return {"valid": True, "image_files": sorted(image_files), "error": None}


def process_batch_scan(txt_path: str, ocr_engine: str, api_key: str = None, output_option: str = "same_folder", merge_suffix: str = "_merged", output_folder: str = None) -> dict:
    """
    Main batch scanning function
    
    Args:
        txt_path: Path to TXT file containing folder paths
        ocr_engine: OCR engine type (tesseract, easyocr, vietocr, gemini-flash, etc.)
        api_key: API key for cloud OCR (if needed)
        output_option: "same_folder" (save in source folder), "new_folder" (save in folder_suffix), or "custom_folder" (save in output_folder organized by folder name)
        merge_suffix: Suffix for new_folder mode (default: "_merged")
        output_folder: Output folder path (required for custom_folder)
    
    Returns:
        JSON object with results, errors, and statistics
    """
    try:
        print(f"📋 Starting batch scan from: {txt_path}")
        print(f"🔧 OCR Engine: {ocr_engine}")
        print(f"📤 Output Option: {output_option}")
    except:
        pass  # Ignore print errors
    
    # Read folder list from TXT
    folders = read_txt_file(txt_path)
    if not folders:
        return {
            "success": False,
            "error": "File TXT rỗng hoặc không đọc được",
            "total_folders": 0,
            "total_files": 0,
            "processed_files": 0,
            "skipped_folders": [],
            "errors": [],
            "results": []
        }
    
    print(f"📁 Found {len(folders)} folder(s) in TXT file")
    
    # Validate output folder if needed
    if output_option == "custom_folder":
        if not output_folder:
            return {
                "success": False,
                "error": f"Output folder is required for custom_folder mode",
                "total_folders": len(folders),
                "total_files": 0,
                "processed_files": 0,
                "skipped_folders": [],
                "errors": [],
                "results": []
            }
        
        # Create output folder if it doesn't exist
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            return {
                "success": False,
                "error": f"Cannot create output folder: {str(e)}",
                "total_folders": len(folders),
                "total_files": 0,
                "processed_files": 0,
                "skipped_folders": [],
                "errors": [],
                "results": [],
                "merged_pdfs": []
            }
    
    # Statistics
    total_files = 0
    processed_files = 0
    skipped_folders = []
    errors = []
    results = []
    merged_pdfs = []
    
    # Process each folder
    for idx, folder_path in enumerate(folders):
        print(f"\n📂 [{idx + 1}/{len(folders)}] Processing: {folder_path}")
        
        # Validate folder
        validation = validate_folder(folder_path)
        if not validation["valid"]:
            print(f"⚠️  Skipped: {validation['error']}")
            skipped_folders.append({
                "folder": folder_path,
                "reason": validation["error"]
            })
            continue
        
        image_files = validation["image_files"]
        total_files += len(image_files)
        print(f"🖼️  Found {len(image_files)} image file(s)")
        
        # Group to store classified images
        folder_groups = {}  # {short_code: [image_paths]}
        
        # Process each image
        for file_idx, image_path in enumerate(image_files):
            try:
                print(f"   [{file_idx + 1}/{len(image_files)}] Processing: {os.path.basename(image_path)}")
                
                # Call process_document
                result = process_document(image_path, ocr_engine, api_key)
                
                if not result.get("success", False):
                    error_msg = result.get("error", "Unknown error")
                    print(f"   ❌ Error: {error_msg}")
                    errors.append({
                        "file": image_path,
                        "error": error_msg
                    })
                    continue
                
                # Extract classification info
                short_code = result.get("short_code", "UNKNOWN")
                doc_type = result.get("doc_type", "Unknown")
                confidence = result.get("confidence", 0)
                
                print(f"   ✅ {short_code} ({doc_type}) - Confidence: {confidence:.0%}")
                
                # Group images by short_code
                if short_code not in folder_groups:
                    folder_groups[short_code] = []
                folder_groups[short_code].append(image_path)
                
                processed_files += 1
                results.append({
                    "original_path": image_path,
                    "short_code": short_code,
                    "doc_type": doc_type,
                    "confidence": confidence,
                    "folder": folder_path
                })
                
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                errors.append({
                    "file": image_path,
                    "error": str(e)
                })
        
        # Merge images to PDF by short_code
        if folder_groups:
            print(f"\n📚 Merging images to PDF for folder: {os.path.basename(folder_path)}")
            
            # Determine output directory
            if output_option == "same_folder":
                # Save in source folder
                output_dir = folder_path
            elif output_option == "new_folder":
                # Save in new folder with suffix
                parent_dir = os.path.dirname(folder_path)
                folder_name = os.path.basename(folder_path)
                output_dir = os.path.join(parent_dir, folder_name + merge_suffix)
                os.makedirs(output_dir, exist_ok=True)
            elif output_option == "custom_folder":
                # Save in output_folder/folder_name/
                folder_name = os.path.basename(folder_path)
                output_dir = os.path.join(output_folder, folder_name)
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = folder_path
            
            # Merge each group
            for short_code, img_paths in folder_groups.items():
                pdf_name = f"{short_code}.pdf"
                pdf_path = os.path.join(output_dir, pdf_name)
                
                # Handle duplicate PDF names
                counter = 1
                while os.path.exists(pdf_path):
                    pdf_name = f"{short_code}({counter}).pdf"
                    pdf_path = os.path.join(output_dir, pdf_name)
                    counter += 1
                
                print(f"   📄 Merging {len(img_paths)} images → {pdf_name}")
                
                success = merge_images_to_pdf(img_paths, pdf_path)
                if success:
                    merged_pdfs.append({
                        "short_code": short_code,
                        "path": pdf_path,
                        "count": len(img_paths),
                        "folder": folder_path
                    })
                    print(f"   ✅ Saved: {pdf_path}")
                else:
                    errors.append({
                        "file": folder_path,
                        "error": f"Failed to merge PDF for {short_code}"
                    })
    
    # Summary
    print(f"\n✅ Batch scan complete!")
    print(f"📊 Total folders: {len(folders)}")
    print(f"📊 Skipped folders: {len(skipped_folders)}")
    print(f"📊 Total files: {total_files}")
    print(f"📊 Processed files: {processed_files}")
    print(f"📊 Merged PDFs: {len(merged_pdfs)}")
    print(f"📊 Errors: {len(errors)}")
    
    return {
        "success": True,
        "total_folders": len(folders),
        "valid_folders": len(folders) - len(skipped_folders),
        "skipped_folders_count": len(skipped_folders),
        "total_files": total_files,
        "processed_files": processed_files,
        "merged_pdfs_count": len(merged_pdfs),
        "error_count": len(errors),
        "skipped_folders": skipped_folders,
        "errors": errors,
        "results": results,
        "merged_pdfs": merged_pdfs
    }


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            error_result = {
                "success": False,
                "error": "Invalid arguments. Usage: batch_scanner.py <txt_path> <ocr_engine> [api_key] [output_option] [merge_suffix] [output_folder]",
                "total_folders": 0,
                "total_files": 0,
                "processed_files": 0,
                "skipped_folders": [],
                "errors": [],
                "results": [],
                "merged_pdfs": []
            }
            print(json.dumps(error_result, ensure_ascii=False))
            sys.exit(1)
        
        txt_path = sys.argv[1]
        ocr_engine = sys.argv[2]
        api_key = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "none" else None
        output_option = sys.argv[4] if len(sys.argv) > 4 else "same_folder"
        merge_suffix = sys.argv[5] if len(sys.argv) > 5 else "_merged"
        output_folder = sys.argv[6] if len(sys.argv) > 6 else None
        
        result = process_batch_scan(txt_path, ocr_engine, api_key, output_option, merge_suffix, output_folder)
        
        # Print JSON result to stdout
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
        
    except Exception as e:
        # Catch any unhandled exceptions and return JSON error
        error_result = {
            "success": False,
            "error": f"Unhandled exception: {str(e)}",
            "total_folders": 0,
            "total_files": 0,
            "processed_files": 0,
            "skipped_folders": [],
            "errors": [{"file": "N/A", "error": str(e)}],
            "results": []
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)
