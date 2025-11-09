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
    """Get prompt for multi-image batch analysis with full 98 document types"""
    return """Bạn đang phân tích nhiều trang scan tài liệu đất đai Việt Nam (có thể thuộc 1 hoặc nhiều tài liệu khác nhau).

NHIỆM VỤ:
1. Xác định có BAO NHIÊU tài liệu khác nhau trong các trang này
2. Nhóm các trang theo tài liệu
3. Phân loại loại tài liệu của từng nhóm theo DANH SÁCH 98 LOẠI bên dưới
4. Trích xuất metadata (ngày cấp cho GCN, màu sắc, v.v.)

DẤU HIỆU NHẬN BIẾT TRANG MỚI vs TRANG TIẾP NỐI:

TRANG 1 CỦA TÀI LIỆU (New Document):
- Có TIÊU ĐỀ CHÍNH ở TOP 30% (đầu trang)
- Cỡ chữ LỚN, IN HOA, căn giữa
- Ví dụ: "HỢP ĐỒNG CHUYỂN NHƯỢNG", "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG"
- Có quốc huy (đối với GCN)
- Khác biệt rõ về format/màu sắc so với trang trước

TRANG TIẾP NỐI (Continuation - Trang 2, 3, 4...):
- KHÔNG có tiêu đề chính ở đầu
- Chỉ có section headers: "II.", "III.", "ĐIỀU 2", "PHẦN II", "MỤC III"
- Cùng format/màu sắc với trang trước
- Nội dung liên tục (điều khoản, sơ đồ, bảng biểu, chữ ký)

RANH GIỚI GIỮA CÁC TÀI LIỆU:
- Thay đổi rõ rệt: màu giấy (hồng → trắng), format (có quốc huy → không có)
- Xuất hiện tiêu đề chính mới ở TOP
- Thay đổi hoàn toàn về layout

⚠️ DANH SÁCH 98 LOẠI TÀI LIỆU (CHỈ DÙNG MÃ TRONG DANH SÁCH NÀY):

📋 NHÓM 1: BẢN VẼ / BẢN ĐỒ (5 loại)
BMT = Bản mô tả ranh giới
HSKT = Bản vẽ (trích lục, đo tách)
BVHC = Bản vẽ hoàn công
BVN = Bản vẽ nhà
SDTT = Sơ đồ dự kiến tách thửa

📋 NHÓM 2: BẢNG KÊ / DANH SÁCH (4 loại)
BKKDT = Bảng kê khai diện tích
DSCG = Bảng liệt kê danh sách thửa đất
DS15 = Danh sách chủ sử dụng (Mẫu 15)
DSCK = Danh sách công khai hồ sơ cấp giấy

📋 NHÓM 3: BIÊN BẢN (10 loại)
BBBDG = Biên bản bán đấu giá
BBGD = Biên bản bàn giao đất
BBHDDK = Biên bản hội đồng đăng ký đất đai
BBNT = Biên bản nghiệm thu công trình
BBKTSS = Biên bản kiểm tra sai sót
BBKTHT = Biên bản kiểm tra hiện trạng
BBKTDC = Biên bản kết thúc công khai di chúc
KTCKCG = Biên bản kết thúc thông báo cấp GCN
KTCKMG = Biên bản kết thúc thông báo mất GCN
BLTT = Biên lai thu thuế

📋 NHÓM 4: GIẤY TỜ CÁ NHÂN (4 loại)
CCCD = Căn cước công dân
GKS = Giấy khai sinh
GKH = Giấy kết hôn
DICHUC = Di chúc

📋 NHÓM 5: GIẤY CHỨNG NHẬN (9 loại)
🚨 GCN = Giấy chứng nhận quyền sử dụng đất (❌ KHÔNG bao giờ trả về GCNM/GCNC)
  ⚠️ BẮT BUỘC tìm NGÀY CẤP (có thể viết tay, format: DD/MM/YYYY hoặc MM/YYYY hoặc YYYY)
  ⚠️ Nếu thấy "Ngày XX tháng YY năm ZZZZ" → chuyển thành "XX/YY/ZZZZ"
GXNNVTC = Giấy xác nhận nộp vào ngân sách
GNT = Giấy nộp tiền
GSND = Giấy sang nhượng đất
GTLQ = Giấy tờ liên quan (giấy tiếp nhận, biên nhận hồ sơ, phiếu kiểm soát)
GUQ = Giấy ủy quyền
GXNDKLD = Giấy xác nhận đăng ký lần đầu
GPXD = Giấy phép xây dựng

📋 NHÓM 6: HỢP ĐỒNG (7 loại)
HDCQ = Hợp đồng chuyển nhượng, tặng cho
HDUQ = Hợp đồng ủy quyền
HDTHC = Hợp đồng thế chấp
HDTD = Hợp đồng thuê đất
HDTCO = Hợp đồng thi công
HDBDG = Hợp đồng mua bán đấu giá
hoadon = Hóa đơn giá trị gia tăng

📋 NHÓM 7: ĐƠN (15 loại)
DDKBD = Đơn đăng ký biến động (có "BIẾN ĐỘNG")
DDK = Đơn đăng ký (không có "BIẾN ĐỘNG")
DCK = Đơn cam kết, giấy cam kết
CHTGD = Đơn chuyển hình thức giao đất
DCQDGD = Đơn điều chỉnh quyết định giao đất
DMG = Đơn miễn giảm lệ phí
DMD = Đơn đa mục đích
DXN = Đơn xác nhận
DXCMD = Đơn xin chuyển mục đích
DGH = Đơn xin gia hạn
DXGD = Đơn xin giao đất
DXTHT = Đơn xin tách/hợp thửa
DXCD = Đơn xin cấp đổi GCN
DDCTH = Đơn điều chỉnh thời hạn dự án
DXNTH = Đơn xác nhận thời hạn nông nghiệp

📋 NHÓM 8: QUYẾT ĐỊNH (15 loại)
QDGTD = Quyết định giao đất/cho thuê
QDCMD = Quyết định chuyển mục đích
QDTH = Quyết định thu hồi đất
QDGH = Quyết định gia hạn
QDTT = Quyết định tách/hợp thửa
QDCHTGD = Quyết định chuyển hình thức giao đất
QDDCGD = Quyết định điều chỉnh QĐ giao đất
QDDCTH = Quyết định điều chỉnh thời hạn dự án
QDHG = Quyết định hủy GCN
QDPDBT = Quyết định phê duyệt bồi thường
QDDCQH = Quyết định điều chỉnh quy hoạch
QDPDDG = Quyết định phê quyết đơn giá
QDTHA = Quyết định thi hành án
QDHTSD = Quyết định hình thức sử dụng đất
QDXP = Quyết định xử phạt

📋 NHÓM 9: PHIẾU (8 loại)
PCT = Phiếu chuyển thông tin nghĩa vụ tài chính
PKTHS = Phiếu kiểm tra hồ sơ (KIỂM TRA, không phải KIỂM SOÁT)
PLYKDC = Phiếu lấy ý kiến khu dân cư
PXNKQDD = Phiếu xác nhận kết quả đo đạc
DKTC = Phiếu yêu cầu đăng ký biện pháp bảo đảm
DKTD = Phiếu yêu cầu thay đổi biện pháp bảo đảm
DKXTC = Phiếu yêu cầu xóa đăng ký biện pháp bảo đảm
QR = Quét mã QR

📋 NHÓM 10: THÔNG BÁO (8 loại)
TBT = Thông báo thuế
TBMG = Thông báo về việc mất GCN
TBCKCG = Thông báo công khai kết quả cấp GCN
TBCKMG = Thông báo niêm yết mất GCN
HTNVTC = Thông báo hoàn thành nghĩa vụ tài chính
TBCNBD = Thông báo cập nhật biến động
CKDC = Thông báo công bố di chúc
HTBTH = Hoàn thành bồi thường hỗ trợ

📋 NHÓM 11: TỜ KHAI / TỜ TRÌNH (3 loại)
TKT = Tờ khai thuế
TTr = Tờ trình về giao đất (chữ "r" thường)
TTCG = Tờ trình về đăng ký đất đai (UBND xã)

📋 NHÓM 12: VĂN BẢN (10 loại)
CKTSR = Văn bản cam kết tài sản riêng
VBCTCMD = Văn bản chấp thuận chuyển mục đích
VBDNCT = Văn bản đề nghị chấp thuận nhận chuyển nhượng
PDPASDD = Văn bản đề nghị thẩm định phương án
VBTK = Văn bản thỏa thuận phân chia DI SẢN THỪA KẾ
TTHGD = Văn bản thỏa thuận HỘ GIA ĐÌNH (không phải vợ chồng)
CDLK = Văn bản chấm dứt quyền hạn chế liền kề
HCLK = Văn bản xác lập quyền hạn chế liền kề
VBTC = Văn bản từ chối nhận di sản
PCTSVC = Văn bản phân chia tài sản VỢ CHỒNG (không phải hộ gia đình)

⚠️ QUAN TRỌNG - QUY TẮC PHÂN LOẠI:
- CHỈ phân loại dựa vào TIÊU ĐỀ CHÍNH ở TOP 30%
- BỎ QUA section headers (ĐIỀU 2, PHẦN II, ...)
- BỎ QUA mentions trong body text
- ❌ TUYỆT ĐỐI không trả về GCNM hoặc GCNC, chỉ trả về GCN
- Nếu không khớp 98 loại → trả về "UNKNOWN"

🚨 ĐẶC BIỆT VỚI GCN:
- Luôn trả về "GCN" (không phải GCNM/GCNC)
- BẮT BUỘC tìm NGÀY CẤP (issue_date) ở mọi trang
- Format ngày: DD/MM/YYYY (hoặc MM/YYYY, YYYY nếu mờ)
- Vị trí: Thường ở trang 2, bottom, gần chữ ký/con dấu
- Nếu không tìm thấy → issue_date: null, issue_date_confidence: "not_found"

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
                            except json.JSONDecodeError as je:
                                print(f"⚠️ JSON decode error in batch {batch_num}: {je}", file=sys.stderr)
                                print(f"   Response text: {response_text[:500]}...", file=sys.stderr)
                        else:
                            print(f"⚠️ No valid JSON in response for batch {batch_num}", file=sys.stderr)
            
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
    Phương án 2: Smart Batching - TRUE AI-POWERED
    Gửi nhiều files (10-20) để AI tự detect document boundaries
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🧠 BATCH MODE 2: Smart Batching (AI Document Detection)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    total_files = len(image_paths)
    
    # Smart batch size strategy
    if total_files <= 20:
        # Small batch: Send all at once
        batch_size = total_files
        print(f"📊 Strategy: Send ALL {total_files} files in 1 batch", file=sys.stderr)
    elif total_files <= 60:
        # Medium batch: 15-20 files per batch
        batch_size = 20
        print(f"📊 Strategy: Send {batch_size} files per batch", file=sys.stderr)
    else:
        # Large batch: 15 files per batch (more batches but still smart)
        batch_size = 15
        print(f"📊 Strategy: Send {batch_size} files per batch (large dataset)", file=sys.stderr)
    
    print(f"   Why? AI needs 10-20 files to detect document boundaries accurately", file=sys.stderr)
    print(f"   Fixed Batch (5 files) may cut documents in half ❌", file=sys.stderr)
    print(f"   Smart Batch ({batch_size} files) sees full documents ✅", file=sys.stderr)
    
    # Use fixed batch with smart size
    return batch_classify_fixed(image_paths, api_key, batch_size=batch_size)


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
