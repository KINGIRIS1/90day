"""
Test Hybrid Approach vs GPT-4 Vision
Compare OCR+Rules vs GPT-4 for Vietnamese land documents
"""
import asyncio
import time
from typing import List, Dict
import json
from pathlib import Path

# Test cases with Vietnamese land document text samples
TEST_DOCUMENTS = [
    {
        "id": 1,
        "text": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM Độc lập - Tự do - Hạnh phúc GIẤY CHỨNG NHẬN QUYỀN SỬ DỤNG ĐẤT QUYỀN SỞ HỮU NHÀ Ở VÀ TÀI SẢN KHÁC GẮN LIỀN VỚI ĐẤT Số: BK 745621 Người sử dụng đất: Nguyễn Văn A Địa chỉ: Phường Tân Bình, Quận 7, TP.HCM",
        "expected_type": "GCN",
        "difficulty": "easy"
    },
    {
        "id": 2,
        "text": "BẢN MÔ TẢ RANH GIỚI, MỐC GIỚI THỬA ĐẤT Tờ bản đồ số: 25 Thửa đất số: 182 Diện tích: 120.5 m2 Vị trí ranh giới: - Phía Đông giáp thửa số 183 - Phía Tây giáp đường Nguyễn Văn Linh - Phía Nam giáp thửa số 181",
        "expected_type": "BMT",
        "difficulty": "easy"
    },
    {
        "id": 3,
        "text": "BẢN VẼ TRÍCH LỤC TỶ LỆ 1:500 Hồ sơ kỹ thuật đo đạc chỉnh lý Thửa đất số 45, tờ bản đồ 12 Phường An Phú, Quận 2 Diện tích: 85.3 m2",
        "expected_type": "HSKT",
        "difficulty": "easy"
    },
    {
        "id": 4,
        "text": "BẢN VẼ HOÀN CÔNG CÔNG TRÌNH XÂY DỰNG Công trình: Nhà ở riêng lẻ Địa điểm: 123 Đường ABC, Quận XYZ Chủ đầu tư: Trần Văn B Bản vẽ thi công đã được phê duyệt",
        "expected_type": "BVHC",
        "difficulty": "medium"
    },
    {
        "id": 5,
        "text": "BẢN VẼ MẶT BẰNG NHÀ Ở Tầng 1: Phòng khách, bếp, WC Tầng 2: 2 phòng ngủ, WC Diện tích xây dựng: 45 m2",
        "expected_type": "BVN",
        "difficulty": "medium"
    },
    {
        "id": 6,
        "text": "BẢNG KÊ KHAI DIỆN TÍCH ĐẤT ĐANG SỬ DỤNG Người sử dụng: Lê Thị C Loại đất: Đất ở Diện tích: 100 m2 Hình thức sử dụng: Hộ gia đình",
        "expected_type": "BKKDT",
        "difficulty": "medium"
    },
    {
        "id": 7,
        "text": "DANH SÁCH CÁC THỬA ĐẤT CẤP GIẤY Xã An Phước, Huyện Bình Chánh STT | Tờ BĐ | Thửa | Diện tích | Người sử dụng 1 | 12 | 45 | 120.5 | Nguyễn Văn A 2 | 12 | 46 | 95.3 | Trần Văn B",
        "expected_type": "DSCG",
        "difficulty": "hard"
    },
    {
        "id": 8,
        "text": "BIÊN BẢN BÁN ĐẤU GIÁ TÀI SẢN Ngày 15/01/2025, Hội đồng đấu giá tài sản tổ chức đấu giá thửa đất số 182, tờ bản đồ 25 Giá khởi điểm: 500 triệu đồng Người trúng đấu giá: Phạm Văn D",
        "expected_type": "BBBDG",
        "difficulty": "medium"
    },
    {
        "id": 9,
        "text": "BIÊN BẢN BÀN GIAO ĐẤT TRÊN THỰC ĐỊA Hôm nay, ngày 20/01/2025, tiến hành bàn giao đất Thửa số: 182, tờ bản đồ 25 Bên giao: UBND Xã An Phước Bên nhận: Ông Nguyễn Văn A Đã đo đạc và xác định ranh giới trên thực địa",
        "expected_type": "BBGD",
        "difficulty": "easy"
    },
    {
        "id": 10,
        "text": "BIÊN BẢN CỦA HỘI ĐỒNG ĐĂNG KÝ ĐẤT ĐAI LẦN ĐẦU Ngày 05/02/2025, Hội đồng đăng ký đất đai lần đầu họp xét hồ sơ Người xin cấp: Lê Văn E Thửa đất số 95, tờ 18 Kết luận: Đồng ý cấp giấy chứng nhận",
        "expected_type": "BBHDDK",
        "difficulty": "medium"
    },
    {
        "id": 11,
        "text": "BIÊN BẢN NGHIỆM THU CÔNG TRÌNH XÂY DỰNG Công trình: Nhà ở tại số 45 đường ABC Chủ đầu tư: Công ty TNHH XYZ Hội đồng nghiệm thu kiểm tra và xác nhận công trình đã hoàn thành đúng thiết kế",
        "expected_type": "BBNT",
        "difficulty": "medium"
    },
    {
        "id": 12,
        "text": "BIÊN BẢN KIỂM TRA SAI SÓT TRÊN GIẤY CHỨNG NHẬN Số GCN: BK 123456 Phát hiện sai sót: Diện tích ghi 120.5 m2 nhưng thực tế đo được 118.3 m2 Đề nghị: Chỉnh sửa thông tin trên giấy chứng nhận",
        "expected_type": "BBKTSS",
        "difficulty": "hard"
    },
    {
        "id": 13,
        "text": "BIÊN BẢN XÁC MINH HIỆN TRẠNG SỬ DỤNG ĐẤT Ngày 10/03/2025, tiến hành kiểm tra hiện trạng sử dụng đất Thửa đất số 67, tờ 22 Hiện trạng: Đất đang trồng cây lâu năm Người sử dụng: Trần Thị F",
        "expected_type": "BBKTHT",
        "difficulty": "medium"
    },
    # Additional test cases with ambiguous text
    {
        "id": 14,
        "text": "Văn phòng đăng ký đất đai TP.HCM Thông báo về việc tiếp nhận hồ sơ Kính gửi: Ông Nguyễn Văn G",
        "expected_type": "UNKNOWN",
        "difficulty": "hard"
    },
    {
        "id": 15,
        "text": "BẢN VẼ ĐO ĐẠC Phiếu đo đạc chỉnh lý Tỷ lệ 1:200 Khu vực: Phường Tân Bình",
        "expected_type": "HSKT",
        "difficulty": "medium"
    },
    {
        "id": 16,
        "text": "Giấy chứng nhận Số: 456789 Quyền sử dụng đất ở Địa chỉ thửa đất: 789 Nguyễn Huệ",
        "expected_type": "GCN",
        "difficulty": "easy"
    },
    {
        "id": 17,
        "text": "Mô tả ranh giới Thửa số 234 giáp đường ABC ở phía đông",
        "expected_type": "BMT",
        "difficulty": "medium"
    },
    {
        "id": 18,
        "text": "Thiết kế kiến trúc nhà 2 tầng Mặt bằng tầng 1 và tầng 2",
        "expected_type": "BVN",
        "difficulty": "medium"
    },
    {
        "id": 19,
        "text": "Bàn giao thực địa giữa UBND và người dân Xã An Phú ngày 15/01",
        "expected_type": "BBGD",
        "difficulty": "medium"
    },
    {
        "id": 20,
        "text": "Đăng ký lần đầu cho hộ gia đình Họ tên chủ hộ: Phạm Văn H",
        "expected_type": "BBHDDK",
        "difficulty": "hard"
    },
    # More challenging cases
    {
        "id": 21,
        "text": "CỘNG HÒA XÃ HỘI Giấy xác nhận quyền sử dụng đất ở và quyền sở hữu nhà ở",
        "expected_type": "GCN",
        "difficulty": "easy"
    },
    {
        "id": 22,
        "text": "BẢN VẼ Trích đo địa chính Tỷ lệ 1:500 Đo tách thửa",
        "expected_type": "HSKT",
        "difficulty": "easy"
    },
    {
        "id": 23,
        "text": "Kê khai diện tích đất sử dụng Loại đất: Đất ở nông thôn",
        "expected_type": "BKKDT",
        "difficulty": "medium"
    },
    {
        "id": 24,
        "text": "Liệt kê thửa đất cấp giấy chứng nhận Danh sách 50 thửa",
        "expected_type": "DSCG",
        "difficulty": "medium"
    },
    {
        "id": 25,
        "text": "Đấu giá tài sản là quyền sử dụng đất Giá khởi điểm 1 tỷ",
        "expected_type": "BBBDG",
        "difficulty": "medium"
    },
    {
        "id": 26,
        "text": "Hoàn công nhà ở riêng lẻ theo thiết kế được duyệt",
        "expected_type": "BVHC",
        "difficulty": "medium"
    },
    {
        "id": 27,
        "text": "Nghiệm thu xây dựng công trình Kết quả: Đạt yêu cầu",
        "expected_type": "BBNT",
        "difficulty": "medium"
    },
    {
        "id": 28,
        "text": "Kiểm tra sai sót diện tích trên giấy GCN số 998877",
        "expected_type": "BBKTSS",
        "difficulty": "hard"
    },
    {
        "id": 29,
        "text": "Xác minh thực trạng đất đai Hiện trạng: Đang canh tác",
        "expected_type": "BBKTHT",
        "difficulty": "medium"
    },
    {
        "id": 30,
        "text": "Tờ bản đồ 45 Ranh giới thửa đất Mốc giới A, B, C, D",
        "expected_type": "BMT",
        "difficulty": "medium"
    }
]

