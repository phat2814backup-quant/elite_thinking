# -*- coding: utf-8 -*-
"""
Module UI Rooms: Các phòng chức năng chuyên sâu độc lập
1. 📡 Máy Quét Đọc Vị Thế Cuộc (AI Macro Radar) — Chỉ gồm Tab Quét & Kho Lưu Trữ
2. 🎯 Phân Rã Thực Chiến & Nhật Ký Quyết Định — Chỉ gồm Tab Phân Rã & Kho Lưu Trữ
"""

from __future__ import annotations

import streamlit as st
from datetime import datetime

from core.macro_evolution import (
    SAMPLE_MACRO_TRENDS,
    analyze_macro_radar,
    scout_macro_trends,
    drill_down_macro_trend,
)
from core.problem_decomposition import (
    decompose_problem_with_ai,
    SAMPLE_DECOMPOSITION_CASES,
)
from core.farrow_engine import compress_with_farrow_ai
from core.export_utils import (
    sanitize_filename,
    export_macro_radar_to_markdown,
    export_problem_decomposition_to_markdown,
    export_farrow_compression_to_markdown,
)
from core.db_storage import (
    load_macro_scans,
    save_macro_scan,
    delete_macro_scan,
    load_macro_scout_trees,
    save_macro_scout_tree,
    update_tree_drilldown,
    delete_macro_scout_tree,
    load_problem_analyses,
    save_problem_analysis,
    delete_problem_analysis,
    load_compression_history,
    save_compression_record,
    delete_compression_record,
    get_user_decisions,
    create_decision_entry,
    resolve_decision_review,
    delete_decision_entry,
    get_decision_summary_stats,
    get_supabase_client,
    DECISION_CATEGORIES,
    REVIEW_INTERVALS,
    OUTCOME_RATINGS,
)


def render_macro_radar_result_cards(
    res_radar: Dict[str, Any],
    query: str = "",
    record_id: str = "latest",
    created_at: str = ""
):
    """Hiển thị toàn diện kết quả quét vĩ mô với đầy đủ thông tin, xuất file và chuyển tiếp Farrow."""
    if not res_radar or not isinstance(res_radar, dict):
        st.info("Không có dữ liệu chi tiết bản quét.")
        return

    st.markdown(f"#### 🎯 Bản Chất Cốt Lõi: {res_radar.get('trend_summary', '')}")
    st.info(f"⚡ **Chi Phí Giao Dịch Bị Kéo Tụt:** {res_radar.get('transaction_costs_impact', '')}")
    
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.error("#### 📉 Nguồn Lực Bị Trượt Giá Về 0")
        comm_assets = res_radar.get("commoditized_assets", [])
        if comm_assets:
            for item in comm_assets:
                if isinstance(item, dict):
                    st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.caption("Không có dữ liệu.")
            
    with c_r2:
        st.success("#### 💎 Nút Thắt Khan Hiếm Mới")
        comp_scarcities = res_radar.get("complementary_scarcities", [])
        if comp_scarcities:
            for item in comp_scarcities:
                if isinstance(item, dict):
                    st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.caption("Không có dữ liệu.")

    st.markdown("#### 👁️ Nước Cờ Chiến Lược Của Giới Elite")
    elite_moves = res_radar.get("elite_strategic_moves", [])
    if elite_moves:
        for move in elite_moves:
            st.markdown(f"- ♟️ {move}")
    else:
        st.caption("Không có dữ liệu.")

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown("#### 🕸️ Mô Hình Hạt Nhân Kích Hoạt")
        act_models = res_radar.get("activated_mental_models", [])
        if act_models:
            for m_item in act_models:
                if isinstance(m_item, dict):
                    st.markdown(f"- `{m_item.get('model_name', '')}`: {m_item.get('mechanism', '')}")
                else:
                    st.markdown(f"- `{m_item}`")
        else:
            st.caption("Không có dữ liệu.")
            
    with c_b2:
        st.markdown("#### 🧭 Playbook Hành Động")
        playbook = res_radar.get("action_playbook_for_individual", [])
        if playbook:
            for act in playbook:
                st.markdown(f"- 🚀 {act}")
        else:
            st.caption("Không có dữ liệu.")

    # Thanh công cụ: Xuất Markdown & Chuyển sang Máy Ép Farrow
    st.divider()
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        md_data = export_macro_radar_to_markdown(query=query, res=res_radar, created_at=created_at)
        file_slug = sanitize_filename(query if query else "the_cuoc")
        st.download_button(
            label="📥 Xuất Bản Bóc Tách (.md)",
            data=md_data,
            file_name=f"MacroRadar_{file_slug}.md",
            mime="text/markdown",
            key=f"dl_macro_{record_id}",
            use_container_width=True
        )
    with col_act2:
        if st.button("⚡ Ép Nén Farrow (3 Mỏ Neo & Nhớ Lâu)", key=f"btn_to_farrow_macro_{record_id}", use_container_width=True):
            comm_list = [c.get("asset", "") if isinstance(c, dict) else str(c) for c in res_radar.get("commoditized_assets", [])]
            scarce_list = [s.get("asset", "") if isinstance(s, dict) else str(s) for s in res_radar.get("complementary_scarcities", [])]
            synth_text = f"""[XU HƯỚNG VĨ MÔ]: {query}
- Bản chất cốt lõi: {res_radar.get('trend_summary', '')}
- Chi phí giao dịch bị kéo tụt: {res_radar.get('transaction_costs_impact', '')}
- Nguồn lực rớt giá về 0: {', '.join(comm_list)}
- Nút thắt khan hiếm mới: {', '.join(scarce_list)}
- Nước cờ chiến lược Elite: {'; '.join(res_radar.get('elite_strategic_moves', []))}
- Hành động khuyến nghị: {'; '.join(res_radar.get('action_playbook_for_individual', []))}
"""
            st.session_state["comp_raw_input"] = synth_text
            st.session_state["app_mode_redirect"] = "⚡ Máy Ép Farrow 1-Click (AI Compressor)"
            st.session_state["auto_run_compress"] = True
            st.rerun()


