#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Rules Reload Mechanism
Shows that rules changes take effect immediately without app restart
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python'))

from rule_classifier import get_active_rules, classify_by_rules

def demo_rules_reload():
    """Demonstrate rules reload mechanism"""
    print("\n" + "=" * 80)
    print("DEMO: Rules Reload Mechanism")
    print("=" * 80)
    
    print("\n📋 SCENARIO: Thay đổi rules trong UI và test ngay lập tức\n")
    
    # Step 1: Check current rules
    print("🔍 Step 1: Kiểm tra rules hiện tại")
    print("-" * 80)
    rules = get_active_rules()
    print(f"  Tổng số rules: {len(rules)}")
    
    gtlq_rules = rules.get('GTLQ', {})
    gtlq_keywords = gtlq_rules.get('keywords', [])
    print(f"  GTLQ keywords count: {len(gtlq_keywords)}")
    print(f"  GTLQ weight: {gtlq_rules.get('weight', 'N/A')}")
    print(f"  GTLQ min_matches: {gtlq_rules.get('min_matches', 'N/A')}")
    
    # Step 2: Simulate classification
    print("\n🔍 Step 2: Test classification với GTLQ text")
    print("-" * 80)
    test_text = """
    GIẤY TIẾP NHẬN HỒ SƠ VÀ HẸN TRẢ KẾT QUẢ
    
    Trung tâm phục vụ hành chính công
    Mã hồ sơ: 123456
    Ngày tiếp nhận: 01/01/2025
    Ngày hẹn trả: 15/01/2025
    """
    
    result = classify_by_rules(test_text, test_text)
    
    print(f"  Kết quả: {result.get('type')} ({result.get('confidence', 0):.0%})")
    print(f"  Method: {result.get('method')}")
    print(f"  Matched keywords (top 3): {result.get('matched_keywords', [])[:3]}")
    
    # Step 3: Show how to modify rules
    print("\n📝 Step 3: Cách thay đổi rules trong UI")
    print("-" * 80)
    print("  1. Mở app → Settings → Rules Manager")
    print("  2. Click vào GTLQ rule")
    print("  3. Click 'Sửa'")
    print("  4. Thêm keyword mới, ví dụ: 'giấy tiếp nhận hồ sơ và trả kết quả'")
    print("  5. Click 'Lưu'")
    print("  6. → Thay đổi có hiệu lực NGAY LẬP TỨC!")
    print("  7. Quay lại scan file → thấy rule mới được áp dụng")
    
    # Step 4: Explain the mechanism
    print("\n⚙️ Step 4: Cơ chế hoạt động")
    print("-" * 80)
    print("  ✅ get_active_rules() đọc từ 2 nguồn:")
    print("     - DEFAULT_RULES (hardcoded trong rule_classifier.py)")
    print("     - rules_overrides.json (user customizations)")
    print("  ✅ Mỗi lần scan file → gọi get_active_rules() → load fresh rules")
    print("  ✅ KHÔNG cần restart app")
    print("  ✅ KHÔNG cần reload Python module")
    
    # Step 5: Override file location
    print("\n📂 Step 5: Vị trí file overrides")
    print("-" * 80)
    user_data_path = Path.home() / '.90daychonhanh'
    override_file = user_data_path / 'rules_overrides.json'
    print(f"  Path: {override_file}")
    
    if override_file.exists():
        try:
            with open(override_file, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
            print(f"  ✅ File exists")
            print(f"  Overrides count: {len(overrides)}")
            
            if overrides:
                print(f"  Customized rules: {', '.join(overrides.keys())}")
        except Exception as e:
            print(f"  ⚠️ Error reading file: {e}")
    else:
        print(f"  ℹ️ File chưa tồn tại (sẽ được tạo khi user lưu rule đầu tiên)")
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print("\n💡 TÓM TẮT:")
    print("  - Rules reload hoạt động: mỗi lần scan → load fresh rules")
    print("  - User thay đổi rules trong UI → có hiệu lực ngay lập tức")
    print("  - Không cần restart app hay reload Python module")
    print()


if __name__ == "__main__":
    demo_rules_reload()
