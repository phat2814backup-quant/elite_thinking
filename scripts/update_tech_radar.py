# -*- coding: utf-8 -*-
"""
Script chạy tự động định kỳ hàng tuần (Cron / GitHub Actions):
Quét và phân tích Top 10 dự án mã nguồn mở định hình tương lai bằng AI Scout.
Lưu thẳng vào data/tech_radar.json.
"""

import sys
import os
import datetime

# Thêm thư mục gốc vào sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.tech_radar import (
    load_tech_radar_data,
    generate_weekly_tech_radar_with_ai,
    get_current_iso_week_id,
    get_current_date_range_str
)


def main():
    print("=" * 60)
    print("🛰️ ELITE TECH RADAR — WEEKLY AUTO-UPDATE RUNNER")
    print(f"⏰ Thời gian thực thi: {datetime.datetime.now().isoformat()}")
    print("=" * 60)

    current_week_id = get_current_iso_week_id()
    date_range = get_current_date_range_str()
    print(f"🎯 Tuần mục tiêu: {current_week_id} ({date_range})")

    db = load_tech_radar_data()
    existing_weeks = [w.get("week_id") for w in db.get("weeks", [])]

    force = "--force" in sys.argv
    if current_week_id in existing_weeks and not force:
        print(f"✅ Tuần {current_week_id} đã tồn tại với đủ dữ liệu. Bỏ qua (hoặc dùng --force để tạo lại).")
        return 0

    print("🚀 Đang khởi động Elite AI Scout để phân tích Top 10 mã nguồn mở...")
    result = generate_weekly_tech_radar_with_ai(force_week_id=current_week_id)

    if result and "items" in result and len(result["items"]) > 0:
        print(f"🎉 Cập nhật thành công {len(result['items'])} dự án cho {current_week_id}:")
        for it in result["items"]:
            print(f"   - #{it.get('rank')}: {it.get('name')} [{it.get('category')}]")
        return 0
    else:
        print("⚠️ Không thể sinh dữ liệu tuần mới hoặc có lỗi xảy ra.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
