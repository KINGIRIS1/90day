#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug classification để xem chi tiết score calculation
"""
import sys
sys.path.insert(0, '/app/desktop-app/python')

from rule_classifier import RuleClassifier, DOCUMENT_RULES, normalize_text

if len(sys.argv) < 2:
    print("Usage: python debug_classifier.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]

# Import OCR engine
from ocr_engine_easyocr import OCREngine

print("=" * 70)
print("STEP 1: OCR EXTRACTION")
print("=" * 70)

engine = OCREngine()
ocr_result = engine.extract_text(image_path)

full_text = ocr_result['full_text']
title_text = ocr_result['title_text']

print(f"Full text ({len(full_text)} chars):")
print(full_text)
print()
print(f"Title text ({len(title_text)} chars):")
print(title_text)
print()

print("=" * 70)
print("STEP 2: KEYWORD MATCHING")
print("=" * 70)

text_normalized = normalize_text(full_text)
title_normalized = normalize_text(title_text)

# Check specific doc types
for doc_type in ['HDCQ', 'CCCD', 'GCNM']:
    keywords = DOCUMENT_RULES[doc_type]['keywords']
    weight = DOCUMENT_RULES[doc_type]['weight']
    
    matched = []
    title_matches = 0
    
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if title_normalized and kw_norm in title_normalized:
            matched.append(f"{kw} [TITLE]")
            title_matches += 1
        elif kw_norm in text_normalized:
            matched.append(kw)
    
    if matched:
        base_score = len(matched) * weight
        title_boost = title_matches * weight * 3.0
        total_score = base_score + title_boost
        
        print(f"\n{doc_type}:")
        print(f"  Weight: {weight}")
        print(f"  Matched keywords ({len(matched)}): {matched[:5]}...")
        print(f"  Title matches: {title_matches}")
        print(f"  Base score: {base_score:.2f}")
        print(f"  Title boost: {title_boost:.2f}")
        print(f"  TOTAL SCORE: {total_score:.2f}")

print()
print("=" * 70)
print("STEP 3: CLASSIFICATION RESULT")
print("=" * 70)

classifier = RuleClassifier()
result = classifier.classify(full_text, title_text=title_text)

print(f"Doc Type: {result['doc_type']}")
print(f"Short Code: {result['short_code']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Reasoning: {result['reasoning'][:200]}...")
print("=" * 70)
