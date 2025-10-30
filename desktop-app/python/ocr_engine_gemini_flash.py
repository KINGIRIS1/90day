#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash 2.0 - AI Document Classification Engine
Using direct REST API (no async, no emergentintegrations)
"""

import sys
import base64
from PIL import Image
import io


def classify_document_gemini_flash(image_path, api_key, crop_top_percent=0.35):
    """
    Classify Vietnamese land document using Gemini Flash 2.0 AI
    
    Args:
        image_path: Path to image file
        api_key: Google API key (BYOK)
        crop_top_percent: Percentage of top image to process (default 0.35 = 35%)
        
    Returns:
        dict: Classification result with short_code, confidence, reasoning
    """
    try:
        import requests
        
        # Read and crop image to top portion (where title/header usually is)
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Crop to top N% (default 35%)
            crop_height = int(height * crop_top_percent)
            cropped_img = img.crop((0, 0, width, crop_height))
            
            # Convert to base64
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format=img.format or 'PNG')
            image_content = img_byte_arr.getvalue()
            
            print(f"🖼️ Image cropped: {width}x{height} → {width}x{crop_height} (top {int(crop_top_percent*100)}%)", file=sys.stderr)
        
        # Encode to base64
        encoded_image = base64.b64encode(image_content).decode('utf-8')
        
        # Use direct REST API - v1beta is the standard API version
        # Model: gemini-2.5-flash (latest stable Flash model)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Create request payload
        payload = {
            "contents": [{
                "parts": [
                    {"text": get_classification_prompt()},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_image
                        }
                    }
                ]
            }]
        }
        
        print(f"📡 Sending request to Gemini Flash...", file=sys.stderr)
        
        # Send request (timeout 60s for large images)
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Increased from 30s to handle large image processing
        )
        
        print(f"📊 Response status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            error_msg = f"API error {response.status_code}: {response.text[:200]}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {
                "short_code": "ERROR",
                "confidence": 0,
                "reasoning": error_msg
            }
        
        result_data = response.json()
        
        # Extract text from response
        if 'candidates' in result_data and len(result_data['candidates']) > 0:
            candidate = result_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    result_text = parts[0]['text']
                    print(f"🤖 Gemini response: {result_text[:200]}...", file=sys.stderr)
                    
                    # Parse result
                    classification = parse_gemini_response(result_text)
                    return classification
        
        # No valid response
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse Gemini response"
        }
        
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else "unknown"
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Missing library: {missing_lib}. Install: pip install {missing_lib}"
        }
    except Exception as e:
        print(f"❌ Gemini Flash error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Error: {str(e)}"
        }


def get_classification_prompt():
    """
    System prompt for Vietnamese document classification
    IMPORTANT: This prompt is aligned with OpenAI Vision backend prompt for consistency
    UPDATED: More flexible matching (85-90% similarity acceptable)
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🔍 Sau đó kiểm tra tiêu đề:
  • "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất" → GCNM (GCN mới - tiêu đề DÀI)
  • "Giấy chứng nhận quyền sử dụng đất" (KHÔNG có "quyền sở hữu...") → GCNC (GCN cũ - tiêu đề NGẮN)
  • Nếu chỉ thấy "GIẤY CHỨNG NHẬN" mà không rõ tiếp theo → GCNC

⚠️ QUAN TRỌNG với tài liệu 2 trang ngang:
- Nếu thấy nền cam/vàng với quốc huy ở bên PHẢI → Đây là GCNC
- Tập trung vào trang BÊN PHẢI để đọc tiêu đề

⚠️ BỎ QUA bất kỳ ảnh cá nhân nào - chỉ tập trung vào văn bản và con dấu chính thức.

⚠️ QUY TẮC KHỚP: CHO PHÉP ~85-90% TƯƠNG ĐỒNG!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CHẤP NHẬN khi tiêu đề khớp 85-90% với danh sách
✅ CHO PHÉP lỗi chính tả nhỏ (ví dụ: "NHUỢNG" → "NHƯỢNG")
✅ CHO PHÉP thiếu/thừa dấu câu, khoảng trắng
✅ CHO PHÉP viết tắt (ví dụ: "QSDĐ" → "quyền sử dụng đất")
❌ KHÔNG khớp nếu thiếu từ khóa QUAN TRỌNG phân biệt loại

⚠️ CỰC KỲ QUAN TRỌNG: PHÂN BIỆT TIÊU ĐỀ vs NỘI DUNG BODY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TIÊU ĐỀ CHÍNH (Main Title):
- Nằm Ở ĐẦU trang, TRÊN CÙNG
- Cỡ chữ LỚN, IN HOA, căn giữa
- VD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI..."
- → CHỈ TIÊU ĐỀ CHÍNH mới dùng để phân loại!

❌ KHÔNG PHÂN LOẠI DỰA VÀO:
- Section headers (III. THÔNG TIN VỀ...)
- Mentions trong body text
- Danh sách đính kèm
- Ghi chú cuối trang

VÍ DỤ DỄ NHẦM:

❌ SAI: Trang có section "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG..."
   → Đây CHỈ là section header, KHÔNG phải title
   → Trả về: UNKNOWN (không có title chính rõ ràng)

❌ SAI: Body text có mention "...hợp đồng chuyển nhượng..."
   → Đây là mention, KHÔNG phải title
   → CHỈ phân loại HDCQ nếu có TITLE "HỢP ĐỒNG CHUYỂN NHƯỢNG"

✅ ĐÚNG: Tiêu đề ở đầu trang: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG..."
   → Có title chính rõ ràng
   → Phân loại: DDKBD

