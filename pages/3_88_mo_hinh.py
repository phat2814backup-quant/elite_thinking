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

    # Callout Banner nổi bật: The Great Mental Models Hub
    with st.container(border=True):
        c_banner_info, c_banner_actions = st.columns([3, 2])
        with c_banner_info:
            st.markdown("""
            ##### 💎 Tuyển Tập The Great Mental Models (Shane Parrish — Volume 1)
            Đã tích hợp đầy đủ **Khung phân tích 3 tầng** bao gồm:
            * **🛠️ Quy trình thực thi 4 bước (Action Protocol)**
            * **⛔ Ranh giới áp dụng (Boundary Conditions — Khi nào KHÔNG dùng)**
            * **🌐 Tình huống thực chiến đa chiều (K12 & Gia đình, Phát triển sự nghiệp, Đầu tư VN-Index)**
            """)
            st.caption("📌 Hiện tại hệ thống đã tích hợp 3 siêu mô hình đầu tiên: **[SYS-11]**, **[PSY-12]**, **[MATH-05]**.")

        with c_banner_actions:
            st.markdown("**⚡ Phím tắt mở xem ngay:**")
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("🗺️ SYS-11\nBản đồ", use_container_width=True, help="Bản đồ không phải Lãnh thổ"):
                    st.session_state["_action_jump_mid"] = "SYS-11"
                    st.rerun()
            with col_b2:
                if st.button("🎯 PSY-12\nVòng tròn", use_container_width=True, help="Vòng tròn Năng lực"):
                    st.session_state["_action_jump_mid"] = "PSY-12"
                    st.rerun()
            with col_b3:
                if st.button("🔄 MATH-05\nĐảo ngược", use_container_width=True, help="Tư duy Đảo ngược"):
                    st.session_state["_action_jump_mid"] = "MATH-05"
                    st.rerun()

            btn_all_gmm, btn_reset = st.columns(2)
            with btn_all_gmm:
                if st.button("✨ Lọc cả 3 mô hình GMM", type="primary", use_container_width=True):
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

