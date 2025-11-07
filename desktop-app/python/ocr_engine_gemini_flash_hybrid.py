#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Flash 2.0 - AI Document Classification Engine (HYBRID VERSION)

HYBRID = Best Architecture (new) + Best Content (existing)

Features:
- Single source of truth (CODE_DEFINITIONS)
- Auto-generated code list in prompt
- Strict validation
- Full 98 codes coverage
- Extensive Vietnamese-optimized prompt
- Smart resize + position-aware cropping
"""

import sys
import base64
from PIL import Image
import io


# =========================================================
# 1. CODE DEFINITIONS - SINGLE SOURCE OF TRUTH (98 codes)
# =========================================================

CODE_DEFINITIONS = {
    # ===== GCN GROUP =====
    "GCN": "Giấy chứng nhận QSDĐ/QSHNƠ/tài sản gắn liền đất (Generic - batch processing sẽ phân loại thành GCNM/GCNC)",
    "GCNM": "Giấy chứng nhận quyền sử dụng đất MỚI (màu hồng)",
    "GCNC": "Giấy chứng nhận quyền sử dụng đất CŨ (màu đỏ/cam)",
    
    # ===== BẢN VẼ / HỒ SƠ KỸ THUẬT =====
    "BMT": "Bản mô tả ranh giới, mốc giới thửa đất",
    "HSKT": "Bản vẽ (Trích lục, đo tách, chỉnh lý, bản đồ địa chính)",
    "BVHC": "Bản vẽ hoàn công",
    "BVN": "Bản vẽ nhà",
    "BKKDT": "Bảng kê khai diện tích đang sử dụng",
    "DSCG": "Bảng liệt kê danh sách các thửa đất cấp giấy",
    "SDPT": "Sơ đồ phân thửa",
    "SDTT": "Sơ đồ dự kiến tách thửa",
    
    # ===== ĐƠN / ĐĂNG KÝ / CAM KẾT =====
    "DDKBD": "Đơn đăng ký biến động đất đai, tài sản gắn liền với đất",
    "DDK": "Đơn đăng ký đất đai, tài sản gắn liền với đất",
    "DXTHT": "Đơn xin (đề nghị) tách thửa đất, hợp thửa đất",
    "DXGD": "Đơn xin (đề nghị) giao đất, cho thuê đất",
    "DXCMD": "Đơn xin (đề nghị) chuyển mục đích sử dụng đất",
    "DGH": "Đơn xin (đề nghị) gia hạn sử dụng đất",
    "DXCD": "Đơn xin cấp đổi Giấy chứng nhận",
    "DCK": "Đơn cam kết, Giấy cam kết",
    "DKTC": "Phiếu yêu cầu đăng ký biện pháp bảo đảm bằng quyền sử dụng đất",
    "DKXTC": "Phiếu yêu cầu xóa đăng ký biện pháp bảo đảm",
    "DKTD": "Phiếu yêu cầu đăng ký thay đổi nội dung biện pháp bảo đảm",
    "CHTGD": "Đơn đề nghị chuyển hình thức giao đất (cho thuê đất)",
    "DCQDGD": "Đơn đề nghị điều chỉnh quyết định giao đất",
    "DMG": "Đơn đề nghị miễn giảm lệ phí trước bạ, thuế",
    "DMD": "Đơn đề nghị sử dụng đất kết hợp đa mục đích",
    "DDCTH": "Đơn xin điều chỉnh thời hạn sử dụng đất",
    "DXNTH": "Đơn xin xác nhận lại thời hạn sử dụng đất nông nghiệp",
    
    # ===== HỢP ĐỒNG =====
    "HDCQ": "Hợp đồng chuyển nhượng, tặng cho quyền sử dụng đất",
    "HDTG": "Hợp đồng tặng cho (alias của HDCQ)",
    "HDBDG": "Hợp đồng mua bán tài sản bán đấu giá",
    "HDTHC": "Hợp đồng thế chấp quyền sử dụng đất",
    "HDTCO": "Hợp đồng thi công",
    "HDTD": "Hợp đồng thuê đất, điều chỉnh hợp đồng thuê đất",
    "HDUQ": "Hợp đồng ủy quyền",
    
    # ===== QUYẾT ĐỊNH =====
    "QDGTD": "Quyết định giao đất, cho thuê đất",
    "QDTT": "Quyết định cho phép tách, hợp thửa đất",
    "QDCMD": "Quyết định cho phép chuyển mục đích",
    "QDTH": "Quyết định thu hồi đất",
    "QDCHTGD": "Quyết định chuyển hình thức giao đất (cho thuê đất)",
    "QDDCGD": "Quyết định điều chỉnh quyết định giao đất",
    "QDDCTH": "Quyết định điều chỉnh thời hạn SDĐ",
    "QDGH": "Quyết định gia hạn sử dụng đất",
    "QDHG": "Quyết định hủy Giấy chứng nhận",
    "QDPDBT": "Quyết định phê duyệt phương án bồi thường, hỗ trợ, tái định cư",
    "QDDCQH": "Quyết định phê duyệt điều chỉnh quy hoạch",
    "QDPDDG": "Quyết định phê duyệt đơn giá",
    "QDTHA": "Quyết định thi hành án",
    "QDHTSD": "Quyết định về hình thức sử dụng đất",
    "QDXP": "Quyết định xử phạt",
    
    # ===== GIẤY / BIÊN NHẬN =====
    "GTLQ": "Giấy tiếp nhận hồ sơ và hẹn trả kết quả",
    "GUQ": "Giấy ủy quyền",
    "GNT": "Giấy nộp tiền vào Ngân sách nhà nước",
    "DXN": "Đơn xác nhận, Giấy xác nhận",
    "GKH": "Giấy chứng nhận kết hôn",
    "GKS": "Giấy Khai Sinh",
    "GXNNVTC": "Giấy đề nghị xác nhận các khoản nộp vào ngân sách",
    "GSND": "Giấy sang nhượng đất",
    "GXNDKLD": "Giấy xác nhận đăng ký lần đầu",
    "GPXD": "Giấy xin phép xây dựng",
    
    # ===== BIÊN BẢN =====
    "BBBDG": "Biên bản bán đấu giá tài sản",
    "BBGD": "Biên bản bàn giao đất trên thực địa",
    "BBHDDK": "Biên bản của Hội đồng đăng ký đất đai lần đầu",
    "BBNT": "Biên bản kiểm tra nghiệm thu công trình xây dựng",
    "BBKTSS": "Biên bản kiểm tra sai sót trên Giấy chứng nhận",
    "BBKTHT": "Biên bản kiểm tra, xác minh hiện trạng sử dụng đất",
    "BBKTDC": "Biên bản về việc kết thúc công khai công bố di chúc",
    "KTCKCG": "Biên bản kết thúc thông báo niêm yết công khai kết quả kiểm tra hồ sơ",
    "KTCKMG": "Biên bản kết thúc thông báo niêm yết công khai về mất GCNQSD đất",
    "BLTT": "Biên lai thu thuế sử dụng đất phi nông nghiệp",
    
    # ===== PHIẾU / BIỂU MẪU =====
    "PCT": "Phiếu chuyển thông tin nghĩa vụ tài chính",
    "PKTHS": "Phiếu kiểm tra hồ sơ",
    "PLYKDC": "Phiếu lấy ý kiến khu dân cư",
    "PXNKQDD": "Phiếu xác nhận kết quả đo đạc",
    "QR": "Quét mã QR",
    
    # ===== THÔNG BÁO =====
    "TBT": "Thông báo thuế (trước bạ, thuế TNCN, tiền sử dụng đất)",
    "TBMG": "Thông báo về việc chuyển thông tin Giấy chứng nhận bị mất",
    "TBCKCG": "Thông báo về việc công khai kết quả thẩm tra xét duyệt hồ sơ",
    "TBCKMG": "Thông báo về việc niêm yết công khai mất giấy chứng nhận",
    "TBCNBD": "Thông báo cập nhật, chỉnh lý biến động",
    "CKDC": "Thông báo công bố công khai di chúc",
    "HTNVTC": "Thông báo xác nhận Hoàn thành nghĩa vụ tài chính",
    
    # ===== TỜ KHAI / TỜ TRÌNH =====
    "TKT": "Tờ khai thuế (trước bạ, thuế TNCN, tiền sử dụng đất)",
    "TTr": "Tờ trình về giao đất (cho thuê đất, cho phép chuyển mục đích)",
    "TTCG": "Tờ trình về việc đăng ký đất đai, tài sản gắn liền với đất",
    
    # ===== VĂN BẢN DÂN SỰ / THỎA THUẬN =====
    "CKTSR": "Văn bản cam kết tài sản riêng",
    "VBCTCMD": "Văn bản chấp thuận cho phép chuyển mục đích",
    "PCTSVC": "Văn bản phân chia tài sản vợ chồng",
    
    # ===== KHÁC =====
    "CCCD": "Căn cước công dân",
    "DS15": "Danh sách chủ sử dụng và các thửa đất (mẫu 15)",
    "DSCK": "Danh sách công khai hồ sơ cấp giấy CNQSDĐ",
    "DICHUC": "Di chúc",
    "hoadon": "Hoá đơn giá trị gia tăng",
    "HTBTH": "Hoàn thành công tác bồi thường hỗ trợ",
}

# Allowed codes = all defined codes + UNKNOWN
ALLOWED_SHORT_CODES = set(CODE_DEFINITIONS.keys()) | {"UNKNOWN"}

print(f"📚 Loaded {len(CODE_DEFINITIONS)} document type definitions", file=sys.stderr)


def get_code_list_summary() -> str:
    """
    Generate grouped code list for prompt (organized by category)
    Auto-generated from CODE_DEFINITIONS
    """
    lines = []
    
    # Group codes by category
    groups = {
        "GCN": ["GCN", "GCNM", "GCNC"],
        "Bản vẽ/Sơ đồ": ["BMT", "HSKT", "BVHC", "BVN", "BKKDT", "DSCG", "SDPT", "SDTT"],
        "Đơn/Đăng ký": ["DDKBD", "DDK", "DXTHT", "DXGD", "DXCMD", "DGH", "DXCD", "DCK", 
                         "DKTC", "DKXTC", "DKTD", "CHTGD", "DCQDGD", "DMG", "DMD", "DDCTH", "DXNTH"],
        "Hợp đồng": ["HDCQ", "HDTG", "HDBDG", "HDTHC", "HDTCO", "HDTD", "HDUQ"],
        "Quyết định": ["QDGTD", "QDTT", "QDCMD", "QDTH", "QDCHTGD", "QDDCGD", "QDDCTH", 
                       "QDGH", "QDHG", "QDPDBT", "QDDCQH", "QDPDDG", "QDTHA", "QDHTSD", "QDXP"],
        "Giấy": ["GTLQ", "GUQ", "GNT", "DXN", "GKH", "GKS", "GXNNVTC", "GSND", "GXNDKLD", "GPXD"],
        "Biên bản": ["BBBDG", "BBGD", "BBHDDK", "BBNT", "BBKTSS", "BBKTHT", "BBKTDC", 
                     "KTCKCG", "KTCKMG", "BLTT"],
        "Phiếu": ["PCT", "PKTHS", "PLYKDC", "PXNKQDD", "QR"],
        "Thông báo": ["TBT", "TBMG", "TBCKCG", "TBCKMG", "TBCNBD", "CKDC", "HTNVTC"],
        "Tờ khai/Trình": ["TKT", "TTr", "TTCG"],
        "Văn bản dân sự": ["CKTSR", "VBCTCMD", "PCTSVC"],
        "Khác": ["CCCD", "DS15", "DSCK", "DICHUC", "hoadon", "HTBTH"]
    }
    
    for group_name, codes in groups.items():
        lines.append(f"\n📌 {group_name.upper()}:")
        for code in codes:
            if code in CODE_DEFINITIONS:
                lines.append(f"  {code} = {CODE_DEFINITIONS[code]}")
    
    lines.append("\n📌 UNKNOWN = Khi không khớp chắc chắn với bất kỳ mã nào")
    
    return "\n".join(lines)


# =========================================================
# 2. IMAGE PROCESSING
# =========================================================

def resize_image_smart(img, max_width=2000, max_height=2800):
    """Smart resize: only if exceeds limits, maintains aspect ratio"""
    width, height = img.size
    
    if width <= max_width and height <= max_height:
        return img, {
            "resized": False,
            "original_size": f"{width}x{height}",
            "final_size": f"{width}x{height}",
            "reduction_percent": 0
        }
    
    width_ratio = max_width / float(width)
    height_ratio = max_height / float(height)
    scale_factor = min(width_ratio, height_ratio)
    
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    reduction = (1 - (new_width * new_height) / (width * height)) * 100
    
    print(
        f"🔽 Image resized: {width}x{height} → {new_width}x{new_height} "
        f"(-{reduction:.1f}% pixels)",
        file=sys.stderr
    )
    
    return resized_img, {
        "resized": True,
        "original_size": f"{width}x{height}",
        "final_size": f"{new_width}x{new_height}",
        "reduction_percent": round(reduction, 1)
    }


def encode_image_to_base64(
    image_path,
    crop_top_percent=1.0,
    position_aware=True,
    enable_resize=True,
    max_width=2000,
    max_height=2800
):
    """
    Load image, optionally crop top %, optionally resize, return base64 JPEG
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Crop to top % if position_aware and < 1.0
            if position_aware and crop_top_percent < 1.0:
                crop_height = int(height * crop_top_percent)
                img = img.crop((0, 0, width, crop_height))
                print(
                    f"✂️ Cropped to top {int(crop_top_percent*100)}%: "
                    f"{width}x{height} → {width}x{crop_height}",
                    file=sys.stderr
                )
            else:
                print(f"🖼️ Processing full image: {width}x{height} (position-aware mode)", file=sys.stderr)
            
            # Smart resize if enabled
            if enable_resize:
                img, resize_info = resize_image_smart(img, max_width, max_height)
            else:
                resize_info = {
                    "resized": False,
                    "original_size": f"{img.size[0]}x{img.size[1]}",
                    "final_size": f"{img.size[0]}x{img.size[1]}",
                    "reduction_percent": 0
                }
            
            # Convert to JPEG base64
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            
            return encoded, resize_info
            
    except Exception as e:
        print(f"❌ Error encoding image: {e}", file=sys.stderr)
        raise


