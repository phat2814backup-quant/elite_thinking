# -*- coding: utf-8 -*-
"""
Trang: Sổ Tay Tri Thức Đa Chiều (Elite Knowledge Vault & Second Brain)
- Lưu trữ 100% nguyên vẹn nội dung gốc
- AI tự động phân rã nguyên tử (Atomic Knowledge)
- Mạng lưới liên kết chéo với 88 Mô hình tư duy & 100 Nguyên lý đệ nhất
- Tra cứu đa chiều, Ôn tập phản xạ Active Recall & AI Tổng hợp giao thoa
"""

import streamlit as st
from datetime import datetime

from utils.app_common import bootstrap
from utils.notes_manager import (
    NOTE_DOMAINS,
    DEFAULT_FEYNMAN_NOTE,
    create_note,
    get_user_notes,
    get_note_by_id,
    update_note,
    delete_note,
    toggle_favorite,
    update_mastery,
    search_notes,
    find_related_notes,
    get_all_vault_tags,
    get_all_vault_models,
    get_random_flashcards,
    export_notes_to_markdown,
    export_notes_to_json,
    heuristic_decompose_note,
    decompose_knowledge_note,
    synthesize_cross_notes,
)

# -----------------------------------------------------------------------------
# Bootstrap & Auth
# -----------------------------------------------------------------------------
ctx = bootstrap()
username = ctx["username"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

st.title("💡 Sổ Tay Tri Thức Đa Chiều (Second Brain)")
st.caption(
    "Xây dựng mạng lưới tri thức nguyên tử (Zettelkasten Latticework) · "
    "Lưu trữ nguyên bản · Phân rã đa chiều · Liên kết 88 Mô hình & 100 Nguyên lý · Ôn tập phản xạ Active Recall"
)

# -----------------------------------------------------------------------------
# 4 Main Tabs
# -----------------------------------------------------------------------------
tab_labels = [
    "✍️ Ghi Chép Nhanh & AI Phân Rã",
    "🗂️ Kho Tri Thức & Tra Cứu Đan Chéo",
    "🎓 Ôn Tập Phản Xạ & AI Tổng Hợp",
    "🕸️ Bản Đồ Tri Thức & Xuất Dữ Liệu",
]
tab_capture, tab_vault, tab_recall, tab_graph = st.tabs(tab_labels)

# =============================================================================
# TAB 1: GHI CHÉP NHANH & AI PHÂN RÃ
# =============================================================================
with tab_capture:
    st.markdown("### ✍️ Thu Nạp Tri Thức & Tự Động Phân Rã Nguyên Tử")
    st.info(
        "💡 **Nguyên lý Second Brain**: Bất cứ khi nào bạn đọc sách, nghiên cứu một kỹ thuật (như *Kỹ thuật Feynman*), "
        "hay ghi nhận một bài học đầu tư/quản trị, hãy dán nguyên văn vào đây. "
        "Hệ thống sẽ **lưu giữ 100% văn bản gốc**, đồng thời AI sẽ tự động bóc tách bản chất cốt lõi, "
        "tìm ẩn dụ, nhận diện bẫy tư duy và kết nối vào mạng lưới **88 Mô hình & 100 Nguyên lý**."
    )

    # Nút bấm nạp mẫu nhanh
    c_btn_sample, c_btn_clear = st.columns([3, 1])
    with c_btn_sample:
        if st.button("💡 Nạp nội dung mẫu: Kỹ thuật Feynman (Trải nghiệm nhanh)", use_container_width=True):
            st.session_state["raw_input_content"] = DEFAULT_FEYNMAN_NOTE["raw_content"]
            st.session_state["input_custom_title"] = "Kỹ thuật Feynman (Feynman Technique) — Giải thích bình dân"
            st.rerun()

    with c_btn_clear:
        if st.button("🗑️ Xóa trắng ô nhập", use_container_width=True):
            st.session_state["raw_input_content"] = ""
            st.session_state["input_custom_title"] = ""
            st.session_state.pop("latest_decomposed_preview", None)
            st.rerun()

    custom_title = st.text_input(
        "Tiêu đề ghi chú (Tùy chọn — để trống nếu muốn AI tự đặt tiêu đề tinh hoa):",
        value=st.session_state.get("input_custom_title", ""),
        placeholder="Ví dụ: Kỹ thuật Feynman: Giải thích cho trẻ 10 tuổi...",
        key="note_custom_title_input",
    )

    raw_text = st.text_area(
        "Nội dung ghi chú nguyên bản (dán bài viết, trích dẫn, suy ngẫm thực chiến...):",
        value=st.session_state.get("raw_input_content", ""),
        height=320,
        placeholder="Dán toàn bộ văn bản ghi chú vào đây... Hệ thống sẽ bảo toàn 100% văn bản này.",
        key="note_raw_text_area",
    )

    if st.button("🚀 Phân Rã Đa Chiều & Lưu Vào Second Brain", type="primary", use_container_width=True):
        if not raw_text.strip():
            st.warning("Vui lòng nhập hoặc dán nội dung ghi chú trước khi phân rã.")
        else:
            with st.spinner("🧠 Đang phân rã nguyên tử, định vị bẫy nhận thức và kết nối mạng lưới mô hình..."):
                decomposed = decompose_knowledge_note(
                    api_keys=active_keys,
                    model_name=model_choice,
                    raw_content=raw_text,
                    title_hint=custom_title.strip(),
                )
                new_note = create_note(
                    username=username,
                    raw_content=raw_text,
                    decomposed_data=decomposed,
                    custom_title=custom_title.strip(),
                )
                st.session_state["latest_decomposed_preview"] = new_note
                st.success(f"✅ Đã phân rã và lưu thành công ghi chú: **{new_note['title']}** (Mã: `{new_note['id']}`)!")

    # Hiển thị bản xem trước của Note vừa được phân rã
    preview_note = st.session_state.get("latest_decomposed_preview")
    if preview_note:
        st.divider()
        st.markdown(f"#### 🔍 Kết Quả Phân Rã Tri Thức: **{preview_note.get('title')}**")
        st.caption(f"🏷️ Lĩnh vực: **{preview_note.get('domain')}** | ID: `{preview_note.get('id')}`")

        col_es, col_met = st.columns([3, 2])
        with col_es:
            st.markdown(
                f"""<div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-left: 5px solid #38bdf8; margin-bottom: 12px;">
                <b style="color: #38bdf8;">💡 Bản Chất Cốt Lõi (Essence):</b><br/>
                {preview_note.get('essence')}
                </div>""",
                unsafe_allow_html=True,
            )
        with col_met:
            met = preview_note.get("metaphor") or "Chưa có hình ảnh ẩn dụ cụ thể."
            st.markdown(
                f"""<div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-left: 5px solid #f59e0b; margin-bottom: 12px;">
                <b style="color: #f59e0b;">🍲 Hình Tượng Ẩn Dụ (Metaphor):</b><br/>
                {met}
                </div>""",
                unsafe_allow_html=True,
            )

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("##### 🧩 Khái Niệm Nguyên Tử (Atomic Concepts)")
            for c in preview_note.get("atomic_concepts", []):
                st.markdown(f"- {c}")

            st.markdown("##### 🛡️ Bẫy Tư Duy & Điểm Mù Khắc Phục")
            st.markdown(f"> *{preview_note.get('traps_and_biases', 'Không có')}*")

        with col_c2:
            st.markdown("##### 🪜 Khung Các Bước Thực Hành (Action Protocol)")
            for step in preview_note.get("actionable_steps", []):
                st.markdown(f"- {step}")

            st.markdown("##### 🕸️ Mô Hình Tư Duy Liên Kết")
            models_linked = preview_note.get("mental_models_linked", [])
            if models_linked:
                st.write(", ".join([f"`{m}`" for m in models_linked]))
            else:
                st.caption("Chưa gắn mô hình cụ thể.")

            st.markdown("##### 📚 Nguyên Lý Đệ Nhất Liên Quan")
            principles_linked = preview_note.get("first_principles_linked", [])
            if principles_linked:
                st.write(", ".join([f"`{p}`" for p in principles_linked]))
            else:
                st.caption("Chưa gắn nguyên lý cụ thể.")

        with st.expander("📄 Xem lại toàn bộ nội dung gốc đã lưu trữ"):
            st.text_area("Nội dung gốc nguyên bản:", value=preview_note.get("raw_content", ""), height=200, disabled=True)


# =============================================================================
# TAB 2: KHO TRI THỨC & TRA CỨU ĐAN CHÉO (SECOND BRAIN VAULT)
# =============================================================================
with tab_vault:
    st.markdown("### 🗂️ Kho Tri Thức & Mạng Lưới Tra Cứu Đa Chiều")

    all_vault_tags = ["Tất cả"] + get_all_vault_tags(username)
    all_vault_models = ["Tất cả"] + get_all_vault_models(username)
    domain_options = ["Tất cả"] + NOTE_DOMAINS

    c_s1, c_s2 = st.columns([3, 2])
    with c_s1:
        search_q = st.text_input("🔍 Tìm kiếm theo từ khóa (tiêu đề, bản chất, nội dung gốc, ẩn dụ...):", key="vault_search_q")
    with c_s2:
        sel_domain = st.selectbox("Lĩnh vực tri thức:", domain_options, key="vault_filter_domain")

    c_f1, c_f2, c_f3, c_f4 = st.columns([2, 2, 2, 1])
    with c_f1:
        sel_model = st.selectbox("Mô hình tư duy kết nối:", all_vault_models, key="vault_filter_model")
    with c_f2:
        sel_tag = st.selectbox("Thẻ phân loại (Tag):", all_vault_tags, key="vault_filter_tag")
    with c_f3:
        sel_mastery = st.selectbox(
            "Mức độ nhuần nhuyễn:",
            ["Tất cả", "🌱 Mới lưu", "🔥 Đang rèn luyện", "👑 Đã nhuần nhuyễn"],
            key="vault_filter_mastery",
        )
    with c_f4:
        fav_only = st.checkbox("⭐ Yêu thích", value=False, key="vault_filter_fav")

    # Thực thi truy vấn
    matched_notes = search_notes(
        username=username,
        query=search_q,
        domain=sel_domain,
        mental_model=sel_model,
        tag=sel_tag,
        only_favorites=fav_only,
        mastery_filter=sel_mastery,
    )

    st.caption(f"Tìm thấy **{len(matched_notes)}** ghi chú phù hợp với điều kiện tra cứu.")
    st.divider()

    if not matched_notes:
        st.info("Chưa tìm thấy ghi chú nào phù hợp. Bạn hãy thử nới lỏng bộ lọc hoặc tạo ghi chú mới ở Tab 1.")
    else:
        for note in matched_notes:
            n_id = note["id"]
            is_fav = note.get("favorite", False)
            fav_icon = "⭐" if is_fav else "☆"
            mastery = note.get("mastery_level", 1)
            mastery_badges = {1: "🌱 Mới nạp", 2: "🔥 Đang rèn", 3: "👑 Nhuần nhuyễn"}

            with st.container():
                c_title, c_actions = st.columns([4, 2])
                with c_title:
                    st.markdown(f"#### {fav_icon} {note.get('title')} `[{mastery_badges.get(mastery, '🌱')}]`")
                    st.caption(f"🏷️ **{note.get('domain')}** · 🕒 Cập nhật: `{note.get('updated_at', note.get('created_at'))}` · ID: `{n_id}`")
                with c_actions:
                    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])
                    with col_act1:
                        if st.button(fav_icon, key=f"fav_btn_{n_id}", help="Đánh dấu yêu thích"):
                            toggle_favorite(username, n_id)
                            st.rerun()
                    with col_act2:
                        next_lvl = (mastery % 3) + 1
                        if st.button(f"⭐x{mastery}", key=f"lvl_btn_{n_id}", help=f"Chuyển sang cấp độ {next_lvl}"):
                            update_mastery(username, n_id, next_lvl)
                            st.rerun()
                    with col_act3:
                        if st.button("🗑️", key=f"del_btn_{n_id}", help="Xóa ghi chú này"):
                            delete_note(username, n_id)
                            st.toast("Đã xóa ghi chú khỏi kho Second Brain!")
                            st.rerun()

                # 3 View Modes trong từng Note
                view_mode = st.radio(
                    "Chế độ hiển thị:",
                    ["💡 Phân Rã Nguyên Tử (Atomic View)", "🔗 Mạng Lưới Kết Nối Chéo (Latticework)", "📄 Văn Bản Gốc (Raw Text)"],
                    key=f"view_mode_{n_id}",
                    horizontal=True,
                )

                if "Phân Rã Nguyên Tử" in view_mode:
                    c_n1, c_n2 = st.columns([3, 2])
                    with c_n1:
                        st.markdown(
                            f"""<div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #38bdf8; margin-bottom: 10px;">
                            <b style="color: #38bdf8;">💡 Bản chất cốt lõi:</b><br/>{note.get('essence')}
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        st.markdown("**🧩 Khái niệm nguyên tử:**")
                        for ac in note.get("atomic_concepts", []):
                            st.markdown(f"- {ac}")

                        st.markdown("**🪜 Khung hành động thực tế:**")
                        for act in note.get("actionable_steps", []):
                            st.markdown(f"- {act}")

                    with c_n2:
                        if note.get("metaphor"):
                            st.markdown(
                                f"""<div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 10px;">
                                <b style="color: #f59e0b;">🍲 Ẩn dụ trực quan:</b><br/>{note.get('metaphor')}
                                </div>""",
                                unsafe_allow_html=True,
                            )
                        st.markdown(f"**🛡️ Bẫy nhận thức:** *{note.get('traps_and_biases', 'None')}*")
                        if note.get("tags"):
                            st.write("🏷️ " + " ".join([f"`#{t}`" for t in note.get("tags", [])]))

                elif "Mạng Lưới Kết Nối Chéo" in view_mode:
                    c_net1, c_net2 = st.columns([1, 1])
                    with c_net1:
                        st.markdown("##### 🕸️ Mô hình tư duy & Nguyên lý đệ nhất")
                        m_list = note.get("mental_models_linked", [])
                        if m_list:
                            for m in m_list:
                                st.markdown(f"- 🧠 **{m}**")
                        else:
                            st.caption("Chưa gắn mô hình.")

                        p_list = note.get("first_principles_linked", [])
                        if p_list:
                            for p in p_list:
                                st.markdown(f"- 📚 *{p}*")

                        if note.get("cross_topic_connections"):
                            st.markdown("##### 🌐 Gợi ý ứng dụng liên ngành:")
                            st.info(note.get("cross_topic_connections"))

                    with c_net2:
                        st.markdown("##### 🔗 Các ghi chú có mối liên hệ chéo trong kho")
                        related_items = find_related_notes(username, n_id, limit=4)
                        if not related_items:
                            st.caption("Chưa có ghi chú khác cùng chủ đề hoặc trùng tag/mô hình trong kho.")
                        else:
                            for r_note, r_score, r_reasons in related_items:
                                st.markdown(f"- **{r_note.get('title')}** `(Tương đồng: {r_score}đ)`")
                                for reas in r_reasons:
                                    st.caption(f"  ↳ {reas}")

                else:
                    st.text_area(
                        "Toàn văn ghi chú gốc (được bảo tồn 100% nguyên vẹn):",
                        value=note.get("raw_content", ""),
                        height=250,
                        disabled=True,
                        key=f"raw_view_{n_id}",
                    )

                st.markdown("---")


# =============================================================================
# TAB 3: ÔN TẬP PHẢN XẠ ACTIVE RECALL & AI TỔNG HỢP GIAO THOA
# =============================================================================
with tab_recall:
    st.markdown("### 🎓 Rèn Luyện & Ôn Tập Chủ Động (Active Recall & Synthesis)")
    st.caption("Biến tri thức tích lũy thành phản xạ nhận thức tầng tiềm thức thay vì ảo tưởng ghi nhớ mặt chữ.")

    sub_r1, sub_r2 = st.tabs(["🎯 Thẻ Phản Xạ Nhận Thức (Active Recall)", "✨ AI Tổng Hợp Giao Thoa Tri Thức"])

    # SUB-TAB 1: Active Recall Flashcards
    with sub_r1:
        st.markdown("#### 🎯 Thử Thách Ôn Tập Không Giở Sách (Active Recall Cards)")
        st.info("💡 Hệ thống tự động trích xuất các câu hỏi thử thách từ chính kho ghi chú của bạn để bạn tự kiểm định xem mình có đang hiểu sâu hay bị 'nghẽn' như Feynman đã cảnh báo.")

        c_rf1, _ = st.columns([2, 3])
        with c_rf1:
            if st.button("🎲 Rút Bộ Câu Hỏi Ôn Tập Mới", key="btn_draw_flashcards"):
                st.session_state["active_flashcards"] = get_random_flashcards(username, limit=4)
                st.rerun()

        flashcards = st.session_state.get("active_flashcards")
        if not flashcards:
            flashcards = get_random_flashcards(username, limit=4)
            st.session_state["active_flashcards"] = flashcards

        if not flashcards:
            st.warning("Kho ghi chú hiện tại chưa có câu hỏi ôn tập. Hãy thêm ghi chú mới tại Tab 1 để AI tự động sinh câu hỏi.")
        else:
            for idx, card in enumerate(flashcards, 1):
                with st.container():
                    st.markdown(
                        f"""<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 12px;">
                        <span style="color: #38bdf8; font-weight: bold;">Câu hỏi #{idx}</span> · <span style="color: #94a3b8;">{card.get('domain')}</span><br/>
                        <h4 style="margin: 8px 0; color: #f8fafc;">❓ {card.get('question')}</h4>
                        <span style="color: #64748b; font-size: 0.9em;">Thuộc ghi chú: <b>{card.get('note_title')}</b></span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    with st.expander("👁️ Lật thẻ xem Bản chất cốt lõi & Đáp án gợi ý"):
                        st.markdown(f"**💡 Bản chất cốt lõi:** {card.get('essence')}")
                        st.success(f"**🎯 Gợi ý trả lời trôi chảy:** {card.get('answer')}")

    # SUB-TAB 2: AI Cross-Synthesis
    with sub_r2:
        st.markdown("#### ✨ AI Kiến Trúc Sư: Tổng Hợp Giao Thoa Giữa Các Ghi Chú")
        st.info("💡 Chọn 2 hoặc nhiều ghi chú trong kho để AI phân tích mối liên hệ đan chéo, điểm cộng hưởng (Latticework Synergy) và tạo ra khung hành động kết hợp.")

        user_notes_all = get_user_notes(username)
        if len(user_notes_all) < 2:
            st.warning("Cần tối thiểu 2 ghi chú trong kho để thực hiện tính năng tổng hợp giao thoa tri thức.")
        else:
            note_options_map = {f"[{n.get('id')}] {n.get('title')}": n for n in user_notes_all}
            selected_note_keys = st.multiselect(
                "Chọn 2 đến 5 ghi chú cần phân tích giao thoa:",
                options=list(note_options_map.keys()),
                default=list(note_options_map.keys())[:2],
                max_selections=5,
                key="synthesis_note_picker",
            )

            focus_q = st.text_input(
                "Định hướng bài toán cần giải quyết (Tùy chọn):",
                placeholder="Ví dụ: Làm thế nào kết hợp Kỹ thuật Feynman với Quản trị rủi ro để cải thiện hiệu suất?",
                key="synthesis_focus_q",
            )

            if st.button("🚀 Phân Tích Giao Thoa & Sức Mạnh Cộng Hưởng", type="primary", use_container_width=True):
                if len(selected_note_keys) < 2:
                    st.warning("Vui lòng chọn ít nhất 2 ghi chú.")
                else:
                    target_notes = [note_options_map[k] for k in selected_note_keys]
                    with st.spinner("🧠 AI đang tổng hợp các tầng nhận thức và kết nối các mô hình..."):
                        synthesis_result = synthesize_cross_notes(
                            api_keys=active_keys,
                            model_name=model_choice,
                            notes_list=target_notes,
                            user_query=focus_q.strip(),
                        )
                        st.session_state["latest_synthesis_result"] = synthesis_result

            res = st.session_state.get("latest_synthesis_result")
            if res:
                st.divider()
                st.markdown("### 🌐 Báo Cáo Giao Thoa Tri Thức Đa Chiều")
                st.markdown(res)


# =============================================================================
# TAB 4: BẢN ĐỒ TRI THỨC & XUẤT DỮ LIỆU
# =============================================================================
with tab_graph:
    st.markdown("### 🕸️ Toàn Cảnh Kho Tri Thức & Công Cụ Xuất Dữ Liệu")

    all_notes = get_user_notes(username)
    total_notes = len(all_notes)
    mastered_count = sum(1 for n in all_notes if n.get("mastery_level") == 3)
    fav_count = sum(1 for n in all_notes if n.get("favorite"))
    all_tags = get_all_vault_tags(username)
    all_models = get_all_vault_models(username)

    # Thống kê tổng quan
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.metric("Tổng số Ghi chú", total_notes)
    with c_m2:
        st.metric("Đã Nhuần nhuyễn (Mastered)", f"{mastered_count}/{total_notes}")
    with c_m3:
        st.metric("Mô hình đã kết nối", len(all_models))
    with c_m4:
        st.metric("Thẻ phân loại (Tags)", len(all_tags))

    st.divider()

    c_g1, c_g2 = st.columns([1, 1])
    with c_g1:
        st.markdown("##### 📊 Phân Bổ Theo Lĩnh Vực")
        domain_counts = {}
        for n in all_notes:
            d = n.get("domain", "Khác")
            domain_counts[d] = domain_counts.get(d, 0) + 1
        st.bar_chart(domain_counts)

    with c_g2:
        st.markdown("##### 🧠 Top Mô Hình Tư Duy Xuất Hiện Nhiều Nhất")
        model_counts = {}
        for n in all_notes:
            for m in n.get("mental_models_linked", []):
                model_counts[m] = model_counts.get(m, 0) + 1
        if model_counts:
            sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            for m_name, cnt in sorted_models:
                st.markdown(f"- **{m_name}**: `{cnt} ghi chú`")
        else:
            st.caption("Chưa có mô hình nào được liên kết.")

    st.divider()
    st.markdown("### 📥 Xuất Dữ Liệu & Sao Lưu Vĩnh Viễn")
    st.write("Xuất kho tri thức sang định dạng Markdown Zettelkasten chuẩn hai chiều `[[Wiki-links]]` (tương thích Obsidian, Logseq, Notion) hoặc file JSON sao lưu dự phòng:")

    c_exp1, c_exp2 = st.columns(2)
    with c_exp1:
        md_content = export_notes_to_markdown(username)
        st.download_button(
            label="📥 Tải Về File Markdown Zettelkasten (.md)",
            data=md_content,
            file_name=f"Second_Brain_Vault_{username}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with c_exp2:
        json_content = export_notes_to_json(username)
        st.download_button(
            label="📥 Tải Về Bản Sao Lưu JSON (.json)",
            data=json_content,
            file_name=f"Second_Brain_Backup_{username}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
