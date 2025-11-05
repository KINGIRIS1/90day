"""
COMPLETE Rule-based classifier for Vietnamese land documents with Smart Scoring
- HYBRID APPROACH: EXACT title → Fuzzy title (80%+) → Keyword fallback
- Tier 0: EXACT title match → Instant confidence 100%
- Tier 1: Title similarity >= 80% → High confidence (Instant match)
- Tier 2: Title similarity 70-80% → Verify with keywords
- Tier 3: Title similarity < 70% → Pure keyword matching
"""
import re
import sys
import os
import json
from typing import Dict, Tuple, List
from difflib import SequenceMatcher
from pathlib import Path

# TIER 0: EXACT Title Matching (100% confidence)
# User-provided exact titles for precise matching
EXACT_TITLE_MAPPING = {
    "BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT": "BMT",
    "BẢN VẼ (TRÍCH LỤC, ĐO TÁCH, CHỈNH LÝ)": "HSKT",
    "ĐỒ ĐẠC CHÍNH LÝ BẢN ĐỒ ĐỊA CHÍNH": "HSKT",
    "BẢN VẼ HOÀN CÔNG": "BVHC",
    "BẢN VẼ NHÀ": "BVN",
    "BẢNG KÊ KHAI DIỆN TÍCH ĐANG SỬ DỤNG": "BKKDT",
    "BẢNG LIỆT KÊ DANH SÁCH CÁC THỬA ĐẤT CẤP GIẤY": "DSCG",
    "BIÊN BẢN BÁN ĐẤU GIÁ TÀI SẢN": "BBBDG",
    "BIÊN BẢN BÀN GIAO ĐẤT TRÊN THỰC ĐỊA": "BBGD",
    "BIÊN BẢN CỦA HỘI ĐỒNG ĐĂNG KÝ ĐẤT ĐAI LẦN ĐẦU": "BBHDDK",
    "BIÊN BẢN KIỂM TRA NGHIỆM THU CÔNG TRÌNH XÂY DỰNG": "BBNT",
    "BIÊN BẢN KIỂM TRA SAI SÓT TRÊN GIẤY CHỨNG NHẬN": "BBKTSS",
    "BIÊN BẢN KIỂM TRA, XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT": "BBKTHT",
    "BIÊN BẢN VỀ VIỆC KẾT THÚC CÔNG KHAI CÔNG BỐ DI CHÚC": "BBKTDC",
    "BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI KẾT QUẢ KIỂM TRA HỒ SƠ ĐĂNG KÝ CẤP GCNQSD ĐẤT": "KTCKCG",
    "BIÊN BẢN VỀ VIỆC KẾT THÚC THÔNG BÁO NIÊM YẾT CÔNG KHAI VỀ VIỆC MẤT GCNQSD ĐẤT": "KTCKMG",
    "BIÊN LAI THU THUẾ SỬ DỤNG ĐẤT PHI NÔNG NGHIỆP": "BLTT",
    "CĂN CƯỚC CÔNG DÂN": "CCCD",
    "DANH SÁCH CHỦ SỬ DỤNG VÀ CÁC THỬA ĐẤT (MẪU 15)": "DS15",
    "DANH SÁCH CÔNG KHAI HỒ SƠ CẤP GIẤY CNQSDĐ": "DSCK",
    "DI CHÚC": "DICHUC",
    "ĐƠN CAM KẾT, GIẤY CAM KẾT": "DCK",
    "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT": "DDKBD",
    "ĐƠN ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT": "DDK",
    "ĐƠN ĐỀ NGHỊ CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT)": "CHTGD",
    "ĐƠN ĐỀ NGHỊ ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH)": "DCQDGD",
    "ĐƠN ĐỀ NGHỊ MIỄN GIẢM LỆ PHÍ TRƯỚC BẠ, THUẾ THU NHẬP CÁ NHÂN": "DMG",
    "ĐƠN ĐỀ NGHỊ SỬ DỤNG ĐẤT KẾT HỢP ĐA MỤC ĐÍCH": "DMD",
    "ĐƠN XÁC NHẬN, GIẤY XÁC NHẬN": "DXN",
    "ĐƠN XIN (ĐỀ NGHỊ) CHUYỂN MỤC ĐÍCH SỬ DỤNG ĐẤT": "DXCMD",
    "ĐƠN XIN (ĐỀ NGHỊ) GIA HẠN SỬ DỤNG ĐẤT": "DGH",
    "ĐƠN XIN (ĐỀ NGHỊ) GIAO ĐẤT, CHO THUÊ ĐẤT": "DXGD",
    "ĐƠN XIN (ĐỀ NGHỊ) TÁCH THỬA ĐẤT, HỢP THỬA ĐẤT": "DXTHT",
    "ĐƠN ĐỀ NGHỊ TÁCH THỪA ĐẤT, HỢP THỪA ĐẤT": "DXTHT",
    "ĐƠN XIN CẤP ĐỔI GIẤY CHỨNG NHẬN": "DXCD",
    "ĐƠN XIN ĐIỀU CHỈNH THỜI HẠN SỬ DỤNG ĐẤT CỦA DỰ ÁN ĐẦU TƯ": "DDCTH",
    "ĐƠN XIN XÁC NHẬN LẠI THỜI HẠN SỬ DỤNG ĐẤT NÔNG NGHIỆP": "DXNTH",
    "GIẤY CHỨNG NHẬN KẾT HÔN": "GKH",
    "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT, QUYỀN SỞ HỮU TÀI SẢN GẮN LIỀN VỚI ĐẤT": "GCNM",  # Can map to both GCNM/GCNC
    "GIẤY ĐỀ NGHỊ XÁC NHẬN CÁC KHOẢN NỘP VÀO NGÂN SÁCH": "GXNNVTC",
    "GIẤY KHAI SINH": "GKS",
    "GIẤY NỘP TIỀN VÀO NGÂN SÁCH NHÀ NƯỚC": "GNT",
    "GIẤY SANG NHƯỢNG ĐẤT": "GSND",
    "GIẤY TỜ LIÊN QUAN (CÁC LOẠI GIẤY TỜ KÈM THEO)": "GTLQ",
    "GIẤY TỜ LIÊN QUAN": "GTLQ",
    "GIẤY TIẾP NHẬN": "GTLQ",
    "GIẤY BIÊN NHẬN": "GTLQ",
    "GIẤY BIÊN NHẬN HỒ SƠ": "GTLQ",
    "PHIẾU KIỂM SOÁT QUÁ TRÌNH GIẢI QUYẾT HỒ SƠ": "GTLQ",
    "BỘ PHẬN TIẾP NHẬN VÀ TRẢ KẾT QUẢ": "GTLQ",
    "BỘ PHẬN TIẾP NHẬN VÀ TRẢ KQ": "GTLQ",
    "PHIẾU TIẾP NHẬN HỒ SƠ": "GTLQ",
    "BIÊN NHẬN HỒ SƠ": "GTLQ",
    "GIẤY ỦY QUYỀN": "GUQ",
    "GIẤY XÁC NHẬN ĐĂNG KÝ LẦN ĐẦU": "GXNDKLD",
    "GIẤY XIN PHÉP XÂY DỰNG": "GPXD",
    "HOÁ ĐƠN GIÁ TRỊ GIA TĂNG": "hoadon",
    "HOÀN THÀNH CÔNG TÁC BỒI THƯỜNG HỖ TRỢ": "HTBTH",
    "HỢP ĐỒNG CHUYỂN NHƯỢNG, TẶNG CHO QUYỀN SỬ DỤNG ĐẤT": "HDCQ",
    "HỢP ĐỒNG TẶNG CHO QUYỀN SỬ DỤNG ĐẤT": "HDCQ",
    "HỢP ĐỒNG MUA BÁN TÀI SẢN BÁN ĐẤU GIÁ": "HDBDG",
    "HỢP ĐỒNG THẾ CHẤP QUYỀN SỬ DỤNG ĐẤT": "HDTHC",
    "HỢP ĐỒNG THI CÔNG": "HDTCO",
    "HỢP ĐỒNG THUÊ ĐẤT, ĐIỀU HỈNH HỢP ĐỒNG THUÊ ĐẤT": "HDTD",
    "HỢP ĐỒNG ỦY QUYỀN": "HDUQ",
    "PHIẾU CHUYỂN THÔNG TIN NGHĨA VỤ TÀI CHÍNH": "PCT",
    "PHIẾU KIỂM TRA HỒ SƠ": "PKTHS",
    "PHIẾU TRÌNH KÝ HỒ SƠ CẤP GIẤY CHỨNG NHẬN": "PKTHS",
    "PHIẾU TRÌNH KÝ HỒ SƠ": "PKTHS",
    "PHIẾU LẤY Ý KIẾN KHU DÂN CƯ": "PLYKDC",
    "PHIẾU XÁC NHẬN KẾT QUẢ ĐO ĐẠC": "PXNKQDD",
    "PHIẾU YÊU CẦU ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT": "DKTC",
    "PHIẾU YÊU CẦU ĐĂNG KÝ THAY ĐỔI NỘI DUNG BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SDĐ, TÀI SẢN GẮN LIỀN VỚI ĐẤT": "DKTD",
    "PHIẾU YÊU CẦU XÓA ĐĂNG KÝ BIỆN PHÁP BẢO ĐẢM BẰNG QUYỀN SỬ DỤNG ĐẤT, TÀI SẢN GẮN LIỀN VỚI ĐẤT": "DKXTC",
    "QUÉT MÃ QR": "QR",
    "QUYẾT ĐỊNH CHO PHÉP CHUYỂN MỤC ĐÍCH": "QDCMD",
    "QUYẾT ĐỊNH CHO PHÉP TÁCH, HỢP THỬA ĐẤT": "QDTT",
    "QUYẾT ĐỊNH CHUYỂN HÌNH THỨC GIAO ĐẤT (CHO THUÊ ĐẤT)": "QDCHTGD",
    "QUYẾT ĐỊNH ĐIỀU CHỈNH QUYẾT ĐỊNH GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH)": "QDDCGD",
    "QUYẾT ĐỊNH ĐIỀU CHỈNH THỜI HẠN SDĐ CỦA DỰ ÁN ĐẦU TƯ": "QDDCTH",
    "QUYẾT ĐỊNH GIA HẠN SỬ DỤNG ĐẤT KHI HẾT THỜI HẠN SDĐ": "QDGH",
    "QUYẾT ĐỊNH GIAO ĐẤT, CHO THUÊ ĐẤT": "QDGTD",
    "QUYẾT ĐỊNH HỦY GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT": "QDHG",
    "QUYẾT ĐỊNH PHÊ DUYỆT PHƯƠNG ÁN BỒI THƯỜNG, HỖ TRỢ, TÁI ĐỊNH CƯ": "QDPDBT",
    "QUYẾT ĐỊNH PHÊ QUYỆT ĐIỀU CHỈNH QUY HOẠCH": "QDDCQH",
    "QUYẾT ĐỊNH PHÊ QUYỆT ĐƠN GIÁ": "QDPDDG",
    "QUYẾT ĐỊNH THI HÀNH ÁN THEO ĐƠN YÊU CẦU": "QDTHA",
    "QUYẾT ĐỊNH THU HỒI ĐẤT": "QDTH",
    "QUYẾT ĐỊNH VỀ HÌNH THỨC SỬ DỤNG ĐẤT": "QDHTSD",
    "QUYẾT ĐỊNH XỬ PHẠT": "QDXP",
    "SƠ ĐỒ DỰ KIẾN TÁCH THỬA": "SDTT",
    "THÔNG BÁO CẬP NHẬT, CHỈNH LÝ BIẾN ĐỘNG": "TBCNBD",
    "THÔNG BÁO CÔNG BỐ CÔNG KHAI DI CHÚC": "CKDC",
    "THÔNG BÁO THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT)": "TBT",
    "THÔNG BÁO VỀ VIỆC CHUYỂN THÔNG TIN GIẤY CHỨNG NHẬN BỊ MẤT ĐỂ NIÊM YẾT CÔNG KHAI": "TBMG",
    "THÔNG BÁO VỀ VIỆC CÔNG KHAI KẾT QUẢ THẨM TRA XÉT DUYỆT HỒ SƠ CẤP GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT": "TBCKCG",
    "THÔNG BÁO VỀ VIỆC NIÊM YẾT CÔNG KHAI MẤT GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT": "TBCKMG",
    "THÔNG BÁO XÁC NHẬN HOÀN THÀNH NGHĨA VỤ TÀI CHÍNH": "HTNVTC",
    "TỜ KHAI THUẾ (TRƯỚC BẠ, THUẾ TNCN, TIỀN SỬ DỤNG ĐẤT)": "TKT",
    "TỜ TRÌNH VỀ GIAO ĐẤT (CHO THUÊ ĐẤT, CHO PHÉP CHUYỂN MỤC ĐÍCH)": "TTr",
    "TỜ TRÌNH VỀ VIỆC ĐĂNG KÝ ĐẤT ĐAI, TÀI SẢN GẮN LIỀN VỚI ĐẤT (UBND XÃ)": "TTCG",
    "VĂN BẢN CAM KẾT TÀI SẢN RIÊNG": "CKTSR",
    "VĂN BẢN CHẤP THUẬN CHO PHÉP CHUYỂN MỤC ĐÍCH": "VBCTCMD",
    "VĂN BẢN ĐỀ NGHỊ CHẤP THUẬN NHẬN CHUYỂN NHƯỢNG, THUÊ, GÓP VỐN QUYỀN SDĐ": "VBDNCT",
    "VĂN BẢN ĐỀ NGHỊ THẨM ĐỊNH, PHÊ DUYỆT PHƯƠNG ÁN SDĐ": "PDPASDD",
    "VĂN BẢN THỎA THUẬN PHÂN CHIA DI SẢN THỪA KẾ": "VBTK",
    "VĂN BẢN THỎA THUẬN QUYỀN SỬ DỤNG ĐẤT CỦA HỘ GIA ĐÌNH": "TTHGD",
    "THỎA THUẬN QUYỀN SỬ DỤNG ĐẤT CỦA HỘ GIA ĐÌNH": "TTHGD",
    "VĂN BẢN THỎA THUẬN QUYỀN QSDĐ CỦA HỘ GIA ĐÌNH": "TTHGD",
    "THỎA THUẬN QUYỀN QSDĐ HỘ GIA ĐÌNH": "TTHGD",
    "THỎA THUẬN SỬ DỤNG ĐẤT HỘ GIA ĐÌNH": "TTHGD",
    "VĂN BẢN THOẢ THUẬN VỀ VIỆC CHẤM DỨT QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ": "CDLK",
    "VĂN BẢN THỎA THUẬN VỀ VIỆC XÁC LẬP QUYỀN HẠN CHẾ ĐỐI VỚI THỬA ĐẤT LIỀN KỀ": "HCLK",
    "VĂN BẢN TỪ CHỐI NHẬN DI SẢN THỪA KẾ": "VBTC",
    "VĂN BẢN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG": "PCTSVC",
    "PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG": "PCTSVC",
    "VĂN BẢN PHÂN CHIA TÀI SẢN CHUNG": "PCTSVC",
    "THỎA THUẬN PHÂN CHIA TÀI SẢN CHUNG VỢ CHỒNG": "PCTSVC",
    "VĂN BẢN THỎA THUẬN PHÂN CHIA TÀI SẢN VỢ CHỒNG": "PCTSVC",
    "PHÂN CHIA TÀI SẢN VỢ CHỒNG": "PCTSVC",
    "VĂN BẢN ĐỀ NGHỊ ĐĂNG KÝ TÀI SẢN CHUNG VỢ CHỒNG": "PCTSVC",
}

