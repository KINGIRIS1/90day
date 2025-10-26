#!/usr/bin/env python3
"""
Batch enhancement script for all document rules
Automatically adds uppercase variants to ALL document types
"""
import re

# Read the original file
with open('/app/desktop-app/python/rule_classifier.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match document type rules
pattern = r'("[\w]+"):\s*\{[^}]*"keywords":\s*\[(.*?)\]'

def enhance_keyword_section(match):
    """Enhance a single document type's keywords"""
    doc_type = match.group(1)
    keywords_str = match.group(2)
    
    # Skip if already has uppercase variants (check for "# Viết hoa" comment)
    if "# Viết hoa" in keywords_str or "VIẾT HOA" in keywords_str:
        return match.group(0)  # Return unchanged
    
    # Extract individual keywords
    keywords = re.findall(r'"([^"]+)"', keywords_str)
    
    # Generate uppercase variants for Vietnamese keywords (not English abbreviations)
    uppercase_keywords = []
    for kw in keywords:
        # Only add uppercase if keyword contains Vietnamese characters or is long enough
        if any(c in kw for c in 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'):
            upper = kw.upper()
            if upper not in keywords and upper not in uppercase_keywords:
                uppercase_keywords.append(upper)
    
    # If we found uppercase variants, add them
    if uppercase_keywords:
        # Build the enhanced keyword list
        enhanced_str = keywords_str.rstrip()
        if not enhanced_str.endswith(','):
            enhanced_str += ','
        enhanced_str += '\n            # Viết hoa (auto-generated)\n'
        for uk in uppercase_keywords[:10]:  # Limit to top 10 to avoid bloat
            enhanced_str += f'            "{uk}",\n'
        enhanced_str = enhanced_str.rstrip(',\n') + '\n        '
        
        # Replace in the match
        result = match.group(0).replace(keywords_str, enhanced_str)
        return result
    
    return match.group(0)

# Apply enhancement
enhanced_content = re.sub(
    pattern,
    enhance_keyword_section,
    content,
    flags=re.DOTALL
)

# Write back
with open('/app/desktop-app/python/rule_classifier_enhanced.py', 'w', encoding='utf-8') as f:
    f.write(enhanced_content)

print("✅ Enhancement complete!")
print("📄 Output saved to: rule_classifier_enhanced.py")
print("📊 Review the file and replace original if satisfied")
