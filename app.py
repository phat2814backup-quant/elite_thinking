# -*- coding: utf-8 -*-
"""
ELITE FARROW 10-MINUTE ENGINE (V2.2)
Ứng dụng Nén Tri Thức & Phản Xạ 10 Phút theo Phương pháp Kỷ lục gia Guinness Dave Farrow
Thiết kế tối giản tuyệt đối:
1. 🏛️ Lâu Đài Ký Ức (The 3 Trinity) — 11 Chủ đề nén sẵn theo 7 nhóm ngành khoa học
2. ⏱️ Phòng Ép Xung 10 Phút (Focus Sprint) — Chạy nước rút tập trung cao độ
3. ⚡ Máy Ép Farrow 1-Click (AI Compressor) — Nén tài liệu dài với xoay tua 8 API keys
4. 🫁 Trạm Thở Bụng Sạc Pin — Box Breathing phục hồi pin não
"""

import os
import time
import textwrap
import html
import base64
import streamlit as st


try:
    import dotenv
    for p in ["D:/02_HocTap/elite/.env", "D:/02_HocTap/elite_thinking/.env", ".env"]:
        if os.path.exists(p):
            dotenv.load_dotenv(p, override=True)
except ImportError:
    pass

from core.knowledge_vault import (
    get_all_farrow_topics,
    get_farrow_topic_by_id,
    get_farrow_topics_by_category
)
from core.farrow_engine import (
    compress_with_farrow_ai,
    get_all_gemini_api_keys,
    get_api_key_status
)
from core.models_engine import (
    load_unified_farrow_catalog,
    get_farrow_models_grouped,
    get_farrow_metrics,
    draw_random_farrow_sprint_trio,
    get_models_for_topic_chunk,
    get_model_full_detail
)
from core.macro_evolution import (
    CIVILIZATIONAL_ERAS,
    ELITE_HIDDEN_LAWS,
    SAMPLE_MACRO_TRENDS,
    analyze_macro_radar,
)
from core.db_storage import (
    load_macro_scans,
    save_macro_scan,
    delete_macro_scan,
    get_supabase_client
)


# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Elite Farrow — Động Cơ Nén Tri Thức 10 Phút",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
base_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(base_dir, "assets", "style.css")
if not os.path.exists(css_path):
    css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_html(html_content: str):
    """Render HTML an toàn tuyệt đối, sử dụng st.html của Streamlit để tránh triệt để lỗi code-block của Markdown."""
    if hasattr(st, "html"):
        st.html(html_content)
    else:
        stripped = "\n".join(line.lstrip() for line in html_content.strip().splitlines())
        st.markdown(stripped, unsafe_allow_html=True)


def get_anchor_image_html(topic_id: str, chunk_id: str) -> str:
    """Tự động kiểm tra và nhúng ảnh mỏ neo siêu nhẹ định dạng WebP/PNG/SVG nếu có."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in [".webp", ".png", ".jpg", ".svg"]:
        candidate_paths = [
            os.path.join(base_dir, "assets", "anchors", f"{topic_id}_{chunk_id}{ext}"),
            os.path.join("assets", "anchors", f"{topic_id}_{chunk_id}{ext}"),
            os.path.join("D:/02_HocTap/elite/assets/anchors", f"{topic_id}_{chunk_id}{ext}"),
            os.path.join("D:/02_HocTap/elite_thinking/assets/anchors", f"{topic_id}_{chunk_id}{ext}")
        ]
        for img_path in candidate_paths:
            if os.path.exists(img_path):
                try:
                    with open(img_path, "rb") as f:
                        b64_data = base64.b64encode(f.read()).decode("utf-8")
                    mime = "image/svg+xml" if ext == ".svg" else f"image/{ext[1:]}"
                    return f'<div style="text-align: center; margin: 10px 0 14px 0;"><img src="data:{mime};base64,{b64_data}" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.4); box-shadow: 0 4px 15px rgba(0,0,0,0.4);" alt="Mỏ neo trực quan" /></div>'
                except Exception:
                    pass
    return ""




PILLAR_ICONS = {
    "Kinh tế học": "📈",
    "Tâm lý học": "🧠",
    "Vật lý học": "⚛️",
    "Sinh học": "🧬",
    "Toán học & Xác suất": "🎲",
    "Hệ thống": "🕸️",
}


def render_gmm_detailed_model(m: dict, is_expanded: bool = False):
    """Render chi tiết mô hình theo chuẩn The Great Mental Models Framework với đầy đủ các trường tinh hoa."""
    tier_badge = {1: "⭐ Tier 1 (Siêu hạt nhân)", 2: "🎯 Tier 2 (Chiến lược)", 3: "🔬 Tier 3 (Hệ thống)"}.get(m.get("tier"), "")
    has_gmm = bool(m.get("action_steps"))
    deep_badge = " · 💎 GMM Chuyên sâu" if has_gmm else ""
    icon = PILLAR_ICONS.get(m.get("pillar", ""), "📌")

    expander_title = f"{icon} [{m.get('id', '')}] {m.get('name_vi', '')} — {m.get('name_en', '')} ({tier_badge}{deep_badge})"
    with st.expander(expander_title, expanded=is_expanded):
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

        if m.get("id") == "PHYS-11":
            st.success("⚡ **Gợi ý thực hành Tư duy Nguyên bản (First Principles):** Bóc tách về chân lý vật lý không thể tối giản hơn trước khi suy luận tiếp!")
        elif m.get("id") == "PSY-12":
            st.info("📓 **Gợi ý thực hành Vòng tròn Năng lực (Circle of Competence):** Luôn xác định ranh giới những gì bạn thực sự am hiểu và những gì chỉ là ảo tưởng!")

        # GMM Deep Framework: Action Steps, Boundary Conditions & Real-World Case Studies
        if m.get("action_steps") or m.get("boundary_conditions") or m.get("real_world_case"):
            st.divider()
            st.markdown("#### 💎 Khung Phân Tích Chuyên Sâu (The Great Mental Models Framework)")

            col_proto, col_bound = st.columns([3, 2])
            with col_proto:
                if m.get("action_steps"):
                    st.markdown(f"**🛠️ Quy trình thực thi {len(m['action_steps'])} bước (Action Protocol):**")
                    for step in m["action_steps"]:
                        st.markdown(f"- {step}")
            with col_bound:
                if m.get("boundary_conditions"):
                    st.markdown("**⛔ Ranh giới áp dụng (Khi nào KHÔNG dùng):**")
                    st.error(m["boundary_conditions"])

            if m.get("real_world_case"):
                st.markdown("**🌐 Tình huống thực chiến đa chiều (Case Studies Thực tế):**")
                st.markdown(m["real_world_case"])



# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
render_html("""
<div class="farrow-header">
    <div class="farrow-badge">⚡ DAVE FARROW 10-MINUTE MEMORY ENGINE</div>
    <h1 style="color: #f8fafc; margin: 4px 0 8px 0; font-weight: 800;">ELITE THINKING: FARROW EDITION</h1>
    <p style="color: #94a3b8; margin: 0; font-size: 1.05rem;">
        Loại bỏ 90% chữ rườm rà. Nén toàn bộ tri thức tinh hoa về đúng <b>Bộ 3 Hạt Nhân (Rule of 3)</b>, 
        ghim vào <b>Lâu Đài Ký Ức 3 Mỏ Neo</b> và chiếm lĩnh trong <b>10 Phút Nước Rút</b>.
    </p>
