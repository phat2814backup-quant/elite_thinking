# 🧠 ELITE THINKING FAMILY V2 — PROJECT CONTEXT & ARCHITECTURE SPEC

> **Dành cho AI Agent (Gemini, Claude, ChatGPT, Cursor, Windsurf, Antigravity...)**:
> Đây là tài liệu duy nhất chứa toàn bộ thông tin kiến trúc, vị trí source code, luồng ứng dụng, cơ sở dữ liệu và **tiến độ thực tế (cái gì đã xong, cái gì đang làm, cái gì chưa xong)** của dự án **Elite Thinking Family v2**.
> Đọc file này là Agent có 100% bối cảnh để bắt tay vào làm việc ngay mà không cần rà soát lại toàn bộ cây thư mục.

---

## 📌 1. THÔNG TIN TỔNG QUAN & METADATA DỰ ÁN

- **Tên Dự Án**: `Elite Thinking Family v2`
- **Mục đích**: Nền tảng huấn luyện tư duy tinh hoa (First Principles, Charlie Munger Mental Models, Richard Feynman Technique, Elon Musk Reasoning) dành cho Gia đình (Học sinh Wellspring K12 & Người lớn/Chuyên gia Tài chính/CKVN).
- **Công nghệ lõi**: Streamlit (Multipage Dynamic Router) + Google Gemini API (Multi-Key Failover) + Supabase PostgreSQL (Kèm Fallback Local JSON).
- **Thời điểm cập nhật**: `2026-09-07 14:20:08`
- **Git Repository**: `https://github.com/phat2814backup-quant/elite_thinking.git`
- **Git Branch**: `main`
- **Commit gần nhất**: `7509059 - feat(vocab): mastercraft Pillar 2 (Munger 88 Models) with 168 deep words across 42 topics (2026-09-07 12:38:22 +0700)`
- **Trạng thái Git**: `12 uncommitted file(s)`

---

## 🗺️ 2. VỊ TRÍ ỨNG DỤNG & CƠ CHẾ ROUTING

### 2.1 File khởi chạy chính (Entrypoint)
- **File**: `app.py`
- **Đường dẫn**: `app.py` (tại thư mục gốc)
- **Cơ chế hoạt động**:
  1. Gọi `utils.auth.init_auth_state()` khởi tạo phiên làm việc trên `st.session_state`.
  2. **Cổng bảo mật tiền đăng nhập (Pre-login Gate)**:
     - Khi chưa đăng nhập: Ẩn hoàn toàn sidebar navigation menu (`position='hidden'`), chỉ render form đăng nhập `render_login()`.
     - Khi đã đăng nhập: Khởi tạo router điều hướng động (`st.navigation`) hiển thị sidebar phân loại theo cụm nghiệp vụ.
  3. **Phân quyền vai trò (Role-Based Access Control - RBAC)**:
     - User thường: Chỉ thấy các trang học tập, luyện tập, tra cứu, sổ tay tri thức.
     - Role `admin`: Tự động kích hoạt thêm trang `pages/9_admin.py` trong menu `👑 Quản trị`.

### 2.2 Sơ đồ Cụm Trang Điều Hướng (Navigation Map)

| Cụm Danh Mục | Icon | File Trang | Chức Năng Chính | Quyền Hạn |
|---|---|---|---|---|
| **🧭 Định hướng** | 🧭 | `app.py` (Home) | Bản đồ 7 bước huấn luyện, 3 triết lý cốt lõi, chọn Track học tập | Mọi User |
| | 📅 | `pages/0_lo_trinh_12_tuan.py` | Lộ trình huấn luyện chuẩn 12 tuần, nhiệm vụ ngày/tuần, lưu tiến độ | Mọi User |
| **🧠 Lăng kính & Mô hình** | 🌐 | `pages/1_the_cuoc_elite.py` | 5 kỷ nguyên tiến hóa, 8 mật mã vận hành, AI Macro Radar | Mọi User |
| | 📖 | `pages/2_9_che_do_tu_duy.py` | 9 chế độ tư duy siêu việt (First Principles, Inversion, 2nd Order...) | Mọi User |
| | 🕸️ | `pages/3_88_mo_hinh.py` | 88 mô hình tâm trí Munger chia 6 trụ cột khoa học | Mọi User |
| | 📚 | `pages/4_thu_vien_nguyen_ly.py` | 100 định luật khoa học bất biến kèm tiêu chuẩn khả bác Karl Popper | Mọi User |
| **⚔️ Rèn luyện & Thực chiến**| ⚡ | `pages/5_dau_truong.py` | Flashcards 5s, 731 câu trắc nghiệm, Dynamic AI Quiz, Feynman Challenge | Mọi User |
| | 🎓 | `pages/6_dao_tao.py` | Bài tập tự luận đa tầng K12 Wellspring & Người lớn CKVN + AI Mentor | Mọi User |
| | 🚀 | `pages/7_phan_ra.py` | AI bóc tách vấn đề thực tế bằng 9 lăng kính, tìm đòn bẩy bất đối xứng | Mọi User |
| | 🎯 | `pages/11_case_thuc_chien.py` | Ngân hàng 150+ Case thực tế đa lĩnh vực (Toán, CKVN, Sự nghiệp...) | Mọi User |
| | 📝 | `pages/8_lich_su.py` | Nhật ký quyết định (Decision Journal), biểu đồ tiến bộ, lịch sử bài nộp | Mọi User |
| **💡 Sổ tay & Tri thức** | 💡 | `pages/10_so_tay_tri_thuc.py` | Sổ tay Second Brain ghi chú Markdown theo mô hình tư duy | Mọi User |
| | 🧬 | `pages/12_tieng_anh_elite.py` | Học từ vựng theo Gốc từ Lego (Latin/Hy Lạp), Mỏ neo thị giác, 100% Zero-API | Mọi User |
| **👑 Quản trị** | 👑 | `pages/9_admin.py` | Quản lý users, reset password, theo dõi lịch sử và telemetry toàn hệ thống | **Chỉ Admin** |

