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
    1_🌐_Thế_cuộc_Elite.py
    2_📖_9_Chế_độ_Tư_duy.py
    3_🕸️_88_Mô_hình.py
    4_📚_Thư_viện_Nguyên_lý.py
    5_⚡_Đấu_trường.py
    6_🎓_Đào_tạo.py
    7_🚀_Phân_rã.py
    8_📝_Lịch_sử.py
    9_👑_Admin.py
  utils/
    app_common.py                 # login + sidebar + API keys (dùng chung mọi page)
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
