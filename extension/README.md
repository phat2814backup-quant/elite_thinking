# Extension: Case Thực Chiến

Thư mục này chứa page mới + dữ liệu để tích hợp vào app Elite Thinking.

## Cấu trúc

```
extension/
├── README.md
├── data/
│   └── cases_toan_khoa_hoc.json   # 25 case nhóm A (Toán & Khoa học)
└── pages/
    └── 10_case_thuc_chien.py      # Page Streamlit mới
```

## Cách tích hợp vào app chính

1. Copy `pages/10_case_thuc_chien.py` → vào thư mục `pages/` của app chính.
2. Copy `data/cases_toan_khoa_hoc.json` → vào thư mục `data/` của app chính (hoặc giữ nguyên đường dẫn tương đối nếu muốn).
3. Đảm bảo page vẫn import được `from utils.app_common import bootstrap` (đã có try/except fallback).
4. Commit & push. Streamlit multipage sẽ tự nhận page mới theo tên file.

## Ghi chú

- Hiện tại chỉ có **nhóm A** (25 case).
- Các nhóm tiếp theo (B–E + F Elite 10–20 năm) sẽ bổ sung bằng file JSON riêng hoặc gộp vào loader.
- Page có filter theo độ khó, nguyên lý, tìm kiếm; có nút chuẩn bị nội dung để đưa sang tab Phân Rã AI.

## Phát triển tiếp

- Thêm `cases_elite_future.json` (~50 case).
- Thêm tracking đã làm case nào (dùng user_histories).
- Mode song ngữ hoặc persona (trẻ / người lớn).