def render_problem_decomposition_result_cards(
    res: Dict[str, Any],
    prob: str = "",
    record_id: str = "latest",
    show_decision_transfer: bool = True,
    created_at: str = ""
):
    """Hiển thị toàn diện kết quả phân rã 9 Lăng Kính & First Principles với xuất file và chuyển tiếp Farrow."""
    if not res or not isinstance(res, dict):
        st.info("Không có dữ liệu chi tiết bản phân rã.")
        return

    # 1. First principles breakdown
    st.markdown("### ⚡ Chân Lý Nguyên Bản (First Principles)")
    st.info(res.get("first_principles_breakdown", ""))

    # 2. Core principles found (Nguyên lý hạt nhân chi phối)
    core_principles = res.get("core_principles_found", [])
    if core_principles:
        st.markdown("#### 🧬 Các Nguyên Lý Hạt Nhân Chi Phối:")
        c_pr = st.columns(min(len(core_principles), 3))
        for pr_idx, pr in enumerate(core_principles):
            with c_pr[pr_idx % len(c_pr)]:
                if isinstance(pr, dict):
                    st.markdown(f"**📌 {pr.get('name', '')}**")
                    if pr.get("domain"):
                        st.caption(f"Lĩnh vực: *{pr.get('domain', '')}*")
                    if pr.get("description"):
                        st.write(pr.get("description", ""))
                else:
                    st.markdown(f"**📌 {pr}**")

    # 3. 5 Elite Lenses cards (Đủ 5 lăng kính gồm cả Đa Khung Thời Gian)
    lenses = res.get("elite_lenses", {})
    st.markdown("### 👁️ Phân Tích Đa Chiều Qua 5 Lăng Kính Lớn")

    c_l1, c_l2 = st.columns(2)
    with c_l1:
        st.warning(f"🔄 **Lật Ngược Vấn Đề (Inversion - Munger):**  \n{lenses.get('inversion', '')}")
        st.error(f"🎯 **Hệ Quả Bậc Hai & Bậc Cao (Second-Order):**  \n{lenses.get('second_order', '')}")
        st.info(f"⏳ **Đa Khung Thời Gian (Multi-Timescale):**  \n{lenses.get('multi_timescale', '')}")
    with c_l2:
        st.info(f"🎲 **Xác Suất Bayes & Tỷ Lệ Nền (Bayesian Base Rate):**  \n{lenses.get('bayesian', '')}")
        st.success(f"⚖️ **Đòn Bẩy & Điểm Nghẽn (Leverage & Bottlenecks):**  \n{lenses.get('leverage', '')}")

    # 4. Actionable insights & Human decision questions (Câu hỏi quyết định chỉ bạn mới trả lời được)
    c_act1, c_act2 = st.columns(2)
    with c_act1:
        st.markdown("#### 🚀 Hành Động Đòn Bẩy Cao (Actionable Insights):")
        act_insights = res.get("actionable_insights", [])
        if act_insights:
            for insight in act_insights:
                st.markdown(f"- 💡 {insight}")
        else:
            st.caption("Không có dữ liệu.")
            
    with c_act2:
        st.markdown("#### ❓ Câu Hỏi Quyết Định Chỉ Bạn Mới Trả Lời Được:")
        decisions = res.get("human_decision_needed", [])
        if decisions:
            for q_item in decisions:
                st.markdown(f"- 👉 *{q_item}*")
        else:
            st.caption("Không có dữ liệu.")

    # Thanh công cụ: Xuất Markdown & Chuyển sang Máy Ép Farrow
    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        md_decomp = export_problem_decomposition_to_markdown(prob=prob, res=res, created_at=created_at)
        file_slug = sanitize_filename(prob if prob else "phan_ra")
        st.download_button(
            label="📥 Xuất Bản Phân Rã (.md)",
            data=md_decomp,
            file_name=f"Decomposition_{file_slug}.md",
            mime="text/markdown",
            key=f"dl_decomp_{record_id}",
            use_container_width=True
        )
    with col_p2:
        if st.button("⚡ Ép Nén Farrow (3 Mỏ Neo & Nhớ Lâu)", key=f"btn_to_farrow_decomp_{record_id}", use_container_width=True):
            pr_list = [p.get("name", "") if isinstance(p, dict) else str(p) for p in res.get("core_principles_found", [])]
            synth_text = f"""[BÀI TOÁN THỰC CHIẾN]: {prob}
- Chân lý nguyên bản: {res.get('first_principles_breakdown', '')}
- Nguyên lý chi phối: {', '.join(pr_list)}
- Lật ngược vấn đề (Inversion): {lenses.get('inversion', '')}
- Hệ quả bậc hai (Second-Order): {lenses.get('second_order', '')}
- Đa khung thời gian: {lenses.get('multi_timescale', '')}
- Xác suất Bayes: {lenses.get('bayesian', '')}
- Đòn bẩy & Nút thắt: {lenses.get('leverage', '')}
- Hành động đòn bẩy: {'; '.join(res.get('actionable_insights', []))}
"""
            st.session_state["comp_raw_input"] = synth_text
            st.session_state["app_mode_redirect"] = "⚡ Máy Ép Farrow 1-Click (AI Compressor)"
            st.session_state["auto_run_compress"] = True
            st.rerun()

    # 5. Chuyển sang Decision Journal
    if show_decision_transfer:
        st.write("")
        btn_key = f"btn_transfer_dj_{record_id}"
        if st.button("📓 Chuyển phân rã này thành Bản ghi Quyết định để kiểm chứng sau 30-90 ngày", type="primary", key=btn_key, use_container_width=True):
            st.session_state["dj_prefill_title"] = prob[:70]
            st.session_state["dj_prefill_hypo"] = res.get("first_principles_breakdown", "")[:300]
            st.session_state["dj_prefill_inv"] = lenses.get("inversion", "")[:250]
            st.session_state["dj_prefill_sec"] = lenses.get("second_order", "")[:250]
            st.session_state["dj_prefill_source"] = prob[:400]
            st.info("👉 Đã nạp dữ liệu vào form! Vui lòng chuyển sang chế độ **'📓 Elite Decision Journal'** phía trên để lưu!")


