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

# Import existing engines and prompts
from ocr_engine_gemini_flash import (
    resize_image_smart, 
    parse_gemini_response,
    get_classification_prompt,
    get_classification_prompt_lite
)


def adapt_prompt_for_multi_image(single_image_prompt, batch_size):
    """
    Adapt single-image prompt to multi-image batch context
    
    Changes:
    1. Add multi-image context introduction
    2. Add document grouping instructions
    3. Change output format from single result to documents array
    4. Add page indexing (0-indexed)
    5. Emphasize MUST return ALL pages
    """
    
    multi_image_intro = f"""🎯 BATCH ANALYSIS - {batch_size} TRANG SCAN

Bạn đang phân tích {batch_size} trang scan tài liệu đất đai Việt Nam.
Các trang này có thể thuộc 1 hoặc nhiều tài liệu khác nhau.

NHIỆM VỤ:
1. Xác định có BAO NHIÊU tài liệu khác nhau trong {batch_size} trang này
2. Nhóm các trang theo tài liệu (pages array)
3. Phân loại loại tài liệu của từng nhóm
4. Trích xuất metadata (ngày cấp cho GCN, màu sắc, v.v.)

DẤU HIỆU NHẬN BIẾT:

TRANG 1 CỦA TÀI LIỆU (New Document):
- Có TIÊU ĐỀ CHÍNH ở TOP 30% (đầu trang)
- Cỡ chữ LỚN, IN HOA, căn giữa
- Có quốc huy (đối với GCN)
- Khác biệt rõ về format/màu sắc so với trang trước

TRANG TIẾP NỐI (Continuation - Trang 2, 3, 4...):
- KHÔNG có tiêu đề chính ở đầu
- Chỉ có section headers: "II.", "III.", "ĐIỀU 2", "PHẦN II"
- Cùng format/màu sắc với trang trước
- Nội dung liên tục (điều khoản, chữ ký, bảng biểu)

🚨 QUAN TRỌNG - NHẬN DIỆN CONTINUATION PAGES:
Các dấu hiệu sau = CONTINUATION (trang tiếp theo, KHÔNG phải document mới):
1. Section headers với số: "II.", "III.", "IV.", "V.", "ĐIỀU 2", "ĐIỀU 3", "PHẦN II", "MỤC III"
2. Bảng biểu với số phân cấp: "4.1", "4.2", "4.2.1", "4.2.2", "(1.1)", "(2.1.3)"
3. Text body tiếp nối: "...tiếp theo...", "...như sau:", danh sách bullet points
4. Chữ ký/con dấu ở cuối trang
5. Không có header chính thức (quốc huy, cơ quan ban hành)

VÍ DỤ CONTINUATION - PHẢI GOM VÀO DOCUMENT TRƯỚC:
✅ "III. TÍNH THUẾ CỦA CƠ QUAN THUẾ" + bảng 4.1, 4.2
   → Section header với số La Mã
   → Bảng biểu phân cấp
   → Đây là continuation của document trước (có thể là TBT, HDCQ, etc.)
   → KHÔNG classify thành UNKNOWN
   → GOM VÀO document có trang trước đó
   
   VÍ DỤ CỤ THỂ:
   Page 4 (index 4): "THÔNG BÁO THUẾ" (title) → TBT
   Page 5 (index 5): "ĐIỀU 1: ..." → TBT continuation
   Page 6 (index 6): "III. TÍNH THUẾ" + bảng 4.1 → TBT continuation ✅ (KHÔNG phải UNKNOWN)
   
   Result: {"type": "TBT", "pages": [4, 5, 6], ...}

✅ "ĐIỀU 2: NỘI DUNG THỎA THUẬN PHÂN CHIA"
   → Section header
   → Continuation của TTHGD hoặc PCTSVC
   → GOM VÀO document trước

✅ Trang chỉ có bảng biểu (không có title)
   → Continuation
   → GOM VÀO document trước

✅ Trang có "1.1 Trường hợp...", "1.2 Trường hợp..." (numbered list)
   → Continuation với structured content
   → GOM VÀO document trước

❌ SAI - Classify continuation thành UNKNOWN:
Page 5: "THÔNG BÁO THUẾ" (title)
Page 6: "III. TÍNH THUẾ" + bảng
→ AI classify:
  {"type": "TBT", "pages": [5]},
  {"type": "UNKNOWN", "pages": [6]}  ❌ SAI!
→ ĐÚNG:
  {"type": "TBT", "pages": [5, 6]}  ✅

RANH GIỚI GIỮA CÁC TÀI LIỆU:
- Thay đổi rõ rệt: màu giấy (hồng → trắng), format khác
- Xuất hiện tiêu đề chính mới ở TOP
- Layout hoàn toàn khác

---

"""

    unknown_rules = f"""

⚠️ QUAN TRỌNG - KHI NÀO TRẢ VỀ "UNKNOWN":
CHỈ trả về "UNKNOWN" khi:
1. Trang thực sự không có tiêu đề VÀ không match continuation patterns
2. Title không thuộc 98 loại VÀ không phải continuation
3. Trang hoàn toàn trống hoặc không đọc được

❌ KHÔNG trả về "UNKNOWN" cho:
- Trang có section headers (III., ĐIỀU 2) → Continuation, gom vào doc trước
- Trang có bảng biểu structured → Continuation, gom vào doc trước
- Trang có text liên tục với trang trước → Continuation, gom vào doc trước

🎯 NGUYÊN TẮC: Khi nghi ngờ → Gom vào document trước (safer than creating new UNKNOWN doc)

VÍ DỤ:
Page 0: "THÔNG BÁO THUẾ" → TBT
Page 1: "ĐIỀU 1: ..." → TBT continuation
Page 2: "III. TÍNH THUẾ" + bảng → TBT continuation (KHÔNG phải UNKNOWN)

Result: {{"type": "TBT", "pages": [0, 1, 2], ...}} ✅

---

"""

    output_format = f"""

---

🎯 OUTPUT FORMAT - BẮT BUỘC:

{{
  "documents": [
    {{
      "type": "HDCQ",
      "pages": [0, 1, 2, 3, 4],
      "confidence": 0.95,
      "reasoning": "5 trang đầu cùng format, trang 0 có tiêu đề 'HỢP ĐỒNG CHUYỂN NHƯỢNG', trang 1-4 là continuation pages với ĐIỀU 2, ĐIỀU 3",
      "metadata": {{}}
    }},
    {{
      "type": "GCN",
      "pages": [5, 6],
      "confidence": 0.98,
      "reasoning": "Trang 5-6 là GCN màu hồng, có quốc huy, tìm thấy ngày cấp ở trang 6",
      "metadata": {{
        "color": "pink",
        "issue_date": "27/10/2021",
        "issue_date_confidence": "full"
      }}
    }},
    {{
      "type": "UNKNOWN",
      "pages": [7, 8, 9],
      "confidence": 0.3,
      "reasoning": "3 trang cuối không rõ ràng, không có tiêu đề, không match 98 loại",
      "metadata": {{}}
    }}
  ]
}}

🚨 CỰC KỲ QUAN TRỌNG - BẮT BUỘC RETURN TẤT CẢ {batch_size} PAGES:
- Bạn PHẢI assign MỌI page (0 đến {batch_size-1}) vào 1 document
- Nếu page không rõ → assign vào document type "UNKNOWN"
- KHÔNG BAO GIỜ bỏ qua page nào
- Tổng số pages trong "pages" arrays = {batch_size}

VÍ DỤ ĐÚNG ({batch_size} pages):
- Document 1: pages [0,1,2,3,4] (5 pages)
- Document 2: pages [5,6,7,8] (4 pages)
- Document 3: pages [9,10,...,{batch_size-1}] ({batch_size-9} pages)
→ Total: {batch_size} pages ✅

VÍ DỤ SAI:
- Document 1: pages [0,1,2] (3 pages only)
- Document 2: pages [5,6] (2 pages, SKIP pages 3-4!)
→ Total: 5 pages ❌ (Missing pages 3,4,7,8,...,{batch_size-1})

INDEXING:
- pages dùng 0-indexed (trang đầu tiên = 0, trang cuối = {batch_size-1})
- Nếu chỉ có 1 document → vẫn trả về array với 1 phần tử
"""

    # Combine: intro + original rules + unknown rules + output format
    full_multi_prompt = multi_image_intro + single_image_prompt + unknown_rules + output_format
    
    return full_multi_prompt


