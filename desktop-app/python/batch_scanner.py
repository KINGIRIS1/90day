#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Scanner - Process multiple folders from CSV/Excel list
Scans image files (.jpg, .jpeg, .png) in each folder path
"""

import sys
import os
import json
from pathlib import Path


def read_folder_list(file_path):
    """
    Read folder paths from CSV or Excel file
    
    Args:
        file_path: Path to CSV or Excel file
        
    Returns:
        list: List of folder paths
    """
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.csv':
            import csv
            folder_paths = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                # Try common column names
                for row in reader:
                    # Support multiple column name variants
                    path = (row.get('folder_path') or 
                           row.get('path') or 
                           row.get('folder') or 
                           row.get('đường dẫn') or
                           row.get('thu_muc') or
                           list(row.values())[0])  # First column as fallback
                    if path and path.strip():
                        folder_paths.append(path.strip())
            return folder_paths
            
        elif file_ext in ['.xlsx', '.xls']:
            try:
                import openpyxl
            except ImportError:
                print(json.dumps({
                    "success": False,
                    "error": "Missing openpyxl library. Install: pip install openpyxl"
                }))
                return []
            
            workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            sheet = workbook.active
            folder_paths = []
            
            # Skip header row, read from row 2
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row and row[0]:  # Get first column
                    path = str(row[0]).strip()
                    if path:
                        folder_paths.append(path)
            
            workbook.close()
            return folder_paths
        else:
            print(json.dumps({
                "success": False,
                "error": f"Unsupported file format: {file_ext}. Use .csv or .xlsx"
            }))
            return []
            
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }))
        return []


def validate_folder(folder_path):
    """
    Validate if folder exists and is accessible
    
    Args:
        folder_path: Path to folder
        
    Returns:
        dict: Validation result
    """
    if not folder_path:
        return {"valid": False, "error": "Empty path"}
    
    path = Path(folder_path)
    
    if not path.exists():
        return {"valid": False, "error": "Folder does not exist"}
    
    if not path.is_dir():
        return {"valid": False, "error": "Path is not a folder"}
    
    try:
        # Test read access
        list(path.iterdir())
        return {"valid": True}
    except PermissionError:
        return {"valid": False, "error": "Permission denied"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def get_image_files(folder_path):
    """
    Get all image files in folder (non-recursive)
    
    Args:
        folder_path: Path to folder
        
    Returns:
        list: List of image file paths
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    try:
        folder = Path(folder_path)
        image_files = []
        
        for file in folder.iterdir():
            if file.is_file() and file.suffix in image_extensions:
                image_files.append(str(file.absolute()))
        
        return sorted(image_files)
    except Exception as e:
        print(f"Error scanning folder {folder_path}: {e}", file=sys.stderr)
        return []


def analyze_batch(csv_file_path):
    """
    Analyze CSV/Excel file and prepare batch scan summary
    
    Args:
        csv_file_path: Path to CSV/Excel file
        
    Returns:
        JSON with batch analysis
    """
    folder_paths = read_folder_list(csv_file_path)
    
    if not folder_paths:
        return {
            "success": False,
            "error": "No folder paths found in file"
        }
    
    batch_summary = {
        "success": True,
        "total_folders": len(folder_paths),
        "valid_folders": 0,
        "invalid_folders": 0,
        "total_images": 0,
        "folders": []
    }
    
    for folder_path in folder_paths:
        validation = validate_folder(folder_path)
        
        folder_info = {
            "path": folder_path,
            "valid": validation["valid"],
            "error": validation.get("error"),
            "image_count": 0,
            "images": []
        }
        
        if validation["valid"]:
            batch_summary["valid_folders"] += 1
            images = get_image_files(folder_path)
            folder_info["image_count"] = len(images)
            folder_info["images"] = images
            batch_summary["total_images"] += len(images)
        else:
            batch_summary["invalid_folders"] += 1
        
        batch_summary["folders"].append(folder_info)
    
    return batch_summary


def main():
    """
    Main entry point for batch scanner
    Usage: python batch_scanner.py <csv_or_excel_file>
    """
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python batch_scanner.py <csv_or_excel_file>"
        }))
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(json.dumps({
            "success": False,
            "error": f"File not found: {csv_file}"
        }))
        sys.exit(1)
    
    # Analyze batch
    result = analyze_batch(csv_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
