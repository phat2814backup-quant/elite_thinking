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
    delete_socratic_reflection
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
    st.subheader("📥 Cổng Nạp & Phê Duyệt Tri Thức Sống (Living Knowledge Ingestion Gate)")
    st.markdown("""
    Cơ chế đám mây tinh gọn (**Cloud-Native & Zero-Bloat**): 
    Admin tải file bất kỳ (PDF, Word, PowerPoint, Excel, TXT...) ➔ Engine AnyDoc (Rust) chuyển đổi sang Markdown GFM trong tích tắc (<5ms) ➔ 
    File nhị phân gốc lập tức bị xóa khỏi hệ thống để giữ app siêu nhẹ ➔ Lưu bản Markdown vào kho tham khảo ➔ 
    Admin phân loại và phê duyệt đẩy trực tiếp vào: **Lý thuyết 9 Chế độ**, **Case Thực chiến (Nhóm P)**, hoặc **Gương soi Socratic**.
    """)

    sub_tabs = st.tabs([
        "📤 1. Tải Lên & Chuyển Đổi",
        "📚 2. Kho Tham Khảo",
        "🔬 3. Lý Thuyết Chuyên Sâu",
        "💼 4. Case Thực Chiến (Nhóm P)",
        "🪞 5. Gương Soi Socratic"
    ])
    
    # Sub-tab 1: Tải lên & Chuyển đổi
    with sub_tabs[0]:
        st.markdown("#### 📤 Tải Lên & Tự Động Chuyển Đổi Sang Markdown")
        st.caption("Engine AnyDoc hỗ trợ PDF, DOCX, DOC, PPTX, XLSX, TXT, MD, EPUB, RTF, CSV. File nhị phân tải lên sẽ tự động bị xóa sau khi chuyển đổi.")
        
        up_file = st.file_uploader(
            "Chọn tệp tài liệu cần nạp:",
            type=["pdf", "docx", "doc", "pptx", "xlsx", "txt", "md", "epub", "rtf", "csv"],
            key="admin_doc_uploader"
        )
        
        if up_file is not None:
            col_u1, col_u2 = st.columns([3, 2])
            with col_u1:
                default_title = up_file.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                doc_title = st.text_input("Tiêu đề tài liệu / Phiên tham vấn:", value=default_title)
            with col_u2:
                doc_tags = st.text_input("Thẻ phân loại (cách nhau bởi dấu phẩy):", value="Hội đồng Trí tuệ, Thực chiến")
            
            if st.button("🚀 Chuyển Đổi Sang Markdown & Lưu Vào Kho", type="primary", key="btn_convert_save"):
                with st.spinner("Đang phân tích và chuyển đổi siêu tốc bằng AnyDoc engine..."):
                    try:
                        md_res = convert_document_to_markdown(up_file, up_file.name)
                        tags_list = [t.strip() for t in doc_tags.split(",") if t.strip()]
                        entry = save_to_archive(
                            content=md_res,
                            original_filename=up_file.name,
                            title=doc_title,
                            author=username,
                            tags=tags_list
                        )
                        st.success(f"🎉 Chuyển đổi thành công! Đã lưu vào kho tham khảo: `{entry['filename']}` ({entry['word_count']} từ · {entry['char_count']} ký tự). File nhị phân gốc đã được xóa hoàn toàn.")
                        with st.expander("👁️ Xem trước nội dung Markdown vừa trích xuất", expanded=True):
                            st.markdown(md_res[:3000] + ("\n\n*(Nội dung còn tiếp...)*" if len(md_res) > 3000 else ""))
                        st.rerun()
                    except Exception as err:
                        st.error(f"Lỗi chuyển đổi: {err}")

    # Sub-tab 2: Kho Tham khảo
    with sub_tabs[1]:
        st.markdown("#### 📚 Kho Tài Liệu Tham Khảo Nguyên Bản")
        arch_items = list_archives()
        if not arch_items:
            st.info("Chưa có tài liệu nào trong kho tham khảo.")
        else:
            st.caption(f"Tổng cộng: **{len(arch_items)}** tài liệu đối thoại / tham khảo Markdown.")
            arch_sel_id = st.selectbox(
                "Chọn tài liệu cần xem / quản lý:",
                [item["id"] for item in arch_items],
                format_func=lambda x: next((f"📄 {i['title']} ({i['created_at']})" for i in arch_items if i["id"] == x), x)
            )
            cur_item = get_archive(arch_sel_id)
            if cur_item:
                c_meta1, c_meta2, c_meta3 = st.columns(3)
                c_meta1.metric("Số từ", f"{cur_item.get('word_count', 0):,}")
                c_meta2.metric("Số ký tự", f"{cur_item.get('char_count', 0):,}")
                c_meta3.caption(f"File: `{cur_item.get('filename')}`\nNgày nạp: {cur_item.get('created_at')}\nTác giả: {cur_item.get('created_by')}")
                
                with st.expander("📖 Xem toàn bộ văn bản Markdown", expanded=False):
                    st.text_area("Markdown text", value=cur_item.get("content", ""), height=350, key=f"preview_arch_{cur_item['id']}")
                
                col_del, col_down = st.columns([1, 1])
                with col_down:
                    st.download_button(
                        "📥 Tải file Markdown (.md)",
                        data=cur_item.get("content", ""),
                        file_name=cur_item.get("filename", "document.md"),
                        mime="text/markdown",
                        key=f"dl_arch_{cur_item['id']}"
                    )
                with col_del:
                    if st.button("🗑️ Xóa vĩnh viễn khỏi kho", type="secondary", key=f"del_arch_{cur_item['id']}"):
                        delete_archive(cur_item["id"])
                        st.warning("Đã xóa tài liệu khỏi kho.")
                        st.rerun()

    # Sub-tab 3: Lý thuyết chuyên sâu
    with sub_tabs[2]:
        st.markdown("#### 🔬 Phê Duyệt Luận Giải Chuyên Sâu (Mode Deep-Dives)")
        st.caption("Các luận giải 4 Tầng Tinh Hoa sẽ xuất hiện bên dưới Chế độ tư duy tương ứng tại trang '9 Chế độ tư duy'.")
        
        all_modes = [
            ("MODE-01", "🎯 Chế độ 1: First Principles — Tư duy Nguyên bản"),
            ("MODE-02", "🎲 Chế độ 2: Tư duy Xác suất & Cập nhật Bayesian"),
            ("MODE-03", "🔄 Chế độ 3: Tư duy Đảo ngược (Inversion)"),
            ("MODE-04", "🌊 Chế độ 4: Tư duy Bậc hai & Bậc cao"),
            ("MODE-05", "⚖️ Chế độ 5: Tư duy Tùy chọn & Bất đối xứng"),
            ("MODE-06", "🕸️ Chế độ 6: Mạng lưới Mô hình Đa ngành (Latticework)"),
            ("MODE-07", "⚡ Chế độ 7: Tư duy Thực nghiệm Nhanh (Lean)"),
            ("MODE-08", "♟️ Chế độ 8: Tư duy Chiến lược & Lý thuyết Trò chơi"),
            ("MODE-09", "⏳ Chế độ 9: Tư duy Đa quy mô Thời gian")
        ]
        
        existing_deep_dives = load_deep_dives()
        
        # Danh sách đã duyệt
        st.markdown("##### 📌 Tình trạng luận giải đã duyệt:")
        cols_dd = st.columns(3)
        for idx, (m_code, m_name) in enumerate(all_modes):
            col_target = cols_dd[idx % 3]
            is_approved = m_code in existing_deep_dives
            status_icon = "✅" if is_approved else "⚪"
            col_target.markdown(f"- {status_icon} **{m_code}**: {'Đã có bài chuyên sâu' if is_approved else 'Chưa có'}")
            
        st.divider()
        sel_mode_code = st.selectbox(
            "Chọn chế độ tư duy cần soạn / chỉnh sửa Luận giải chuyên sâu:",
            [m[0] for m in all_modes],
            format_func=lambda x: next((m[1] for m in all_modes if m[0] == x), x)
        )
        
        cur_dd = existing_deep_dives.get(sel_mode_code, {})
        cur_layers = cur_dd.get("layers", {})
        
        with st.form(f"form_deep_dive_{sel_mode_code}"):
            dd_title = st.text_input("Tiêu đề luận giải chuyên sâu:", value=cur_dd.get("title", f"Luận Giải Chuyên Sâu: {sel_mode_code}"))
            dd_quote = st.text_input("Châm ngôn cốt lõi (Quote):", value=cur_dd.get("quote", ""))
            dd_source = st.text_input("Nguồn tham chiếu (Source reference):", value=cur_dd.get("source_ref", "Phiên tham vấn Hội đồng Trí tuệ Tối cao"))
            
            st.markdown("###### 🏛️ Tầng 1: Bản chất Cốt lõi (First Principles Core & Toán học)")
            l1_val = st.text_area("Nội dung Tầng 1", value=cur_layers.get("layer_1_core", ""), height=150)
            
            st.markdown("###### 🕸️ Tầng 2: Đa Lăng kính Mô hình (Latticework Analysis)")
            l2_val = st.text_area("Nội dung Tầng 2", value=cur_layers.get("layer_2_latticework", ""), height=150)
            
            st.markdown("###### ⚖️ Tầng 3: Hệ quả Bậc hai & Đòn bẩy Bất đối xứng / Barbell")
            l3_val = st.text_area("Nội dung Tầng 3", value=cur_layers.get("layer_3_second_order", ""), height=150)
            
            st.markdown("###### 🪞 Tầng 4: Thử thách Feynman & Câu hỏi Socratic")
            l4_val = st.text_area("Nội dung Tầng 4", value=cur_layers.get("layer_4_feynman_socratic", ""), height=150)
            
            col_save_dd, col_del_dd = st.columns([3, 1])
            with col_save_dd:
                submit_dd = st.form_submit_button("💾 Phê duyệt & Cập nhật Luận Giải Chuyên Sâu", type="primary")
            
            if submit_dd:
                if dd_title.strip() and l1_val.strip():
                    save_deep_dive(
                        mode_code=sel_mode_code,
                        title=dd_title.strip(),
                        quote=dd_quote.strip(),
                        layers={
                            "layer_1_core": l1_val.strip(),
                            "layer_2_latticework": l2_val.strip(),
                            "layer_3_second_order": l3_val.strip(),
                            "layer_4_feynman_socratic": l4_val.strip()
                        },
                        source_ref=dd_source.strip(),
                        author=username
                    )
                    st.success(f"✅ Đã phê duyệt và lưu Luận giải chuyên sâu cho {sel_mode_code}!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập tiêu đề và ít nhất nội dung Tầng 1.")
        
        if sel_mode_code in existing_deep_dives:
            if st.button(f"🗑️ Gỡ bỏ Luận giải Chuyên sâu của {sel_mode_code}", type="secondary", key=f"del_dd_{sel_mode_code}"):
                delete_deep_dive(sel_mode_code)
                st.warning(f"Đã gỡ bỏ Luận giải chuyên sâu của {sel_mode_code}.")
                st.rerun()

    # Sub-tab 4: Case Thực chiến
    with sub_tabs[3]:
        st.markdown("#### 💼 Phê Duyệt Case Thực Chiến (Nhóm P)")
        st.caption("Các case thực chiến do Hội đồng bóc tách từ các phiên thực tế, tự động hiển thị trong trang 'Case Thực Chiến' (Tab 11).")
        
        p_cases_data = load_practice_cases()
        p_cases_list = p_cases_data.get("cases", [])
        
        st.markdown(f"Hiện có **{len(p_cases_list)}** Case trong Nhóm P:")
        for c in p_cases_list:
            with st.expander(f"💼 **{c.get('id')}**: {c.get('title')} ({c.get('category')})"):
                st.markdown(f"**Vấn đề:** {c.get('problem')}")
                st.markdown(f"**Bài học:** *{c.get('key_takeaways')}*")
                if st.button(f"🗑️ Xóa Case {c.get('id')}", key=f"del_case_{c.get('id')}"):
                    delete_practice_case(c.get("id"))
                    st.warning(f"Đã xóa {c.get('id')}")
                    st.rerun()
                    
        st.divider()
        st.markdown("##### ➕ Soạn & Phê Duyệt Case Thực Chiến Mới:")
        with st.form("form_add_practice_case"):
            next_num = len(p_cases_list) + 1
            case_id = st.text_input("Mã Case:", value=f"CASE-P{next_num:02d}")
            case_title = st.text_input("Tiêu đề Case:")
            case_category = st.selectbox("Lĩnh vực:", [
                "Giao dịch Định lượng (Quant Trading)",
                "Giáo dục & Nuôi dạy Tinh hoa",
                "Kinh doanh & Khởi nghiệp",
                "Quản trị Hệ thống & Công nghệ",
                "Tâm lý & Ra quyết định"
            ])
            case_audience = st.text_input("Đối tượng mục tiêu:", value="Giới Elite, Nhà đầu tư & Cha mẹ")
            case_problem = st.text_area("Mô tả Vấn đề thực tế (Problem):", height=100)
            case_principles = st.text_area("Các nguyên tắc cốt lõi (mỗi dòng 1 nguyên tắc):", value="Optionality & Antifragility\nFirst Principles\nSecond-Order Thinking")
            case_lattice = st.text_area("Phân tích đa ngành (Latticework Analysis):", height=120)
            case_solution = st.text_area("Quy trình giải pháp của giới Elite (mỗi dòng 1 bước):", height=120)
            case_takeaways = st.text_area("Bài học rút ra (Key Takeaways):", height=80)
            
            if st.form_submit_button("💾 Phê Duyệt & Thêm Vào Case Thực Chiến Nhóm P", type="primary"):
                if case_id and case_title and case_problem:
                    principle_list = [p.strip() for p in case_principles.split("\n") if p.strip()]
                    sol_list = [s.strip() for s in case_solution.split("\n") if s.strip()]
                    new_c = {
                        "id": case_id.strip(),
                        "title": case_title.strip(),
                        "category": case_category,
                        "target_audience": case_audience.strip(),
                        "problem": case_problem.strip(),
                        "core_principles": principle_list,
                        "latticework_analysis": case_lattice.strip(),
                        "elite_solution": sol_list,
                        "key_takeaways": case_takeaways.strip()
                    }
                    save_practice_case(new_c)
                    st.success(f"✅ Đã phê duyệt và lưu {case_id} vào Nhóm P!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập đầy đủ Mã, Tiêu đề và Vấn đề.")

    # Sub-tab 5: Gương soi Socratic
    with sub_tabs[4]:
        st.markdown("#### 🪞 Phê Duyệt Gương Soi Socratic")
        st.caption("Các câu hỏi tự vấn trực diện giúp người học tự soi chiếu, tích hợp vào Tab 5 của 'Sổ tay tri thức'.")
        
        soc_items = load_socratic_reflections()
        st.markdown(f"Hiện có **{len(soc_items)}** câu hỏi tự vấn:")
        for s in soc_items:
            with st.expander(f"🪞 **{s.get('id')}**: {s.get('title')} [{s.get('mode_title')}]"):
                st.info(s.get("inquiry_prompt"))
                if s.get("feynman_challenge"):
                    st.warning(s.get("feynman_challenge"))
                if st.button(f"🗑️ Xóa Gương soi {s.get('id')}", key=f"del_soc_{s.get('id')}"):
                    delete_socratic_reflection(s.get("id"))
                    st.warning(f"Đã xóa {s.get('id')}")
                    st.rerun()
                    
        st.divider()
        st.markdown("##### ➕ Soạn & Phê Duyệt Gương Soi Socratic Mới:")
        with st.form("form_add_socratic"):
            next_soc_num = len(soc_items) + 1
            soc_id = st.text_input("Mã Gương soi:", value=f"SOC-{next_soc_num:02d}")
            soc_mode_choice = st.selectbox(
                "Chế độ tư duy liên quan:",
                [m[0] for m in all_modes],
                format_func=lambda x: next((m[1] for m in all_modes if m[0] == x), x)
            )
            soc_mode_title = next((m[1] for m in all_modes if m[0] == soc_mode_choice), soc_mode_choice)
            soc_title = st.text_input("Tiêu đề Gương soi:")
            soc_source = st.text_input("Nguồn đối thoại / tài liệu:", value="antifragility_and_option_20260907.md")
            soc_prompt = st.text_area("Câu hỏi truy vấn chính từ Hội đồng:", height=120)
            soc_feynman = st.text_area("Thử thách Feynman (Đừng tự dối mình):", height=100)
            soc_qlist = st.text_area("Các câu hỏi tự vấn chi tiết (mỗi dòng 1 câu hỏi):", height=100)
            
            if st.form_submit_button("💾 Phê Duyệt & Thêm Vào Gương Soi Socratic", type="primary"):
                if soc_id and soc_title and soc_prompt:
                    q_list = [q.strip() for q in soc_qlist.split("\n") if q.strip()]
                    new_s = {
                        "id": soc_id.strip(),
                        "mode_code": soc_mode_choice,
                        "mode_title": soc_mode_title,
                        "title": soc_title.strip(),
                        "source": soc_source.strip(),
                        "inquiry_prompt": soc_prompt.strip(),
                        "feynman_challenge": soc_feynman.strip(),
                        "reflection_questions": q_list
                    }
                    save_socratic_reflection(new_s)
                    st.success(f"✅ Đã phê duyệt và lưu {soc_id}!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập đầy đủ Mã, Tiêu đề và Câu hỏi truy vấn chính.")

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