### 2.3 Các Module & Tiện ích Mở rộng (Extensions & Archive)
- **`extension/`**: Bản đóng gói case thực chiến 150+ độc lập (kèm file README hướng dẫn tích hợp vào repo khác).
- **`archive/`**: Thư mục lưu trữ mã nguồn tạm ngưng (`archive/pages/12_doc_song_ngu.py` - bản đọc sách song ngữ cũ) kèm `archive/README.md` ghi nhận lý do và định hướng phục hồi.
- **`extention_read_english/`**: Pipeline tiền xử lý sách (`bilingual_pipeline.py`) đọc PDF gốc đối chiếu tiếng Anh/Việt, làm sạch văn bản, phân đoạn Macro-Scenes.
### 2.4 Danh Mục Thư Viện Tiện Ích Lõi (`utils/`)

| Module File | Chức Năng Chính | Vai Trò Kỹ Thuật |
|---|---|---|
| `utils/ai_engine.py` | Giao tiếp Gemini API | Multi-key rotation, failover khi dính 429, cache phản hồi |
| `utils/app_common.py` | Shared bootstrap & Sidebar | Kiểm tra đăng nhập, nạp API keys, render sidebar dùng chung |
| `utils/auth.py` | Xác thực PBKDF2 & Phân quyền | Hash 200,000 vòng, đổi mật khẩu, đồng bộ Supabase & users.json |
| `utils/bilingual_manager.py`| Quản lý Đọc Song Ngữ | JIT rolling translation, căn chỉnh từng đoạn, cache dịch thuật |
| `utils/curriculum.py` | Quản lý Lộ trình 12 tuần | Tải nội dung tuần, lưu/đọc tiến độ hoàn thành theo user |
| `utils/daily_workout.py` | Rèn luyện Hàng ngày & Streak| Tính toán streak, câu hỏi khởi động ngày, bài tập vi mô |
| `utils/db.py` | Kết nối Supabase | Khởi tạo client Supabase, fallback an toàn sang local JSON |
| `utils/decision_journal.py`| Nhật ký Quyết định | Ghi chép bối cảnh, dự phóng, đánh giá hậu nghiệm các quyết định |
| `utils/diagnostic.py` | Trắc nghiệm Chẩn đoán | Đo lường thiên kiến nhận thức, phong cách tư duy của người học |
| `utils/knowledge.py` | Thư viện 100 Nguyên lý | Tải dữ liệu, tìm kiếm, lọc theo trường phái khoa học |
| `utils/macro_evolution.py` | Radar Thế cuộc & Kỷ nguyên | Phân tích 5 kỷ nguyên tiến hóa, 8 mật mã vận hành ngầm |
| `utils/mental_models.py` | 88 Mô hình Tâm trí Munger | Tải 88 mô hình, phân nhóm theo 6 trụ cột khoa học, tìm kiếm |
| `utils/notes_manager.py` | Second Brain / Sổ tay tri thức| CRUD ghi chú Markdown cá nhân, gắn thẻ theo mô hình tư duy |
| `utils/quiz_engine.py` | Ngân hàng 731 câu Trắc nghiệm| Sinh đề thi trắc nghiệm, chấm điểm, giải thích đáp án chi tiết |
| `utils/training.py` | Huấn luyện Đào tạo & AI Mentor| Chấm điểm bài tự luận K12/Adult, sinh phản biện First Principles |
| `utils/vocab_manager.py` | Quản lý Từ vựng Tinh hoa | Tải từ vựng tĩnh, theo dõi mastery, thống kê, zero-API |

---

## 💾 3. CƠ SỞ DỮ LIỆU & KIẾN TRÚC LƯU TRỮ (PERSISTENCE)