def get_multi_image_prompt_full(batch_size):
    """Get FULL prompt (Flash Full rules) for multi-image batch"""
    single_prompt = get_classification_prompt()
    return adapt_prompt_for_multi_image(single_prompt, batch_size)


def get_multi_image_prompt_lite(batch_size):
    """Get LITE prompt (Flash Lite rules) for multi-image batch"""
    single_prompt = get_classification_prompt_lite()
    return adapt_prompt_for_multi_image(single_prompt, batch_size)


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




def batch_classify_fixed(image_paths, api_key, batch_size=5, overlap=3):
    """
    Phương án 1: Fixed Batch Size với OVERLAP
    Gom mỗi 5 files nhưng overlap 3 files để giữ context
    
    Ví dụ overlap=3, batch_size=15:
      Batch 1: Files 0-14  (15 files)
      Batch 2: Files 12-29 (18 files) → Overlap files 12,13,14
      Batch 3: Files 27-44 (18 files) → Overlap files 27,28,29
      
    Tại sao? File 15,16,17 có thể là continuation của file 14.
    Nếu batch 2 không thấy file 14 → classify sai!
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🔄 BATCH MODE 1: Fixed Batch Size ({batch_size} files, overlap {overlap})", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    all_results = []
    processed_files = set()  # Track processed files to detect missing ones
    batch_num = 0
    current_idx = 0
    
    while current_idx < len(image_paths):
        batch_num += 1
        
        # Calculate batch range with overlap
        batch_start = max(0, current_idx - overlap) if batch_num > 1 else current_idx
        batch_end = min(len(image_paths), current_idx + batch_size)
        batch_paths = image_paths[batch_start:batch_end]
        
        # Track which files are NEW in this batch (not overlap)
        new_file_start_idx = current_idx - batch_start
        
        print(f"\n📦 Batch {batch_num}: Files {batch_start}-{batch_end-1} ({len(batch_paths)} images)", file=sys.stderr)
        if batch_num > 1:
            print(f"   ↩️ Overlap: {overlap} files from previous batch (for context)", file=sys.stderr)
            print(f"   🆕 New files: {batch_end - current_idx} (starting from index {new_file_start_idx})", file=sys.stderr)
        
        for i, path in enumerate(batch_paths):
            marker = "🆕" if i >= new_file_start_idx else "↩️"
            print(f"   [{i}] {marker} {os.path.basename(path)}", file=sys.stderr)
        
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
        parts = [{"text": get_multi_image_prompt_full(len(batch_paths))}]
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
                "maxOutputTokens": 8000,  # Large enough for 20 documents × 400 tokens each
                "responseMimeType": "application/json"  # Force JSON output
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
        }
        
        # Call Gemini API
        print("📡 Sending batch request to Gemini Flash...", file=sys.stderr)
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        try:
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            result_data = response.json()
            
            print(f"📊 Response status: {response.status_code}", file=sys.stderr)
            
            # Debug: Check finish reason and safety
            if 'candidates' in result_data and len(result_data['candidates']) > 0:
                candidate = result_data['candidates'][0]
                finish_reason = candidate.get('finishReason', 'UNKNOWN')
                print(f"🔍 Finish reason: {finish_reason}", file=sys.stderr)
                
                if finish_reason == 'MAX_TOKENS':
                    print("⚠️ WARNING: Response truncated due to MAX_TOKENS!", file=sys.stderr)
                    print("   Some pages may be missing from response", file=sys.stderr)
            
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
                                
                                # Validate: Check if all pages are covered
                                total_pages_in_batch = len(batch_paths)
                                pages_returned = set()
                                
                                for doc in batch_result.get('documents', []):
                                    doc_type = doc.get('type', 'UNKNOWN')
                                    pages = doc.get('pages', [])
                                    confidence = doc.get('confidence', 0)
                                    print(f"   📄 {doc_type}: {len(pages)} pages, confidence {confidence:.0%}", file=sys.stderr)
                                    
                                    # Collect all page indices
                                    for p in pages:
                                        pages_returned.add(p)
                                
                                # Check for missing pages
                                expected_pages = set(range(total_pages_in_batch))
                                missing_pages = expected_pages - pages_returned
                                
                                if missing_pages:
                                    print(f"   ⚠️ WARNING: AI didn't return {len(missing_pages)} pages: {sorted(missing_pages)}", file=sys.stderr)
                                    print("      These files will be processed by fallback", file=sys.stderr)
                                else:
                                    print(f"   ✅ All {total_pages_in_batch} pages accounted for", file=sys.stderr)
                                
                                # Map results back to original file paths
                                # ONLY process NEW files (skip overlap files)
                                for doc in batch_result.get('documents', []):
                                    for page_idx in doc.get('pages', []):
                                        # Check if this is a NEW file (not overlap)
                                        if page_idx >= new_file_start_idx and page_idx < len(batch_paths):
                                            file_path = batch_paths[page_idx]
                                            
                                            # Skip if already processed (from previous batch)
                                            if file_path in processed_files:
                                                print(f"   ⏭️ Skipping duplicate: {os.path.basename(file_path)}", file=sys.stderr)
                                                continue
                                            
                                            processed_files.add(file_path)  # Track this file
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
                            except json.JSONDecodeError as je:
                                print(f"⚠️ JSON decode error in batch {batch_num}: {je}", file=sys.stderr)
                                print(f"   Response text: {response_text[:500]}...", file=sys.stderr)
                        else:
                            print(f"⚠️ No valid JSON in response for batch {batch_num}", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ Batch {batch_num} error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        # Move to next batch (increment by batch_size, not batch_end)
        current_idx += batch_size
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✅ BATCH MODE 1 COMPLETE: {len(all_results)} files processed", file=sys.stderr)
    
    # Detect missing files
    all_input_files = set(image_paths)
    missing_files = all_input_files - processed_files
    
    if missing_files:
        print(f"⚠️ WARNING: {len(missing_files)} files were NOT processed by AI:", file=sys.stderr)
        for missing_file in sorted(missing_files):
            print(f"   ❌ {os.path.basename(missing_file)}", file=sys.stderr)
        print("   Possible causes: AI didn't return page indices, JSON parsing error", file=sys.stderr)
        print(f"\n🔄 FALLBACK: Processing {len(missing_files)} missing files individually...", file=sys.stderr)
        
        # Fallback: Process missing files with single-file tier1 scan
        for missing_file in sorted(missing_files):
            try:
                print(f"   🔄 Processing {os.path.basename(missing_file)}...", file=sys.stderr)
                result = quick_scan_tier1(missing_file, api_key)
                all_results.append({
                    'file_path': missing_file,
                    'file_name': os.path.basename(missing_file),
                    'short_code': result.get('short_code', 'UNKNOWN'),
                    'confidence': result.get('confidence', 0.5),
                    'reasoning': result.get('reasoning', 'Fallback single-file scan'),
                    'metadata': result.get('metadata', {}),
                    'method': 'batch_fallback',
                    'batch_num': 'fallback'
                })
                print(f"      ✅ {result.get('short_code', 'UNKNOWN')} ({result.get('confidence', 0):.0%})", file=sys.stderr)
            except Exception as e:
                print(f"      ❌ Error: {e}", file=sys.stderr)
                # Add as UNKNOWN if fallback also fails
                all_results.append({
                    'file_path': missing_file,
                    'file_name': os.path.basename(missing_file),
                    'short_code': 'UNKNOWN',
                    'confidence': 0.0,
                    'reasoning': f'Fallback failed: {str(e)}',
                    'metadata': {},
                    'method': 'batch_fallback_failed',
                    'batch_num': 'fallback'
                })
        
        print(f"✅ Fallback complete: {len(all_results)} total results (original + fallback)", file=sys.stderr)
    else:
        print(f"✅ All {len(all_input_files)} input files were successfully processed", file=sys.stderr)
    
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
    print("\n🧠 Analyzing document boundaries...", file=sys.stderr)
    
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
    Phương án 2: Smart Batching - TRUE AI-POWERED với OVERLAP
    Gửi nhiều files (10-20) với overlap để AI có full context
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print("🧠 BATCH MODE 2: Smart Batching (AI Document Detection)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    total_files = len(image_paths)
    
    # Smart batch size strategy với overlap
    if total_files <= 20:
        # Small batch: Send all at once, no overlap needed
        batch_size = total_files
        overlap = 0
        print(f"📊 Strategy: Send ALL {total_files} files in 1 batch", file=sys.stderr)
    elif total_files <= 60:
        # Medium batch: 20 files per batch, 5 files overlap
        batch_size = 20
        overlap = 5
        print(f"📊 Strategy: Send {batch_size} files per batch với {overlap} files overlap", file=sys.stderr)
    else:
        # Large batch: 15 files per batch, 4 files overlap
        batch_size = 15
        overlap = 4
        print(f"📊 Strategy: Send {batch_size} files per batch với {overlap} files overlap (large dataset)", file=sys.stderr)
    
    if overlap > 0:
        print(f"   ↩️ Overlap purpose: Batch sau thấy {overlap} files cuối của batch trước", file=sys.stderr)
        print("   Why? File 16 không có title → cần thấy file 14-15 để biết nó thuộc document nào", file=sys.stderr)
    
    print("   AI needs 10-20 files to detect document boundaries accurately", file=sys.stderr)
    
    # Use fixed batch with smart size + overlap
    return batch_classify_fixed(image_paths, api_key, batch_size=batch_size, overlap=overlap)


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
        results = batch_classify_fixed(image_paths, api_key, batch_size=5, overlap=2)
    elif mode == 'smart':
        results = batch_classify_smart(image_paths, api_key)
    else:
        print(f"❌ Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)
    
    # Output JSON to stdout for IPC
    print(json.dumps(results, ensure_ascii=False))
    
    print(f"\n📊 BATCH COMPLETE: {len(results)} files processed", file=sys.stderr)