🎯 TRANG TIẾP THEO (Continuation Pages):
Nếu trang KHÔNG có tiêu đề chính (title page), có thể có:
- Section headers: "II. THÔNG TIN...", "III. ĐĂNG KÝ..."
- Body content: Danh sách, bảng biểu, nội dung chi tiết
- → Trả về: UNKNOWN (Frontend sẽ tự động gán theo trang trước)

🎯 NHẬN DIỆN TRANG GCN (Continuation):
Trang 2+ của GCN thường có các section:
- "Nội dung thay đổi và cơ sở pháp lý"
- "Xác nhận của cơ quan có thẩm quyền"
- "Thửa đất, nhà ở và tài sản khác gắn liền với đất"
- "II. NỘI DUNG THAY ĐỔI..."
- "III. XÁC NHẬN..."
→ Nếu thấy những section này NHƯNG KHÔNG có title chính
→ Trả về: UNKNOWN (đây là trang continuation của GCN)

VÍ DỤ CHẤP NHẬN:
- Thấy "HỢP ĐỒNG CHUYỂN NHUỢNG..." (lỗi chính tả) → HDCQ ✅
- Thấy "Giấy chứng nhận QSDĐ" (viết tắt) → GCNM ✅
- Thấy "QUYET  DINH GIAO DAT" (no diacritics) → QDGTD ✅

VÍ DỤ TỪ CHỐI:
- Chỉ có section "III. THÔNG TIN VỀ ĐĂNG KÝ BIẾN ĐỘNG" → UNKNOWN ❌
- Body text mention "đăng ký biến động" → UNKNOWN ❌
- Trang có "Nội dung thay đổi" nhưng không có title GCN → UNKNOWN ❌
- "HỢP ĐỒNG" (không rõ loại) → UNKNOWN ❌
- "QUYẾT ĐỊNH" (không rõ loại) → UNKNOWN ❌

NẾU KHÔNG KHỚP ~85%+ → Trả về:
{
  "short_code": "UNKNOWN",
  "confidence": 0.1,
  "reasoning": "Không thấy tiêu đề chính khớp đủ với danh sách (chỉ thấy section header hoặc mention)"
}

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Frontend sẽ tự động copy tên từ trang 1
  - CHỈ KHI thấy tiêu đề MỚI khớp ~85%+ → Mới đổi sang loại mới

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÁC CẶP DỄ NHẦM - PHẢI CÓ TỪ KHÓA PHÂN BIỆT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG" hoặc tương tự)
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   ⚠️ CHECK HDCQ TRƯỚC! Nếu có cả 2 từ → chọn HDCQ
   Nếu không rõ loại → "UNKNOWN"

2. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" → Nên chọn DDK (phổ biến hơn)

3. "Hợp đồng THUÊ đất" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   "Hợp đồng THI CÔNG" → HDTCO (PHẢI có "THI CÔNG")
   "Hợp đồng mua bán" → HDBDG (PHẢI có "MUA BÁN" hoặc "ĐẤU GIÁ")
   Nếu chỉ thấy "HỢP ĐỒNG" → "UNKNOWN"

4. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP" + "CHUYỂN MỤC ĐÍCH")
   "Quyết định GIAO ĐẤT" → QDGTD (PHẢI có "GIAO ĐẤT" hoặc "CHO THUÊ ĐẤT")
   "Quyết định THU HỒI đất" → QDTH (PHẢI có "THU HỒI")
   "Quyết định GIA HẠN" → QDGH (PHẢI có "GIA HẠN")
   Nếu không rõ loại → "UNKNOWN"

5. "Giấy ỦY QUYỀN" → GUQ (riêng lẻ, không phải hợp đồng)
   "Hợp đồng ủy quyền" → HDUQ (là HỢP ĐỒNG ủy quyền)
   PHẢI phân biệt rõ!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DANH SÁCH ĐẦY ĐỦ 98 LOẠI TÀI LIỆU (KHỚP ~85-90%):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NHÓM 1: BẢN VẼ / BẢN ĐỒ (5 loại)
BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
BẢN VẼ HOÀN CÔNG → BVHC
BẢN VẼ NHÀ → BVN
SƠ ĐỒ DỰ KIẾN TÁCH THỬA → SDTT

📋 NHÓM 2: BẢNG KÊ / DANH SÁCH (4 loại)
BẢNG KÊ KHAI DIỆN TÍCH ĐANG SỬ DỤNG → BKKDT
BẢNG LIỆT KÊ DANH SÁCH CÁC THỬA ĐẤT CẤP GIẤY → DSCG
DANH SÁCH CHỦ SỬ DỤNG VÀ CÁC THỬA ĐẤT (MẪU 15) → DS15
DANH SÁCH CÔNG KHAI HỒ SƠ CẤP GIẤY CNQSDĐ → DSCK

📋 NHÓM 3: BIÊN BẢN (10 loại)
BIÊN BẢN BÁN ĐẤU GIÁ TÀI SẢN → BBBDG
BIÊN BẢN BÀN GIAO ĐẤT TRÊN THỰC ĐỊA → BBGD
BIÊN BẢN CỦA HỘI ĐỒNG ĐĂNG KÝ ĐẤT ĐAI LẦN ĐẦU → BBHDDK
BIÊN BẢN KIỂM TRA NGHIỆM THU CÔNG TRÌNH XÂY DỰNG → BBNT
BIÊN BẢN KIỂM TRA SAI SÓT TRÊN GIẤY CHỨNG NHẬN → BBKTSS
BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT → BBKTHT
BIÊN BẢN VỀ VIỆC KẾT THÚC CÔNG KHAI CÔNG BỐ DI CHÚC → BBKTDC
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI KẾT QUẢ KIỂM TRA HỒ SƠ ĐĂNG KÝ CẤP GCNQSD ĐẤT → KTCKCG
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI VỀ VIỆC MẤT GCNQSD ĐẤT → KTCKMG
BIÊN LAI THU THUẾ SỬ DỤNG ĐẤT PHI NÔNG NGHIỆP → BLTT

