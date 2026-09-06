# Extension: Case Thực Chiến

Thư mục chứa page mới + dữ liệu case để tích hợp vào app Elite Thinking.

## Cấu trúc

```
extension/
├── README.md
├── data/
│   ├── cases_toan_khoa_hoc.json      # A · 25 case Toán & Khoa học
│   ├── cases_hoc_tap_tu_duy.json     # B · 20 case Học tập & Siêu học
│   ├── cases_tai_chinh_ckvn.json     # C · 25 case Tài chính & CKVN
│   ├── cases_su_nghiep_quyet_dinh.json # D · 15 case Sự nghiệp & Quyết định
│   ├── cases_tam_ly_he_thong.json    # E · 15 case Tâm lý & Hệ thống
│   └── cases_elite_future.json       # F · 50 case Elite hiện tại & 10–20 năm
└── pages/
    └── 10_case_thuc_chien.py         # Page Streamlit (load cả 6 nhóm)
```

**Tổng: 150 case**

## Cách tích hợp

1. Copy `pages/10_case_thuc_chien.py` → `pages/` của app chính.
2. Copy toàn bộ file trong `data/` → `data/` của app chính (hoặc giữ nguyên nếu page trỏ đúng đường dẫn).
3. Đảm bảo import `utils.app_common.bootstrap` hoạt động (page đã có fallback).
4. Commit & push. Streamlit multipage tự nhận page mới.

## Tính năng page

- Filter theo nhóm (A–F), độ khó, nguyên lý, tìm kiếm.
- Mỗi case: vấn đề → câu hỏi kích hoạt → phân rã First Principles → nguyên lý → bước giải → biến thể → Elite Insight.
- Nút chuẩn bị nội dung đưa sang tab Phân Rã AI 9 Lenses.
- Sidebar tổng quan số case từng nhóm.

## Ghi chú

- Cấu trúc JSON thống nhất với `metadata.group` + `cases[]`.
- Page tự động load mọi file `cases_*.json` theo map trong code.
- Có thể bổ sung case mới bằng cách sửa/thêm JSON, không cần sửa page (trừ khi thêm nhóm mới).
