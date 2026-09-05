# -*- coding: utf-8 -*-
"""Thế cuộc & Quy luật Elite"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.macro_evolution import (
    CIVILIZATIONAL_ERAS,
    ELITE_HIDDEN_LAWS,
    SAMPLE_MACRO_TRENDS,
    analyze_macro_radar,
)

st.title("🌐 Lăng Kính Thế Cuộc & Quy Luật Vận Hành Ngầm Của Giới Elite")
st.caption("Bóc tách dòng chảy chuyển dịch các thời đại kinh tế và giải mã 8 mật mã chiến lược của tầng lớp tinh hoa dưới lăng kính First Principles.")

macro_sub_tabs = st.tabs([
    "⏳ Trục Tiến Hóa 5 Kỷ Nguyên",
    "👁️ 8 Mật Mã Vận Hành Ngầm Elite",
    "📡 Máy Quét Đọc Vị Thế Cuộc (AI Radar)",
])

# --- SUB-TAB 0: Trục Tiến Hóa 5 Kỷ Nguyên ---
with macro_sub_tabs[0]:
    st.markdown("""
    ### 🧬 Bản Chất Chuyển Dịch Kinh Tế Qua Các Thời Đại
    Bản chất của mọi nền kinh tế, dù ở bất kỳ thời đại nào, đều xoay quanh việc giải quyết bài toán cốt lõi: 
    **Phân bổ nguồn lực khan hiếm để tối đa hóa sự sinh tồn và phát triển.**
    
    Sự chuyển giao giữa các kỷ nguyên không diễn ra ngẫu nhiên, mà tuân theo cơ chế vật lý bất biến:
    """)

    st.info("""
    💥 **Định luật Chuyển Pha Kinh Tế (The Phase-Transition Law):**  
    Khi một rào cản về **Năng lượng** hoặc **Công nghệ** bị phá vỡ ➔ **Nguồn lực cốt lõi cũ bị bình dân hóa (tiến về giá trị 0đ)** ➔ **Một nguồn lực mới lên ngôi** ➔ Dẫn đến sự tổ chức lại toàn bộ cấu trúc quyền lực, nhà nước và xã hội.
    """)

    st.markdown("#### 📐 Công Thức 3 Biến Số Đọc Vị Mọi Biến Động Vĩ Mô:")
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown("""
        **1. Chi Phí Giao Dịch (Transaction Costs)**  
        Mô hình mới luôn thắng mô hình cũ vì kéo tụt chi phí giao dịch (tìm kiếm, niềm tin, đàm phán, thực thi). Tiền giấy thay vàng vì nhẹ; E-commerce thay chợ vì bỏ mặt bằng; AI thay quy trình vì chi phí nhận thức = 0.
        """)
    with c_m2:
        st.markdown("""
        **2. Sự Trượt Giá Của Nguồn Lực Cũ**  
        Khi thời đại mới đến, nguồn lực cũ không biến mất nhưng bị *bình dân hóa (commoditized)*, tỷ trọng trong tổng của cải toàn cầu ngày càng teo nhỏ so với nguồn lực công nghệ mới.
        """)
    with c_m3:
        st.markdown("""
        **3. Công Cụ Đòn Bẩy (Leverage Shift)**  
        - Thời Nông nghiệp: Đòn bẩy **Sức người (Tá điền)**  
        - Thời Công nghiệp: Đòn bẩy **Vốn (Tư bản & Máy móc)**  
        - Thời Thông tin & AI: Đòn bẩy **Code, Media & AI Compute** (Không cần xin phép ai).
        """)

    st.divider()
    st.markdown("### 🗺️ Khám Phá 5 Kỷ Nguyên Tiến Hóa Văn Minh")

    era_titles = [f"{e['icon']} {e['name']}" for e in CIVILIZATIONAL_ERAS]
    selected_era_idx = st.radio(
        "Chọn thời đại để mổ xẻ cấu trúc kinh tế:",
        range(len(CIVILIZATIONAL_ERAS)),
        format_func=lambda i: era_titles[i],
        horizontal=True,
        key="macro_era_selector",
    )

    era_data = CIVILIZATIONAL_ERAS[selected_era_idx]

    st.markdown(f"#### {era_data['icon']} {era_data['name']} — *{era_data['subtitle']}*")
    st.caption(f"⏱️ Khung thời gian: **{era_data['timeframe']}**")

    c_e_left, c_e_right = st.columns([1, 1])
    with c_e_left:
        st.markdown(f"**📌 Nguồn Lực Cốt Lõi:**  \n{era_data['core_resource']}")
        st.markdown(f"**⚡ Năng Lượng & Công Nghệ:**  \n{era_data['energy_tech']}")
        st.markdown(f"**🛑 Giới Hạn / Điểm Nghẽn (Constraint):**  \n{era_data['constraint']}")
        st.markdown(f"**💼 Mô Hình Kinh Tế & Thặng Dư:**  \n{era_data['economic_model']}")

    with c_e_right:
        st.error(f"**📉 Bị Bình Dân Hóa (Rớt Giá Về 0đ):**  \n{era_data['commoditized']}")
        st.success(f"**💎 Nút Thắt Khan Hiếm Mới Lên Ngôi:**  \n{era_data['new_scarce_asset']}")
        st.markdown(f"**🚀 Đòn Bẩy Của Giới Tinh Hoa:**  \n{era_data['elite_leverage']}")
        st.warning(f"**💥 Tại Sao Chuyển Giao? (Turning Point):**  \n{era_data['turning_point']}")

    with st.expander("🔬 Phân tích bản chất sâu sắc & Bài học lịch sử", expanded=True):
        st.markdown(era_data['deep_dive'])
        st.markdown("**Các mô hình hạt nhân kích hoạt:**")
        st.write(" · ".join([f"`{m['name']}`" for m in era_data.get('associated_models', [])]))
        st.markdown("**Chế độ tư duy tương ứng:**")
        st.write(" · ".join([f"**[{mode}]**" for mode in era_data.get('associated_modes', [])]))

    st.divider()
    st.markdown("### 📊 Ma Trận So Sánh Tổng Hợp 5 Kỷ Nguyên")
    comparison_rows = []
    for e in CIVILIZATIONAL_ERAS:
        comparison_rows.append({
            "Kỷ Nguyên": f"{e['icon']} {e['name']}",
            "Nguồn Lực Cốt Lõi": e['core_resource'][:32] + "...",
            "Giới Hạn Vật Lý": e['constraint'][:32] + "...",
            "Thứ Rớt Giá Về 0": e['commoditized'][:28] + "...",
            "Nút Thắt Khan Hiếm Mới": e['new_scarce_asset'].replace('\n', ' ')[:35] + "...",
            "Đòn Bẩy Elite": e['elite_leverage'][:32] + "...",
        })
    st.dataframe(comparison_rows, use_container_width=True)

    st.divider()
    st.markdown("""
    ### 🤖 Tiêu Điểm: Kỷ Nguyên 5 — Nền Kinh Tế "Khan Hiếm Tính Chân Thực"
    Trong kỷ nguyên AI (Synthetic Abundance), chi phí biên để tạo ra nội dung, hình ảnh, văn bản, mã code và thậm chí logic cơ bản **đều lao dốc về 0**. 
    Theo **Định lý Khan hiếm Bổ trợ**, giá trị kinh tế lập tức dịch chuyển sang 4 trụ cột không thể giả mạo:
    """)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.info("""
        **1. 🆔 Nền Kinh Tế Chứng Minh Nhân Dạng (Proof-of-Personhood)**
        - Web mở bị ngập trong bot và AI Slop. 'Ẩn danh' sẽ bị thuật toán coi là bot rác và bỏ qua.
        - Người dùng trả phí cho tích xanh (X, Meta) và World ID để chứng minh 'Tôi là một thực thể sinh học có thật'.
        """)
        st.warning("""
        **2. 🎭 Định Giá Cho "Sự Không Hoàn Hảo" (The Imperfection Premium)**
        - AI tạo ra những bài viết mượt mà, video không tì vết. Hệ quả: Con người bắt đầu chán ngấy sự hoàn hảo vô hồn.
        - Lên ngôi: Nội dung Raw/Unedited, podcast kéo dài 3 tiếng, livestream tự nhiên không kịch bản. Con người khao khát nhìn thấy sai sót duyên dáng, sự ngập ngừng và cảm xúc nguyên bản.
        """)
    with c_p2:
        st.success("""
        **3. 🎪 Bùng Nổ Trải Nghiệm Vật Lý (Physicality & Live Presence)**
        - Bạn có thể nghe bài hát AI tạo ra miễn phí, nhưng không thể làm giả việc bạn đang đứng cùng 50.000 người thật tại Concert.
        - Vé concert, sự kiện thể thao, hội thảo offline và đĩa than analog (Vinyl) tăng trưởng phi mã vì tính xác thực vật lý không thể sao chép số.
        """)
        st.error("""
        **4. 🏰 Thuyết Internet Chết (Dead Internet) & Các Ốc Đảo Khép Kín**
        - Web mở trở thành bãi rác nội dung AI giật gân (Low-trust environment).
        - Giới tinh hoa và người cầu tiến rút lui vào các **Cộng đồng khép kín (Gated Communities)**: Discord riêng, nhóm kín có bảo lãnh, nơi tỷ lệ Tín hiệu/Nhiễu (Signal-to-Noise) đạt 99%.
        """)

# --- SUB-TAB 1: 8 Mật Mã Vận Hành Ngầm Elite ---
with macro_sub_tabs[1]:
    st.markdown("""
    ### 👁️ Bộ Mật Mã 8 Quy Tắc Vận Hành Ngầm Của Giới Tinh Hoa (The Elite Playbook)
    Những quy tắc dưới đây không phải là thuyết âm mưu, mà là **các định luật toán học, vật lý và kinh tế học hành vi** 
    được giới tinh hoa thấu hiểu và áp dụng triệt để nhằm định vị dòng chảy tài sản và quyền lực.
    """)

    search_law = st.text_input("🔍 Tìm kiếm quy tắc ngầm hoặc mô hình liên kết:", "", placeholder="Ví dụ: Cantillon, Bất đối xứng, Khan hiếm, Coase, Đòn bẩy...")

    for law in ELITE_HIDDEN_LAWS:
        if search_law.strip():
            match = (
                search_law.lower() in law["title"].lower()
                or search_law.lower() in law["axiom"].lower()
                or any(search_law.lower() in m.lower() for m in law.get("linked_models", []))
            )
            if not match:
                continue

        with st.expander(f"{law['icon']} #{law['number']}. {law['title']}", expanded=(law['number'] <= 2 and not search_law.strip())):
            st.markdown(f"> *\"{law['axiom']}\"*")
            
            c_l1, c_l2 = st.columns(2)
            with c_l1:
                st.error(f"👥 **Góc Nhìn Đám Đông (Bẫy Nhận Thức):**  \n{law['mass_perception']}")
                st.success(f"👁️ **Hành Động Của Giới Elite:**  \n{law['elite_execution']}")
            with c_l2:
                st.info(f"🔬 **Cơ Sở Toán Học / Vật Lý / Kinh Tế:**  \n{law['physics_math_basis']}")
                st.warning(f"💡 **Ví Dụ Thực Chiến & Lịch Sử:**  \n{law['real_world_case']}")

            st.markdown("---")
            c_sub1, c_sub2, c_sub3 = st.columns([1, 1, 1])
            with c_sub1:
                st.markdown("**🕸️ Mô hình hạt nhân liên kết:**")
                st.caption(" · ".join([f"`{m}`" for m in law['linked_models']]))
            with c_sub2:
                st.markdown("**🧠 Chế độ tư duy tương ứng:**")
                st.caption(" · ".join([f"**{mode}**" for mode in law['linked_modes']]))
            with c_sub3:
                st.markdown("**🎯 Câu hỏi tự vấn vị thế bản thân:**")
                st.caption(f"*{law['self_inquiry']}*")

# --- SUB-TAB 2: Máy Quét Đọc Vị Thế Cuộc (AI Radar) ---
with macro_sub_tabs[2]:
    st.markdown("""
    ### 📡 Máy Quét Đọc Vị Thế Cuộc Bằng AI (First-Principles Macro Radar)
    Ứng dụng **Định lý Khan hiếm Bổ trợ**, **Tư duy Bậc hai** và **Bộ Mật mã Elite** để bóc tách bất kỳ biến động vĩ mô, công nghệ mới hoặc xu hướng xã hội nào. 
    Máy quét sẽ phân tích: *Thứ gì sắp rớt giá về 0? Nút thắt khan hiếm mới ở đâu? Giới tinh hoa sẽ đi nước cờ gì?*
    """)

    st.markdown("##### 💡 Hoặc bấm chọn một xu hướng mẫu kinh điển để quét nhanh:")
    sample_cols = st.columns(len(SAMPLE_MACRO_TRENDS))
    for s_idx, sample in enumerate(SAMPLE_MACRO_TRENDS):
        with sample_cols[s_idx]:
            sample_short_title = sample["title"].split()[0] + " " + " ".join(sample["title"].split()[1:3])
            if st.button(sample_short_title, key=f"macro_sample_{s_idx}", help=sample["title"]):
                st.session_state["macro_radar_input"] = sample["query"]
                st.rerun()

    default_query = st.session_state.get(
        "macro_radar_input",
        "Sự xuất hiện của các AI Agents tự hành có khả năng lập trình, viết báo cáo, xử lý dữ liệu và vận hành quy trình kinh doanh 24/7 với chi phí tiệm cận 0."
    )

    trend_text = st.text_area(
        "Nhập mô tả biến động vĩ mô, công nghệ hoặc sự kiện cần bóc tách:",
        value=default_query,
        height=110,
        key="macro_trend_text_area",
    )

    btn_radar = st.button("📡 Quét Đọc Vị Theo First Principles", type="primary", use_container_width=True)

    if btn_radar:
        if not active_keys:
            st.error("Chưa có API key để chạy AI Macro Radar. Hãy thêm key ở sidebar.")
        elif not trend_text.strip():
            st.warning("Vui lòng nhập mô tả sự kiện hoặc xu hướng cần phân tích.")
        else:
            with st.spinner("Đang kích hoạt Bộ máy Phân tích Thế cuộc & First Principles Engine..."):
                result = analyze_macro_radar(active_keys, model_choice, trend_text.strip())

            if not result:
                st.error("Không nhận được phản hồi từ AI Engine.")
            elif "error" in result and not result.get("trend_summary"):
                st.error(f"Lỗi phân tích: {result['error']}")
            else:
                st.success("✅ Đã hoàn tất bóc tách thế cuộc theo First Principles!")
                if result.get("_used_key"):
                    st.caption(f"Đã xử lý an toàn qua Key: `{result['_used_key']}`")

                st.markdown(f"#### 🎯 Bản Chất Cốt Lõi: {result.get('trend_summary', '')}")
                st.info(f"**⚡ Chi Phí Giao Dịch Bị Kéo Tụt:** {result.get('transaction_costs_impact', '')}")

                c_r1, c_r2 = st.columns(2)
                with c_r1:
                    st.error("#### 📉 Nguồn Lực Bị Trượt Giá Về 0 (Commoditized)")
                    for item in result.get("commoditized_assets", []):
                        st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")

                with c_r2:
                    st.success("#### 💎 Nút Thắt Khan Hiếm Mới (Complementary Scarcity)")
                    for item in result.get("complementary_scarcities", []):
                        st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")

                st.markdown("#### 👁️ Nước Cờ Chiến Lược Của Giới Elite")
                for move in result.get("elite_strategic_moves", []):
                    st.markdown(f"- ♟️ {move}")

                c_bot1, c_bot2 = st.columns(2)
                with c_bot1:
                    st.markdown("#### 🕸️ Các Mô Hình Hạt Nhân Kích Hoạt")
                    for m in result.get("activated_mental_models", []):
                        st.markdown(f"- `{m.get('model_name', '')}`: {m.get('mechanism', '')}")
                with c_bot2:
                    st.markdown("#### 🧭 Playbook Hành Động Cho Bạn")
                    for act in result.get("action_playbook_for_individual", []):
                        st.markdown(f"- 🚀 {act}")