📋 NHÓM 4: GIẤY TỜ CÁ NHÂN (4 loại)
CĂN CƯỚC CÔNG DÂN → CCCD
GIẤY KHAI SINH → GKS
GIẤY CHỨNG NHẬN KẾT HÔN → GKH
DI CHÚC → DICHUC

📋 NHÓM 5: GIẤY CHỨNG NHẬN (9 loại)
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT, QUYỀN SỞ HỮU TÀI SẢN GẮN LIỀN VỚI ĐẤT → GCNM
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → GCNC (⚠️ NGẮN HƠN GCNM)
GIẤY ĐỀ NGHỊ XÁC NHẬN CÁC KHOẢN NỘP VÀO NGÂN SÁCH → GXNNVTC
GIẤY NỘP TIỀN VÀO NGÂN SÁCH NHÀ NƯỚC → GNT
GIẤY SANG NHƯỢNG ĐẤT → GSND
GIẤY TỜ LIÊN QUAN (CÁC LOẠI GIẤY TỜ KÈM THEO) → GTLQ
GIẤY TIẾP NHẬN, GIẤY BIÊN NHẬN (HỒ SƠ) → GTLQ
BỘ PHẬN TIẾP NHẬN VÀ TRẢ KẾT QUẢ (KQ) → GTLQ
PHIẾU TIẾP NHẬN HỒ SƠ, PHIẾU KIỂM SOÁT QUÁ TRÌNH → GTLQ
GIẤY ỦY QUYỀN → GUQ
GIẤY XÁC NHẬN ĐĂNG KÝ LẦN ĐẦU → GXNDKLD
GIẤY XIN PHÉP XÂY DỰNG → GPXD

📋 NHÓM 6: HỢP ĐỒNG (7 loại) ⚠️ DỄ NHẦM
HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT → HDCQ
HỢP ĐỒNG ỦY QUYỀN → HDUQ
HỢP ĐỒNG THẾ CHẤP QUYỀN SỬ DỤNG ĐẤT → HDTHC
HỢP ĐỒNG THUÊ ĐẤT, ĐIỀU HỈNH HỢP ĐỒNG THUÊ ĐẤT → HDTD
HỢP ĐỒNG THI CÔNG → HDTCO
HỢP ĐỒNG MUA BÁN TÀI SẢN BÁN ĐẤU GIÁ → HDBDG
HOÁ ĐƠN GIÁ TRỊ GIA TĂNG → hoadon

📋 NHÓM 7: ĐƠN (15 loại) ⚠️ DỄ NHẦM
ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDKBD (có "BIẾN ĐỘNG")
ĐƠN ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDK (không có "BIẾN ĐỘNG")
ĐƠN CAM KẾT, GIẤY CAM KẾT → DCK
ĐƠN ĐỀ NGHỊ CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT) → CHTGD
ĐƠN ĐỀ NGHỊ ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → DCQDGD
ĐƠN ĐỀ NGHỊ MIỄN GIẢM LỆ PHÍ TRƯỚC BẠ, THUẾ THU NHẬP CÁ NHÂN → DMG
ĐƠN ĐỀ NGHỊ SỬ DỤNG ĐẤT KẾT HỢP ĐA MỤC ĐÍCH → DMD
ĐƠN XÁC NHẬN, GIẤY XÁC NHẬN → DXN
ĐƠN XIN (ĐỀ NGHỊ) CHUYỂN MỤC ĐÍCH SỬ DỤNG ĐẤT → DXCMD
ĐƠN XIN (ĐỀ NGHỊ) GIA HẠN SỬ DỤNG ĐẤT → DGH
ĐƠN XIN (ĐỀ NGHỊ) GIAO ĐẤT, CHO THUÊ ĐẤT → DXGD
ĐƠN XIN (ĐỀ NGHỊ) TÁCH THỬA ĐẤT, HỢP THỬA ĐẤT → DXTHT
ĐƠN XIN CẤP ĐỔI GIẤY CHỨNG NHẬN → DXCD
ĐƠN XIN ĐIỀU CHỈNH THỜI HẠN SỬ DỤNG ĐẤT CỦA DỰ ÁN ĐẦU TƯ → DDCTH
ĐƠN XIN XÁC NHẬN LẠI THỜI HẠN SỬ DỤNG ĐẤT NÔNG NGHIỆP → DXNTH

