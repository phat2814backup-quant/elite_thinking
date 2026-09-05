# -*- coding: utf-8 -*-
"""Shared bootstrap for multipage: login gate, sidebar, API keys, user context."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st
from dotenv import load_dotenv

from utils.auth import (
    require_login,
    logout,
    current_user,
    is_admin,
    change_password,
)
from utils.daily_workout import get_user_streak_info
from utils.db import supabase_status

CURRENT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(CURRENT_DIR / ".env")


def get_configured_api_keys() -> List[str]:
    keys: List[str] = []
    try:
        if "GEMINI_API_KEYS" in st.secrets:
            val = st.secrets["GEMINI_API_KEYS"]
            if isinstance(val, (list, tuple)):
                keys.extend([str(k).strip() for k in val if str(k).strip()])
            elif isinstance(val, str):
                keys.extend([k.strip() for k in val.split(",") if k.strip()])

        for idx in range(1, 10):
            k_name = f"GEMINI_API_KEY_{idx}"
            if k_name in st.secrets and st.secrets[k_name]:
                keys.append(str(st.secrets[k_name]).strip())

        for k_name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
            if k_name in st.secrets and st.secrets[k_name]:
                keys.append(str(st.secrets[k_name]).strip())
    except Exception:
        pass

    for idx in range(1, 10):
        v = os.getenv(f"GEMINI_API_KEY_{idx}")
        if v and v.strip():
            keys.append(v.strip())

    for k_name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        v = os.getenv(k_name)
        if v and v.strip():
            keys.append(v.strip())

    seen: set[str] = set()
    unique: List[str] = []
    for k in keys:
        if k and k not in seen:
            seen.add(k)
            unique.append(k)
    return unique


def render_sidebar(username: str, display_name: str, role: str) -> Tuple[List[str], str]:
    """Render common sidebar. Returns (active_keys, model_choice)."""
    with st.sidebar:
        st.markdown(f"### 👤 {display_name}")
        st.caption(f"Vai trò: **{'Quản trị' if role == 'admin' else 'Thành viên'}**")
        if st.button("Đăng xuất", use_container_width=True, key="sidebar_logout"):
            logout()

        st.divider()
        sb_streak = get_user_streak_info(username)
        s_val = sb_streak["current_streak"]
        s_badge = (
            "⚡ Khởi động"
            if s_val < 7
            else ("🔥 Thói quen thép" if s_val < 30 else "🏆 Phản xạ vô thức")
        )
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.metric("🔥 Chuỗi Streak", f"{s_val} ngày", s_badge)
        with col_sb2:
            st.metric("✅ Đã hoàn thành", f"{sb_streak['total_completed']} bài")

        if sb_streak["is_done_today"]:
            st.success("✨ Hôm nay: Đã xong 15p rèn luyện!")
        else:
            st.info("⏳ Hôm nay: Chưa làm bài (vào trang Đào tạo)")

        st.divider()
        st.markdown("#### 🔑 Gemini API Key")
        configured_keys = get_configured_api_keys()
        if configured_keys:
            st.success(f"Đã kích hoạt {len(configured_keys)} Key (xoay tua)")
        else:
            st.warning("Chưa cấu hình API Key. Secrets hoặc nhập tạm bên dưới.")

        override_key = ""
        model_choice = st.session_state.get("model_choice", "gemini-2.5-flash")
        with st.expander("⚙️ Tùy chọn Key / Model"):
            override_key = st.text_input(
                "Key tạm (session này)",
                value="",
                type="password",
                help="Ưu tiên key này cho session. Để trống = Secrets/Env.",
                key="sidebar_override_key",
            )
            model_choice = st.selectbox(
                "Model",
                ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"],
                index=0,
                key="sidebar_model_choice",
            )

        if override_key and override_key.strip():
            active_keys = [override_key.strip()] + [
                k for k in configured_keys if k != override_key.strip()
            ]
        else:
            active_keys = configured_keys

        st.session_state["active_api_keys"] = active_keys
        st.session_state["model_choice"] = model_choice

        st.divider()
        with st.expander("🔐 Đổi mật khẩu"):
            with st.form("change_pw_form"):
                old_pw = st.text_input("Mật khẩu hiện tại", type="password")
                new_pw = st.text_input("Mật khẩu mới (≥8 ký tự)", type="password")
                new_pw2 = st.text_input("Xác nhận mật khẩu mới", type="password")
                if st.form_submit_button("Đổi mật khẩu", use_container_width=True):
                    if new_pw != new_pw2:
                        st.error("Xác nhận mật khẩu không khớp.")
                    else:
                        ok, msg = change_password(username, old_pw, new_pw)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

        st.divider()
        status = supabase_status()
        if status["connected"]:
            st.caption("🟢 Persistence: **Supabase**")
        elif status["configured"]:
            st.caption("🟡 Supabase đã cấu hình nhưng chưa kết nối được")
        else:
            st.caption("🟠 Persistence: local JSON (có thể mất khi reboot Cloud)")
        st.caption("Knowledge dùng chung · Tiến độ học riêng")

    return active_keys, model_choice


def bootstrap() -> Dict[str, Any]:
    """
    Call at the top of every page.
    - Enforces login
    - Renders sidebar
    - Returns context: user, username, display_name, role, active_keys, model_choice, is_admin
    """
    if not require_login():
        st.stop()

    user = current_user()
    username = user["username"]
    display_name = user.get("display_name", username)
    role = user.get("role", "user")

    active_keys, model_choice = render_sidebar(username, display_name, role)

    return {
        "user": user,
        "username": username,
        "display_name": display_name,
        "role": role,
        "active_keys": active_keys,
        "model_choice": model_choice,
        "is_admin": is_admin(),
    }


def ensure_quiz_imports():
    """Lazy import quiz_engine with safe fallbacks (same as original app)."""
    try:
        from utils.quiz_engine import (
            MODES_QUIZ,
            MODELS_QUIZ,
            PRINCIPLES_QUIZ,
            get_all_flashcards,
            record_quiz_completion,
            update_flashcard_mastery,
            get_user_mastery_summary,
            generate_ai_quiz,
            evaluate_feynman_challenge,
            get_theory_questions_for_modes,
            get_theory_questions_for_models,
            get_theory_questions_for_principles,
        )

        return {
            "ready": True,
            "error": None,
            "MODES_QUIZ": MODES_QUIZ,
            "MODELS_QUIZ": MODELS_QUIZ,
            "PRINCIPLES_QUIZ": PRINCIPLES_QUIZ,
            "get_all_flashcards": get_all_flashcards,
            "record_quiz_completion": record_quiz_completion,
            "update_flashcard_mastery": update_flashcard_mastery,
            "get_user_mastery_summary": get_user_mastery_summary,
            "generate_ai_quiz": generate_ai_quiz,
            "evaluate_feynman_challenge": evaluate_feynman_challenge,
            "get_theory_questions_for_modes": get_theory_questions_for_modes,
            "get_theory_questions_for_models": get_theory_questions_for_models,
            "get_theory_questions_for_principles": get_theory_questions_for_principles,
        }
    except Exception as e:
        import traceback

        err = traceback.format_exc()

        def _noop(*a, **k):
            return {} if "summary" in str(a) else []

        return {
            "ready": False,
            "error": err,
            "MODES_QUIZ": [],
            "MODELS_QUIZ": [],
            "PRINCIPLES_QUIZ": [],
            "get_all_flashcards": _noop,
            "record_quiz_completion": _noop,
            "update_flashcard_mastery": _noop,
            "get_user_mastery_summary": lambda u: {
                "accuracy": 0,
                "total_quizzes": 0,
                "mastered_count": 0,
                "mastery_pct": 0,
                "learning_count": 0,
                "review_count": 0,
            },
            "generate_ai_quiz": _noop,
            "evaluate_feynman_challenge": _noop,
            "get_theory_questions_for_modes": _noop,
            "get_theory_questions_for_models": _noop,
            "get_theory_questions_for_principles": _noop,
        }
