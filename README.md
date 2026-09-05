# Elite Thinking Family v2

Huấn luyện tư duy tinh hoa (First Principles · Munger · Feynman) — multipage Streamlit + **Supabase persistence**.

## Điểm mới so với v1

| Hạng mục | v1 | v2 |
|----------|----|----|
| Cấu trúc | 1 file `app.py` ~2700 dòng | Multipage: `app.py` + `pages/*` |
| Password | Plain-text | PBKDF2 hash |
| API key | Hardcode trong source | Chỉ Secrets / Env |
| Histories / users trên Cloud | Mất khi reboot | **Supabase** (bền) |
| Đổi / reset mật khẩu | Không | Sidebar + Admin |

## Cấu trúc

```
elite_thinking_v2/
  app.py                          # Home: Hướng dẫn & Bản đồ
  pages/
    0_lo_trinh_12_tuan.py
    1_the_cuoc_elite.py
    2_9_che_do_tu_duy.py
    3_88_mo_hinh.py
    4_thu_vien_nguyen_ly.py
    5_dau_truong.py
    6_dao_tao.py
    7_phan_ra.py
    8_lich_su.py
    9_admin.py
  utils/
    app_common.py                 # login + sidebar + API keys (dùng chung mọi page)
    curriculum.py                 # Lộ trình 12 tuần & persistence
    db.py                         # Supabase client
    auth.py / knowledge.py / ...
  data/                           # knowledge, lessons, models, users seed
  supabase/
    schema.sql                    # chạy 1 lần trên Supabase
    seed_users.py                 # đẩy users.json → app_users
```

## 1. Setup Supabase (bắt buộc nếu muốn data không mất)

1. Tạo project tại [supabase.com](https://supabase.com)
2. **SQL Editor** → dán & Run toàn bộ `supabase/schema.sql`
3. **Project Settings → API** lấy:
   - Project URL → `SUPABASE_URL`
   - `service_role` key (secret) → `SUPABASE_SERVICE_KEY`  
     *(hoặc anon key nếu dùng policy permissive trong schema)*
4. (Tuỳ chọn local) seed users:

```bash
cp .env.example .env   # điền SUPABASE_* + GEMINI_*
pip install -r requirements.txt
python supabase/seed_users.py
```

Trên Cloud: lần login đầu với user trong `data/users.json` vẫn chạy được (fallback local).  
Muốn users cũng nằm trên Supabase: chạy seed 1 lần, hoặc admin tạo/reset qua app rồi data sẽ upsert lên Supabase.

## 2. Secrets trên Streamlit Cloud

```toml
GEMINI_API_KEY_1 = "AIzaSy..."
GEMINI_API_KEY_2 = "AIzaSy..."

SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOi..."
```

**Main file path:** `app.py`

## 3. Chạy local

```bash
cd elite_thinking_v2
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền key
streamlit run app.py
```

## Tài khoản mặc định

| User | Password | Role |
|------|----------|------|
| Phat | Phat@12345 | admin |
| Ha / xuka / bong / A1 / A2 | `<Tên>@12345` | user |

Đổi mật khẩu không bắt buộc — chỉ nên đổi nếu muốn.

## Hành vi persistence

| Có Supabase secrets? | Users | Histories (quiz, streak, diagnostic…) |
|----------------------|-------|----------------------------------------|
| Có + schema đã chạy | Supabase `app_users` | Supabase `user_histories` (JSONB) |
| Không | `data/users.json` | `data/histories/<user>.json` (mất khi Cloud reboot) |

Sidebar hiển thị trạng thái: 🟢 Supabase / 🟠 local JSON.

## Ghi chú kỹ thuật

- Knowledge / lessons / mental models vẫn là file trong repo → không cần DB.
- `user_histories.data` là JSONB — giữ nguyên schema nội bộ cũ (analyses, training, quiz_stats, daily_workouts, diagnostics, decisions…) nên không phá các module hiện có.
- Nếu Supabase lỗi tạm thời, app **fallback local JSON** tự động.

## Lộ trình 12 tuần (v2.1)

Trang **📅 Lộ trình 12 tuần** là xương sống học tập gia đình:

| Tuần | Nội dung |
|------|----------|
| 1–4 | Nền tảng: First Principles, Inversion, Bayesian, Latticework |
| 5–6 | **Systems**: stock/flow, feedback, leverage, emergence |
| 7–8 | **Uncertainty**: scenario, premortem+, fat tail, optionality, antifragile |
| 9–10 | **AI Judgment**: ủy thác có ranh giới, red-team / verify |
| 11–12 | Integration: incentive, decision review, Personal OS + teach-back |

Tiến độ lưu trong `user_histories` (Supabase hoặc local) dưới key `curriculum_12w`.
Mỗi tuần: đọc gợi ý → concept/drill → bài tập đời thực (bắt buộc) → quiz → hoàn thành.