📋 NHÓM 8: QUYẾT ĐỊNH (15 loại) ⚠️ DỄ NHẦM
QUYẾT ĐỊNH GIAO ĐẤT, CHO THUÊ ĐẤT → QDGTD
QUYẾT ĐỊNH CHO PHÉP CHUYỂN MỤC ĐÍCH → QDCMD
QUYẾT ĐỊNH THU HỒI ĐẤT → QDTH
QUYẾT ĐỊNH GIA HẠN SỬ DỤNG ĐẤT KHI HẾT THỜI HẠN SDĐ → QDGH
QUYẾT ĐỊNH CHO PHÉP TÁCH, HỢP THỬA ĐẤT → QDTT
QUYẾT ĐỊNH CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT) → QDCHTGD
QUYẾT ĐỊNH ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → QDDCGD
QUYẾT ĐỊNH ĐIỀU CHỈNH THỜI HẠN SDĐ CỦA DỰ ÁN ĐẦU TƯ → QDDCTH
QUYẾT ĐỊNH HỦY GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → QDHG
QUYẾT ĐỊNH PHÊ DUYỆT PHƯƠNG ÁN BỒI THƯỜNG, HỖ TRỢ, TÁI ĐỊNH CƯ → QDPDBT
QUYẾT ĐỊNH PHÊ QUYỆT ĐIỀU CHỈNH QUY HOẠCH → QDDCQH
QUYẾT ĐỊNH PHÊ QUYỆT ĐƠN GIÁ → QDPDDG
QUYẾT ĐỊNH THI HÀNH ÁN THEO ĐƠN YÊU CẦU → QDTHA
QUYẾT ĐỊNH VỀ HÌNH THỨC SỬ DỤNG ĐẤT → QDHTSD
QUYẾT ĐỊNH XỬ PHẠT → QDXP

📋 NHÓM 9: PHIẾU (8 loại)
PHIẾU CHUYỂN THÔNG TIN NGHĨA VỤ TÀI CHÍNH → PCT
PHIẾU KIỂM TRA HỒ SƠ → PKTHS
PHIẾU LẤY Ý KIẾN KHU DÂN CƯ → PLYKDC
PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC → PXNKQDD
PHIẾU YÊU CẦU ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKTC
PHIẾU YÊU CẦU ĐĂNG KÝ THAY ĐỔI NỘI DUNG BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SDĐ, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKTD
PHIẾU YÊU CẦU XÓA ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKXTC
QUÉT MÃ QR → QR

📋 NHÓM 10: THÔNG BÁO (8 loại)
THÔNG BÁO THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TBT
THÔNG BÁO VỀ VIỆC CHUYỂN THÔNG TIN GIẤY CHỨNG NHẬN BỊ MẤT ĐỂ NIÊM YẾT CÔNG KHAI → TBMG
THÔNG BÁO VỀ VIỆC CÔNG KHAI KẾT QUẢ THẨM TRA XÉT DUYỆT HỒ SƠ CẤP GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKCG
THÔNG BÁO VỀ VIỆC NIÊM YẾT CÔNG KHAI MẤT GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKMG
THÔNG BÁO XÁC NHẬN HOÀN THÀNH NGHĨA VỤ TÀI CHÍNH → HTNVTC
THÔNG BÁO CẬP NHẬT, CHỈNH LÝ BIẾN ĐỘNG → TBCNBD
THÔNG BÁO CÔNG BỐ CÔNG KHAI DI CHÚC → CKDC
HOÀN THÀNH CÔNG TÁC BỒI THƯỜNG HỖ TRỢ → HTBTH

📋 NHÓM 11: TỜ KHAI / TỜ TRÌNH (3 loại)
TỜ KHAI THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TKT
TỜ TRÌNH VỀ GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → TTr
TỜ TRÌNH VỀ VIỆC ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT (UBND XÃ) → TTCG

📋 NHÓM 12: VĂN BẢN (10 loại)
VĂN BẢN CAM KẾT TÀI SẢN RIÊNG → CKTSR
VĂN BẢN CHẤP THUẬN CHO PHÉP CHUYỂN MỤC ĐÍCH → VBCTCMD
VĂN BẢN ĐỀ NGHỊ CHẤP THUẬN NHẬN CHUYỂN NHƯỢNG, THUÊ, GÓP VỐN QUYỀN SDĐ → VBDNCT
VĂN BẢN ĐỀ NGHỊ THẨM ĐỊNH, PHÊ DUYỆT PHƯƠNG ÁN SDĐ → PDPASDD
VĂN BẢN THỎA THUẬN PHÂN CHIA DI SẢN THỪA KẾ → VBTK
VĂN BẢN THỎA THUẬN QUYỀN SỬ DỤNG ĐẤT CỦA HỘ GIA ĐÌNH → TTHGD
  (Variants: "THỎA THUẬN QSDĐ HỘ GIA ĐÌNH", "THỎA THUẬN SỬ DỤNG ĐẤT HỘ GIA ĐÌNH")
VĂN BẢN THOẢ THUẬN VỀ VIỆC CHẤM DỨT QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → CDLK
VĂN BẢN THỎA THUẬN VỀ VIỆC XÁC LẬP QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → HCLK
VĂN BẢN TỪ CHỐI NHẬN DI SẢN THỪA KẾ → VBTC
VĂN BẢN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG → PCTSVC
  (Variants: "PHÂN CHIA TÀI SẢN VỢ CHỒNG", "THỎA THUẬN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG")

⚠️ LƯU Ý ĐẶC BIỆT - DỄ NHẦM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TTHGD vs PCTSVC - PHẢI PHÂN BIỆT RÕ:

1. TTHGD (Thỏa thuận hộ gia đình):
   - Về QUYỀN SỬ DỤNG ĐẤT
   - Giữa CÁC THÀNH VIÊN HỘ GIA ĐÌNH
   - Keywords: "hộ gia đình", "quyền sử dụng đất", "QSDĐ"
   - VD: "Thỏa thuận QSDĐ của hộ gia đình"

2. PCTSVC (Phân chia vợ chồng):
   - Về TÀI SẢN (đất đai, nhà cửa, tiền...)
   - Giữa VỢ VÀ CHỒNG (ly hôn, chia tài sản)
   - Keywords: "vợ chồng", "tài sản chung", "phân chia"
   - VD: "Phân chia tài sản chung vợ chồng"