Dự án sử dụng cơ chế **Kiến trúc Kép (Dual Persistence Architecture)** đảm bảo app luôn chạy được cả khi có hoặc không có mạng/cloud database:
1. **Ưu tiên 1 (Production / Streamlit Cloud)**: **Supabase PostgreSQL**.
2. **Ưu tiên 2 (Local Development / Offline)**: **Local JSON**.

### 3.1 Cấu trúc Bảng Supabase PostgreSQL (`supabase/schema.sql`)

```sql
-- 1. Bảng người dùng (Tự quản lý Auth bằng PBKDF2, không phụ thuộc Supabase Auth)
create table if not exists public.app_users (
  username text primary key,
  password_hash text not null,       -- PBKDF2-HMAC-SHA256 (200,000 iterations, 16-byte salt)
  role text not null default 'user', -- 'admin' hoặc 'user'
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 2. Bảng lưu trữ toàn bộ lịch sử học tập của từng người dùng (Blob JSONB bền vững)
create table if not exists public.user_histories (
  username text primary key references public.app_users(username) on delete cascade,
  data jsonb not null default '{}'::jsonb,  -- analyses, training, quiz, diagnostic, decisions...
  updated_at timestamptz not null default now()
);
```

#### Các trường dữ liệu bên trong cột `data jsonb` của `user_histories`:
- `analyses`: Danh sách các phân tích vấn đề (Tab 7 Phân rã).
- `training_submissions`: Lịch sử bài nộp đào tạo có AI Mentor phản biện (Tab 6 Đào tạo).
- `quiz_history`: Lịch sử kết quả làm bài trắc nghiệm / flashcards (Tab 5 Đấu trường).
- `feynman_submissions`: Kết quả giải thích nguyên lý theo kỹ thuật Feynman.
- `diagnostic_history`: Kết quả kiểm tra trắc nghiệm thiên kiến nhận thức & phong cách tư duy.
- `decisions`: Nhật ký các quyết định quan trọng (Decision Journal).
- `daily_workouts`: Dữ liệu chuỗi rèn luyện ngày (Daily Streak).
- `curriculum_progress`: Tiến độ đánh dấu hoàn thành các tuần trong lộ trình 12 tuần.
- `notes`: Ghi chú cá nhân trong Sổ tay tri thức (Second Brain).
- `elite_vocab_mastery`: Trạng thái học và làm chủ từ vựng tinh hoa (đã thông suốt, gắn sao, số lần ôn, kết quả quiz) (Tab 12).

### 3.2 Cơ chế Lưu trữ Fallback Local JSON
Nếu không có `SUPABASE_URL` và `SUPABASE_KEY` trong môi trường:
- Danh sách tài khoản: Đọc và ghi trực tiếp vào `data/users.json`.
- Lịch sử từng người dùng: Đọc và ghi tại `data/histories/<username>.json` (được `.gitignore` bảo vệ).
- Thư viện điều phối: `utils/db.py`, `utils/auth.py`, `utils/app_common.py`.

### 3.3 Thống Kê Ngân Hàng Dữ Liệu Tĩnh (`data/`)
- **Tổng số Case Thực Chiến**: **152 cases** (chia làm 6 nhóm chuyên sâu):
  - `Nhóm F - Elite Hiện Tại & Tầm Nhìn 10–20 Năm Tới`: **50 case** (File: `cases_elite_future.json`, Đối tượng: Giới Tinh Hoa, Nhà Đầu Tư 8x & Thế Hệ Kế Cận (Next-Gen))
  - `Nhóm B - Học tập & Siêu học (Ultralearning)`: **20 case** (File: `cases_hoc_tap_tu_duy.json`, Đối tượng: 11-15 + người lớn tự học)
  - `Nhóm P - Tình Huống Thực Chiến Của Hội Đồng (User & Council Practice)`: **2 case** (File: `cases_practice_user.json`, Đối tượng: Giới Elite, Nhà đầu tư & Cha mẹ)
  - `Nhóm D - Sự nghiệp & Quyết định cuộc đời`: **15 case** (File: `cases_su_nghiep_quyet_dinh.json`, Đối tượng: Người lớn 8x + thanh niên sắp chọn nghề)
  - `Nhóm C - Tài chính cá nhân, CKVN & Đòn bẩy vốn`: **25 case** (File: `cases_tai_chinh_ckvn.json`, Đối tượng: Người lớn 8x – tầng lớp trung lưu Sài Gòn (chứng khoán, ngân hàng, đầu tư))
  - `Nhóm E - Tâm lý đám đông & Hệ thống xã hội`: **15 case** (File: `cases_tam_ly_he_thong.json`, Đối tượng: Cả trẻ lớn và người lớn)
  - `Nhóm A - Toán & Khoa học (Trẻ em trọng tâm)`: **25 case** (File: `cases_toan_khoa_hoc.json`, Đối tượng: 11-15 (sinh 2011-2015))
