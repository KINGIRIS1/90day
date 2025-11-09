#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Document Processor - Multi-Image Analysis
Supports 2 modes:
- Mode 1: Fixed batch size (5 images per batch)
- Mode 2: Smart batching (group by document boundaries)
"""

import sys
import os
import json
import base64
import re
import requests
from PIL import Image
import io

# Import existing engines
from ocr_engine_gemini_flash import resize_image_smart, parse_gemini_response


def encode_image_base64(image_path, max_width=1500, max_height=2100):
    """Encode image to base64 with smart resize"""
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize
        resized_img, resize_info = resize_image_smart(img, max_width, max_height)
        
        # Encode to base64
        buffer = io.BytesIO()
        resized_img.save(buffer, format='JPEG', quality=95)
        img_bytes = buffer.getvalue()
        encoded = base64.b64encode(img_bytes).decode('utf-8')
        
        return encoded, resize_info
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}", file=sys.stderr)
        return None, None


def get_multi_image_prompt():
    """Get prompt for multi-image batch analysis"""
    return """Bạn đang phân tích nhiều trang scan tài liệu đất đai Việt Nam (có thể thuộc 1 hoặc nhiều tài liệu khác nhau).

NHIỆM VỤ:
1. Xác định có BAO NHIÊU tài liệu khác nhau trong các trang này
2. Nhóm các trang theo tài liệu
3. Phân loại loại tài liệu của từng nhóm
4. Trích xuất metadata (ngày cấp cho GCN, màu sắc, v.v.)

DẤU HIỆU NHẬN BIẾT:

Trang 1 của tài liệu:
- Có TIÊU ĐỀ CHÍNH ở đầu trang (20% đầu)
- Rõ ràng, đầy đủ (ví dụ: "HỢP ĐỒNG CHUYỂN NHƯỢNG", "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT")
- Có quốc huy (đối với GCN)
- Khác biệt rõ ràng về format/màu sắc với trang trước

Trang tiếp nối (trang 2, 3, 4...):
- KHÔNG có tiêu đề chính ở đầu
- Có section headers (II., III., IV., "Điều 2", "Phần II", "Mục III")
- Cùng format/màu sắc với trang trước
- Nội dung liên tục (điều khoản, sơ đồ, bảng biểu)

Ranh giới giữa các tài liệu:
- Thay đổi rõ rệt về màu giấy (hồng → trắng, đỏ → hồng)
- Xuất hiện tiêu đề chính mới
- Thay đổi hoàn toàn về định dạng

CÁC LOẠI TÀI LIỆU CHÍNH (98 loại):
- GCN, GCNM, GCNC: Giấy chứng nhận (có quốc huy, 3 dòng tiêu đề)
- HDCQ: Hợp đồng chuyển nhượng, tặng cho
- DDKBD: Đơn đăng ký biến động
- HSKT: Hồ sơ kỹ thuật
- (và 94 loại khác...)

QUAN TRỌNG - ĐỐI VỚI GCN:
- Tìm NGÀY CẤP (có thể ở trang 1 HOẶC trang 2)
- Xác định MÀU (đỏ/cam = cũ, hồng = mới)
- Ngày cấp thường ở bottom, gần chữ ký/con dấu

OUTPUT JSON:
{
  "documents": [
    {
      "type": "HDCQ",
      "pages": [0, 1, 2],
      "confidence": 0.95,
      "reasoning": "3 trang đầu cùng format, trang 0 có tiêu đề 'HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT'",
      "metadata": {}
    },
    {
      "type": "GCN",
      "pages": [3, 4],
      "confidence": 0.98,
      "reasoning": "Trang 3-4 là GCN màu hồng, có quốc huy, tìm thấy ngày cấp ở trang 4",
      "metadata": {
        "color": "pink",
        "issue_date": "27/10/2021",
        "issue_date_confidence": "full"
      }
    }
  ]
}