# Title templates for fuzzy matching (các mẫu title chuẩn)
TITLE_TEMPLATES = {
    "GCN": [
        "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT",
        "GIẤY CHỨNG NHẬN",
        "GIAY CHUNG NHAN QUYEN SU DUNG DAT"
    ],
    "GCNM": [
        "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT QUYỀN SỞ HỮU NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT",
        "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT",
        "GIẤY CHỨNG NHẬN",
        "GIAY CHUNG NHAN QUYEN SU DUNG DAT"
    ],
    "HDCQ": [
        "HỢP ĐỒNG CHUYỂN NHƯỢNG QUYỀN SỬ DỤNG ĐẤT",
        "HỢP ĐỒNG CHUYỂN NHƯỢNG",
        "HOP DONG CHUYEN NHUONG QUYEN SU DUNG DAT",
        "HOP DONG CHUYEN NHUONG"
    ],
    "GUQ": [
        "GIẤY UỶ QUYỀN",
        "GIẤY ỦY QUYỀN",
        "GIAY UY QUYEN"
    ],
    "HDUQ": [
        "HỢP ĐỒNG ỦY QUYỀN",
        "HỢP ĐỒNG UỶ QUYỀN",
        "HỢP ĐỎNG ỦY QUYỀN",
        "HỢP ĐỎNG UỶ QUYỀN",
        "HOP DONG UY QUYEN"
    ],
    "DDKBD": [
        "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG ĐẤT ĐAI TÀI SẢN GẮN LIỀN VỚI ĐẤT",
        "ĐƠN ĐĂNG KÝ BIẾN ĐỘNG",
        "DON DANG KY BIEN DONG"
    ],
    "BMT": [
        "BẢN ĐỒ ĐỊA CHÍNH",
        "BẢN ĐỒ THỬA ĐẤT",
        "BẢN ĐỒ",
        "BAN DO DIA CHINH"
    ],
    "CCCD": [
        "CĂN CƯỚC CÔNG DÂN",
        "CAN CUOC CONG DAN"
    ],
    "CMND": [
        "CHỨNG MINH NHÂN DÂN",
        "CHUNG MINH NHAN DAN"
    ],
    "HDBDG": [
        "HỢP ĐỒNG MUA BÁN",
        "HOP DONG MUA BAN"
    ],
    "GCNC": [
        "GIẤY CHỨNG NHẬN BẢN CHÍNH",
        "GIAY CHUNG NHAN BAN CHINH"
    ],
    # NEW: GTLQ = Giấy tiếp nhận hồ sơ và hẹn trả kết quả (bao gồm Biên nhận hồ sơ)
    "GTLQ": [
        "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
        "GIAY TIEP NHAN HO SO VA HEN TRA KET QUA",
        "GIẤY TIẾP NHẬN HỒ SƠ",
        "TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
        "GIẤY TIẾP NHẬN HỒ SƠ VÀ TRẢ KẾT QUẢ",
        # Biên nhận variants (merged from BNHS)
        "BIÊN NHẬN HỒ SƠ",
        "BIEN NHAN HO SO",
        "PHIẾU BIÊN NHẬN",
        "PHIEU BIEN NHAN"
    ],
}

# NEW: Document type configuration with required title keywords
DOCUMENT_TYPE_CONFIG = {
    "GCN": {
        "required_in_title": ["giấy chứng nhận", "GIẤY CHỨNG NHẬN", "giay chung nhan", "chứng nhận"],
        "weight": 1.6
    },
    "GCNM": {
        "required_in_title": ["giấy chứng nhận", "GIẤY CHỨNG NHẬN", "giay chung nhan", "chứng nhận"],
        "weight": 1.5
    },
    "GCNC": {
        "required_in_title": ["giấy chứng nhận", "GIẤY CHỨNG NHẬN", "bản chính", "BẢN CHÍNH"],
        "weight": 1.4
    },
    "HDCQ": {
        "required_in_title": ["hợp đồng", "HỢP ĐỒNG", "HỢP ĐỎNG", "hop dong"],
        "weight": 1.6
    },
    "HDBDG": {
        "required_in_title": ["hợp đồng", "HỢP ĐỒNG", "hop dong", "mua bán"],
        "weight": 1.5
    },
    "HDUQ": {
        "required_in_title": ["hợp đồng", "HỢP ĐỒNG", "ủy quyền"],
        "weight": 1.5
    },
    "GUQ": {
        "required_in_title": ["giấy ủy quyền", "GIẤY ỦY QUYỀN", "giay uy quyen", "ủy quyền"],
        "weight": 1.7
    },
    "DDKBD": {
        "required_in_title": ["đơn đăng ký", "ĐƠN ĐĂNG KÝ", "don dang ky", "đăng ký biến động", "biến động"],
        "weight": 1.2
    },
    "BMT": {
        "required_in_title": ["bản đồ", "BẢN ĐỒ", "ban do", "bản vẽ", "bản vẽ"],
        "weight": 1.1
    },
    "CCCD": {
        "required_in_title": ["căn cước", "CĂN CƯỚC", "can cuoc", "căn cước công dân"],
        "weight": 1.0
    },
    "CMND": {
        "required_in_title": ["chứng minh", "CHỨNG MINH", "chung minh", "chứng minh nhân dân"],
        "weight": 1.0
    },
    # NEW
    "GTLQ": {
        "required_in_title": [
            "tiếp nhận", "hồ sơ", "hẹn trả",
            "tiep nhan", "ho so", "hen tra"
        ],
        "weight": 1.2
    },
}

