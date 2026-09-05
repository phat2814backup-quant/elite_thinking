-- Elite Thinking Family — Supabase schema
-- Chạy trong Supabase Dashboard → SQL Editor

-- 1. Users (auth app riêng, không dùng Supabase Auth)
create table if not exists public.app_users (
  username text primary key,
  password_hash text not null,
  role text not null default 'user',
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 2. Per-user history blob (analyses, training, quiz, diagnostic, decisions, daily_workouts...)
create table if not exists public.user_histories (
  username text primary key references public.app_users(username) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- Index for admin listing
create index if not exists idx_user_histories_updated
  on public.user_histories (updated_at desc);

-- Auto-update updated_at
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_app_users_updated on public.app_users;
create trigger trg_app_users_updated
  before update on public.app_users
  for each row execute function public.set_updated_at();

drop trigger if exists trg_user_histories_updated on public.user_histories;
create trigger trg_user_histories_updated
  before update on public.user_histories
  for each row execute function public.set_updated_at();

-- RLS: app dùng service_role key từ server → bypass RLS.
-- Nếu dùng anon key, bật policy phù hợp hoặc tắt RLS cho 2 bảng này (family app).
alter table public.app_users enable row level security;
alter table public.user_histories enable row level security;

-- Policy cho phép full access khi dùng service role (bypass).
-- Với anon key + family internal: mở policy permissive (chỉ dùng trong private app).
drop policy if exists "allow_all_app_users" on public.app_users;
create policy "allow_all_app_users" on public.app_users
  for all using (true) with check (true);

drop policy if exists "allow_all_user_histories" on public.user_histories;
create policy "allow_all_user_histories" on public.user_histories
  for all using (true) with check (true);
