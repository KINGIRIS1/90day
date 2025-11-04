#!/usr/bin/env python3
"""
Test script to verify DCK classification pattern
"""

print("=" * 70)
print("TEST: DCK (GIẤY CAM KẾT) Classification Pattern")
print("=" * 70)

# Test titles that should match DCK
test_titles = [
    "GIẤY CAM KẾT",
    "GIẤY CAM KẾT\n(V/v chọn thửa đất để xác định trong hạn mức đất ở)",
    "ĐƠN CAM KẾT",
    "ĐƠN CAM KẾT\n(Về việc sử dụng đất đúng mục đích)",
    "GIẤY CAM KẾT\nCủa hộ gia đình về việc chọn thửa đất",
]

print("\n📋 Testing DCK keyword patterns:")
for i, title in enumerate(test_titles, 1):
    # Check if title matches DCK pattern
    has_giay = "GIẤY" in title.upper() or "ĐƠN" in title.upper()
    has_cam_ket = "CAM KẾT" in title.upper()
    
    matches = has_giay and has_cam_ket
    
    print(f"\n{i}. Title: {title[:60]}...")
    print(f"   • GIẤY/ĐƠN: {has_giay}")
    print(f"   • CAM KẾT: {has_cam_ket}")
    print(f"   → Classification: {'✅ DCK' if matches else '❌ NOT DCK'}")

print("\n" + "=" * 70)
print("EXPECTED RESULTS:")
print("=" * 70)
print("✅ All 5 test cases should match DCK pattern")
print("✅ Pattern: (GIẤY|ĐƠN) + CAM KẾT")
print("✅ Gemini Flash should return: short_code='DCK', confidence=0.85-0.92")
print("\n📌 User should scan real 'GIẤY CAM KẾT' document to verify")
print("=" * 70)