Lưu ý:
- pages dùng 0-indexed (trang đầu tiên = 0)
- Nếu không chắc chắn, đánh dấu confidence thấp
- Nếu chỉ có 1 tài liệu, vẫn trả về array với 1 phần tử
"""


def batch_classify_fixed(image_paths, api_key, batch_size=5):
    """
    Phương án 1: Fixed Batch Size
    Gom mỗi 5 files và gửi cùng lúc
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🔄 BATCH MODE 1: Fixed Batch Size ({batch_size} images per batch)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    all_results = []
    total_batches = (len(image_paths) + batch_size - 1) // batch_size
    
    for batch_idx in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[batch_idx:batch_idx + batch_size]
        batch_num = batch_idx // batch_size + 1
        
        print(f"\n📦 Batch {batch_num}/{total_batches}: Processing {len(batch_paths)} images", file=sys.stderr)
        for i, path in enumerate(batch_paths):
            print(f"   [{i}] {os.path.basename(path)}", file=sys.stderr)
        
        # Encode all images in batch
        print(f"🖼️ Encoding {len(batch_paths)} images...", file=sys.stderr)
        encoded_images = []
        for path in batch_paths:
            encoded, resize_info = encode_image_base64(path)
            if encoded:
                encoded_images.append(encoded)
                print(f"   ✅ {os.path.basename(path)}: {resize_info.get('original_size', 'N/A')} → {resize_info.get('new_size', 'N/A')}", file=sys.stderr)
            else:
                print(f"   ❌ Failed to encode {os.path.basename(path)}", file=sys.stderr)
        
        if not encoded_images:
            print(f"❌ No valid images in batch {batch_num}", file=sys.stderr)
            continue
        
        # Build multi-image payload
        parts = [{"text": get_multi_image_prompt()}]
        for img_data in encoded_images:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_data
                }
            })
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "topK": 10,
                "maxOutputTokens": 4000  # Larger for multi-document response
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
        }
        
        # Call Gemini API
        print(f"📡 Sending batch request to Gemini Flash...", file=sys.stderr)
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        try:
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            result_data = response.json()
            
            print(f"📊 Response status: {response.status_code}", file=sys.stderr)
            
            # Parse response
            if 'candidates' in result_data and len(result_data['candidates']) > 0:
                candidate = result_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        response_text = parts[0]['text']
                        
                        print(f"📄 Raw response preview: {response_text[:200]}...", file=sys.stderr)
                        
                        # Extract JSON from response - try multiple patterns
                        json_match = re.search(r'\{[\s\S]*"documents"[\s\S]*\}', response_text)
                        if not json_match:
                            # Try finding JSON with triple backticks
                            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text)
                            if json_match:
                                response_text = json_match.group(1)
                            else:
                                # Try finding any JSON object
                                json_match = re.search(r'(\{[\s\S]*\})', response_text)
                                if json_match:
                                    response_text = json_match.group(1)
                        else:
                            response_text = json_match.group(0)
                        
                        if response_text:
                            try:
                                batch_result = json.loads(response_text)
                            
                            print(f"✅ Batch {batch_num} complete:", file=sys.stderr)
                            for doc in batch_result.get('documents', []):
                                doc_type = doc.get('type', 'UNKNOWN')
                                pages = doc.get('pages', [])
                                confidence = doc.get('confidence', 0)
                                print(f"   📄 {doc_type}: {len(pages)} pages, confidence {confidence:.0%}", file=sys.stderr)
                            
                            # Map results back to original file paths
                            for doc in batch_result.get('documents', []):
                                for page_idx in doc.get('pages', []):
                                    if page_idx < len(batch_paths):
                                        file_path = batch_paths[page_idx]
                                        all_results.append({
                                            'file_path': file_path,
                                            'file_name': os.path.basename(file_path),
                                            'short_code': doc.get('type', 'UNKNOWN'),
                                            'confidence': doc.get('confidence', 0.5),
                                            'reasoning': doc.get('reasoning', ''),
                                            'metadata': doc.get('metadata', {}),
                                            'method': 'batch_fixed',
                                            'batch_num': batch_num
                                        })
                        else:
                            print(f"⚠️ No valid JSON in response", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Batch {batch_num} error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✅ BATCH MODE 1 COMPLETE: {len(all_results)} files processed", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    return all_results


def quick_scan_tier1(image_path, api_key):
    """Quick scan với Tier 1 để detect document boundaries"""
    from ocr_engine_gemini_flash import classify_document_gemini_flash
    
    try:
        result = classify_document_gemini_flash(
            image_path=image_path,
            api_key=api_key,
            crop_top_percent=0.60,
            model_type='gemini-flash-lite',
            enable_resize=True,
            max_width=1500,
            max_height=2100
        )
        return result
    except Exception as e:
        print(f"Quick scan error for {image_path}: {e}", file=sys.stderr)
        return {'short_code': 'ERROR', 'confidence': 0}


def group_by_document(quick_results, file_paths):
    """
    Nhóm files thành documents dựa trên quick scan results
    Returns: List of document groups [[0,1,2], [3,4], [5,6,7,8], ...]
    """
    print(f"\n🧠 Analyzing document boundaries...", file=sys.stderr)
    
    groups = []
    current_group = [0]
    last_type = quick_results[0].get('short_code', 'UNKNOWN')
    
    for i in range(1, len(quick_results)):
        result = quick_results[i]
        short_code = result.get('short_code', 'UNKNOWN')
        confidence = result.get('confidence', 0)
        reasoning = result.get('reasoning', '').lower()
        
        # Check if this is a new document
        is_new_document = False
        
        # High confidence with clear title → New document
        if confidence >= 0.8 and short_code != 'UNKNOWN':
            is_new_document = True
            print(f"   📄 [{i}] New document detected: {short_code} ({confidence:.0%})", file=sys.stderr)
        
        # Low confidence + continuation indicators → Same document
        elif confidence < 0.5 and any(kw in reasoning for kw in ['section header', 'ii.', 'iii.', 'thửa đất']):
            is_new_document = False
            print(f"   ➡️ [{i}] Continuation page: {short_code} ({confidence:.0%})", file=sys.stderr)
        
        # Borderline case - use confidence
        else:
            is_new_document = (confidence >= 0.7)
            print(f"   ❓ [{i}] Borderline: {short_code} ({confidence:.0%}) → {'New' if is_new_document else 'Continue'}", file=sys.stderr)
        
        if is_new_document:
            # Start new group
            groups.append(current_group)
            current_group = [i]
            last_type = short_code
        else:
            # Continue current group
            current_group.append(i)
    
    # Add last group
    if current_group:
        groups.append(current_group)
    
    print(f"\n✅ Grouped into {len(groups)} documents:", file=sys.stderr)
    for g_idx, group in enumerate(groups):
        print(f"   Document {g_idx + 1}: {len(group)} pages {group}", file=sys.stderr)
    
    return groups


def batch_classify_smart(image_paths, api_key):
    """
    Phương án 2: Smart Batching
    Quét nhanh tất cả → Nhóm theo document → Gửi từng nhóm
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🧠 BATCH MODE 2: Smart Batching (Group by Document)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    # Step 1: Quick scan all images
    print(f"\n📊 STEP 1: Quick scan {len(image_paths)} images...", file=sys.stderr)
    quick_results = []
    for i, path in enumerate(image_paths):
        print(f"   [{i+1}/{len(image_paths)}] Scanning {os.path.basename(path)}...", file=sys.stderr)
        result = quick_scan_tier1(path, api_key)
        quick_results.append(result)
        print(f"      → {result.get('short_code')} ({result.get('confidence', 0):.0%})", file=sys.stderr)
    
    # Step 2: Group by document
    print(f"\n📊 STEP 2: Grouping by document boundaries...", file=sys.stderr)
    document_groups = group_by_document(quick_results, image_paths)
    
    # Step 3: Process each document group
    print(f"\n📊 STEP 3: Detailed analysis of {len(document_groups)} documents...", file=sys.stderr)
    all_results = []
    
    for doc_idx, group_indices in enumerate(document_groups):
        group_paths = [image_paths[i] for i in group_indices]
        
        print(f"\n📄 Document {doc_idx + 1}/{len(document_groups)}: {len(group_paths)} pages", file=sys.stderr)
        
        # Use fixed batch for this document
        group_results = batch_classify_fixed(group_paths, api_key, batch_size=len(group_paths))
        all_results.extend(group_results)
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✅ BATCH MODE 2 COMPLETE: {len(all_results)} files processed in {len(document_groups)} documents", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    return all_results


# CLI interface for testing
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python batch_processor.py <mode> <api_key> <image1> <image2> ...", file=sys.stderr)
        print("Modes: fixed, smart", file=sys.stderr)
        print("Example: python batch_processor.py fixed AIza... img1.jpg img2.jpg img3.jpg", file=sys.stderr)
        sys.exit(1)
    
    mode = sys.argv[1]
    api_key = sys.argv[2]
    image_paths = sys.argv[3:]
    
    print(f"🔍 Batch processing {len(image_paths)} images in '{mode}' mode", file=sys.stderr)
    
    if mode == 'fixed':
        results = batch_classify_fixed(image_paths, api_key, batch_size=5)
    elif mode == 'smart':
        results = batch_classify_smart(image_paths, api_key)
    else:
        print(f"❌ Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
    
    # Output JSON to stdout for IPC
    print(json.dumps(results, ensure_ascii=False))
    
    print(f"\n📊 BATCH COMPLETE: {len(results)} files processed", file=sys.stderr)
