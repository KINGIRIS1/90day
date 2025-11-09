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

🎯 QUY TẮC PHÂN BIỆT DỄ NHẦM:

**1. HDCQ vs HDUQ (CỰC KỲ QUAN TRỌNG):**
- HDCQ = "HỢP ĐỒNG CHUYỂN NHƯỢNG" (transfer ownership)
  * Keywords: "CHUYỂN NHƯỢNG", "TẶNG CHO"
  * ✅ "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT" → HDCQ
- HDUQ = "HỢP ĐỒNG ỦY QUYỀN" (power of attorney)
  * Keywords: "ỦY QUYỀN"
  * ✅ "HỢP ĐỒNG ỦY QUYỀN" → HDUQ
- ⚠️ KHÔNG nhầm: Nếu thấy "ỦY QUYỀN" → BẮT BUỘC là HDUQ, không phải HDCQ

**2. TTHGD vs PCTSVC vs VBTK (DỄ NHẦM):**
- TTHGD = Thỏa thuận HỘ GIA ĐÌNH
  * Keywords: "HỘ GIA ĐÌNH" (family members)
  * ✅ "THỎA THUẬN QSDĐ HỘ GIA ĐÌNH" → TTHGD
  * ✅ "PHÂN CHIA TÀI SẢN HỘ GIA ĐÌNH" → TTHGD
- PCTSVC = Phân chia VỢ CHỒNG
  * Keywords: "VỢ CHỒNG" (couple)
  * ✅ "PHÂN CHIA TÀI SẢN VỢ CHỒNG" → PCTSVC
- VBTK = Phân chia DI SẢN THỪA KẾ
  * Keywords: "DI SẢN THỪA KẾ", "KẾ THỪA" (inheritance)
  * ✅ "THỎA THUẬN PHÂN CHIA DI SẢN THỪA KẾ" → VBTK

**3. DDKBD vs DDK:**
- DDKBD = Có chữ "BIẾN ĐỘNG"
  * ✅ "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI" → DDKBD
- DDK = KHÔNG có "BIẾN ĐỘNG"
  * ✅ "ĐƠN ĐĂNG KÝ ĐẤT ĐAI" → DDK

**4. PKTHS vs GTLQ:**
- PKTHS = "KIỂM TRA HỒ SƠ"
  * ✅ "PHIẾU KIỂM TRA HỒ SƠ" → PKTHS
- GTLQ = "KIỂM SOÁT" hoặc "TIẾP NHẬN"
  * ✅ "PHIẾU KIỂM SOÁT QUÁ TRÌNH" → GTLQ
  * ✅ "GIẤY TIẾP NHẬN HỒ SƠ" → GTLQ

**5. GUQ (GIẤY) vs HDUQ (HỢP ĐỒNG):**
- GUQ = "GIẤY ỦY QUYỀN" (simple authorization letter)
  * ✅ "GIẤY ỦY QUYỀN" → GUQ
- HDUQ = "HỢP ĐỒNG ỦY QUYỀN" (formal contract)
  * ✅ "HỢP ĐỒNG ỦY QUYỀN" → HDUQ

❌ VÍ DỤ SAI (KHÔNG LÀM NHƯ VẦY):
- "HỢP ĐỒNG ỦY QUYỀN" → HDCQ ❌ (Sai! Phải là HDUQ)
- "PHÂN CHIA TÀI SẢN VỢ CHỒNG" → TTHGD ❌ (Sai! Phải là PCTSVC)
- "Giấy chứng nhận màu hồng" → GCNM ❌ (Sai! Phải là GCN)
- "ĐIỀU 2: NỘI DUNG THỎA THUẬN" → TTHGD ❌ (Section header, không phải title)

✅ VÍ DỤ ĐÚNG:
- Trang có "HỢP ĐỒNG CHUYỂN NHƯỢNG" ở TOP → HDCQ ✅
- Trang có "HỢP ĐỒNG ỦY QUYỀN" ở TOP → HDUQ ✅
- Trang có "ĐIỀU 2" ở TOP → UNKNOWN (continuation page) ✅
- Trang có "THỎA THUẬN...HỘ GIA ĐÌNH" → TTHGD ✅

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

🚨 CỰC KỲ QUAN TRỌNG - BẮT BUỘC RETURN TẤT CẢ PAGES:
- Bạn PHẢI assign MỌI page vào 1 document
- Nếu page không rõ ràng → assign vào document "UNKNOWN"
- KHÔNG BAO GIỜ bỏ qua bất kỳ page nào
- Ví dụ: Nếu có 20 pages → "pages" arrays phải cover hết 0-19

VÍ DỤ ĐÚNG (20 pages):
{
  "documents": [
    {"type": "HDCQ", "pages": [0,1,2,3,4], ...},      // 5 pages
    {"type": "GCN", "pages": [5,6,7,8], ...},         // 4 pages
    {"type": "DDKBD", "pages": [9,10,11], ...},       // 3 pages
    {"type": "UNKNOWN", "pages": [12,13,14,15,16,17,18,19], ...}  // 8 unclear pages
  ]
}
→ Total pages: 5+4+3+8 = 20 ✅ (ALL pages covered)

VÍ DỤ SAI:
{
  "documents": [
    {"type": "HDCQ", "pages": [0,1,2,3,4], ...},
    {"type": "GCN", "pages": [5,6,7,8], ...}
  ]
}
→ Total pages: 5+4 = 9 ❌ (Missing pages 9-19!)

Lưu ý:
- pages dùng 0-indexed (trang đầu tiên = 0)
- Nếu không chắc chắn, đánh dấu confidence thấp
- Nếu chỉ có 1 tài liệu, vẫn trả về array với 1 phần tử
"""


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
                                    print(f"      These files will be processed by fallback", file=sys.stderr)
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
        print(f"   Possible causes: AI didn't return page indices, JSON parsing error", file=sys.stderr)
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
    Phương án 2: Smart Batching - TRUE AI-POWERED với OVERLAP
    Gửi nhiều files (10-20) với overlap để AI có full context
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🧠 BATCH MODE 2: Smart Batching (AI Document Detection)", file=sys.stderr)
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
        print(f"   Why? File 16 không có title → cần thấy file 14-15 để biết nó thuộc document nào", file=sys.stderr)
    
    print(f"   AI needs 10-20 files to detect document boundaries accurately", file=sys.stderr)
    
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
