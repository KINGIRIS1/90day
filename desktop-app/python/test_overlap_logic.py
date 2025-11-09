#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Overlap Logic - Verify batch ranges are correct
"""

def test_overlap_logic():
    """Test batch range calculation with overlap"""
    
    print("=" * 80)
    print("TEST: Overlap Logic Verification")
    print("=" * 80)
    
    # Simulate 30 files
    image_paths = [f"file_{i:03d}.jpg" for i in range(30)]
    batch_size = 10
    overlap = 3
    
    print(f"\nSetup:")
    print(f"  Total files: {len(image_paths)}")
    print(f"  Batch size: {batch_size}")
    print(f"  Overlap: {overlap}")
    
    batch_num = 0
    current_idx = 0
    
    print(f"\nBatch Calculation:")
    print(f"-" * 80)
    
    while current_idx < len(image_paths):
        batch_num += 1
        
        # Calculate batch range with overlap (same logic as batch_processor.py)
        batch_start = max(0, current_idx - overlap) if batch_num > 1 else current_idx
        batch_end = min(len(image_paths), current_idx + batch_size)
        batch_paths = image_paths[batch_start:batch_end]
        
        # Track which files are NEW
        new_file_start_idx = current_idx - batch_start
        
        print(f"\nBatch {batch_num}:")
        print(f"  Range: Files {batch_start}-{batch_end-1}")
        print(f"  Total: {len(batch_paths)} files")
        
        if batch_num > 1:
            print(f"  Overlap: {overlap} files (indices {batch_start}-{current_idx-1})")
            overlap_files = batch_paths[:new_file_start_idx]
            print(f"    ↩️ Overlap files: {[f for f in overlap_files]}")
        
        new_files = batch_paths[new_file_start_idx:]
        print(f"  New: {len(new_files)} files (indices {current_idx}-{batch_end-1})")
        print(f"    🆕 New files: {[f for f in new_files]}")
        
        # Move to next batch
        current_idx += batch_size
    
    print(f"\n{'=' * 80}")
    print(f"✅ Test Complete: {batch_num} batches")
    print(f"{'=' * 80}")


def test_100_files():
    """Test with 100 files (user's case)"""
    
    print("\n" + "=" * 80)
    print("TEST: 100 Files with Smart Batch (batch_size=15, overlap=4)")
    print("=" * 80)
    
    image_paths = [f"file_{i:03d}.jpg" for i in range(100)]
    batch_size = 15
    overlap = 4
    
    batch_num = 0
    current_idx = 0
    all_processed = set()
    
    while current_idx < len(image_paths):
        batch_num += 1
        
        batch_start = max(0, current_idx - overlap) if batch_num > 1 else current_idx
        batch_end = min(len(image_paths), current_idx + batch_size)
        new_file_start_idx = current_idx - batch_start
        
        # Simulate processing new files only
        new_files_in_batch = list(range(current_idx, batch_end))
        
        print(f"\nBatch {batch_num}: Files {batch_start}-{batch_end-1}")
        print(f"  Overlap: {batch_start}-{current_idx-1} (for context)")
        print(f"  New files: {current_idx}-{batch_end-1} ({len(new_files_in_batch)} files)")
        
        # Add new files to processed set
        all_processed.update(new_files_in_batch)
        
        current_idx += batch_size
    
    # Verify all files processed
    expected = set(range(100))
    missing = expected - all_processed
    
    print(f"\n{'=' * 80}")
    print(f"VERIFICATION:")
    print(f"  Expected: {len(expected)} files (0-99)")
    print(f"  Processed: {len(all_processed)} files")
    print(f"  Missing: {len(missing)} files")
    
    if missing:
        print(f"  ❌ Missing files: {sorted(missing)}")
    else:
        print(f"  ✅ All files processed!")
    
    print(f"{'=' * 80}")


if __name__ == "__main__":
    test_overlap_logic()
    test_100_files()
