# -*- coding: utf-8 -*-
"""Phân rã thực chiến"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.ai_engine import analyze_problem
from utils.ai_engine import analyze_problem
from utils.knowledge import (
    append_analysis,
    load_user_history,
    update_analysis_note,
    delete_analysis,
)
from utils.decision_journal import (
    DECISION_CATEGORIES,
    REVIEW_INTERVALS,
    OUTCOME_RATINGS,
    create_decision_entry,
    get_user_decisions,
    resolve_decision_review,
    get_decision_summary_stats,
)

st.title("🚀 Phân Rã Thực Chiến & Nhật Ký Quyết Định")
st.caption("Bóc tách vấn đề qua 9 Lăng kính Tinh hoa, Lưu vết nhận định cá nhân & Hiệu chuẩn sai số sau 30-90 ngày.")

tab7_subtabs = st.tabs([
    "🚀 Phân Rã Vấn Đề (AI 9 Lenses)",
    "📜 Lịch Sử Bản Phân Rã Chi Tiết (Deep Archive)",
    "📓 Elite Decision Journal (Nhật Ký Quyết Định & Đo Sai Số)",
])

with tab7_subtabs[0]:
    st.markdown("""
    Đưa bất kỳ vấn đề, quyết định, tình huống hóc búa hay dự án thực tế vào đây. 
    Hệ thống AI sẽ kích hoạt cùng lúc **9 Lăng kính Tinh hoa & Các Mô hình Hạt nhân** để bóc tách tận cùng First Principles, 
    nhận diện hệ quả bậc hai, lật ngược vấn đề và đề xuất hành động đòn bẩy cao nhất.
    """)

    sample = st.selectbox(
        "💡 Chọn ví dụ mẫu để thử nghiệm:",
        [
            "— Chọn ví dụ —",
            "Đầu tư CKVN: Thị trường giảm mạnh, tin tức xấu bủa vây, có nên bán tháo hay giải ngân tích sản?",
            "Giao dịch Vàng / XAU: Mục tiêu x5 tài khoản trong 1 năm từ vốn 10.000 lên 50.000, khả thi và rủi ro ra sao?",
            "Quyết định nghề nghiệp: Nên ở lại công ty ổn định hay khởi nghiệp với rủi ro cao nhưng tiềm năng lớn?",
            "Học sinh Wellspring: Muốn tham gia nhiều CLB nhưng sợ tụt điểm số và áp lực thi cử, giải quyết ra sao?",
            "Thời gian: Cuối tuần nên cày phim xả stress hay dành 3 giờ rèn luyện tư duy và đọc sách?",
        ],
        key="tab7_sample_select",
    )
    initial = "" if sample.startswith("—") else sample
    if "prefill_problem" in st.session_state and st.session_state["prefill_problem"]:
        initial = st.session_state.pop("prefill_problem")

    problem = st.text_area("Nội dung vấn đề cần phân rã:", value=initial, height=120, placeholder="Mô tả cụ thể bối cảnh, mục tiêu, các ràng buộc và điều bạn đang băn khoăn...", key="tab7_problem_input")

    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        run_click = st.button("🚀 Phân rã ngay", type="primary", use_container_width=True, key="tab7_btn_breakdown")
    with col_b2:
        if st.session_state.get("active_analysis"):
            if st.button("🔄 Phân rã mới", use_container_width=True, key="tab7_btn_clear"):
                st.session_state.pop("active_analysis", None)
                st.rerun()

    if run_click:
        if not active_keys:
            st.warning("Cần Gemini API Key (cấu hình trong Secrets hoặc sidebar).")
        elif not problem.strip():
            st.warning("Hãy nhập nội dung.")
        else:
            with st.spinner("Đang chạy 9 lenses qua Gemini (tự động xoay tua nếu bận/hết quota)..."):
                result = analyze_problem(active_keys, model_choice, problem.strip())

            if not result:
                st.error("Không có kết quả.")
            elif result.get("error"):
                st.error(result["error"])
                if result.get("raw"):
                    st.code(result["raw"])
            else:
                summary = result.get("first_principles_breakdown", "")[:300]
                entry = append_analysis(username, problem.strip(), summary, full_result=result)
                st.session_state["active_analysis"] = entry

                st.session_state["dj_pref_title"] = problem.strip()[:60]
                st.session_state["dj_pref_hypo"] = result.get("first_principles_breakdown", "")[:300]
                st.session_state["dj_pref_inv"] = result.get("elite_lenses", {}).get("inversion", "")[:200]
                st.session_state["dj_pref_sec"] = result.get("elite_lenses", {}).get("second_order", "")[:200]
                st.session_state["open_new_decision_form"] = True
                st.rerun()

    active_entry = st.session_state.get("active_analysis")
    if active_entry:
        res = active_entry.get("details", {})
        a_id = active_entry.get("id") or active_entry.get("time")
        key_info = f" (Key: `{res.get('_used_key')}`)" if res.get("_used_key") else ""
        st.success(f"✅ Đã phân rã xong{key_info} · Đã lưu vĩnh viễn vào Supabase")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🔬 First Principles (Bản chất gốc)")
            st.write(res.get("first_principles_breakdown", active_entry.get("summary", "—")))
            st.markdown("#### 📚 Nguyên lý Khởi thủy Liên quan")
            pr_list = res.get("core_principles_found", [])
            if pr_list:
                for p in pr_list:
                    domain_str = f" *({p.get('domain')})*" if p.get('domain') else ""
                    desc_str = f": {p.get('description')}" if p.get('description') else ""
                    st.markdown(f"- **{p.get('name')}**{domain_str}{desc_str}")
            else:
                st.caption("Không có nguyên lý liên quan cụ thể.")

        with c2:
            st.markdown("#### 👁️ Elite Lenses (Các lăng kính tư duy)")
            lenses = res.get("elite_lenses", {})
            lens_titles = {
                "inversion": "🔄 Tư duy Đảo ngược (Inversion)",
                "second_order": "🎯 Hệ quả bậc hai (Second-Order)",
                "bayesian": "🎲 Xác suất Bayes (Bayesian Thinking)",
                "leverage": "⚙️ Điểm tựa & Đòn bẩy (Leverage)",
                "multi_timescale": "⏳ Đa quy mô thời gian (Multi-timescale)",
            }
            for k, v in lenses.items():
                title = lens_titles.get(k, k.replace('_', ' ').title())
                st.markdown(f"**{title}:** {v}")

        st.markdown("#### ⚡ Hành động gợi ý có đòn bẩy cao")
        for a in res.get("actionable_insights", []):
            st.markdown(f"- {a}")

        st.markdown("#### 🧭 Câu hỏi cốt lõi cần bạn quyết định")
        for h in res.get("human_decision_needed", []):
            st.markdown(f"- {h}")

        st.divider()
        st.markdown("### 📝 Ghi Chú & Nhận Định Cá Nhân Của Bạn")
        st.caption("Đúc kết nhận định, bài học hoặc chiến lược hành động bạn tự rút ra từ phân rã này (được lưu trực tiếp vào cơ sở dữ liệu).")

        curr_note = active_entry.get("user_note", "")
        user_note_input = st.text_area(
            "Nhận định / Kết luận hành động của bạn:",
            value=curr_note,
            placeholder="Ví dụ: Sau khi xem lăng kính đảo ngược và xác suất Bayes, việc đặt mục tiêu x5 tài khoản trong 1 năm là quá tham vọng. Tôi quyết định hạ mục tiêu về 30-50%/năm, rủi ro 1%/lệnh để bảo toàn vốn...",
            height=90,
            key=f"active_note_input_{a_id}",
        )

        col_n1, col_n2 = st.columns([1, 2])
        with col_n1:
            if st.button("💾 Lưu Nhận Định Này", type="primary", use_container_width=True, key=f"btn_save_active_note_{a_id}"):
                update_analysis_note(username, a_id, user_note_input)
                active_entry["user_note"] = user_note_input
                st.session_state["active_analysis"] = active_entry
                st.success("✅ Đã lưu nhận định cá nhân của bạn vào Supabase!")
                st.rerun()
        with col_n2:
            st.info("💡 Bạn có thể bấm sang tab **'📓 Elite Decision Journal'** bên cạnh để đặt lịch theo dõi và kiểm định kết quả sau 30-90 ngày.")

with tab7_subtabs[1]:
    st.markdown("### 📜 Lịch Sử Toàn Bộ Các Bản Phân Rã Chi Tiết")
    st.caption("Xem lại trọn vẹn từng lăng kính, nguyên lý khởi thủy và cập nhật ghi chú nhận định cá nhân của bạn bất cứ lúc nào.")

    hist_arch = load_user_history(username)
    all_ana = hist_arch.get("analyses", [])

    if not all_ana:
        st.info("Chưa có bản phân rã nào được lưu. Hãy nhập vấn đề ở Tab 1 để bắt đầu!")
    else:
        st.metric("📊 Tổng số bản phân rã đã lưu", f"{len(all_ana)} bản")
        st.markdown("---")

        for idx, a in enumerate(all_ana):
            a_id = a.get("id") or a.get("time")
            a_time = a.get("time", "—")
            a_prob = a.get("problem", "—")
            a_note = a.get("user_note", "")
            has_note_badge = " · 📝 Có nhận định" if a_note else ""

            with st.expander(f"🔍 [{a_time}] {a_prob[:80]}...{has_note_badge}", expanded=(idx == 0)):
                st.markdown("**📌 Vấn đề ban đầu:**")
                st.info(a_prob)

                details = a.get("details")
                if details and isinstance(details, dict):
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.markdown("#### 🔬 First Principles (Bản chất gốc)")
                        st.write(details.get("first_principles_breakdown", "—"))

                        st.markdown("#### 📚 Nguyên lý Khởi thủy Liên quan")
                        pr_list = details.get("core_principles_found", [])
                        if pr_list:
                            for p in pr_list:
                                domain_str = f" *({p.get('domain')})*" if p.get('domain') else ""
                                desc_str = f": {p.get('description')}" if p.get('description') else ""
                                st.markdown(f"- **{p.get('name')}**{domain_str}{desc_str}")
                        else:
                            st.caption("Không có nguyên lý liên quan cụ thể.")

                    with col_d2:
                        st.markdown("#### 👁️ Elite Lenses (Các lăng kính tư duy)")
                        lenses = details.get("elite_lenses", {})
                        lens_titles = {
                            "inversion": "🔄 Tư duy Đảo ngược (Inversion)",
                            "second_order": "🎯 Hệ quả bậc hai (Second-Order)",
                            "bayesian": "🎲 Xác suất Bayes (Bayesian Thinking)",
                            "leverage": "⚙️ Điểm tựa & Đòn bẩy (Leverage)",
                            "multi_timescale": "⏳ Đa quy mô thời gian (Multi-timescale)",
                        }
                        for k, v in lenses.items():
                            title = lens_titles.get(k, k.replace('_', ' ').title())
                            st.markdown(f"**{title}:** {v}")

                    st.markdown("#### ⚡ Hành động gợi ý có đòn bẩy cao")
                    for act in details.get("actionable_insights", []):
                        st.markdown(f"- {act}")

                    st.markdown("#### 🧭 Câu hỏi cốt lõi cần bạn quyết định")
                    for dec in details.get("human_decision_needed", []):
                        st.markdown(f"- {dec}")
                else:
                    st.markdown("#### 🔬 Tóm tắt First Principles")
                    st.write(a.get("summary", "—"))

                st.divider()
                st.markdown("#### 📝 Nhận định / Ghi chú cá nhân")
                edit_note = st.text_area(
                    "Cập nhật nhận định / đúc kết:",
                    value=a_note,
                    key=f"archive_note_{a_id}_{idx}",
                    height=80,
                    placeholder="Nhập nhận định cá nhân của bạn tại đây...",
                )
                col_save_arch, col_del_arch = st.columns([1, 4])
                with col_save_arch:
                    if st.button("💾 Cập nhật nhận định", key=f"btn_save_arch_{a_id}_{idx}"):
                        update_analysis_note(username, a_id, edit_note)
                        st.success("✅ Đã cập nhật nhận định!")
                        st.rerun()
                with col_del_arch:
                    if st.button("🗑️ Xóa bản phân rã này", key=f"btn_del_arch_{a_id}_{idx}"):
                        delete_analysis(username, a_id)
                        st.warning("Đã xóa bản phân rã khỏi lịch sử!")
                        st.rerun()

with tab7_subtabs[2]:
    st.markdown("### 📓 Elite Decision Journal — Lưu Vết & Hiệu Chuẩn Quyết Định")
    st.caption("Phương pháp của Ray Dalio & Howard Marks: Không thể nâng cao chất lượng tư duy nếu không ghi chép giả định ban đầu và kiểm định lại kết quả thực tế sau 30-90 ngày để triệt tiêu Thiên kiến nhận thức muộn (Hindsight Bias).")

    d_stats = get_decision_summary_stats(username)

    dj_c1, dj_c2, dj_c3, dj_c4 = st.columns(4)
    with dj_c1:
        st.metric("📋 Tổng quyết định", f"{d_stats['total_logged']} mục")
    with dj_c2:
        st.metric("🕒 Đang chờ kiểm định", f"{d_stats['pending_count']} mục")
    with dj_c3:
        due_cnt = d_stats['due_count']
        st.metric("⏳ Đến hạn kiểm định", f"{due_cnt} mục", "Cần xem lại ngay!" if due_cnt > 0 else "Đúng tiến độ")
    with dj_c4:
        acc = d_stats['calibration_accuracy']
        st.metric("🎯 Điểm Hiệu Chuẩn", f"{acc}%" if d_stats['reviewed_count'] > 0 else "Chưa có", f"{d_stats['reviewed_count']} bài đã duyệt")

    st.divider()

    with st.expander("➕ Ghi Nhận Quyết Định Mới Vào Nhật Ký", expanded=(d_stats['total_logged'] == 0 or st.session_state.get("open_new_decision_form", False))):
        with st.form("form_create_decision"):
            pref_title = st.session_state.get("dj_pref_title", "")
            pref_hypo = st.session_state.get("dj_pref_hypo", "")
            pref_inv = st.session_state.get("dj_pref_inv", "")
            pref_sec = st.session_state.get("dj_pref_sec", "")

            dec_title = st.text_input("Tiêu đề quyết định:", value=pref_title, placeholder="Ví dụ: Đầu tư cổ phiếu FPT, Chọn chuyên ngành AI, Rời bỏ công ty X...")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                dec_cat = st.selectbox("Lĩnh vực:", DECISION_CATEGORIES)
            with c_f2:
                dec_interval_label = st.selectbox("Mốc hẹn kiểm định thực tế:", list(REVIEW_INTERVALS.keys()), index=1)
                dec_interval_days = REVIEW_INTERVALS[dec_interval_label]

            dec_hypo = st.text_area(
                "Giả định cốt lõi (Core Hypothesis):",
                value=pref_hypo,
                height=80,
                placeholder="Tại sao bạn đưa ra quyết định này? Bạn tin rằng điều gì sẽ xảy ra và vì sao?",
            )

            dec_conf = st.slider(
                "Mức độ tự tin / Xác suất Bayes chủ quan của bạn:",
                min_value=10,
                max_value=100,
                value=75,
                step=5,
                format="%d%%",
                help="Theo tư duy Bayes: Đừng bao giờ đặt 100% hay 0%. Hãy thành thật với mức độ không chắc chắn.",
            )

            c_ta1, c_ta2 = st.columns(2)
            with c_ta1:
                dec_inv = st.text_area(
                    "Bẫy đảo ngược đã lường trước (Inversion):",
                    value=pref_inv,
                    height=80,
                    placeholder="Những điều gì có thể biến quyết định này thành thảm họa? Bạn phòng vệ thế nào?",
                )
            with c_ta2:
                dec_sec = st.text_area(
                    "Hệ quả bậc hai dự kiến (Second-Order Effects):",
                    value=pref_sec,
                    height=80,
                    placeholder="Sau khi quyết định này được thực thi, phản ứng tiếp theo của hệ thống sẽ là gì?",
                )

            st.markdown("---")
            st.markdown("##### 🎭 Feynman Honesty Gate: *'You must not fool yourself' — Richard Feynman*")
            st.caption("Nguyên tắc đầu tiên là bạn không được tự lừa dối chính mình — và bạn chính là người dễ bị lừa nhất.")
            dec_feynman_honesty = st.text_area(
                "Tự vấn chống tự lừa dối (Điều gì tôi đang thầm hy vọng là đúng mà chưa có bằng chứng thực tế?):",
                value="",
                height=70,
                placeholder="Ví dụ: Tôi có đang thầm hy vọng thị trường sẽ quay đầu chỉ vì không muốn thừa nhận mình đã chọn sai? Điều gì tôi đang né tránh nhìn thẳng vào?",
                help="Bắt buộc bản thân đối diện với mong ước chủ quan (wishful thinking) và điểm mù nhận thức.",
            )

            btn_save_dec = st.form_submit_button("💾 Lưu Quyết Định Vào Nhật Ký", type="primary", use_container_width=True)

        if btn_save_dec:
            if not dec_title.strip() or not dec_hypo.strip():
                st.warning("Vui lòng nhập ít nhất Tiêu đề và Giả định cốt lõi của quyết định.")
            else:
                new_dec = create_decision_entry(
                    username=username,
                    title=dec_title.strip(),
                    category=dec_cat,
                    hypothesis=dec_hypo.strip(),
                    confidence_pct=dec_conf,
                    inversion_traps=dec_inv.strip(),
                    second_order_consequences=dec_sec.strip(),
                    review_days=dec_interval_days,
                    feynman_honesty_check=dec_feynman_honesty.strip(),
                )
                st.session_state["open_new_decision_form"] = False
                st.success(f"✅ Đã ghi nhận quyết định '{new_dec['title']}'! Hệ thống sẽ nhắc bạn kiểm định vào ngày {new_dec['review_date']}.")
                st.rerun()

    st.markdown("#### 📋 Danh Sách Quyết Định Trong Nhật Ký")
    user_decs = d_stats["decisions"]

    if not user_decs:
        st.info("Nhật ký của bạn đang trống. Hãy bấm '➕ Ghi Nhận Quyết Định Mới Vào Nhật Ký' ở trên để bắt đầu lưu vết các quyết định quan trọng!")
    else:
        filter_status = st.radio(
            "Lọc theo trạng thái:",
            ["Tất cả", "⏳ Đến hạn kiểm định (Due)", "🕒 Đang chờ (Pending)", "✅ Đã kiểm định (Reviewed)"],
            horizontal=True,
            key="dj_filter_status",
        )

        status_map = {
            "⏳ Đến hạn kiểm định (Due)": "due",
            "🕒 Đang chờ (Pending)": "pending",
            "✅ Đã kiểm định (Reviewed)": "reviewed",
        }

        for d in user_decs:
            if filter_status != "Tất cả":
                target_st = status_map[filter_status]
                if d.get("status") != target_st:
                    continue

            st_icon = "⏳ CẦN KIỂM ĐỊNH" if d.get("status") == "due" else ("🕒 Đang chờ" if d.get("status") == "pending" else "✅ Đã kiểm định")
            expander_title = f"{st_icon} · [{d.get('category', '').split()[0]}] {d.get('title')} (Tạo: {d.get('created_at')} — Hẹn: {d.get('review_date')})"

            with st.expander(expander_title, expanded=(d.get("status") == "due")):
                c_det1, c_det2 = st.columns(2)
                with c_det1:
                    st.markdown(f"**📌 Giả định gốc:**  \n{d.get('hypothesis')}")
                    st.markdown(f"**🎯 Độ tự tin ban đầu:** `{d.get('confidence_pct')}%`")
                with c_det2:
                    if d.get("inversion_traps"):
                        st.markdown(f"**⚠️ Bẫy đảo ngược lường trước:**  \n{d.get('inversion_traps')}")
                    if d.get("second_order_consequences"):
                        st.markdown(f"**🌊 Hệ quả bậc hai dự kiến:**  \n{d.get('second_order_consequences')}")
                    if d.get("feynman_honesty_check"):
                        st.warning(f"🎭 **Feynman Honesty Check (Tự vấn chống tự lừa dối):**  \n*{d.get('feynman_honesty_check')}*")

                st.markdown("---")

                if d.get("status") == "reviewed":
                    st.success(f"**Kết quả thực tế ({d.get('reviewed_at')}):**  \n{d.get('actual_outcome')}")
                    sc_c1, sc_c2 = st.columns(2)
                    with sc_c1:
                        st.metric("Đánh giá kết quả", f"{d.get('outcome_score')}%")
                    with sc_c2:
                        diff_val = d.get('calibration_diff', 0)
                        st.metric("Độ lệch nhận thức", f"{diff_val}%", "Khớp hoàn hảo!" if diff_val <= 10 else "Có sai lệch")
                    if d.get("lessons_learned"):
                        st.info(f"💡 **Bài học rút ra:** {d.get('lessons_learned')}")
                else:
                    st.markdown("##### 🔍 Kiểm Định Thực Tế & Tự Đo Sai Số Nhận Thức")
                    with st.form(key=f"form_review_{d['id']}"):
                        actual_res = st.text_area(
                            "Thực tế diễn ra như thế nào?",
                            height=80,
                            placeholder="Ghi nhận khách quan: Điều gì đã xảy ra so với giả định ban đầu của bạn?",
                        )
                        rate_label = st.selectbox(
                            "Mức độ chính xác so với dự tính ban đầu:",
                            list(OUTCOME_RATINGS.keys()),
                            index=1,
                        )
                        outcome_num = OUTCOME_RATINGS[rate_label]

                        lessons = st.text_area(
                            "Bài học rút ra (Tư duy nào đã giúp ích hoặc mô hình nào bạn đã bỏ sót?):",
                            height=80,
                            placeholder="Ví dụ: Đã quá lạc quan về tiến độ, bỏ quên bẫy chi phí chìm...",
                        )

                        btn_submit_rev = st.form_submit_button("🎯 Hoàn Tất Kiểm Định & Ghi Nhận Sai Số", type="primary", use_container_width=True)

                    if btn_submit_rev:
                        if not actual_res.strip():
                            st.warning("Vui lòng ghi lại kết quả thực tế để hoàn tất kiểm định.")
                        else:
                            resolve_decision_review(
                                username=username,
                                decision_id=d["id"],
                                actual_outcome=actual_res.strip(),
                                outcome_score=outcome_num,
                                lessons_learned=lessons.strip(),
                            )
                            st.success("✅ Đã hoàn tất kiểm định quyết định! Điểm hiệu chuẩn của bạn đã được cập nhật.")
                            st.rerun()