</div>
""")

# -----------------------------------------------------------------------------
# Sidebar Navigation & API Setup
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧭 ĐIỀU HƯỚNG FARROW")
    app_mode = st.radio(
        "Chọn phòng chức năng:",
        [
            "🏛️ Lâu Đài Ký Ức (The 3 Trinity)",
            "⏱️ Phòng Ép Xung 10 Phút (Focus Sprint)",
            "⚡ Máy Ép Farrow 1-Click (AI Compressor)",
            "🫁 Trạm Thở Bụng Sạc Pin"
        ],
        index=0
    )
    
    st.divider()
    st.markdown("#### 🔑 Kết Nối Trí Tuệ Nhân Tạo (Gemini AI)")
    
    custom_key = st.text_input(
        "Khóa API dự phòng (Tùy chọn ghi đè):",
        type="password",
        value="",
        help="Hệ thống đã tự động liên kết 8 API keys từ file .env. Chỉ nhập vào đây nếu bạn muốn sử dụng một key cá nhân khác."
    )
    active_api_key = custom_key.strip() if custom_key.strip() else None

    api_status = get_api_key_status()
    if active_api_key:
        st.info("🔑 Đang sử dụng Khóa API ghi đè thủ công.")
    elif api_status["has_keys"]:
        st.success(f"🟢 **Hệ thống AI sẵn sàng:**\n{api_status['active_hint']}")
    else:
        st.warning("⚠️ Chưa phát hiện API Key trong `.env` (Vui lòng nhập key ở trên để dùng AI).")

    st.caption("💡 *Quy chuẩn Dave Farrow: Não chỉ là cục pin nhỏ, đừng học dồn 2 tiếng. Hãy chạy nước rút 10 phút rồi thở bụng xả hơi.*")

# -----------------------------------------------------------------------------
# PHÒNG 1: LÂU ĐÀI KÝ ỨC (THE 3 TRINITY)
# -----------------------------------------------------------------------------
if app_mode == "🏛️ Lâu Đài Ký Ức (The 3 Trinity)":
    st.markdown("### 🏛️ Lâu Đài Ký Ức: Chọn Chủ Đề Nén Sẵn")
    st.caption("Toàn bộ 152 Mô hình & Nguyên lý đã được phân loại và nén sẵn theo Quy tắc số 3: Đúng 3 Khối hạt nhân gắn tại 3 mỏ neo phòng học của bạn.")

    all_topics = get_all_farrow_topics()
    categories = ["Tất cả danh mục"] + list(dict.fromkeys(t.get("category", "Khác") for t in all_topics))

    col_cat, col_top = st.columns([1, 2])
    with col_cat:
        selected_cat = st.selectbox("Lọc theo nhóm ngành:", categories)

    filtered_topics = all_topics
    if selected_cat != "Tất cả danh mục":
        filtered_topics = [t for t in all_topics if t.get("category") == selected_cat]

    topic_options = {t["id"]: f"{t['icon']} {t['title']}" for t in filtered_topics}
    
    with col_top:
        selected_id = st.selectbox(
            "Chọn chủ đề tinh hoa cần nạp vào não:",
            options=list(topic_options.keys()),
            format_func=lambda x: topic_options[x]
        )
    
    topic = get_farrow_topic_by_id(selected_id)
    
    col_tinfo1, col_tinfo2 = st.columns([1, 3])
    with col_tinfo1:
        st.markdown(f"**Danh mục:** `{topic.get('category', 'Khác')}`")
    with col_tinfo2:
        st.caption(f"📖 *{topic.get('summary', '')}*")
        
    st.info(f"🎯 **Khẩu quyết:** *\"{topic['tagline']}\"*")
    
    # Render 3 Columns
    c1, c2, c3 = st.columns(3)
    chunks = topic["chunks"]
    cols = [c1, c2, c3]
    for idx, (col, chunk) in enumerate(zip(cols, chunks)):
        with col:
            img_html = get_anchor_image_html(topic["id"], chunk["id"])
            card_html = f"""<div class="trinity-card">
