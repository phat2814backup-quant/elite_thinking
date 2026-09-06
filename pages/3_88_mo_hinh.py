# -*- coding: utf-8 -*-
"""88 Mô hình Hạt nhân"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.mental_models import (
    get_all_models,
    get_pillars,
    TIER_LABELS,
    PILLAR_ICONS,
    filter_models,
    models_to_dataframe,
    export_models_to_csv,
    analyze_latticework_synthesis,
)

st.title("🕸️ Ma Trận 88 Mô Hình Hạt Nhân (Munger Latticework)")
st.caption("Mạng lưới tư duy đa ngành đỉnh cao của Charlie Munger — Tối ưu hóa học siêu tốc với ít nguồn lực nhất")

# Elite Framework Expander
with st.expander("⚡ 5 NGUYÊN TẮC VÀNG LÀM CHỦ 88 MÔ HÌNH VỚI ÍT NGUỒN LỰC NHẤT (ELITE META-LEARNING)", expanded=False):
    c_e1, c_e2 = st.columns(2)
    with c_e1:
        st.markdown("""
        **1. Quy luật Pareto 80/20 (Tier 1 First):**
        Không học dàn trải 88 mô hình cùng lúc. Tập trung làm chủ **25 mô hình Siêu hạt nhân (Tier 1)** trước tiên — chỉ 25 mô hình này đã giải thích và giải quyết được 80% mọi biến cố trong đầu tư, quản trị và đời sống.

        **2. Nén Nguyên tử (First-Principles Compression):**
        Mỗi mô hình được nén về đúng **1 câu quy luật bất biến** của tự nhiên (vật lý, sinh học, toán học). Loại bỏ mọi định nghĩa hàn lâm rườm rà. Nếu không giải thích được trong 1 câu, bạn chưa thực sự hiểu nó.

        **3. Phản xạ Kích hoạt 5 Giây (The 5-Second Trigger Question):**
        Khi đứng trước áp lực thời gian, não bộ không nhớ lý thuyết. Gắn chặt mỗi mô hình với **1 câu hỏi kích hoạt duy nhất**. Khi ra quyết định, chỉ cần tự vấn nhanh câu hỏi này.
        """)
    with c_e2:
        st.markdown("""
        **4. Tư duy Đảo ngược (Inversion & Anti-Models):**
        Munger dạy: *'Chỉ cần biết tôi sẽ chết ở đâu để tôi không bao giờ đến đó'*. Mỗi mô hình đều đi kèm một **Bẫy ngụy biện (Inversion Trap)**. Nhận diện sai lầm nguy hiểm để phòng vệ trước khi tìm kiếm sự thông thái.

        **5. Cộng hưởng Đa ngành (Lollapalooza Synergy):**
        Sức mạnh tối thượng của giới tinh hoa là khả năng **kết hợp 2-3 mô hình từ các ngành khoa học khác nhau** (Vật lý + Sinh học + Tâm lý học) soi chiếu vào một bài toán thực tế để tạo ra đòn bẩy x10 với chi phí gần bằng 0.
        """)

all_models = get_all_models()

# Metric Row
m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)
with m_c1:
    st.metric("🌟 Tổng số mô hình", f"{len(all_models)} mô hình")
with m_c2:
    tier1_count = sum(1 for m in all_models if m.get("tier") == 1)
    st.metric("⭐ Tier 1 (Cốt lõi 80/20)", f"{tier1_count} hạt nhân")
with m_c3:
    tier2_count = sum(1 for m in all_models if m.get("tier") == 2)
    st.metric("🎯 Tier 2 (Chiến lược)", f"{tier2_count} mô hình")
with m_c4:
    gmm_count = sum(1 for m in all_models if m.get("action_steps"))
    st.metric("💎 GMM Chuyên sâu", f"{gmm_count} mô hình", "The Great Mental Models")
with m_c5:
    st.metric("🔬 Trụ cột khoa học", "6 Trụ cột lớn")

st.divider()

# Handle pending navigation/filter actions before widgets are instantiated
if "_action_jump_mid" in st.session_state:
    target_mid = st.session_state.pop("_action_jump_mid")
    st.session_state["filter_model_search"] = target_mid
    st.session_state["filter_model_gmm"] = False
    st.session_state["filter_model_pillar"] = "Tất cả"
    st.session_state["filter_model_tier"] = "Tất cả"

if "_action_filter_gmm" in st.session_state:
    st.session_state.pop("_action_filter_gmm")
    st.session_state["filter_model_gmm"] = True
    st.session_state["filter_model_search"] = ""
    st.session_state["filter_model_pillar"] = "Tất cả"
    st.session_state["filter_model_tier"] = "Tất cả"

if "_action_reset_all" in st.session_state:
    st.session_state.pop("_action_reset_all")
    st.session_state["filter_model_gmm"] = False
    st.session_state["filter_model_search"] = ""
    st.session_state["filter_model_pillar"] = "Tất cả"
    st.session_state["filter_model_tier"] = "Tất cả"

# Filter Bar
f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.8, 2.2, 1.5])
with f_col1:
    sel_pillar = st.selectbox("Lọc theo Trụ cột", get_pillars(), key="filter_model_pillar")
with f_col2:
    sel_tier_label = st.selectbox("Cấp độ đòn bẩy", list(TIER_LABELS.keys()), index=0, key="filter_model_tier")
    sel_tier_val = TIER_LABELS[sel_tier_label]
with f_col3:
    sel_search = st.text_input("🔍 Tìm kiếm tức thì", placeholder="Tên mô hình, đòn bẩy, câu hỏi kích hoạt...", key="filter_model_search")
with f_col4:
    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
    sel_only_gmm = st.checkbox("💎 Chỉ xem GMM", value=False, key="filter_model_gmm", help="Chỉ hiển thị các mô hình đã có Khung GMM Chuyên sâu (Volume 1)")

filtered_models = filter_models(all_models, pillar=sel_pillar, tier=sel_tier_val, query=sel_search, only_gmm=sel_only_gmm)

st.caption(f"Tìm thấy **{len(filtered_models)} / {len(all_models)}** mô hình phù hợp")

# Sub-tabs inside Tab
subtab1, subtab2, subtab3, subtab4 = st.tabs([
    "📊 Bảng Ma trận Tổng hợp",
    "🗂️ Thẻ Chi tiết Thực chiến",
    "🔬 Latticework Sandbox (Cộng hưởng AI)",
    "⚡ Lộ trình Làm chủ 3 Tuần",
])

with subtab1:
    st.markdown("#### 📋 Bảng Tra Cứu Tương Tác Toàn Bộ Mô Hình")
    df_display = models_to_dataframe(filtered_models)
    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        column_config={
            "Mã": st.column_config.TextColumn("Mã", width="small"),
            "Tên Mô Hình": st.column_config.TextColumn("Tên Mô Hình", width="medium"),
            "Trụ Cột": st.column_config.TextColumn("Trụ Cột", width="small"),
            "Cấp Độ Đòn Bẩy": st.column_config.TextColumn("Cấp Độ", width="small"),
            "Khung GMM": st.column_config.TextColumn("Khung GMM", width="small"),
            "Chân Lý Gốc (First Principle)": st.column_config.TextColumn("Chân Lý Gốc", width="large"),
            "Đòn Bẩy Elite": st.column_config.TextColumn("Đòn Bẩy Elite", width="large"),
            "Bẫy Ngụy Biện (Inversion)": st.column_config.TextColumn("Bẫy Sai Lầm", width="large"),
            "Câu Hỏi Kích Hoạt (5s)": st.column_config.TextColumn("Câu Hỏi Kích Hoạt", width="large"),
        }
    )

    # Export CSV Button
    csv_data = export_models_to_csv(filtered_models)
    st.download_button(
        label="📥 Tải xuống CSV (Mở chuẩn tiếng Việt trên Excel)",
        data=csv_data,
        file_name="munger_88_mental_models.csv",
        mime="text/csv",
        use_container_width=False,
    )

with subtab2:
    st.markdown("#### 🗂️ Thẻ Flashcard Bóc Tách Chuyên Sâu Từng Mô Hình")

    # Callout Banner nổi bật: The Great Mental Models Hub (Volumes 1, 2 & 3)
    with st.container(border=True):
        c_banner_info, c_banner_actions = st.columns([2.3, 3.7])
        with c_banner_info:
            st.markdown("""
            ##### 💎 Trọn Bộ The Great Mental Models (Shane Parrish — Volumes 1, 2 & 3)
            Đã tích hợp đầy đủ **Khung phân tích 3 tầng** cho **29 Siêu Mô Hình Hạt Nhân**:
            * **🛠️ Quy trình thực thi 4 bước (Action Protocol)**
            * **⛔ Ranh giới áp dụng (Boundary Conditions — Khi nào KHÔNG dùng)**
            * **🌐 Tình huống thực chiến đa chiều (K12 & Gia đình, Phát triển sự nghiệp, Đầu tư VN-Index)**
            """)
            st.caption("📘 **Vol 1:** Tư duy nền tảng (9) · 📗 **Vol 2:** Vật lý & Sinh học (10) · 📙 **Vol 3:** Hệ thống & Toán học (10)")

        with c_banner_actions:
            st.markdown("**⚡ Phím tắt mở nhanh từng mô hình GMM:**")
            gmm_t1, gmm_t2, gmm_t3 = st.tabs(["📘 Vol 1: Tư duy (9)", "📗 Vol 2: Tự nhiên (10)", "📙 Vol 3: Hệ thống (10)"])

            with gmm_t1:
                # Row 1: Logic & Tinh giản
                r1_c1, r1_c2, r1_c3 = st.columns(3)
                with r1_c1:
                    if st.button("🔬 PHYS-11\nNguyên bản", key="btn_gmm_phys11", use_container_width=True, help="Tư duy Nguyên bản (First Principles)"):
                        st.session_state["_action_jump_mid"] = "PHYS-11"
                        st.rerun()
                with r1_c2:
                    if st.button("🪒 SYS-13\nDao Occam", key="btn_gmm_sys13", use_container_width=True, help="Dao cạo Occam (Occam's Razor)"):
                        st.session_state["_action_jump_mid"] = "SYS-13"
                        st.rerun()
                with r1_c3:
                    if st.button("🕊️ PSY-18\nDao Hanlon", key="btn_gmm_psy18", use_container_width=True, help="Dao cạo Hanlon (Hanlon's Razor)"):
                        st.session_state["_action_jump_mid"] = "PSY-18"
                        st.rerun()

                # Row 2: Nhận thức & Khám phá
                r2_c1, r2_c2, r2_c3 = st.columns(3)
                with r2_c1:
                    if st.button("🗺️ SYS-11\nBản đồ", key="btn_gmm_sys11", use_container_width=True, help="Bản đồ không phải Lãnh thổ"):
                        st.session_state["_action_jump_mid"] = "SYS-11"
                        st.rerun()
                with r2_c2:
                    if st.button("🎯 PSY-12\nVòng tròn", key="btn_gmm_psy12", use_container_width=True, help="Vòng tròn Năng lực"):
                        st.session_state["_action_jump_mid"] = "PSY-12"
                        st.rerun()
                with r2_c3:
                    if st.button("💡 PHYS-10\nThí nghiệm", key="btn_gmm_phys10", use_container_width=True, help="Thí nghiệm Tư duy (Thought Experiment)"):
                        st.session_state["_action_jump_mid"] = "PHYS-10"
                        st.rerun()

                # Row 3: Dự phóng & Quyết định
                r3_c1, r3_c2, r3_c3 = st.columns(3)
                with r3_c1:
                    if st.button("🔄 MATH-05\nĐảo ngược", key="btn_gmm_math05", use_container_width=True, help="Tư duy Đảo ngược (Inversion)"):
                        st.session_state["_action_jump_mid"] = "MATH-05"
                        st.rerun()
                with r3_c2:
                    if st.button("⏳ SYS-10\nBậc hai+", key="btn_gmm_sys10", use_container_width=True, help="Hệ quả Bậc hai & Bậc cao (Second-Order Thinking)"):
                        st.session_state["_action_jump_mid"] = "SYS-10"
                        st.rerun()
                with r3_c3:
                    if st.button("🎲 MATH-03\nXác suất Bayes", key="btn_gmm_math03", use_container_width=True, help="Tư duy Xác suất & Cập nhật Bayes"):
                        st.session_state["_action_jump_mid"] = "MATH-03"
                        st.rerun()

            with gmm_t2:
                st.caption("⚡ **Vật lý học (Physics):**")
                p_c1, p_c2, p_c3, p_c4, p_c5 = st.columns(5)
                with p_c1:
                    if st.button("🚀 PHYS-01\nĐòn bẩy", key="btn_gmm_phys01", use_container_width=True, help="Đòn bẩy (Leverage — Archimedes & Naval Ravikant)"):
                        st.session_state["_action_jump_mid"] = "PHYS-01"
                        st.rerun()
                with p_c2:
                    if st.button("🏎️ PHYS-02\nQuán tính", key="btn_gmm_phys02", use_container_width=True, help="Quán tính (Inertia — Newton's 1st Law)"):
                        st.session_state["_action_jump_mid"] = "PHYS-02"
                        st.rerun()
                with p_c3:
                    if st.button("🔥 PHYS-03\nEntropy", key="btn_gmm_phys03", use_container_width=True, help="Entropy & Định luật 2 Nhiệt động học"):
                        st.session_state["_action_jump_mid"] = "PHYS-03"
                        st.rerun()
                with p_c4:
                    if st.button("💥 PHYS-04\nTới hạn", key="btn_gmm_phys04", use_container_width=True, help="Khối lượng Tới hạn (Critical Mass)"):
                        st.session_state["_action_jump_mid"] = "PHYS-04"
                        st.rerun()
                with p_c5:
                    if st.button("🛑 PHYS-08\nMa sát", key="btn_gmm_phys08", use_container_width=True, help="Ma sát & Độ nhớt (Friction & Viscosity)"):
                        st.session_state["_action_jump_mid"] = "PHYS-08"
                        st.rerun()

                st.caption("🌿 **Sinh học (Biology):**")
                b_c1, b_c2, b_c3, b_c4, b_c5 = st.columns(5)
                with b_c1:
                    if st.button("🧬 BIO-01\nTiến hóa", key="btn_gmm_bio01", use_container_width=True, help="Tiến hóa & Chọn lọc Tự nhiên (Natural Selection)"):
                        st.session_state["_action_jump_mid"] = "BIO-01"
                        st.rerun()
                with b_c2:
                    if st.button("🪺 BIO-02\nHốc ST", key="btn_gmm_bio02", use_container_width=True, help="Hốc Sinh Thái & Chuyên Biệt Hóa (Gause's Law)"):
                        st.session_state["_action_jump_mid"] = "BIO-02"
                        st.rerun()
                with b_c3:
                    if st.button("⚖️ BIO-03\nNội môi", key="btn_gmm_bio03", use_container_width=True, help="Cân bằng Nội môi (Homeostasis)"):
                        st.session_state["_action_jump_mid"] = "BIO-03"
                        st.rerun()
                with b_c4:
                    if st.button("👑 BIO-04\nNữ hoàng Đỏ", key="btn_gmm_bio04", use_container_width=True, help="Hiệu ứng Nữ hoàng Đỏ (The Red Queen Effect)"):
                        st.session_state["_action_jump_mid"] = "BIO-04"
                        st.rerun()
                with b_c5:
                    if st.button("🤝 BIO-05\nCộng sinh", key="btn_gmm_bio05", use_container_width=True, help="Đồng sinh & Cộng sinh (Mutualism & Symbiosis)"):
                        st.session_state["_action_jump_mid"] = "BIO-05"
                        st.rerun()

            with gmm_t3:
                st.caption("📐 **Toán học & Xác suất (Mathematics):**")
                m3_c1, m3_c2, m3_c3 = st.columns(3)
                with m3_c1:
                    if st.button("📈 MATH-01\nLãi kép", key="btn_gmm_math01", use_container_width=True, help="Lãi kép (Compounding — Kỳ quan thứ 8)"):
                        st.session_state["_action_jump_mid"] = "MATH-01"
                        st.rerun()
                with m3_c2:
                    if st.button("⚖️ MATH-02\nPareto 80/20", key="btn_gmm_math02", use_container_width=True, help="Định luật Lũy thừa & Pareto 80/20"):
                        st.session_state["_action_jump_mid"] = "MATH-02"
                        st.rerun()
                with m3_c3:
                    if st.button("🎯 MATH-04\nEV & Kelly", key="btn_gmm_math04", use_container_width=True, help="Giá trị Kỳ vọng & Tiêu chuẩn Kelly"):
                        st.session_state["_action_jump_mid"] = "MATH-04"
                        st.rerun()

                m3_d1, m3_d2, m3_d3 = st.columns(3)
                with m3_d1:
                    if st.button("📉 MATH-06\nHồi quy TB", key="btn_gmm_math06", use_container_width=True, help="Hồi quy về Giá trị Trung bình (Regression to Mean)"):
                        st.session_state["_action_jump_mid"] = "MATH-06"
                        st.rerun()
                with m3_d2:
                    if st.button("🦢 MATH-07\nĐuôi béo", key="btn_gmm_math07", use_container_width=True, help="Phân phối Chuẩn vs Đuôi béo (Fat Tails / Extremistan)"):
                        st.session_state["_action_jump_mid"] = "MATH-07"
                        st.rerun()
                with m3_d3:
                    if st.button("⭕ MATH-10\nNhân số 0", key="btn_gmm_math10", use_container_width=True, help="Tính Phi công thái học & Nhân với số 0 (Non-Ergodicity)"):
                        st.session_state["_action_jump_mid"] = "MATH-10"
                        st.rerun()

                st.caption("⚙️ **Kỹ thuật & Hệ thống (Systems Thinking):**")
                s3_c1, s3_c2, s3_c3, s3_c4 = st.columns(4)
                with s3_c1:
                    if st.button("🔁 SYS-01\nPhản hồi", key="btn_gmm_sys01", use_container_width=True, help="Vòng Phản hồi Âm & Dương (Feedback Loops)"):
                        st.session_state["_action_jump_mid"] = "SYS-01"
                        st.rerun()
                with s3_c2:
                    if st.button("🛡️ SYS-02\nBiên an toàn", key="btn_gmm_sys02", use_container_width=True, help="Biên độ An toàn & Dự phòng (Margin of Safety)"):
                        st.session_state["_action_jump_mid"] = "SYS-02"
                        st.rerun()
                with s3_c3:
                    if st.button("🍾 SYS-03\nNút cổ chai", key="btn_gmm_sys03", use_container_width=True, help="Nút Cổ chai & Lý thuyết Điểm Hạn chế (TOC)"):
                        st.session_state["_action_jump_mid"] = "SYS-03"
                        st.rerun()
                with s3_c4:
                    if st.button("🏋️ SYS-04\nChống mong manh", key="btn_gmm_sys04", use_container_width=True, help="Tính Chống Mong manh (Antifragility & Barbell)"):
                        st.session_state["_action_jump_mid"] = "SYS-04"
                        st.rerun()

            btn_all_gmm, btn_reset = st.columns(2)
            with btn_all_gmm:
                if st.button("✨ Lọc trọn bộ 29 mô hình GMM", type="primary", use_container_width=True):
                    st.session_state["_action_filter_gmm"] = True
                    st.rerun()
            with btn_reset:
                if st.button("🔄 Hiện đủ 88 mô hình", use_container_width=True):
                    st.session_state["_action_reset_all"] = True
                    st.rerun()

    st.caption(f"Đang hiển thị **{len(filtered_models)} / {len(all_models)}** mô hình phù hợp")

    for m in filtered_models:
        tier_badge = {1: "⭐ Tier 1 (Siêu hạt nhân)", 2: "🎯 Tier 2 (Chiến lược)", 3: "🔬 Tier 3 (Hệ thống)"}.get(m.get("tier"), "")
        has_gmm = bool(m.get("action_steps"))
        deep_badge = " · 💎 GMM Chuyên sâu" if has_gmm else ""
        icon = PILLAR_ICONS.get(m.get("pillar", ""), "📌")

        # Tự động mở rộng (expanded=True) nếu đang lọc GMM hoặc nếu kết quả hiển thị ít
        is_expanded = True if (sel_only_gmm or len(filtered_models) <= 3) else False

        with st.expander(f"{icon} [{m.get('id')}] {m.get('name_vi')} — {m.get('name_en')} ({tier_badge}{deep_badge})", expanded=is_expanded):
            c_left, c_right = st.columns([3, 2])
            with c_left:
                st.markdown(f"**⚡ Chân lý gốc (First Principle):**")
                st.info(m.get("first_principle", ""))
                st.markdown(f"**🚀 Đòn bẩy Elite (Cách vận dụng tối thượng):**")
                st.write(m.get("elite_leverage", ""))
            with c_right:
                st.markdown(f"**⚠️ Bẫy ngụy biện (Inversion Trap):**")
                st.warning(m.get("inversion_trap", ""))
                st.markdown(f"**⏱️ Câu hỏi kích hoạt 5 giây (Trigger Prompt):**")
                st.caption(f"👉 *\"{m.get('trigger_question', '')}\"*")

            if m.get("lollapalooza_pairs"):
                st.markdown(f"**🔗 Cặp cộng hưởng Lollapalooza đề xuất:** `{'` · `'.join(m['lollapalooza_pairs'])}`")

            # GMM Deep Framework: Action Steps, Boundary Conditions & Real-World Case Studies
            if m.get("action_steps") or m.get("boundary_conditions") or m.get("real_world_case"):
                st.divider()
                st.markdown("#### 💎 Khung Phân Tích Chuyên Sâu (The Great Mental Models Framework)")

                col_proto, col_bound = st.columns([3, 2])
                with col_proto:
                    if m.get("action_steps"):
                        st.markdown("**🛠️ Quy trình thực thi 4 bước (Action Protocol):**")
                        for step in m["action_steps"]:
                            st.markdown(f"- {step}")
                with col_bound:
                    if m.get("boundary_conditions"):
                        st.markdown("**⛔ Ranh giới áp dụng (Khi nào KHÔNG dùng):**")
                        st.error(m["boundary_conditions"])

                if m.get("real_world_case"):
                    st.markdown("**🌐 Tình huống thực chiến đa chiều (Case Studies Thực tế):**")
                    st.markdown(m["real_world_case"])

with subtab3:
    st.markdown("#### 🔬 Latticework Sandbox — Phòng Thí Nghiệm Đa Ngành")
    st.markdown("""
    Chọn một tình huống thực tế của bạn và chọn **2 đến 3 mô hình từ các trụ cột khoa học khác nhau**. 
    Hệ thống AI sẽ đóng vai Charlie Munger để soi chiếu đa chiều và tìm ra **hiệu ứng cộng hưởng Lollapalooza x10 đòn bẩy**.
    """)

    sandbox_sample = st.selectbox(
        "Gợi ý tình huống thực tế",
        [
            "— Tự nhập tình huống riêng của bạn bên dưới —",
            "Tôi muốn bắt đầu học và ứng dụng AI tự động hóa vào công việc hiện tại nhưng đang bị quá tải thông tin và sợ tốn thời gian vô ích.",
            "Đang cân nhắc có nên bỏ một khoản đầu tư chứng khoán đang bị lỗ 25% để chuyển tiền sang một cơ hội kinh doanh mới mở ra.",
            "Muốn xây dựng một sản phẩm công nghệ nhỏ (SaaS/Tool) với nguồn vốn ít, làm sao để sản phẩm tự lan tỏa mà không tốn tiền quảng cáo?",
            "Nhóm làm việc của tôi đang xuất hiện tình trạng một vài người ỷ lại, năng suất giảm sút và các thành viên bắt đầu bất mãn ngầm.",
        ],
        key="sandbox_sample_sel"
    )
    sandbox_init = "" if sandbox_sample.startswith("—") else sandbox_sample
    sandbox_problem = st.text_area("Vấn đề / Quyết định thực tế cần soi chiếu", value=sandbox_init, height=100, key="sandbox_prob_input")

    # Multi-select models
    model_options = {f"[{m.get('id')}] {m.get('name_vi')} ({m.get('pillar')})": m for m in all_models}
    
    # Default selection: 1 Physics + 1 Psychology + 1 Economics
    default_keys = [
        k for k in model_options.keys() 
        if any(x in k for x in ["[PHYS-01]", "[PSY-01]", "[ECON-02]"])
    ]
    
    selected_model_keys = st.multiselect(
        "Chọn 2-3 Mô hình Hạt nhân (Khuyến khích chọn chéo từ các Trụ cột khác nhau)",
        options=list(model_options.keys()),
        default=default_keys[:3],
        max_selections=4,
        key="sandbox_models_sel",
    )

    if st.button("💥 Kích Hoạt Phân Tích Lollapalooza (Gemini)", type="primary", use_container_width=True):
        if not active_keys:
            st.warning("Cần Gemini API Key để kích hoạt AI Latticework Engine.")
        elif not sandbox_problem.strip():
            st.warning("Vui lòng nhập vấn đề thực tế cần phân tích.")
        elif len(selected_model_keys) < 2:
            st.warning("Vui lòng chọn ít nhất 2 mô hình để tạo hiệu ứng cộng hưởng đa ngành.")
        else:
            chosen_models_data = [model_options[k] for k in selected_model_keys]
            with st.spinner("Đang kích hoạt mạng lưới Latticework và phân tích cộng hưởng Lollapalooza qua Gemini..."):
                synth_res = analyze_latticework_synthesis(active_keys, model_choice, sandbox_problem.strip(), chosen_models_data)

            if not synth_res:
                st.error("Không có kết quả trả về.")
            elif synth_res.get("error"):
                st.error(synth_res["error"])
                if synth_res.get("raw"):
                    st.code(synth_res["raw"])
            else:
                key_tag = f" (Key: `{synth_res.get('_used_key')}`)" if synth_res.get("_used_key") else ""
                st.success(f"Đã hoàn thành phân tích cộng hưởng Lollapalooza{key_tag}")

                st.markdown("### 🎯 Bản Chất Gốc Rễ Vấn Đề")
                st.info(synth_res.get("problem_summary", "—"))

                st.markdown("### 🔍 Góc Nhìn Đa Chiều Từng Mô Hình")
                for m_app in synth_res.get("models_applied", []):
                    with st.expander(f"📌 {m_app.get('model_name', 'Mô hình')}", expanded=True):
                        st.markdown(f"**Soi sáng:** {m_app.get('lens_analysis', '')}")
                        st.markdown(f"**Insight thực chiến:** *{m_app.get('actionable_insight', '')}*")

                st.markdown("### 💥 Điểm Bùng Nổ Cộng Hưởng (Lollapalooza Synergy)")
                st.success(synth_res.get("lollapalooza_synergy", "—"))

                st.markdown("### 🛡️ Kiểm Tra Bẫy Đảo Ngược (Inversion Check)")
                st.warning(synth_res.get("inversion_check", "—"))

                st.markdown("### 🚀 Kế Hoạch Hành Động Elite")
                for idx_act, act in enumerate(synth_res.get("elite_action_plan", []), 1):
                    st.markdown(f"**{idx_act}.** {act}")

with subtab4:
    st.markdown("#### ⚡ Lộ Trình Làm Chủ 88 Mô Hình Hạt Nhân Trong 3 Tuần")
    st.markdown("""
    Làm chủ 88 mô hình không phải là học thuộc lòng như từ điển. Dưới đây là chiến lược hành quân chuẩn xác của giới tinh hoa để nạp toàn bộ mạng lưới tư duy này vào tiềm thức với chi phí năng lượng thấp nhất:
    """)

    c_w1, c_w2, c_w3 = st.columns(3)
    with c_w1:
        st.markdown("""
        ### 📅 TUẦN 1: Cốt Lõi Sống Còn
        **Mục tiêu: Làm chủ 25 mô hình Tier 1**
        - **Thời gian:** 20 phút mỗi sáng.
        - **Nhiệm vụ:** Mỗi ngày nạp 3-4 mô hình Tier 1.
        - **Thực hành:** 
          1. Đọc Chân lý gốc 1 câu.
          2. Học thuộc lòng Câu hỏi kích hoạt (Trigger Question).
          3. Tự lấy 1 ví dụ trong quá khứ bản thân từng dính bẫy ngụy biện (Inversion Trap).
        - **Kết quả:** Sau 7 ngày, bạn sở hữu 80% sức mạnh tư duy của Charlie Munger.
        """)
    with c_w2:
        st.markdown("""
        ### 📅 TUẦN 2: Chiến Lược Mở Rộng
        **Mục tiêu: Nạp 37 mô hình Tier 2**
        - **Thời gian:** 20 phút mỗi sáng.
        - **Nhiệm vụ:** Mỗi ngày nạp 5 mô hình Tier 2.
        - **Thực hành:**
          1. Phân nhóm theo cặp đối xứng (ví dụ: Cung cầu vs Lợi thế so sánh; Bẫy mỏ neo vs Thiên kiến sẵn có).
          2. Áp dụng ngay vào các tin tức thời sự, biến động thị trường chứng khoán hoặc các quyết định tại cơ quan.
        - **Kết quả:** Nhìn thấu động cơ ngầm và cấu trúc vận hành của mọi tổ chức.
        """)
    with c_w3:
        st.markdown("""
        ### 📅 TUẦN 3: Luyện Phản Xạ Đa Ngành
        **Mục tiêu: Luyện tập Lollapalooza Synthesis**
        - **Thời gian:** 15 phút mỗi tối.
        - **Nhiệm vụ:** Không đọc thêm lý thuyết; đưa các vấn đề thực tế vào **Latticework Sandbox**.
        - **Thực hành:**
          1. Đặt mục tiêu mỗi quyết định quan trọng phải được soi qua ít nhất 3 lăng kính khác ngành.
          2. Tự thiết kế các cơ chế Win-Win dựa trên Lý thuyết trò chơi và Hệ sinh thái.
        - **Kết quả:** Hình thành trực giác tinh hoa, biến mạng lưới mô hình thành bản năng phản xạ tự nhiên.
        """)

st.divider()
st.info("🎯 **Sẵn sàng kiểm tra phản xạ của bạn?** Vào ngay **Tab [⚡ Đấu trường Luyện nhớ]** để làm trắc nghiệm tình huống 88 mô hình, lật Flashcards và thử thách Richard Feynman!")