# COMPLETE Document type rules - 96 types (added GCN)
DOCUMENT_RULES = {
    "GCN": {
        "keywords": [
            # Generic GCN - will be classified to GCNC/GCNM after batch
            "giấy chứng nhận quyền sử dụng đất", "giấy chứng nhận", "giầy chứng nhận",
            "quyền sử dụng đất", "cộng hòa xã hội chủ nghĩa việt nam",
            # Không dấu
            "giay chung nhan quyen su dung dat", "giay chung nhan",
            "quyen su dung dat", "cong hoa xa hoi chu nghia viet nam"
        ],
        "min_keywords": 2,
        "confidence_boost": 0.05
    },
    "GCNM": {
        "keywords": [
            # Có dấu
            "giấy chứng nhận quyền sử dụng đất", "giấy chứng nhận", "giầy chứng nhận",
            "quyền sử dụng đất", "quyền sở hữu", "tài sản gắn liền",
            "cộng hòa xã hội chủ nghĩa việt nam", "độc lập tự do hạnh phúc",
            "chi nhánh văn phòng đăng ký", "văn phòng đăng ký đất đai",
            "chứng nhan", "chứng nhận",
            # GCN continuation page (trang 2)
            "nội dung thay đổi và cơ sở pháp lý",
            "xác nhận của cơ quan có thẩm quyền",
            "xác nhận của cơ quan",
            "thửa đất, nhà ở và tài sản khác",
            # Không dấu
            "giay chung nhan", "quyen su dung dat", "quyen so huu",
            "tai san gan lien", "cong hoa xa hoi chu nghia viet nam",
            "doc lap tu do hanh phuc", "van phong dang ky dat dai",
            "chung nhan",
            "noi dung thay doi va co so phap ly",
            "xac nhan cua co quan co tham quyen",
            "xac nhan cua co quan",
            "thua dat nha o va tai san khac",
            # Viết hoa (auto-generated)
            "GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT",
            "GIẤY CHỨNG NHẬN",
            "GIẦY CHỨNG NHẬN",
            "QUYỀN SỬ DỤNG ĐẤT",
            "QUYỀN SỞ HỮU",
            "TÀI SẢN GẮN LIỀN",
            "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
            "ĐỘC LẬP TỰ DO HẠNH PHÚC",
            "CHI NHÁNH VĂN PHÒNG ĐĂNG KÝ",
            "VĂN PHÒNG ĐĂNG KÝ ĐẤT ĐAI",
            "NỘI DUNG THAY ĐỔI VÀ CƠ SỞ PHÁP LÝ",
            "XÁC NHẬN CỦA CƠ QUAN CÓ THẨM QUYỀN",
            "XÁC NHẬN CỦA CƠ QUAN",
            "THỬA ĐẤT, NHÀ Ở VÀ TÀI SẢN KHÁC"
        ],
        "weight": 1.5, "min_matches": 1
    },
    "GCNC": {
        "keywords": [
            # Có dấu
            "giấy chứng nhận quyền sử dụng đất", "giấy chứng nhận", "giầy chứng nhận",
            "bản chính", "gcn bản chính", "chứng nhận",
            # Không dấu
            "giay chung nhan", "ban chinh", "gcn ban chinh", "chung nhan",
            # Viết hoa
            "GIAY CHUNG NHAN", "BAN CHINH", "CHUNG NHAN"
        ],
        "weight": 1.4, "min_matches": 1
    },
    "BMT": {
        "keywords": [
            # Có dấu
            "bản mô tả ranh giới", "mốc giới thửa đất", "vị trí ranh giới",
            "mô tả ranh giới", "ranh giới thửa", "mốc giới", "ranh giới",
            "phía đông giáp", "phía tây giáp", "phía nam giáp", "phía bắc giáp",
            # Không dấu
            "ban mo ta ranh gioi", "moc gioi thua dat", "vi tri ranh gioi",
            "mo ta ranh gioi", "ranh gioi thua", "moc gioi", "ranh gioi",
            "phia dong giap", "phia tay giap", "phia nam giap", "phia bac giap",
            # Viết hoa
            "BAN MO TA", "RANH GIOI", "MOC GIOI"
        ],
        "weight": 1.1, "min_matches": 2
    },
    "HSKT": {
        "keywords": [
            # Có dấu
            "bản vẽ", "trích lục", "đo tách", "chỉnh lý", "hồ sơ kỹ thuật",
            "trích đo", "tỷ lệ 1:", "phiếu đo đạc", "đo đạc chỉnh lý",
            "hồ sơ kỹ thuật", "kỹ thuật",
            # Không dấu
            "ban ve", "trich luc", "do tach", "chinh ly", "ho so ky thuat",
            "trich do", "ty le 1:", "phieu do dac", "do dac chinh ly", "ky thuat",
            # Viết hoa
            "BAN VE", "TRICH LUC", "HO SO KY THUAT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BVHC": {
        "keywords": [
            # Có dấu
            "bản vẽ hoàn công", "hoàn công", "công trình xây dựng",
            "bản vẽ thi công", "hoàn thành thi công",
            # Không dấu
            "ban ve hoan cong", "hoan cong", "cong trinh xay dung",
            "ban ve thi cong", "hoan thanh thi cong",
            # Viết hoa (auto-generated)
            "BẢN VẼ HOÀN CÔNG",
            "HOÀN CÔNG",
            "CÔNG TRÌNH XÂY DỰNG",
            "BẢN VẼ THI CÔNG",
            "HOÀN THÀNH THI CÔNG"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BVN": {
        "keywords": [
            # Có dấu
            "bản vẽ nhà", "mặt bằng nhà", "thiết kế nhà", "kiến trúc nhà",
            "mặt bằng", "mặt tiền", "mặt cắt",
            # Không dấu
            "ban ve nha", "mat bang nha", "thiet ke nha", "kien truc nha",
            "mat bang", "mat tien", "mat cat",
            # Viết hoa (auto-generated)
            "BẢN VẼ NHÀ",
            "MẶT BẰNG NHÀ",
            "THIẾT KẾ NHÀ",
            "KIẾN TRÚC NHÀ",
            "MẶT BẰNG",
            "MẶT TIỀN",
            "MẶT CẮT"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "BKKDT": {
        "keywords": [
            # Có dấu
            "bảng kê khai diện tích", "diện tích đang sử dụng",
            "kê khai đất đai", "kê khai diện tích",
            # Không dấu
            "bang ke khai dien tich", "dien tich dang su dung",
            "ke khai dat dai", "ke khai dien tich",
            # Viết hoa (auto-generated)
            "BẢNG KÊ KHAI DIỆN TÍCH",
            "DIỆN TÍCH ĐANG SỬ DỤNG",
            "KÊ KHAI ĐẤT ĐAI",
            "KÊ KHAI DIỆN TÍCH"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DSCG": {
        "keywords": [
            # Có dấu
            "danh sách", "cấp giấy", "thửa đất cấp giấy",
            "liệt kê", "bảng liệt kê",
            # Không dấu
            "danh sach", "cap giay", "thua dat cap giay",
            "liet ke", "bang liet ke",
            # Viết hoa (auto-generated)
            "DANH SÁCH",
            "CẤP GIẤY",
            "THỬA ĐẤT CẤP GIẤY",
            "LIỆT KÊ",
            "BẢNG LIỆT KÊ"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "BBBDG": {
        "keywords": [
            # Có dấu
            "biên bản bán đấu giá", "đấu giá tài sản", "bán đấu giá",
            "hội đồng đấu giá", "trúng đấu giá",
            # Không dấu
            "bien ban ban dau gia", "dau gia tai san", "ban dau gia",
            "hoi dong dau gia", "trung dau gia",
            # Viết hoa (auto-generated)
            "BIÊN BẢN BÁN ĐẤU GIÁ",
            "ĐẤU GIÁ TÀI SẢN",
            "BÁN ĐẤU GIÁ",
            "HỘI ĐỒNG ĐẤU GIÁ",
            "TRÚNG ĐẤU GIÁ"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBGD": {
        "keywords": [
            # Có dấu
            "biên bản bàn giao", "bàn giao đất", "thực địa",
            "bàn giao thực địa", "giao nhận",
            # Không dấu
            "bien ban ban giao", "ban giao dat", "thuc dia",
            "ban giao thuc dia", "giao nhan",
            # Viết hoa (auto-generated)
            "BIÊN BẢN BÀN GIAO",
            "BÀN GIAO ĐẤT",
            "THỰC ĐỊA",
            "BÀN GIAO THỰC ĐỊA",
            "GIAO NHẬN"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBHDDK": {
        "keywords": [
            # Có dấu
            "hội đồng đăng ký", "đăng ký đất đai lần đầu",
            "biên bản hội đồng", "đăng ký lần đầu",
            # Không dấu
            "hoi dong dang ky", "dang ky dat dai lan dau",
            "bien ban hoi dong", "dang ky lan dau",
            # Viết hoa (auto-generated)
            "HỘI ĐỒNG ĐĂNG KÝ",
            "ĐĂNG KÝ ĐẤT ĐAI LẦN ĐẦU",
            "BIÊN BẢN HỘI ĐỒNG",
            "ĐĂNG KÝ LẦN ĐẦU"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBNT": {
        "keywords": [
            # Có dấu
            "biên bản nghiệm thu", "nghiệm thu công trình",
            "kiểm tra nghiệm thu", "hội đồng nghiệm thu",
            # Không dấu
            "bien ban nghiem thu", "nghiem thu cong trinh",
            "kiem tra nghiem thu", "hoi dong nghiem thu",
            # Viết hoa (auto-generated)
            "BIÊN BẢN NGHIỆM THU",
            "NGHIỆM THU CÔNG TRÌNH",
            "KIỂM TRA NGHIỆM THU",
            "HỘI ĐỒNG NGHIỆM THU"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBKTSS": {
        "keywords": [
            # Có dấu
            "kiểm tra sai sót", "sai sót trên giấy chứng nhận",
            "biên bản kiểm tra", "chỉnh sửa thông tin",
            # Không dấu
            "kiem tra sai sot", "sai sot tren giay chung nhan",
            "bien ban kiem tra", "chinh sua thong tin",
            # Viết hoa (auto-generated)
            "KIỂM TRA SAI SÓT",
            "SAI SÓT TRÊN GIẤY CHỨNG NHẬN",
            "BIÊN BẢN KIỂM TRA",
            "CHỈNH SỬA THÔNG TIN"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBKTHT": {
        "keywords": [
            # Có dấu
            "xác minh hiện trạng", "kiểm tra hiện trạng",
            "sử dụng đất hiện trạng", "kiểm tra thực địa",
            # Không dấu
            "xac minh hien trang", "kiem tra hien trang",
            "su dung dat hien trang", "kiem tra thuc dia",
            # Viết hoa (auto-generated)
            "XÁC MINH HIỆN TRẠNG",
            "KIỂM TRA HIỆN TRẠNG",
            "SỬ DỤNG ĐẤT HIỆN TRẠNG",
            "KIỂM TRA THỰC ĐỊA"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBKTDC": {
        "keywords": [
            # Có dấu
            "kết thúc công khai", "công bố di chúc", "biên bản di chúc",
            # Không dấu
            "ket thuc cong khai", "cong bo di chuc", "bien ban di chuc",
            # Viết hoa (auto-generated)
            "KẾT THÚC CÔNG KHAI",
            "CÔNG BỐ DI CHÚC",
            "BIÊN BẢN DI CHÚC"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "KTCKCG": {
        "keywords": [
            # Có dấu
            "kết thúc thông báo", "niêm yết công khai", "kiểm tra hồ sơ",
            "kết quả kiểm tra", "cấp gcn",
            # Không dấu
            "ket thuc thong bao", "niem yet cong khai", "kiem tra ho so",
            "ket qua kiem tra", "cap gcn",
            # Viết hoa (auto-generated)
            "KẾT THÚC THÔNG BÁO",
            "NIÊM YẾT CÔNG KHAI",
            "KIỂM TRA HỒ SƠ",
            "KẾT QUẢ KIỂM TRA",
            "CẤP GCN"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "KTCKMG": {
        "keywords": [
            # Có dấu
            "kết thúc thông báo", "niêm yết công khai", "mất gcn",
            "mất giấy chứng nhận",
            # Không dấu
            "ket thuc thong bao", "niem yet cong khai", "mat gcn",
            "mat giay chung nhan",
            # Viết hoa (auto-generated)
            "KẾT THÚC THÔNG BÁO",
            "NIÊM YẾT CÔNG KHAI",
            "MẤT GCN",
            "MẤT GIẤY CHỨNG NHẬN"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "BLTT": {
        "keywords": [
            # Có dấu
            "biên lai thu thuế", "thuế sử dụng đất", "phi nông nghiệp",
            "biên lai nộp thuế",
            # Không dấu
            "bien lai thu thue", "thue su dung dat", "phi nong nghiep",
            "bien lai nop thue",
            # Viết hoa (auto-generated)
            "BIÊN LAI THU THUẾ",
            "THUẾ SỬ DỤNG ĐẤT",
            "PHI NÔNG NGHIỆP",
            "BIÊN LAI NỘP THUẾ"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "CCCD": {
        "keywords": [
            # Có dấu - phải có keyword chính xác
            "căn cước công dân", "cccd", "thẻ căn cước", "căn cước",
            "số căn cước", "thẻ cccd",
            # Không dấu
            "can cuoc cong dan", "the can cuoc", "can cuoc",
            "so can cuoc", "the cccd",
            # Viết hoa
            "CAN CUOC CONG DAN", "CCCD", "THE CAN CUOC",
            "SO CAN CUOC"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "DS15": {
        "keywords": [
            # Có dấu
            "danh sách chủ sử dụng", "các thửa đất", "mẫu 15",
            # Không dấu
            "danh sach chu su dung", "cac thua dat", "mau 15",
            # Viết hoa (auto-generated)
            "DANH SÁCH CHỦ SỬ DỤNG",
            "CÁC THỬA ĐẤT",
            "MẪU 15"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DSCK": {
        "keywords": [
            # Có dấu
            "danh sách công khai", "hồ sơ cấp giấy", "cnqsdđ",
            # Không dấu
            "danh sach cong khai", "ho so cap giay", "cnqsdd",
            # Viết hoa (auto-generated)
            "DANH SÁCH CÔNG KHAI",
            "HỒ SƠ CẤP GIẤY",
            "CNQSDĐ"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DICHUC": {
        "keywords": [
            # Có dấu
            "di chúc", "lập di chúc", "người lập di chúc",
            # Không dấu
            "di chuc", "lap di chuc", "nguoi lap di chuc",
            # Viết hoa (auto-generated)
            "DI CHÚC",
            "LẬP DI CHÚC",
            "NGƯỜI LẬP DI CHÚC"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "DCK": {
        "keywords": [
            # Có dấu
            "đơn cam kết", "giấy cam kết", "cam kết",
            # Không dấu
            "don cam ket", "giay cam ket", "cam ket",
            # Viết hoa (auto-generated)
            "ĐƠN CAM KẾT",
            "GIẤY CAM KẾT",
            "CAM KẾT"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "DDKBD": {
        "keywords": [
            # Có dấu
            "đơn đăng ký biến động", "biến động đất đai",
            "tài sản gắn liền", "đăng ký biến động",
            "đơn đăng ký biến động đất đai",
            # Trang 2 DDKBD (KHÔNG phải GCNM)
            "xác nhận của ủy ban nhân dân",
            "xác nhận của ubnd",
            "ủy ban nhân dân cấp xã",
            "ủy ban nhân dân",
            # Không dấu (OCR thường bỏ dấu)
            "don dang ky bien dong", "bien dong dat dai",
            "tai san gan lien", "dang ky bien dong",
            "don dang ky bien dong dat dai",
            "xac nhan cua uy ban nhan dan",
            "xac nhan cua ubnd",
            "uy ban nhan dan cap xa",
            "uy ban nhan dan",
            # OCR common typos
            "dang ky bien dong", "bien dong",
            "đăng ký biến động đất",
            # Viết hoa (OCR thường đọc title là chữ hoa)
            "DON DANG KY BIEN DONG", "BIEN DONG DAT DAI",
            "DANG KY BIEN DONG",
            "XÁC NHẬN CỦA ỦY BAN NHÂN DÂN",
            "XÁC NHẬN CỦA UBND",
            "ỦY BAN NHÂN DÂN CẤP XÃ",
            "ỦY BAN NHÂN DÂN"
        ],
        "weight": 1.2,
        "min_matches": 1
    },
    "DDK": {
        "keywords": [
            # Có dấu
            "đơn đăng ký đất đai", "đăng ký đất đai",
            "tài sản gắn liền với đất",
            # Không dấu
            "don dang ky dat dai", "dang ky dat dai",
            "tai san gan lien voi dat",
            # Viết hoa (auto-generated)
            "ĐƠN ĐĂNG KÝ ĐẤT ĐAI",
            "ĐĂNG KÝ ĐẤT ĐAI",
            "TÀI SẢN GẮN LIỀN VỚI ĐẤT"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "CHTGD": {
        "keywords": [
            # Có dấu
            "đề nghị chuyển hình thức", "giao đất", "cho thuê đất",
            "chuyển hình thức giao đất",
            # Không dấu
            "de nghi chuyen hinh thuc", "giao dat", "cho thue dat",
            "chuyen hinh thuc giao dat",
            # Viết hoa (auto-generated)
            "ĐỀ NGHỊ CHUYỂN HÌNH THỨC",
            "GIAO ĐẤT",
            "CHO THUÊ ĐẤT",
            "CHUYỂN HÌNH THỨC GIAO ĐẤT"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DCQDGD": {
        "keywords": [
            # Có dấu
            "đề nghị điều chỉnh", "quyết định giao đất",
            "cho thuê đất", "chuyển mục đích",
            # Không dấu
            "de nghi dieu chinh", "quyet dinh giao dat",
            "cho thue dat", "chuyen muc dich",
            # Viết hoa (auto-generated)
            "ĐỀ NGHỊ ĐIỀU CHỈNH",
            "QUYẾT ĐỊNH GIAO ĐẤT",
            "CHO THUÊ ĐẤT",
            "CHUYỂN MỤC ĐÍCH"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DMG": {
        "keywords": [
            # Có dấu
            "đề nghị miễn giảm", "lệ phí trước bạ",
            "thuế thu nhập cá nhân", "miễn giảm thuế",
            # Không dấu
            "de nghi mien giam", "le phi truoc ba",
            "thue thu nhap ca nhan", "mien giam thue",
            # Viết hoa (auto-generated)
            "ĐỀ NGHỊ MIỄN GIẢM",
            "LỆ PHÍ TRƯỚC BẠ",
            "THUẾ THU NHẬP CÁ NHÂN",
            "MIỄN GIẢM THUẾ"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DMD": {
        "keywords": [
            # Có dấu
            "đề nghị sử dụng đất", "kết hợp đa mục đích",
            "đất đa mục đích",
            # Không dấu
            "de nghi su dung dat", "ket hop da muc dich",
            "dat da muc dich",
            # Viết hoa (auto-generated)
            "ĐỀ NGHỊ SỬ DỤNG ĐẤT",
            "KẾT HỢP ĐA MỤC ĐÍCH",
            "ĐẤT ĐA MỤC ĐÍCH"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DXN": {
        "keywords": [
            # Có dấu
            "đơn xác nhận", "giấy xác nhận", "xác nhận",
            # Không dấu
            "don xac nhan", "giay xac nhan", "xac nhan",
            # Viết hoa (auto-generated)
            "ĐƠN XÁC NHẬN",
            "GIẤY XÁC NHẬN",
            "XÁC NHẬN"
        ],
        "weight": 0.7, "min_matches": 1
    },
    "DXCMD": {
        "keywords": [
            # Có dấu
            "đơn xin chuyển mục đích", "đề nghị chuyển mục đích",
            "chuyển mục đích sử dụng đất",
            # Không dấu
            "don xin chuyen muc dich", "de nghi chuyen muc dich",
            "chuyen muc dich su dung dat",
            # Viết hoa (auto-generated)
            "ĐƠN XIN CHUYỂN MỤC ĐÍCH",
            "ĐỀ NGHỊ CHUYỂN MỤC ĐÍCH",
            "CHUYỂN MỤC ĐÍCH SỬ DỤNG ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DGH": {
        "keywords": [
            # Có dấu
            "đơn xin gia hạn", "gia hạn sử dụng đất",
            "đề nghị gia hạn",
            # Không dấu
            "don xin gia han", "gia han su dung dat",
            "de nghi gia han",
            # Viết hoa (auto-generated)
            "ĐƠN XIN GIA HẠN",
            "GIA HẠN SỬ DỤNG ĐẤT",
            "ĐỀ NGHỊ GIA HẠN"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DXGD": {
        "keywords": [
            # Có dấu
            "đơn xin giao đất", "đề nghị giao đất",
            "đơn xin cho thuê đất",
            # Không dấu
            "don xin giao dat", "de nghi giao dat",
            "don xin cho thue dat",
            # Viết hoa (auto-generated)
            "ĐƠN XIN GIAO ĐẤT",
            "ĐỀ NGHỊ GIAO ĐẤT",
            "ĐƠN XIN CHO THUÊ ĐẤT"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DXTHT": {
        "keywords": [
            # Có dấu
            "đơn xin tách thửa", "đơn xin hợp thửa",
            "tách thửa đất", "hợp thửa đất",
            # Không dấu
            "don xin tach thua", "don xin hop thua",
            "tach thua dat", "hop thua dat",
            # Viết hoa (auto-generated)
            "ĐƠN XIN TÁCH THỬA",
            "ĐƠN XIN HỢP THỬA",
            "TÁCH THỬA ĐẤT",
            "HỢP THỬA ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DXCD": {
        "keywords": [
            # Có dấu
            "đơn xin cấp đổi", "cấp đổi giấy chứng nhận",
            "đổi gcn",
            # Không dấu
            "don xin cap doi", "cap doi giay chung nhan",
            "doi gcn",
            # Viết hoa (auto-generated)
            "ĐƠN XIN CẤP ĐỔI",
            "CẤP ĐỔI GIẤY CHỨNG NHẬN",
            "ĐỔI GCN"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "DDCTH": {
        "keywords": [
            # Có dấu
            "đơn xin điều chỉnh", "thời hạn sử dụng đất",
            "dự án đầu tư", "điều chỉnh thời hạn",
            # Không dấu
            "don xin dieu chinh", "thoi han su dung dat",
            "du an dau tu", "dieu chinh thoi han",
            # Viết hoa (auto-generated)
            "ĐƠN XIN ĐIỀU CHỈNH",
            "THỜI HẠN SỬ DỤNG ĐẤT",
            "DỰ ÁN ĐẦU TƯ",
            "ĐIỀU CHỈNH THỜI HẠN"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DXNTH": {
        "keywords": [
            # Có dấu
            "đơn xin xác nhận", "thời hạn sử dụng đất",
            "đất nông nghiệp", "xác nhận lại thời hạn",
            # Không dấu
            "don xin xac nhan", "thoi han su dung dat",
            "dat nong nghiep", "xac nhan lai thoi han",
            # Viết hoa (auto-generated)
            "ĐƠN XIN XÁC NHẬN",
            "THỜI HẠN SỬ DỤNG ĐẤT",
            "ĐẤT NÔNG NGHIỆP",
            "XÁC NHẬN LẠI THỜI HẠN"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "GKH": {
        "keywords": [
            # Có dấu
            "giấy chứng nhận kết hôn", "kết hôn", "hôn nhân",
            # Không dấu
            "giay chung nhan ket hon", "ket hon", "hon nhan",
            # Viết hoa (auto-generated)
            "GIẤY CHỨNG NHẬN KẾT HÔN",
            "KẾT HÔN",
            "HÔN NHÂN"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "GXNNVTC": {
        "keywords": [
            # Có dấu
            "giấy đề nghị xác nhận", "nộp vào ngân sách",
            "các khoản nộp", "xác nhận nộp thuế",
            # Không dấu
            "giay de nghi xac nhan", "nop vao ngan sach",
            "cac khoan nop", "xac nhan nop thue",
            # Viết hoa (auto-generated)
            "GIẤY ĐỀ NGHỊ XÁC NHẬN",
            "NỘP VÀO NGÂN SÁCH",
            "CÁC KHOẢN NỘP",
            "XÁC NHẬN NỘP THUẾ"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "GKS": {
        "keywords": [
            # Có dấu
            "giấy khai sinh", "khai sinh", "gks",
            # Không dấu
            "giay khai sinh", "khai sinh",
            # Viết hoa (auto-generated)
            "GIẤY KHAI SINH"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "GNT": {
        "keywords": [
            # Có dấu
            "giấy nộp tiền", "nộp vào ngân sách", "ngân sách nhà nước",
            # Không dấu
            "giay nop tien", "nop vao ngan sach", "ngan sach nha nuoc",
            # Viết hoa (auto-generated)
            "GIẤY NỘP TIỀN",
            "NỘP VÀO NGÂN SÁCH",
            "NGÂN SÁCH NHÀ NƯỚC"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GSND": {
        "keywords": [
            # Có dấu
            "giấy sang nhượng đất", "sang nhượng", "chuyển nhượng đất",
            # Không dấu
            "giay sang nhuong dat", "sang nhuong", "chuyen nhuong dat",
            # Viết hoa (auto-generated)
            "GIẤY SANG NHƯỢNG ĐẤT",
            "SANG NHƯỢNG",
            "CHUYỂN NHƯỢNG ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GTLQ": {
        "keywords": [
            # Có dấu (GTLQ: Giấy tiếp nhận hồ sơ và hẹn trả kết quả, bao gồm cả Biên nhận hồ sơ)
            "giấy tiếp nhận hồ sơ", "hẹn trả kết quả", "mã hồ sơ",
            "bộ phận tiếp nhận và trả kết quả", "trung tâm phục vụ hành chính công",
            "thành phần hồ sơ", "tiếp nhận hồ sơ",
            "giấy tiếp nhận hồ sơ và trả kết quả",
            "giấy tiếp nhận hồ sơ và hẹn trả kết quả",
            # Từ BNHS (merged)
            "biên nhận hồ sơ", "biên nhận", "đã nhận hồ sơ",
            "phiếu biên nhận", "nhận hồ sơ từ",
            # Không dấu
            "giay tiep nhan ho so", "hen tra ket qua", "ma ho so",
            "bo phan tiep nhan va tra ket qua", "trung tam phuc vu hanh chinh cong",
            "thanh phan ho so", "tiep nhan ho so",
            "giay tiep nhan ho so va tra ket qua",
            "giay tiep nhan ho so va hen tra ket qua",
            # Từ BNHS (merged)
            "bien nhan ho so", "bien nhan", "da nhan ho so",
            "phieu bien nhan", "nhan ho so tu",
            # Viết hoa
            "GIẤY TIẾP NHẬN HỒ SƠ", "HẸN TRẢ KẾT QUẢ",
            "BỘ PHẬN TIẾP NHẬN VÀ TRẢ KẾT QUẢ", "TRUNG TÂM PHỤC VỤ HÀNH CHÍNH CÔNG",
            "THÀNH PHẦN HỒ SƠ",
            "GIẤY TIẾP NHẬN HỒ SƠ VÀ TRẢ KẾT QUẢ",
            "GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ",
            # Từ BNHS (merged)
            "BIÊN NHẬN HỒ SƠ", "BIÊN NHẬN", "ĐÃ NHẬN HỒ SƠ",
            "PHIẾU BIÊN NHẬN", "NHẬN HỒ SƠ"
        ],
        "weight": 1.2, "min_matches": 2
    },
    "GUQ": {
        "keywords": [
            # Có dấu
            "giấy ủy quyền", "ủy quyền", "người được ủy quyền",
            "tôi tên là", "tôi là", "được ủy quyền",
            # Không dấu
            "giay uy quyen", "uy quyen", "nguoi duoc uy quyen",
            "toi ten la", "toi la", "duoc uy quyen",
            # Viết hoa (auto-generated)
            "GIẤY ỦY QUYỀN",
            "ỦY QUYỀN",
            "NGƯỜI ĐƯỢC ỦY QUYỀN",
            "TÔI TÊN LÀ", "TÔI LÀ", "ĐƯỢC ỦY QUYỀN",
            # OCR typos
            "GIẤY UY QUYỀN", "GIẤY ỦY QUYEN",
            "UY QUYEN", "UY QUYỀN", "Ủ'Y QUYỀN"
        ],
        "weight": 1.7,
        "min_matches": 1
    },
    "GXNDKLD": {
        "keywords": [
            # Có dấu
            "giấy xác nhận đăng ký lần đầu", "đăng ký lần đầu",
            "xác nhận đăng ký",
            # Không dấu
            "giay xac nhan dang ky lan dau", "dang ky lan dau",
            "xac nhan dang ky",
            # Viết hoa (auto-generated)
            "GIẤY XÁC NHẬN ĐĂNG KÝ LẦN ĐẦU",
            "ĐĂNG KÝ LẦN ĐẦU",
            "XÁC NHẬN ĐĂNG KÝ"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GPXD": {
        "keywords": [
            # Có dấu
            "giấy phép xây dựng", "phép xây dựng", "giấy phép",
            # Không dấu
            "giay phep xay dung", "phep xay dung", "giay phep",
            # Viết hoa (auto-generated)
            "GIẤY PHÉP XÂY DỰNG",
            "PHÉP XÂY DỰNG",
            "GIẤY PHÉP"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "hoadon": {
        "keywords": [
            # Có dấu
            "hoá đơn", "hóa đơn", "gtgt", "giá trị gia tăng",
            # Không dấu
            "hoa don", "gia tri gia tang",
            # Viết hoa (auto-generated)
            "HOÁ ĐƠN",
            "HÓA ĐƠN",
            "GIÁ TRỊ GIA TĂNG"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HTBTH": {
        "keywords": [
            # Có dấu
            "hoàn thành", "bồi thường hỗ trợ", "công tác bồi thường",
            # Không dấu
            "hoan thanh", "boi thuong ho tro", "cong tac boi thuong",
            # Viết hoa (auto-generated)
            "HOÀN THÀNH",
            "BỒI THƯỜNG HỖ TRỢ",
            "CÔNG TÁC BỒI THƯỜNG"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "HDCQ": {
        "keywords": [
            # Có dấu
            "hợp đồng chuyển nhượng", "hợp đồng tặng cho",
            "chuyển nhượng quyền", "tặng cho quyền", "hợp đồng",
            "chuyển nhượng quyền sử dụng đất", "chuyển nhượng qsd",
            # Không dấu
            "hop dong chuyen nhuong", "hop dong tang cho",
            "chuyen nhuong quyen", "tang cho quyen", "hop dong",
            "chuyen nhuong quyen su dung dat",
            # Viết hoa (OCR thường đọc thành chữ hoa)
            "HOP DONG", "CHUYEN NHUONG", "TANG CHO",
            "HOP DONG CHUYEN NHUONG", "CHUYEN NHUONG QUYEN",
            "CHUYEN NHUONG QUYEN SU DUNG DAT",
            # OCR common typos (quan trọng!)
            "NHUQNG", "CHUYEN NHUQNG", "HOP DONG CHUYEN NHUQNG",
            "NHUONG", "CHUYEN NHUONG QUYEN SU' DUNG",
            "chuyen nhuqng", "hop dong chuyen nhuqng",
            # EasyOCR specific typos
            "HỢP ĐỎNG", "ĐỎNG", "hop dong", "HOP ĐỎNG",
            "CHUYỂN NHƯONG", "NHƯONG", "chuyen nhuong",
            "HỢP ĐỎNG CHUYỂN NHƯỢNG", "HỢP ĐỎNG CHUYỂN NHƯONG",
            "QUYẺN", "QUYỀN", "quyen", "QUYẺN SỬ DỤNG",
            # More variants
            "hợp đỏng", "đỏng", "chuyển nhưong", "nhưong"
        ],
        "weight": 1.6,
        "min_matches": 1
    },
    "HDBDG": {
        "keywords": [
            # Có dấu
            "hợp đồng mua bán", "bán đấu giá", "tài sản đấu giá",
            "hợp đồng", "đấu giá",
            # Không dấu
            "hop dong mua ban", "ban dau gia", "tai san dau gia",
            "hop dong", "dau gia",
            # Viết hoa
            "HOP DONG MUA BAN", "DAU GIA"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "HDTHC": {
        "keywords": [
            # Có dấu
            "hợp đồng thế chấp", "thế chấp quyền", "thế chấp đất",
            "hợp đồng", "thế chấp",
            # Không dấu
            "hop dong the chap", "the chap quyen", "the chap dat",
            "hop dong", "the chap",
            # Viết hoa
            "HOP DONG THE CHAP", "THE CHAP"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "HDTCO": {
        "keywords": [
            # Có dấu
            "hợp đồng thi công", "thi công xây dựng", "hợp đồng", "thi công",
            # Không dấu
            "hop dong thi cong", "thi cong xay dung", "hop dong", "thi cong",
            # Viết hoa
            "HOP DONG THI CONG", "THI CONG"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDTD": {
        "keywords": [
            # Có dấu
            "hợp đồng thuê đất", "thuê đất", "điều chỉnh hợp đồng",
            # Không dấu
            "hop dong thue dat", "thue dat", "dieu chinh hop dong",
            # Viết hoa (auto-generated)
            "HỢP ĐỒNG THUÊ ĐẤT",
            "THUÊ ĐẤT",
            "ĐIỀU CHỈNH HỢP ĐỒNG"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDUQ": {
        "keywords": [
            # Có dấu
            "hợp đồng ủy quyền", "ủy quyền",
            # Không dấu
            "hop dong uy quyen", "uy quyen",
            # Viết hoa (auto-generated)
            "HỢP ĐỒNG ỦY QUYỀN",
            "ỦY QUYỀN"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "PCT": {
        "keywords": [
            # Có dấu
            "phiếu chuyển thông tin", "nghĩa vụ tài chính",
            "chuyển thông tin", "phiếu chuyển",
            # Không dấu
            "phieu chuyen thong tin", "nghia vu tai chinh",
            "chuyen thong tin", "phieu chuyen",
            # Viết hoa
            "PHIEU CHUYEN", "CHUYEN THONG TIN", "NGHIA VU TAI CHINH"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "PKTHS": {
        "keywords": [
            # Có dấu
            "phiếu kiểm tra", "kiểm tra hồ sơ",
            # Không dấu
            "phieu kiem tra", "kiem tra ho so",
            # Viết hoa (auto-generated)
            "PHIẾU KIỂM TRA",
            "KIỂM TRA HỒ SƠ"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "PLYKDC": {
        "keywords": [
            # Có dấu
            "phiếu lấy ý kiến", "khu dân cư", "ý kiến dân",
            # Không dấu
            "phieu lay y kien", "khu dan cu", "y kien dan",
            # Viết hoa (auto-generated)
            "PHIẾU LẤY Ý KIẾN",
            "KHU DÂN CƯ",
            "Ý KIẾN DÂN"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "PXNKQDD": {
        "keywords": [
            # Có dấu
            "phiếu xác nhận", "kết quả đo đạc", "đo đạc",
            # Không dấu
            "phieu xac nhan", "ket qua do dac", "do dac",
            # Viết hoa (auto-generated)
            "PHIẾU XÁC NHẬN",
            "KẾT QUẢ ĐO ĐẠC",
            "ĐO ĐẠC"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DKTC": {
        "keywords": [
            # Có dấu
            "phiếu yêu cầu", "đăng ký biện pháp", "bảo đảm",
            "quyền sử dụng đất",
            # Không dấu
            "phieu yeu cau", "dang ky bien phap", "bao dam",
            "quyen su dung dat",
            # Viết hoa (auto-generated)
            "PHIẾU YÊU CẦU",
            "ĐĂNG KÝ BIỆN PHÁP",
            "BẢO ĐẢM",
            "QUYỀN SỬ DỤNG ĐẤT"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DKTD": {
        "keywords": [
            # Có dấu
            "phiếu yêu cầu", "đăng ký thay đổi", "biện pháp bảo đảm",
            # Không dấu
            "phieu yeu cau", "dang ky thay doi", "bien phap bao dam",
            # Viết hoa (auto-generated)
            "PHIẾU YÊU CẦU",
            "ĐĂNG KÝ THAY ĐỔI",
            "BIỆN PHÁP BẢO ĐẢM"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DKXTC": {
        "keywords": [
            # Có dấu
            "phiếu yêu cầu", "xóa đăng ký", "biện pháp bảo đảm",
            # Không dấu
            "phieu yeu cau", "xoa dang ky", "bien phap bao dam",
            # Viết hoa (auto-generated)
            "PHIẾU YÊU CẦU",
            "XÓA ĐĂNG KÝ",
            "BIỆN PHÁP BẢO ĐẢM"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QR": {
        "keywords": [
            # Có dấu
            "mã qr", "quét mã", "qr code",
            # Không dấu
            "ma qr", "quet ma", "qr code",
            # Viết hoa (auto-generated)
            "MÃ QR",
            "QUÉT MÃ"
        ],
        "weight": 1.2, "min_matches": 1
    },
    "QDCMD": {
        "keywords": [
            # Có dấu
            "quyết định", "cho phép chuyển mục đích",
            "chuyển mục đích sử dụng",
            # Không dấu
            "quyet dinh", "cho phep chuyen muc dich",
            "chuyen muc dich su dung",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "CHO PHÉP CHUYỂN MỤC ĐÍCH",
            "CHUYỂN MỤC ĐÍCH SỬ DỤNG"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDTT": {
        "keywords": [
            # Có dấu
            "quyết định", "cho phép tách", "hợp thửa",
            "tách thửa đất",
            # Không dấu
            "quyet dinh", "cho phep tach", "hop thua",
            "tach thua dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "CHO PHÉP TÁCH",
            "HỢP THỬA",
            "TÁCH THỬA ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDCHTGD": {
        "keywords": [
            # Có dấu
            "quyết định", "chuyển hình thức", "giao đất",
            "cho thuê đất",
            # Không dấu
            "quyet dinh", "chuyen hinh thuc", "giao dat",
            "cho thue dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "CHUYỂN HÌNH THỨC",
            "GIAO ĐẤT",
            "CHO THUÊ ĐẤT"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCGD": {
        "keywords": [
            # Có dấu
            "quyết định", "điều chỉnh quyết định", "giao đất",
            # Không dấu
            "quyet dinh", "dieu chinh quyet dinh", "giao dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "ĐIỀU CHỈNH QUYẾT ĐỊNH",
            "GIAO ĐẤT"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCTH": {
        "keywords": [
            # Có dấu
            "quyết định", "điều chỉnh thời hạn", "dự án đầu tư",
            # Không dấu
            "quyet dinh", "dieu chinh thoi han", "du an dau tu",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "ĐIỀU CHỈNH THỜI HẠN",
            "DỰ ÁN ĐẦU TƯ"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDGH": {
        "keywords": [
            # Có dấu
            "quyết định", "gia hạn", "hết thời hạn",
            # Không dấu
            "quyet dinh", "gia han", "het thoi han",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "GIA HẠN",
            "HẾT THỜI HẠN"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDGTD": {
        "keywords": [
            # Có dấu
            "quyết định", "giao đất", "cho thuê đất",
            # Không dấu
            "quyet dinh", "giao dat", "cho thue dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "GIAO ĐẤT",
            "CHO THUÊ ĐẤT"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "QDHG": {
        "keywords": [
            # Có dấu
            "quyết định", "hủy giấy chứng nhận", "hủy gcn",
            # Không dấu
            "quyet dinh", "huy giay chung nhan", "huy gcn",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "HỦY GIẤY CHỨNG NHẬN",
            "HỦY GCN"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "QDPDBT": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "bồi thường", "tái định cư",
            # Không dấu
            "quyet dinh", "phe duyet", "boi thuong", "tai dinh cu",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "PHÊ DUYỆT",
            "BỒI THƯỜNG",
            "TÁI ĐỊNH CƯ"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCQH": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "điều chỉnh quy hoạch",
            # Không dấu
            "quyet dinh", "phe duyet", "dieu chinh quy hoach",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "PHÊ DUYỆT",
            "ĐIỀU CHỈNH QUY HOẠCH"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDPDDG": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "đơn giá",
            # Không dấu
            "quyet dinh", "phe duyet", "don gia",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "PHÊ DUYỆT",
            "ĐƠN GIÁ"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "QDTHA": {
        "keywords": [
            # Có dấu
            "quyết định", "thi hành án", "đơn yêu cầu",
            # Không dấu
            "quyet dinh", "thi hanh an", "don yeu cau",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "THI HÀNH ÁN",
            "ĐƠN YÊU CẦU"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDTH": {
        "keywords": [
            # Có dấu
            "quyết định", "thu hồi đất",
            # Không dấu
            "quyet dinh", "thu hoi dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "THU HỒI ĐẤT"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "QDHTSD": {
        "keywords": [
            # Có dấu
            "quyết định", "hình thức sử dụng đất",
            # Không dấu
            "quyet dinh", "hinh thuc su dung dat",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "HÌNH THỨC SỬ DỤNG ĐẤT"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "QDXP": {
        "keywords": [
            # Có dấu
            "quyết định", "xử phạt", "vi phạm",
            # Không dấu
            "quyet dinh", "xu phat", "vi pham",
            # Viết hoa (auto-generated)
            "QUYẾT ĐỊNH",
            "XỬ PHẠT",
            "VI PHẠM"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "SDTT": {
        "keywords": [
            # Có dấu
            "sơ đồ", "dự kiến tách thửa", "tách thửa",
            # Không dấu
            "so do", "du kien tach thua", "tach thua",
            # Viết hoa (auto-generated)
            "SƠ ĐỒ",
            "DỰ KIẾN TÁCH THỬA",
            "TÁCH THỬA"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "TBCNBD": {
        "keywords": [
            # Có dấu
            "thông báo", "cập nhật", "chỉnh lý", "biến động",
            # Không dấu
            "thong bao", "cap nhat", "chinh ly", "bien dong",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "CẬP NHẬT",
            "CHỈNH LÝ",
            "BIẾN ĐỘNG"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "CKDC": {
        "keywords": [
            # Có dấu
            "thông báo", "công bố", "công khai", "di chúc",
            # Không dấu
            "thong bao", "cong bo", "cong khai", "di chuc",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "CÔNG BỐ",
            "CÔNG KHAI",
            "DI CHÚC"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "TBT": {
        "keywords": [
            # Có dấu
            "thông báo thuế", "trước bạ", "thu nhập cá nhân",
            "tiền sử dụng đất",
            # Không dấu
            "thong bao thue", "truoc ba", "thu nhap ca nhan",
            "tien su dung dat",
            # Viết hoa (auto-generated)
            "THÔNG BÁO THUẾ",
            "TRƯỚC BẠ",
            "THU NHẬP CÁ NHÂN",
            "TIỀN SỬ DỤNG ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "TBMG": {
        "keywords": [
            # Có dấu
            "thông báo", "gcn bị mất", "niêm yết",
            # Không dấu
            "thong bao", "gcn bi mat", "niem yet",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "GCN BỊ MẤT",
            "NIÊM YẾT"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "TBCKCG": {
        "keywords": [
            # Có dấu
            "thông báo", "công khai", "kết quả", "thẩm tra",
            "cấp gcn",
            # Không dấu
            "thong bao", "cong khai", "ket qua", "tham tra",
            "cap gcn",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "CÔNG KHAI",
            "KẾT QUẢ",
            "THẨM TRA",
            "CẤP GCN"
        ],
        "weight": 0.8, "min_matches": 3
    },
    "TBCKMG": {
        "keywords": [
            # Có dấu
            "thông báo", "niêm yết", "mất gcn",
            # Không dấu
            "thong bao", "niem yet", "mat gcn",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "NIÊM YẾT",
            "MẤT GCN"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "HTNVTC": {
        "keywords": [
            # Có dấu
            "thông báo", "xác nhận", "hoàn thành", "nghĩa vụ tài chính",
            # Không dấu
            "thong bao", "xac nhan", "hoan thanh", "nghia vu tai chinh",
            # Viết hoa (auto-generated)
            "THÔNG BÁO",
            "XÁC NHẬN",
            "HOÀN THÀNH",
            "NGHĨA VỤ TÀI CHÍNH"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "TKT": {
        "keywords": [
            # Có dấu
            "tờ khai thuế", "trước bạ", "tncn", "tiền sử dụng đất",
            # Không dấu
            "to khai thue", "truoc ba", "tien su dung dat",
            # Viết hoa (auto-generated)
            "TỜ KHAI THUẾ",
            "TRƯỚC BẠ",
            "TIỀN SỬ DỤNG ĐẤT"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "TTr": {
        "keywords": [
            # Có dấu
            "tờ trình", "giao đất", "cho thuê đất",
            "chuyển mục đích",
            # Không dấu
            "to trinh", "giao dat", "cho thue dat",
            "chuyen muc dich",
            # Viết hoa (auto-generated)
            "TỜ TRÌNH",
            "GIAO ĐẤT",
            "CHO THUÊ ĐẤT",
            "CHUYỂN MỤC ĐÍCH"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "TTCG": {
        "keywords": [
            # Có dấu
            "tờ trình", "đăng ký đất đai", "ubnd xã",
            # Không dấu
            "to trinh", "dang ky dat dai", "ubnd xa",
            # Viết hoa (auto-generated)
            "TỜ TRÌNH",
            "ĐĂNG KÝ ĐẤT ĐAI",
            "UBND XÃ"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "CKTSR": {
        "keywords": [
            # Có dấu
            "văn bản", "cam kết", "tài sản riêng",
            # Không dấu
            "van ban", "cam ket", "tai san rieng",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "CAM KẾT",
            "TÀI SẢN RIÊNG"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "VBCTCMD": {
        "keywords": [
            # Có dấu
            "văn bản", "chấp thuận", "chuyển mục đích",
            # Không dấu
            "van ban", "chap thuan", "chuyen muc dich",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "CHẤP THUẬN",
            "CHUYỂN MỤC ĐÍCH"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "VBDNCT": {
        "keywords": [
            # Có dấu
            "văn bản", "đề nghị", "chấp thuận", "chuyển nhượng",
            "thuê", "góp vốn",
            # Không dấu
            "van ban", "de nghi", "chap thuan", "chuyen nhuong",
            "thue", "gop von",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "ĐỀ NGHỊ",
            "CHẤP THUẬN",
            "CHUYỂN NHƯỢNG",
            "THUÊ",
            "GÓP VỐN"
        ],
        "weight": 0.8, "min_matches": 3
    },
    "PDPASDD": {
        "keywords": [
            # Có dấu
            "văn bản", "đề nghị", "thẩm định", "phê duyệt",
            "phương án sử dụng đất",
            # Không dấu
            "van ban", "de nghi", "tham dinh", "phe duyet",
            "phuong an su dung dat",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "ĐỀ NGHỊ",
            "THẨM ĐỊNH",
            "PHÊ DUYỆT",
            "PHƯƠNG ÁN SỬ DỤNG ĐẤT"
        ],
        "weight": 0.8, "min_matches": 3
    },
    "VBTK": {
        "keywords": [
            # Có dấu
            "văn bản", "thỏa thuận", "phân chia", "di sản", "thừa kế",
            # Không dấu
            "van ban", "thoa thuan", "phan chia", "di san", "thua ke",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "THỎA THUẬN",
            "PHÂN CHIA",
            "DI SẢN",
            "THỪA KẾ"
        ],
        "weight": 0.9, "min_matches": 3
    },
    "TTHGD": {
        "keywords": [
            # Có dấu
            "văn bản", "thỏa thuận", "quyền sử dụng đất",
            "hộ gia đình",
            # Không dấu
            "van ban", "thoa thuan", "quyen su dung dat",
            "ho gia dinh",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "THỎA THUẬN",
            "QUYỀN SỬ DỤNG ĐẤT",
            "HỘ GIA ĐÌNH"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "CDLK": {
        "keywords": [
            # Có dấu
            "văn bản", "thỏa thuận", "chấm dứt", "quyền hạn chế",
            "thửa đất liền kề",
            # Không dấu
            "van ban", "thoa thuan", "cham dut", "quyen han che",
            "thua dat lien ke",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "THỎA THUẬN",
            "CHẤM DỨT",
            "QUYỀN HẠN CHẾ",
            "THỬA ĐẤT LIỀN KỀ"
        ],
        "weight": 0.9, "min_matches": 3
    },
    "HCLK": {
        "keywords": [
            # Có dấu
            "văn bản", "thỏa thuận", "xác lập", "quyền hạn chế",
            "thửa đất liền kề",
            # Không dấu
            "van ban", "thoa thuan", "xac lap", "quyen han che",
            "thua dat lien ke",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "THỎA THUẬN",
            "XÁC LẬP",
            "QUYỀN HẠN CHẾ",
            "THỬA ĐẤT LIỀN KỀ"
        ],
        "weight": 0.9, "min_matches": 3
    },
    "VBTC": {
        "keywords": [
            # Có dấu
            "văn bản", "từ chối", "nhận di sản", "thừa kế",
            # Không dấu
            "van ban", "tu choi", "nhan di san", "thua ke",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "TỪ CHỐI",
            "NHẬN DI SẢN",
            "THỪA KẾ"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "PCTSVC": {
        "keywords": [
            # Có dấu
            "văn bản", "phân chia", "tài sản chung", "vợ chồng",
            # Không dấu
            "van ban", "phan chia", "tai san chung", "vo chong",
            # Viết hoa (auto-generated)
            "VĂN BẢN",
            "PHÂN CHIA",
            "TÀI SẢN CHUNG",
            "VỢ CHỒNG"
        ],
        "weight": 0.9, "min_matches": 2
    }
}


def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for matching (lowercase + clean whitespace)"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_title_text(text: str) -> str:
    """
    Remove common government headers from document titles
    to improve fuzzy matching accuracy
    
    Vietnamese admin docs often start with:
    - CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
    - Độc lập - Tự do - Hạnh phúc
    
    Returns:
        Cleaned title text without header
    """
    if not text:
        return text
    
    cleaned = text
    
    # Remove common Vietnamese government headers (very aggressive)
    patterns = [
        (r'CỘNG\s*HÒA.*?VIỆT\s*NAM', ''),
        (r'[ĐD][ôoố]c\s*[lL][âaậ]p.*?[Pp]húc', ''),  # Độc lập ... Hạnh phúc
        (r'[ĐD][ôoố]c\s*[lL][âaậ]p\s+Tự\s+[dD]o\s+H[aạ]nh\s+[pP]húc', ''),  # Without dash
        (r'Mẫu\s*số\s*[\w/]+', ''),
        (r'BÊN\s+\w+\s+QUYỀN', ''),  # BÊN ỦY QUYỀN, BÊN CHUYỂN NHƯỢNG
        (r'\(sau\s+đây.*', ''),  # Everything after "(sau đây..."
    ]
    
    for pattern, replacement in patterns:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and punctuation
    cleaned = re.sub(r'[-–—]\s*', ' ', cleaned)  # Remove dashes
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


def calculate_uppercase_ratio(text: str) -> float:
    """
    Calculate ratio of uppercase letters in text
    
    Vietnamese administrative documents:
    - Titles: 80-100% uppercase (e.g., "GIẤY CHỨNG NHẬN")
    - Body: 10-30% uppercase (proper nouns only)
    
    Returns:
        float: Ratio of uppercase letters (0.0 to 1.0)
    """
    if not text:
        return 0.0
    
    # Count Vietnamese letters (exclude numbers, punctuation)
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    
    uppercase_count = sum(1 for c in letters if c.isupper())
    return uppercase_count / len(letters)


def is_title_text(text: str, uppercase_threshold: float = 0.7) -> bool:
    """
    Check if text appears to be a title based on uppercase ratio
    
    Vietnamese titles typically have 70%+ uppercase letters
    
    Args:
        text: Text to check
        uppercase_threshold: Minimum uppercase ratio to be considered title (default 0.7)
    
    Returns:
        bool: True if likely a title, False otherwise
    """
    ratio = calculate_uppercase_ratio(text)
    return ratio >= uppercase_threshold


def get_case_aware_score_multiplier(text: str) -> float:
    """
    Get score multiplier based on uppercase ratio (case-aware scoring)
    
    Multipliers based on Vietnamese administrative document conventions:
    - 80-100% uppercase: 2.0x (definitely title)
    - 70-80% uppercase: 1.5x (likely title)
    - 50-70% uppercase: 1.2x (mixed, some title elements)
    - 30-50% uppercase: 1.0x (normal body with proper nouns)
    - <30% uppercase: 0.8x (mostly body text)
    
    Returns:
        float: Score multiplier
    """
    ratio = calculate_uppercase_ratio(text)
    
    if ratio >= 0.8:
        return 2.0  # Definitely title (80-100% uppercase)
    elif ratio >= 0.7:
        return 1.5  # Likely title (70-80% uppercase)
    elif ratio >= 0.5:
        return 1.2  # Mixed (50-70% uppercase)
    elif ratio >= 0.3:
        return 1.0  # Normal body (30-50% uppercase)
    else:
        return 0.8  # Mostly lowercase body (<30% uppercase)


def calculate_similarity_with_case_awareness(str1: str, str2: str) -> Tuple[float, float]:
    """
    Calculate string similarity with case awareness bonus
    
    Returns:
        Tuple[float, float]: (base_similarity, case_aware_similarity)
        
    Vietnamese admin documents: UPPERCASE titles are more reliable
    """
    # Base similarity (case-insensitive)
    s1_norm = normalize_text(str1)
    s2_norm = normalize_text(str2)
    base_similarity = SequenceMatcher(None, s1_norm, s2_norm).ratio()
    
    # Case awareness bonus
    uppercase_ratio = calculate_uppercase_ratio(str1)
    
    # If title is UPPERCASE (70%+), it's more reliable → boost similarity
    if uppercase_ratio >= 0.7:
        # 70-80%: +2% boost, 80-90%: +3% boost, 90-100%: +5% boost
        case_bonus = 0.02 + (uppercase_ratio - 0.7) * 0.1  # Max +5%
        case_aware_similarity = min(base_similarity + case_bonus, 1.0)
    else:
        # Lowercase/mixed case: penalize slightly to require higher base similarity
        case_penalty = (0.7 - uppercase_ratio) * 0.05  # Max -3.5%
        case_aware_similarity = max(base_similarity - case_penalty, 0.0)
    
    return base_similarity, case_aware_similarity


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate string similarity ratio (for backward compatibility)
    Returns case-aware similarity
    """
    _, case_aware_sim = calculate_similarity_with_case_awareness(str1, str2)
    return case_aware_sim


def find_best_template_match(title_text: str, templates: Dict[str, List[str]]) -> Tuple[str, float]:
    """
    Find best matching document type based on title templates
    
    Args:
        title_text: Extracted title from document
        templates: Dict of doc_type -> list of title templates
    
    Returns:
        Tuple[str, float]: (best_doc_type, best_similarity_score)
    """
    if not title_text:
        return None, 0.0
    
    best_match = None
    best_score = 0.0
    
    for doc_type, template_list in templates.items():
        for template in template_list:
            similarity = calculate_similarity(title_text, template)
            if similarity > best_score:
                best_score = similarity
                best_match = doc_type
    
    return best_match, best_score


def calculate_keyword_specificity(keyword: str, all_rules: Dict) -> float:
    """
    Calculate how specific a keyword is
    
    Specificity = 1.0 / (number of doc types using this keyword)
    
    Returns:
        float: Multiplier (1.0 = very specific, 0.1 = very generic)
    """
    keyword_norm = normalize_text(keyword)
    usage_count = 0
    
    for doc_type, rules in all_rules.items():
        keywords = rules.get("keywords", [])
        for kw in keywords:
            if normalize_text(kw) == keyword_norm or keyword_norm in normalize_text(kw):
                usage_count += 1
                break  # Count each doc type only once
    
    if usage_count == 0:
        return 1.0
    
    # Specificity: fewer types use it = more specific = higher score
    # 1 type: 2.0x, 2 types: 1.0x, 5 types: 0.4x, 10+ types: 0.2x
    if usage_count == 1:
        return 2.0
    elif usage_count == 2:
        return 1.0
    elif usage_count <= 5:
        return 0.6
    else:
        return 0.3


def get_active_rules() -> Dict:
    """
    Get active rules with user overrides applied
    
    Priority:
    1. User overrides from rules_overrides.json
    2. Default DOCUMENT_RULES
    
    Returns:
        Dict: Merged rules
    """
    try:
        from pathlib import Path
        import json
        
        # Get user data path
        USER_DATA_PATH = os.environ.get('USER_DATA_PATH', str(Path.home() / '.90daychonhanh'))
        RULES_OVERRIDE_FILE = Path(USER_DATA_PATH) / 'rules_overrides.json'
        
        # Start with default rules
        merged_rules = dict(DOCUMENT_RULES)
        
        # Apply overrides if file exists
        if RULES_OVERRIDE_FILE.exists():
            try:
                with open(RULES_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
                    overrides = json.load(f)
                
                # Merge overrides into default rules
                for doc_type, rule_data in overrides.items():
                    if doc_type in merged_rules:
                        # Update existing rule (merge keywords, update weight/min_matches)
                        merged_rules[doc_type].update(rule_data)
                    else:
                        # Add new rule
                        merged_rules[doc_type] = rule_data
            except Exception as e:
                print(f"⚠️ Error loading rules overrides: {e}", file=sys.stderr)
        
        return merged_rules
    except Exception as e:
        print(f"⚠️ Error in get_active_rules: {e}, falling back to defaults", file=sys.stderr)
        return DOCUMENT_RULES


def check_required_keywords_in_title(doc_type: str, title_text: str, config: Dict) -> bool:
    """
    Check if document type's required keywords appear in title
    
    Returns:
        bool: True if required keywords found (or no requirement), False otherwise
    """
    if doc_type not in config:
        return True  # No requirement = pass
    
    required = config[doc_type].get("required_in_title", [])
    if not required:
        return True  # No requirement = pass
    
    if not title_text:
        return False  # Has requirement but no title = fail
    
    title_norm = normalize_text(title_text)
    
    # Check if ANY of the required keywords is in title
    for req_kw in required:
        if normalize_text(req_kw) in title_norm:
            return True
    
    return False


def classify_by_rules(text: str, title_text: str = None, confidence_threshold: float = 0.3, ocr_engine: str = 'tesseract') -> Dict:
    """
    HYBRID CLASSIFICATION: Fuzzy title matching + Keyword fallback
    
    Tier 1: Title similarity >= 75% → High confidence (instant match)
    Tier 2: Title similarity >= 50% → Check keywords
    Tier 3: Title similarity < 50% → Pure keyword matching
    
    Args:
        text: Full OCR text
        title_text: Text extracted from large fonts (titles/headers)
        confidence_threshold: Minimum confidence threshold
        ocr_engine: OCR engine used ('tesseract', 'easyocr', 'vietocr', 'google', 'azure')

        
    Returns:
        Classification result with type, confidence, and method used
    """
    text_normalized = normalize_text(text)
    title_normalized = normalize_text(title_text) if title_text else ""
    
    # Load active rules (with user overrides applied)
    active_rules = get_active_rules()
    
    # ==================================================================
    # TIER 0: EXACT TITLE MATCHING (100% confidence)
    # ==================================================================
    if title_text:
        # Normalize and clean title for exact matching
        cleaned_title = clean_title_text(title_text)
        title_upper = cleaned_title.upper().strip()
        
        # Check exact match in EXACT_TITLE_MAPPING
        if title_upper in EXACT_TITLE_MAPPING:
            matched_code = EXACT_TITLE_MAPPING[title_upper]
            doc_name = classify_document_name_from_code(matched_code)
            
            print(f"🎯 TIER 0: EXACT title match '{title_upper[:60]}...' → {matched_code}", file=sys.stderr)
            
            return {
                "type": matched_code,
                "doc_type": doc_name,
                "short_code": matched_code,
                "confidence": 1.0,  # 100% confidence
                "matched_keywords": [f"Exact title match: {title_upper[:50]}..."],
                "title_boost": True,
                "reasoning": f"Exact title match (100%)",
                "method": "exact_title_match",
                "accuracy_estimate": "100%",
                "recommend_cloud_boost": False
            }
    
    # ==================================================================
    # PRE-CHECK: Vietnamese admin titles MUST be uppercase (70%+)
    # ==================================================================
    # Clean title first to remove government headers, then check uppercase
    # This prevents headers like "Đôc lâp - Tự do" from affecting ratio
    if title_text:
        cleaned_title = clean_title_text(title_text)
        
        # Calculate uppercase on CLEANED title (without headers)
        if cleaned_title:
            title_uppercase_ratio = calculate_uppercase_ratio(cleaned_title)
        else:
            # If cleaning removed everything, check original
            title_uppercase_ratio = calculate_uppercase_ratio(title_text)
        
        # STRICT MODE: Vietnamese admin titles MUST be uppercase (70%+)
        # Apply same threshold for both Cloud and Offline OCR
        # Rationale: Cloud OCR (Google/Azure) is highly accurate, no need for relaxed threshold
        is_cloud_ocr = ocr_engine in ['google', 'azure']
        uppercase_threshold = 0.7  # STRICT: 70% for ALL engines (Cloud + Offline)
        
        # If title has low uppercase ratio, it's likely NOT a real title but
        # a mention in body text (e.g., "Giấy chứng nhận..." in contract body)
        # → Ignore this title and use ONLY body text for classification
        if title_uppercase_ratio < uppercase_threshold:
            engine_note = "(Cloud OCR)" if is_cloud_ocr else "(Offline OCR)"
            print(f"⚠️ Title has low uppercase ({title_uppercase_ratio:.0%} < {uppercase_threshold:.0%}), likely not a real title {engine_note}. Using body text only.", file=sys.stderr)
            title_text = None  # Ignore this title
            title_normalized = ""
    
    # ==================================================================
    # TIER 1: FUZZY TITLE MATCHING (>= 75% similarity)
    # ==================================================================
    if title_text:
        # Clean title by removing common government headers
        cleaned_title = clean_title_text(title_text)
        
        # Try matching with both original and cleaned title (use best result)
        best_template_match1, best_similarity1 = find_best_template_match(title_text, TITLE_TEMPLATES)
        best_template_match2, best_similarity2 = find_best_template_match(cleaned_title, TITLE_TEMPLATES)
        
        # Use whichever gives better similarity
        if best_similarity2 > best_similarity1:
            best_template_match = best_template_match2
            best_similarity = best_similarity2
        else:
            best_template_match = best_template_match1
            best_similarity = best_similarity1
        
        # Check if title is in UPPERCASE (Vietnamese admin document standard)
        title_uppercase_ratio = calculate_uppercase_ratio(title_text)
        is_uppercase_title = title_uppercase_ratio >= 0.7
        
        # INSTANT HIGH CONFIDENCE: Title similarity >= 80%
        if best_similarity >= 0.80 and is_uppercase_title:
            # HIGH CONFIDENCE - Direct match based on title
            doc_name = classify_document_name_from_code(best_template_match)
            
            # Boost confidence for UPPERCASE titles (more reliable)
            confidence = best_similarity
            confidence = min(confidence * 1.05, 1.0)  # 5% boost for uppercase
            
            print(f"✅ TIER 1 MATCH: Title '{title_text[:50]}...' matches {best_template_match} ({best_similarity:.1%} similarity)", file=sys.stderr)
            
            return {
                "type": best_template_match,
                "doc_type": doc_name,
                "short_code": best_template_match,
                "confidence": confidence,
                "matched_keywords": [f"Title fuzzy match: {best_similarity:.0%} (Uppercase: {title_uppercase_ratio:.0%})"],
                "title_boost": True,
                "reasoning": f"High title similarity: {best_similarity:.1%} (Instant match)",
                "method": "fuzzy_title_match",
                "accuracy_estimate": "95%+",
                "recommend_cloud_boost": False  # Very confident, no need for cloud boost
            }
        
        elif best_similarity >= 0.70 and is_uppercase_title:
            # MEDIUM CONFIDENCE (70-80%) - Verify with keywords
            print(f"⚠️ TIER 2: Title similarity {best_similarity:.1%}, verifying with keywords...", file=sys.stderr)
            # Continue to Tier 2...
            pass
        
        else:
            # LOW SIMILARITY (< 70%) - Don't trust title, use body keywords only
            print(f"⚠️ Title similarity too low ({best_similarity:.1%}), using body text only", file=sys.stderr)
            # Continue to Tier 3...
            pass
    
    # ==================================================================
    # TIER 2 & 3: KEYWORD MATCHING (with or without title boost)
    # ==================================================================
    scores = {}
    matched_keywords_dict = {}
    title_boost_applied = {}
    fuzzy_score_boost = {}
    
    for doc_type, rules in active_rules.items():
        # Check required keywords in title
        if not check_required_keywords_in_title(doc_type, title_text, DOCUMENT_TYPE_CONFIG):
            continue
        
        keywords = rules["keywords"]
        weight = rules.get("weight", 1.0)
        min_matches = rules.get("min_matches", 1)
        
        matched = []
        title_matches = 0
        total_score = 0.0
        
        for keyword in keywords:
            keyword_normalized = normalize_text(keyword)
            specificity = calculate_keyword_specificity(keyword, active_rules)
            
            if title_normalized and keyword_normalized in title_normalized:
                matched.append(f"{keyword} [TITLE]")
                title_matches += 1
                
                # Case-aware scoring: Check if keyword appears in UPPERCASE in original title
                # Find the keyword in original title_text (case-sensitive)
                if title_text:
                    # Get case-aware multiplier for the matched keyword context
                    case_multiplier = get_case_aware_score_multiplier(title_text)
                    total_score += weight * specificity * 3.0 * case_multiplier
                else:
                    total_score += weight * specificity * 3.0
                    
            elif keyword_normalized in text_normalized:
                matched.append(keyword)
                # Body match: weight × specificity × 1.0 (no case bonus for body)
                total_score += weight * specificity * 1.0
        
        if len(matched) >= min_matches:
            # TIER 2 BONUS: If doc type has good title similarity (50-80%), boost score
            if title_text and doc_type in TITLE_TEMPLATES:
                doc_templates = TITLE_TEMPLATES[doc_type]
                max_sim = max(calculate_similarity(title_text, t) for t in doc_templates)
                if max_sim >= 0.5:
                    fuzzy_boost = max_sim * 10  # 50% = +5 points, 70% = +7 points
                    total_score += fuzzy_boost
                    fuzzy_score_boost[doc_type] = max_sim
            
            scores[doc_type] = total_score
            matched_keywords_dict[doc_type] = matched
            title_boost_applied[doc_type] = title_matches > 0
    
    if not scores:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0,
            "matched_keywords": [],
            "title_boost": False,
            "reasoning": "Không khớp mẫu nào đủ điều kiện",
            "method": "no_match"
        }
    
    # Pick best scoring type
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    doc_name = classify_document_name_from_code(best_type)
    
    # Convert aggregated score to confidence (0.0 - 1.0) with simple logistic-like scaling
    confidence = min(0.35 + best_score / 20.0, 1.0)
    
    reasoning_parts = [
        f"Top score: {best_type} = {best_score:.2f}",
        f"Matches: {', '.join(matched_keywords_dict[best_type][:6])}"
    ]
    if best_type in fuzzy_score_boost:
        reasoning_parts.append(f"Title fuzzy boost ~{fuzzy_score_boost[best_type]:.0%}")
    reasoning = "; ".join(reasoning_parts)
    
    return {
        "type": best_type,
        "doc_type": doc_name,
        "short_code": best_type,
        "confidence": confidence,
        "matched_keywords": matched_keywords_dict[best_type],
        "title_boost": title_boost_applied.get(best_type, False),
        "reasoning": reasoning,
        "method": "keyword_match" if best_type not in fuzzy_score_boost else "hybrid_match"
    }


def classify_document_name_from_code(short_code: str) -> str:
    """Get full document name from short code"""
    code_to_name = {
        "GCN": "Giấy chứng nhận quyền sử dụng đất (Generic - sẽ phân loại sau batch)",
        "GCNM": "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất",
        "GCNC": "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất (Bản chính)",
        "BMT": "Bản mô tả ranh giới, mốc giới thửa đất",
        "HSKT": "Bản vẽ (Trích lục, đo tách, chỉnh lý)",
        "BVHC": "Bản vẽ hoàn công",
        "BVN": "Bản vẽ nhà",
        "BKKDT": "Bảng kê khai diện tích đang sử dụng",
        "DSCG": "Bảng liệt kê danh sách các thửa đất cấp giấy",
        "BBBDG": "Biên bản bán đấu giá tài sản",
        "BBGD": "Biên bản bàn giao đất trên thực địa",
        "BBHDDK": "Biên bản của Hội đồng đăng ký đất đai lần đầu",
        "BBNT": "Biên bản kiểm tra nghiệm thu công trình xây dựng",
        "BBKTSS": "Biên bản kiểm tra sai sót trên Giấy chứng nhận",
        "BBKTHT": "Biên bản kiểm tra, xác minh hiện trạng sử dụng đất",
        "BBKTDC": "Biên bản về việc kết thúc công khai công bố di chúc",
        "KTCKCG": "Biên bản về việc kết thúc thông báo niêm yết công khai kết quả kiểm tra hồ sơ đăng ký cấp GCNQSD đất",
        "KTCKMG": "Biên bản về việc kết thúc thông báo niêm yết công khai về việc mất GCNQSD đất",
        "BLTT": "Biên lai thu thuế sử dụng đất phi nông nghiệp",
        "CCCD": "Căn cước công dân",
        "DS15": "Danh sách chủ sử dụng và các thửa đất (mẫu 15)",
        "DSCK": "Danh sách công khai hồ sơ cấp giấy CNQSDĐ",
        "DICHUC": "Di chúc",
        "DCK": "Đơn cam kết, Giấy cam Kết",
        "DDKBD": "Đơn đăng ký biến động đất đai, tài sản gắn liền với đất",
        "DDK": "Đơn đăng ký đất đai, tài sản gắn liền với đất",
        "CHTGD": "Đơn đề nghị chuyển hình thức giao đất (cho thuê đất)",
        "DCQDGD": "Đơn đề nghị điều chỉnh quyết định giao đất (cho thuê đất, cho phép chuyển mục đích)",
        "DMG": "Đơn đề nghị miễn giảm Lệ phí trước bạ, thuế thu nhập cá nhân",
        "DMD": "Đơn đề nghị sử dụng đất kết hợp đa mục đích",
        "DXN": "Đơn xác nhận, Giấy Xác nhận",
        "DXCMD": "Đơn xin (đề nghị) chuyển mục đích sử dụng đất",
        "DGH": "Đơn xin (đề nghị) gia hạn sử dụng đất",
        "DXGD": "Đơn xin (đề nghị) giao đất, cho thuê đất",
        "DXTHT": "Đơn xin (đề nghị) tách thửa đất, hợp thửa đất",
        "DXCD": "Đơn xin cấp đổi Giấy chứng nhận",
        "DDCTH": "Đơn xin điều chỉnh thời hạn sử dụng đất của dự án đầu tư",
        "DXNTH": "Đơn xin xác nhận lại thời hạn sử dụng đất nông nghiệp",
        "GKH": "Giấy chứng nhận kết hôn",
        "GXNNVTC": "Giấy đề nghị xác nhận các khoản nộp vào ngân sách",
        "GKS": "Giấy Khai Sinh",
        "GNT": "Giấy nộp tiền vào Ngân sách nhà nước",
        "GSND": "Giấy sang nhượng đất",
        # UPDATED
        "GTLQ": "Giấy tiếp nhận hồ sơ và hẹn trả kết quả",
        "GUQ": "Giấy ủy quyền",
        "GXNDKLD": "Giấy xác nhận đăng ký lần đầu",
        "GPXD": "Giấy xin phép xây dựng",
        "hoadon": "Hoá đơn giá trị gia tăng",
        "HTBTH": "Hoàn thành công tác bồi thường hỗ trợ",
        "HDCQ": "Hợp đồng chuyển nhượng, tặng cho quyền sử dụng đất",
        "HDBDG": "Hợp đồng mua bán tài sản bán đấu giá",
        "HDTHC": "Hợp đồng thế chấp quyền sử dụng đất",
        "HDTCO": "Hợp đồng thi công",
        "HDTD": "Hợp đồng thuê đất, điều hỉnh hợp đồng thuê đất",
        "HDUQ": "Hợp đồng ủy quyền",
        "PCT": "Phiếu chuyển thông tin nghĩa vụ tài chính",
        "PKTHS": "Phiếu kiểm tra hồ sơ",
        "PLYKDC": "Phiếu lấy ý kiến khu dân cư",
        "PXNKQDD": "Phiếu xác nhận kết quả đo đạc",
        "DKTC": "Phiếu yêu cầu đăng ký biện pháp bảo đảm bằng quyền sử dụng đất",
        "DKTD": "Phiếu yêu cầu đăng ký thay đổi nội dung biện pháp bảo đảm",
        "DKXTC": "Phiếu yêu cầu xóa đăng ký biện pháp bảo đảm",
        "QR": "Quét mã QR",
        "QDCMD": "Quyết định cho phép chuyển mục đích",
        "QDTT": "Quyết định cho phép tách, hợp thửa đất",
        "QDCHTGD": "Quyết định chuyển hình thức giao đất (cho thuê đất)",
        "QDDCGD": "Quyết định điều chỉnh quyết định giao đất",
        "QDDCTH": "Quyết định điều chỉnh thời hạn SDĐ của dự án đầu tư",
        "QDGH": "Quyết định gia hạn sử dụng đất khi hết thời hạn SDĐ",
        "QDGTD": "Quyết định giao đất, cho thuê đất",
        "QDHG": "Quyết định hủy Giấy chứng nhận quyền sử dụng đất",
        "QDPDBT": "Quyết định phê duyệt phương án bồi thường, hỗ trợ, tái định cư",
        "QDDCQH": "Quyết định phê quyệt điều chỉnh quy hoạch",
        "QDPDDG": "Quyết định phê quyệt đơn giá",
        "QDTHA": "Quyết định thi hành án theo đơn yêu cầu",
        "QDTH": "Quyết định thu hồi đất",
        "QDHTSD": "Quyết định về hình thức sử dụng đất",
        "QDXP": "Quyết định xử phạt",
        "SDTT": "Sơ đồ dự kiến tách thửa",
        "TBCNBD": "Thông báo cập nhật, chỉnh lý biến động",
        "CKDC": "Thông báo công bố công khai di chúc",
        "TBT": "Thông báo thuế (trước bạ, thuế TNCN, tiền sử dụng đất)",
        "TBMG": "Thông báo về việc chuyển thông tin Giấy chứng nhận bị mất",
        "TBCKCG": "Thông báo về việc công khai kết quả thẩm tra xét duyệt hồ sơ",
        "TBCKMG": "Thông báo về việc niêm yết công khai mất giấy chứng nhận",
        "HTNVTC": "Thông báo xác nhận Hoàn thành nghĩa vụ tài chính",
        "TKT": "Tờ khai thuế (trước bạ, thuế TNCN, tiền sử dụng đất)",
        "TTr": "Tờ trình về giao đất (cho thuê đất, cho phép chuyển mục đích)",
        "TTCG": "Tờ trình về việc đăng ký đất đai, tài sản gắn liền với đất",
        "CKTSR": "Văn bản cam kết tài sản riêng",
        "VBCTCMD": "Văn bản chấp thuận cho phép chuyển mục đích",
    }
    return code_to_name.get(short_code, short_code)


class RuleClassifier:
    def __init__(self):
        pass

    def classify(self, text: str, title_text: str = None, ocr_engine: str = 'tesseract') -> Dict:
        return classify_by_rules(text, title_text, ocr_engine=ocr_engine)