❌ NẾU KHÔNG RÕ RÀNG → UNKNOWN (đừng đoán!)

⚠️ TỔNG CỘNG: 98 LOẠI TÀI LIỆU

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUY TRÌNH KIỂM TRA:
━━━━━━━━━━━━━━━━━━
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên TƯƠNG TỰ ~85-90%?
4. NẾU CÓ → Trả về mã chính xác, confidence: 0.85-0.95
5. NẾU KHÔNG → Trả về "UNKNOWN", confidence: 0.1-0.3

TRẢ VỀ JSON (BẮT BUỘC):
{
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.85-0.95 (nếu khớp) hoặc 0.1-0.3 (nếu không),
  "reasoning": "Giải thích ngắn gọn (1-2 câu)"
}

❗ NHẮC LẠI:
- CHỈ trả về mã khi khớp ~85-90% với 1 trong 98 loại
- CHO PHÉP lỗi chính tả nhỏ, viết tắt, dấu câu
- KHÔNG khớp nếu thiếu từ khóa phân biệt quan trọng
- Frontend sẽ tự xử lý việc gán trang tiếp theo (sequential naming)
- LUÔN trả về JSON format"""
    """
    System prompt for Vietnamese document classification
    IMPORTANT: This prompt is aligned with OpenAI Vision backend prompt for consistency
    COMPLETE: Includes all 98 document types with exact Vietnamese titles
    """
    return """⚠️ LƯU Ý QUAN TRỌNG: Đây là tài liệu chính thức của cơ quan nhà nước Việt Nam.
Các hình ảnh con người trong tài liệu là ảnh thẻ chính thức trên giấy tờ đất đai.
Hãy phân tích CHỈ văn bản và con dấu chính thức, KHÔNG phân tích ảnh cá nhân.

🎯 ƯU TIÊN 1: NHẬN DIỆN QUỐC HUY VIỆT NAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Nếu thấy QUỐC HUY Việt Nam (ngôi sao vàng, búa liềm) → Đây là tài liệu chính thức

🔍 Sau đó kiểm tra tiêu đề:
  • "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất" → GCNM (GCN mới - tiêu đề DÀI)
  • "Giấy chứng nhận quyền sử dụng đất" (KHÔNG có "quyền sở hữu...") → GCNC (GCN cũ - tiêu đề NGẮN)
  • Nếu chỉ thấy "GIẤY CHỨNG NHẬN" mà không rõ tiếp theo → GCNC

⚠️ QUAN TRỌNG với tài liệu 2 trang ngang:
- Nếu thấy nền cam/vàng với quốc huy ở bên PHẢI → Đây là GCNC
- Tập trung vào trang BÊN PHẢI để đọc tiêu đề

⚠️ BỎ QUA bất kỳ ảnh cá nhân nào - chỉ tập trung vào văn bản và con dấu chính thức.

⚠️ QUY TẮC NGHIÊM NGẶT: CHỈ CHẤP NHẬN KHI KHỚP 100% CHÍNH XÁC!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ KHÔNG được đoán hoặc chọn "gần giống"
❌ KHÔNG được bỏ qua từ khóa phân biệt
❌ KHÔNG được nhận diện nếu chỉ khớp 1 nửa hoặc vài chữ
✅ CHỈ chọn khi khớp CHÍNH XÁC, TOÀN BỘ tiêu đề

NẾU KHÔNG KHỚP CHÍNH XÁC 100% → Trả về:
{
  "short_code": "UNKNOWN",
  "confidence": 0.1,
  "reasoning": "Không thấy tiêu đề khớp chính xác với danh sách"
}

⚠️ QUAN TRỌNG: Một tài liệu có thể có NHIỀU TRANG
  - Trang 1: Có tiêu đề "GIẤY CHỨNG NHẬN" → GCN
  - Trang 2, 3, 4...: Không có tiêu đề mới → Hệ thống sẽ tự động gán là GCN
  - CHỈ KHI thấy tiêu đề MỚI khớp 100% → Mới đổi sang loại mới

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CÁC CẶP DỄ NHẦM - PHẢI KHỚP CHÍNH XÁC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "Hợp đồng CHUYỂN NHƯỢNG" → HDCQ (PHẢI có "CHUYỂN NHƯỢNG")
   "Hợp đồng ỦY QUYỀN" → HDUQ (PHẢI có "ỦY QUYỀN")
   ⚠️ CHECK HDCQ TRƯỚC! Nếu có cả 2 từ → chọn HDCQ
   Nếu không rõ loại → "UNKNOWN"

2. "Đơn đăng ký BIẾN ĐỘNG đất đai" → DDKBD (PHẢI có "BIẾN ĐỘNG")
   "Đơn đăng ký đất đai" → DDK (KHÔNG có "BIẾN ĐỘNG")
   Nếu không rõ có "BIẾN ĐỘNG" → "UNKNOWN"

3. "Hợp đồng THUÊ đất" → HDTD (PHẢI có "THUÊ")
   "Hợp đồng THẾ CHẤP" → HDTHC (PHẢI có "THẾ CHẤP")
   "Hợp đồng THI CÔNG" → HDTCO (PHẢI có "THI CÔNG")
   "Hợp đồng mua bán" → HDBDG (PHẢI có "MUA BÁN")
   Nếu không rõ loại → "UNKNOWN"