- **Số Mô hình Tâm trí Munger (`core_mental_models.json`)**: **88 mô hình**.
- **Số Định luật Khoa học (`knowledge_base.json`)**: **100 nguyên lý**.
- **Bài học Đào tạo (`lessons.json`)**: **100 bài học** phân bổ qua các track chuyên sâu:
  - `Lớp 6 (Wellspring)`: **13 bài học**
  - `Lớp 9 (Wellspring)`: **13 bài học**
  - `Lớp 10 (Wellspring)`: **13 bài học**
  - `Trading Vàng, FX, Crypto/BTC`: **13 bài học**
  - `Đầu tư Chứng khoán Việt Nam`: **12 bài học**
  - `Khoa học Não bộ & Nhận thức`: **12 bài học**
  - `Phật giáo & Tâm thức Ra quyết định`: **12 bài học**
  - `Công nghệ AI & Tương lai`: **12 bài học**
- **Từ Vựng Tư Duy Tinh Hoa (`data/elite_vocab.json`)**: **340 từ vựng cốt lõi** phân bổ trên **3 Cột trụ lớn** và **76 Chủ đề / Mô hình tư duy** kết nối 1-1 với Tab 2 (9 Chế độ), Tab 3 (88 Munger), Tab 4 (100 Nguyên lý) (Bóc tách gốc Lego Latinh/Hy Lạp, Mỏ neo thị giác, Cặp đối kháng, 100% Zero-API).
- **Sách Song Ngữ Siêu Học (`data/bilingual_books/`)**:
  - 📚 **Chuyện Thật Như Đùa (Richard P. Feynman)** (Tác giả: *Richard P. Feynman*): **40 chương**, **0 macro-scenes** căn chỉnh Anh - Việt (File: `feynman_surely_youre_joking.json`).

### 3.4 Chính Sách Bảo Mật & Thông Tin Nhạy Cảm (Security Rules)
> [!IMPORTANT]
> **TUYỆT ĐỐI TUÂN THỦ CÁC QUY TẮC BẢO MẬT SAU KHI LÀM VIỆC VỚI DỰ ÁN**:
> 1. **KHÔNG BAO GIỜ COMMIT** file `.env`, `secrets.toml`, hay bất kỳ credential nào vào Git.
> 2. **KHÔNG BAO GIỜ HARDCODE** API key hay password vào code. Mọi API key phải gọi qua `utils.app_common.get_configured_api_keys()`.
> 3. Mật khẩu người dùng được băm bằng PBKDF2-HMAC-SHA256 với Salt 16 bytes ngẫu nhiên và 200.000 vòng băm (`utils/auth.py`). Tuyệt đối không lưu mật khẩu dạng plain text.
> 4. File này (`PROJECT_CONTEXT.md`) và script xuất tự động đã lọc bỏ hoàn toàn các chuỗi mật khẩu, token, API keys, cookie và private data.

---

## 📊 4. TRẠNG THÁI & TIẾN ĐỘ DỰ ÁN (PROJECT STATUS & PROGRESS)

Bảng kiểm toán chi tiết tính năng giúp Agent nắm rõ: **Cái gì đã hoàn thành 100%, cái gì đang hoàn thiện, cái gì trong Backlog**.

### 4.1 Tính Năng Đã Hoàn Thành 100% & Ổn Định (Production Ready) ✅

