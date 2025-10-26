#!/usr/bin/env python3
"""
Quick test script to verify PaddleOCR works without verbose output
"""
import sys
import os
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')
os.environ['GLOG_minloglevel'] = '2'
os.environ['FLAGS_use_mkldnn'] = '0'

print("Testing PaddleOCR with suppressed output...")

try:
    from paddleocr import PaddleOCR
    
    # Redirect stdout/stderr during initialization
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    # Initialize OCR
    ocr = PaddleOCR(lang='vi', use_textline_orientation=True)
    
    # Restore output
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    print("✅ PaddleOCR initialized successfully (silent mode)")
    print("Models loaded without verbose output")
    print("Ready for desktop app integration!")
    
except Exception as e:
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    print(f"❌ Error: {e}")
    sys.exit(1)