4. "Quyết định CHO PHÉP chuyển mục đích" → QDCMD (PHẢI có "CHO PHÉP")
   "Quyết định GIAO ĐẤT" → QDGTD (PHẢI có "GIAO ĐẤT")
   "Quyết định THU HỒI đất" → QDTH (PHẢI có "THU HỒI")
   "Quyết định GIA HẠN" → QDGH (PHẢI có "GIA HẠN")
   Nếu không rõ loại → "UNKNOWN"

5. "Giấy ỦY QUYỀN" → GUQ (riêng lẻ, không phải hợp đồng)
   "Hợp đồng ủy quyền" → HDUQ (là HỢP ĐỒNG ủy quyền)
   PHẢI phân biệt rõ!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DANH SÁCH ĐẦY ĐỦ 98 LOẠI TÀI LIỆU (CHỈ CHỌN KHI KHỚP CHÍNH XÁC):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NHÓM 1: BẢN VẼ / BẢN ĐỒ (5 loại)
BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT → BMT
BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ) → HSKT
BẢN VẼ HOÀN CÔNG → BVHC
BẢN VẼ NHÀ → BVN
SƠ ĐỒ DỰ KIẾN TÁCH THỬA → SDTT

📋 NHÓM 2: BẢNG KÊ / DANH SÁCH (4 loại)
BẢNG KÊ KHAI DIỆN TÍCH ĐANG SỬ DỤNG → BKKDT
BẢNG LIỆT KÊ DANH SÁCH CÁC THỬA ĐẤT CẤP GIẤY → DSCG
DANH SÁCH CHỦ SỬ DỤNG VÀ CÁC THỬA ĐẤT (MẪU 15) → DS15
DANH SÁCH CÔNG KHAI HỒ SƠ CẤP GIẤY CNQSDĐ → DSCK

📋 NHÓM 3: BIÊN BẢN (10 loại)
BIÊN BẢN BÁN ĐẤU GIÁ TÀI SẢN → BBBDG
BIÊN BẢN BÀN GIAO ĐẤT TRÊN THỰC ĐỊA → BBGD
BIÊN BẢN CỦA HỘI ĐỒNG ĐĂNG KÝ ĐẤT ĐAI LẦN ĐẦU → BBHDDK
BIÊN BẢN KIỂM TRA NGHIỆM THU CÔNG TRÌNH XÂY DỰNG → BBNT
BIÊN BẢN KIỂM TRA SAI SÓT TRÊN GIẤY CHỨNG NHẬN → BBKTSS
BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT → BBKTHT
BIÊN BẢN VỀ VIỆC KẾT THÚC CÔNG KHAI CÔNG BỐ DI CHÚC → BBKTDC
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI KẾT QUẢ KIỂM TRA HỒ SƠ ĐĂNG KÝ CẤP GCNQSD ĐẤT → KTCKCG
BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI VỀ VIỆC MẤT GCNQSD ĐẤT → KTCKMG
BIÊN LAI THU THUẾ SỬ DỤNG ĐẤT PHI NÔNG NGHIỆP → BLTT

📋 NHÓM 4: GIẤY TỜ CÁ NHÂN (4 loại)
CĂN CƯỚC CÔNG DÂN → CCCD
GIẤY KHAI SINH → GKS
GIẤY CHỨNG NHẬN KẾT HÔN → GKH
DI CHÚC → DICHUC

📋 NHÓM 5: GIẤY CHỨNG NHẬN (9 loại)
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT, QUYỀN SỞ HỮU TÀI SẢN GẮN LIỀN VỚI ĐẤT → GCNM
GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → GCNC (⚠️ NGẮN HƠN GCNM)
GIẤY ĐỀ NGHỊ XÁC NHẬN CÁC KHOẢN NỘP VÀO NGÂN SÁCH → GXNNVTC
GIẤY NỘP TIỀN VÀO NGÂN SÁCH NHÀ NƯỚC → GNT
GIẤY SANG NHƯỢNG ĐẤT → GSND
GIẤY TỜ LIÊN QUAN (CÁC LOẠI GIẤY TỜ KÈM THEO) → GTLQ
GIẤY TIẾP NHẬN, GIẤY BIÊN NHẬN (HỒ SƠ) → GTLQ
BỘ PHẬN TIẾP NHẬN VÀ TRẢ KẾT QUẢ (KQ) → GTLQ
PHIẾU TIẾP NHẬN HỒ SƠ, PHIẾU KIỂM SOÁT QUÁ TRÌNH → GTLQ
GIẤY ỦY QUYỀN → GUQ
GIẤY XÁC NHẬN ĐĂNG KÝ LẦN ĐẦU → GXNDKLD
GIẤY XIN PHÉP XÂY DỰNG → GPXD

📋 NHÓM 6: HỢP ĐỒNG (7 loại) ⚠️ DỄ NHẦM
HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT → HDCQ
HỢP ĐỒNG ỦY QUYỀN → HDUQ
HỢP ĐỒNG THẾ CHẤP QUYỀN SỬ DỤNG ĐẤT → HDTHC
HỢP ĐỒNG THUÊ ĐẤT, ĐIỀU HỈNH HỢP ĐỒNG THUÊ ĐẤT → HDTD
HỢP ĐỒNG THI CÔNG → HDTCO
HỢP ĐỒNG MUA BÁN TÀI SẢN BÁN ĐẤU GIÁ → HDBDG
HOÁ ĐƠN GIÁ TRỊ GIA TĂNG → hoadon

