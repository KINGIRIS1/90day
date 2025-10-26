"""
Rule-based classifier for Vietnamese land documents
"""
import re
from typing import Dict, Tuple

# Document type rules with Vietnamese keywords (IMPROVED VERSION)
DOCUMENT_RULES = {
    "GCN": {
        "keywords": [
            # Có dấu đầy đủ
            "giấy chứng nhận quyền sử dụng đất",
            "giấy chứng nhận",
            "quyền sử dụng đất",
            "quyền sở hữu nhà ở",
            "cộng hòa xã hội chủ nghĩa việt nam",
            "độc lập tự do hạnh phúc",
            "gcn quyền sử dụng",
            "quyền sở hữu",
            "chứng nhận quyền",
            "chi nhánh văn phòng đăng ký",
            "văn phòng đăng ký đất đai",
            # Không dấu
            "giay chung nhan",
            "quyen su dung dat",
            "quyen so huu",
            "chung nhan quyen",
            "giay chung nhan quyen su dung dat",
            "cong hoa xa hoi chu nghia viet nam",
            "doc lap tu do hanh phuc"
        ],
        "weight": 1.5,
        "min_matches": 1
    },
    "BMT": {
        "keywords": [
            # Có dấu
            "bản mô tả ranh giới",
            "mốc giới thửa đất",
            "vị trí ranh giới",
            "mô tả ranh giới",
            "ranh giới thửa",
            "giới hạn thửa",
            "mốc giới",
            "phía đông giáp",
            "phía tây giáp",
            "phía nam giáp",
            "phía bắc giáp",
            # Không dấu
            "ban mo ta ranh gioi",
            "moc gioi thua dat",
            "vi tri ranh gioi",
            "mo ta ranh gioi",
            "ranh gioi thua",
            "gioi han thua",
            "moc gioi",
            "phia dong giap",
            "phia tay giap",
            "phia nam giap",
            "phia bac giap"
        ],
        "weight": 1.0,
        "min_matches": 2
    },
    "HSKT": {
        "keywords": [
            # Có dấu
            "bản vẽ",
            "trích lục",
            "đo tách",
            "chỉnh lý",
            "hồ sơ kỹ thuật",
            "trích đo",
            "tỷ lệ 1:",
            "phiếu đo đạc",
            "bản vẽ trích lục",
            "đo đạc chỉnh lý",
            "trích đo địa chính",
            # Không dấu
            "ban ve",
            "trich luc",
            "do tach",
            "chinh ly",
            "ho so ky thuat",
            "trich do",
            "ty le 1:",
            "phieu do dac",
            "ban ve trich luc",
            "do dac chinh ly",
            "trich do dia chinh"
        ],
        "weight": 0.9,
        "min_matches": 1
    },
    "BVHC": {
        "keywords": [
            # Có dấu
            "bản vẽ hoàn công",
            "hoàn công công trình",
            "công trình xây dựng",
            "bản vẽ thi công",
            "hoàn công nhà",
            "hoàn công",
            "công trình hoàn công",
            "thi công hoàn thành",
            # Không dấu
            "ban ve hoan cong",
            "hoan cong cong trinh",
            "cong trinh xay dung",
            "ban ve thi cong",
            "hoan cong nha",
            "hoan cong",
            "cong trinh hoan cong",
            "thi cong hoan thanh"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BVN": {
        "keywords": [
            # Có dấu
            "bản vẽ nhà",
            "mặt bằng nhà",
            "thiết kế nhà",
            "kiến trúc nhà",
            "thiết kế kiến trúc",
            "mặt bằng",
            "mặt tiền",
            "mặt cắt",
            "tầng 1",
            "tầng 2",
            "phòng khách",
            "phòng ngủ",
            # Không dấu
            "ban ve nha",
            "mat bang nha",
            "thiet ke nha",
            "kien truc nha",
            "thiet ke kien truc",
            "mat bang",
            "mat tien",
            "mat cat",
            "tang 1",
            "tang 2",
            "phong khach",
            "phong ngu"
        ],
        "weight": 0.9,
        "min_matches": 1
    },
    "BKKDT": {
        "keywords": [
            # Có dấu
            "bảng kê khai diện tích",
            "diện tích đang sử dụng",
            "kê khai đất đai",
            "kê khai diện tích",
            "bảng kê diện tích",
            "diện tích sử dụng",
            "kê khai đất",
            # Không dấu
            "bang ke khai dien tich",
            "dien tich dang su dung",
            "ke khai dat dai",
            "ke khai dien tich",
            "bang ke dien tich",
            "dien tich su dung",
            "ke khai dat"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "DSCG": {
        "keywords": [
            # Có dấu
            "danh sách",
            "cấp giấy",
            "thửa đất cấp giấy",
            "liệt kê",
            "danh sách thửa đất",
            "danh sách cấp giấy",
            "bảng liệt kê",
            "danh sách các thửa",
            "stt",
            "tờ bđ",
            # Không dấu
            "danh sach",
            "cap giay",
            "thua dat cap giay",
            "liet ke",
            "danh sach thua dat",
            "danh sach cap giay",
            "bang liet ke",
            "danh sach cac thua",
            "to bd"
        ],
        "weight": 0.8,
        "min_matches": 1
    },
    "BBBDG": {
        "keywords": [
            # Có dấu
            "biên bản bán đấu giá",
            "đấu giá tài sản",
            "bán đấu giá",
            "đấu giá",
            "hội đồng đấu giá",
            "tổ chức đấu giá",
            "giá khởi điểm",
            "trúng đấu giá",
            # Không dấu
            "bien ban ban dau gia",
            "dau gia tai san",
            "ban dau gia",
            "dau gia",
            "hoi dong dau gia",
            "to chuc dau gia",
            "gia khoi diem",
            "trung dau gia"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBGD": {
        "keywords": [
            # Có dấu
            "biên bản bàn giao",
            "bàn giao đất",
            "thực địa",
            "bàn giao thực địa",
            "bàn giao",
            "nhận bàn giao",
            "giao nhận",
            "bên giao",
            "bên nhận",
            # Không dấu
            "bien ban ban giao",
            "ban giao dat",
            "thuc dia",
            "ban giao thuc dia",
            "ban giao",
            "nhan ban giao",
            "giao nhan",
            "ben giao",
            "ben nhan"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBHDDK": {
        "keywords": [
            # Có dấu
            "hội đồng đăng ký",
            "đăng ký đất đai lần đầu",
            "biên bản hội đồng",
            "hội đồng",
            "đăng ký lần đầu",
            "xét hồ sơ",
            "đăng ký đất đai",
            # Không dấu
            "hoi dong dang ky",
            "dang ky dat dai lan dau",
            "bien ban hoi dong",
            "hoi dong",
            "dang ky lan dau",
            "xet ho so",
            "dang ky dat dai"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBNT": {
        "keywords": [
            # Có dấu
            "biên bản nghiệm thu",
            "nghiệm thu công trình",
            "kiểm tra nghiệm thu",
            "nghiệm thu",
            "hội đồng nghiệm thu",
            "xác nhận hoàn thành",
            "đạt yêu cầu",
            # Không dấu
            "bien ban nghiem thu",
            "nghiem thu cong trinh",
            "kiem tra nghiem thu",
            "nghiem thu",
            "hoi dong nghiem thu",
            "xac nhan hoan thanh",
            "dat yeu cau"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBKTSS": {
        "keywords": [
            # Có dấu
            "kiểm tra sai sót",
            "sai sót trên giấy chứng nhận",
            "biên bản kiểm tra",
            "sai sót",
            "phát hiện sai sót",
            "chỉnh sửa thông tin",
            "sai sót trên gcn",
            # Không dấu
            "kiem tra sai sot",
            "sai sot tren giay chung nhan",
            "bien ban kiem tra",
            "sai sot",
            "phat hien sai sot",
            "chinh sua thong tin",
            "sai sot tren gcn"
        ],
        "weight": 1.0,
        "min_matches": 1
    },
    "BBKTHT": {
        "keywords": [
            # Có dấu
            "xác minh hiện trạng",
            "kiểm tra hiện trạng",
            "sử dụng đất hiện trạng",
            "hiện trạng",
            "kiểm tra thực địa",
            "hiện trạng sử dụng",
            "xác minh",
            # Không dấu
            "xac minh hien trang",
            "kiem tra hien trang",
            "su dung dat hien trang",
            "hien trang",
            "kiem tra thuc dia",
            "hien trang su dung",
            "xac minh"
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

def classify_by_rules(text: str, confidence_threshold: float = 0.3) -> Dict[str, any]:
    """
    Classify document based on keyword rules
    
    Args:
        text: Extracted text from OCR
        confidence_threshold: Minimum confidence to accept (default 0.3)
        
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
            # Give bonus for multiple matches
            base_score = (len(matched) / len(keywords)) * weight
            bonus = min(len(matched) * 0.1, 0.3)  # Bonus for multiple keywords
            score = min(base_score + bonus, 1.0)
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
    
    # Use threshold parameter
    if confidence < confidence_threshold:
        return {
            "type": "UNKNOWN",
            "confidence": confidence,
            "method": "rules_low_conf",
            "matched_keywords": matched_keywords_all.get(best_type, []),
            "best_guess": best_type  # Include best guess for debugging
        }
    
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


class RuleClassifier:
    """
    Rule-based classifier wrapper class
    """
    
    def __init__(self):
        """Initialize classifier"""
        pass
    
    def classify(self, text: str) -> dict:
        """
        Classify document using rules
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Dict with doc_type, confidence, short_code, reasoning
        """
        result = classify_by_rules(text, confidence_threshold=0.3)
        
        doc_type_code = result.get('type', 'UNKNOWN')
        confidence = result.get('confidence', 0.0)
        
        return {
            'doc_type': classify_document_name_from_code(doc_type_code),
            'short_code': doc_type_code,
            'confidence': confidence,
            'reasoning': f"Matched keywords: {', '.join(result.get('matched_keywords', []))}"
        }