# =========================================================
# 3. PROMPT (EXTENSIVE + VIETNAMESE-OPTIMIZED)
# =========================================================

def get_classification_prompt_lite():
    """
    OPTIMIZED prompt for Flash Lite
    Full rules + auto-generated code list from CODE_DEFINITIONS
    """
    return f"""🎯 NHIỆM VỤ: Phân loại tài liệu đất đai Việt Nam

📋 QUY TẮC PHÂN LOẠI (QUAN TRỌNG):

🔍 1. VỊ TRÍ TIÊU ĐỀ (TOP 30%):
✅ CHỈ PHÂN LOẠI NẾU:
- Text LỚN NHẤT, IN HOA, căn giữa
- NẰM ĐỘC LẬP (không có text khác cùng dòng)
- VD đúng: "HỢP ĐỒNG CHUYỂN NHƯỢNG" (riêng 1 dòng)
- VD sai: "theo Giấy chứng nhận số..." (có "theo" + số)

❌ BỎ QUA NẾU:
- Text ở giữa/cuối trang (MIDDLE/BOTTOM)
- Có từ: "căn cứ", "theo", "kèm theo", "số..."
- NẰM CHUNG với text khác trên cùng dòng
- Chữ thường trong câu văn

👁️ 2. VISUAL INDICATORS:
✅ QUỐC HUY (National Emblem):
- Có QUỐC HUY ở top center → GCN (Giấy chứng nhận)
- Có QUỐC HUY + "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" → Giấy tờ chính thức

✅ LAYOUT:
- CERTIFICATE: Có quốc huy, serial, filled data, formal layout
- FORM: Có blank fields, ô trống, checkbox, table để điền
- MAP: Có sơ đồ, ranh giới, coordinates, visual diagram
- NOTICE: Header quan, footer chữ ký, structured sections

⚠️ 3. GCN SPECIAL RULES (CỰC KỲ QUAN TRỌNG):
🚨 LUÔN trả về "GCN" (KHÔNG bao giờ "GCNM" hay "GCNC") 🚨

• ⚠️ BẮT BUỘC 1: XÁC ĐỊNH MÀU SẮC (COLOR - QUAN TRỌNG NHẤT):
  - Màu ĐỎ/CAM (red/orange): GCN cũ → color: "red"
  - Màu HỒNG (pink): GCN mới → color: "pink"
  - Không xác định được: color: "unknown"

• ⚠️ BẮT BUỘC 2: TÌM NGÀY CẤP (có thể viết tay):
  - Formats: "DD/MM/YYYY", "Ngày DD tháng MM năm YYYY", "DD.MM.YYYY"
  - Tìm gần: "Ngày cấp", "Cấp ngày", "Ngày...tháng...năm", "TM. UBND"
  - GCN A3 (2 trang): Ngày thường ở trang 2
  - GCN A4 (1 trang): Ngày thường ở bottom trang 1
  - ⚠️ "Ngày 25 tháng 8 năm 2010" → "25/08/2010" hoặc "25/8/2010"
  - Nếu mờ: "MM/YYYY" hoặc "YYYY"
  - Không tìm thấy: null + "not_found"

• Response example:
  {{
    "short_code": "GCN",
    "color": "pink",
    "issue_date": "14/04/2025",
    "issue_date_confidence": "full",
    "confidence": 0.95
  }}

⚠️ 4. GCN CONTINUATION PAGE:
NẾU THẤY (đứng riêng, không tiêu đề chính):
- "III. THÔNG TIN VỀ THỬA ĐẤT"
- "IV. THÔNG TIN VỀ TÀI SẢN..."
- "V. THÔNG TIN VỀ HẠN CHẾ..." + bảng
→ Trả về GCN (trang tiếp theo)

🔧 5. CÁC CẶP DỄ NHẦM:

A) DDKBD vs GCN:
- DDKBD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG", nhiều ô trống
- GCN: Giấy đã cấp, có quốc huy, serial

B) DXTHT vs DDKBD:
- DXTHT: "ĐƠN ĐỀ NGHỊ TÁCH THỪA, HỢP THỪA"
- DDKBD: "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG"
- ⚠️ Ưu tiên DXTHT nếu có từ "tách" hoặc "hợp"

C) HSKT vs GCN:
- HSKT: Sơ đồ, tọa độ, tỉ lệ 1/500, bản vẽ
- GCN: Giấy chứng nhận, không phải bản vẽ

D) GTLQ vs PKTHS:
- GTLQ: "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ"
- PKTHS: "PHIẾU KIỂM TRA HỒ SƠ" (nội bộ)

E) PCTSVC vs Others:
- PCTSVC: có "VỢ CHỒNG" + phân chia tài sản
- TTHGD: có "HỘ GIA ĐÌNH"

📤 ĐỊNH DẠNG JSON (BẮT BUỘC):
{{
  "short_code": "MÃ_HỢP_LỆ_HOẶC_UNKNOWN",
  "confidence": 0.0-1.0,
  "title_position": "top" | "middle" | "bottom" | "none",
  "reasoning": "Ngắn gọn: từ khóa + vị trí + logic",
  "color": "red" | "pink" | "unknown" | null,
  "issue_date": "DD/MM/YYYY" | "MM/YYYY" | "YYYY" | null,
  "issue_date_confidence": "full" | "partial" | "year_only" | "not_found"
}}

❌ KHÔNG trả text ngoài JSON
❌ KHÔNG tự tạo mã mới
❌ NẾU không chắc → "UNKNOWN"

──────────────────
✅ DANH SÁCH {len(CODE_DEFINITIONS)} MÃ HỢP LỆ:
──────────────────
{get_code_list_summary()}

──────────────────
⚠️ LƯU Ý CUỐI:
- Chỉ chọn mã khi tiêu đề + ngữ cảnh khớp rõ ràng
- "căn cứ...", "theo..." → chỉ là tham chiếu, không dùng phân loại
- Không chắc chắn → "UNKNOWN"
"""


