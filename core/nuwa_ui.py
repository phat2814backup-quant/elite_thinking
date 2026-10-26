# -*- coding: utf-8 -*-
"""
Module Giao Diện Xưởng Chưng Cất Nhận Thức Nữ Oa (Nuwa Cognitive Forge UI)
Tích hợp:
1. 🎯 Bàn Hội Chẩn Vấn Đề (Problem Diagnostic & Council of Thinkers)
2. 🏛️ Bảo Tàng Hồ Sơ Đã Chưng Cất (14+ Profiles Catalog)
3. 🧪 Xưởng Đúc Chưng Cất Mới (Distill Anyone & Lưu Cơ Sở Dữ Liệu)
"""

from __future__ import annotations

import streamlit as st
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.nuwa_engine import (
    get_all_distilled_profiles,
    get_profile_by_id,
    save_new_distilled_profile,
    remove_distilled_profile,
    diagnose_and_match_thinkers,
    consult_thinkers_council,
    distill_new_thinker_ai
)
from core.db_storage import create_decision_entry
from core.export_utils import sanitize_filename

SAMPLE_PROBLEMS = [
    {
        "label": "🚀 Startup: Nên làm tính năng khách đòi hay bám sát tầm nhìn?",
        "query": "Tôi đang xây dựng một sản phẩm SaaS B2B. Hiện có 2 khách hàng doanh nghiệp lớn hứa trả tiền ngay nếu chúng tôi code thêm tính năng tùy biến riêng cho họ, nhưng tính năng này sẽ làm phân tán nguồn lực và không thể scale cho thị trường đại chúng. Tôi nên nhận tiền trước để sống sót hay từ chối để giữ sản phẩm tinh gọn?"
    },
    {
        "label": "🎬 Nội dung: Kênh YouTube / TikTok view lẹt đẹt, bí ý tưởng",
        "query": "Tôi làm nội dung kiến thức chuyên sâu trên mạng xã hội hơn 6 tháng nhưng lượng người xem vẫn lẹt đẹt dưới 1.000 view. Video làm rất kỹ nhưng người ta chỉ xem 15 giây là thoát. Làm sao thiết kế lại cấu trúc hook, nhịp điệu và tiêu đề để thu hút sự chú ý cực đoan mà không bị rẻ tiền?"
    },
    {
        "label": "🤝 Đàm phán: Đối tác lớn ép giảm 30% giá để ký hợp đồng",
        "query": "Công ty chúng tôi sắp ký hợp đồng cung cấp giải pháp với một tập đoàn lớn. Vào phút chót, bên mua yêu cầu giảm giá 30% và thanh toán chậm 90 ngày với lý do ngân sách hạn hẹp, nếu không sẽ chuyển sang đối thủ. Làm sao tạo đòn bẩy và thương thuyết áp đảo trong thế yếu?"
    },
    {
        "label": "📈 Đầu tư: Thị trường biến động dữ dội, tâm lý hoang mang",
        "query": "Thị trường tài chính biến động mạnh với các rủi ro địa chính trị và lạm phát. Danh mục đầu tư đang sụt giảm 18%. Tôi nên cơ cấu lại danh mục thế nào để vừa chống chịu được cú sốc Thiên Nga Đen, vừa có tiềm năng bứt phá khi hồi phục?"
    },
    {
        "label": "🤖 Kỹ thuật AI: Nên tự train fine-tune hay dùng Agentic Workflow?",
        "query": "Dự án công nghệ của nhóm đang tranh cãi giữa việc chi tiền thuê GPU để fine-tune một mô hình mã nguồn mở riêng, hay tận dụng các API mạnh nhất hiện nay kết hợp với kiến trúc Agent đa tầng và Prompt Engineering. Quyết định kỹ thuật nào mang lại ROI và độ bền vững cao hơn?"
    },
    {
        "label": "🎓 Nghề nghiệp: Chọn ngành an toàn hay theo đuổi đam mê mạo hiểm?",
        "query": "Tôi đang đứng trước ngã ba đường sự nghiệp: Tiếp tục gắn bó với một công việc văn phòng ổn định lương 25 triệu/tháng có tính lặp lại, hay mạo hiểm chuyển hẳn sang một lĩnh vực mới nổi chưa có lộ trình rõ ràng nhưng có tiềm năng tăng trưởng vượt trội? Làm sao bóc trần ảo tưởng và ra quyết định?"
    }
]