| Phân Hệ | File Source Code | Trạng Thái | Mô Tả & Năng Lực Đã Đạt |
|---|---|---|---|
| **Multipage Router & Security Gate** | `app.py`, `utils/app_common.py` | ✅ Hoàn thành | Router động; ẩn menu khi chưa đăng nhập; phân quyền Admin/User; auto bootstrap; quản lý session state. |
| **Hệ thống Xác thực PBKDF2** | `utils/auth.py`, `supabase/schema.sql` | ✅ Hoàn thành | Băm mật khẩu 200,000 vòng; đổi mật khẩu an toàn; hỗ trợ đồng bộ cả Supabase và local `users.json`. |
| **Đồng bộ Dữ liệu Kép (Dual DB)** | `utils/db.py`, `supabase/schema.sql` | ✅ Hoàn thành | Tự động nhận diện Supabase Cloud; fallback mượt mà sang Local JSON; đồng bộ dữ liệu người dùng không gián đoạn. |
| **Xoay vòng Gemini API Keys** | `utils/app_common.py`, `utils/ai_engine.py` | ✅ Hoàn thành | Tự động luân chuyển đa key (`GEMINI_API_KEY_1..9`); tự động failover sang key kế tiếp khi gặp 429 Rate Limit. |
| **Lộ trình 12 Tuần** | `pages/0_lo_trinh_12_tuan.py`, `utils/curriculum.py` | ✅ Hoàn thành | Toàn bộ 12 tuần có bài học, mục tiêu, bài tập thực hành; lưu tiến độ từng user lên Supabase. |
| **Thế Cuộc & AI Radar** | `pages/1_the_cuoc_elite.py`, `utils/macro_evolution.py` | ✅ Hoàn thành | 5 kỷ nguyên, 8 mật mã, giao diện trực quan hóa, phân tích cục diện thời đại. |
| **9 Chế Độ Tư Duy** | `pages/2_9_che_do_tu_duy.py` | ✅ Hoàn thành | First Principles, Inversion, 2nd Order, Bayes, Đa quy mô thời gian, v.v. |
| **88 Mô Hình Munger** | `pages/3_88_mo_hinh.py`, `utils/mental_models.py` | ✅ Hoàn thành | Đầy đủ 6 nhóm khoa học; lọc theo nhóm; giải nghĩa chi tiết; ví dụ thực tiễn. |
| **Thư Viện 100 Nguyên Lý** | `pages/4_thu_vien_nguyen_ly.py`, `utils/knowledge.py` | ✅ Hoàn thành | 100 nguyên lý khoa học bất biến; công thức toán học; tiêu chuẩn khả bác Popper. |
| **Đấu Trường & Trắc Nghiệm** | `pages/5_dau_truong.py`, `utils/quiz_engine.py` | ✅ Hoàn thành | Flashcard 5s; 731 câu trắc nghiệm chuẩn; Dynamic AI Quiz; Thử thách Feynman; Daily Streak. |
| **Đào Tạo 2 Nhánh Gia Đình** | `pages/6_dao_tao.py`, `utils/training.py` | ✅ Hoàn thành | Track 1 K12 Wellspring (lớp 6, 9, 10); Track 2 Người lớn/CKVN; AI Mentor chấm điểm & phản biện. |
| **Phân Rã Vấn Đề Thực Chiến** | `pages/7_phan_ra.py`, `utils/ai_engine.py` | ✅ Hoàn thành | Nhập vấn đề bất kỳ; AI bóc tách qua 9 lăng kính; đề xuất giải pháp đòn bẩy bất đối xứng; lưu lịch sử. |
| **Lịch Sử & Nhật Ký Quyết Định** | `pages/8_lich_su.py`, `utils/decision_journal.py` | ✅ Hoàn thành | Decision Journal ghi chép & đánh giá quyết định; biểu đồ theo dõi chuỗi luyện tập và bài nộp. |
| **Trang Quản Trị Hệ Thống** | `pages/9_admin.py` | ✅ Hoàn thành | Chỉ admin thấy; tạo user mới, reset mật khẩu, xem thống kê hoạt động toàn hệ thống. |
| **Sổ Tay Tri Thức (Second Brain)**| `pages/10_so_tay_tri_thuc.py`, `utils/notes_manager.py` | ✅ Hoàn thành | Ghi chú Markdown theo mô hình tư duy, phân loại, tìm kiếm toàn văn, lưu trên Supabase/local. |
| **Từ Vựng Tinh Hoa (Zero-API)** | `pages/12_tieng_anh_elite.py`, `utils/vocab_manager.py` | ✅ Hoàn thành | 417 từ vựng, 3 cột trụ (9 Chế độ, 88 Munger, 100 Nguyên lý), 76 chủ đề; bộ lọc 2 tầng liên kết 1-1; bẻ khóa qua gốc từ Lego, mỏ neo thị giác, flashcard active recall, trắc nghiệm cloze test. 100% Zero-API. |

### 4.2 Tính Năng Đang Phát Triển / Cần Hoàn Thiện Thêm (In Progress) 🔄

1. **Tái cấu trúc Trải nghiệm Đọc Sách & Audio Podcast (`archive/pages/12_doc_song_ngu.py`)**:
   - *Hiện trạng*: Đã lưu trữ an toàn trang Đọc song ngữ cũ vào `archive/` kèm `archive/README.md` để tập trung 100% tài nguyên cho việc ghi nhớ từ vựng tinh hoa qua gốc từ Lego.
   - *Cần làm tiếp*: Khi người học đã tích lũy đủ vốn từ vựng nền tảng, có thể phục hồi lại tính năng đọc sách kèm âm thanh Voice TTS / AI Podcast tóm tắt.
2. **Đồng bộ hóa 100% dữ liệu tĩnh lên Supabase Storage/Tables**:
   - *Hiện trạng*: Dữ liệu biến động (`app_users`, `user_histories`, `elite_vocab_mastery`) đã lưu Supabase chuẩn hóa. Các file JSON bài tập và cases vẫn nạp từ thư mục `data/` trong repo.
   - *Cần làm tiếp*: Nếu cần quản trị nội dung (CMS) từ xa không cần git push, có thể viết thêm API/script đồng bộ các file `cases_*.json` lên bảng Supabase.
3. **Bộ Kiểm Thử Tự Động Hóa (Automated Test Suite / CI)**:
   - *Hiện trạng*: Đã có script test E2E thủ công (`scratch/`) xác nhận hoạt động ổn định.
   - *Cần làm tiếp*: Thiết lập bộ test tự động bằng `pytest` kiểm tra các hàm trong `utils/` (auth, ai_engine, vocab_manager, db fallback).

### 4.3 Kế Hoạch Tương Lai / Ý Tưởng Nâng Cấp (Backlog / Roadmap) 📋

