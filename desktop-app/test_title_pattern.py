#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify title pattern extraction order
"""

import re

# Test text from user's log
test_text = """CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT
Chúng tôi gồm có:
Bên chuyển nhượng (sau đây gọi là bên A):
"""

# Patterns in NEW order (HDCQ before HDUQ)
title_patterns = [
    # HỢP ĐỒNG CHUYỂN NHƯỢNG (check FIRST - more specific)
    (r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+CHUY[EÊÉÈẾỀỂỄỆ]N\s+NH[UƯÚÙỦŨỤỨỪỬỮỰ][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG(?:\s+QUY[EÊÉÈẾỀỂỄỆ]N)?(?:\s+S[UƯÚÙỦŨỤỨỪỬỮỰ]\s+D[UỤ]NG\s+[ĐD][AÁẤ]T)?)', 'HDCQ'),
    
    # HỢP ĐỒNG ỦY QUYỀN (check AFTER HDCQ)
    (r'(H[OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]P\s+[ĐD][OÔƠÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢ]NG\s+(?:[UỦ][\sỶ]*Y|U[ỶY])\s+QUY[EÊÉÈẾỀỂỄỆ]N)', 'HDUQ'),
]

print("=" * 80)
print("Testing title pattern extraction with NEW order (HDCQ first)")
print("=" * 80)
print(f"\nTest text:\n{test_text}")
print("\n" + "=" * 80)

for pattern, name in title_patterns:
    match = re.search(pattern, test_text, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        print(f"\n✅ Pattern {name} MATCHED:")
        print(f"   Extracted: '{title}'")
        print(f"   Length: {len(title)}")
        
        # Calculate uppercase ratio
        letters = [c for c in title if c.isalpha()]
        uppercase_letters = [c for c in letters if c.isupper()]
        uppercase_ratio = len(uppercase_letters) / len(letters) if letters else 0
        print(f"   Uppercase ratio: {uppercase_ratio:.1%}")
        
        # This is what extract_document_title_from_text() would return
        cleaned = re.sub(r'\s+[a-zàáạảãâầấậẩẫăằắặẳẵđèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ].*$', '', title)
        print(f"   After cleaning: '{cleaned}'")
        print(f"   → This should be returned!")
        break
    else:
        print(f"❌ Pattern {name} did not match")

print("\n" + "=" * 80)
print("Expected result: Should match HDCQ (HỢP ĐỒNG CHUYỂN NHƯỢNG...)")
print("=" * 80)