📋 NHÓM 7: ĐƠN (15 loại) ⚠️ DỄ NHẦM
ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDKBD (có "BIẾN ĐỘNG")
ĐƠN ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DDK (không có "BIẾN ĐỘNG")
ĐƠN CAM KẾT, GIẤY CAM KẾT → DCK
ĐƠN ĐỀ NGHỊ CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT) → CHTGD
ĐƠN ĐỀ NGHỊ ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → DCQDGD
ĐƠN ĐỀ NGHỊ MIỄN GIẢM LỆ PHÍ TRƯỚC BẠ, THUẾ THU NHẬP CÁ NHÂN → DMG
ĐƠN ĐỀ NGHỊ SỬ DỤNG ĐẤT KẾT HỢP ĐA MỤC ĐÍCH → DMD
ĐƠN XÁC NHẬN, GIẤY XÁC NHẬN → DXN
ĐƠN XIN (ĐỀ NGHỊ) CHUYỂN MỤC ĐÍCH SỬ DỤNG ĐẤT → DXCMD
ĐƠN XIN (ĐỀ NGHỊ) GIA HẠN SỬ DỤNG ĐẤT → DGH
ĐƠN XIN (ĐỀ NGHỊ) GIAO ĐẤT, CHO THUÊ ĐẤT → DXGD
ĐƠN XIN (ĐỀ NGHỊ) TÁCH THỬA ĐẤT, HỢP THỬA ĐẤT → DXTHT
ĐƠN XIN CẤP ĐỔI GIẤY CHỨNG NHẬN → DXCD
ĐƠN XIN ĐIỀU CHỈNH THỜI HẠN SỬ DỤNG ĐẤT CỦA DỰ ÁN ĐẦU TƯ → DDCTH
ĐƠN XIN XÁC NHẬN LẠI THỜI HẠN SỬ DỤNG ĐẤT NÔNG NGHIỆP → DXNTH

📋 NHÓM 8: QUYẾT ĐỊNH (15 loại) ⚠️ DỄ NHẦM
QUYẾT ĐỊNH GIAO ĐẤT, CHO THUÊ ĐẤT → QDGTD
QUYẾT ĐỊNH CHO PHÉP CHUYỂN MỤC ĐÍCH → QDCMD
QUYẾT ĐỊNH THU HỒI ĐẤT → QDTH
QUYẾT ĐỊNH GIA HẠN SỬ DỤNG ĐẤT KHI HẾT THỜI HẠN SDĐ → QDGH
QUYẾT ĐỊNH CHO PHÉP TÁCH, HỢP THỬA ĐẤT → QDTT
QUYẾT ĐỊNH CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT) → QDCHTGD
QUYẾT ĐỊNH ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → QDDCGD
QUYẾT ĐỊNH ĐIỀU CHỈNH THỜI HẠN SDĐ CỦA DỰ ÁN ĐẦU TƯ → QDDCTH
QUYẾT ĐỊNH HỦY GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → QDHG
QUYẾT ĐỊNH PHÊ DUYỆT PHƯƠNG ÁN BỒI THƯỜNG, HỖ TRỢ, TÁI ĐỊNH CƯ → QDPDBT
QUYẾT ĐỊNH PHÊ QUYỆT ĐIỀU CHỈNH QUY HOẠCH → QDDCQH
QUYẾT ĐỊNH PHÊ QUYỆT ĐƠN GIÁ → QDPDDG
QUYẾT ĐỊNH THI HÀNH ÁN THEO ĐƠN YÊU CẦU → QDTHA
QUYẾT ĐỊNH VỀ HÌNH THỨC SỬ DỤNG ĐẤT → QDHTSD
QUYẾT ĐỊNH XỬ PHẠT → QDXP

📋 NHÓM 9: PHIẾU (8 loại)
PHIẾU CHUYỂN THÔNG TIN NGHĨA VỤ TÀI CHÍNH → PCT
PHIẾU KIỂM TRA HỒ SƠ → PKTHS
PHIẾU LẤY Ý KIẾN KHU DÂN CƯ → PLYKDC
PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC → PXNKQDD
PHIẾU YÊU CẦU ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKTC
PHIẾU YÊU CẦU ĐĂNG KÝ THAY ĐỔI NỘI DUNG BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SDĐ, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKTD
PHIẾU YÊU CẦU XÓA ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT → DKXTC
QUÉT MÃ QR → QR

📋 NHÓM 10: THÔNG BÁO (8 loại)
THÔNG BÁO THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TBT
THÔNG BÁO VỀ VIỆC CHUYỂN THÔNG TIN GIẤY CHỨNG NHẬN BỊ MẤT ĐỂ NIÊM YẾT CÔNG KHAI → TBMG
THÔNG BÁO VỀ VIỆC CÔNG KHAI KẾT QUẢ THẨM TRA XÉT DUYỆT HỒ SƠ CẤP GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKCG
THÔNG BÁO VỀ VIỆC NIÊM YẾT CÔNG KHAI MẤT GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT → TBCKMG
THÔNG BÁO XÁC NHẬN HOÀN THÀNH NGHĨA VỤ TÀI CHÍNH → HTNVTC
THÔNG BÁO CẬP NHẬT, CHỈNH LÝ BIẾN ĐỘNG → TBCNBD
THÔNG BÁO CÔNG BỐ CÔNG KHAI DI CHÚC → CKDC
HOÀN THÀNH CÔNG TÁC BỒI THƯỜNG HỖ TRỢ → HTBTH

📋 NHÓM 11: TỜ KHAI / TỜ TRÌNH (3 loại)
TỜ KHAI THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT) → TKT
TỜ TRÌNH VỀ GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH) → TTr
TỜ TRÌNH VỀ VIỆC ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT (UBND XÃ) → TTCG