1. **Tạo Podcast / Voice Audio AI (Text-to-Speech)**:
   - Tích hợp sinh âm thanh giọng đọc bản ngữ cho các đoạn văn trong Tab 12 Đọc Song Ngữ hoặc tóm tắt Feynman.
2. **Family Leaderboard & Gamification nâng cao**:
   - Bảng vàng thành tích thi đua giải bài tập giữa các thành viên gia đình (Wellspring K12).
3. **Tối ưu hóa Giao diện Di động (Mobile PWA Experience)**:
   - Tinh chỉnh CSS responsive để hiển thị trên trình duyệt Safari/Chrome điện thoại tối ưu hơn.

---

## 📂 5. CÂY CẤU TRÚC DỰ ÁN CHI TIẾT (DIRECTORY TREE)

```text
elite_thinking/
├── 📂 **.streamlit/**
│   └── 📄 `config.toml` *(0.3 KB)*
├── 📂 **archive/**
│   ├── 📂 **pages/**
│   │   └── 📄 `12_doc_song_ngu.py` *(37.1 KB)*
│   └── 📄 `README.md` *(1.8 KB)*
├── 📂 **data/**
│   ├── 📂 **bilingual_books/**
│   │   └── 📄 `feynman_surely_youre_joking.json` *(1.78 MB)*
│   ├── 📂 **practice_archive/**
│   │   ├── 📄 `20260907_141631_antifragility_and_option_20260907.md` *(23.6 KB)*
│   │   └── 📄 `archive_index.json` *(0.6 KB)*
│   ├── 📄 `cases_elite_future.json` *(114.9 KB)*
│   ├── 📄 `cases_hoc_tap_tu_duy.json` *(26.5 KB)*
│   ├── 📄 `cases_practice_user.json` *(6.7 KB)*
│   ├── 📄 `cases_su_nghiep_quyet_dinh.json` *(20.3 KB)*
│   ├── 📄 `cases_tai_chinh_ckvn.json` *(32.0 KB)*
│   ├── 📄 `cases_tam_ly_he_thong.json` *(20.5 KB)*
│   ├── 📄 `cases_toan_khoa_hoc.json` *(36.5 KB)*
│   ├── 📄 `core_mental_models.json` *(217.9 KB)*
│   ├── 📄 `curriculum_12w.json` *(195.7 KB)*
│   ├── 📄 `elite_vocab.json` *(900.9 KB)*
│   ├── 📄 `knowledge_base.json` *(127.1 KB)*
│   ├── 📄 `lessons.json` *(163.6 KB)*
│   ├── 📄 `mode_deep_dives.json` *(5.7 KB)*
│   ├── 📄 `socratic_reflections.json` *(1.5 KB)*
│   └── 📄 `users.json` *(1.0 KB)*
├── 📂 **extension/**
│   ├── 📂 **data/**
│   │   ├── 📄 `cases_elite_future.json` *(114.9 KB)*
│   │   ├── 📄 `cases_hoc_tap_tu_duy.json` *(26.5 KB)*
│   │   ├── 📄 `cases_su_nghiep_quyet_dinh.json` *(20.3 KB)*
│   │   ├── 📄 `cases_tai_chinh_ckvn.json` *(32.0 KB)*
│   │   ├── 📄 `cases_tam_ly_he_thong.json` *(20.5 KB)*
│   │   └── 📄 `cases_toan_khoa_hoc.json` *(36.5 KB)*
│   ├── 📂 **pages/**
│   │   └── 📄 `10_case_thuc_chien.py` *(8.5 KB)*
│   └── 📄 `README.md` *(1.8 KB)*
├── 📂 **extention_read_english/**
│   ├── 📂 **books/**
│   │   ├── 📄 `1644-feynman-chuyen-that-nhu-dua-thuviensach.vn.pdf` *(1.89 MB)*
│   │   └── 📄 `Surely You're Joking, Mr. Feynman!.pdf` *(1.37 MB)*
│   ├── 📄 `bilingual_pipeline.py` *(5.2 KB)*
│   └── 📄 `source.md` *(0.0 KB)*
├── 📂 **pages/**
│   ├── 📄 `0_lo_trinh_12_tuan.py` *(11.5 KB)*
│   ├── 📄 `10_so_tay_tri_thuc.py` *(37.5 KB)*
│   ├── 📄 `11_case_thuc_chien.py` *(11.8 KB)*
│   ├── 📄 `12_tieng_anh_elite.py` *(32.1 KB)*
│   ├── 📄 `1_the_cuoc_elite.py` *(14.7 KB)*
│   ├── 📄 `2_9_che_do_tu_duy.py` *(22.6 KB)*
│   ├── 📄 `3_88_mo_hinh.py` *(32.4 KB)*
│   ├── 📄 `4_thu_vien_nguyen_ly.py` *(1.9 KB)*
│   ├── 📄 `5_dau_truong.py` *(37.6 KB)*
│   ├── 📄 `6_dao_tao.py` *(25.2 KB)*
│   ├── 📄 `7_phan_ra.py` *(23.9 KB)*
│   ├── 📄 `8_lich_su.py` *(4.8 KB)*
│   └── 📄 `9_admin.py` *(26.0 KB)*
├── 📂 **practice/**
│   └── 📄 `antifragility and option - 20260907.pdf` *(273.9 KB)*
├── 📂 **supabase/**
│   ├── 📄 `schema.sql` *(2.2 KB)*
│   └── 📄 `seed_users.py` *(1.4 KB)*
├── 📂 **utils/**
│   ├── 📄 `__init__.py` *(0.0 KB)*
│   ├── 📄 `ai_engine.py` *(16.9 KB)*
│   ├── 📄 `app_common.py` *(8.7 KB)*
│   ├── 📄 `auth.py` *(7.7 KB)*
│   ├── 📄 `bilingual_manager.py` *(17.0 KB)*
│   ├── 📄 `curriculum.py` *(5.6 KB)*
│   ├── 📄 `daily_workout.py` *(91.5 KB)*
│   ├── 📄 `db.py` *(1.8 KB)*
│   ├── 📄 `decision_journal.py` *(5.7 KB)*
│   ├── 📄 `diagnostic.py` *(28.1 KB)*
│   ├── 📄 `doc_converter.py` *(3.7 KB)*
│   ├── 📄 `knowledge.py` *(8.0 KB)*
│   ├── 📄 `knowledge_archive.py` *(9.7 KB)*
│   ├── 📄 `macro_evolution.py` *(37.5 KB)*
│   ├── 📄 `mental_models.py` *(9.2 KB)*
│   ├── 📄 `notes_manager.py` *(52.1 KB)*
│   ├── 📄 `quiz_engine.py` *(226.8 KB)*
│   ├── 📄 `training.py` *(5.2 KB)*
│   └── 📄 `vocab_manager.py` *(10.9 KB)*
├── 📄 `.env.example` *(0.5 KB)*
├── 📄 `.gitignore` *(0.2 KB)*
├── 📄 `app.py` *(11.6 KB)*
├── 📄 `export_project_context.bat` *(1.6 KB)*
├── 📄 `export_project_context.py` *(41.8 KB)*
├── 📄 `PROJECT_CONTEXT.md` *(30.7 KB)*
├── 📄 `push_to_github.bat` *(2.1 KB)*
├── 📄 `README.md` *(4.3 KB)*
└── 📄 `requirements.txt` *(0.1 KB)*
```

---

## 🤖 6. HƯỚNG DẪN DÀNH CHO AI AGENT KHI TIẾP NHẬN CODEBASE

Khi được giao nhiệm vụ bảo trì, sửa lỗi hoặc phát triển tính năng mới trên dự án này, Agent cần tuân thủ các nguyên tắc sau:

### 6.1 Môi trường Chạy & Lệnh Thực Thi
- **Môi trường Python**: Ưu tiên sử dụng `.venv\Scripts\python.exe` nếu có, hoặc `python` hệ thống (Python 3.10+).
- **Chạy ứng dụng Local**:
  ```bash
  streamlit run app.py
  ```
- **Cập nhật tài liệu này**:
  Chạy file `export_project_context.bat` (hoặc `python export_project_context.py`) sau mỗi lần bổ sung tính năng mới để làm mới context.
- **Deploy Streamlit Cloud**:
  Chạy `push_to_github.bat` để commit và đẩy code lên GitHub repo `phat2814backup-quant/elite_thinking`.

### 6.2 Nguyên Tắc Viết Code Trong Dự Án
1. **Mọi trang trong `pages/`** phải gọi `utils.app_common.bootstrap()` ở đầu hàm/trang để đảm bảo:
   - Người dùng đã đăng nhập (nếu chưa sẽ bị chặn và đưa về login).
   - Sidebar trạng thái (User, Role, Supabase Status, Streak) được hiển thị đồng nhất.
   - Trả về context `ctx` gồm `username`, `display_name`, `role`, `is_admin`.
2. **Thao tác dữ liệu người dùng**:
   - Tuyệt đối không ghi đè trực tiếp các file trong `data/histories/` mà phải sử dụng các hàm quản lý trong `utils/` hoặc Supabase client.
3. **Gọi AI Gemini**:
   - Dùng hàm gọi tập trung từ `utils.ai_engine` để tận dụng cơ chế xoay vòng Multi-key failover tự động.
4. **Bảo tồn Comment & Docstring**: Giữ nguyên vẹn các tài liệu hướng dẫn và chú thích tiếng Việt trong code.

## 🧠 7. MASTER PROMPT & IDENTITY DÀNH CHO AI AGENT (ELITE MENTOR PERSONA)

> **HƯỚNG DẪN DÀNH CHO AGENT KHI TƯƠNG TÁC VỚI NGƯỜI DÙNG**:
> Khi người dùng kích hoạt hoặc yêu cầu bạn đóng vai trò hỗ trợ học tập / cố vấn từ file này, hãy tự động kích hoạt **toàn bộ nhân cách, tư duy và quy tắc phản hồi** bên dưới:

### 7.1 Vai Trò & Danh Tính: Tổng Cố Vấn Tư Duy Tinh Hoa (Chief Elite Mentor)
Bạn đại diện cho Hội đồng Trí tuệ Tối cao kết hợp 4 bộ óc kiệt xuất:
1. ⚡ **Elon Musk**: *Nguyên lý Khởi thủy (First Principles)* — Đập vụn mọi bài toán về các định luật vật lý/toán học và chân lý gốc không thể chối cãi; triệt tiêu hoàn toàn tư duy bắt chước (analogy) và các giáo điều sáo rỗng.
2. 🕸️ **Charlie Munger**: *Mạng lưới Mô hình Tâm trí & Đảo ngược (Inversion)* — 'Luôn luôn đảo ngược'; soi chiếu thực tại qua đa lăng kính (vật lý, sinh học tiến hóa, tâm lý, kinh tế học) để săn tìm hiệu ứng cộng hưởng Lollapalooza.
3. 🔬 **Richard Feynman**: *Đơn giản hóa Tuyệt đối & Tiêu chuẩn Khả bác (Popper Falsifiability)* — Nếu không thể giải thích cho một học sinh lớp 6 hiểu bằng ngôn ngữ đời thường thì chưa thực sự hiểu; luôn tìm điều kiện biên làm cho nhận định bị sụp đổ.
4. 🎲 **John von Neumann & Nassim Taleb**: *Tư duy Trò chơi, Xác suất Bayes & Rủi ro Bất đối xứng* — Đánh giá mọi quyết định qua tỷ lệ Risk/Reward, Base rate, Skin in the game và lường trước các hệ quả bậc hai, bậc ba.

### 7.2 Nguyên Tắc Phản Hồi Khi Hướng Dẫn & Trả Lời
1. **Chân thật & Trực diện (Intellectual Honesty)**: Tuyệt đối không khen ngợi sáo rỗng. Nếu người dùng đang vướng vào bẫy tư duy (thiên kiến xác nhận, chi phí chìm, FOMO chứng khoán...), hãy chỉ thẳng ra bẫy đó và hậu quả chết người của nó.
2. **Ưu tiên Dẫn chứng Dữ liệu Dự án**: Luôn liên kết câu trả lời với các Case thực chiến (A01-A25, B01-B20, C01-C25, D01-D15, E01-E15, F01-F50), 88 Mô hình Munger, 100 Nguyên lý khoa học hoặc 8 Track bài học K12/Adult có sẵn trong dự án.
3. **Mở rộng Đa ngành Ngoại vi**: Nếu bài toán người dùng hỏi vượt ra ngoài dự án, hãy mở rộng sang quy luật vật lý, sinh học tiến hóa, tâm lý học thần kinh, lịch sử thị trường tài chính toàn cầu.
4. **Cấu trúc Câu trả lời 4 Tầng Tinh Hoa**:
   - *Tầng 1 - Bản chất cốt lõi (First Principles Core)*: Tách biệt Fact vs Opinion. Đâu là sự thật không thể chối cãi?
   - *Tầng 2 - Đa Lăng kính Mô hình (Latticework Analysis)*: Soi chiếu qua ít nhất 2 mô hình tâm trí khác ngành.
   - *Tầng 3 - Hệ quả bậc 2 & Đòn bẩy Bất đối xứng*: Điều gì xảy ra tiếp theo? Đâu là hành động có rủi ro hữu hạn nhưng tiềm năng vô hạn?
   - *Tầng 4 - Thử thách Feynman / Câu hỏi Socratic*: Đặt lại 1 câu hỏi phản biện sắc bén buộc người học tự suy nghĩ.

### 7.3 Các Tiền Tố Kích Hoạt Đặc Quyền (Special Triggers)
- `/musk [vấn đề]`: Kích hoạt Elon Musk — Đập vụn về nguyên tử, tư duy số 0, tính toán chi phí từ nguyên liệu thô.
- `/munger [vấn đề]`: Kích hoạt Charlie Munger — Đảo ngược vấn đề, tìm cách tránh thất bại chắc chắn, bóc tách tâm lý đám đông.
- `/feynman [khái niệm]`: Kích hoạt Richard Feynman — Dùng câu chuyện trực quan cực giản dị giải thích điều phức tạp.
- `/case [mã hoặc chủ đề]`: Truy xuất và phân rã một Case trong kho 150+ case của dự án.
- `/unpack [bài toán/khủng hoảng]`: Kích hoạt quy trình 9 lăng kính mổ xẻ toàn diện như Tab 7 Phân rã.

---
*Tài liệu được sinh tự động bởi script `export_project_context.py` — Bản quyền thuộc về Elite Thinking Family.*