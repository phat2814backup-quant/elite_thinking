# Kế Hoạch Nâng Cấp: Phân Rã Thực Chiến & Võ Đài Đối Kháng Socrates

Tài liệu này tổng hợp toàn bộ phương án kỹ thuật và luồng trải nghiệm người dùng để chốt nâng cấp module **Phân Rã Thực Chiến & Nhật Ký Quyết Định** theo đúng kiến trúc nhận thức chuẩn: **3 Trụ Cột Định Tuyến ➔ 9 Lăng Kính Tinh Hoa ➔ 152 Mô Hình Thực Chứng ➔ 3 Mũi Giáo Socrates Đối Kháng**.

---

## 🏛️ Kiến Trúc Tổng Thể: Khung Đồng Bộ Chuẩn 100%

Hệ thống phân rã sẽ được cấu trúc thành **3 Trụ Cột** đồng nhất với Lâu Đài Ký Ức Dave Farrow (`Topic 1: The Farrow Trinity`) và phân bổ chính xác **9 Lăng Kính**:

```
                                ┌─────────────────────────────────────────────────────────────┐
                                │          KHO 152 MÔ HÌNH TINH HOA (GROUND TRUTHS)           │
                                └──────────────────────────────┬──────────────────────────────┘
                                                               │ (Lọc & Chiếu xạ)
                                                               ▼
        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │                                        3 TRỤ CỘT ĐỊNH TUYẾN & 9 LĂNG KÍNH                                   │
        ├──────────────────────────────────────┬──────────────────────────────────────┬───────────────────────────────┤
        │ 💎 TRỤ 1: SOI GỐC (ROOT)             │ 🔭 TRỤ 2: ĐỌC DÒNG (FLOW)            │ 🏹 TRỤ 3: RA ĐÒN (STRIKE)      │
        ├──────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────┤
        │ 1. First Principles (Nguyên lý gốc)  │ 4. Xác suất Bayes (Cập nhật dữ liệu) │ 7. Bất đối xứng Barbell (Taleb)│
        │ 2. Inversion (Tư duy đảo ngược)      │ 5. Tư duy Bậc hai (Second-Order)     │ 8. Thử nghiệm Tinh gọn (Lean) │
        │ 3. Latticework (Lưới đa ngành)       │ 6. Game Theory (Đọc vị đối thủ)      │ 9. Đa quy mô thời gian (10 năm│
        └──────────────────────────────────────┴──────────────────────────────────────┴───────────────────────────────┘
                                                               │
                                                               ▼
        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │                              VÕ ĐÀI ĐỐI KHÁNG SOCRATES (3 MŨI GIÁO SÁT THỦ)                                 │
        ├──────────────────────────────────────┬──────────────────────────────────────┬───────────────────────────────┤
        │ 🗡️ Mũi 1: Truy sát Giả định & Bẫy Chết│ 🗡️ Mũi 2: Truy sát Xác suất & Phản ứng│ 🗡️ Mũi 3: Truy sát Rủi ro tối│
        │    vật lý (Soi Gốc)                  │    dây chuyền đối thủ (Đọc Dòng)     │    đa & Thử nghiệm (Ra Đòn)   │
        └──────────────────────────────────────┴──────────────────────────────────────┴───────────────────────────────┘
```

---

## 🛠️ Quy Trình 3 Bước Triển Khai Thực Tế

### Bước 1: Bơm Kho 152 Mô Hình vào Bộ Máy Phân Rã (`core/problem_decomposition.py`)
- Kết nối trực tiếp với `load_unified_farrow_catalog()` từ `core/models_engine.py`.
- Khi người dùng nhập vấn đề, AI sẽ quét toàn bộ vấn đề và:
  - Phân bổ phân tích vào **đúng 3 Trụ Cột (Soi Gốc - Đọc Dòng - Ra Đòn)**, mỗi Trụ Cột phân tích đủ **3 Lăng Kính**.
  - Ở mỗi lăng kính, AI **chỉ đích danh mã ID và tên mô hình từ Kho 152** (ví dụ: `[SYS-04: Theory of Constraints]`, `[MATH-05: Inversion]`, `[PSY-03: Principal-Agent]`).
  - Sinh ra **3 Mũi Giáo Socrates cực kỳ sắc bén** (1 câu về Gốc, 1 câu về Dòng, 1 câu về Đòn).

### Bước 2: Thiết Kế Lại Giao Diện Hiển Thị Trực Quan (`core/ui_rooms.py`)
- **Phần 1: Thẻ Tóm Tắt Tối Thượng (Executive Synthesis)**
  - Tóm tắt chân lý gốc rễ trong 2 câu đanh thép.
  - Các mã mô hình được kích hoạt hiển thị dưới dạng badge tương tác (click xem định nghĩa nhanh).
- **Phần 2: 3 Tab Trụ Cột (3 Pillars Accordion / Tabs)**
  - Tab 1: 💎 **TRỤ 1: SOI GỐC** (First Principles + Inversion + Latticework)
  - Tab 2: 🔭 **TRỤ 2: ĐỌC DÒNG** (Bayes + Bậc hai + Game Theory)
  - Tab 3: 🏹 **TRỤ 3: RA ĐÒN** (Barbell + Thử nghiệm Lean + Đa quy mô thời gian)
  - Dưới mỗi Trụ Cột có đề xuất **Hành Động Đòn Bẩy cụ thể**.

### Bước 3: Tích Hợp "Võ Đài Đối Kháng Socrates" (Interactive Socratic Duel)
- Phía dưới bảng phân rã, mở ra khu vực đối kháng trực tiếp:
  - Hiển thị **3 Mũi Giáo Socrates (Chất vấn ngược chiều)**.
  - Người dùng có khung nhập liệu để phản hồi, giải trình hoặc bảo vệ lập luận của mình trước 3 mũi giáo.
  - Nút bấm: **`🥊 Tiếp Chiêu & Thẩm Định Sức Bền Nhận Thức`**.
  - AI chấm điểm:
    - Phân tích xem người dùng đã phá giải được mũi giáo hay vẫn mắc bẫy nhận thức.
    - Chấm điểm **+50 đến +150 XP Sức bền nhận thức (Cognitive Grit XP)** cộng thẳng vào Profile người chơi.
    - Lưu lại toàn bộ đoạn đối thoại Socrates vào Kho Lưu Trữ / Nhật Ký Quyết Định.

---

## 🧪 Kế Hoạch Kiểm Thử (Verification Plan)

### Kiểm Thử Backend
1. Chạy script test `scratch/test_decompose_socratic.py`:
   - Kiểm tra API Gemini sinh đúng cấu trúc JSON gồm 3 Trụ, 9 Lăng kính gắn mã mô hình `[ID]`, và 3 Mũi giáo Socrates.
   - Kiểm tra hàm đánh giá phản hồi Socrates (`evaluate_socratic_sparring`).
2. Chạy `scratch/test_compile_full_v2.py` để đảm bảo toàn bộ hệ thống biên dịch sạch 100%.

### Kiểm Thử Trực Quan (Manual Verification)
1. Thử phân rã 1 tình huống thực chiến (ví dụ: Case CKVN hoặc Sự nghiệp khởi nghiệp).
2. Kiểm tra giao diện 3 Tab Trụ Cột hiển thị rõ ràng, không lỗi font hay tràn layout.
3. Thử gõ câu trả lời vào 3 Mũi Giáo Socrates, bấm "Tiếp Chiêu" và kiểm tra AI phản hồi chấm điểm Cognitive Grit XP.