def render_macro_radar_room(active_api_key: str | None = None, is_embedded: bool = False):
    """Render phòng chức năng Máy Quét Đọc Vị Thế Cuộc: Chỉ 2 Tab (Quét & Kho Lưu Trữ)."""
    if not is_embedded:
        st.markdown("## 📡 Máy Quét Đọc Vị Thế Cuộc (First-Principles Macro Radar)")
        st.caption(
            "Bóc tách bất kỳ biến động vĩ mô, công nghệ hoặc sự kiện thế cuộc nào dưới lăng kính First Principles: "
            "Thứ gì sắp rớt giá về 0? Nút thắt khan hiếm mới ở đâu? Giới tinh hoa sẽ đi nước cờ gì?"
        )

    sb_client = get_supabase_client()
    sync_badge = "☁️ Supabase Cloud (Đồng bộ vĩnh viễn)" if sb_client is not None else "💾 Cục bộ (Local JSON)"
    saved_scans = load_macro_scans()

    m_tab1, m_tab2 = st.tabs([
        "📡 Máy Quét Đọc Vị (AI Radar)",
        f"📚 Kho Lưu Trữ Bản Quét ({len(saved_scans)})",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: MÁY QUÉT ĐỌC VỊ THẾ CUỘC
    # -------------------------------------------------------------------------
    with m_tab1:
        # ---------------------------------------------------------------------
        # TẦNG 1 & 2: RA-ĐA TRINH SÁT THỜI CUỘC (CÂY PHÂN CẤP F1 & F2 + LƯU TRỮ VĨNH VIỄN)
        # ---------------------------------------------------------------------
        with st.expander("🛰️ Ra-đa Trinh Sát Thời Cuộc (Cây Phân Nhánh F1 & F2 Đã Lưu Trữ)", expanded=True):
            st.markdown(
                "Đừng để bị lạc hậu hay đi ngược thời đại (như bỏ công nghiên cứu thứ đã bão hòa)! "
                "Hệ thống trinh sát **Cây Thế Cuộc Đa Tầng (F0 ➔ F1 ➔ F2)** tự động lưu trữ từng nhánh đã bóc tách. "
                "Bạn có thể chuyển đổi qua lại giữa các F1 và F2 mà không tốn API, đồng thời theo dõi sự biến chuyển sau 30–90 ngày."
            )

            all_saved_trees = load_macro_scout_trees()

            # Quản lý phiên cây trinh sát
            col_tree_sel, col_tree_act = st.columns([3, 1])
            tree_options = ["➕ Bắt mạch lĩnh vực mới"] + [
                f"🌲 [{t.get('domain', 'Chưa đặt tên')}] ({t.get('updated_at', '')[:10]})"
                for t in all_saved_trees
            ]
            
            with col_tree_sel:
                selected_tree_idx = st.selectbox(
                    "Chọn Bản Đồ Cây Đã Lưu (Hoặc tạo mới):",
                    range(len(tree_options)),
                    format_func=lambda i: tree_options[i],
                    key="sb_tree_selector"
                )

            active_tree = None
            if selected_tree_idx > 0 and len(all_saved_trees) >= selected_tree_idx:
                active_tree = all_saved_trees[selected_tree_idx - 1]
                st.session_state["active_tree_id"] = active_tree["id"]
                st.session_state["active_scout_domain"] = active_tree.get("domain", "")

            # Nút xóa cây hiện tại nếu đang xem cây cũ
            with col_tree_act:
                if active_tree:
                    st.write("")
                    if st.button("🗑️ Xóa cây này", key=f"btn_del_tree_{active_tree['id']}", use_container_width=True):
                        delete_macro_scout_tree(active_tree["id"])
                        st.session_state.pop("active_tree_id", None)
                        st.success("Đã xóa cây trinh sát!")
                        st.rerun()

            # Form nhập hoặc quét mới
            if not active_tree:
                scout_chips = [
                    ("🤖 Công nghệ & AI", "Công nghệ & AI"),
                    ("🧠 Não bộ & BCI", "Công nghệ não bộ & Giao diện não-máy tính BCI"),
                    ("💰 Tài chính & Tiền tệ", "Tài chính & Dòng tiền"),
                    ("⚡ Năng lượng & Hạ tầng", "Năng lượng & Điện lưới"),
                    ("🧬 Y sinh & Gene", "Y sinh & Công nghệ gene"),
                    ("🏭 Robotics & Tự hành", "Robotics & Xe tự hành")
                ]
                
                c_ch1, c_ch2, c_ch3, c_ch4, c_ch5, c_ch6 = st.columns(6)
                chip_cols = [c_ch1, c_ch2, c_ch3, c_ch4, c_ch5, c_ch6]
                for col_i, (chip_label, chip_query) in zip(chip_cols, scout_chips):
                    with col_i:
                        if st.button(chip_label, key=f"chip_scout_{chip_label}", use_container_width=True):
                            st.session_state["scout_kw_input"] = chip_query
                            st.session_state["trigger_auto_scout"] = True
                            st.rerun()

                col_kw, col_sbtn = st.columns([3, 1])
                with col_kw:
                    scout_query = st.text_input(
                        "Nhập lĩnh vực hoặc từ khóa muốn trinh sát:",
                        value=st.session_state.get("scout_kw_input", "Công nghệ não bộ & BCI"),
                        key="input_scout_kw",
                        placeholder="vd: não bộ, công nghệ, xe điện, bán dẫn, fintech, năng lượng xanh, việc làm..."
                    )
                with col_sbtn:
                    st.write("")
                    run_scout = st.button("🛰️ Bắt Mạch Top 10", type="secondary", use_container_width=True, key="btn_run_scout")

                if st.session_state.pop("trigger_auto_scout", False):
                    run_scout = True

                if run_scout:
                    if not scout_query.strip():
                        st.warning("Vui lòng nhập từ khóa hoặc lĩnh vực muốn trinh sát!")
                    else:
                        with st.spinner(f"🛰️ Đang quét bắt mạch xu hướng mới nhất cho '{scout_query.strip()}'..."):
                            scout_data = scout_macro_trends(scout_query.strip(), api_key=active_api_key)
                        if scout_data and "trends" in scout_data:
                            saved_tree_obj = save_macro_scout_tree(
                                domain_name=scout_query.strip(),
                                scout_overview=scout_data.get("scout_overview", ""),
                                trends=scout_data.get("trends", [])
                            )
                            st.session_state["active_tree_id"] = saved_tree_obj["id"]
                            st.session_state["active_scout_domain"] = scout_query.strip()
                            st.rerun()
                        elif scout_data and scout_data.get("error"):
                            st.error(scout_data["error"])

            else:
                # HIỂN THỊ CÂY TRINH SÁT ĐANG HOẠT ĐỘNG
                upd_time = active_tree.get("updated_at", active_tree.get("created_at", "Gần đây"))
                # Tính độ tươi (Freshness Gauge)
                try:
                    dt_upd = datetime.strptime(upd_time, "%Y-%m-%d %H:%M:%S")
                    diff_days = (datetime.now() - dt_upd).days
                    if diff_days == 0:
                        freshness_label = "🟢 Hôm nay (Dữ liệu mới nhất)"
                    elif diff_days < 7:
                        freshness_label = f"🟢 {diff_days} ngày trước (Dữ liệu tươi)"
                    elif diff_days < 30:
                        freshness_label = f"🟡 {diff_days} ngày trước (Dữ liệu ổn định)"
                    else:
                        freshness_label = f"🔴 {diff_days} ngày trước (>30 ngày - Khuyến nghị bấm Quét Cập Nhật)"
                except Exception:
                    freshness_label = "⏱️ Gần đây"

                col_inf1, col_inf2 = st.columns([3, 1])
                with col_inf1:
                    st.markdown(f"#### 🌐 Bản Đồ Cây: `{active_tree.get('domain', '')}`")
                    st.caption(f"📅 Cập nhật lần cuối: **{upd_time}** &nbsp; | &nbsp; Trạng thái: **{freshness_label}**")
                with col_inf2:
                    if st.button("🔄 Quét Cập Nhật (So sánh mới)", key=f"btn_rescan_{active_tree['id']}", use_container_width=True, help="Bắt mạch lại để cập nhật xu hướng mới nhất và so sánh sự chuyển dịch"):
                        with st.spinner(f"🛰️ Đang cập nhật dữ liệu mới nhất cho '{active_tree.get('domain')}'..."):
                            new_scout = scout_macro_trends(active_tree.get("domain", ""), api_key=active_api_key)
                            if new_scout and "trends" in new_scout:
                                save_macro_scout_tree(
                                    domain_name=active_tree.get("domain", ""),
                                    scout_overview=new_scout.get("scout_overview", ""),
                                    trends=new_scout.get("trends", []),
                                    tree_id=active_tree["id"]
                                )
                                st.toast("Đã cập nhật bản đồ cây!", icon="✅")
                                st.rerun()

                if active_tree.get("scout_overview"):
                    st.info(f"🧭 **Cục diện hiện nay:** {active_tree['scout_overview']}")

                # Render Top 10 F1 & Màn hình F2 ngay bên dưới F1 được chọn
                trends = active_tree.get("trends", [])
                selected_f1_rank = st.session_state.get("selected_f1_rank", 1)

                for t_item in trends:
                    t_rank = t_item.get("rank", 0)
                    t_title = t_item.get("title", "")
                    t_badge = t_item.get("badge", "🔥 Sóng Thần Tiên Phong")
                    t_status = t_item.get("status", "Bùng nổ")
                    t_one = t_item.get("one_liner", "")
                    t_sug = t_item.get("suggested_query", t_title)
                    has_f2 = bool(t_item.get("drill_down"))

                    # Kiểm tra xem F1 này đã từng được bóc tách First Principles chưa
                    f1_scanned = any(t_title.lower() in s.get("query", "").lower() for s in saved_scans)
                    badge_f1_scanned = " &nbsp; `✅ Đã có bản bóc tách trong Kho`" if f1_scanned else ""

                    is_active_f1 = (selected_f1_rank == t_rank)
                    border_style = "border: 2px solid #6366f1; background: rgba(99, 102, 241, 0.08);" if is_active_f1 else "border: 1px solid rgba(255,255,255,0.1);"

                    st.markdown(f"""
                    <div style="padding: 12px 14px; border-radius: 8px; {border_style} margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 1.05rem;">#{t_rank}. {t_title}</span> 
                        &nbsp; <code style="background: rgba(99, 102, 241, 0.2);">{t_badge}</code>
                        &nbsp; <code style="background: rgba(16, 185, 129, 0.2);">Trạng thái: {t_status}</code>
                        {badge_f1_scanned}
                        <p style="margin: 6px 0 2px 0; color: #cbd5e1; font-size: 0.95rem;">👉 <i>{t_one}</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                    c_act1, c_act2 = st.columns([1, 1])
                    with c_act1:
                        # Nút chọn bóc tách First Principles
                        if st.button(f"🎯 Chọn bóc tách F1-#{t_rank}", key=f"btn_pick_f1_{active_tree['id']}_{t_rank}", use_container_width=True):
                            st.session_state["room_macro_radar_input"] = t_sug
                            st.rerun()

                    with c_act2:
                        # Nút mở màn hình F2 bên dưới
                        label_f2_btn = f"🌿 Xem Lớp 2 ({len(t_item['drill_down'].get('sub_trends', []))} nhánh đã lưu)" if has_f2 else f"🔍 Soi Sâu Lớp 2 & 3 (F1-#{t_rank})"
                        btn_type = "primary" if is_active_f1 else "secondary"
                        if st.button(label_f2_btn, key=f"btn_toggle_f2_{active_tree['id']}_{t_rank}", type=btn_type, use_container_width=True):
                            st.session_state["selected_f1_rank"] = t_rank
                            st.rerun()

                    # ---------------------------------------------------------
                    # MÀN HÌNH F2: HIỆN NGAY PHÍA DƯỚI F1 ĐANG CHỌN
                    # ---------------------------------------------------------
                    if is_active_f1:
                        with st.container():
                            st.markdown(f"""
                            <div style="background: rgba(15, 23, 42, 0.85); border: 2px dashed #6366f1; border-radius: 10px; padding: 16px; margin: 10px 0 18px 0;">
                                <h4 style="color: #a5b4fc; margin-top: 0;">🌿 MÀN HÌNH SOI SÂU LỚP 2 & 3: [F1-#{t_rank}: {t_title}]</h4>
                            </div>
                            """, unsafe_allow_html=True)

                            if not has_f2:
                                st.info(f"Chưa có dữ liệu bóc tách vi xu hướng F2 cho nhánh **#{t_rank}: {t_title}**.")
                                if st.button(f"⚡ Bóc Tách 3–5 Nút Thắt Ngầm (F2) Bằng AI", key=f"btn_run_drill_{active_tree['id']}_{t_rank}", type="primary", use_container_width=True):
                                    with st.spinner(f"AI đang bóc tách 3-5 nút thắt ngầm cho '{t_title}'..."):
                                        drill_res = drill_down_macro_trend(t_title, context=t_one, api_key=active_api_key)
                                        if drill_res and "sub_trends" in drill_res:
                                            update_tree_drilldown(active_tree["id"], t_rank, drill_res)
                                            st.toast("Đã bóc tách và lưu trữ các nhánh F2 vào cây!", icon="💾")
                                            st.rerun()
                                        elif drill_res and drill_res.get("error"):
                                            st.error(drill_res["error"])
                            else:
                                d_data = t_item["drill_down"]
                                if d_data.get("drill_down_insight"):
                                    st.info(f"💡 **Điểm nghẽn cốt lõi:** {d_data.get('drill_down_insight')}")

                                st.markdown(f"**Danh sách các nút thắt & vi xu hướng ngầm ({len(d_data.get('sub_trends', []))} nhánh đã lưu):**")
                                for sub in d_data.get("sub_trends", []):
                                    sub_rank = sub.get("sub_rank", 1)
                                    sub_title = sub.get("title", "")
                                    sub_why = sub.get("why_crucial", "")
                                    sub_sug = sub.get("suggested_query", sub_title)

                                    sub_scanned = any(sub_title.lower() in s.get("query", "").lower() for s in saved_scans)
                                    badge_sub = " &nbsp; `✅ Đã có bản bóc tách trong Kho`" if sub_scanned else ""

                                    with st.container():
                                        st.markdown(f"**[F2-{sub_rank}] {sub_title}**{badge_sub}")
                                        st.caption(f"💎 *Tại sao quan trọng:* {sub_why}")

                                        c_sub1, c_sub2 = st.columns([1, 1])
                                        with c_sub1:
                                            if st.button(f"🎯 Chọn bóc tách F2-{sub_rank} theo First Principles", key=f"btn_pick_sub_{active_tree['id']}_{t_rank}_{sub_rank}", use_container_width=True):
                                                st.session_state["room_macro_radar_input"] = sub_sug
                                                st.rerun()
                                        with c_sub2:
                                            if sub_scanned:
                                                st.caption("👉 Bạn đã có bài bóc tách trong Kho Lưu Trữ (Tab 2).")

                    st.divider()

        # ---------------------------------------------------------------------
        # TẦNG 3: BÓC TÁCH THẾ CUỘC THEO FIRST PRINCIPLES
        # ---------------------------------------------------------------------
        st.markdown("#### 💡 Hoặc chọn nhanh các xu hướng vĩ mô kinh điển:")
        s_cols = st.columns(len(SAMPLE_MACRO_TRENDS))
        for s_idx, sample in enumerate(SAMPLE_MACRO_TRENDS):
            with s_cols[s_idx]:
                sample_short_title = sample["title"].split()[0] + " " + " ".join(sample["title"].split()[1:3])
                if st.button(sample_short_title, key=f"room_macro_sample_{s_idx}", help=sample["title"]):
                    st.session_state["room_macro_radar_input"] = sample["query"]
                    st.rerun()

        if "room_macro_radar_input" not in st.session_state:
            st.session_state["room_macro_radar_input"] = (
                "Sự xuất hiện của các AI Agents tự hành có khả năng lập trình, viết báo cáo, xử lý dữ liệu và vận hành quy trình kinh doanh 24/7 với chi phí tiệm cận 0."
            )
        default_q = st.session_state["room_macro_radar_input"]
        trend_text = st.text_area(
            "Nhập mô tả biến động vĩ mô, công nghệ hoặc sự kiện cần bóc tách:",
            value=default_q,
            height=110,
            key="room_macro_trend_text_area"
        )

        col_m_run, col_m_reset = st.columns([3, 1])
        with col_m_run:
            run_macro_btn = st.button("📡 Quét Đọc Vị Theo First Principles", type="primary", use_container_width=True, key="room_btn_radar")
        with col_m_reset:
            if st.button("🔄 Làm mới ô nhập", use_container_width=True, key="room_btn_clear_radar"):
                st.session_state["room_macro_radar_input"] = ""
                st.session_state.pop("latest_macro_radar_result", None)
                st.session_state.pop("latest_macro_radar_trend", None)
                st.rerun()

        if run_macro_btn:
            if not trend_text.strip():
                st.warning("Vui lòng nhập nội dung biến động vĩ mô cần bóc tách!")
            else:
                with st.spinner("🤖 Đang kích hoạt Bộ máy Phân tích Thế cuộc & First Principles Engine..."):
                    res_radar = analyze_macro_radar(trend_text.strip(), api_key=active_api_key)
                if not res_radar:
                    st.error("Không nhận được phản hồi từ AI Engine.")
                elif "error" in res_radar and not res_radar.get("trend_summary"):
                    st.error(f"Lỗi: {res_radar['error']}")
                else:
                    st.session_state["latest_macro_radar_result"] = res_radar
                    st.session_state["latest_macro_radar_trend"] = trend_text.strip()
                    saved_ok = save_macro_scan(trend_text.strip(), res_radar)
                    if saved_ok:
                        st.toast("☁️ Đã tự động lưu kết quả quét vào Supabase Cloud!", icon="💾")

        # Hiển thị kết quả quét mới nhất
        if "latest_macro_radar_result" in st.session_state:
            res_radar = st.session_state["latest_macro_radar_result"]
            st.success("✅ Đã hoàn tất bóc tách thế cuộc & Lưu trữ bền vững!")
            render_macro_radar_result_cards(
                res_radar,
                query=st.session_state.get("latest_macro_radar_trend", ""),
                record_id="latest"
            )

    # -------------------------------------------------------------------------
    # TAB 2: KHO LƯU TRỮ BẢN QUÉT THẾ CUỘC
    # -------------------------------------------------------------------------
    with m_tab2:
        st.markdown(f"#### 📚 Kho Lưu Trữ Lịch Sử Quét Thế Cuộc")
        st.caption(f"Trạng thái đồng bộ: **{sync_badge}**. Toàn bộ dữ liệu được lưu vĩnh viễn trên Supabase Cloud.")

        all_scans = load_macro_scans()
        if all_scans:
            s_search = st.text_input(
                "🔍 Tìm kiếm trong kho lưu trữ:",
                placeholder="Nhập từ khóa (vd: chip não, robot, xe điện, năng lượng...)",
                key="room_macro_history_search"
            )
            filtered = all_scans
            if s_search.strip():
                kw = s_search.strip().lower()
                filtered = [s for s in all_scans if kw in s.get("query", "").lower() or kw in str(s.get("result", {})).lower()]

            if not filtered:
                st.info("Không tìm thấy bản quét nào khớp với từ khóa.")

            for idx, sc in enumerate(filtered):
                sc_id = sc.get("id", f"scan_{idx}")
                sc_time = sc.get("created_at", "Gần đây")
                sc_query = sc.get("query", "Không có tiêu đề")
                sc_res = sc.get("result", {})

                short_title = sc_query[:75] + ("..." if len(sc_query) > 75 else "")
                with st.expander(f"📑 [{sc_time}] {short_title}", expanded=(idx == 0 and len(filtered) == 1)):
                    col_h_left, col_h_right = st.columns([4, 1])
                    with col_h_left:
                        st.markdown(f"**🎯 Xu hướng đã quét:**  \n*{sc_query}*")
                    with col_h_right:
                        if st.button("🗑️ Xóa", key=f"room_del_macro_{sc_id}"):
                            delete_macro_scan(sc_id)
                            st.success("Đã xóa bản ghi!")
                            st.rerun()

                    st.divider()
                    render_macro_radar_result_cards(
                        sc_res,
                        query=sc_query,
                        record_id=sc_id,
                        created_at=sc_time
                    )
        else:
            st.info("💡 Chưa có bản quét nào được lưu. Hãy quét một xu hướng ở Tab 1 để tự động lưu vào đây!")


def render_problem_decomposition_room(active_api_key: str | None = None):
    """Render phòng chức năng Phân Rã Thực Chiến: Chỉ 2 Tab (Phân Rã Vấn Đề & Kho Lưu Trữ / Nhật Ký)."""
    st.markdown("## 🎯 Phân Rã Thực Chiến & Nhật Ký Quyết Định")
    st.caption(
        "Bóc tách tận gốc vấn đề phức tạp qua 9 Lăng kính Tinh hoa & First Principles. "
        "Thiết lập Nhật ký Quyết định theo chuẩn Ray Dalio & Howard Marks để tự đo lường và hiệu chuẩn sai số nhận thức."
    )

    sb_client = get_supabase_client()
    sync_badge = "☁️ Supabase Cloud (Đồng bộ vĩnh viễn)" if sb_client is not None else "💾 Cục bộ (Local JSON)"
    all_analyses = load_problem_analyses()

    p_tab1, p_tab2 = st.tabs([
        "🚀 Phân Rã Vấn Đề (AI 9 Lenses)",
        f"📓 Kho Lưu Trữ & Nhật Ký Quyết Định ({len(all_analyses)})",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PHÂN RÃ VẤN ĐỀ 9 LĂNG KÍNH
    # -------------------------------------------------------------------------
    with p_tab1:
        st.markdown("#### 💡 Chọn tình huống thực chiến mẫu để nạp nhanh:")
        p_cols = st.columns(len(SAMPLE_DECOMPOSITION_CASES))
        for p_idx, p_case in enumerate(SAMPLE_DECOMPOSITION_CASES):
            with p_cols[p_idx]:
                short_btn = p_case["title"].split(":")[0]
                if st.button(short_btn, key=f"case_sample_{p_idx}", help=p_case["title"]):
                    st.session_state["p_problem_input"] = p_case["query"]
                    st.rerun()

        default_problem = st.session_state.get(
            "p_problem_input",
            "Đầu tư CKVN: Thị trường giảm mạnh 15% trong 2 tuần, tin tức xấu bủa vây, tâm lý hoang mang. Nên bán tháo cắt lỗ hay giải ngân mua gom tích sản cổ phiếu cơ bản tốt?"
        )
        problem_text = st.text_area(
            "Mô tả cụ thể bối cảnh vấn đề, mục tiêu, các ràng buộc và điều bạn đang băn khoăn:",
            value=default_problem,
            height=120,
            key="p_problem_text_area"
        )

        col_run, col_reset = st.columns([3, 1])
        with col_run:
            run_btn = st.button("🚀 Bóc Tách Vấn Đề Theo 9 Lăng Kính", type="primary", use_container_width=True, key="btn_run_decomp")
        with col_reset:
            if st.button("🔄 Làm mới ô nhập", use_container_width=True, key="btn_clear_decomp"):
                st.session_state["p_problem_input"] = ""
                st.session_state.pop("latest_decomposition_result", None)
                st.rerun()

        if run_btn:
            if not problem_text.strip():
                st.warning("Vui lòng nhập nội dung vấn đề cần phân rã!")
            else:
                with st.spinner("🤖 Đang kích hoạt 9 Lăng kính Tinh hoa & Bóc tách First Principles..."):
                    decomp_res = decompose_problem_with_ai(problem_text.strip(), api_key=active_api_key)
                if not decomp_res:
                    st.error("Không nhận được phản hồi từ AI Engine.")
                elif decomp_res.get("error"):
                    st.error(f"Lỗi: {decomp_res['error']}")
                else:
                    st.session_state["latest_decomposition_result"] = decomp_res
                    st.session_state["latest_decomposition_problem"] = problem_text.strip()
                    # Lưu vào Supabase Cloud & Local JSON
                    save_problem_analysis(problem_text.strip(), decomp_res)
                    st.toast("☁️ Đã lưu bản phân rã vào Supabase Cloud!", icon="💾")

        # Hiển thị kết quả phân rã
        if "latest_decomposition_result" in st.session_state:
            res = st.session_state["latest_decomposition_result"]
            prob = st.session_state.get("latest_decomposition_problem", "")

            st.success("✅ Đã hoàn tất bóc tách 9 Lăng kính & Lưu trữ an toàn!")
            render_problem_decomposition_result_cards(
                res,
                prob=prob,
                record_id="latest",
                show_decision_transfer=True
            )

    # -------------------------------------------------------------------------
    # TAB 2: KHO LƯU TRỮ BẢN PHÂN RÃ & NHẬT KÝ QUYẾT ĐỊNH
    # -------------------------------------------------------------------------
    with p_tab2:
        view_mode = st.radio(
            "Chọn chế độ xem:",
            ["📜 Lịch Sử Bản Phân Rã (Archive)", "📓 Elite Decision Journal (Đo Sai Số)"],
            horizontal=True,
            key="p_view_mode_toggle"
        )

        if view_mode == "📜 Lịch Sử Bản Phân Rã (Archive)":
            st.markdown(f"#### 📜 Kho Lưu Trữ Bản Phân Rã Vấn Đề")
            st.caption(f"Trạng thái đồng bộ: **{sync_badge}**. Toàn bộ các bản phân rã vấn đề qua 9 Lăng kính được lưu trữ vĩnh viễn.")

            all_ana = load_problem_analyses()
            if not all_ana:
                st.info("💡 Chưa có bản phân rã nào trong kho lưu trữ. Hãy phân rã một vấn đề ở Tab 1 để tự động lưu vào đây!")
            else:
                s_ana = st.text_input("🔍 Tìm kiếm trong kho phân rã:", placeholder="Nhập từ khóa (vd: CKVN, vàng, công ty, sự nghiệp...)", key="p_search_analyses")
                filtered_ana = all_ana
                if s_ana.strip():
                    kw_a = s_ana.strip().lower()
                    filtered_ana = [a for a in all_ana if kw_a in a.get("problem", "").lower() or kw_a in str(a.get("full_result", {})).lower()]

                if not filtered_ana:
                    st.info("Không tìm thấy bản ghi nào khớp với từ khóa tìm kiếm.")

                for a_idx, a_item in enumerate(filtered_ana):
                    a_id = a_item.get("id", f"ana_{a_idx}")
                    a_time = a_item.get("created_at") or a_item.get("time", "Gần đây")
                    a_problem = a_item.get("problem", "Không có nội dung")
                    a_res = a_item.get("full_result", {})

                    short_prob = a_problem[:80] + ("..." if len(a_problem) > 80 else "")
                    with st.expander(f"📌 [{a_time}] {short_prob}"):
                        c_al, c_ar = st.columns([4, 1])
                        with c_al:
                            st.markdown(f"**🎯 Vấn đề đã phân rã:**  \n*{a_problem}*")
                        with c_ar:
                            if st.button("🗑️ Xóa", key=f"btn_del_ana_{a_id}"):
                                delete_problem_analysis(a_id)
                                st.success("Đã xóa bản phân rã!")
                                st.rerun()

                        st.divider()
                        render_problem_decomposition_result_cards(
                            a_res,
                            prob=a_problem,
                            record_id=a_id,
                            show_decision_transfer=True,
                            created_at=a_time
                        )

        else:
            # Elite Decision Journal
            st.markdown("#### 📓 Elite Decision Journal: Đo Lường & Hiệu Chuẩn Sai Số Nhận Thức")
            st.caption(
                "Ghi lại giả định HÔM NAY $\\rightarrow$ Hẹn lịch tự động kiểm định sau 30/90/180 ngày "
                "$\\rightarrow$ Chấm điểm thực tế để đo độ lệch nhận thức (Calibration Score) và diệt trừ Hindsight Bias."
            )

            # Stats banner
            stats = get_decision_summary_stats()
            c_st1, c_st2, c_st3, c_st4, c_st5 = st.columns(5)
            with c_st1:
                st.metric("Tổng Quyết Định", stats["total_logged"])
            with c_st2:
                st.metric("⏳ Đang Chờ", stats["pending_count"])
            with c_st3:
                st.metric("🔔 Cần Kiểm Tra Ngay", stats["due_count"])
            with c_st4:
                st.metric("✅ Đã Đánh Giá", stats["reviewed_count"])
            with c_st5:
                st.metric("🎯 Độ Chuẩn Xác", f"{stats['calibration_accuracy']}%")

            st.divider()

            # Form tạo quyết định mới
            with st.expander("➕ GHI NHẬN QUYẾT ĐỊNH MỚI CẦN KIỂM CHỨNG", expanded=bool(st.session_state.get("dj_prefill_title"))):
                with st.form("form_create_decision"):
                    f_title = st.text_input(
                        "Tiêu đề quyết định:",
                        value=st.session_state.get("dj_prefill_title", ""),
                        placeholder="Ví dụ: Mua gom cổ phiếu HPG giá 25; Nghỉ việc chuyển sang AI Startup..."
                    )
                    c_cat, c_days = st.columns(2)
                    with c_cat:
                        f_category = st.selectbox("Lĩnh vực quyết định:", DECISION_CATEGORIES)
                    with c_days:
                        f_interval_label = st.selectbox("Hạn định kiểm chứng sau:", list(REVIEW_INTERVALS.keys()), index=1)
                        f_review_days = REVIEW_INTERVALS[f_interval_label]

                    f_hypo = st.text_area(
                        "Giả định cốt lõi & Cơ sở lập luận (Tại sao bạn tin quyết định này đúng?):",
                        value=st.session_state.get("dj_prefill_hypo", ""),
                        height=90,
                        placeholder="Mô tả cụ thể giả định và nguyên lý bạn dựa vào để ra quyết định..."
                    )

                    f_conf = st.slider(
                        "Mức độ tự tin ban đầu của bạn (Confidence Level):",
                        min_value=50, max_value=99, value=75, step=5,
                        help="Nếu bạn chấm 80%, nghĩa là trong 10 quyết định tương tự, bạn kỳ vọng đúng 8 lần."
                    )

                    c_inv, c_sec = st.columns(2)
                    with c_inv:
                        f_inv = st.text_area(
                            "Bẫy đảo ngược (Điều gì có thể khiến quyết định này sụp đổ?):",
                            value=st.session_state.get("dj_prefill_inv", ""),
                            height=80
                        )
                    with c_sec:
                        f_sec = st.text_area(
                            "Hệ quả bậc hai (Nếu điều này xảy ra thì điều gì tiếp theo?):",
                            value=st.session_state.get("dj_prefill_sec", ""),
                            height=80
                        )

                    f_feynman = st.text_input(
                        "Thử nghiệm trung thực Feynman:",
                        placeholder="Tự vấn trung thực: Có phải mình chỉ đang FOMO hoặc sợ bỏ lỡ cơ hội?"
                    )

                    submit_dec = st.form_submit_button("💾 Lưu Quyết Định Vào Nhật Ký (Supabase Cloud)", type="primary")

                    if submit_dec:
                        if not f_title.strip() or not f_hypo.strip():
                            st.error("Vui lòng điền tối thiểu Tiêu đề và Giả định cốt lõi!")
                        else:
                            create_decision_entry(
                                title=f_title.strip(),
                                category=f_category,
                                hypothesis=f_hypo.strip(),
                                confidence_pct=f_conf,
                                inversion_traps=f_inv.strip(),
                                second_order_consequences=f_sec.strip(),
                                review_days=f_review_days,
                                source_analysis=st.session_state.get("dj_prefill_source", ""),
                                feynman_honesty_check=f_feynman.strip(),
                            )
                            st.session_state.pop("dj_prefill_title", None)
                            st.session_state.pop("dj_prefill_hypo", None)
                            st.session_state.pop("dj_prefill_inv", None)
                            st.session_state.pop("dj_prefill_sec", None)
                            st.session_state.pop("dj_prefill_source", None)
                            st.success("🎉 Đã lưu quyết định thành công! Hệ thống sẽ nhắc bạn kiểm định khi đến hạn.")
                            st.rerun()

            # Danh sách quyết định
            st.markdown("#### 📋 Danh Sách Quyết Định Đang Theo Dõi:")
            decisions = get_user_decisions()
            if not decisions:
                st.info("💡 Chưa có quyết định nào được ghi nhận. Hãy bấm vào nút '➕ GHI NHẬN QUYẾT ĐỊNH MỚI' ở trên để bắt đầu!")
            else:
                filter_status = st.radio(
                    "Lọc theo trạng thái:",
                    ["Tất cả", "🔔 Cần kiểm tra ngay (Due)", "⏳ Đang chờ (Pending)", "✅ Đã đánh giá (Reviewed)"],
                    horizontal=True
                )

                filtered_dec = decisions
                if "Cần kiểm tra ngay" in filter_status:
                    filtered_dec = [d for d in decisions if d.get("status") == "due"]
                elif "Đang chờ" in filter_status:
                    filtered_dec = [d for d in decisions if d.get("status") == "pending"]
                elif "Đã đánh giá" in filter_status:
                    filtered_dec = [d for d in decisions if d.get("status") == "reviewed"]

                for d_item in filtered_dec:
                    d_id = d_item.get("id")
                    d_status = d_item.get("status", "pending")
                    status_icon = "🔔 [ĐẾN HẠN KIỂM ĐỊNH]" if d_status == "due" else ("✅ [ĐÃ ĐÁNH GIÁ]" if d_status == "reviewed" else "⏳ [ĐANG CHỜ]")

                    expander_label = f"{status_icon} [{d_item.get('category')}] {d_item.get('title')} (Hạn: {d_item.get('review_date')})"
                    with st.expander(expander_label, expanded=(d_status == "due")):
                        c_det1, c_det2 = st.columns([3, 2])
                        with c_det1:
                            st.markdown(f"**🎯 Quyết định:** *{d_item.get('title')}*")
                            st.markdown(f"**💡 Giả định ban đầu:** {d_item.get('hypothesis')}")
                            if d_item.get("inversion_traps"):
                                st.warning(f"⚠️ **Bẫy đảo ngược:** {d_item.get('inversion_traps')}")
                            if d_item.get("second_order_consequences"):
                                st.info(f"🎯 **Hệ quả bậc hai:** {d_item.get('second_order_consequences')}")
                            if d_item.get("feynman_honesty_check"):
                                st.caption(f"🔍 **Feynman Check:** *{d_item.get('feynman_honesty_check')}*")
                        with c_det2:
                            st.markdown(f"📅 **Ngày lập:** `{d_item.get('created_at')}`")
                            st.markdown(f"⏱️ **Hạn kiểm tra:** `{d_item.get('review_date')}` ({d_item.get('review_days')} ngày)")
                            st.markdown(f"🎲 **Độ tự tin ban đầu:** `{d_item.get('confidence_pct')}%`")

                        # Form đánh giá hậu nghiệm nếu chưa reviewed
                        if d_status in ["due", "pending"]:
                            st.divider()
                            st.markdown("#### ⚖️ Biểu Mẫu Hiệu Chuẩn Sai Số Hậu Nghiệm:")
                            with st.form(f"form_review_{d_id}"):
                                f_actual = st.text_area("Kết quả thực tế đã diễn ra như thế nào?", placeholder="Mô tả cụ thể thị trường, kết quả công việc hoặc tình huống thực tế sau thời gian qua...")
                                f_rating_label = st.selectbox("Đánh giá độ chuẩn xác so với dự tính ban đầu:", list(OUTCOME_RATINGS.keys()))
                                f_score = OUTCOME_RATINGS[f_rating_label]
                                f_lessons = st.text_area("Bài học xương máu rút ra:", placeholder="Điểm nào mình đã đoán đúng? Điểm nào bị thiên kiến? Điều gì sẽ làm khác đi lần tới?")

                                sub_review = st.form_submit_button("✅ Hoàn tất Hiệu Chuẩn & Tính Điểm", type="primary")

                                if sub_review:
                                    if not f_actual.strip():
                                        st.error("Vui lòng ghi nhận kết quả thực tế!")
                                    else:
                                        resolve_decision_review(
                                            decision_id=d_id,
                                            actual_outcome=f_actual.strip(),
                                            outcome_score=f_score,
                                            lessons_learned=f_lessons.strip()
                                        )
                                        st.success("🎉 Đã hiệu chuẩn thành công!")
                                        st.rerun()

                        # Kết quả đã reviewed
                        elif d_status == "reviewed":
                            st.divider()
                            st.markdown("#### 🏆 Kết Quả Đánh Giá Hậu Nghiệm:")
                            st.markdown(f"**Kết quả thực tế:** {d_item.get('actual_outcome')}")
                            st.metric("Điểm Kết Quả Thực Tế", f"{d_item.get('outcome_score')}%", delta=f"Độ lệch: {d_item.get('calibration_diff')}%")
                            st.markdown(f"**Bài học rút ra:** {d_item.get('lessons_learned')}")

                        if st.button("🗑️ Xóa quyết định này", key=f"btn_del_dec_{d_id}"):
                            delete_decision_entry(decision_id=d_id)
                            st.success("Đã xóa quyết định!")
                            st.rerun()


# =============================================================================
# 3. MÁY ÉP FARROW 1-CLICK (UNIVERSAL AI COMPRESSOR)
# =============================================================================
SAMPLE_COMPRESSIONS = [
    {
        "title": "📈 Chiến Lược Cạnh Tranh (Michael Porter)",
        "text": (
            "Trong kinh tế học và quản trị chiến lược của Michael Porter, một doanh nghiệp chỉ có thể đạt được lợi nhuận vượt trội bền vững thông qua hai con đường cơ bản: "
            "Chi phí thấp (Cost Leadership) hoặc Khác biệt hóa (Differentiation). Cả hai chiến lược này đều nhằm mục tiêu tự vệ trước 5 lực lượng cạnh tranh: "
            "Áp lực từ nhà cung cấp, Áp lực từ khách hàng, Nguy cơ từ sản phẩm thay thế, Rào cản gia nhập ngành của đối thủ tiềm năng và Mức độ khốc liệt của các đối thủ hiện hữu. "
            "Nếu một công ty cố gắng làm tất cả để làm hài lòng mọi đối tượng khách hàng mà không chọn rõ ràng một trong hai con đường, công ty đó sẽ rơi vào trạng thái 'mắc kẹt ở giữa' "
            "(stuck in the middle) và chắc chắn sẽ bị các đối thủ tập trung chuyên biệt tiêu diệt."
        )
    },
    {
        "title": "🧬 Điểm Tựa Năng Lượng & Sự Sống (Nick Lane)",
        "text": (
            "Theo nghiên cứu của nhà sinh học Nick Lane, nguồn gốc của mọi sự sống phức tạp (sinh vật nhân thực Eukaryote) bắt nguồn từ một sự kiện cộng sinh ngẫu nhiên cực kỳ hiếm hoi "
            "cách đây 2 tỷ năm: một vi khuẩn cổ nuốt chửng một vi khuẩn khác và biến nó thành ti thể (mitochondria). Ti thể đóng vai trò như nhà máy phát điện mini, giải phóng năng lượng "
            "gấp hàng nghìn lần trên mỗi gen so với vi khuẩn đơn bào thông thường. Nhờ có nguồn năng lượng dư thừa khổng lồ này, tế bào mới có thể nuôi dưỡng một bộ gen khổng lồ, "
            "tạo tiền đề cho sự xuất hiện của các sinh vật đa bào, động thực vật và trí thông minh con người. Năng lượng chính là giới hạn vật lý cứng quyết định độ phức tạp của mọi cấu trúc sống."
        )
    },
    {
        "title": "🧠 Chiến Lược Barbell & Chống Mong Manh (Nassim Taleb)",
        "text": (
            "Nassim Taleb đề xuất Chiến lược Barbell (Quả tạ hai đầu) như một cơ chế thực chiến để tồn tại và phát triển trong một thế giới đầy biến động và Thiên Nga Đen. "
            "Thay vì chọn phương án trung bình rủi ro vừa phải (vốn là nơi dễ chết nhất khi xảy ra khủng hoảng), nhà đầu tư nên chia vốn làm 2 cực đối nghịch tuyệt đối: "
            "85-90% tài sản được giữ ở nơi an toàn tối đa (trái phiếu chính phủ ngắn hạn, tiền mặt, vàng) để không bao giờ bị phá sản; 10-15% còn lại được phân bổ vào các canh bạc có rủi ro cao "
            "nhưng tiềm năng lợi nhuận lũy thừa bất đối xứng (như quyền chọn mua, khởi nghiệp mạo hiểm, công nghệ đột phá). Bằng cách này, tổn thất tối đa bị khóa cứng ở mức 10-15%, "
            "trong khi tiềm năng tăng trưởng là vô hạn."
        )
    }
]


def render_farrow_compression_cards(
    res: Dict[str, Any],
    title: str = "",
    raw_text: str = "",
    record_id: str = "latest",
    created_at: str = ""
):
    """Hiển thị bộ 3 thẻ nén Dave Farrow với đầy đủ thông tin, định dạng trực quan 100% và xuất file."""
    if not res or not isinstance(res, dict):
        st.info("Không có dữ liệu chi tiết bản nén.")
        return

    st.markdown(f"### 📦 Kết quả: {res.get('title', 'Bản Nén Farrow')}")
    if res.get('tagline'):
        st.info(f"🎯 **Khẩu quyết cốt lõi:** *\"{res.get('tagline', '')}\"*")

    chunks = res.get("chunks", [])
    if chunks:
        cols = st.columns(min(len(chunks), 3))
        icons = ["🚪", "🖥️", "🪑"]
        for idx, chunk in enumerate(chunks[:3]):
            col = cols[idx % len(cols)]
            with col:
                anchor_name = chunk.get('anchor', f'Mỏ neo #{idx+1}')
                label = chunk.get('label', f'TRỤ {idx+1}')
                principle = chunk.get('principle', '')
                crazy_image = chunk.get('crazy_image', '')
                trigger_q = chunk.get('trigger_question', '')

                card_html = f"""
                <div class="trinity-card" style="margin-bottom: 1rem;">
                    <div class="anchor-badge">{icons[idx]} MỎ NEO: {anchor_name}</div>
                    <h3 style="color: #f8fafc; font-size: 1.15rem; margin-top: 8px;">{label}</h3>
                    <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; margin: 12px 0;">
                        <b>Nguyên lý gốc:</b><br>{principle}
                    </div>
                    <div class="crazy-image-box" style="margin: 10px 0;">
                        🧠 <b>HÌNH ẢNH DỊ BIỆT:</b><br>
                        {crazy_image}
                    </div>
                    <div class="trigger-box" style="margin-top: 10px;">
                        ⚡ <b>PHẢN XẠ 5S:</b><br>
                        <i>"{trigger_q}"</i>
                    </div>
                </div>
                """
                if hasattr(st, "html"):
                    st.html(card_html)
                else:
                    stripped = "\n".join(line.lstrip() for line in card_html.strip().splitlines())
                    st.markdown(stripped, unsafe_allow_html=True)

    if res.get('asymmetric_action'):
        st.success(f"🎯 **Đòn bẩy Bất đối xứng (Actionable Strike):** {res.get('asymmetric_action', '')}")

    # Nút Xuất File Markdown
    st.divider()
    t_name = title if title else res.get("title", "Bản Nén Farrow")
    md_farrow = export_farrow_compression_to_markdown(title=t_name, raw_text=raw_text, res=res, created_at=created_at)
    file_slug = sanitize_filename(t_name)
    st.download_button(
        label="📥 Xuất Bản Nén (.md)",
        data=md_farrow,
        file_name=f"Farrow_{file_slug}.md",
        mime="text/markdown",
        key=f"dl_farrow_{record_id}",
        use_container_width=True
    )


def render_ai_compressor_room(active_api_key: str | None = None):
    """Render phòng chức năng Máy Ép Farrow 1-Click: 2 Tab (Máy Ép & Kho Lưu Trữ Bản Nén)."""
    st.markdown("## ⚡ Máy Ép Farrow 1-Click (Universal AI Compressor)")
    st.caption(
        "Dán bất kỳ tài liệu dài, bài luận, case study hoặc báo cáo nào vào đây. "
        "AI sẽ tự động nghiền nát về đúng 3 khối hạt nhân theo chuẩn Dave Farrow Memory Palace."
    )

    # Tự động nén nếu được chuyển tiếp từ Radar hoặc Decomposition
    if st.session_state.get("auto_run_compress") and st.session_state.get("comp_raw_input"):
        st.session_state["auto_run_compress"] = False
        raw_to_run = st.session_state["comp_raw_input"]
        with st.spinner("🤖 Đang kích hoạt Máy Ép Farrow 1-Click để chuyển hóa dữ liệu thành 3 Mỏ Neo..."):
            auto_res = compress_with_farrow_ai(raw_to_run, api_key=active_api_key)
            if auto_res and not auto_res.get("error"):
                st.session_state["latest_compress_result"] = auto_res
                st.session_state["latest_compress_raw"] = raw_to_run
                save_compression_record(raw_to_run, auto_res)
                st.toast("⚡ Đã tự động nén Farrow & Lưu trữ vĩnh viễn!", icon="💾")

    sb_client = get_supabase_client()
    sync_badge = "☁️ Supabase Cloud (Đồng bộ vĩnh viễn)" if sb_client is not None else "💾 Cục bộ (Local JSON)"
    all_comp = load_compression_history()

    c_tab1, c_tab2 = st.tabs([
        "⚡ Máy Ép 1-Click",
        f"📚 Kho Lưu Trữ Bản Nén ({len(all_comp)})"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: MÁY ÉP 1-CLICK
    # -------------------------------------------------------------------------
    with c_tab1:
        st.markdown("#### 💡 Bấm chọn tình huống mẫu để nạp nhanh:")
        s_cols = st.columns(len(SAMPLE_COMPRESSIONS))
        for s_idx, sample in enumerate(SAMPLE_COMPRESSIONS):
            with s_cols[s_idx]:
                short_title = sample["title"].split()[0] + " " + " ".join(sample["title"].split()[1:3])
                if st.button(short_title, key=f"comp_sample_{s_idx}", help=sample["title"]):
                    st.session_state["comp_raw_input"] = sample["text"]
                    st.rerun()

        default_input = st.session_state.get(
            "comp_raw_input",
            ""
        )
        user_raw_text = st.text_area(
            "Dán văn bản thô vào đây (tối đa 8.000 ký tự):",
            value=default_input,
            placeholder="Ví dụ: Dán một bài phân tích dài về kinh tế vĩ mô, một chiến lược kinh doanh 10 trang, hoặc một bài giảng khó hiểu của trường học...",
            height=160,
            key="comp_text_area"
        )

        col_c_run, col_c_reset = st.columns([3, 1])
        with col_c_run:
            run_comp_btn = st.button("💥 ÉP NÉN THEO CHUẨN DAVE FARROW (RULE OF 3)", type="primary", use_container_width=True, key="btn_run_compress")
        with col_c_reset:
            if st.button("🔄 Làm mới ô nhập", use_container_width=True, key="btn_clear_compress"):
                st.session_state["comp_raw_input"] = ""
                st.session_state.pop("latest_compress_result", None)
                st.session_state.pop("latest_compress_raw", None)
                st.rerun()

        if run_comp_btn:
            if not user_raw_text.strip():
                st.warning("Vui lòng dán nội dung văn bản cần nén!")
            else:
                with st.spinner("🤖 Đang nghiền nát câu chữ rườm rà, bóc tách 3 hạt nhân và tạo hình ảnh kỳ quặc..."):
                    comp_res = compress_with_farrow_ai(user_raw_text.strip(), api_key=active_api_key)
                if not comp_res:
                    st.error("Không nhận được phản hồi từ AI Engine.")
                elif comp_res.get("error"):
                    st.error(f"Lỗi: {comp_res['error']}")
                else:
                    st.session_state["latest_compress_result"] = comp_res
                    st.session_state["latest_compress_raw"] = user_raw_text.strip()
                    # Lưu vào Supabase Cloud & Local JSON
                    saved_ok = save_compression_record(user_raw_text.strip(), comp_res)
                    if saved_ok:
                        st.toast("☁️ Đã tự động lưu bản nén vào Supabase Cloud!", icon="💾")

        # Hiển thị kết quả nén mới nhất
        if "latest_compress_result" in st.session_state:
            res = st.session_state["latest_compress_result"]
            st.success("🎉 Nén thành công & Lưu trữ bền vững! Dưới đây là bộ 3 hạt nhân đã được giải mã:")
            render_farrow_compression_cards(
                res,
                title=res.get("title", "Bản Nén Farrow"),
                raw_text=st.session_state.get("latest_compress_raw", ""),
                record_id="latest"
            )

    # -------------------------------------------------------------------------
    # TAB 2: KHO LƯU TRỮ BẢN NÉN
    # -------------------------------------------------------------------------
    with c_tab2:
        st.markdown(f"#### 📚 Kho Lưu Trữ Lịch Sử Bản Nén Farrow")
        st.caption(f"Trạng thái đồng bộ: **{sync_badge}**. Toàn bộ các bản nén được lưu trữ vĩnh viễn trên Supabase Cloud.")

        history = load_compression_history()
        if not history:
            st.info("💡 Chưa có bản nén nào được lưu. Hãy dán tài liệu vào Tab 1 và bấm ép nén để tự động lưu vào đây!")
        else:
            s_kw = st.text_input("🔍 Tìm kiếm trong kho bản nén:", placeholder="Nhập từ khóa (vd: Porter, năng lượng, Barbell, đầu tư...)", key="search_comp_history")
            filtered_h = history
            if s_kw.strip():
                kw_low = s_kw.strip().lower()
                filtered_h = [
                    h for h in history
                    if kw_low in h.get("title", "").lower()
                    or kw_low in h.get("raw_text", "").lower()
                    or kw_low in h.get("summary", "").lower()
                    or kw_low in str(h.get("result", {})).lower()
                ]

            if not filtered_h:
                st.info("Không tìm thấy bản nén nào khớp với từ khóa tìm kiếm.")

            for h_idx, h_item in enumerate(filtered_h):
                h_id = h_item.get("id", f"comp_{h_idx}")
                h_time = h_item.get("created_at") or h_item.get("time", "Gần đây")
                h_title = h_item.get("title") or "Bản Nén Farrow"
                h_raw = h_item.get("raw_text", "")
                h_res = h_item.get("result", {})

                with st.expander(f"📑 [{h_time}] {h_title}", expanded=(h_idx == 0 and len(filtered_h) == 1)):
                    col_hl, col_hr = st.columns([4, 1])
                    with col_hl:
                        with st.expander("📄 Xem văn bản thô gốc ban đầu", expanded=False):
                            st.write(h_raw if h_raw else "(Không có nội dung văn bản thô)")
                    with col_hr:
                        if st.button("🗑️ Xóa", key=f"btn_del_comp_{h_id}"):
                            delete_compression_record(h_id)
                            st.success("Đã xóa bản nén!")
                            st.rerun()

                    st.divider()
                    render_farrow_compression_cards(
                        h_res,
                        title=h_title,
                        raw_text=h_raw,
                        record_id=h_id,
                        created_at=h_time
                    )

