"""
Rule-based classifier for Vietnamese land documents
"""
import re
from typing import Dict, Tuple

# Document type rules with Vietnamese keywords (IMPROVED VERSION)
DOCUMENT_RULES = {
    "GCN": {
        "keywords": [
            "giấy chứng nhận quyền sử dụng đất",
            "giấy chứng nhận",
            "quyền sử dụng đất",
            "quyền sở hữu nhà ở",
            "cộng hòa xã hội chủ nghĩa việt nam",
            "độc lập tự do hạnh phúc",
            "gcn quyền sử dụng",
            "quyền sở hữu",
            "chứng nhận quyền"
        ],
        "weight": 1.0,
        "min_matches": 1  # Reduced from 2
    },
    "BMT": {
        "keywords": [
            "bản mô tả ranh giới",
            "mốc giới thửa đất",
            "vị trí ranh giới",
            "thửa đất số",
            "tờ bản đồ số",
            "mô tả ranh giới",  # NEW
            "ranh giới thửa",   # NEW
            "giới hạn thửa",    # NEW
            "mốc giới",          # NEW
            "phía đông giáp",   # NEW
            "phía tây giáp",    # NEW
            "phía nam giáp",    # NEW
            "phía bắc giáp"     # NEW
        ],
        "weight": 1.0,
        "min_matches": 1  # Reduced from 2
    },
    "HSKT": {
        "keywords": [
            "bản vẽ",
            "trích lục",
            "đo tách",
            "chỉnh lý",
            "hồ sơ kỹ thuật",
            "trích đo",
            "tỷ lệ 1:",
            "phiếu đo đạc",
            "bản vẽ trích lục",  # NEW
            "đo đạc chỉnh lý",   # NEW
            "trích đo địa chính" # NEW
        ],
        "weight": 0.9,
        "min_matches": 1
    },
    "BVHC": {
        "keywords": [
            "bản vẽ hoàn công",
            "hoàn công công trình",
            "công trình xây dựng",
            "bản vẽ thi công",
            "hoàn công nhà",        # NEW
            "hoàn công",            # NEW
            "công trình hoàn công", # NEW
            "thi công hoàn thành"   # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BVN": {
        "keywords": [
            "bản vẽ nhà",
            "mặt bằng nhà",
            "thiết kế nhà",
            "kiến trúc nhà",
            "thiết kế kiến trúc",   # NEW
            "mặt bằng",              # NEW
            "mặt tiền",              # NEW
            "mặt cắt",               # NEW
            "tầng 1",                # NEW
            "tầng 2",                # NEW
            "phòng khách",           # NEW
            "phòng ngủ"              # NEW
        ],
        "weight": 0.9,
        "min_matches": 1
    },
    "BKKDT": {
        "keywords": [
            "bảng kê khai diện tích",
            "diện tích đang sử dụng",
            "kê khai đất đai",
            "kê khai diện tích",     # NEW
            "bảng kê diện tích",     # NEW
            "diện tích sử dụng",     # NEW
            "kê khai đất"            # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "DSCG": {
        "keywords": [
            "danh sách",
            "cấp giấy",
            "thửa đất cấp giấy",
            "liệt kê",
            "danh sách thửa đất",    # NEW
            "danh sách cấp giấy",    # NEW
            "bảng liệt kê",          # NEW
            "danh sách các thửa",    # NEW
            "stt",                   # NEW (table indicator)
            "tờ bđ"                  # NEW (table header)
        ],
        "weight": 0.8,
        "min_matches": 1  # Reduced from 2
    },
    "BBBDG": {
        "keywords": [
            "biên bản bán đấu giá",
            "đấu giá tài sản",
            "bán đấu giá",
            "đấu giá",               # NEW
            "hội đồng đấu giá",      # NEW
            "tổ chức đấu giá",       # NEW
            "giá khởi điểm",         # NEW
            "trúng đấu giá"          # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBGD": {
        "keywords": [
            "biên bản bàn giao",
            "bàn giao đất",
            "thực địa",
            "bàn giao thực địa",
            "bàn giao",              # NEW
            "nhận bàn giao",         # NEW
            "giao nhận",             # NEW
            "bên giao",              # NEW
            "bên nhận"               # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBHDDK": {
        "keywords": [
            "hội đồng đăng ký",
            "đăng ký đất đai lần đầu",
            "biên bản hội đồng",
            "hội đồng",              # NEW
            "đăng ký lần đầu",       # NEW
            "xét hồ sơ",             # NEW
            "đăng ký đất đai"        # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBNT": {
        "keywords": [
            "biên bản nghiệm thu",
            "nghiệm thu công trình",
            "kiểm tra nghiệm thu",
            "nghiệm thu",            # NEW
            "hội đồng nghiệm thu",   # NEW
            "xác nhận hoàn thành",   # NEW
            "đạt yêu cầu"            # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBKTSS": {
        "keywords": [
            "kiểm tra sai sót",
            "sai sót trên giấy chứng nhận",
            "biên bản kiểm tra",
            "sai sót",               # NEW
            "phát hiện sai sót",     # NEW
            "chỉnh sửa thông tin",   # NEW
            "sai sót trên gcn"       # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBKTHT": {
        "keywords": [
            "xác minh hiện trạng",
            "kiểm tra hiện trạng",
            "sử dụng đất hiện trạng",
            "hiện trạng",            # NEW
            "kiểm tra thực địa",     # NEW
            "hiện trạng sử dụng",    # NEW
            "xác minh"               # NEW
        ],
        "weight": 1.0,
        "min_matches": 1
    }
}

def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for matching"""
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def classify_by_rules(text: str) -> Dict[str, any]:
    """
    Classify document based on keyword rules
    
    Args:
        text: Extracted text from OCR
        
    Returns:
        Dict with classification result
    """
    if not text or len(text) < 10:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0,
            "method": "rules",
            "matched_keywords": []
        }
    
    text_normalized = normalize_text(text)
    scores = {}
    matched_keywords_all = {}
    
    # Calculate scores for each document type
    for doc_type, rules in DOCUMENT_RULES.items():
        keywords = rules["keywords"]
        weight = rules["weight"]
        min_matches = rules["min_matches"]
        
        matched = []
        for keyword in keywords:
            if keyword in text_normalized:
                matched.append(keyword)
        
        if len(matched) >= min_matches:
            # Score based on number of matches and weight
            score = (len(matched) / len(keywords)) * weight
            scores[doc_type] = score
            matched_keywords_all[doc_type] = matched
    
    # Return best match
    if not scores:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0,
            "method": "rules",
            "matched_keywords": []
        }
    
    best_type = max(scores, key=scores.get)
    confidence = min(scores[best_type], 0.95)  # Cap at 0.95
    
    return {
        "type": best_type,
        "confidence": round(confidence, 2),
        "method": "rules",
        "matched_keywords": matched_keywords_all[best_type]
    }

def classify_document_name_from_code(short_code: str) -> str:
    """Get full document name from short code"""
    code_to_name = {
        "GCN": "Giấy chứng nhận quyền sử dụng đất",
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
        "BBKTHT": "Biên bản kiểm tra, xác minh hiện trạng sử dụng đất"
    }
    return code_to_name.get(short_code, "Không rõ loại tài liệu")