<div class="anchor-badge">{chunk['anchor_icon']} MỎ NEO: {chunk['anchor_name']}</div>
{img_html}
<h3 style="color: #f8fafc; margin-top: 0; font-size: 1.25rem;">{chunk['label']}</h3>
<p style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; line-height: 1.4;">{chunk.get('sub_modes', '')}</p>
<div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; margin: 12px 0;">
<b>Nguyên lý gốc:</b><br>{chunk['principle']}
</div>
<div class="crazy-image-box">
🧠 <b>HÌNH ẢNH DỊ BIỆT GHIM NÃO:</b><br>
{chunk['crazy_image']}
</div>
<div class="trigger-box">
⚡ <b>CÂU HỎI KÍCH HOẠT 5 GIÂY:</b><br>
<i>"{chunk['trigger_question']}"</i>
</div>
</div>"""
            render_html(card_html)



    st.markdown("---")
    st.markdown("### ⚡ Đấu Trường Phản Xạ 5 Giây (Feynman Challenge)")
    for q_idx, q in enumerate(topic.get("quiz", [])):
        with st.expander(f"🎯 Thử thách #{q_idx+1}: {q['question']}", expanded=True):
            user_ans = st.radio(
                "Phương án phản xạ của bạn:",
                q["options"],
                key=f"quiz_{selected_id}_{q_idx}",
                index=None
            )
            if user_ans is not None:
                chosen_idx = q["options"].index(user_ans)
                if chosen_idx == q["correct_idx"]:
                    st.success(f"🎉 **CHÍNH XÁC!** {q['explanation']}")
                else:
                    st.error("❌ **CHƯA ĐÚNG!** Hãy nhớ lại 3 mỏ neo trong lâu đài ký ức để phản xạ lại.")

    # Expander bóc tách chi tiết 9 mô hình gốc của chủ đề hiện tại
    st.markdown("---")
    with st.expander(f"📚 Bóc Tách Chi Tiết Mô Hình & Nguyên Lý Gốc Của Chủ Đề: {topic['title']} (9 Mô Hình Tinh Hoa)", expanded=True):
        st.markdown(f"Trực tiếp bóc tách 9 mô hình cấu thành nên 3 Trụ Cột của **{topic['title']}** theo chuẩn Charlie Munger & The Great Mental Models Framework:")
        
        tab_t1, tab_t2, tab_t3 = st.tabs([
            f"🚪 {chunks[0]['label']}",
            f"🖥️ {chunks[1]['label']}",
            f"🪑 {chunks[2]['label']}"
        ])
        
        for tab_obj, chunk in zip([tab_t1, tab_t2, tab_t3], chunks):
            with tab_obj:
                st.caption(f"📍 **Mỏ neo không gian:** {chunk['anchor_icon']} {chunk['anchor_name']}  |  ⚙️ **Cơ chế nén:** `{chunk.get('sub_modes', '')}`")
                models_in_chunk = get_models_for_topic_chunk(chunk)
                for m_idx, m in enumerate(models_in_chunk):
                    # Mở rộng thẻ đầu tiên mặc định trong mỗi Trụ
                    render_gmm_detailed_model(m, is_expanded=(m_idx == 0))

        # Tùy chọn mở rộng: tra cứu thêm trong toàn bộ 152 mô hình nếu cần
        st.markdown("---")
        with st.expander("🔍 Mở rộng: Tra cứu tìm kiếm trong toàn bộ 152 Mô hình & Nguyên lý gốc khác", expanded=False):
            all_items = load_unified_farrow_catalog()
            metrics = get_farrow_metrics()
            st.caption(f"Tổng hợp {metrics['total']} mô hình & nguyên lý sạch (gồm {metrics['tier1_count']} siêu hạt nhân Tier 1).")
            
            c_f1, c_f2 = st.columns([1, 2])
            with c_f1:
                t_filter = st.selectbox("Lọc cấp độ:", ["Tất cả", "⭐ Tier 1 (Pareto)", "Cấp 2 & 3"], key="exp_tier")
            with c_f2:
                s_kw = st.text_input("Tìm kiếm:", placeholder="Nhập tên mô hình hoặc nguyên lý...", key="exp_search")
                
            display_items = all_items
            if t_filter == "⭐ Tier 1 (Pareto)":
                display_items = [x for x in display_items if x.get("tier") == 1]
            elif t_filter == "Cấp 2 & 3":
                display_items = [x for x in display_items if x.get("tier") in [2, 3]]
                
            if s_kw.strip():
                kw_low = s_kw.strip().lower()
                display_items = [x for x in display_items if kw_low in str(x.get("name_vi", "")).lower() or kw_low in str(x.get("name_en", "")).lower() or kw_low in str(x.get("first_principle", "")).lower()]
                
            st.caption(f"Tìm thấy {len(display_items)} kết quả:")
            for sub_item in display_items[:10]:
                render_gmm_detailed_model(sub_item, is_expanded=False)

    if topic.get("category") == "🌐 Thế Cuộc & Giới Elite":
        st.markdown("---")
        st.markdown("### 🌐 Lăng Kính Thế Cuộc & Quy Luật Vận Hành Ngầm Của Giới Elite (Bản Bổ Trợ Chuyên Sâu)")
        st.caption("Bóc tách toàn cảnh dòng chảy chuyển dịch các thời đại kinh tế và giải mã 8 mật mã chiến lược của tầng lớp tinh hoa dưới lăng kính First Principles.")
        
        m_tab1, m_tab2, m_tab3 = st.tabs([
            "⏳ Trục Tiến Hóa 5 Kỷ Nguyên",
            "👁️ 8 Mật Mã Vận Hành Ngầm Elite",
            "📡 Máy Quét Đọc Vị Thế Cuộc (AI Radar)"
        ])
        
        with m_tab1:
            st.markdown("""
            #### 🧬 Bản Chất Chuyển Dịch Kinh Tế Qua Các Thời Đại
            Bản chất của mọi nền kinh tế đều xoay quanh: **Phân bổ nguồn lực khan hiếm để tối đa hóa sự sinh tồn và phát triển.**
            """)
            st.info("""
            💥 **Định luật Chuyển Pha Kinh Tế (The Phase-Transition Law):**  
            Khi một rào cản về **Năng lượng** hoặc **Công nghệ** bị phá vỡ ➔ **Nguồn lực cốt lõi cũ bị bình dân hóa (tiến về giá trị 0đ)** ➔ **Một nguồn lực mới lên ngôi** ➔ Dẫn đến sự tổ chức lại toàn bộ cấu trúc quyền lực, nhà nước và xã hội.
            """)
            
            era_titles = [f"{e['icon']} {e['name']}" for e in CIVILIZATIONAL_ERAS]
            selected_era_idx = st.radio(
                "Chọn thời đại để mổ xẻ cấu trúc kinh tế:",
                range(len(CIVILIZATIONAL_ERAS)),
                format_func=lambda i: era_titles[i],
                horizontal=True,
                key="vault_macro_era_selector"
            )
            era_data = CIVILIZATIONAL_ERAS[selected_era_idx]
            st.markdown(f"##### {era_data['icon']} {era_data['name']} — *{era_data['subtitle']}*")
            st.caption(f"⏱️ Khung thời gian: **{era_data['timeframe']}**")
            
            c_e1, c_e2 = st.columns(2)
            with c_e1:
                st.markdown(f"**📌 Nguồn Lực Cốt Lõi:**  \n{era_data['core_resource']}")
                st.markdown(f"**⚡ Năng Lượng & Công Nghệ:**  \n{era_data['energy_tech']}")
                st.markdown(f"**🛑 Giới Hạn / Điểm Nghẽn (Constraint):**  \n{era_data['constraint']}")
                st.markdown(f"**💼 Mô Hình Kinh Tế:**  \n{era_data['economic_model']}")
            with c_e2:
                st.error(f"**📉 Bị Bình Dân Hóa (Rớt Giá Về 0đ):**  \n{era_data['commoditized']}")
                st.success(f"**💎 Nút Thắt Khan Hiếm Mới Lên Ngôi:**  \n{era_data['new_scarce_asset']}")
                st.markdown(f"**🚀 Đòn Bẩy Của Giới Tinh Hoa:**  \n{era_data['elite_leverage']}")
                st.warning(f"**💥 Tại Sao Chuyển Giao? (Turning Point):**  \n{era_data['turning_point']}")
            
            with st.expander("🔬 Phân tích bản chất sâu sắc & Bài học lịch sử", expanded=False):
                st.markdown(era_data['deep_dive'])

        with m_tab2:
            st.markdown("#### 👁️ Bộ Mật Mã 8 Quy Tắc Vận Hành Ngầm Của Giới Tinh Hoa (The Elite Playbook)")
            st.caption("Các định luật toán học, vật lý và kinh tế hành vi được giới tinh hoa thấu hiểu và áp dụng triệt để:")
            search_law = st.text_input("🔍 Tìm kiếm quy tắc ngầm:", "", placeholder="Ví dụ: Cantillon, Bất đối xứng, Khan hiếm, Coase, Đòn bẩy...", key="vault_law_search")
            for law in ELITE_HIDDEN_LAWS:
                if search_law.strip():
                    match = (
                        search_law.lower() in law["title"].lower()
                        or search_law.lower() in law["axiom"].lower()
                        or any(search_law.lower() in m.lower() for m in law.get("linked_models", []))
                    )
                    if not match:
                        continue
                with st.expander(f"{law['icon']} #{law['number']}. {law['title']}", expanded=False):
                    st.markdown(f"> *\"{law['axiom']}\"*")
                    c_l1, c_l2 = st.columns(2)
                    with c_l1:
                        st.error(f"👥 **Góc Nhìn Đám Đông (Bẫy Nhận Thức):**  \n{law['mass_perception']}")
                        st.success(f"👁️ **Hành Động Của Giới Elite:**  \n{law['elite_execution']}")
                    with c_l2:
                        st.info(f"🔬 **Cơ Sở Toán Học / Vật Lý / Kinh Tế:**  \n{law['physics_math_basis']}")
                        st.warning(f"💡 **Ví Dụ Thực Chiến & Lịch Sử:**  \n{law['real_world_case']}")
                    st.caption(f"🎯 **Câu hỏi tự vấn:** *{law['self_inquiry']}*")

        with m_tab3:
            st.markdown("#### 📡 Máy Quét Đọc Vị Thế Cuộc Bằng AI (First-Principles Macro Radar)")
            st.caption("Bóc tách bất kỳ biến động vĩ mô hoặc công nghệ mới nào: Thứ gì sắp rớt giá về 0? Nút thắt khan hiếm mới ở đâu? Giới tinh hoa sẽ đi nước cờ gì?")
            
            st.markdown("##### 💡 Bấm chọn xu hướng mẫu kinh điển để nạp nhanh:")
            s_cols = st.columns(len(SAMPLE_MACRO_TRENDS))
            for s_idx, sample in enumerate(SAMPLE_MACRO_TRENDS):
                with s_cols[s_idx]:
                    sample_short_title = sample["title"].split()[0] + " " + " ".join(sample["title"].split()[1:3])
                    if st.button(sample_short_title, key=f"vault_macro_sample_{s_idx}", help=sample["title"]):
                        st.session_state["vault_macro_radar_input"] = sample["query"]
                        st.rerun()

            default_q = st.session_state.get(
                "vault_macro_radar_input",
                "Sự xuất hiện của các AI Agents tự hành có khả năng lập trình, viết báo cáo, xử lý dữ liệu và vận hành quy trình kinh doanh 24/7 với chi phí tiệm cận 0."
            )
            trend_text = st.text_area(
                "Nhập mô tả biến động vĩ mô, công nghệ hoặc sự kiện cần bóc tách:",
                value=default_q,
                height=110,
                key="vault_macro_trend_text_area"
            )
            if st.button("📡 Quét Đọc Vị Theo First Principles", type="primary", use_container_width=True, key="vault_btn_radar"):
                with st.spinner("🤖 Đang kích hoạt Bộ máy Phân tích Thế cuộc & First Principles Engine..."):
                    res_radar = analyze_macro_radar(trend_text.strip(), api_key=active_api_key)
                if not res_radar:
                    st.error("Không nhận được phản hồi từ AI Engine.")
                elif "error" in res_radar and not res_radar.get("trend_summary"):
                    st.error(f"Lỗi: {res_radar['error']}")
                else:
                    # Tự động lưu bản quét vào Supabase Cloud & Local Storage
                    saved_ok = save_macro_scan(trend_text.strip(), res_radar)
                    if saved_ok:
                        st.toast("☁️ Đã lưu bản quét vào Supabase Cloud!", icon="💾")
                    st.success("✅ Đã hoàn tất bóc tách thế cuộc & Đã lưu vào Kho Lịch sử!")
                    st.markdown(f"#### 🎯 Bản Chất Cốt Lõi: {res_radar.get('trend_summary', '')}")
                    st.info(f"⚡ **Chi Phí Giao Dịch Bị Kéo Tụt:** {res_radar.get('transaction_costs_impact', '')}")
                    c_r1, c_r2 = st.columns(2)
                    with c_r1:
                        st.error("#### 📉 Nguồn Lực Bị Trượt Giá Về 0")
                        for item in res_radar.get("commoditized_assets", []):
                            st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")
                    with c_r2:
                        st.success("#### 💎 Nút Thắt Khan Hiếm Mới")
                        for item in res_radar.get("complementary_scarcities", []):
                            st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")
                    st.markdown("#### 👁️ Nước Cờ Chiến Lược Của Giới Elite")
                    for move in res_radar.get("elite_strategic_moves", []):
                        st.markdown(f"- ♟️ {move}")
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        st.markdown("#### 🕸️ Mô Hình Hạt Nhân Kích Hoạt")
                        for m_item in res_radar.get("activated_mental_models", []):
                            st.markdown(f"- `{m_item.get('model_name', '')}`: {m_item.get('mechanism', '')}")
                    with c_b2:
                        st.markdown("#### 🧭 Playbook Hành Động")
                        for act in res_radar.get("action_playbook_for_individual", []):
                            st.markdown(f"- 🚀 {act}")

            # -------------------------------------------------------------
            # KHO LƯU TRỮ CÁC LẦN QUÉT THẾ CUỘC (LỊCH SỬ PHÂN TÍCH BỀN VỮNG)
            # -------------------------------------------------------------
            st.divider()
            saved_scans = load_macro_scans()
            sb_client = get_supabase_client()
            sync_badge = "☁️ Supabase Cloud (Đồng bộ vĩnh viễn)" if sb_client is not None else "💾 Cục bộ (Local JSON)"

            st.markdown(f"### 📚 Kho Lưu Trữ Lịch Sử Quét Thế Cuộc ({len(saved_scans)} bản ghi)")
            st.caption(f"Trạng thái đồng bộ: **{sync_badge}**. Bất kỳ biến động vĩ mô nào bạn quét đều được lưu giữ để đọc lại mọi lúc mọi nơi trên điện thoại hoặc máy tính.")

            if saved_scans:
                s_search = st.text_input(
                    "🔍 Tìm kiếm trong kho lưu trữ:",
                    placeholder="Nhập từ khóa (vd: chip não, robot, năng lượng, ai agents...)",
                    key="vault_history_search"
                )
                filtered_scans = saved_scans
                if s_search.strip():
                    kw = s_search.strip().lower()
                    filtered_scans = [
                        s for s in saved_scans
                        if kw in s.get("query", "").lower() or kw in str(s.get("result", {})).lower()
                    ]

                if not filtered_scans:
                    st.info("Không tìm thấy bản ghi nào khớp với từ khóa.")

                for idx, sc in enumerate(filtered_scans):
                    sc_id = sc.get("id", f"scan_{idx}")
                    sc_time = sc.get("created_at", "Gần đây")
                    sc_query = sc.get("query", "Không có tiêu đề")
                    sc_res = sc.get("result", {})

                    short_title = sc_query[:75] + ("..." if len(sc_query) > 75 else "")
                    with st.expander(f"📑 [{sc_time}] {short_title}", expanded=(idx == 0 and len(filtered_scans) == 1)):
                        col_h_left, col_h_right = st.columns([4, 1])
                        with col_h_left:
                            st.markdown(f"**🎯 Xu hướng / Biến động đã quét:**  \n*{sc_query}*")
                        with col_h_right:
                            if st.button("🗑️ Xóa", key=f"btn_del_scan_{sc_id}", help="Xóa bản ghi này khỏi lịch sử"):
                                delete_macro_scan(sc_id)
                                st.success("Đã xóa bản ghi!")
                                st.rerun()

                        st.markdown(f"**🎯 Bản Chất Cốt Lõi:** {sc_res.get('trend_summary', '')}")
                        st.info(f"⚡ **Chi Phí Giao Dịch Bị Kéo Tụt:** {sc_res.get('transaction_costs_impact', '')}")

                        c_s1, c_s2 = st.columns(2)
                        with c_s1:
                            st.error("📉 **Nguồn Lực Bị Trượt Giá Về 0:**")
                            for item in sc_res.get("commoditized_assets", []):
                                st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")
                        with c_s2:
                            st.success("💎 **Nút Thắt Khan Hiếm Mới:**")
                            for item in sc_res.get("complementary_scarcities", []):
                                st.markdown(f"- **{item.get('asset', '')}**: {item.get('why', '')}")

                        st.markdown("👁️ **Nước Cờ Chiến Lược Của Giới Elite:**")
                        for move in sc_res.get("elite_strategic_moves", []):
                            st.markdown(f"- ♟️ {move}")

                        c_sb1, c_sb2 = st.columns(2)
                        with c_sb1:
                            st.markdown("🕸️ **Mô Hình Hạt Nhân Kích Hoạt:**")
                            for m_item in sc_res.get("activated_mental_models", []):
                                st.markdown(f"- `{m_item.get('model_name', '')}`: {m_item.get('mechanism', '')}")
                        with c_sb2:
                            st.markdown("🧭 **Playbook Hành Động:**")
                            for act in sc_res.get("action_playbook_for_individual", []):
                                st.markdown(f"- 🚀 {act}")
            else:
                st.info("💡 Chưa có bản quét nào được lưu. Hãy nhập một xu hướng ở trên và bấm **'📡 Quét Đọc Vị Theo First Principles'**, kết quả sẽ tự động lưu vĩnh viễn vào đây để bạn đọc lại bất cứ lúc nào!")


elif app_mode == "⏱️ Phòng Ép Xung 10 Phút (Focus Sprint)":
    st.markdown("### ⏱️ Phòng Ép Xung 10 Phút (The 10-Minute Focus Sprint)")
    st.caption("Chạy nước rút tập trung cao độ trong 10 phút. Chọn một chủ đề Lâu Đài Ký Ức hoặc Rút 3 Thẻ Bài Farrow Tarot để thử thách não bộ!")

    sprint_type = st.radio(
        "Chọn chế độ Sprint:",
        ["📖 Chọn Chủ Đề Lâu Đài Ký Ức", "🎲 Rút 3 Thẻ Ngẫu Nhiên (Bộ 3 Farrow Tarot)"],
        horizontal=True
    )

    if sprint_type == "📖 Chọn Chủ Đề Lâu Đài Ký Ức":
        topics = get_all_farrow_topics()
        sprint_topic_id = st.selectbox(
            "Chọn chủ đề để chạy nước rút 10 phút:",
            options=[t["id"] for t in topics],
            format_func=lambda x: [f"{t['icon']} {t['title']} [{t.get('category', '')}]" for t in topics if t["id"] == x][0]
        )
        s_topic = get_farrow_topic_by_id(sprint_topic_id)
        st.info(f"🎯 **Khẩu quyết 10 phút:** *\"{s_topic['tagline']}\"*")
        
        # Render 3 Trinity cards for the sprint topic
        c_s1, c_s2, c_s3 = st.columns(3)
        cols_s = [c_s1, c_s2, c_s3]
        for col_s, chunk in zip(cols_s, s_topic["chunks"]):
            with col_s:
                card_html = f"""
                <div class="trinity-card">
                    <div class="anchor-badge">{chunk['anchor_icon']} {chunk['anchor_name']}</div>
                    <h3 style="color: #f8fafc; font-size: 1.15rem; margin-top: 4px;">{chunk['label']}</h3>
                    <div style="color: #38bdf8; font-size: 0.82rem; font-weight: 600; margin-bottom: 6px;">{chunk.get('sub_modes', '')}</div>
                    <div class="model-rule">💡 <b>Quy luật:</b><br>{chunk['principle']}</div>
                    <div class="crazy-image-box">
                        🧠 <b>ẢNH DỊ BIỆT:</b><br>{chunk['crazy_image']}
                    </div>
                    <div class="trigger-box">
                        ⚡ <b>KÍCH HOẠT 5S:</b><br><i>"{chunk['trigger_question']}"</i>
                    </div>
                </div>
                """
                render_html(card_html)
    else:
        if "random_trio" not in st.session_state or st.button("🔀 Rút Lại 3 Thẻ Tinh Hoa Mới", type="secondary"):
            st.session_state.random_trio = draw_random_farrow_sprint_trio()
        
        trio = st.session_state.random_trio
        st.info("🎯 **Thử thách 10 phút của bạn:** Hãy ghi nhớ và kết nối 3 mô hình này vào 3 mỏ neo trong phòng học của bạn!")
        
        c_r1, c_r2, c_r3 = st.columns(3)
        cols_t = [c_r1, c_r2, c_r3]
        anchors = [("🚪 CỬA RA VÀO", "Soi Gốc"), ("🖥️ MÀN HÌNH", "Đọc Dòng"), ("🪑 BÀN GHẾ", "Ra Đòn")]
        for idx, (col_item, m, (anc_name, anc_desc)) in enumerate(zip(cols_t, trio, anchors)):
            with col_item:
                card_html = f"""
                <div class="trinity-card">
                    <div class="anchor-badge">{anc_name} ({anc_desc})</div>
                    <h3 style="color: #f8fafc; font-size: 1.15rem; margin-top: 4px;">{m.get('name_vi', '')}</h3>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">{m.get('pillar', '')}</div>
                    <div class="model-rule">💡 <b>Quy luật:</b> {m.get('first_principle', '')}</div>
                    <div class="trigger-box">
                        ⚡ <b>KÍCH HOẠT 5S:</b><br>
                        <i>"{m.get('trigger_question', '')}"</i>
                    </div>
                </div>
                """
                render_html(card_html)

    st.markdown("---")

    # Sprint Interactive Controller
    if "sprint_running" not in st.session_state:
        st.session_state.sprint_running = False
    if "sprint_seconds" not in st.session_state:
        st.session_state.sprint_seconds = 600

    col_timer, col_ctrl = st.columns([2, 1])
    with col_timer:
        mins = st.session_state.sprint_seconds // 60
        secs = st.session_state.sprint_seconds % 60
        phase_label = (
            "CHẶNG 1: BÓC TÁCH VÀ NÉN (00-02m)" if mins >= 8 else
            "CHẶNG 2: GẮN VÀO LÂU ĐÀI KÝ ỨC (02-05m)" if mins >= 5 else
            "CHẶNG 3: ÉP XUNG QUÉT TỐC ĐỘ X3 (05-08m)" if mins >= 2 else
            "CHẶNG 4: PHẢN XẠ VÀ THỞ BỤNG SẠC PIN (08-10m)"
        )
        timer_html = f"""
        <div class="timer-container">
            <div style="color: #94a3b8; font-weight: 600; text-transform: uppercase;">ĐỒNG HỒ ĐẾM NGƯỢC NƯỚC RÚT</div>
            <div class="timer-digits">{mins:02d}:{secs:02d}</div>
            <div style="color: #38bdf8; font-weight: 600; margin-top: 8px;">{phase_label}</div>
        </div>
        """
        render_html(timer_html)

    with col_ctrl:
        st.write("")
        st.write("")
        if st.button("▶️ BẮT ĐẦU SPRINT 10 PHÚT", use_container_width=True, type="primary"):
            st.session_state.sprint_running = True
            st.success("🔥 Đồng hồ đã kích hoạt! Hãy tập trung 100% vào 3 khối hạt nhân phía trên.")
        if st.button("🔄 ĐẶT LẠI 10 PHÚT (RESET)", use_container_width=True):
            st.session_state.sprint_seconds = 600
            st.session_state.sprint_running = False
            st.rerun()

# -----------------------------------------------------------------------------
# PHÒNG 3: MÁY ÉP FARROW 1-CLICK (AI COMPRESSOR)
# -----------------------------------------------------------------------------
elif app_mode == "⚡ Máy Ép Farrow 1-Click (AI Compressor)":
    st.markdown("### ⚡ Máy Ép Farrow 1-Click (Universal AI Compressor)")
    st.caption("Dán bất kỳ tài liệu dài, bài luận, case study hoặc báo cáo nào vào đây. AI sẽ tự động ép nát về đúng 3 khối hạt nhân.")

    user_raw_text = st.text_area(
        "Dán văn bản thô vào đây (tối đa 8.000 ký tự):",
        placeholder="Ví dụ: Dán một bài phân tích dài về kinh tế vĩ mô, một chiến lược kinh doanh 10 trang, hoặc một bài giảng khó hiểu của trường học...",
        height=200
    )

    if st.button("💥 ÉP NÉN THEO CHUẨN DAVE FARROW (RULE OF 3)", type="primary"):
        if not user_raw_text.strip():
            st.warning("Vui lòng dán nội dung văn bản cần nén!")
        else:
            with st.spinner("🤖 Đang nghiền nát câu chữ rườm rà, bóc tách 3 hạt nhân và tạo hình ảnh kỳ quặc..."):
                result = compress_with_farrow_ai(user_raw_text, api_key=active_api_key)
                st.session_state.compress_result = result
                st.success("🎉 Nén thành công! Dưới đây là bộ 3 hạt nhân đã được giải mã:")

    if "compress_result" in st.session_state:
        res = st.session_state.compress_result
        st.markdown(f"### 📦 Kết quả: {res.get('title', 'Bản Nén Farrow')}")
        st.info(f"🎯 **Khẩu quyết cốt lõi:** *\"{res.get('tagline', '')}\"*")

        c1, c2, c3 = st.columns(3)
        cols = [c1, c2, c3]
        chunks = res.get("chunks", [])

        icons = ["🚪", "🖥️", "🪑"]
        for idx, (col, chunk) in enumerate(zip(cols, chunks)):
            with col:
                card_html = f"""
                <div class="trinity-card">
                    <div class="anchor-badge">{icons[idx]} MỎ NEO: {chunk.get('anchor', '')}</div>
                    <h3 style="color: #f8fafc; font-size: 1.2rem;">{chunk.get('label', '')}</h3>
                    <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; margin: 12px 0;">
                        <b>Nguyên lý gốc:</b><br>{chunk.get('principle', '')}
                    </div>
                    <div class="crazy-image-box">
                        🧠 <b>HÌNH ẢNH DỊ BIỆT:</b><br>
                        {chunk.get('crazy_image', '')}
                    </div>
                    <div class="trigger-box">
                        ⚡ <b>PHẢN XẠ 5S:</b><br>
                        <i>"{chunk.get('trigger_question', '')}"</i>
                    </div>
                </div>
                """
                render_html(card_html)

        st.success(f"🎯 **Đòn bẩy Bất đối xứng (Actionable Strike):** {res.get('asymmetric_action', '')}")

# -----------------------------------------------------------------------------
# PHÒNG 4: TRẠM THỞ BỤNG SẠC PIN
# -----------------------------------------------------------------------------
elif app_mode == "🫁 Trạm Thở Bụng Sạc Pin":
    st.markdown("### 🫁 Trạm Thở Bụng Sạc Pin (Dave Farrow Belly Breathing)")
    st.markdown("""
    Dave Farrow nhấn mạnh: **Học xong mà không thở là tự sát trí nhớ**.
    Khi bạn ép xung học nhanh, hạch hạnh nhân (amygdala) bị kích thích và sản sinh cortisol (hormone căng thẳng) làm tắc nghẽn khả năng truy xuất của hồi hải mã.
    Hít thở sâu bằng bụng giúp đưa nhịp tim về trạng thái thư giãn (sóng não Alpha) và đưa oxy tối đa lên não để hồi hải mã "đóng đinh" ký ức dài hạn.
    """)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.info("1️⃣ **HÍT VÀO** (4 Giây)<br>Phình căng bụng lên", icon="🌬️")
    with b2:
        st.warning("2️⃣ **GIỮ KHÍ** (4 Giây)<br>Khóa chặt không khí trong bụng", icon="🛑")
    with b3:
        st.success("3️⃣ **THỞ RA** (4 Giây)<br>Xẹp sát bụng lại tống hết khí độc", icon="😮‍💨")
    with b4:
        st.info("4️⃣ **NGHỈ NGƠI** (4 Giây)<br>Thả lỏng toàn bộ cơ thể", icon="🧘")

    st.markdown("---")
    st.markdown("#### ⏱️ Đồng Hồ Dẫn Nhịp Thở 4 Nhịp (Box Breathing)")
    
    if st.button("▶️ BẮT ĐẦU 1 PHÚT THỞ BỤNG PHỤC HỒI", type="primary"):
        cycle_placeholder = st.empty()
        for cycle in range(3):
            cycle_placeholder.markdown(f"### 🌊 Vòng Thở #{cycle+1}/3: **HÍT VÀO...** (Phình bụng)", unsafe_allow_html=True)
            time.sleep(4)
            cycle_placeholder.markdown(f"### 🛑 Vòng Thở #{cycle+1}/3: **GIỮ KHÍ...** (Khóa chặt)", unsafe_allow_html=True)
            time.sleep(4)
            cycle_placeholder.markdown(f"### 😮‍💨 Vòng Thở #{cycle+1}/3: **THỞ RA CHẬM...** (Xẹp bụng)", unsafe_allow_html=True)
            time.sleep(4)
            cycle_placeholder.markdown(f"### 🧘 Vòng Thở #{cycle+1}/3: **THẢ LỎNG...** (Tĩnh lặng)", unsafe_allow_html=True)
            time.sleep(4)
        cycle_placeholder.success("🎉 **CHÚC MỪNG!** Pin não của bạn đã được sạc đầy 100%. Bạn đã sẵn sàng cho thử thách tiếp theo!")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("⚡ **Elite Farrow Engine v2.2** — Hệ thống tư duy tinh hoa nén tối giản dành cho con người hiện đại.")