def render_html_safe(html_content: str):
    """Render HTML an toàn, ưu tiên st.html nếu có."""
    if hasattr(st, "html"):
        st.html(html_content)
    else:
        stripped = "\n".join(line.lstrip() for line in html_content.strip().splitlines())
        st.markdown(stripped, unsafe_allow_html=True)


def export_council_advice_to_markdown(problem: str, advice_data: Dict[str, Any]) -> str:
    """Tạo báo cáo Markdown chuẩn mực về phiên hội chẩn."""
    lines = [
        "# BÁO CÁO HỘI CHẨN NHẬN THỨC NỮ OA (COUNCIL OF THINKERS)",
        f"> *Thời gian lập:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. NAN ĐỀ ĐƯỢC MỔ XẺ",
        f"```text\n{problem}\n```",
        "",
        "## 2. BÓC TÁCH TỪ CÁC BỘ ÓC CỐ VẤN TINH HOA",
        ""
    ]
    
    for t in advice_data.get("thinkers_advice", []):
        lines.extend([
            f"### 👤 {t.get('name', 'Nhà tư tưởng')}",
            f"- 🔍 **Lăng kính áp dụng:** {t.get('applied_mental_model', '')}",
            f"- ⚡ **Quy tắc quyết định:** `{t.get('applied_heuristic', '')}`",
            f"- ⚠️ **Cảnh báo vùng cấm & Ngụy biện:** {t.get('trap_warning', '')}",
            f"- 💥 **Phản biện sắc bén:** *\"{t.get('brutal_critique', '')}\"*",
            f"- 🎯 **Hành động đề xuất:** {t.get('action_step', '')}",
            ""
        ])
        
    syn = advice_data.get("lollapalooza_synthesis", {})
    if syn:
        lines.extend([
            "---",
            "## 3. CỘNG HƯỞNG LOLLAPALOOZA (ĐỒNG THUẬN TỐI THƯỢNG)",
            f"- 🌐 **Điểm giao thoa:** {syn.get('convergence_point', '')}",
            f"- 🚀 **Nước đi bất đối xứng trong 24h:** **{syn.get('asymmetric_action_24h', '')}**",
            f"- 🛡️ **Nguyên lý dài hạn:** *{syn.get('long_term_rule', '')}*",
            ""
        ])
        
    lines.append("\n---\n*Được tạo bởi Elite Thinking — Nuwa Cognitive Forge.*")
    return "\n".join(lines)


