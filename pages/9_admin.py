# -*- coding: utf-8 -*-
"""Admin"""
from __future__ import annotations

import json
from datetime import datetime
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
    get_vn_now_str,
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
from utils.notes_manager import (
    load_curated_notes,
    save_curated_note,
    create_note
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
        
        approved_parts = st.session_state.setdefault("approved_decomposition_parts", set())

        status_dd = "✅ Đã duyệt" if "dd" in approved_parts else "⏳ Chờ duyệt"
        status_c = "✅ Đã duyệt" if "cases" in approved_parts else "⏳ Chờ duyệt"
        status_s = "✅ Đã duyệt" if "soc" in approved_parts else "⏳ Chờ duyệt"
        status_n = "✅ Đã duyệt" if "note" in approved_parts else "⏳ Chờ duyệt"

        # Chuẩn bị dữ liệu Atomic Note hoàn chỉnh cho Sổ Tay Tri Thức (Second Brain)
        note_title = f"{m_title} ({m_code}) — {dd_data.get('title', 'Luận Giải Tinh Hoa')}"
        note_domain = "📈 Đầu tư, Chứng khoán & Trading" if "05" in m_code else "🧠 Siêu nhận thức & Phương pháp học (Metacognition)"
        note_essence = dd_data.get("quote", "") or dd_data.get("layer_1_core", "")[:250]
        note_metaphor = "Cấu trúc Lồi, Quả tạ Barbell & Ngọn lửa gặp bão: Ngọn lửa nhỏ gặp bão sẽ tắt, ngọn lửa lớn gặp bão sẽ bùng thành đại hỏa hoạn."
        note_concepts = [
            f"Tầng 1 Core: {dd_data.get('title', m_title)}",
            f"Tầng 2 Latticework: Soi chiếu đa chiều (Quant, Sinh học, Tâm lý)",
            f"Tầng 3 Barbell: Cực 90% an toàn triệt tiêu Ruin Risk kết hợp 10% biên độ lớn",
            f"Tầng 4 Socratic: Thử thách Feynman & Câu hỏi tự vấn trung thực"
        ]
        note_models = [m_title, "Tư duy nguyên bản (First Principles Thinking)", "Tư duy đảo ngược (Inversion)"]
        note_steps = [s for c in cases_data for s in c.get("elite_solution", [])][:4] or [
            "Bước 1: Xác định và cắt cụt rủi ro đuôi trái (Stop Loss cố định <= 1% NAV).",
            "Bước 2: Triệt tiêu vùng trung gian giả tạo — cấu trúc lại theo Quả tạ Barbell.",
            "Bước 3: Tích lũy các Tùy chọn rẻ (chi phí thử sai thấp, đòn bẩy lớn).",
            "Bước 4: Trailing stop thu hoạch biên độ mở rộng khi có biến động."
        ]
        note_raw = f"""# {note_title}
> *\"{dd_data.get('quote', '')}\"*

{dd_data.get('layer_1_core', '')}

{dd_data.get('layer_2_latticework', '')}

{dd_data.get('layer_3_second_order', '')}

{dd_data.get('layer_4_feynman_socratic', '')}
"""

        # 4 Tabs hiển thị kết quả
        preview_tabs = st.tabs([
            f"🔬 1. Lý Thuyết Chuyên Sâu [{status_dd}] ({m_code})",
            f"💼 2. Case Thực Chiến [{status_c}] ({len(cases_data)} cases)",
            f"🪞 3. Gương Soi Socratic [{status_s}] ({len(soc_data)} mục)",
            f"💡 4. Sổ Tay Tri Thức [{status_n}] (Atomic Note)"
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

            st.markdown("---")
            if "dd" in approved_parts:
                st.success(f"✅ Đã phê duyệt và đồng bộ Lý thuyết ({m_code}) vào App thành công!")
            else:
                if st.button(f"🔬 Phê Duyệt Chỉ Riêng Lý Thuyết ({m_code}) Này", key="btn_app_dd_only"):
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
                    approved_parts.add("dd")
                    st.cache_data.clear()
                    st.success(f"✅ Đã cập nhật Lý thuyết {m_code} vào '9 Chế độ tư duy'!")
                    st.rerun()
                
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

            st.markdown("---")
            if "cases" in approved_parts:
                st.success(f"✅ Đã phê duyệt và thêm {len(cases_data)} Case vào Nhóm P thành công!")
            else:
                if st.button(f"💼 Phê Duyệt Chỉ Riêng {len(cases_data)} Case Thực Chiến Này", key="btn_app_cases_only"):
                    cur_cases_count = len(load_practice_cases().get("cases", []))
                    for i_c, c_item in enumerate(cases_data):
                        case_id = f"P{cur_cases_count + i_c + 1:02d}"
                        save_practice_case({
                            "id": case_id,
                            "title": c_item.get("title", "Case Thực Chiến"),
                            "difficulty": "Nâng cao",
                            "time_minutes": 15,
                            "category": c_item.get("category", "Thực chiến"),
                            "target_audience": c_item.get("target_audience", "Giới Elite"),
                            "problem": c_item.get("problem", ""),
                            "trigger_question": c_item.get("trigger_question") or f"Làm sao để áp dụng nguyên tắc này nhằm giải quyết triệt để vấn đề?",
                            "principles": c_item.get("core_principles", []) or [m_title],
                            "core_principles": c_item.get("core_principles", []) or [m_title],
                            "first_principles_breakdown": c_item.get("latticework_analysis", ""),
                            "latticework_analysis": c_item.get("latticework_analysis", ""),
                            "solution_steps": c_item.get("elite_solution", []),
                            "elite_solution": c_item.get("elite_solution", []),
                            "elite_insight": c_item.get("key_takeaways", ""),
                            "key_takeaways": c_item.get("key_takeaways", "")
                        })
                    approved_parts.add("cases")
                    st.cache_data.clear()
                    st.success(f"✅ Đã thêm {len(cases_data)} Case vào Nhóm P tại 'Case thực chiến'!")
                    st.rerun()
                
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

            st.markdown("---")
            if "soc" in approved_parts:
                st.success(f"✅ Đã phê duyệt và thêm {len(soc_data)} Gương Soi Socratic thành công!")
            else:
                if st.button(f"🪞 Phê Duyệt Chỉ Riêng {len(soc_data)} Gương Soi Socratic Này", key="btn_app_soc_only"):
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
                    approved_parts.add("soc")
                    st.cache_data.clear()
                    st.success(f"✅ Đã thêm {len(soc_data)} Gương soi vào Tab 5 'Sổ tay tri thức'!")
                    st.rerun()

        with preview_tabs[3]:
            st.markdown(f"#### 💡 {note_title}")
            st.caption(f"Lĩnh vực: **{note_domain}** · Thẻ: `[living-knowledge, {m_code.lower()}]`")
            st.info(f"💡 **Bản chất cốt lõi:** {note_essence}")
            st.markdown(f"🍲 **Ẩn dụ:** *{note_metaphor}*")
            st.markdown("##### 🪜 Các bước hành động đúc kết:")
            for stp in note_steps:
                st.markdown(f"- {stp}")

            st.markdown("---")
            if "note" in approved_parts:
                st.success("✅ Đã phê duyệt và lưu Ghi chú Atomic Note vào Kho Tri Thức của Sổ Tay thành công!")
            else:
                if st.button("💡 Phê Duyệt Chỉ Riêng Ghi Chú Sổ Tay Này", key="btn_app_note_only"):
                    note_obj = {
                        "id": f"NOTE-{m_code}-{datetime.now().strftime('%Y%m%d')}",
                        "title": note_title,
                        "note_type": "standard",
                        "created_at": get_vn_now_str(),
                        "updated_at": get_vn_now_str(),
                        "domain": note_domain,
                        "essence": note_essence,
                        "metaphor": note_metaphor,
                        "atomic_concepts": note_concepts,
                        "mental_models_linked": note_models,
                        "first_principles_linked": ["Nguyên lý Bất đối xứng lồi (Jensen's Inequality)", "Nguyên lý Triệt tiêu rủi ro diệt vong"],
                        "actionable_steps": note_steps,
                        "traps_and_biases": dd_data.get("quote", ""),
                        "tags": ["living-knowledge", "council-approved", m_code.lower(), "second-brain"],
                        "study_questions": [
                            {"question": f"Làm sao ứng dụng {m_title} vào đời sống thực tế?", "answer": note_essence}
                        ],
                        "cross_topic_connections": f"Kết nối trực tiếp tới {len(cases_data)} Case Thực Chiến Nhóm P và {len(soc_data)} Gương Soi Socratic.",
                        "favorite": True,
                        "mastery_level": 3,
                        "raw_content": note_raw
                    }
                    save_curated_note(note_obj)
                    create_note(
                        username=username,
                        raw_content=note_raw,
                        decomposed_data=note_obj,
                        custom_title=note_title,
                        note_type="standard"
                    )
                    approved_parts.add("note")
                    st.cache_data.clear()
                    st.success("✅ Đã thêm Ghi chú vào Sổ Tay Tri Thức (Kho Tri Thức)!")
                    st.rerun()
                
        # NÚT PHÊ DUYỆT TỔNG LỰC / ĐỒNG BỘ
        st.markdown("#### 🚀 Tùy Chọn Phê Duyệt & Đồng Bộ Hệ Thống:")
        
        c_chk1, c_chk2, c_chk3, c_chk4 = st.columns(4)
        with c_chk1:
            sel_dd = st.checkbox(f"🔬 1. Lý thuyết ({m_code})", value=("dd" not in approved_parts), disabled=("dd" in approved_parts))
        with c_chk2:
            sel_cases = st.checkbox(f"💼 2. Case Nhóm P ({len(cases_data)} cases)", value=("cases" not in approved_parts), disabled=("cases" in approved_parts))
        with c_chk3:
            sel_soc = st.checkbox(f"🪞 3. Gương soi ({len(soc_data)} mục)", value=("soc" not in approved_parts), disabled=("soc" in approved_parts))
        with c_chk4:
            sel_note = st.checkbox("💡 4. Sổ tay tri thức", value=("note" not in approved_parts), disabled=("note" in approved_parts))

        col_app_all, col_app_cancel = st.columns([3, 1])
        
        with col_app_all:
            if st.button("🚀 XÁC NHẬN PHÊ DUYỆT CÁC MỤC ĐÃ CHỌN VÀO APP", type="primary", use_container_width=True):
                synced_msgs = []
                # 1. Lưu deep-dive nếu chọn
                if sel_dd and "dd" not in approved_parts:
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
                    approved_parts.add("dd")
                    synced_msgs.append(f"Lý thuyết {m_code} tại '9 Chế độ tư duy'")

                # 2. Lưu cases nếu chọn
                if sel_cases and "cases" not in approved_parts:
                    cur_cases_count = len(load_practice_cases().get("cases", []))
                    for i_c, c_item in enumerate(cases_data):
                        case_id = f"P{cur_cases_count + i_c + 1:02d}"
                        save_practice_case({
                            "id": case_id,
                            "title": c_item.get("title", "Case Thực Chiến"),
                            "difficulty": "Nâng cao",
                            "time_minutes": 15,
                            "category": c_item.get("category", "Thực chiến"),
                            "target_audience": c_item.get("target_audience", "Giới Elite"),
                            "problem": c_item.get("problem", ""),
                            "trigger_question": c_item.get("trigger_question") or f"Làm sao để áp dụng nguyên tắc này nhằm giải quyết triệt để vấn đề?",
                            "principles": c_item.get("core_principles", []) or [m_title],
                            "core_principles": c_item.get("core_principles", []) or [m_title],
                            "first_principles_breakdown": c_item.get("latticework_analysis", ""),
                            "latticework_analysis": c_item.get("latticework_analysis", ""),
                            "solution_steps": c_item.get("elite_solution", []),
                            "elite_solution": c_item.get("elite_solution", []),
                            "elite_insight": c_item.get("key_takeaways", ""),
                            "key_takeaways": c_item.get("key_takeaways", "")
                        })
                    approved_parts.add("cases")
                    synced_msgs.append(f"{len(cases_data)} Case vào Nhóm P tại 'Case thực chiến'")

                # 3. Lưu socratic nếu chọn
                if sel_soc and "soc" not in approved_parts:
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
                    approved_parts.add("soc")
                    synced_msgs.append(f"{len(soc_data)} Gương soi vào Tab 5 của 'Sổ tay tri thức'")

                # 4. Lưu note vào Sổ Tay Tri Thức nếu chọn
                if sel_note and "note" not in approved_parts:
                    note_obj = {
                        "id": f"NOTE-{m_code}-{datetime.now().strftime('%Y%m%d')}",
                        "title": note_title,
                        "note_type": "standard",
                        "created_at": get_vn_now_str(),
                        "updated_at": get_vn_now_str(),
                        "domain": note_domain,
                        "essence": note_essence,
                        "metaphor": note_metaphor,
                        "atomic_concepts": note_concepts,
                        "mental_models_linked": note_models,
                        "first_principles_linked": ["Nguyên lý Bất đối xứng lồi (Jensen's Inequality)", "Nguyên lý Triệt tiêu rủi ro diệt vong"],
                        "actionable_steps": note_steps,
                        "traps_and_biases": dd_data.get("quote", ""),
                        "tags": ["living-knowledge", "council-approved", m_code.lower(), "second-brain"],
                        "study_questions": [
                            {"question": f"Làm sao ứng dụng {m_title} vào đời sống thực tế?", "answer": note_essence}
                        ],
                        "cross_topic_connections": f"Kết nối trực tiếp tới {len(cases_data)} Case Thực Chiến Nhóm P và {len(soc_data)} Gương Soi Socratic.",
                        "favorite": True,
                        "mastery_level": 3,
                        "raw_content": note_raw
                    }
                    save_curated_note(note_obj)
                    create_note(
                        username=username,
                        raw_content=note_raw,
                        decomposed_data=note_obj,
                        custom_title=note_title,
                        note_type="standard"
                    )
                    approved_parts.add("note")
                    synced_msgs.append("Ghi chú Atomic Note vào Kho Tri Thức của 'Sổ tay tri thức'")

                st.cache_data.clear()
                if synced_msgs:
                    st.balloons()
                    st.success(f"🎉 ĐÃ PHÊ DUYỆT & ĐỒNG BỘ THÀNH CÔNG:\n- " + "\n- ".join(synced_msgs))
                else:
                    st.info("Không có mục mới nào được chọn để đồng bộ.")
                st.rerun()

        with col_app_cancel:
            if approved_parts:
                if st.button("🏁 Hoàn tất & Đóng bản phân rã", use_container_width=True, type="secondary"):
                    st.session_state.pop("extracted_knowledge", None)
                    st.session_state.pop("approved_decomposition_parts", None)
                    st.cache_data.clear()
                    st.rerun()
            else:
                if st.button("❌ Hủy kết quả phân rã này", use_container_width=True):
                    st.session_state.pop("extracted_knowledge", None)
                    st.session_state.pop("approved_decomposition_parts", None)
                    st.rerun()

    # -------------------------------------------------------------------------
    # PHẦN 4: QUẢN LÝ CÁC NỘI DUNG ĐANG HOẠT ĐỘNG (XEM & GỠ GỌN GÀNG)
    # -------------------------------------------------------------------------
    st.divider()
    with st.expander("📋 Quản lý & Gỡ bỏ các nội dung tri thức đang hoạt động trên App", expanded=False):
        t_inv_dd, t_inv_c, t_inv_s, t_inv_note, t_inv_arch = st.tabs([
            "🔬 Lý thuyết Chuyên sâu",
            "💼 Case Nhóm P",
            "🪞 Gương soi Socratic",
            "💡 Ghi chú Sổ tay",
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
                        st.cache_data.clear()
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
                        st.cache_data.clear()
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
                        st.cache_data.clear()
                        st.rerun()

        with t_inv_note:
            live_curated = load_curated_notes()
            if not live_curated:
                st.info("Chưa có ghi chú tinh hoa chung nào trong Second Brain.")
            else:
                for cn in live_curated:
                    col_n1, col_n2 = st.columns([4, 1])
                    col_n1.markdown(f"**{cn.get('id')}**: {cn.get('title')} *({cn.get('domain')})*")
                    if col_n2.button("🗑️ Xóa", key=f"inv_del_cn_{cn.get('id')}"):
                        new_c = [x for x in live_curated if x.get("id") != cn.get("id")]
                        from utils.notes_manager import CURATED_NOTES_FILE
                        with open(CURATED_NOTES_FILE, "w", encoding="utf-8") as f:
                            json.dump(new_c, f, ensure_ascii=False, indent=2)
                        st.cache_data.clear()
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
                        st.cache_data.clear()
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