def get_classification_prompt():
    """
    FULL prompt with extensive examples
    """
    core = get_classification_prompt_lite()
    
    examples = """

📌 VÍ DỤ MINH HỌA:

1) GCN rõ ràng (màu hồng):
{{
  "short_code": "GCN",
  "color": "pink",
  "issue_date": "14/04/2025",
  "issue_date_confidence": "full",
  "confidence": 0.97,
  "title_position": "top",
  "reasoning": "Giấy chứng nhận màu hồng, ngày cấp 14/04/2025"
}}

2) GCN format "Ngày...tháng...năm":
{{
  "short_code": "GCN",
  "color": "red",
  "issue_date": "25/8/2010",
  "issue_date_confidence": "full",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "GCN màu đỏ, ngày từ 'Ngày 25 tháng 8 năm 2010'"
}}

3) GCN trang tiếp theo:
{{
  "short_code": "GCN",
  "confidence": 0.78,
  "title_position": "none",
  "reasoning": "Trang biến động tiếp theo của GCN"
}}

4) DDKBD:
{{
  "short_code": "DDKBD",
  "confidence": 0.95,
  "title_position": "top",
  "reasoning": "Đơn đăng ký biến động"
}}

5) DXTHT (phân biệt với DDKBD):
{{
  "short_code": "DXTHT",
  "confidence": 0.93,
  "title_position": "top",
  "reasoning": "Đơn đề nghị tách hợp thửa"
}}

6) HDCQ:
{{
  "short_code": "HDCQ",
  "confidence": 0.93,
  "title_position": "top",
  "reasoning": "Hợp đồng chuyển nhượng"
}}

7) GTLQ:
{{
  "short_code": "GTLQ",
  "confidence": 0.93,
  "title_position": "top",
  "reasoning": "Giấy tiếp nhận & hẹn trả KQ"
}}

8) HSKT:
{{
  "short_code": "HSKT",
  "confidence": 0.94,
  "title_position": "top",
  "reasoning": "Bản vẽ với sơ đồ & tỉ lệ"
}}

9) PCTSVC:
{{
  "short_code": "PCTSVC",
  "confidence": 0.92,
  "title_position": "top",
  "reasoning": "Văn bản phân chia tài sản vợ chồng"
}}

10) UNKNOWN (chỉ tham chiếu):
{{
  "short_code": "UNKNOWN",
  "confidence": 0.3,
  "title_position": "middle",
  "reasoning": "Chỉ câu tham chiếu, không có tiêu đề"
}}
"""
    
    return core + examples


