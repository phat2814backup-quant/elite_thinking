# -*- coding: utf-8 -*-
"""
Trang: Kho Mảnh Ghép Tri Thức & Đúc Kết Sách (Living Knowledge Vault & Book Studio)
- Triết lý Bottom-Up (Từ dưới lên): Lưu trữ nhanh chóng với 1-3 thẻ tag mà không cần tạo mục lục trước.
- Bảo toàn 100% nguyên văn (Zero-Paraphrase): Giữ nguyên vẹn câu chữ, số liệu của tài liệu gốc.
- Đúc kết sách thông minh (AI Book Synthesis): AI tự động phân cụm các mảnh ghép và kiến tạo cây mục lục sách hoàn chỉnh.
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
    get_all_sku_tags,
    get_user_book_projects,
    create_book_project,
    update_book_project,
    delete_book_project,
    get_book_project_by_id,
    add_chapter_to_book,
    add_section_to_chapter,
    compile_book_manuscript,
    ai_auto_cluster_and_build_book,
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
# Header & Philosophy
# -----------------------------------------------------------------------------
st.title("💎 Kho Mảnh Ghép Tri Thức & Đúc Kết Sách")
st.caption(
    "Tối thiểu thao tác lưu trữ (1–3 Thẻ Tag) · 100% Bảo toàn nguyên văn · "
    "AI tự động phân cụm & Đúc kết thành sách hoàn chỉnh"
)

with st.expander("💡 **Triết Lý Vận Hành: 'Gạch Xây Nhà' (Bottom-Up Knowledge Building)**", expanded=False):
    st.markdown(
        """
        - **1. Tích lũy không áp lực (Gom gạch)**: Khi đọc sách, xem biểu đồ hay tra cứu tài liệu (như file XAU/USD), 
          bạn chưa cần biết cuốn sách sau này sẽ có những chương gì. Chỉ cần dán đoạn văn hay và gõ **1–3 thẻ tag** 
          ngắn gọn (VD: `vàng, nến, marubozu`). Hệ thống bảo toàn **100% câu chữ gốc bất biến**.
        - **2. Đúc kết tự động (AI Kiến trúc sư)**: Khi bạn gom đủ 20–50 mảnh ghép, chỉ cần chọn một chủ đề (VD: `vàng`), 
          AI sẽ đọc toàn bộ các mảnh ghép đó và **tự động dựng Cây Mục Lục chuẩn mực** (từ Bản chất ➔ Kỹ thuật ➔ Quản trị rủi ro).
        - **3. Xuất bản sách một chạm**: Bạn chỉ cần duyệt lại dàn ý, tinh chỉnh nếu thích và tải về cuốn sách hoàn chỉnh!
        """
    )

# -----------------------------------------------------------------------------
# 3 Tabs Tinh Gọn
# -----------------------------------------------------------------------------
tab_capture, tab_vault, tab_book_studio = st.tabs([
    "📥 Gom Mảnh Ghép (Quick Capture)",
    "🗃️ Kho Mảnh Ghép & Thẻ Tag (Vault)",
    "📖 Đúc Kết Sách & Xuất Bản (Book Studio)",
])


# =============================================================================
# TAB 1: GOM MẢNH GHÉP SIÊU TỐC (ZERO-FRICTION CAPTURE)
# =============================================================================
with tab_capture:
    st.markdown("### 📥 Thu Nạp Mảnh Ghép Tri Thức")
    st.caption("Dán đoạn văn bạn tâm đắc. Chỉ cần 1 đến 3 từ khóa phân loại ngắn gọn.")

    # Form nhập tối giản
    raw_text = st.text_area(
        "📄 Nội dung trích dẫn (Bảo toàn 100% nguyên văn):",
        height=220,
        placeholder="Dán đoạn văn bản nguyên gốc vào đây... (Ví dụ: Một trích đoạn về CVD râu nến, quy luật quét thanh khoản XAU, bài học quản trị rủi ro...)",
        key="qc_raw_text"
    )

    col_tag, col_save = st.columns([3, 1])

    with col_tag:
        tags_input = st.text_input(
            "🏷️ Thẻ phân loại nhanh (1–3 từ khóa, cách nhau bằng dấu phẩy):",
            placeholder="VD: vàng, nến, marubozu  |  hoặc: vàng, định nghĩa  |  hoặc: rủi ro, stoploss",
            key="qc_tags_input"
        )

    # Phần mở rộng tùy chọn (không bắt buộc)
    with st.expander("➕ Ghi chú cá nhân & Nguồn gốc (Tùy chọn - có thể bỏ qua)", expanded=False):
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            user_personal_note = st.text_input(
                "💡 Ghi chú / Trải nghiệm cá nhân của bạn:",
                placeholder="VD: Áp dụng rất tốt ở khung H1 phiên Mỹ, kiểm chứng ngày 08/09...",
                key="qc_user_note"
            )
            src_author = st.text_input("Tác giả / Diễn giả:", placeholder="VD: Nassim Taleb, Elite Mentor...", key="qc_author")
        with c_opt2:
            src_book = st.text_input("Tên sách / Tài liệu:", placeholder="VD: XAU.pdf, Poor Charlie's Almanack...", key="qc_book")
            src_page_url = st.text_input("Trang hoặc Link URL:", placeholder="VD: Trang 15 hoặc https://...", key="qc_url")

    st.write("")
    if st.button("💾 LƯU MẢNH GHÉP VÀO KHO", type="primary", use_container_width=True):
        if not raw_text.strip():
            st.error("Vui lòng dán nội dung trích đoạn trước khi lưu!")
        else:
            # Xử lý tags
            raw_tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
            if not raw_tags:
                raw_tags = ["tri-thuc-chung"]

            # Tiêu đề tự động nếu không nhập
            words = raw_text.strip().split()
            auto_title = " ".join(words[:8]) + ("..." if len(words) > 8 else "")

            # Nguồn
            source_dict = {
                "author": src_author.strip() or "Khuyết danh",
                "book_title": src_book.strip(),
                "page": src_page_url.strip(),
                "url": src_page_url.strip() if src_page_url.startswith("http") else "",
                "collected_date": datetime.now().strftime("%Y-%m-%d")
            }

            new_sku = create_sku(
                username=username,
                raw_content=raw_text,
                title=auto_title,
                source=source_dict,
                tags=raw_tags,
                user_note=user_personal_note
            )

            st.success(f"🎉 Đã lưu mảnh ghép: **{new_sku['sku_id']}** với các thẻ `#{' #'.join(raw_tags)}`")
            st.toast("✅ Đã lưu thành công vào kho tri thức!")
            st.rerun()

    # Hiển thị 3 mảnh ghép vừa nạp gần nhất
    recent_skus = get_user_skus(username)[:3]
    if recent_skus:
        st.markdown("---")
        st.markdown("##### 🕒 Vừa lưu gần đây:")
        for r in recent_skus:
            r_tags = " ".join([f"`#{t}`" for t in r.get("tags", [])])
            with st.container(border=True):
                st.markdown(f"**`[{r.get('sku_id')}]`** {r_tags}")
                st.markdown(f"> {r.get('raw_content', '')[:160]}...")
                if r.get("user_note"):
                    st.caption(f"💡 *Ghi chú:* {r.get('user_note')}")


# =============================================================================
# TAB 2: KHO MẢNH GHÉP & TRA CỨU THEO THẺ TAG (VAULT)
# =============================================================================
with tab_vault:
    all_skus = get_user_skus(username)
    all_projects = get_user_book_projects(username)
    proj_map = {p.get("project_id"): p.get("title") for p in all_projects}

    st.markdown("### 🗃️ Kho Mảnh Ghép Tri Thức Đang Tích Lũy")

    # Metrics tổng quan
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("📦 Tổng Mảnh Ghép", f"{len(all_skus)} đoạn")
    with m2:
        assigned_count = sum(1 for s in all_skus if s.get("book_project_id"))
        st.metric("📖 Đã Đưa Vào Sách", f"{assigned_count} đoạn")
    with m3:
        all_tags_list = get_all_sku_tags(all_skus)
        unique_tags_count = max(0, len(all_tags_list) - 1)
        st.metric("🏷️ Số Thẻ Phân Loại", f"{unique_tags_count} thẻ")
    with m4:
        st.metric("📚 Dự Án Sách", f"{len(all_projects)} cuốn")

    st.markdown("---")

    # Đám mây Thẻ Tag (Tag Cloud)
    tag_counts: Dict[str, int] = {}
    for s in all_skus:
        for t in s.get("tags", []):
            if t:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    if tag_counts:
        st.markdown("##### 🏷️ Các Thẻ Nổi Bật Nhất (Bấm để lọc nhanh):")
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:12]
        tag_cols = st.columns(len(sorted_tags) if len(sorted_tags) < 6 else 6)
        for i, (t_name, count) in enumerate(sorted_tags[:6]):
            with tag_cols[i]:
                if st.button(f"#{t_name} ({count})", key=f"cloud_tag_{t_name}", use_container_width=True):
                    st.session_state["vault_filter_tag"] = t_name

    # Bộ lọc tra cứu
    st.markdown("##### 🔍 Tìm kiếm & Lọc")
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

    with f_col1:
        search_kw = st.text_input("🔎 Tìm từ khóa trong nội dung:", placeholder="VD: CVD, râu nến, thanh khoản, Taleb...", key="vault_search_kw")
    with f_col2:
        default_tag_idx = 0
        current_sess_tag = st.session_state.get("vault_filter_tag", "Tất cả")
        if current_sess_tag in all_tags_list:
            default_tag_idx = all_tags_list.index(current_sess_tag)
        filter_tag = st.selectbox("Lọc theo Thẻ Tag:", all_tags_list, index=default_tag_idx, key="vault_filter_tag_select")
    with f_col3:
        filter_status = st.selectbox("Tình trạng sách:", ["Tất cả", "Chưa gán vào sách", "Đã gán vào sách"], key="vault_filter_status")

    # Áp dụng bộ lọc
    filtered = search_filter_skus(all_skus, query=search_kw, tag=filter_tag)
    if filter_status == "Chưa gán vào sách":
        filtered = [s for s in filtered if not s.get("book_project_id")]
    elif filter_status == "Đã gán vào sách":
        filtered = [s for s in filtered if s.get("book_project_id")]

    st.caption(f"Hiển thị **{len(filtered)}** / {len(all_skus)} mảnh ghép phù hợp")

    if not filtered:
        st.info("Chưa có mảnh ghép nào phù hợp với điều kiện tìm kiếm.")
    else:
        for s in filtered:
            sku_id = s.get("sku_id")
            title = s.get("title")
            raw = s.get("raw_content", "")
            tags = s.get("tags", [])
            note = s.get("user_note", "")
            source = s.get("source", {})
            auth = source.get("author", "Khuyết danh")
            book_title = source.get("book_title", "")
            proj_id = s.get("book_project_id")

            with st.container(border=True):
                c_head1, c_head2 = st.columns([3, 1])
                with c_head1:
                    tag_badges = " ".join([f"`#{t}`" for t in tags])
                    st.markdown(f"#### 🏷️ `[{sku_id}]` {tag_badges}")
                with c_head2:
                    if proj_id and proj_id in proj_map:
                        st.badge(f"📖 {proj_map[proj_id]}")
                    else:
                        st.caption("*(Chưa gán vào sách)*")

                # Văn bản gốc 100%
                st.markdown(f"> {raw}")

                cite_info = f"*(Nguồn: **{auth}**"
                if book_title:
                    cite_info += f" · Tác phẩm: *{book_title}*"
                if source.get("page"):
                    cite_info += f" · Trang: {source.get('page')}"
                cite_info += ")*"
                st.caption(cite_info)

                if note:
                    st.info(f"💡 **Ghi chú của bạn:** {note}")

                if s.get("target_chapter") or s.get("target_section"):
                    st.caption(f"📍 **Vị trí trong sách:** {s.get('target_chapter')} ➔ {s.get('target_section')} (Thứ tự: {s.get('sort_order', 1)})")

                # Nút thao tác
                act1, act2 = st.columns([5, 1])
                with act1:
                    # Chỉnh sửa thẻ tag hoặc ghi chú
                    with st.popover("✏️ Sửa Tag & Ghi chú"):
                        new_tags_str = st.text_input("Sửa Thẻ Tag (phân cách bằng dấu phẩy):", value=", ".join(tags), key=f"edit_tags_{sku_id}")
                        new_note_str = st.text_input("Sửa Ghi chú cá nhân:", value=note, key=f"edit_note_{sku_id}")
                        if st.button("Lưu Thay Đổi", key=f"save_edit_{sku_id}"):
                            new_tag_list = [t.strip().lower() for t in new_tags_str.split(",") if t.strip()]
                            update_sku(username, sku_id, {
                                "tags": new_tag_list,
                                "user_note": new_note_str
                            })
                            st.success("Đã cập nhật!")
                            st.rerun()
                with act2:
                    if st.button("🗑️ Xoá", key=f"del_sku_{sku_id}", help="Xoá mảnh ghép này"):
                        delete_sku(username, sku_id)
                        st.toast("Đã xoá mảnh ghép")
                        st.rerun()


# =============================================================================
# TAB 3: ĐÚC KẾT SÁCH & XUẤT BẢN THẢO (AI BOOK STUDIO)
# =============================================================================
with tab_book_studio:
    st.markdown("### 📖 Đúc Kết Sách & Trình Biên Soạn Hoàn Chỉnh")
    st.caption("Biến hàng chục mảnh ghép rời rạc thành một cuốn sách có cấu trúc chặt chẽ.")

    # -------------------------------------------------------------------------
    # PHẦN 1: TỰ ĐỘNG ĐÚC KẾT TỪ THẺ TAG (AI SYNTHESIS)
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("#### 🪄 AI Tự Động Phân Cụm & Dựng Sách Từ Thẻ Tag")
        st.caption("Chọn 1 chủ đề (Thẻ Tag), AI sẽ đọc toàn bộ các mảnh ghép liên quan để thiết kế mục lục và phân bổ vào các chương.")

        col_syn1, col_syn2 = st.columns([1.5, 2])

        all_skus = get_user_skus(username)
        existing_tags = [t for t in get_all_sku_tags(all_skus) if t != "Tất cả"]

        with col_syn1:
            selected_tag_for_book = st.selectbox(
                "Chọn Thẻ Tag chủ đề để gom thành sách:",
                existing_tags if existing_tags else ["(Chưa có thẻ nào)"],
                key="syn_selected_tag"
            )

            # Đếm số lượng mảnh ghép khớp tag
            matched_count = 0
            if selected_tag_for_book and selected_tag_for_book != "(Chưa có thẻ nào)":
                matched_count = sum(1 for s in all_skus if selected_tag_for_book in [str(t).lower() for t in s.get("tags", [])])

            st.info(f"📊 Tìm thấy **{matched_count} mảnh ghép** mang thẻ `#{selected_tag_for_book}`")

        with col_syn2:
            default_book_title = f"Cẩm Nang Chuyên Đề: {selected_tag_for_book.upper()}" if selected_tag_for_book else "Bản Thảo Sách Mới"
            custom_book_title = st.text_input("Tựa đề cuốn sách mong muốn:", value=default_book_title, key="syn_book_title")
            custom_book_sub = st.text_input("Phụ đề (tùy chọn):", placeholder="VD: Từ nguyên lý cốt lõi đến chiến lược thực chiến", key="syn_book_sub")

        st.write("")
        if st.button("🪄 AI PHÂN CỤM & TỰ TẠO CÂY MỤC LỤC SÁCH", type="primary", use_container_width=True):
            if matched_count == 0:
                st.warning(f"Không có mảnh ghép nào chứa thẻ '{selected_tag_for_book}' để tạo sách!")
            else:
                with st.spinner("AI Tổng Biên Tập đang đọc các mảnh ghép, thiết kế Cây Mục Lục và phân bổ vào các chương..."):
                    res_build = ai_auto_cluster_and_build_book(
                        username=username,
                        target_tag=selected_tag_for_book,
                        book_title=custom_book_title,
                        book_subtitle=custom_book_sub,
                        author=display_name,
                        api_keys=active_keys,
                        model_name=model_choice
                    )

                if res_build.get("success"):
                    st.success(
                        f"🎉 Xuất sắc! Đã kiến tạo cuốn sách: **{custom_book_title}** "
                        f"với {res_build.get('total_chapters')} chương và phân bổ {res_build.get('assigned_count')} trích đoạn!"
                    )
                    st.rerun()
                else:
                    st.error(res_build.get("error", "Lỗi tạo sách!"))

    st.markdown("---")

    # -------------------------------------------------------------------------
    # PHẦN 2: QUẢN LÝ DÀN Ý & BIÊN TẬP SÁCH
    # -------------------------------------------------------------------------
    user_projects = get_user_book_projects(username)
    proj_map_studio = {p.get("title"): p.get("project_id") for p in user_projects}

    col_bp1, col_bp2 = st.columns([2.5, 1])
    with col_bp1:
        chosen_p_title = st.selectbox(
            "📚 Chọn Cuốn Sách đang làm việc:",
            list(proj_map_studio.keys()) if proj_map_studio else ["(Chưa có dự án sách)"],
            key="studio_active_project"
        )
        active_pid = proj_map_studio.get(chosen_p_title, "")
        active_project = get_book_project_by_id(username, active_pid)

    with col_bp2:
        with st.popover("➕ Tạo Cuốn Sách Thủ Công"):
            st.markdown("##### 📖 Tạo Dự Án Mới")
            manual_title = st.text_input("Tựa đề sách:", placeholder="VD: Nghệ Thuật Đầu Tư XAU")
            manual_sub = st.text_input("Phụ đề:", placeholder="VD: Cẩm nang thực chiến")
            if st.button("Tạo Sách", key="btn_create_manual_book"):
                if manual_title.strip():
                    create_book_project(username, title=manual_title, subtitle=manual_sub, author=display_name)
                    st.success("Đã tạo dự án sách mới!")
                    st.rerun()

    if active_project:
        st.markdown(f"### 📖 {active_project.get('title')}")
        if active_project.get("subtitle"):
            st.caption(f"*{active_project.get('subtitle')}* · Tác giả: **{active_project.get('author')}**")

        outline = active_project.get("outline", [])
        proj_skus = [s for s in all_skus if s.get("book_project_id") == active_pid]

        # Thêm chương mới
        with st.expander("➕ **Thêm Chương Mới Vào Cuốn Sách Này**", expanded=False):
            col_nc1, col_nc2 = st.columns([3, 1])
            with col_nc1:
                new_chap_name = st.text_input("Tên chương mới:", placeholder="VD: Chương 4: Quản Trị Rủi Ro Bất Đối Xứng", key="in_new_chap")
            with col_nc2:
                st.write("")
                if st.button("Thêm Chương", key="btn_add_new_chap", use_container_width=True):
                    if new_chap_name.strip():
                        add_chapter_to_book(username, active_pid, new_chap_name)
                        st.rerun()

        # Hiển thị Cây Mục Lục
        st.markdown("#### 📑 Cây Mục Lục Chi Tiết:")
        for idx_c, chap in enumerate(outline, 1):
            c_id = chap.get("chapter_id", "")
            c_title = chap.get("chapter_title", "")

            with st.container(border=True):
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"#### 📂 {c_title}")
                with col_c2:
                    with st.popover("➕ Thêm Tiết Con"):
                        new_sec_name = st.text_input(f"Tiết mới của '{c_title}':", key=f"in_sec_{c_id}")
                        if st.button("Lưu Tiết", key=f"btn_sec_{c_id}"):
                            if new_sec_name.strip():
                                add_section_to_chapter(username, active_pid, c_id, new_sec_name)
                                st.rerun()

                # Các tiết
                for sec in chap.get("sections", []):
                    s_id = sec.get("section_id", "")
                    s_title = sec.get("section_title", "")

                    sec_skus = [
                        s for s in proj_skus
                        if (s.get("target_section_id") == s_id or s.get("target_section") == s_title)
                    ]
                    sec_skus.sort(key=lambda x: int(x.get("sort_order", 1)))

                    st.markdown(f"##### 📄 {s_title} `({len(sec_skus)} trích đoạn)`")

                    if not sec_skus:
                        st.caption("*(Tiết này chưa có trích đoạn nào)*")
                    else:
                        for s_item in sec_skus:
                            sid = s_item.get("sku_id")
                            st_title = s_item.get("title")
                            st_order = s_item.get("sort_order", 1)
                            st_auth = s_item.get("source", {}).get("author", "N/A")

                            col_item1, col_item2, col_item3 = st.columns([3.5, 0.8, 0.5])
                            with col_item1:
                                st.markdown(f"- **`#{st_order}`** `[{sid}]` **{st_title}** *(Tác giả: {st_auth})*")
                            with col_item2:
                                new_o = st.number_input(
                                    "Thứ tự",
                                    min_value=1,
                                    max_value=100,
                                    value=int(st_order),
                                    key=f"sec_ord_{sid}",
                                    label_visibility="collapsed"
                                )
                                if new_o != st_order:
                                    update_sku(username, sid, {"sort_order": new_o})
                                    st.rerun()
                            with col_item3:
                                if st.button("❌", key=f"rm_sku_{sid}", help="Bóc khỏi tiết này"):
                                    update_sku(username, sid, {
                                        "book_project_id": "",
                                        "target_chapter_id": "",
                                        "target_chapter": "",
                                        "target_section_id": "",
                                        "target_section": ""
                                    })
                                    st.rerun()

        # ---------------------------------------------------------------------
        # PHẦN 3: BIÊN SOẠN & XUẤT BẢN THẢO HOÀN CHỈNH
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🚀 Biên Soạn & Xuất Bản Thảo Hoàn Chỉnh")
        st.caption("Tự động bốc tất cả các trích đoạn nguyên bản theo đúng thứ tự mục lục để tạo cuốn sách hoàn chỉnh.")

        if st.button("⚡ BẮT ĐẦU BIÊN SOẠN SÁCH (COMPILE)", type="primary", use_container_width=True):
            st.session_state["do_compile_pid"] = active_pid

        if st.session_state.get("do_compile_pid") == active_pid:
            res_compile = compile_book_manuscript(username, active_pid)
            if res_compile.get("success"):
                md_content = res_compile.get("markdown", "")
                total_words = res_compile.get("total_words", 0)
                total_skus = res_compile.get("total_skus", 0)
                total_chaps = res_compile.get("total_chapters", 0)

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("📖 Số Chương Sách", f"{total_chaps} chương")
                with col_m2:
                    st.metric("📦 Tổng Số Trích Đoạn", f"{total_skus} trích đoạn")
                with col_m3:
                    st.metric("📝 Tổng Độ Dài", f"~{total_words:,} từ")

                st.markdown("#### 📥 Tải Về Bản Thảo")
                file_name = f"{active_pid}_manuscript.md"
                st.download_button(
                    label="📄 Tải File Markdown Hoàn Chỉnh (.md)",
                    data=md_content,
                    file_name=file_name,
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True
                )

                st.markdown("#### 🔍 Xem Trước Bản Thảo Toàn Văn (Live Preview)")
                with st.container(border=True):
                    st.markdown(md_content)
            else:
                st.error(res_compile.get("error", "Lỗi biên soạn sách!"))
