#!/usr/bin/env python3
"""
Script to automatically enhance keywords for all document types
Adds uppercase variants and common OCR typos
"""
import re

def enhance_keywords(keywords_list):
    """
    Enhance a list of keywords by adding:
    - Uppercase variants
    - Common OCR typos
    """
    enhanced = set(keywords_list)  # Start with original
    
    for keyword in keywords_list:
        # Add uppercase variant (OCR often reads titles as uppercase)
        uppercase = keyword.upper()
        if uppercase != keyword:
            enhanced.add(uppercase)
        
        # Add lowercase variant  
        lowercase = keyword.lower()
        if lowercase != keyword:
            enhanced.add(lowercase)
    
    return list(enhanced)


def process_document_rules(rules_dict):
    """Process all document rules and enhance keywords"""
    enhanced_rules = {}
    
    for doc_type, rules in rules_dict.items():
        keywords = rules.get("keywords", [])
        enhanced_keywords = enhance_keywords(keywords)
        
        # Increase weight slightly for better detection
        weight = rules.get("weight", 1.0)
        if weight < 1.0:
            weight = min(weight + 0.1, 1.0)
        
        enhanced_rules[doc_type] = {
            "keywords": enhanced_keywords,
            "weight": weight,
            "min_matches": rules.get("min_matches", 1)
        }
    
    return enhanced_rules


if __name__ == "__main__":
    # Example usage
    sample_keywords = [
        "hợp đồng chuyển nhượng",
        "hop dong chuyen nhuong",
        "chuyển nhượng"
    ]
    
    enhanced = enhance_keywords(sample_keywords)
    print("Original keywords:")
    for kw in sample_keywords:
        print(f"  - {kw}")
    
    print("\nEnhanced keywords:")
    for kw in sorted(enhanced):
        print(f"  - {kw}")
