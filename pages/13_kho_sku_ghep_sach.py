# -*- coding: utf-8 -*-
"""
Trang: Kho Hồ Sơ SKU Tri Thức Nguyên Bản & Trình Ghép Sách (Book Compiler)
- Mô hình Amazon Fulfillment SKU: Quản trị tri thức dạng kiện hàng nguyên tử đa chiều.
- Zero-Paraphrase Golden Rule: Bảo tồn 100% văn bản gốc, cấm sửa đổi/tóm tắt văn phong tác giả.
- Book Assembler: Bốc dỡ các SKU theo cây mục lục và xuất bản thảo sách hoàn chỉnh.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

from utils.app_common import bootstrap
from utils.sku_warehouse import (
    SKU_DOMAINS,
    get_user_skus,
    create_sku,
    update_sku,
    delete_sku,
    get_sku_by_id,
    search_filter_skus,
    get_all_sku_domains,
    get_all_sku_tags,
    get_all_sku_authors,
    get_user_book_projects,
    create_book_project,
    update_book_project,
    delete_book_project,
    get_book_project_by_id,
    add_chapter_to_book,
    add_section_to_chapter,
    ai_tag_sku_metadata,
    compile_book_manuscript,
)

# -----------------------------------------------------------------------------
# Bootstrap & Auth
# -----------------------------------------------------------------------------
ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

# -----------------------------------------------------------------------------
# Header & Concept Banner
# -----------------------------------------------------------------------------
st.title("📦 Kho SKU Tri Thức Nguyên Bản & Trình Ghép Sách")
st.caption(
    "Mô hình Amazon Fulfillment SKU · 100% Bảo toàn nguyên văn (Zero-Paraphrase) · "
    "Định vị mục lục & Biên soạn bản thảo sách tự động"
)

with st.expander("💡 **Triết Lý Vận Hành: Kho Hàng SKU & Bảo Toàn Nguyên Bản 100%**", expanded=False):
    st.markdown(
        """
        - **1. Kiện hàng nguyên niêm phong (Raw Verbatim)**: Đọc sách, tài liệu, bài nghiên cứu từ hàng chục nguồn khác nhau.
          Văn bản gốc khi đưa vào kho được **khóa bất biến 100%** (từng câu chữ, số liệu, văn phong tác giả). 
          Tuyệt đối không để AI hay hệ thống tự ý tóm tắt làm sai lệch, thất thoát chiều sâu tư liệu.
        - **2. Quét mã vạch & Phân kệ SKU (Metadata Tagging)**: AI chỉ làm nhiệm vụ thủ kho: phân tích để gắn mã SKU, 
          gợi ý Lĩnh vực, Chủ đề, Thẻ tag và vị trí Chương/Tiết sách tiềm năng.
        - **3. Bốc hàng ghép Sách (Book Compiler & Assembler)**: Bạn chỉ cần xây dựng Dàn ý cuốn sách (Outline). 
          Khi cần xuất bản thảo, hệ thống sẽ bốc toàn bộ các SKU nguyên bản vào đúng vị trí mục lục, 
          kèm đầy đủ chú thích nguồn và ghi chú chỉ đạo của bạn để tạo ra cuốn sách hoàn chỉnh!
        """
    )

# -----------------------------------------------------------------------------
# 4 Main Tabs
# -----------------------------------------------------------------------------
tab_capture, tab_inventory, tab_outliner, tab_compile = st.tabs([
    "📥 Nhập Kho SKU (Fast Capture)",
    "🏢 Kho Hàng & Tra Cứu (Inventory)",
    "📑 Quản Lý Mục Lục Sách (Outliner)",
    "🚀 Xuất Bản Thảo Hoàn Chỉnh (Compiler)",
])


# =============================================================================
# TAB 1: NHẬP KHO SKU (FAST CAPTURE & AUTO-TAG)
# =============================================================================
with tab_capture:
    st.markdown("### 📥 Thu Nạp Trích Đoạn Vào Kho Hồ Sơ SKU")
    st.info(
        "📌 **Quy tắc bảo tồn nguyên bản**: Hãy dán trích đoạn văn bản bạn tâm đắc từ sách, bài báo hoặc nghiên cứu. "
        "Hệ thống sẽ bảo toàn 100% từng câu chữ gốc mà không viết lại hay tóm tắt."
    )

    col_c1, col_c2 = st.columns([1.6, 1.0])

    with col_c1:
        raw_text_input = st.text_area(
            "📄 Văn bản trích dẫn nguyên gốc (Bảo toàn 100%):",
            height=260,
            placeholder="Dán đoạn văn bản nguyên gốc vào đây... (Ví dụ: Một trích dẫn của Charlie Munger, đoạn văn trong sách giáo khoa, số liệu bài báo...)",
            key="sku_capture_raw_text"
        )

        st.markdown("##### 🏷️ Thông Tin Nguồn Gốc (Citation)")
        col_src1, col_src2 = st.columns(2)
        with col_src1:
            src_author = st.text_input("Tác giả / Diễn giả:", placeholder="VD: Charlie Munger, Richard Feynman...", key="sku_src_author")
            src_book = st.text_input("Tên sách / Bài báo / Báo cáo:", placeholder="VD: Poor Charlie's Almanack, Six Easy Pieces...", key="sku_src_book")
        with col_src2:
            src_page = st.text_input("Trang / Chương / Vị trí:", placeholder="VD: Tr. 142 hoặc Chap 4...", key="sku_src_page")
            src_url = st.text_input("Đường link URL (nếu có):", placeholder="https://...", key="sku_src_url")

    with col_c2:
        st.markdown("##### 🤖 Quét Mã Vạch Tự Động (AI Auto-Tagger)")
        st.caption("AI chỉ phân tích để trích xuất Metadata. Tuyệt đối không can thiệp nội dung gốc.")

        if st.button("🔍 Quét Mã Vạch & Gợi Ý Nhãn (AI)", use_container_width=True, type="primary"):
            if not raw_text_input.strip():
                st.warning("Vui lòng dán văn bản trích dẫn trước khi quét mã vạch!")
            else:
                with st.spinner("Thủ kho AI đang quét mã vạch & phân tích tọa độ..."):
                    ai_res = ai_tag_sku_metadata(raw_text_input, active_keys, model_choice)
                    st.session_state["sku_ai_suggestion"] = ai_res
                    st.success("✅ Quét mã vạch thành công!")

        ai_sug = st.session_state.get("sku_ai_suggestion", {})

        sug_title = ai_sug.get("suggested_title", "")
        sug_domain = ai_sug.get("domain", SKU_DOMAINS[0])
        sug_topic = ai_sug.get("topic", "")
        sug_tags = ", ".join(ai_sug.get("tags", []))
        sug_chap = ai_sug.get("suggested_chapter", "")
        sug_sec = ai_sug.get("suggested_section", "")

        sku_title = st.text_input(
            "Tiêu đề định danh SKU:",
            value=sug_title,
            placeholder="Tiêu đề ngắn nhận diện trích đoạn",
            key="sku_capture_title"
        )

        domain_idx = 0
        if sug_domain in SKU_DOMAINS:
            domain_idx = SKU_DOMAINS.index(sug_domain)

        sku_domain = st.selectbox(
            "Lĩnh vực lưu trữ:",
            SKU_DOMAINS,
            index=domain_idx,
            key="sku_capture_domain"
        )

        sku_topic = st.text_input(
            "Chủ đề nhánh:",
            value=sug_topic,
            placeholder="VD: Tư duy đảo ngược, Định giá DCF...",
            key="sku_capture_topic"
        )

        sku_tags_str = st.text_input(
            "Thẻ Tags (phân cách bằng dấu phẩy):",
            value=sug_tags,
            placeholder="VD: munger, inversion, mental-models...",
            key="sku_capture_tags"
        )

    st.markdown("---")
    st.markdown("#### 📚 Định Vị Mục Lục Sách & Ghi Chú Riêng (Tùy chọn)")
    
    # Lấy danh sách dự án sách hiện có
    book_projects = get_user_book_projects(username)
    project_options = {"(Chưa gán vào sách)": ""}
    for p in book_projects:
        project_options[f"📖 {p.get('title')}"] = p.get("project_id")

    col_bk1, col_bk2, col_bk3 = st.columns([1.2, 1.2, 0.8])
    with col_bk1:
        chosen_proj_label = st.selectbox("Dự án Sách mục tiêu:", list(project_options.keys()), key="sku_target_project_select")
        chosen_project_id = project_options[chosen_proj_label]

    chosen_proj = get_book_project_by_id(username, chosen_project_id) if chosen_project_id else None
    
    # Options chương & tiết
    chapter_options = {"(Không chọn chương)": ("", "")}
    section_options = {"(Không chọn tiết)": ("", "")}

    if chosen_proj:
        for c in chosen_proj.get("outline", []):
            c_id = c.get("chapter_id", "")
            c_title = c.get("chapter_title", "")
            chapter_options[f"📂 {c_title}"] = (c_id, c_title)

    with col_bk2:
        chosen_chap_label = st.selectbox("Chương mục trong sách:", list(chapter_options.keys()), key="sku_target_chap_select")
        chosen_chap_id, chosen_chap_title = chapter_options[chosen_chap_label]

    if chosen_proj and chosen_chap_id:
        for c in chosen_proj.get("outline", []):
            if c.get("chapter_id") == chosen_chap_id:
                for s in c.get("sections", []):
                    s_id = s.get("section_id", "")
                    s_title = s.get("section_title", "")
                    section_options[f"📄 {s_title}"] = (s_id, s_title)

    with col_bk3:
        chosen_sec_label = st.selectbox("Tiết chi tiết:", list(section_options.keys()), key="sku_target_sec_select")
        chosen_sec_id, chosen_sec_title = section_options[chosen_sec_label]

    col_note, col_order = st.columns([3, 1])
    with col_note:
        sku_user_note = st.text_input(
            "💡 Ghi chú / Chỉ đạo của tác giả (sẽ xuất hiện dưới dạng bình luận riêng, không đụng vào văn bản gốc):",
            placeholder="VD: Dùng làm ví dụ mở đầu cho phần phản biện tương suy...",
            key="sku_capture_note"
        )
    with col_order:
        sku_sort_order = st.number_input("Thứ tự trong tiết:", min_value=1, max_value=100, value=1, step=1, key="sku_capture_order")

    if st.button("📦 Lưu Trích Đoạn Vào Kho SKU", type="primary", use_container_width=True):
        if not raw_text_input.strip():
            st.error("Vui lòng nhập nội dung trích đoạn gốc trước khi lưu!")
        else:
            tag_list = [t.strip() for t in sku_tags_str.split(",") if t.strip()]
            src_dict = {
                "author": src_author.strip(),
                "book_title": src_book.strip(),
                "page": src_page.strip(),
                "url": src_url.strip(),
                "collected_date": datetime.now().strftime("%Y-%m-%d")
            }
            new_item = create_sku(
                username=username,
                raw_content=raw_text_input,
                title=sku_title,
                source=src_dict,
                domain=sku_domain,
                topic=sku_topic,
                tags=tag_list,
                book_project_id=chosen_project_id,
                target_chapter_id=chosen_chap_id,
                target_chapter=chosen_chap_title,
                target_section_id=chosen_sec_id,
                target_section=chosen_sec_title,
                sort_order=sku_sort_order,
                user_note=sku_user_note
            )
            st.success(f"🎉 Đã lưu thành công kiện hàng: **{new_item['sku_id']}** ({new_item['title']})")
            st.session_state.pop("sku_ai_suggestion", None)
            st.rerun()


# =============================================================================
# TAB 2: KHO HÀNG & TRA CỨU (WAREHOUSE INVENTORY)
# =============================================================================
with tab_inventory:
    all_skus = get_user_skus(username)
    all_projects = get_user_book_projects(username)
    proj_map = {p.get("project_id"): p.get("title") for p in all_projects}

    st.markdown("### 🏢 Quản Trị Kho Bãi & Tra Cứu Kiện Hàng SKU")

    # Metrics tổng quan kho
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("📦 Tổng Số SKU", f"{len(all_skus)} kiện")
    with m2:
        assigned_count = sum(1 for s in all_skus if s.get("book_project_id"))
        st.metric("📚 Đã Gán Vào Sách", f"{assigned_count} SKU")
    with m3:
        unique_authors = len({s.get("source", {}).get("author") for s in all_skus if s.get("source", {}).get("author")})
        st.metric("👤 Số Tác Giả Gốc", f"{unique_authors} người")
    with m4:
        unique_tags = len(get_all_sku_tags(all_skus)) - 1
        st.metric("🏷️ Số Thẻ Phân Loại", f"{max(0, unique_tags)} thẻ")

    st.markdown("---")

    # Bộ lọc ma trận đa chiều
    st.markdown("##### 🔍 Bộ Lọc Ma Trận Đa Chiều (Faceted Search)")
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 1, 1])

    with f_col1:
        search_kw = st.text_input("🔎 Tìm kiếm từ khoá trong nội dung gốc:", placeholder="Từ khoá, tác giả, tiêu đề...", key="inv_search_kw")
    with f_col2:
        filter_domain = st.selectbox("Lĩnh vực:", get_all_sku_domains(all_skus), key="inv_filter_domain")
    with f_col3:
        filter_tag = st.selectbox("Thẻ Tag:", get_all_sku_tags(all_skus), key="inv_filter_tag")
    with f_col4:
        proj_opts = ["Tất cả"] + list(proj_map.values())
        filter_proj_title = st.selectbox("Dự án Sách:", proj_opts, key="inv_filter_proj")

    # Map project title sang id
    filter_proj_id = None
    if filter_proj_title != "Tất cả":
        for pid, ptitle in proj_map.items():
            if ptitle == filter_proj_title:
                filter_proj_id = pid
                break

    filtered_skus = search_filter_skus(
        all_skus,
        query=search_kw,
        domain=filter_domain,
        tag=filter_tag,
        book_project_id=filter_proj_id
    )

    st.caption(f"Hiển thị **{len(filtered_skus)}** / {len(all_skus)} kiện hàng phù hợp")

    if not filtered_skus:
        st.info("Không có kiện hàng nào khớp với điều kiện lọc.")
    else:
        for idx, sku in enumerate(filtered_skus):
            sku_id = sku.get("sku_id", f"SKU-{idx}")
            title = sku.get("title", "Không tiêu đề")
            domain = sku.get("domain", "Chưa phân loại")
            topic = sku.get("topic", "")
            source = sku.get("source", {})
            author = source.get("author", "Khuyết danh")
            book_name = source.get("book_title", "")
            raw_text = sku.get("raw_content", "")
            user_note = sku.get("user_note", "")
            tags = sku.get("tags", [])
            proj_id = sku.get("book_project_id", "")
            target_chap = sku.get("target_chapter", "")
            target_sec = sku.get("target_section", "")

            with st.container(border=True):
                c_top1, c_top2 = st.columns([3, 1])
                with c_top1:
                    st.markdown(f"#### 🏷️ `[{sku_id}]` {title}")
                    st.caption(f"**Lĩnh vực:** {domain} · **Chủ đề:** {topic or 'Tổng quát'} · **Tác giả:** {author}")
                with c_top2:
                    if proj_id and proj_id in proj_map:
                        st.badge(f"📖 {proj_map[proj_id]}")
                    else:
                        st.caption("*(Chưa gán vào sách)*")

                # Trích dẫn nguyên bản (Bảo toàn 100%)
                with st.expander("📄 **Xem Văn Bản Gốc 100% (Verbatim)**", expanded=True):
                    st.markdown(f"> {raw_text}")
                    st.markdown(
                        f"*(Nguồn: **{author}** · Tác phẩm: *{book_name or 'N/A'}* · Trang: {source.get('page', 'N/A')})*"
                    )

                if user_note:
                    st.info(f"💡 **Ghi chú tác giả:** {user_note}")

                if tags:
                    tag_badges = " ".join([f"`#{t}`" for t in tags])
                    st.markdown(f"**Tags:** {tag_badges}")

                if target_chap or target_sec:
                    st.caption(f"📍 **Vị trí mục lục:** {target_chap} ➔ {target_sec} (Thứ tự: {sku.get('sort_order', 1)})")

                # Action buttons
                act1, act2, act3 = st.columns([1.2, 1.2, 1.2])
                with act1:
                    st.code(raw_text, language=None)
                with act2:
                    # Chuyển / Gán vào sách nhanh
                    with st.popover("⚙️ Gán vị trí sách"):
                        st.markdown(f"**Gán SKU `{sku_id}` vào sách:**")
                        new_p = st.selectbox("Chọn sách:", list(project_options.keys()), key=f"quick_proj_{sku_id}")
                        new_pid = project_options[new_p]
                        sel_p_obj = get_book_project_by_id(username, new_pid) if new_pid else None
                        
                        ch_opts = {"(Chọn chương)": ("", "")}
                        if sel_p_obj:
                            for c in sel_p_obj.get("outline", []):
                                ch_opts[c.get("chapter_title")] = (c.get("chapter_id"), c.get("chapter_title"))
                        new_ch_label = st.selectbox("Chọn chương:", list(ch_opts.keys()), key=f"quick_chap_{sku_id}")
                        new_cid, new_ctitle = ch_opts[new_ch_label]

                        sec_opts = {"(Chọn tiết)": ("", "")}
                        if sel_p_obj and new_cid:
                            for c in sel_p_obj.get("outline", []):
                                if c.get("chapter_id") == new_cid:
                                    for s in c.get("sections", []):
                                        sec_opts[s.get("section_title")] = (s.get("section_id"), s.get("section_title"))
                        new_sec_label = st.selectbox("Chọn tiết:", list(sec_opts.keys()), key=f"quick_sec_{sku_id}")
                        new_sid, new_stitle = sec_opts[new_sec_label]

                        new_order = st.number_input("Thứ tự:", min_value=1, max_value=100, value=sku.get("sort_order", 1), key=f"quick_ord_{sku_id}")

                        if st.button("Lưu Vị Trí Mới", key=f"btn_save_loc_{sku_id}"):
                            update_sku(username, sku_id, {
                                "book_project_id": new_pid,
                                "target_chapter_id": new_cid,
                                "target_chapter": new_ctitle,
                                "target_section_id": new_sid,
                                "target_section": new_stitle,
                                "sort_order": new_order
                            })
                            st.success("Đã cập nhật vị trí sách!")
                            st.rerun()

                with act3:
                    if st.button("🗑️ Xoá SKU", key=f"del_{sku_id}"):
                        delete_sku(username, sku_id)
                        st.toast(f"Đã xoá {sku_id}")
                        st.rerun()


# =============================================================================
# TAB 3: QUẢN LÝ MỤC LỤC SÁCH (BOOK OUTLINER)
# =============================================================================
with tab_outliner:
    st.markdown("### 📑 Kiến Tạo Cây Mục Lục Sách & Phân Bổ Kiện Hàng")
    st.caption("Thiết lập khung xương cuốn sách (Chương ➔ Tiết) và kiểm tra các SKU tương ứng.")

    user_projects = get_user_book_projects(username)

    col_bp1, col_bp2 = st.columns([2, 1])

    with col_bp1:
        proj_dict = {p.get("title"): p.get("project_id") for p in user_projects}
        sel_proj_title = st.selectbox("📚 Chọn dự án sách đang làm việc:", list(proj_dict.keys()), key="outliner_active_proj")
        active_pid = proj_dict.get(sel_proj_title, "")
        active_proj = get_book_project_by_id(username, active_pid)

    with col_bp2:
        with st.popover("➕ Tạo Dự Án Sách Mới"):
            st.markdown("##### 📖 Khởi Tạo Dự Án Sách")
            new_bk_title = st.text_input("Tựa đề sách:", placeholder="VD: Nghệ Thuật Phản Biện & First Principles")
            new_bk_sub = st.text_input("Phụ đề:", placeholder="VD: Từ nguyên lý đến thực thi")
            new_bk_auth = st.text_input("Tác giả / Chủ biên:", value=display_name)
            new_bk_desc = st.text_area("Mô tả / Lời tựa ngắn:")

            if st.button("Tạo Dự Án", type="primary"):
                if not new_bk_title.strip():
                    st.error("Vui lòng nhập tựa đề sách!")
                else:
                    create_book_project(
                        username=username,
                        title=new_bk_title,
                        subtitle=new_bk_sub,
                        author=new_bk_auth,
                        description=new_bk_desc
                    )
                    st.success("Đã tạo dự án sách mới!")
                    st.rerun()

    if active_proj:
        st.markdown(f"#### 📖 Bản Thảo: **{active_proj.get('title')}**")
        if active_proj.get("subtitle"):
            st.caption(f"*{active_proj.get('subtitle')}* · Tác giả: **{active_proj.get('author')}**")

        outline = active_proj.get("outline", [])
        all_skus = get_user_skus(username)
        proj_skus = [s for s in all_skus if s.get("book_project_id") == active_pid]

        st.markdown("---")

        # Thêm Chương mới
        with st.expander("➕ **Thêm Chương Mới Vào Mục Lục**", expanded=False):
            new_chap_title = st.text_input("Tên chương mới:", placeholder="VD: Chương 4: Tư Duy Xác Suất & Định Lý Bayes", key="new_chap_input")
            if st.button("Thêm Chương", key="btn_add_chap"):
                if new_chap_title.strip():
                    add_chapter_to_book(username, active_pid, new_chap_title)
                    st.success(f"Đã thêm: {new_chap_title}")
                    st.rerun()

        # Hiển thị Cây Mục Lục chi tiết
        for idx_c, chap in enumerate(outline, 1):
            c_id = chap.get("chapter_id", "")
            c_title = chap.get("chapter_title", "")

            with st.container(border=True):
                col_ch1, col_ch2 = st.columns([3, 1])
                with col_ch1:
                    st.markdown(f"### 📂 {c_title}")
                with col_ch2:
                    # Thêm tiết vào chương
                    with st.popover("➕ Thêm Tiết"):
                        new_sec_title = st.text_input(f"Tên tiết con của '{c_title}':", key=f"sec_in_{c_id}")
                        if st.button("Thêm Tiết Này", key=f"btn_sec_add_{c_id}"):
                            if new_sec_title.strip():
                                add_section_to_chapter(username, active_pid, c_id, new_sec_title)
                                st.rerun()

                # Danh sách Tiết
                sections = chap.get("sections", [])
                for idx_s, sec in enumerate(sections, 1):
                    s_id = sec.get("section_id", "")
                    s_title = sec.get("section_title", "")

                    # Lọc SKU gán cho tiết này
                    sec_skus = [
                        s for s in proj_skus
                        if (s.get("target_section_id") == s_id or s.get("target_section") == s_title)
                    ]
                    sec_skus.sort(key=lambda x: int(x.get("sort_order", 1)))

                    st.markdown(f"##### 📄 {s_title} `({len(sec_skus)} SKU)`")

                    if not sec_skus:
                        st.caption("*(Chưa có trích đoạn nào được gán vào tiết này. Hãy vào Tab 1 hoặc Tab 2 để gán)*")
                    else:
                        for s_item in sec_skus:
                            sku_item_id = s_item.get("sku_id")
                            item_title = s_item.get("title")
                            item_order = s_item.get("sort_order", 1)
                            item_auth = s_item.get("source", {}).get("author", "N/A")

                            col_sku1, col_sku2, col_sku3 = st.columns([3, 1, 0.6])
                            with col_sku1:
                                st.markdown(f"- **`#{item_order}`** `[{sku_item_id}]` **{item_title}** *(Nguồn: {item_auth})*")
                            with col_sku2:
                                # Điều chỉnh số thứ tự
                                new_ord = st.number_input(
                                    "Thứ tự:",
                                    min_value=1,
                                    max_value=100,
                                    value=int(item_order),
                                    key=f"ord_edit_{sku_item_id}",
                                    label_visibility="collapsed"
                                )
                                if new_ord != item_order:
                                    update_sku(username, sku_item_id, {"sort_order": new_ord})
                                    st.rerun()
                            with col_sku3:
                                if st.button("❌", key=f"detach_{sku_item_id}", help="Bóc khỏi tiết này"):
                                    update_sku(username, sku_item_id, {
                                        "book_project_id": "",
                                        "target_chapter_id": "",
                                        "target_chapter": "",
                                        "target_section_id": "",
                                        "target_section": ""
                                    })
                                    st.rerun()


# =============================================================================
# TAB 4: XUẤT BẢN THẢO HOÀN CHỈNH (BOOK COMPILER & EXPORT)
# =============================================================================
with tab_compile:
    st.markdown("### 🚀 Biên Soạn & Xuất Bản Thảo Hoàn Chỉnh")
    st.caption("Bộ máy Book Assembler tự động bốc toàn bộ SKU theo thứ tự mục lục và tạo tài liệu Markdown/Word chuẩn mực.")

    user_projects = get_user_book_projects(username)
    proj_map_c = {p.get("title"): p.get("project_id") for p in user_projects}

    col_cp1, col_cp2 = st.columns([2, 1])
    with col_cp1:
        sel_c_proj_title = st.selectbox("Chọn dự án sách cần biên soạn:", list(proj_map_c.keys()), key="compile_active_proj")
        compile_pid = proj_map_c.get(sel_c_proj_title, "")

    with col_cp2:
        st.write("")
        st.write("")
        compile_btn = st.button("⚡ Bắt Đầu Biên Soạn Sách (Compile)", type="primary", use_container_width=True)

    if compile_pid:
        res = compile_book_manuscript(username, compile_pid)
        if res.get("success"):
            md_content = res.get("markdown", "")
            total_words = res.get("total_words", 0)
            total_skus = res.get("total_skus", 0)
            total_chaps = res.get("total_chapters", 0)

            st.markdown("---")
            # Metrics sách
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("📖 Số Chương Sách", f"{total_chaps} chương")
            with mc2:
                st.metric("📦 Tổng Số Trích Đoạn", f"{total_skus} SKU")
            with mc3:
                st.metric("📝 Tổng Độ Dài Bản Thảo", f"~{total_words:,} từ")

            st.markdown("#### 📥 Tải Về & Sao Chép Bản Thảo")
            file_name = f"{compile_pid}_manuscript.md"

            col_down1, col_down2 = st.columns([1, 1])
            with col_down1:
                st.download_button(
                    label="📄 Tải File Markdown Hoàn Chỉnh (.md)",
                    data=md_content,
                    file_name=file_name,
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True
                )
            with col_down2:
                if st.button("📋 Sao Chép Bản Thảo (Xem bên dưới)", use_container_width=True):
                    st.toast("Hãy chọn toàn bộ nội dung trong khung preview bên dưới để copy!")

            st.markdown("#### 🔍 Xem Trước Toàn Văn Bản Thảo (Live Preview)")
            with st.container(border=True):
                st.markdown(md_content)
        else:
            st.error(res.get("error", "Lỗi biên soạn sách!"))
