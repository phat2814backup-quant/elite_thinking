# -*- coding: utf-8 -*-
"""Secure family authentication (PBKDF2) — Supabase or local users.json."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

_ITERATIONS = 200_000
_SALT_LEN = 16


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_LEN)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return base64.b64encode(salt + dk).decode("ascii")


def _check_password(password: str, stored: str) -> bool:
    try:
        raw = base64.b64decode(stored.encode("ascii"))
        salt, dk = raw[:_SALT_LEN], raw[_SALT_LEN:]
        new_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
        return secrets.compare_digest(dk, new_dk)
    except Exception:
        return False


# ---------- Local JSON ----------

def _load_users_local() -> Dict[str, Any]:
    if not USERS_FILE.exists():
        return {"users": {}}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users_local(data: Dict[str, Any]) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- Supabase ----------

def _load_users_supabase() -> Optional[Dict[str, Any]]:
    from utils.db import get_supabase

    client = get_supabase()
    if client is None:
        return None
    try:
        res = client.table("app_users").select("*").execute()
        users = {}
        for row in res.data or []:
            users[row["username"]] = {
                "password_hash": row.get("password_hash", ""),
                "role": row.get("role", "user"),
                "display_name": row.get("display_name") or row["username"],
            }
        return {"users": users}
    except Exception:
        return None


def _upsert_user_supabase(username: str, user: Dict[str, Any]) -> bool:
    from utils.db import get_supabase

    client = get_supabase()
    if client is None:
        return False
    try:
        client.table("app_users").upsert(
            {
                "username": username,
                "password_hash": user.get("password_hash", ""),
                "role": user.get("role", "user"),
                "display_name": user.get("display_name", username),
            }
        ).execute()
        return True
    except Exception:
        return False


def load_users() -> Dict[str, Any]:
    from utils.db import get_supabase

    if get_supabase() is not None:
        remote = _load_users_supabase()
        if remote is not None:
            return remote
    return _load_users_local()


def save_users(data: Dict[str, Any]) -> None:
    """Save full users dict — prefer Supabase, always mirror local as backup."""
    from utils.db import get_supabase

    if get_supabase() is not None:
        for uname, uinfo in data.get("users", {}).items():
            _upsert_user_supabase(uname, uinfo)
    _save_users_local(data)


def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    data = load_users()
    user = data.get("users", {}).get(username)
    if not user:
        return None

    stored_hash = user.get("password_hash")
    plain = user.get("password")

    ok = False
    if stored_hash:
        ok = _check_password(password, stored_hash)
    elif plain is not None and plain == password:
        ok = True
        user["password_hash"] = _hash_password(password)
        user.pop("password", None)
        save_users(data)

    if not ok:
        return None

    return {
        "username": username,
        "role": user.get("role", "user"),
        "display_name": user.get("display_name", username),
    }


def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    if len(new_password) < 8:
        return False, "Mật khẩu mới phải có ít nhất 8 ký tự."
    if new_password == old_password:
        return False, "Mật khẩu mới phải khác mật khẩu cũ."

    data = load_users()
    user = data.get("users", {}).get(username)
    if not user:
        return False, "Không tìm thấy người dùng."

    stored_hash = user.get("password_hash")
    plain = user.get("password")
    ok = False
    if stored_hash:
        ok = _check_password(old_password, stored_hash)
    elif plain is not None:
        ok = plain == old_password

    if not ok:
        return False, "Mật khẩu hiện tại không đúng."

    user["password_hash"] = _hash_password(new_password)
    user.pop("password", None)
    save_users(data)
    return True, "Đổi mật khẩu thành công."


def admin_reset_password(
    admin_username: str, target_username: str, new_password: str
) -> tuple[bool, str]:
    if len(new_password) < 8:
        return False, "Mật khẩu mới phải có ít nhất 8 ký tự."

    data = load_users()
    admin = data.get("users", {}).get(admin_username)
    if not admin or admin.get("role") != "admin":
        return False, "Chỉ admin mới được reset mật khẩu."

    target = data.get("users", {}).get(target_username)
    if not target:
        return False, f"Không tìm thấy user '{target_username}'."

    target["password_hash"] = _hash_password(new_password)
    target.pop("password", None)
    save_users(data)
    return True, f"Đã reset mật khẩu cho {target_username}."


def list_usernames() -> List[str]:
    data = load_users()
    return sorted(data.get("users", {}).keys())


def init_auth_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None


def require_login() -> bool:
    init_auth_state()

    if st.session_state.authenticated and st.session_state.user:
        return True

    st.title("🧠 Elite Thinking Family")
    st.markdown("Đăng nhập để sử dụng hệ thống tư duy & đào tạo.")

    with st.form("login_form"):
        username = st.text_input(
            "Tên đăng nhập",
            placeholder="Phat / Ha / xuka / bong / A1 / A2",
        )
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)

        if submitted:
            user = authenticate(username.strip(), password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.history = []
                st.session_state.training_progress = {}
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")

    st.caption("Tài khoản gia đình · Dữ liệu kiến thức dùng chung · Tiến độ học tập riêng")
    st.caption("🔒 Password hashed (PBKDF2) · Persistence: Supabase nếu đã cấu hình")
    return False


def logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("user")


def is_admin() -> bool:
    user = current_user()
    return bool(user and user.get("role") == "admin")