# =========================================================
# 4. API CALL
# =========================================================

def build_gemini_flash_request_payload(encoded_image, is_lite=True):
    """Build request payload with prompt + image"""
    prompt = get_classification_prompt_lite() if is_lite else get_classification_prompt()
    print(f"🧠 Using prompt: {len(prompt)} chars", file=sys.stderr)
    
    return {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ]
    }


def call_gemini_flash_api(encoded_image, api_key, is_lite=True):
    """Call Gemini Flash 2.0 API"""
    try:
        import requests
    except ImportError:
        print("❌ Missing requests. pip install requests", file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": "Missing requests library"
        }
    
    model = "gemini-2.5-flash-lite" if is_lite else "gemini-2.5-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    payload = build_gemini_flash_request_payload(encoded_image, is_lite=is_lite)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    try:
        print(f"📡 Sending request to {model}...", file=sys.stderr)
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        print(f"📊 Response status: {resp.status_code}", file=sys.stderr)
        
        if resp.status_code != 200:
            print(f"❌ Error: {resp.text}", file=sys.stderr)
            return {
                "short_code": "ERROR",
                "confidence": 0,
                "reasoning": f"HTTP {resp.status_code}"
            }
        
        return parse_gemini_flash_response(resp.json())
        
    except Exception as e:
        print(f"❌ API error: {e}", file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Exception: {str(e)}"
        }


