#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash Two-Tier Hybrid Engine
Optimizes cost and accuracy by using:
- Tier 1: Flash Lite (60% crop) for easy documents
- Tier 2: Flash Full (100% image) for complex documents or low confidence
"""

import sys
import os

# Import existing Flash engines
from ocr_engine_gemini_flash import classify_document_gemini_flash


def classify_document_gemini_flash_hybrid(
    image_path, 
    api_key, 
    confidence_threshold=0.80,
    complex_doc_types=['GCN', 'GCNM', 'GCNC'],
    enable_resize=True,
    max_width=1500,
    max_height=2100
):
    """
    Two-Tier Hybrid OCR Classification Engine
    
    Strategy:
    - Tier 1: Use Flash Lite (60% crop, simplified prompt) for fast, cheap classification
    - Tier 2: Escalate to Flash Full (100% image, full 98-rule prompt) if:
        * Confidence < threshold (default 80%)
        * Document type is complex (e.g., GCN requires date extraction)
    
    Args:
        image_path: Path to image file
        api_key: Google API key (BYOK)
        confidence_threshold: Minimum confidence to accept Tier 1 result (default: 0.80)
        complex_doc_types: Document types that always trigger Tier 2 (default: GCN variants)
        enable_resize: Enable smart resizing to reduce costs (default: True)
        max_width: Maximum width for resize (default: 1500)
        max_height: Maximum height for resize (default: 2100)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning, tier_used
    """
    
    print("=" * 80, file=sys.stderr)
    print("🔄 TWO-TIER HYBRID ENGINE STARTED", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # ==================== TIER 1: FLASH LITE (Fast & Cheap) ====================
    print("\n📊 TIER 1: Flash Lite - Quick Scan (60% crop, simplified rules)", file=sys.stderr)
    print(f"   ├─ Model: gemini-2.5-flash-lite", file=sys.stderr)
    print(f"   ├─ Crop: 60% top", file=sys.stderr)
    print(f"   ├─ Cost: ~$0.08/1K images", file=sys.stderr)
    print(f"   └─ Target: Easy documents (HDCQ, DDKBD, etc.)", file=sys.stderr)
    
    try:
        tier1_result = classify_document_gemini_flash(
            image_path=image_path,
            api_key=api_key,
            crop_top_percent=0.60,  # 60% crop for speed/cost
            model_type='gemini-flash-lite',
            enable_resize=enable_resize,
            max_width=max_width,
            max_height=max_height
        )
        
        # Extract Tier 1 results
        tier1_code = tier1_result.get('short_code', 'UNKNOWN')
        tier1_confidence = tier1_result.get('confidence', 0)
        tier1_reasoning = tier1_result.get('reasoning', '')
        
        print(f"\n✅ TIER 1 COMPLETE:", file=sys.stderr)
        print(f"   ├─ Classification: {tier1_code}", file=sys.stderr)
        print(f"   ├─ Confidence: {tier1_confidence:.2%}", file=sys.stderr)
        print(f"   └─ Reasoning: {tier1_reasoning[:100]}...", file=sys.stderr)
        
        # Check if Tier 1 result is acceptable
        needs_tier2 = False
        escalation_reason = ""
        
        # Reason 1: Low confidence
        if tier1_confidence < confidence_threshold:
            needs_tier2 = True
            escalation_reason = f"Low confidence ({tier1_confidence:.2%} < {confidence_threshold:.2%})"
            print(f"\n⚠️ ESCALATION TRIGGER: {escalation_reason}", file=sys.stderr)
        
        # Reason 2: Complex document type (e.g., GCN requires date extraction)
        elif tier1_code in complex_doc_types:
            needs_tier2 = True
            escalation_reason = f"Complex document type ({tier1_code} requires date extraction from full image)"
            print(f"\n⚠️ ESCALATION TRIGGER: {escalation_reason}", file=sys.stderr)
            print(f"   📋 GCN Special: Will scan 100% full image to extract issue_date", file=sys.stderr)
        
        # Reason 3: ERROR or UNKNOWN with very low confidence
        # BUT: Check if this is GCN continuation page (section headers, no title)
        elif tier1_code in ['ERROR', 'UNKNOWN'] and tier1_confidence < 0.5:
            # Check reasoning for GCN continuation indicators
            is_gcn_continuation = any(keyword in tier1_reasoning.lower() for keyword in [
                'section header',
                'thửa đất',
                'sơ đồ thửa đất',
                'ii.',
                'iii.',
                'iv.'
            ])
            
            if is_gcn_continuation:
                # This is likely GCN page 2/3 - no need for Tier 2
                print(f"\n💡 DETECTED GCN CONTINUATION PAGE - SKIP TIER 2", file=sys.stderr)
                print(f"   ├─ Reasoning contains: section headers (II., III., etc.)", file=sys.stderr)
                print(f"   ├─ This is likely GCN page 2/3 (no title, no date)", file=sys.stderr)
                print(f"   └─ Will be auto-classified via sequential naming", file=sys.stderr)
                
                # Keep UNKNOWN for now, sequential naming will fix it
                tier1_result['tier_used'] = 'tier1_only'
                tier1_result['tier1_confidence'] = tier1_confidence
                tier1_result['escalation_reason'] = 'GCN continuation page detected - no escalation needed'
                tier1_result['cost_estimate'] = 'low'
                
                return tier1_result
            else:
                needs_tier2 = True
                escalation_reason = f"Uncertain classification ({tier1_code} with {tier1_confidence:.2%} confidence)"
                print(f"\n⚠️ ESCALATION TRIGGER: {escalation_reason}", file=sys.stderr)
        
        # If Tier 1 is good enough, return immediately
        if not needs_tier2:
            print(f"\n✅ TIER 1 ACCEPTED - No escalation needed", file=sys.stderr)
            print(f"   ├─ Confidence: {tier1_confidence:.2%} ≥ threshold ({confidence_threshold:.2%})", file=sys.stderr)
            print(f"   ├─ Document type: {tier1_code} (not complex)", file=sys.stderr)
            print(f"   └─ Cost: ~$0.08/1K (Tier 1 only)", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            # Add tier metadata
            tier1_result['tier_used'] = 'tier1_only'
            tier1_result['tier1_confidence'] = tier1_confidence
            tier1_result['escalation_reason'] = 'none'
            tier1_result['cost_estimate'] = 'low'  # Flash Lite only
            
            return tier1_result
        
    except Exception as e:
        print(f"❌ TIER 1 ERROR: {e}", file=sys.stderr)
        # If Tier 1 fails, force escalation to Tier 2
        needs_tier2 = True
        escalation_reason = f"Tier 1 error: {str(e)}"
        tier1_result = {
            'short_code': 'ERROR',
            'confidence': 0,
            'reasoning': str(e)
        }
        tier1_code = 'ERROR'
        tier1_confidence = 0
    
    # ==================== TIER 2: FLASH FULL (Thorough & Accurate) ====================
    print(f"\n📊 TIER 2: Flash Full - Detailed Analysis (100% image, 98 rules)", file=sys.stderr)
    print(f"   ├─ Model: gemini-2.5-flash", file=sys.stderr)
    print(f"   ├─ Crop: 100% (full image)", file=sys.stderr)
    print(f"   ├─ Cost: ~$0.16/1K images", file=sys.stderr)
    print(f"   ├─ Target: Complex documents (GCN, low confidence)", file=sys.stderr)
    print(f"   └─ Reason: {escalation_reason}", file=sys.stderr)
    
    try:
        tier2_result = classify_document_gemini_flash(
            image_path=image_path,
            api_key=api_key,
            crop_top_percent=1.0,  # 100% - full image
            model_type='gemini-flash',  # Full Flash model
            enable_resize=enable_resize,
            max_width=max_width,
            max_height=max_height
        )
        
        # Extract Tier 2 results
        tier2_code = tier2_result.get('short_code', 'UNKNOWN')
        tier2_confidence = tier2_result.get('confidence', 0)
        tier2_reasoning = tier2_result.get('reasoning', '')
        
        print(f"\n✅ TIER 2 COMPLETE:", file=sys.stderr)
        print(f"   ├─ Classification: {tier2_code}", file=sys.stderr)
        print(f"   ├─ Confidence: {tier2_confidence:.2%}", file=sys.stderr)
        print(f"   └─ Reasoning: {tier2_reasoning[:100]}...", file=sys.stderr)
        
        # Compare Tier 1 vs Tier 2
        # 🔧 FIX: If Tier 2 fails or returns worse result than Tier 1, keep Tier 1
        tier2_failed = (
            tier2_code == 'UNKNOWN' and 
            tier1_code != 'UNKNOWN' and 
            tier2_confidence < tier1_confidence
        )
        
        if tier2_failed:
            print(f"\n⚠️ TIER 2 WORSE THAN TIER 1 - KEEPING TIER 1 RESULT:", file=sys.stderr)
            print(f"   ├─ Tier 1: {tier1_code} ({tier1_confidence:.2%}) ✅ FINAL", file=sys.stderr)
            print(f"   └─ Tier 2: {tier2_code} ({tier2_confidence:.2%}) ❌ DISCARDED", file=sys.stderr)
            print(f"   └─ Reason: Tier 2 parse failed or returned UNKNOWN with lower confidence", file=sys.stderr)
            
            # Return Tier 1 result with Tier 2 metadata
            tier1_result['tier_used'] = 'tier2_fallback_to_tier1'
            tier1_result['tier1_confidence'] = tier1_confidence
            tier1_result['tier2_confidence'] = tier2_confidence
            tier1_result['tier2_failed'] = True
            tier1_result['tier2_error_reason'] = 'Parse failed or UNKNOWN with lower confidence'
            tier1_result['escalation_reason'] = escalation_reason
            tier1_result['cost_estimate'] = 'medium'  # Both tiers used but Tier 1 kept
            
            print(f"\n💰 COST SUMMARY:", file=sys.stderr)
            print(f"   ├─ Tier 1 (Flash Lite): ~$0.08/1K", file=sys.stderr)
            print(f"   ├─ Tier 2 (Flash Full): ~$0.16/1K (failed)", file=sys.stderr)
            print(f"   └─ Total: ~$0.24/1K (kept Tier 1 result)", file=sys.stderr)
            print(f"\n🛡️ FALLBACK PROTECTION:", file=sys.stderr)
            print(f"   └─ Tier 1 result preserved: {tier1_code} ({tier1_confidence:.2%})", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            return tier1_result
        
        # Normal case: Tier 2 succeeded
        if tier1_code != 'ERROR' and tier2_code != tier1_code:
            print(f"\n🔄 CLASSIFICATION CHANGED:", file=sys.stderr)
            print(f"   ├─ Tier 1: {tier1_code} ({tier1_confidence:.2%})", file=sys.stderr)
            print(f"   └─ Tier 2: {tier2_code} ({tier2_confidence:.2%}) ✅ FINAL", file=sys.stderr)
        else:
            print(f"\n✅ CLASSIFICATION CONFIRMED:", file=sys.stderr)
            print(f"   ├─ Both tiers agree: {tier2_code}", file=sys.stderr)
            print(f"   └─ Confidence improved: {tier1_confidence:.2%} → {tier2_confidence:.2%}", file=sys.stderr)
        
        # Add tier metadata to final result
        tier2_result['tier_used'] = 'tier2_full'
        tier2_result['tier1_result'] = {
            'short_code': tier1_code,
            'confidence': tier1_confidence,
            'reasoning': tier1_reasoning
        }
        tier2_result['tier1_confidence'] = tier1_confidence
        tier2_result['tier2_confidence'] = tier2_confidence
        tier2_result['escalation_reason'] = escalation_reason
        tier2_result['cost_estimate'] = 'medium'  # Both tiers used
        tier2_result['confidence_improvement'] = tier2_confidence - tier1_confidence
        
        print(f"\n💰 COST SUMMARY:", file=sys.stderr)
        print(f"   ├─ Tier 1 (Flash Lite): ~$0.08/1K", file=sys.stderr)
        print(f"   ├─ Tier 2 (Flash Full): ~$0.16/1K", file=sys.stderr)
        print(f"   └─ Total: ~$0.24/1K (vs $0.16/1K Flash Full only)", file=sys.stderr)
        print(f"\n📊 ACCURACY IMPROVEMENT:", file=sys.stderr)
        print(f"   └─ Confidence: {tier1_confidence:.2%} → {tier2_confidence:.2%} (+{(tier2_confidence - tier1_confidence):.2%})", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        
        return tier2_result
        
    except Exception as e:
        print(f"❌ TIER 2 ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # If Tier 2 also fails, return Tier 1 result with error flag
        print(f"\n⚠️ Falling back to Tier 1 result", file=sys.stderr)
        tier1_result['tier_used'] = 'tier1_fallback'
        tier1_result['tier2_error'] = str(e)
        tier1_result['escalation_reason'] = escalation_reason
        tier1_result['cost_estimate'] = 'low'
        
        return tier1_result


# CLI interface for testing
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr_engine_gemini_flash_hybrid.py <image_path> <api_key> [confidence_threshold]")
        print("Example: python ocr_engine_gemini_flash_hybrid.py test.jpg AIza... 0.80")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    confidence_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.80
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"\n🔍 Testing Hybrid Engine:")
    print(f"   ├─ Image: {image_path}")
    print(f"   ├─ Confidence threshold: {confidence_threshold:.2%}")
    print(f"   └─ Complex doc types: GCN, GCNM, GCNC\n")
    
    result = classify_document_gemini_flash_hybrid(
        image_path=image_path,
        api_key=api_key,
        confidence_threshold=confidence_threshold
    )
    
    print("\n📊 FINAL RESULT:")
    print(f"   ├─ Classification: {result.get('short_code')}")
    print(f"   ├─ Confidence: {result.get('confidence'):.2%}")
    print(f"   ├─ Tier used: {result.get('tier_used')}")
    print(f"   ├─ Cost estimate: {result.get('cost_estimate')}")
    print(f"   └─ Reasoning: {result.get('reasoning')}")
    
    if result.get('tier_used') == 'tier2_full':
        print(f"\n🔄 Tier Comparison:")
        print(f"   ├─ Tier 1: {result.get('tier1_result', {}).get('short_code')} ({result.get('tier1_confidence', 0):.2%})")
        print(f"   ├─ Tier 2: {result.get('short_code')} ({result.get('tier2_confidence', 0):.2%})")
        print(f"   └─ Improvement: +{result.get('confidence_improvement', 0):.2%}")
