#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Variants Generator
Auto-generate Vietnamese keyword variants for better OCR matching
"""
import unicodedata
import re
from typing import List, Set


def remove_diacritics(text: str) -> str:
    """
    Remove Vietnamese diacritics
    Example: "Tiếng Việt" -> "Tieng Viet"
    """
    # Normalize to NFD (decomposed form)
    nfd = unicodedata.normalize('NFD', text)
    # Remove combining characters (diacritics)
    without_diacritics = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    # Handle special Vietnamese characters that don't decompose properly
    replacements = {
        'đ': 'd', 'Đ': 'D',
        'ð': 'd',  # Sometimes OCR reads đ as ð
    }
    
    result = without_diacritics
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result


def generate_case_variants(text: str) -> List[str]:
    """
    Generate case variants: lowercase, UPPERCASE, Title Case
    """
    variants = set()
    
    # Original
    variants.add(text)
    
    # Lowercase
    variants.add(text.lower())
    
    # UPPERCASE
    variants.add(text.upper())
    
    # Title Case (capitalize first letter of each word)
    variants.add(text.title())
    
    return list(variants)


def generate_ocr_typos(text: str) -> List[str]:
    """
    Generate common OCR typos for Vietnamese
    Based on common OCR misreads
    """
    typos = set()
    
    # Common OCR mistakes
    replacements = [
        ('ă', 'a'), ('Ă', 'A'),
        ('â', 'a'), ('Â', 'A'),
        ('ê', 'e'), ('Ê', 'E'),
        ('ô', 'o'), ('Ô', 'O'),
        ('ơ', 'o'), ('Ơ', 'O'),
        ('ư', 'u'), ('Ư', 'U'),
        ('đ', 'd'), ('Đ', 'D'),
        ('ñ', 'n'),  # OCR sometimes reads nh as ñ
        ('ḥ', 'h'),  # OCR artifact
        ('ọ', 'o'),  # Partial diacritic
        ('ị', 'i'),
        ('q', 'g'),  # Common OCR confusion
        ('rn', 'm'),  # "rn" looks like "m"
        ('vv', 'w'),  # "vv" looks like "w"
        ('cl', 'd'),  # "cl" looks like "d"
        ('0', 'o'), ('O', '0'),  # Number/letter confusion
        ('1', 'l'), ('l', '1'),
        ('5', 's'), ('S', '5'),
    ]
    
    # Apply each replacement once
    for old, new in replacements:
        if old in text:
            typos.add(text.replace(old, new, 1))
    
    return list(typos)


def generate_all_variants(keyword: str, include_typos: bool = True) -> List[str]:
    """
    Generate all variants for a keyword
    
    Args:
        keyword: Original keyword
        include_typos: Whether to include OCR typo variants
        
    Returns:
        List of unique variants (removes duplicates)
    """
    variants = set()
    
    # Original keyword
    variants.add(keyword)
    
    # Case variants of original
    for case_variant in generate_case_variants(keyword):
        variants.add(case_variant)
    
    # Remove diacritics version
    no_diacritics = remove_diacritics(keyword)
    variants.add(no_diacritics)
    
    # Case variants of no-diacritics version
    for case_variant in generate_case_variants(no_diacritics):
        variants.add(case_variant)
    
    # OCR typos (optional)
    if include_typos:
        # Typos of original
        for typo in generate_ocr_typos(keyword):
            variants.add(typo)
            # Case variants of typos
            for case_variant in generate_case_variants(typo):
                variants.add(case_variant)
        
        # Typos of no-diacritics version
        for typo in generate_ocr_typos(no_diacritics):
            variants.add(typo)
    
    # Remove empty strings and strip whitespace
    variants = {v.strip() for v in variants if v.strip()}
    
    # Sort for consistent output
    return sorted(list(variants))


def generate_variants_for_keywords(keywords: List[str], include_typos: bool = True) -> List[str]:
    """
    Generate variants for a list of keywords
    
    Args:
        keywords: List of original keywords
        include_typos: Whether to include OCR typo variants
        
    Returns:
        List of all unique variants (deduplicated)
    """
    all_variants = set()
    
    for keyword in keywords:
        variants = generate_all_variants(keyword, include_typos)
        all_variants.update(variants)
    
    return sorted(list(all_variants))


# CLI interface
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python keyword_variants.py <keyword> [include_typos]",
            "success": False
        }))
        sys.exit(1)
    
    keyword = sys.argv[1]
    include_typos = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True
    
    try:
        variants = generate_all_variants(keyword, include_typos)
        print(json.dumps({
            "success": True,
            "keyword": keyword,
            "variants": variants,
            "count": len(variants)
        }, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)
