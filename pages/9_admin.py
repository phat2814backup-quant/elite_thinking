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
from utils.doc_converter import convert_document_to_markdown
from utils.knowledge_archive import (
    list_archives,
    get_archive,
    save_to_archive,
    delete_archive,
    load_deep_dives,
    save_deep_dive,
    delete_deep_dive,
    load_practice_cases,
    save_practice_case,
    delete_practice_case,
    load_socratic_reflections,
    save_socratic_reflection,
    delete_socratic_reflection,
    auto_decompose_living_knowledge
)

if not is_admin():
    st.warning("Chỉ admin mới truy cập được trang này.")
    st.stop()

st.title("👑 Khu vực quản trị (Phat)")
st.markdown("Xem tiến độ mọi thành viên · Cập nhật bài học · Nạp & Phê duyệt tri thức sống")

admin_tabs = st.tabs([
    "Tiến độ mọi người",
    "Cập nhật bài học",
    "📥 Nạp & Phê Duyệt Tri Thức",
    "🔐 Reset mật khẩu",
    "Thông tin hệ thống"
])

with admin_tabs[0]:
    all_h = list_all_user_histories()
    if not all_h:
        st.info("Chưa có dữ liệu lịch sử nào được ghi.")
    else:
        for h in all_h:
            uname = h.get("username", "?")
            n_ana = len(h.get("analyses", []))
            n_train = len(h.get("training", {}))
            c12 = h.get("curriculum_12w", {})
            c12_weeks = c12.get("weeks", {})
            c12_done = sum(1 for v in c12_weeks.values() if v.get("status") == "completed")
            c12_curr = c12.get("current_week", 1)
            with st.expander(f"**{uname}** · Lộ trình: {c12_done}/12 tuần (Tuần {c12_curr}) · {n_ana} phân rã · {n_train} bài tập"):
                if c12_weeks:
                    st.markdown(f"##### 📅 Lộ trình 12 tuần (Đang ở Tuần {c12_curr})")
                    for w_k, w_v in sorted(c12_weeks.items(), key=lambda x: int(x[0])):
                        st_icon = "✅" if w_v.get("status") == "completed" else "🟡"
                        score_txt = f"Quiz: {w_v.get('quiz_score')}/{w_v.get('quiz_total')}" if w_v.get("quiz_score") is not None else "Chưa làm quiz"
                        st.markdown(f"- {st_icon} **Tuần {w_k}**: {w_v.get('status')} · {score_txt}")
                        if w_v.get("exercise_answer"):
                            st.caption(f"Bài tập: {w_v.get('exercise_answer')[:180]}...")
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

    tracks_meta = get_tracks_meta()
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
    st.subheader("📥 Cổng Tiếp Nhận & Tự Động Phân Rã Tri Thức (Living Knowledge Hub)")
    st.markdown("""
    💡 **Quy trình tự động hóa 100% — Không cần gõ tay hay copy paste**:
    1. **Nạp tài liệu**: Tải file (`PDF`, `Word`, `PPTX`, `TXT`...) hoặc chọn từ kho lưu trữ. File nhị phân được chuyển sang Markdown và tự động xóa ngay lập tức.
    2. **AI Bóc tách**: Bấm nút để **AI Gemini tự động phân rã** thành **Lý thuyết chuyên sâu 4 tầng**, **Case thực chiến** và **Gương soi Socratic**.
    3. **1-Click Phê duyệt**: Admin xem trước kết quả bóc tách và bấm **Duyệt tất cả** để tự động cập nhật vào app.
    """)

    # -------------------------------------------------------------------------
    # BƯỚC 1: CHỌN NGUỒN TÀI LIỆU
    # -------------------------------------------------------------------------
    st.markdown("### 1️⃣ Chọn Tài Liệu Nguồn Cần Bóc Tách")
    
    arch_list = list_archives()
    source_choice = st.radio(
        "Nguồn tài liệu:",
        ["📤 Tải lên file mới (PDF, Word, PPTX, TXT...)", f"📚 Chọn từ kho tài liệu đã có ({len(arch_list)} tài liệu)"],
        horizontal=True
    )
    
    selected_doc_id = None
    selected_doc_title = ""
    selected_doc_content = ""
    selected_doc_filename = ""
    
    if "Tải lên file mới" in source_choice:
        up_file = st.file_uploader(
            "Kéo thả tệp tài liệu cần nạp:",
            type=["pdf", "docx", "doc", "pptx", "xlsx", "txt", "md", "epub", "rtf", "csv"],
            key="hub_doc_uploader"
        )
        if up_file is not None:
            c_u1, c_u2 = st.columns([3, 1])
            with c_u1:
                default_title = up_file.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                custom_title = st.text_input("Tiêu đề phiên tham vấn / tài liệu:", value=default_title, key="hub_custom_title")
            with c_u2:
                st.write("")
                st.write("")
                btn_conv = st.button("🚀 Chuyển Đổi & Nạp Vào Kho", type="primary", key="hub_btn_conv")
                
            if btn_conv:
                with st.spinner("AnyDoc engine đang chuyển đổi sang Markdown và dọn dẹp file nhị phân..."):
                    try:
                        md_text = convert_document_to_markdown(up_file, up_file.name)
                        new_entry = save_to_archive(
                            content=md_text,
                            original_filename=up_file.name,
                            title=custom_title,
                            author=username,
                            tags=["Hội đồng Trí tuệ", "Tự động nạp"]
                        )
                        st.session_state["cur_selected_doc_id"] = new_entry["id"]
                        st.success(f"✅ Đã chuyển đổi thành công sang Markdown! (File gốc đã tự động xóa để bảo toàn dung lượng).")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Lỗi chuyển đổi: {ex}")
                        
        if st.session_state.get("cur_selected_doc_id"):
            selected_doc_id = st.session_state["cur_selected_doc_id"]
    else:
        if not arch_list:
            st.info("Chưa có tài liệu nào trong kho. Vui lòng chọn 'Tải lên file mới'.")
        else:
            sel_idx = st.selectbox(
                "Chọn tài liệu cần bóc tách:",
                range(len(arch_list)),
                format_func=lambda i: f"📄 {arch_list[i].get('title')} ({arch_list[i].get('created_at')} · {arch_list[i].get('word_count', 0)} từ)"
            )
            selected_doc_id = arch_list[sel_idx]["id"]
            st.session_state["cur_selected_doc_id"] = selected_doc_id

    # Đọc nội dung tài liệu đang chọn
    if selected_doc_id:
        doc_info = get_archive(selected_doc_id)
        if doc_info:
            selected_doc_title = doc_info.get("title", "")
            selected_doc_content = doc_info.get("content", "")
            selected_doc_filename = doc_info.get("filename", "")
            
            with st.expander(f"📖 Xem nội dung Markdown nguồn: **{selected_doc_title}** ({doc_info.get('word_count', 0)} từ)", expanded=False):
                st.markdown(selected_doc_content[:3000] + ("\n\n*(Xem tiếp trong file...)*" if len(selected_doc_content) > 3000 else ""))

    st.divider()

    # -------------------------------------------------------------------------
    # BƯỚC 2: KÍCH HOẠT AI BÓC TÁCH TỰ ĐỘNG
    # -------------------------------------------------------------------------
    st.markdown("### 2️⃣ Kích Hoạt AI Gemini Tự Động Phân Rã Toàn Diện")
    st.caption("AI sẽ tự động đọc tài liệu, xác định Chế độ tư duy, bóc tách 4 Tầng Tinh Hoa, trích xuất Case Thực Chiến và tạo Gương Soi Socratic.")

    if not selected_doc_content:
        st.warning("Vui lòng chọn hoặc nạp một tài liệu ở Bước 1 trước khi kích hoạt AI.")
    else:
        c_ai1, c_ai2 = st.columns([3, 2])
        with c_ai1:
            st.write(f"Tài liệu mục tiêu: **{selected_doc_title}**")
        with c_ai2:
            trigger_ai = st.button("⚡ KÍCH HOẠT AI BÓC TÁCH TRI THỨC (AUTO-INGESTION)", type="primary", use_container_width=True)

        if trigger_ai:
            with st.spinner("🤖 Hội đồng Trí tuệ AI đang đọc sâu tài liệu, bóc tách cấu trúc 4 tầng, trích xuất case và gương soi... Vui lòng đợi trong giây lát..."):
                try:
                    ai_result = auto_decompose_living_knowledge(
                        markdown_content=selected_doc_content,
                        api_keys=active_keys,
                        model_name=model_choice
                    )
                    st.session_state["extracted_knowledge"] = ai_result
                    st.session_state["extracted_source_filename"] = selected_doc_filename
                    st.success(f"🎉 AI đã hoàn tất bóc tách bằng model `{ai_result.get('_model_used', 'Gemini')}`! Xem bản phân rã bên dưới.")
                except Exception as ai_err:
                    st.error(f"Lỗi khi AI phân rã: {ai_err}")

    # -------------------------------------------------------------------------
    # BƯỚC 3: XEM TRƯỚC KẾT QUẢ & PHÊ DUYỆT 1-CLICK
    # -------------------------------------------------------------------------
    if "extracted_knowledge" in st.session_state:
        st.divider()
        st.markdown("### 3️⃣ Xem Trước Kết Quả Phân Rã & Phê Duyệt Vào App")
        
        ext = st.session_state["extracted_knowledge"]
        m_code = ext.get("detected_mode_code", "MODE-05")
        m_title = ext.get("mode_title", "Tư duy Tùy chọn & Bất đối xứng")
        dd_data = ext.get("deep_dive", {})
        cases_data = ext.get("practice_cases", [])
        soc_data = ext.get("socratic_reflections", [])
        src_file = st.session_state.get("extracted_source_filename", "tai_lieu.md")
        
        st.info(f"🎯 AI đã phát hiện tài liệu này tương ứng với: **{m_code}: {m_title}**")
        
        # 3 Tabs hiển thị kết quả
        preview_tabs = st.tabs([
            f"🔬 1. Lý Thuyết Chuyên Sâu ({m_code})",
            f"💼 2. Case Thực Chiến ({len(cases_data)} cases)",
            f"🪞 3. Gương Soi Socratic ({len(soc_data)} mục)"
        ])
        
        with preview_tabs[0]:
            st.markdown(f"#### {dd_data.get('title', 'Luận Giải Chuyên Sâu')}")
            st.success(f"💬 *\"{dd_data.get('quote', '')}\"*")
            p_t1, p_t2, p_t3, p_t4 = st.tabs(["Tầng 1 Core", "Tầng 2 Latticework", "Tầng 3 Barbell", "Tầng 4 Socratic"])
            with p_t1:
                st.markdown(dd_data.get("layer_1_core", ""))
            with p_t2:
                st.markdown(dd_data.get("layer_2_latticework", ""))
            with p_t3:
                st.markdown(dd_data.get("layer_3_second_order", ""))
            with p_t4:
                st.markdown(dd_data.get("layer_4_feynman_socratic", ""))
                
        with preview_tabs[1]:
            for idx_c, c_item in enumerate(cases_data):
                st.markdown(f"##### 💼 Case #{idx_c+1}: **{c_item.get('title')}** ({c_item.get('category')})")
                st.caption(f"Đối tượng: {c_item.get('target_audience')}")
                st.markdown(f"**Vấn đề:** {c_item.get('problem')}")
                with st.expander("Xem chi tiết giải pháp & phân tích đa ngành", expanded=False):
                    st.markdown(f"**Latticework:**\n{c_item.get('latticework_analysis')}")
                    st.markdown("**Quy trình giải pháp:**")
                    for s in c_item.get("elite_solution", []):
                        st.markdown(f"- {s}")
                    st.markdown(f"💡 **Bài học rút ra:** *{c_item.get('key_takeaways')}*")
                st.divider()
                
        with preview_tabs[2]:
            for idx_s, s_item in enumerate(soc_data):
                st.markdown(f"##### 🪞 Gương soi #{idx_s+1}: **{s_item.get('title')}**")
                st.info(f"🧠 **Truy vấn:** {s_item.get('inquiry_prompt')}")
                if s_item.get("feynman_challenge"):
                    st.warning(f"🎭 **Thử thách Feynman:** {s_item.get('feynman_challenge')}")
                st.markdown("Bộ câu hỏi:")
                for q in s_item.get("reflection_questions", []):
                    st.markdown(f"- *{q}*")
                st.divider()
                
        # NÚT PHÊ DUYỆT TỔNG LỰC 1-CLICK
        st.markdown("#### 🚀 Hành Động Phê Duyệt:")
        col_app_all, col_app_cancel = st.columns([3, 1])
        
        with col_app_all:
            if st.button("🚀 PHÊ DUYỆT TẤT CẢ VÀ CẬP NHẬT VÀO HỆ THỐNG (1-CLICK SYNC)", type="primary", use_container_width=True):
                # 1. Lưu deep-dive
                save_deep_dive(
                    mode_code=m_code,
                    title=dd_data.get("title", f"Luận Giải Chuyên Sâu: {m_code}"),
                    quote=dd_data.get("quote", ""),
                    layers={
                        "layer_1_core": dd_data.get("layer_1_core", ""),
                        "layer_2_latticework": dd_data.get("layer_2_latticework", ""),
                        "layer_3_second_order": dd_data.get("layer_3_second_order", ""),
                        "layer_4_feynman_socratic": dd_data.get("layer_4_feynman_socratic", "")
                    },
                    source_ref=src_file,
                    author=username
                )
                # 2. Lưu cases
                cur_cases_count = len(load_practice_cases().get("cases", []))
                for i_c, c_item in enumerate(cases_data):
                    case_id = f"CASE-P{cur_cases_count + i_c + 1:02d}"
                    save_practice_case({
                        "id": case_id,
                        "title": c_item.get("title", "Case Thực Chiến"),
                        "category": c_item.get("category", "Thực chiến"),
                        "target_audience": c_item.get("target_audience", "Giới Elite"),
                        "problem": c_item.get("problem", ""),
                        "core_principles": c_item.get("core_principles", []),
                        "latticework_analysis": c_item.get("latticework_analysis", ""),
                        "elite_solution": c_item.get("elite_solution", []),
                        "key_takeaways": c_item.get("key_takeaways", "")
                    })
                # 3. Lưu socratic
                cur_soc_count = len(load_socratic_reflections())
                for i_s, s_item in enumerate(soc_data):
                    soc_id = f"SOC-{cur_soc_count + i_s + 1:02d}"
                    save_socratic_reflection({
                        "id": soc_id,
                        "mode_code": m_code,
                        "mode_title": m_title,
                        "title": s_item.get("title", "Tự vấn Socratic"),
                        "source": src_file,
                        "inquiry_prompt": s_item.get("inquiry_prompt", ""),
                        "feynman_challenge": s_item.get("feynman_challenge", ""),
                        "reflection_questions": s_item.get("reflection_questions", [])
                    })
                st.balloons()
                st.success(f"🎉 ĐÃ PHÊ DUYỆT & ĐỒNG BỘ TOÀN DIỆN THÀNH CÔNG!\n- Đã cập nhật Lý thuyết {m_code} tại '9 Chế độ tư duy'.\n- Đã thêm {len(cases_data)} Case vào Nhóm P tại 'Case thực chiến'.\n- Đã thêm {len(soc_data)} Gương soi vào Tab 5 của 'Sổ tay tri thức'.")
                del st.session_state["extracted_knowledge"]
                st.rerun()

        with col_app_cancel:
            if st.button("❌ Hủy kết quả phân rã này", use_container_width=True):
                del st.session_state["extracted_knowledge"]
                st.rerun()

    # -------------------------------------------------------------------------
    # PHẦN 4: QUẢN LÝ CÁC NỘI DUNG ĐANG HOẠT ĐỘNG (XEM & GỠ GỌN GÀNG)
    # -------------------------------------------------------------------------
    st.divider()
    with st.expander("📋 Quản lý & Gỡ bỏ các nội dung tri thức đang hoạt động trên App", expanded=False):
        t_inv_dd, t_inv_c, t_inv_s, t_inv_arch = st.tabs([
            "🔬 Lý thuyết Chuyên sâu",
            "💼 Case Nhóm P",
            "🪞 Gương soi Socratic",
            "📚 Kho File Tham Khảo"
        ])
        
        with t_inv_dd:
            live_dd = load_deep_dives()
            if not live_dd:
                st.info("Chưa có chế độ nào có bài luận giải chuyên sâu.")
            else:
                for m_k, m_v in live_dd.items():
                    col_k1, col_k2 = st.columns([4, 1])
                    col_k1.markdown(f"**{m_k}**: {m_v.get('title')} *(Cập nhật: {m_v.get('updated_at')})*")
                    if col_k2.button("🗑️ Gỡ bỏ", key=f"inv_del_dd_{m_k}"):
                        delete_deep_dive(m_k)
                        st.rerun()
                        
        with t_inv_c:
            live_cases = load_practice_cases().get("cases", [])
            if not live_cases:
                st.info("Chưa có case thực chiến nào trong Nhóm P.")
            else:
                for c in live_cases:
                    col_c1, col_c2 = st.columns([4, 1])
                    col_c1.markdown(f"**{c.get('id')}**: {c.get('title')} *({c.get('category')})*")
                    if col_c2.button("🗑️ Xóa", key=f"inv_del_c_{c.get('id')}"):
                        delete_practice_case(c.get("id"))
                        st.rerun()
                        
        with t_inv_s:
            live_soc = load_socratic_reflections()
            if not live_soc:
                st.info("Chưa có câu hỏi tự vấn Socratic nào.")
            else:
                for s in live_soc:
                    col_s1, col_s2 = st.columns([4, 1])
                    col_s1.markdown(f"**{s.get('id')}**: {s.get('title')} *[{s.get('mode_title')}]*")
                    if col_s2.button("🗑️ Xóa", key=f"inv_del_s_{s.get('id')}"):
                        delete_socratic_reflection(s.get("id"))
                        st.rerun()
                        
        with t_inv_arch:
            if not arch_list:
                st.info("Kho tham khảo trống.")
            else:
                for a in arch_list:
                    col_a1, col_a2 = st.columns([4, 1])
                    col_a1.markdown(f"📄 **{a.get('title')}** (`{a.get('filename')}` · {a.get('word_count')} từ)")
                    if col_a2.button("🗑️ Xóa file", key=f"inv_del_a_{a.get('id')}"):
                        delete_archive(a.get("id"))
                        st.rerun()

with admin_tabs[3]:
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

with admin_tabs[4]:
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
