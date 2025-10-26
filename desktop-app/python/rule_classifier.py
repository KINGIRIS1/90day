"""
COMPLETE Rule-based classifier for Vietnamese land documents
95 document types with full Vietnamese keyword support
"""
import re
from typing import Dict, Tuple

# COMPLETE Document type rules - 95 types
DOCUMENT_RULES = {
    "GCNM": {
        "keywords": [
            # Có dấu
            "giấy chứng nhận quyền sử dụng đất", "giấy chứng nhận", "giầy chứng nhận",
            "quyền sử dụng đất", "quyền sở hữu", "tài sản gắn liền",
            "cộng hòa xã hội chủ nghĩa việt nam", "độc lập tự do hạnh phúc",
            "chi nhánh văn phòng đăng ký", "văn phòng đăng ký đất đai",
            "chứng nhan", "chứng nhận",  # OCR common typos
            # Không dấu
            "giay chung nhan", "giay chung nhan", "quyen su dung dat", "quyen so huu",
            "tai san gan lien", "cong hoa xa hoi chu nghia viet nam",
            "doc lap tu do hanh phuc", "van phong dang ky dat dai",
            "chung nhan"  # OCR common typo without diacritics
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
            "ban ve thi cong", "hoan thanh thi cong"
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
            "mat bang", "mat tien", "mat cat"
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
            "ke khai dat dai", "ke khai dien tich"
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
            "liet ke", "bang liet ke"
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
            "hoi dong dau gia", "trung dau gia"
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
            "ban giao thuc dia", "giao nhan"
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
            "bien ban hoi dong", "dang ky lan dau"
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
            "kiem tra nghiem thu", "hoi dong nghiem thu"
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
            "bien ban kiem tra", "chinh sua thong tin"
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
            "su dung dat hien trang", "kiem tra thuc dia"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "BBKTDC": {
        "keywords": [
            # Có dấu
            "kết thúc công khai", "công bố di chúc", "biên bản di chúc",
            # Không dấu
            "ket thuc cong khai", "cong bo di chuc", "bien ban di chuc"
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
            "ket qua kiem tra", "cap gcn"
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
            "mat giay chung nhan"
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
            "bien lai nop thue"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "CCCD": {
        "keywords": [
            # Có dấu
            "căn cước công dân", "cccd", "thẻ căn cước", "căn cước",
            # Không dấu
            "can cuoc cong dan", "the can cuoc", "can cuoc",
            # Viết hoa
            "CAN CUOC CONG DAN", "CCCD", "THE CAN CUOC"
        ],
        "weight": 1.3, "min_matches": 1
    },
    "DS15": {
        "keywords": [
            # Có dấu
            "danh sách chủ sử dụng", "các thửa đất", "mẫu 15",
            # Không dấu
            "danh sach chu su dung", "cac thua dat", "mau 15"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DSCK": {
        "keywords": [
            # Có dấu
            "danh sách công khai", "hồ sơ cấp giấy", "cnqsdđ",
            # Không dấu
            "danh sach cong khai", "ho so cap giay", "cnqsdd"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DICHUC": {
        "keywords": [
            # Có dấu
            "di chúc", "lập di chúc", "người lập di chúc",
            # Không dấu
            "di chuc", "lap di chuc", "nguoi lap di chuc"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "DCK": {
        "keywords": [
            # Có dấu
            "đơn cam kết", "giấy cam kết", "cam kết",
            # Không dấu
            "don cam ket", "giay cam ket", "cam ket"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "DDKBD": {
        "keywords": [
            # Có dấu
            "đơn đăng ký biến động", "biến động đất đai",
            "tài sản gắn liền", "đăng ký biến động",
            "đơn đăng ký biến động đất đai",
            # Không dấu (OCR thường bỏ dấu)
            "don dang ky bien dong", "bien dong dat dai",
            "tai san gan lien", "dang ky bien dong",
            "don dang ky bien dong dat dai",
            # OCR common typos
            "dang ky bien dong", "bien dong",
            "đăng ký biến động đất",
            # Viết hoa (OCR thường đọc title là chữ hoa)
            "DON DANG KY BIEN DONG", "BIEN DONG DAT DAI",
            "DANG KY BIEN DONG"
        ],
        "weight": 1.2,  # Tăng weight để ưu tiên hơn GCNM
        "min_matches": 1
    },
    "DDK": {
        "keywords": [
            # Có dấu
            "đơn đăng ký đất đai", "đăng ký đất đai",
            "tài sản gắn liền với đất",
            # Không dấu
            "don dang ky dat dai", "dang ky dat dai",
            "tai san gan lien voi dat"
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
            "chuyen hinh thuc giao dat"
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
            "cho thue dat", "chuyen muc dich"
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
            "thue thu nhap ca nhan", "mien giam thue"
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
            "dat da muc dich"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "DXN": {
        "keywords": [
            # Có dấu
            "đơn xác nhận", "giấy xác nhận", "xác nhận",
            # Không dấu
            "don xac nhan", "giay xac nhan", "xac nhan"
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
            "chuyen muc dich su dung dat"
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
            "de nghi gia han"
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
            "don xin cho thue dat"
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
            "tach thua dat", "hop thua dat"
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
            "doi gcn"
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
            "du an dau tu", "dieu chinh thoi han"
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
            "dat nong nghiep", "xac nhan lai thoi han"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "GKH": {
        "keywords": [
            # Có dấu
            "giấy chứng nhận kết hôn", "kết hôn", "hôn nhân",
            # Không dấu
            "giay chung nhan ket hon", "ket hon", "hon nhan"
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
            "cac khoan nop", "xac nhan nop thue"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "GKS": {
        "keywords": [
            # Có dấu
            "giấy khai sinh", "khai sinh", "gks",
            # Không dấu
            "giay khai sinh", "khai sinh"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "GNT": {
        "keywords": [
            # Có dấu
            "giấy nộp tiền", "nộp vào ngân sách", "ngân sách nhà nước",
            # Không dấu
            "giay nop tien", "nop vao ngan sach", "ngan sach nha nuoc"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GSND": {
        "keywords": [
            # Có dấu
            "giấy sang nhượng đất", "sang nhượng", "chuyển nhượng đất",
            # Không dấu
            "giay sang nhuong dat", "sang nhuong", "chuyen nhuong dat"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GTLQ": {
        "keywords": [
            # Có dấu
            "giấy tờ liên quan", "tài liệu kèm theo",
            # Không dấu
            "giay to lien quan", "tai lieu kem theo"
        ],
        "weight": 0.6, "min_matches": 1
    },
    "GUQ": {
        "keywords": [
            # Có dấu
            "giấy ủy quyền", "ủy quyền", "người được ủy quyền",
            # Không dấu
            "giay uy quyen", "uy quyen", "nguoi duoc uy quyen"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GXNDKLD": {
        "keywords": [
            # Có dấu
            "giấy xác nhận đăng ký lần đầu", "đăng ký lần đầu",
            "xác nhận đăng ký",
            # Không dấu
            "giay xac nhan dang ky lan dau", "dang ky lan dau",
            "xac nhan dang ky"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "GPXD": {
        "keywords": [
            # Có dấu
            "giấy phép xây dựng", "phép xây dựng", "giấy phép",
            # Không dấu
            "giay phep xay dung", "phep xay dung", "giay phep"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "hoadon": {
        "keywords": [
            # Có dấu
            "hoá đơn", "hóa đơn", "gtgt", "giá trị gia tăng",
            # Không dấu
            "hoa don", "gia tri gia tang"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HTBTH": {
        "keywords": [
            # Có dấu
            "hoàn thành", "bồi thường hỗ trợ", "công tác bồi thường",
            # Không dấu
            "hoan thanh", "boi thuong ho tro", "cong tac boi thuong"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "HDCQ": {
        "keywords": [
            # Có dấu
            "hợp đồng chuyển nhượng", "hợp đồng tặng cho",
            "chuyển nhượng quyền", "tặng cho quyền",
            # Không dấu
            "hop dong chuyen nhuong", "hop dong tang cho",
            "chuyen nhuong quyen", "tang cho quyen"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDBDG": {
        "keywords": [
            # Có dấu
            "hợp đồng mua bán", "bán đấu giá", "tài sản đấu giá",
            # Không dấu
            "hop dong mua ban", "ban dau gia", "tai san dau gia"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDTHC": {
        "keywords": [
            # Có dấu
            "hợp đồng thế chấp", "thế chấp quyền", "thế chấp đất",
            # Không dấu
            "hop dong the chap", "the chap quyen", "the chap dat"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDTCO": {
        "keywords": [
            # Có dấu
            "hợp đồng thi công", "thi công xây dựng",
            # Không dấu
            "hop dong thi cong", "thi cong xay dung"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "HDTD": {
        "keywords": [
            # Có dấu
            "hợp đồng thuê đất", "thuê đất", "điều chỉnh hợp đồng",
            # Không dấu
            "hop dong thue dat", "thue dat", "dieu chinh hop dong"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "HDUQ": {
        "keywords": [
            # Có dấu
            "hợp đồng ủy quyền", "ủy quyền",
            # Không dấu
            "hop dong uy quyen", "uy quyen"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "PCT": {
        "keywords": [
            # Có dấu
            "phiếu chuyển thông tin", "nghĩa vụ tài chính",
            "chuyển thông tin",
            # Không dấu
            "phieu chuyen thong tin", "nghia vu tai chinh",
            "chuyen thong tin"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "PKTHS": {
        "keywords": [
            # Có dấu
            "phiếu kiểm tra", "kiểm tra hồ sơ",
            # Không dấu
            "phieu kiem tra", "kiem tra ho so"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "PLYKDC": {
        "keywords": [
            # Có dấu
            "phiếu lấy ý kiến", "khu dân cư", "ý kiến dân",
            # Không dấu
            "phieu lay y kien", "khu dan cu", "y kien dan"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "PXNKQDD": {
        "keywords": [
            # Có dấu
            "phiếu xác nhận", "kết quả đo đạc", "đo đạc",
            # Không dấu
            "phieu xac nhan", "ket qua do dac", "do dac"
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
            "quyen su dung dat"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DKTD": {
        "keywords": [
            # Có dấu
            "phiếu yêu cầu", "đăng ký thay đổi", "biện pháp bảo đảm",
            # Không dấu
            "phieu yeu cau", "dang ky thay doi", "bien phap bao dam"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "DKXTC": {
        "keywords": [
            # Có dấu
            "phiếu yêu cầu", "xóa đăng ký", "biện pháp bảo đảm",
            # Không dấu
            "phieu yeu cau", "xoa dang ky", "bien phap bao dam"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QR": {
        "keywords": [
            # Có dấu
            "mã qr", "quét mã", "qr code",
            # Không dấu
            "ma qr", "quet ma", "qr code"
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
            "chuyen muc dich su dung"
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
            "tach thua dat"
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
            "cho thue dat"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCGD": {
        "keywords": [
            # Có dấu
            "quyết định", "điều chỉnh quyết định", "giao đất",
            # Không dấu
            "quyet dinh", "dieu chinh quyet dinh", "giao dat"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCTH": {
        "keywords": [
            # Có dấu
            "quyết định", "điều chỉnh thời hạn", "dự án đầu tư",
            # Không dấu
            "quyet dinh", "dieu chinh thoi han", "du an dau tu"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDGH": {
        "keywords": [
            # Có dấu
            "quyết định", "gia hạn", "hết thời hạn",
            # Không dấu
            "quyet dinh", "gia han", "het thoi han"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDGTD": {
        "keywords": [
            # Có dấu
            "quyết định", "giao đất", "cho thuê đất",
            # Không dấu
            "quyet dinh", "giao dat", "cho thue dat"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "QDHG": {
        "keywords": [
            # Có dấu
            "quyết định", "hủy giấy chứng nhận", "hủy gcn",
            # Không dấu
            "quyet dinh", "huy giay chung nhan", "huy gcn"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "QDPDBT": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "bồi thường", "tái định cư",
            # Không dấu
            "quyet dinh", "phe duyet", "boi thuong", "tai dinh cu"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDDCQH": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "điều chỉnh quy hoạch",
            # Không dấu
            "quyet dinh", "phe duyet", "dieu chinh quy hoach"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "QDPDDG": {
        "keywords": [
            # Có dấu
            "quyết định", "phê duyệt", "đơn giá",
            # Không dấu
            "quyet dinh", "phe duyet", "don gia"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "QDTHA": {
        "keywords": [
            # Có dấu
            "quyết định", "thi hành án", "đơn yêu cầu",
            # Không dấu
            "quyet dinh", "thi hanh an", "don yeu cau"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "QDTH": {
        "keywords": [
            # Có dấu
            "quyết định", "thu hồi đất",
            # Không dấu
            "quyet dinh", "thu hoi dat"
        ],
        "weight": 1.1, "min_matches": 1
    },
    "QDHTSD": {
        "keywords": [
            # Có dấu
            "quyết định", "hình thức sử dụng đất",
            # Không dấu
            "quyet dinh", "hinh thuc su dung dat"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "QDXP": {
        "keywords": [
            # Có dấu
            "quyết định", "xử phạt", "vi phạm",
            # Không dấu
            "quyet dinh", "xu phat", "vi pham"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "SDTT": {
        "keywords": [
            # Có dấu
            "sơ đồ", "dự kiến tách thửa", "tách thửa",
            # Không dấu
            "so do", "du kien tach thua", "tach thua"
        ],
        "weight": 0.9, "min_matches": 1
    },
    "TBCNBD": {
        "keywords": [
            # Có dấu
            "thông báo", "cập nhật", "chỉnh lý", "biến động",
            # Không dấu
            "thong bao", "cap nhat", "chinh ly", "bien dong"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "CKDC": {
        "keywords": [
            # Có dấu
            "thông báo", "công bố", "công khai", "di chúc",
            # Không dấu
            "thong bao", "cong bo", "cong khai", "di chuc"
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
            "tien su dung dat"
        ],
        "weight": 1.0, "min_matches": 1
    },
    "TBMG": {
        "keywords": [
            # Có dấu
            "thông báo", "gcn bị mất", "niêm yết",
            # Không dấu
            "thong bao", "gcn bi mat", "niem yet"
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
            "cap gcn"
        ],
        "weight": 0.8, "min_matches": 3
    },
    "TBCKMG": {
        "keywords": [
            # Có dấu
            "thông báo", "niêm yết", "mất gcn",
            # Không dấu
            "thong bao", "niem yet", "mat gcn"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "HTNVTC": {
        "keywords": [
            # Có dấu
            "thông báo", "xác nhận", "hoàn thành", "nghĩa vụ tài chính",
            # Không dấu
            "thong bao", "xac nhan", "hoan thanh", "nghia vu tai chinh"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "TKT": {
        "keywords": [
            # Có dấu
            "tờ khai thuế", "trước bạ", "tncn", "tiền sử dụng đất",
            # Không dấu
            "to khai thue", "truoc ba", "tien su dung dat"
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
            "chuyen muc dich"
        ],
        "weight": 0.8, "min_matches": 1
    },
    "TTCG": {
        "keywords": [
            # Có dấu
            "tờ trình", "đăng ký đất đai", "ubnd xã",
            # Không dấu
            "to trinh", "dang ky dat dai", "ubnd xa"
        ],
        "weight": 0.8, "min_matches": 2
    },
    "CKTSR": {
        "keywords": [
            # Có dấu
            "văn bản", "cam kết", "tài sản riêng",
            # Không dấu
            "van ban", "cam ket", "tai san rieng"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "VBCTCMD": {
        "keywords": [
            # Có dấu
            "văn bản", "chấp thuận", "chuyển mục đích",
            # Không dấu
            "van ban", "chap thuan", "chuyen muc dich"
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
            "thue", "gop von"
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
            "phuong an su dung dat"
        ],
        "weight": 0.8, "min_matches": 3
    },
    "VBTK": {
        "keywords": [
            # Có dấu
            "văn bản", "thỏa thuận", "phân chia", "di sản", "thừa kế",
            # Không dấu
            "van ban", "thoa thuan", "phan chia", "di san", "thua ke"
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
            "ho gia dinh"
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
            "thua dat lien ke"
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
            "thua dat lien ke"
        ],
        "weight": 0.9, "min_matches": 3
    },
    "VBTC": {
        "keywords": [
            # Có dấu
            "văn bản", "từ chối", "nhận di sản", "thừa kế",
            # Không dấu
            "van ban", "tu choi", "nhan di san", "thua ke"
        ],
        "weight": 0.9, "min_matches": 2
    },
    "PCTSVC": {
        "keywords": [
            # Có dấu
            "văn bản", "phân chia", "tài sản chung", "vợ chồng",
            # Không dấu
            "van ban", "phan chia", "tai san chung", "vo chong"
        ],
        "weight": 0.9, "min_matches": 2
    }
}


def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for matching"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def classify_by_rules(text: str, title_text: str = None, confidence_threshold: float = 0.3) -> Dict:
    """
    Classify document using rules with Vietnamese keywords
    
    Args:
        text: Full OCR text
        title_text: Text extracted from large fonts (titles/headers) - gets 2x priority
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        Classification result with type, confidence, and matched keywords
    """
    text_normalized = normalize_text(text)
    title_normalized = normalize_text(title_text) if title_text else ""
    
    scores = {}
    matched_keywords_dict = {}
    title_boost_applied = {}
    
    for doc_type, rules in DOCUMENT_RULES.items():
        keywords = rules["keywords"]
        weight = rules.get("weight", 1.0)
        min_matches = rules.get("min_matches", 1)
        
        matched = []
        title_matches = 0
        
        for keyword in keywords:
            keyword_normalized = normalize_text(keyword)
            
            # Check if keyword is in title (large font) - gets 2x weight
            if title_normalized and keyword_normalized in title_normalized:
                matched.append(f"{keyword} [TITLE]")
                title_matches += 1
            # Check if keyword is in full text
            elif keyword_normalized in text_normalized:
                matched.append(keyword)
        
        if len(matched) >= min_matches:
            # Base score from matched keywords
            base_score = len(matched) * weight
            
            # Boost score for title matches (2x multiplier)
            title_boost = title_matches * weight * 2.0
            
            # Final score = base + title boost
            score = base_score + title_boost
            
            scores[doc_type] = score
            matched_keywords_dict[doc_type] = matched
            title_boost_applied[doc_type] = title_matches > 0
    
    if not scores:
        return {
            "type": "UNKNOWN",
            "confidence": 0.0,
            "matched_keywords": [],
            "title_boost": False
        }
    
    best_type = max(scores, key=scores.get)
    max_score = scores[best_type]
    
    # Calculate confidence with title boost consideration
    total_possible_score = len(DOCUMENT_RULES[best_type]["keywords"]) * DOCUMENT_RULES[best_type]["weight"]
    confidence = min(max_score / (total_possible_score * 2), 1.0) if total_possible_score > 0 else 0.0
    
    # Boost confidence if title matches found
    if title_boost_applied.get(best_type, False):
        confidence = min(confidence * 1.2, 1.0)  # 20% confidence boost for title matches
    
    return {
        "type": best_type,
        "confidence": confidence,
        "matched_keywords": matched_keywords_dict[best_type],
        "title_boost": title_boost_applied.get(best_type, False)
    }


def classify_document_name_from_code(short_code: str) -> str:
    """Get full document name from short code"""
    code_to_name = {
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
        "GTLQ": "Giấy tờ liên quan (các loại giấy tờ kèm theo)",
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
        "VBDNCT": "Văn bản đề nghị chấp thuận nhận chuyển nhượng",
        "PDPASDD": "Văn bản đề nghị thẩm định, phê duyệt phương án sdđ",
        "VBTK": "Văn bản thỏa thuận phân chia di sản thừa kế",
        "TTHGD": "Văn bản thỏa thuận quyền sử dụng đất của hộ gia đình",
        "CDLK": "Văn bản thoả thuận về việc chấm dứt quyền hạn chế",
        "HCLK": "Văn bản thỏa thuận về việc xác lập quyền hạn chế",
        "VBTC": "Văn bản từ chối nhận di sản thừa kế",
        "PCTSVC": "Văn bản phân chia tài sản chung vợ chồng"
    }
    return code_to_name.get(short_code, "Không rõ loại tài liệu")


class RuleClassifier:
    """Rule-based classifier wrapper class"""
    
    def __init__(self):
        pass
    
    def classify(self, text: str, title_text: str = None) -> dict:
        """
        Classify document using rules with optional title text priority
        
        Args:
            text: Full OCR text
            title_text: Text from large fonts (titles/headers) - gets priority in matching
            
        Returns:
            Classification result with doc_type, confidence, and reasoning
        """
        result = classify_by_rules(text, title_text=title_text, confidence_threshold=0.3)
        
        doc_type_code = result.get('type', 'UNKNOWN')
        confidence = result.get('confidence', 0.0)
        title_boost = result.get('title_boost', False)
        
        # Build reasoning with title boost indicator
        reasoning_parts = []
        if result.get('matched_keywords'):
            reasoning_parts.append(f"Matched keywords: {', '.join(result.get('matched_keywords', []))}")
        if title_boost:
            reasoning_parts.append("✓ Title detection boosted confidence")
        
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No keywords matched"
        
        return {
            'doc_type': classify_document_name_from_code(doc_type_code),
            'short_code': doc_type_code,
            'confidence': confidence,
            'reasoning': reasoning,
            'title_boost': title_boost
        }