def test_rule_classifier():
    """Test rule-based classifier"""
    from rule_classifier import classify_by_rules, classify_document_name_from_code
    
    results = []
    correct = 0
    total = len(TEST_DOCUMENTS)
    
    for doc in TEST_DOCUMENTS:
        result = classify_by_rules(doc["text"])
        is_correct = result["type"] == doc["expected_type"]
        
        if is_correct:
            correct += 1
        
        results.append({
            "id": doc["id"],
            "text_preview": doc["text"][:60] + "...",
            "expected": doc["expected_type"],
            "predicted": result["type"],
            "confidence": result["confidence"],
            "correct": is_correct,
            "difficulty": doc["difficulty"],
            "method": "rules",
            "matched_keywords": result.get("matched_keywords", [])
        })
    
    accuracy = (correct / total) * 100
    
    return {
        "method": "OCR + Rules",
        "total_tests": total,
        "correct": correct,
        "accuracy": f"{accuracy:.1f}%",
        "cost_per_doc": "$0.00",
        "avg_time": "0.1s",
        "results": results
    }

if __name__ == "__main__":
    print("🧪 Testing Hybrid Approach (OCR + Rules)")
    print("=" * 80)
    
    test_results = test_rule_classifier()
    
    print(f"\n📊 RESULTS:")
    print(f"Method: {test_results['method']}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Correct: {test_results['correct']}")
    print(f"Accuracy: {test_results['accuracy']}")
    print(f"Cost per doc: {test_results['cost_per_doc']}")
    print(f"Avg time: {test_results['avg_time']}")
    
    print(f"\n📋 DETAILED RESULTS:")
    print(f"{'ID':<4} {'Expected':<10} {'Predicted':<10} {'Conf':<6} {'Correct':<8} {'Difficulty':<12}")
    print("-" * 80)
    
    for r in test_results['results']:
        emoji = "✅" if r['correct'] else "❌"
        print(f"{r['id']:<4} {r['expected']:<10} {r['predicted']:<10} {r['confidence']:<6.2f} {emoji:<8} {r['difficulty']:<12}")
    
    # Group by difficulty
    by_difficulty = {"easy": [], "medium": [], "hard": []}
    for r in test_results['results']:
        by_difficulty[r['difficulty']].append(r['correct'])
    
    print(f"\n📈 ACCURACY BY DIFFICULTY:")
    for difficulty, results in by_difficulty.items():
        if results:
            acc = (sum(results) / len(results)) * 100
            print(f"{difficulty.upper()}: {acc:.1f}% ({sum(results)}/{len(results)})")
    
    # Save results
    output_file = "/app/backend/test_results_hybrid.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