📋 NHÓM 12: VĂN BẢN (8 loại)
VĂN BẢN CAM KẾT TÀI SẢN RIÊNG → CKTSR
VĂN BẢN CHẤP THUẬN CHO PHÉP CHUYỂN MỤC ĐÍCH → VBCTCMD
VĂN BẢN ĐỀ NGHỊ CHẤP THUẬN NHẬN CHUYỂN NHƯỢNG, THUÊ, GÓP VỐN QUYỀN SDĐ → VBDNCT
VĂN BẢN ĐỀ NGHỊ THẨM ĐỊNH, PHÊ DUYỆT PHƯƠNG ÁN SDĐ → PDPASDD
VĂN BẢN THỎA THUẬN PHÂN CHIA DI SẢN THỪA KẾ → VBTK
VĂN BẢN THỎA THUẬN QUYỀN SỬ DỤNG ĐẤT CỦA HỘ GIA ĐÌNH → TTHGD
VĂN BẢN THOẢ THUẬN VỀ VIỆC CHẤM DỨT QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → CDLK
VĂN BẢN THỎA THUẬN VỀ VIỆC XÁC LẬP QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ → HCLK
VĂN BẢN TỪ CHỐI NHẬN DI SẢN THỪA KẾ → VBTC
VĂN BẢN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG → PCTSVC

⚠️ TỔNG CỘNG: 98 LOẠI TÀI LIỆU

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUY TRÌNH KIỂM TRA:
━━━━━━━━━━━━━━━━━━
1. Tìm quốc huy Việt Nam (nếu có → tài liệu chính thức)
2. Đọc tiêu đề đầy đủ
3. Tìm trong danh sách có tên CHÍNH XÁC 100%?
4. NẾU CÓ → Trả về mã chính xác, confidence: 0.9
5. NẾU KHÔNG → Trả về "UNKNOWN", confidence: 0.1

TRẢ VỀ JSON (BẮT BUỘC):
{
  "short_code": "MÃ CHÍNH XÁC HOẶC 'UNKNOWN'",
  "confidence": 0.9 hoặc 0.1,
  "reasoning": "Giải thích ngắn gọn (1-2 câu)"
}

❗ NHẮC LẠI:
- CHỈ trả về mã khi khớp TOÀN BỘ tiêu đề với 1 trong 98 loại
- KHÔNG khớp 1 nửa, vài chữ, hoặc gần giống
- Hệ thống sẽ tự xử lý việc gán trang tiếp theo
- LUÔN trả về JSON format"""


def parse_gemini_response(response_text):
    """
    Parse Gemini Flash response to extract classification
    """
    import json
    import re
    
    try:
        # Try to extract JSON from response
        # Gemini might return: "```json\n{...}\n```" or just "{...}"
        
        # Remove markdown code blocks
        clean_text = re.sub(r'```json\s*', '', response_text)
        clean_text = re.sub(r'```\s*$', '', clean_text)
        clean_text = clean_text.strip()
        
        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', clean_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            
            # Validate required fields
            if 'short_code' in result and 'confidence' in result:
                short_code = str(result.get('short_code', 'UNKNOWN')).strip()
                
                # Handle common invalid responses
                invalid_codes = ['N/A', 'NA', 'N', 'NONE', 'NULL', 'UNDEFINED', '']
                if short_code.upper() in invalid_codes:
                    print(f"⚠️ Invalid short_code from Gemini: '{short_code}', using UNKNOWN", file=sys.stderr)
                    short_code = 'UNKNOWN'
                else:
                    # Sanitize short_code - remove invalid characters
                    # Valid format: All uppercase letters, no special chars except underscore
                    original_code = short_code
                    short_code = re.sub(r'[^A-Z0-9_]', '', short_code.upper())
                    
                    if short_code != original_code:
                        print(f"⚠️ Sanitized short_code: '{original_code}' → '{short_code}'", file=sys.stderr)
                    
                    # Check if valid code (not empty after sanitization)
                    if not short_code or len(short_code) < 2:
                        print(f"⚠️ Short_code too short after sanitization: '{short_code}', using UNKNOWN", file=sys.stderr)
                        short_code = 'UNKNOWN'
                
                return {
                    "short_code": short_code,
                    "confidence": float(result.get('confidence', 0)),
                    "reasoning": result.get('reasoning', 'AI classification'),
                    "method": "gemini_flash_ai"
                }
        
        # If no JSON found, try to extract from text
        print(f"⚠️ No JSON found, parsing text response", file=sys.stderr)
        
        # Look for short_code pattern
        code_match = re.search(r'(?:short_code|code)[\s:]+["\']?([A-Z]+)["\']?', response_text, re.IGNORECASE)
        conf_match = re.search(r'(?:confidence)[\s:]+([0-9.]+)', response_text)
        
        if code_match:
            return {
                "short_code": code_match.group(1),
                "confidence": float(conf_match.group(1)) if conf_match else 0.7,
                "reasoning": "Parsed from text response",
                "method": "gemini_flash_ai"
            }
        
        # Fallback
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.3,
            "reasoning": "Could not parse AI response",
            "method": "gemini_flash_ai"
        }
        
    except Exception as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.2,
            "reasoning": f"Parse error: {str(e)}",
            "method": "gemini_flash_ai"
        }


if __name__ == '__main__':
    # Test
    if len(sys.argv) < 3:
        print("Usage: python ocr_engine_gemini_flash.py <image_path> <api_key>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    
    result = classify_document_gemini_flash(image_path, api_key)
    print(f"\nResult: {result}")