def render_nuwa_forge_room(active_api_key: Optional[str] = None):
    """Hiển thị toàn bộ phòng chức năng Xưởng Chưng Cất Nhận Thức Nữ Oa."""
    
    # Nạp toàn bộ danh sách hồ sơ từ storage
    all_profiles = get_all_distilled_profiles()
    builtin_count = len([p for p in all_profiles if p.get("is_builtin", False)])
    custom_count = len(all_profiles) - builtin_count

    # Header phong cách Elite
    render_html_safe(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); 
                border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 12px; padding: 20px 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; font-size: 0.8rem; font-weight: 700; 
                             padding: 4px 10px; border-radius: 999px; letter-spacing: 0.05em; border: 1px solid rgba(99, 102, 241, 0.4);">
                    🧬 NUWA COGNITIVE FORGE (CHƯNG CẤT HỆ ĐIỀU HÀNH NHẬN THỨC)
                </span>
                <h2 style="color: #f8fafc; margin: 8px 0 4px 0; font-size: 1.7rem; font-weight: 800;">
                    XƯỞNG CHƯNG CẤT TƯ DUY & BÀN CỐ VẤN TINH HOA
                </h2>
                <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">
                    <i>「Người tiếp theo bạn muốn chưng cất, việc gì phải là đồng nghiệp.」</i> — Chiết xuất <b>5 tầng nhận thức</b> (Mental Models, Heuristics, DNA Biểu đạt, Vùng cấm, Ranh giới trung thực).
                </p>
            </div>
            <div style="text-align: right; background: rgba(15, 23, 42, 0.8); padding: 10px 16px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.3);">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">KHO HỒ SƠ ĐÃ CHƯNG CẤT</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #38bdf8;">
                    {len(all_profiles)} <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 400;">({builtin_count} Gốc + {custom_count} Mở rộng)</span>
                </div>
            </div>
        </div>
    </div>
    """)

    # 3 Tab chức năng chính
    t1, t2, t3 = st.tabs([
        "🎯 Bàn Hội Chẩn Vấn Đề (Problem Diagnostic & Council)",
        "🏛️ Bảo Tàng Hồ Sơ Đã Chưng Cất (14+ Profiles)",
        "🧪 Lò Nung Chưng Cất Mới (Distill Anyone)"
    ])

    # =========================================================================
    # TAB 1: BÀN HỘI CHẨN VẤN ĐỀ
    # =========================================================================
    with t1:
        st.markdown("#### 🎯 Ô Nhập Nan Đề & Bộ Máy Chẩn Đoán Cố Vấn Tinh Hoa")
        st.caption("Nhập bất kỳ bế tắc, quyết định kinh doanh, kỹ thuật hay ngã ba đường nào của bạn. Hệ thống Nữ Oa sẽ bóc tách và triệu hồi các bộ óc phù hợp nhất để hội chẩn.")

        # Gợi ý bài toán nhanh
        with st.expander("💡 Bấm để nạp nhanh bài toán mẫu thực tế:", expanded=False):
            c_sample_cols = st.columns(3)
            for idx, sc in enumerate(SAMPLE_PROBLEMS):
                with c_sample_cols[idx % 3]:
                    if st.button(sc["label"], key=f"btn_quick_sample_{idx}", use_container_width=True):
                        st.session_state["nuwa_problem_input"] = sc["query"]
                        st.session_state["nuwa_diag_result"] = None
                        st.session_state["nuwa_council_result"] = None
                        st.rerun()

        problem_input = st.text_area(
            "Mô tả nan đề / bài toán bạn đang cần giải quyết:",
            value=st.session_state.get("nuwa_problem_input", ""),
            height=130,
            placeholder="Ví dụ: Tôi đang phân vân giữa việc tiếp tục làm sản phẩm theo hướng an toàn hay mạo hiểm dồn toàn lực vào một tính năng AI mới...",
            key="txt_nuwa_problem"
        )

        col_diag_btn, col_clear_btn = st.columns([3, 1])
        with col_diag_btn:
            run_diag = st.button("🔍 CHẨN ĐOÁN & TÌM CỐ VẤN TINH HOA PHÙ HỢP (PHASE 0B)", type="primary", use_container_width=True)
        with col_clear_btn:
            if st.button("🗑️ Xóa Trắng", use_container_width=True):
                st.session_state["nuwa_problem_input"] = ""
                st.session_state["nuwa_diag_result"] = None
                st.session_state["nuwa_council_result"] = None
                st.rerun()

        if run_diag and problem_input.strip():
            with st.spinner("🧠 Nữ Oa đang quét 5 tầng nhận thức của các nhà tư tưởng để tìm lăng kính giải mã..."):
                diag_res = diagnose_and_match_thinkers(problem_input, all_profiles, top_k=3, api_key=active_api_key)
                st.session_state["nuwa_diag_result"] = diag_res
                st.session_state["nuwa_problem_input"] = problem_input
                # Pre-select recommended profile IDs
                rec_ids = [r.get("profile_id") for r in diag_res.get("recommendations", []) if r.get("profile_id")]
                st.session_state["nuwa_selected_thinkers"] = rec_ids

        # Hiển thị kết quả chẩn đoán nếu có
        diag_res = st.session_state.get("nuwa_diag_result")
        if diag_res:
            st.divider()
            render_html_safe(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid #38bdf8; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">
                    KẾT QUẢ CHẨN ĐOÁN CHIỀU KÍCH: {diag_res.get('dimension', 'Đa chiều')}
                </div>
                <div style="color: #f8fafc; font-size: 1.05rem; font-weight: 600; margin: 4px 0;">
                    {diag_res.get('problem_core', '')}
                </div>
                <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 6px;">
                    💡 <i>{diag_res.get('preliminary_insight', '')}</i>
                </div>
            </div>
            """)

            st.markdown("##### 👥 Đề Xuất 2-3 Cố Vấn Tinh Hoa Khắc Tinh Của Vấn Đề:")
            recs = diag_res.get("recommendations", [])
            cols_rec = st.columns(len(recs)) if recs else [st.container()]
            
            for idx, r in enumerate(recs):
                prof = get_profile_by_id(r.get("profile_id", ""))
                col_box = cols_rec[idx] if idx < len(cols_rec) else st.container()
                with col_box:
                    avatar = prof.get("avatar", "🧠") if prof else "🧠"
                    p_name = prof.get("name", r.get("profile_id", "Cố vấn")) if prof else r.get("profile_id", "Cố vấn")
                    score = r.get("match_score", 90)
                    
                    render_html_safe(f"""
                    <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(56, 189, 248, 0.3); 
                                border-radius: 10px; padding: 14px; height: 100%; display: flex; flex-direction: column;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.5rem;">{avatar}</span>
                            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.75rem; 
                                         font-weight: 700; padding: 2px 8px; border-radius: 999px; border: 1px solid rgba(16, 185, 129, 0.4);">
                                🔥 {score}% PHÙ HỢP
                            </span>
                        </div>
                        <h4 style="color: #f8fafc; margin: 8px 0 4px 0; font-size: 1.1rem;">{p_name}</h4>
                        <div style="color: #38bdf8; font-size: 0.82rem; font-weight: 600; margin-bottom: 8px;">
                            🔍 Lăng kính: {r.get('core_lens', '')}
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.4; flex-grow: 1;">
                            {r.get('match_reason', '')}
                        </div>
                        <div style="margin-top: 10px; background: rgba(239, 68, 68, 0.1); border-left: 2px solid #ef4444; padding: 6px 8px; border-radius: 4px; font-size: 0.78rem; color: #fca5a5;">
                            ⚠️ <b>Ranh giới:</b> {r.get('blindspot_warning', '')}
                        </div>
                    </div>
                    """)

            st.markdown("---")
            st.markdown("##### 🏛️ Chọn Hội Đồng Cố Vấn Tham Gia Hội Chẩn:")
            st.caption("Bạn có thể giữ nguyên các cố vấn được đề xuất ở trên hoặc tùy chọn thêm/bớt từ kho hồ sơ:")
            
            all_opts = {p["id"]: f"{p.get('avatar','🧠')} {p['name']} — {p.get('domain','')[:40]}..." for p in all_profiles}
            default_selected = [pid for pid in st.session_state.get("nuwa_selected_thinkers", []) if pid in all_opts]
            if not default_selected and recs:
                default_selected = [recs[0].get("profile_id")]

            selected_council = st.multiselect(
                "Danh sách các cố vấn tham gia mổ xẻ:",
                options=list(all_opts.keys()),
                default=default_selected,
                format_func=lambda x: all_opts.get(x, x),
                key="ms_nuwa_thinkers"
            )

            if st.button("⚡ TIẾN HÀNH HỘI CHẨN ĐA CHIỀU (COUNCIL OF THINKERS)", type="primary", use_container_width=True):
                if not selected_council:
                    st.warning("Vui lòng chọn ít nhất 1 cố vấn để tiến hành hội chẩn.")
                else:
                    with st.spinner("🔥 Các nhà tư tưởng đang soi chiếu vấn đề qua 5 tầng nhận thức và phản biện lẫn nhau..."):
                        c_res = consult_thinkers_council(problem_input, selected_council, all_profiles, api_key=active_api_key)
                        st.session_state["nuwa_council_result"] = c_res
                        st.session_state["nuwa_council_problem"] = problem_input

        # Hiển thị kết quả hội chẩn nếu có
        c_res = st.session_state.get("nuwa_council_result")
        if c_res:
            st.markdown("### 🏆 BÁO CÁO HỘI CHẨN ĐA MÔ HÌNH")
            st.caption(f"Nan đề: *\"{st.session_state.get('nuwa_council_problem', '')[:100]}...\"*")

            # 1. Ý kiến từng nhà tư tưởng
            t_advices = c_res.get("thinkers_advice", [])
            for t_item in t_advices:
                prof = get_profile_by_id(t_item.get("profile_id", ""))
                avatar = prof.get("avatar", "🧠") if prof else "🧠"
                
                with st.expander(f"{avatar} **Góc Nhìn Của {t_item.get('name', 'Cố vấn')}**", expanded=True):
                    col_l1, col_l2 = st.columns([1, 1])
                    with col_l1:
                        st.markdown(f"**🔍 Lăng kính nhận thức (Mental Model):**\n\n{t_item.get('applied_mental_model', '')}")
                        st.markdown(f"**⚡ Quy tắc quyết định (Heuristic):**\n\n`{t_item.get('applied_heuristic', '')}`")
                    with col_l2:
                        st.error(f"**⚠️ Vùng cấm & Bẫy ngụy biện (Anti-pattern):**\n\n{t_item.get('trap_warning', '')}")
                        st.success(f"**🎯 Hành động đề xuất:**\n\n{t_item.get('action_step', '')}")

                    render_html_safe(f"""
                    <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 14px; border-radius: 6px; margin-top: 10px;">
                        <span style="color: #fbbf24; font-weight: 700; font-size: 0.85rem;">💥 PHẢN BIỆN SẮC BÉN THEO DNA BIỂU ĐẠT:</span><br>
                        <i style="color: #fde68a; font-size: 0.95rem;">\"{t_item.get('brutal_critique', '')}\"</i>
                    </div>
                    """)

            # 2. Tổng hợp Lollapalooza
            syn = c_res.get("lollapalooza_synthesis", {})
            if syn:
                st.divider()
                render_html_safe(f"""
                <div style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(16, 185, 129, 0.2)); 
                            border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 20px; margin-top: 10px;">
                    <div style="color: #a5b4fc; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">
                        🌐 HIỆU ỨNG CỘNG HƯỞNG LOLLAPALOOZA (ĐỒNG THUẬN TỐI THƯỢNG)
                    </div>
                    <h3 style="color: #f8fafc; margin: 8px 0 12px 0;">{syn.get('convergence_point', '')}</h3>
                    <div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 14px; margin-bottom: 12px; border-left: 4px solid #10b981;">
                        <div style="color: #34d399; font-weight: 700; font-size: 0.9rem;">🚀 NƯỚC ĐI BẤT ĐỐI XỨNG CẦN LÀM TRONG 24 GIỜ:</div>
                        <div style="color: #f1f5f9; font-size: 1.05rem; font-weight: 600; margin-top: 4px;">
                            {syn.get('asymmetric_action_24h', '')}
                        </div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.9rem;">
                        🛡️ <b>Nguyên lý trường tồn:</b> <i>{syn.get('long_term_rule', '')}</i>
                    </div>
                </div>
                """)

            # Export & Save actions
            st.divider()
            c_exp1, c_exp2 = st.columns([1, 1])
            with c_exp1:
                md_content = export_council_advice_to_markdown(st.session_state.get("nuwa_council_problem", ""), c_res)
                file_name = f"Hoi_Chan_Nuwa_{sanitize_filename(st.session_state.get('nuwa_council_problem', '')[:25])}.md"
                st.download_button(
                    label="📥 Xuất Báo Cáo Hội Chẩn (.md)",
                    data=md_content,
                    file_name=file_name,
                    mime="text/markdown",
                    use_container_width=True
                )
            with c_exp2:
                if st.button("💾 Lưu Vào Nhật Ký Quyết Định Thực Chiến", use_container_width=True):
                    prob_desc = st.session_state.get("nuwa_council_problem", "")
                    syn_action = syn.get("asymmetric_action_24h", "Hành động bất đối xứng") if syn else "Quyết định sau hội chẩn"
                    dec_id = create_decision_entry(
                        title=f"[Hội Chẩn Nuwa] {prob_desc[:50]}...",
                        description=f"Nan đề: {prob_desc}\n\nGiải pháp Lollapalooza: {syn_action}",
                        chosen_option=syn_action,
                        category="💼 Sự nghiệp, Dự án & Kinh doanh",
                        review_days=30,
                        mental_models_used=[t.get("name") for t in t_advices]
                    )
                    st.success(f"🎉 Đã lưu thành công vào Nhật Ký Quyết Định (Mã: `{dec_id}` - Xem tại phòng Phân Rã & Nhật Ký)!")


    # =========================================================================
    # TAB 2: BẢO TÀNG HỒ SƠ ĐÃ CHƯNG CẤT (14+ PROFILES)
    # =========================================================================
    with t2:
        st.markdown(f"#### 🏛️ Kho Tàng {len(all_profiles)} Hồ Sơ Nhận Thức Đã Chưng Cất")
        st.caption("Các bộ óc xuất chúng đã được bóc tách toàn diện 5 tầng nhận thức, sẵn sàng làm việc và tư vấn bất kỳ lúc nào.")

        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_kw = st.text_input("🔍 Tìm kiếm theo tên hoặc từ khóa:", value="", placeholder="Ví dụ: Musk, Munger, Code, Đầu tư, Sản phẩm...")
        with col_filter:
            filter_type = st.selectbox("Lọc danh mục:", ["Tất cả hồ sơ", "14 Hồ Sơ Cốt Lõi (Built-in)", "Hồ Sơ Mở Rộng Của Bạn (Custom)"])

        # Filter profiles
        display_profiles = all_profiles
        if filter_type == "14 Hồ Sơ Cốt Lõi (Built-in)":
            display_profiles = [p for p in all_profiles if p.get("is_builtin", False)]
        elif filter_type == "Hồ Sơ Mở Rộng Của Bạn (Custom)":
            display_profiles = [p for p in all_profiles if not p.get("is_builtin", False)]

        if search_kw.strip():
            kw = search_kw.lower().strip()
            display_profiles = [
                p for p in display_profiles
                if kw in p.get("name", "").lower()
                or kw in p.get("domain", "").lower()
                or kw in p.get("tagline", "").lower()
                or kw in p.get("id", "").lower()
            ]

        st.markdown(f"Đang hiển thị **{len(display_profiles)}** hồ sơ:")

        # Hiển thị dạng thẻ
        for p in display_profiles:
            is_built = p.get("is_builtin", False)
            badge_label = "🔥 GỐC NUWA" if is_built else "✨ TỰ CHƯNG CẤT"
            badge_color = "#38bdf8" if is_built else "#34d399"
            badge_bg = "rgba(56, 189, 248, 0.15)" if is_built else "rgba(16, 185, 129, 0.15)"
            
            with st.expander(f"{p.get('avatar','🧠')} **{p.get('name')}** — *{p.get('domain')}*", expanded=False):
                # Header card
                render_html_safe(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); 
                            border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #f8fafc; font-size: 1.15rem;">
                            {p.get('avatar','🧠')} {p.get('name')}
                        </span>
                        <span style="background: {badge_bg}; color: {badge_color}; font-size: 0.75rem; 
                                     font-weight: 700; padding: 2px 8px; border-radius: 999px;">
                            {badge_label}
                        </span>
                    </div>
                    <div style="color: #38bdf8; font-size: 0.9rem; font-weight: 600; margin: 4px 0;">
                        \"{p.get('tagline', '')}\"
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">
                        <b>Định vị:</b> {p.get('domain', '')}
                    </div>
                </div>
                """)

                # Details
                c_p1, c_p2 = st.columns([1, 1])
                with c_p1:
                    st.markdown("**👤 Bản sắc nhận thức (Identity):**")
                    st.caption(p.get("identity", "Không có mô tả"))

                    st.markdown(f"**🔍 Lăng kính nhận thức ({len(p.get('mental_models', []))} Models):**")
                    for m in p.get("mental_models", []):
                        st.markdown(f"- **{m.get('name')}**: *{m.get('one_liner', '')}*")

                    st.markdown("**🧬 DNA Biểu đạt & Phong cách:**")
                    for dna in p.get("expression_dna", []):
                        st.markdown(f"- {dna}")

                with c_p2:
                    st.markdown(f"**⚡ Quy tắc trực giác quyết định ({len(p.get('decision_heuristics', []))} Heuristics):**")
                    for h in p.get("decision_heuristics", []):
                        st.markdown(f"- `{h}`")

                    st.markdown("**⚠️ Vùng cấm (Anti-patterns — Tuyệt đối không làm):**")
                    for ap in p.get("anti_patterns", []):
                        st.error(f"⛔ {ap}")

                    st.markdown("**🛡️ Ranh giới trung thực (Honest Boundaries — Không giải quyết được gì):**")
                    for hb in p.get("honest_boundaries", []):
                        st.warning(f"🛑 {hb}")

                # Raw markdown view & Delete button
                c_sub1, c_sub2 = st.columns([3, 1])
                with c_sub1:
                    with st.expander("📄 Xem Mã Nguồn SKILL.md Nguyên Bản", expanded=False):
                        st.code(p.get("raw_skill_md", "Chưa có file markdown."), language="markdown")
                with c_sub2:
                    if not is_built:
                        if st.button("🗑️ Xóa Hồ Sơ Này", key=f"btn_del_prof_{p.get('id')}", use_container_width=True):
                            remove_distilled_profile(p.get("id"))
                            st.success(f"Đã xóa hồ sơ {p.get('name')} thành công!")
                            st.rerun()


    # =========================================================================
    # TAB 3: XƯỞNG ĐÚC CHƯNG CẤT MỚI (DISTILL ANYONE)
    # =========================================================================
    with t3:
        st.markdown("#### 🧪 Xưởng Đúc Chưng Cất Nhận Thức Bất Kỳ Ai (Nuwa Protocol)")
        st.caption("Muốn bổ sung Warren Buffett, Peter Thiel, Sam Altman, Jensen Huang, Lý Quang Diệu hay bất kỳ người cố vấn cá nhân nào? Hãy nhập tên và kích hoạt lò nung. Hệ thống sẽ bóc tách chuẩn 5 tầng nhận thức và lưu vào cơ sở dữ liệu để tăng kho hồ sơ vĩnh viễn!")

        c_f1, c_f2 = st.columns([1, 1])
        with c_f1:
            forge_name = st.text_input(
                "Tên nhân vật / Chuyên gia cần chưng cất (*):",
                placeholder="Ví dụ: Warren Buffett, Peter Thiel, Jensen Huang, Lý Quang Diệu...",
                key="txt_forge_name"
            )
            forge_domain = st.text_input(
                "Lĩnh vực chuyên môn cốt lõi:",
                placeholder="Ví dụ: Đầu tư giá trị dài hạn, Độc quyền sáng tạo 0 to 1, Bán dẫn & Siêu máy tính...",
                key="txt_forge_domain"
            )
            forge_focus = st.selectbox(
                "Tiêu điểm chưng cất ưu tiên:",
                [
                    "Toàn diện (Hệ điều hành nhận thức hoàn chỉnh)",
                    "Quyết định đầu tư & Phân bổ vốn",
                    "Khởi nghiệp & Xây dựng sản phẩm",
                    "Lãnh đạo, Tổ chức & Quản trị nhân tài",
                    "Đàm phán & Nghệ thuật tạo đòn bẩy",
                    "Sáng tạo nội dung & Kỹ nghệ truyền thông"
                ],
                key="sb_forge_focus"
            )

        with c_f2:
            forge_corpus = st.text_area(
                "Tài liệu / Trích dẫn / Bài viết tham khảo (Tùy chọn):",
                height=180,
                placeholder="Dán các bài phát biểu, ghi chú, sách, bài báo hoặc phỏng vấn của nhân vật tại đây để chất lượng chưng cất đạt độ chính xác tối đa. Nếu để trống, AI sẽ tự động truy xuất từ toàn bộ tri thức công khai và các quyết định lịch sử của nhân vật.",
                key="txt_forge_corpus"
            )

        st.info("💡 **Quy trình chuẩn Nữ Oa:** Quá trình chưng cất sẽ bóc tách: 1. Bản sắc & Khẩu quyết ➔ 2. 4-5 Lăng kính nhận thức ➔ 3. 4-6 Quy tắc quyết định ➔ 4. DNA Biểu đạt ➔ 5. Vùng cấm ➔ 6. Ranh giới trung thực.")

        if st.button("🔥 KÍCH HOẠT LÒ NUNG CHƯNG CẤT NHẬN THỨC (NUWA PROTOCOL)", type="primary", use_container_width=True):
            if not forge_name.strip():
                st.error("Vui lòng nhập tên nhân vật cần chưng cất.")
            else:
                with st.spinner(f"🔥 Nữ Oa đang tôi luyện và chưng cất hệ điều hành nhận thức của '{forge_name}'..."):
                    try:
                        new_profile = distill_new_thinker_ai(
                            name=forge_name,
                            domain=forge_domain,
                            corpus_or_bio=forge_corpus,
                            focus_aspect=forge_focus,
                            api_key=active_api_key
                        )
                        st.session_state["nuwa_forge_preview"] = new_profile
                        st.success(f"🎉 Đã chưng cất thành công hồ sơ của **{new_profile.get('name')}**!")
                    except Exception as e:
                        st.error(f"Lỗi trong quá trình chưng cất: {e}")

        # Preview và Lưu vào CSDL
        forge_prev = st.session_state.get("nuwa_forge_preview")
        if forge_prev:
            st.divider()
            st.markdown("### 💎 BẢN XEM TRƯỚC HỒ SƠ VỪA CHƯNG CẤT")
            
            render_html_safe(f"""
            <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(52, 211, 153, 0.4); 
                        border-radius: 10px; padding: 16px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.8rem;">{forge_prev.get('avatar', '🧠')}</span>
                    <span style="background: rgba(52, 211, 153, 0.2); color: #34d399; font-size: 0.8rem; 
                                 font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                        ✨ CHƯNG CẤT MỚI
                    </span>
                </div>
                <h3 style="color: #f8fafc; margin: 8px 0 4px 0;">{forge_prev.get('name')}</h3>
                <div style="color: #38bdf8; font-weight: 600; font-size: 0.95rem; margin-bottom: 6px;">
                    \"{forge_prev.get('tagline', '')}\"
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem;">
                    <b>Lĩnh vực:</b> {forge_prev.get('domain', '')}
                </div>
            </div>
            """)

            col_pv1, col_pv2 = st.columns([1, 1])
            with col_pv1:
                st.markdown("**👤 Bản sắc nhận thức (Identity):**")
                st.caption(forge_prev.get("identity", ""))

                st.markdown("**🔍 Lăng kính nhận thức (Mental Models):**")
                for m in forge_prev.get("mental_models", []):
                    st.markdown(f"- **{m.get('name')}**: *{m.get('one_liner', '')}*\n  {m.get('content', '')[:180]}...")

                st.markdown("**🧬 DNA Biểu đạt:**")
                for d in forge_prev.get("expression_dna", []):
                    st.markdown(f"- {d}")

            with col_pv2:
                st.markdown("**⚡ Quy tắc trực giác quyết định:**")
                for h in forge_prev.get("decision_heuristics", []):
                    st.markdown(f"- `{h}`")

                st.markdown("**⚠️ Vùng cấm (Anti-patterns):**")
                for a in forge_prev.get("anti_patterns", []):
                    st.error(f"⛔ {a}")

                st.markdown("**🛡️ Ranh giới trung thực (Honest Boundaries):**")
                for b in forge_prev.get("honest_boundaries", []):
                    st.warning(f"🛑 {b}")

            if st.button("💾 LƯU CHÍNH THỨC VÀO CƠ SỞ DỮ LIỆU ĐỂ TĂNG KHO HỒ SƠ", type="primary", use_container_width=True):
                success = save_new_distilled_profile(forge_prev)
                if success:
                    st.balloons()
                    st.success(f"🎉 Đã lưu **{forge_prev.get('name')}** vào Cơ sở Dữ liệu thành công! Tổng kho hồ sơ đã tăng lên. Nhân vật này đã sẵn sàng tham gia Bàn Hội Chẩn ở Tab 1.")
                    st.session_state["nuwa_forge_preview"] = None
                    st.rerun()
                else:
                    st.error("Không thể lưu hồ sơ vào cơ sở dữ liệu. Vui lòng kiểm tra quyền ghi.")
