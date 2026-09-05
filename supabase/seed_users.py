#!/usr/bin/env python3
"""Seed app_users từ data/users.json lên Supabase (chạy 1 lần local)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

try:
    from supabase import create_client
except ImportError:
    print("pip install supabase")
    sys.exit(1)

url = os.getenv("SUPABASE_URL", "").strip()
key = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or ""
).strip()

if not url or not key:
    print("Thiếu SUPABASE_URL / SUPABASE_KEY trong .env")
    sys.exit(1)

users_file = ROOT / "data" / "users.json"
data = json.loads(users_file.read_text(encoding="utf-8"))
client = create_client(url, key)

rows = []
for username, info in data.get("users", {}).items():
    rows.append(
        {
            "username": username,
            "password_hash": info.get("password_hash") or "",
            "role": info.get("role", "user"),
            "display_name": info.get("display_name", username),
        }
    )

if not rows:
    print("Không có user để seed")
    sys.exit(0)

res = client.table("app_users").upsert(rows).execute()
print(f"Seeded {len(rows)} users -> app_users")
for r in rows:
    print(f"  - {r['username']} ({r['role']})")

