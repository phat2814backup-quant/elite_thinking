# -*- coding: utf-8 -*-
"""Admin"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.auth import is_admin, admin_reset_password, list_usernames
from utils.knowledge import list_all_user_histories
from utils.training import load_lessons, save_lessons, get_tracks_meta, get_lesson
from utils.db import supabase_status

if not is_admin():
    st.warning("Chỉ admin mới truy cập được trang này.")
    st.stop()

st.title("👑 Khu vực quản trị (Phat)")
st.markdown("Xem tiến độ mọi thành viên · Cập nhật bài học")

admin_tabs = st.tabs(["Tiến độ mọi người", "Cập nhật bài học", "🔐 Reset mật khẩu", "Thông tin hệ thống"])

with admin_tabs[0]:
    all_h = list_all_user_histories()
    if not all_h:
        st.info("Chưa có dữ liệu lịch sử nào được ghi.")
    else:
        for h in all_h:
            uname = h.get("username", "?")
            n_ana = len(h.get("analyses", []))
            n_train = len(h.get("training", {}))
            with st.expander(f"**{uname}** · {n_ana} phân rã · {n_train} bài học · cập nhật {h.get('updated_at', '—')}"):
                st.markdown("##### Phân rã gần đây")
                for a in h.get("analyses", [])[:10]:
                    st.markdown(f"- `{a.get('time')}` {a.get('problem', '')[:100]}")
                st.markdown("##### Bài đào tạo")
                for lid, info in h.get("training", {}).items():
                    lesson = get_lesson(lid)
                    title = lesson["title"] if lesson else lid
                    st.markdown(f"- **{title}** ({info.get('time')})")
                    st.caption(info.get("answer", "")[:200])

with admin_tabs[1]:
    st.markdown("Chỉnh sửa nội dung bài học (lưu vào `data/lessons.json`).")
    data = load_lessons()
    st.caption(f"Version {data.get('version')} · Cập nhật lần cuối: {data.get('updated_at')} bởi {data.get('updated_by')}")

    all_available_tracks = list(tracks_meta.keys())
    g_edit = st.selectbox("Khóa học / Track cần sửa", all_available_tracks, format_func=lambda x: tracks_meta.get(x, {}).get("name", x))
    lessons_edit = data.get(g_edit, [])
    if lessons_edit:
        ids = [l["id"] for l in lessons_edit]
        sel_id = st.selectbox("Chọn bài", ids)
        lesson_e = next(l for l in lessons_edit if l["id"] == sel_id)

        new_title = st.text_input("Tiêu đề", value=lesson_e.get("title", ""))
        new_obj = st.text_area("Mục tiêu", value=lesson_e.get("objective", ""))
        new_sit = st.text_area("Tình huống", value=lesson_e.get("situation", ""))
        new_ex = st.text_area("Bài tập", value=lesson_e.get("exercise_prompt", ""))
        new_hint = st.text_area("Gợi ý", value=lesson_e.get("hint", ""))

        if st.button("💾 Lưu thay đổi bài học", type="primary"):
            for i, l in enumerate(data[g_edit]):
                if l["id"] == sel_id:
                    data[g_edit][i].update({
                        "title": new_title,
                        "objective": new_obj,
                        "situation": new_sit,
                        "exercise_prompt": new_ex,
                        "hint": new_hint,
                    })
                    break
            save_lessons(data, updated_by=username)
            st.success("Đã cập nhật bài học.")
            st.rerun()

    st.divider()
    st.markdown("#### Thêm bài mới thủ công")
    with st.form("add_lesson"):
        add_grade = st.selectbox("Thêm vào track", all_available_tracks, format_func=lambda x: tracks_meta.get(x, {}).get("name", x))
        add_id = st.text_input("ID (vd: g6_c1_02, tr_c2_02)")
        add_title = st.text_input("Tiêu đề")
        add_level_choice = st.selectbox("Mức", ["Cơ bản (level_1)", "Thực hành (level_2)", "Nâng cao (level_3)"])
        add_mode = st.text_input("Chế độ tư duy", value="First Principles")
        add_obj = st.text_area("Mục tiêu")
        add_sit = st.text_area("Tình huống")
        add_ex = st.text_area("Bài tập")
        add_hint = st.text_area("Gợi ý")
        if st.form_submit_button("Thêm bài"):
            if add_id and add_title:
                l_code = "level_1" if "level_1" in add_level_choice else ("level_2" if "level_2" in add_level_choice else "level_3")
                l_name = "Cơ bản" if "level_1" in add_level_choice else ("Thực hành" if "level_2" in add_level_choice else "Nâng cao")
                data.setdefault(add_grade, []).append({
                    "id": add_id,
                    "title": add_title,
                    "level_code": l_code,
                    "level": l_name,
                    "mode": add_mode,
                    "objective": add_obj,
                    "situation": add_sit,
                    "guide_steps": ["Đọc tình huống", "Trả lời bài tập", "Đối chiếu gợi ý"],
                    "exercise_prompt": add_ex,
                    "hint": add_hint,
                    "related_principle": "",
                })
                save_lessons(data, updated_by=username)
                st.success(f"Đã thêm {add_id}")
                st.rerun()
            else:
                st.warning("Cần ID và tiêu đề.")

with admin_tabs[2]:
    st.subheader("🔐 Reset mật khẩu thành viên")
    st.caption("Chỉ admin mới được reset. User có thể tự đổi mật khẩu ở sidebar.")
    all_users = [u for u in list_usernames() if u != username]
    if not all_users:
        st.info("Không có user nào khác.")
    else:
        with st.form("admin_reset_pw"):
            target = st.selectbox("Chọn user", all_users)
            new_pw = st.text_input("Mật khẩu mới (≥8 ký tự)", type="password")
            new_pw2 = st.text_input("Xác nhận", type="password")
            if st.form_submit_button("Reset mật khẩu", type="primary"):
                if new_pw != new_pw2:
                    st.error("Xác nhận không khớp.")
                else:
                    ok, msg = admin_reset_password(username, target, new_pw)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

with admin_tabs[3]:
    st.subheader("Thông tin hệ thống")
    status = supabase_status()
    if status["connected"]:
        st.success("🟢 Persistence backend: **Supabase** (histories + users bền qua reboot)")
    elif status["configured"]:
        st.warning("🟡 SUPABASE_URL/KEY đã có nhưng chưa kết nối được — kiểm tra key & schema")
    else:
        st.info("🟠 Chưa cấu hình Supabase → đang dùng local JSON (có thể mất khi Cloud reboot)")

    st.markdown("""
    **Kiến trúc v2**
    - **Multipage**: `app.py` + `pages/*` (không còn monolith 2700 dòng)
    - **Knowledge / lessons / models**: file JSON trong repo (bền)
    - **Users + histories**: Supabase (`app_users`, `user_histories`) nếu đã cấu hình; fallback local JSON
    - **Auth**: PBKDF2 hash, đổi pass sidebar, admin reset pass
    - **AI**: Gemini multi-key từ Secrets/Env (không hardcode)
    """)
    st.code("Users: Phat (admin), Ha, xuka, bong, A1, A2\nPassword pattern: <Tên>@12345", language="text")