# =========================================================
# 5. RESPONSE PARSING + STRICT VALIDATION
# =========================================================

def parse_gemini_flash_response(data):
    """
    Parse Gemini response with STRICT validation against ALLOWED_SHORT_CODES
    """
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            return {
                "short_code": "UNKNOWN",
                "confidence": 0,
                "reasoning": "No candidates in response"
            }
        
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return {
                "short_code": "UNKNOWN",
                "confidence": 0,
                "reasoning": "No parts in response"
            }
        
        response_text = "".join(p.get("text", "") for p in parts)
        print(f"📨 Raw response (truncated): {response_text[:300]}...", file=sys.stderr)
        
        import json
        import re
        
        # Extract JSON
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try:
                obj = json.loads(match.group(0))
                return _normalize_and_validate(obj)
            except Exception as e:
                print(f"⚠️ JSON parse error: {e}", file=sys.stderr)
        
        # Fallback heuristic
        return _heuristic_parse(response_text)
        
    except Exception as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return {
            "short_code": "UNKNOWN",
            "confidence": 0.2,
            "reasoning": f"Parse exception: {str(e)}"
        }


def _normalize_and_validate(obj):
    """
    Normalize parsed object + STRICT VALIDATION
    """
    short_code = str(obj.get("short_code", "UNKNOWN")).strip().upper()
    confidence = float(obj.get("confidence", 0))
    title_position = obj.get("title_position", "unknown")
    reasoning = obj.get("reasoning", "")
    color = obj.get("color")
    issue_date = obj.get("issue_date")
    issue_date_confidence = obj.get("issue_date_confidence")
    
    # STRICT VALIDATION
    if short_code not in ALLOWED_SHORT_CODES:
        print(f"⚠️ Invalid code '{short_code}' not in ALLOWED_SHORT_CODES, forcing UNKNOWN", file=sys.stderr)
        short_code = "UNKNOWN"
        confidence = min(confidence, 0.5)
    
    # Color only for GCN
    if short_code not in ["GCN", "GCNM", "GCNC"]:
        color = None
    
    # Clean empty strings
    if isinstance(issue_date, str) and not issue_date.strip():
        issue_date = None
    
    print(f"⏱️ Result: {short_code} (confidence: {confidence:.2f}, position: {title_position})", file=sys.stderr)
    
    return {
        "short_code": short_code,
        "confidence": confidence,
        "title_position": title_position,
        "reasoning": reasoning,
        "color": color,
        "issue_date": issue_date,
        "issue_date_confidence": issue_date_confidence,
        "method": "gemini_flash_ai"
    }


def _heuristic_parse(text):
    """
    Fallback heuristic parsing when JSON fails
    """
    import re
    
    code_match = re.search(r'"?short_code"?\s*[:=]\s*"?([A-Z0-9_]+)"?', text)
    conf_match = re.search(r'"?confidence"?\s*[:=]\s*([0-9.]+)', text)
    
    short_code = "UNKNOWN"
    confidence = 0.3
    
    if code_match:
        cand = code_match.group(1).upper()
        if cand in ALLOWED_SHORT_CODES:
            short_code = cand
        else:
            print(f"⚠️ Heuristic found invalid '{cand}', using UNKNOWN", file=sys.stderr)
    
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
        except:
            confidence = 0.3
    
    return {
        "short_code": short_code,
        "confidence": confidence,
        "reasoning": "Heuristic parse (non-JSON response)",
        "title_position": "unknown",
        "method": "gemini_flash_ai"
    }


# =========================================================
# 6. PUBLIC API
# =========================================================

def classify_document_gemini_flash(
    image_path,
    api_key,
    crop_top_percent=1.0,
    model_type='gemini-flash-lite',
    enable_resize=True,
    max_width=2000,
    max_height=2800
):
    """
    High-level API for document classification
    
    Args:
        image_path: Path to image
        api_key: Google API key
        crop_top_percent: Top % to process (1.0 = full image)
        model_type: 'gemini-flash-lite' or 'gemini-flash'
        enable_resize: Smart resize for cost optimization
        max_width, max_height: Resize limits
    
    Returns:
        dict with short_code, confidence, color, issue_date, etc.
    """
    try:
        is_lite = (model_type == 'gemini-flash-lite')
        position_aware = True
        
        print(f"🤖 Using Gemini {'Lite' if is_lite else 'Flash'} AI with POSITION-AWARE classification", file=sys.stderr)
        print(f"📸 Scanning FULL IMAGE with position-aware analysis...", file=sys.stderr)
        print(f"💰 Smart resize enabled: max {max_width}x{max_height}px", file=sys.stderr)
        
        # Encode image
        encoded_image, resize_info = encode_image_to_base64(
            image_path,
            crop_top_percent=crop_top_percent,
            position_aware=position_aware,
            enable_resize=enable_resize,
            max_width=max_width,
            max_height=max_height
        )
        
        # Call API
        result = call_gemini_flash_api(encoded_image, api_key, is_lite=is_lite)
        
        # Add metadata
        result["image_resize_info"] = resize_info
        result["position_aware"] = position_aware
        result["crop_top_percent"] = crop_top_percent
        
        return result
        
    except Exception as e:
        print(f"❌ classify_document_gemini_flash error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "short_code": "ERROR",
            "confidence": 0,
            "reasoning": f"Exception: {str(e)}"
        }


# =========================================================
# 7. CLI TEST
# =========================================================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr_engine_gemini_flash_hybrid.py <image_path> <api_key> [model_type]")
        print("  model_type: 'gemini-flash-lite' (default) or 'gemini-flash'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2]
    model_type = sys.argv[3] if len(sys.argv) > 3 else 'gemini-flash-lite'
    
    result = classify_document_gemini_flash(
        image_path,
        api_key,
        model_type=model_type
    )
    
    print("\n" + "="*60)
    print("CLASSIFICATION RESULT:")
    print("="*60)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
