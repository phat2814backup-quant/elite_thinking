# -*- coding: utf-8 -*-
"""Đấu trường Luyện nhớ"""
from __future__ import annotations

import random
import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.app_common import ensure_quiz_imports
from utils.diagnostic import (
    COGNITIVE_DIMENSIONS,
    DIAGNOSTIC_QUESTIONS,
    evaluate_diagnostic_submission,
    save_user_diagnostic_result,
    get_latest_diagnostic_result,
)
from utils.mental_models import get_pillars, get_all_models
from utils.knowledge import get_domains

_quiz = ensure_quiz_imports()
QUIZ_IMPORT_ERROR = _quiz["error"]
get_user_mastery_summary = _quiz["get_user_mastery_summary"]
get_all_flashcards = _quiz["get_all_flashcards"]
record_quiz_completion = _quiz["record_quiz_completion"]
update_flashcard_mastery = _quiz["update_flashcard_mastery"]
generate_ai_quiz = _quiz["generate_ai_quiz"]
evaluate_feynman_challenge = _quiz["evaluate_feynman_challenge"]
get_theory_questions_for_modes = _quiz["get_theory_questions_for_modes"]
get_theory_questions_for_models = _quiz["get_theory_questions_for_models"]
get_theory_questions_for_principles = _quiz["get_theory_questions_for_principles"]
MODES_QUIZ = _quiz["MODES_QUIZ"]
MODELS_QUIZ = _quiz["MODELS_QUIZ"]
PRINCIPLES_QUIZ = _quiz["PRINCIPLES_QUIZ"]

st.title("⚡ Đấu Trường Luyện Nhớ & Trắc Nghiệm Phản Xạ")
st.caption("Nắm trọn 9 Chế độ · 88 Mô hình Hạt nhân · 100 Nguyên lý Khởi thủy qua Active Recall & Case Quizzes")

if QUIZ_IMPORT_ERROR:
    st.error(f"⚠️ **Thông báo hệ thống Quiz Engine:**\n\n```\n{QUIZ_IMPORT_ERROR}\n```")
    st.info("💡 Nếu bạn đang trên Streamlit Cloud, hãy thử bấm nút **Manage app** ở góc dưới bên phải màn hình và chọn **Reboot app** để nạp lại đầy đủ các module mới.")

# Thống kê thành tích làm chủ
mastery_data = get_user_mastery_summary(username)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("🎯 Độ chính xác Trắc nghiệm", f"{mastery_data['accuracy']}%", f"{mastery_data['total_quizzes']} lượt test")
with col_m2:
    st.metric("🟢 Đã làm chủ (Mastered)", f"{mastery_data['mastered_count']} / 88", f"{mastery_data['mastery_pct']}% tổng mô hình")
with col_m3:
    st.metric("🟡 Đang ghi nhớ", f"{mastery_data['learning_count']} thẻ")
with col_m4:
    st.metric("🔴 Cần ôn tập lại", f"{mastery_data['review_count']} thẻ")

st.progress(mastery_data["mastery_pct"] / 100.0)

arena_tab_diag, arena_tab_th, arena_tab1, arena_tab2, arena_tab3 = st.tabs([
    "🧭 Chẩn Đoán Điểm Mù Nhận Thức",
    "📖 Trắc Nghiệm Lý Thuyết Cốt Lõi",
    "🎯 Trắc Nghiệm Tình Huống Thực Chiến",
    "🗂️ Thẻ Flashcards Phản Xạ 5 Giây",
    "✨ AI Đấu Trí & Thử Thách Feynman"
])

# -------------------------------------------------------------------------
# Sub-tab 0: Chẩn Đoán Điểm Mù Nhận Thức (Cognitive Blindspot Diagnostic)
# -------------------------------------------------------------------------
with arena_tab_diag:
    st.markdown("### 🧭 Chẩn Đoán 6 Chiều Không Gian Nhận Thức & Điểm Mù Tinh Hoa")
    st.caption("Khám phá bản đồ nhận thức của bạn qua 12 tình huống bẫy thực tế. Định vị thế mạnh và vạch trần điểm mù trước khi bước vào các quyết định lớn của cuộc đời.")

    latest_diag = get_latest_diagnostic_result(username)

    retake_key = "retake_diagnostic_flag"
    show_test_form = (latest_diag is None) or st.session_state.get(retake_key, False)

    if latest_diag and not show_test_form:
        st.success(f"🏆 Kết quả chẩn đoán gần nhất của bạn ({latest_diag.get('timestamp')})")
        
        d_c1, d_c2, d_c3 = st.columns([1.5, 1.5, 2])
        with d_c1:
            st.metric("🎯 Chỉ Số Nhận Thức (Cognitive Index)", f"{latest_diag.get('overall_index')}%")
        with d_c2:
            st.markdown(f"**Danh hiệu:**  \n### 🎖️ {latest_diag.get('rank_title')}")
            st.caption(latest_diag.get('rank_desc', ''))
        with d_c3:
            ts = latest_diag.get('top_strength', {})
            cb = latest_diag.get('critical_blindspot', {})
            st.markdown(f"🟢 **Thế mạnh:** {ts.get('name', '')} ({ts.get('score', 0)}%)")
            st.markdown(f"🔴 **Điểm mù chí mạng:** {cb.get('name', '')} ({cb.get('score', 0)}%)")

        st.divider()
        st.markdown("#### 📊 Điểm Chi Tiết 6 Chiều Không Gian Nhận Thức")
        dim_scores = latest_diag.get("dimension_scores", {})
        dim_cols = st.columns(3)
        col_idx = 0
        for dim_key, dim_info in COGNITIVE_DIMENSIONS.items():
            sc = dim_scores.get(dim_key, 0)
            with dim_cols[col_idx % 3]:
                st.markdown(f"**{dim_info['icon']} {dim_info['name']}**")
                st.progress(sc / 100.0)
                st.caption(f"Điểm số: **{sc}%** — *{dim_info['description']}*")
            col_idx += 1

        st.divider()
        st.markdown("#### 🗺️ Lộ Trình Hành Động Đề Xuất 3–6 Tháng Cho Bạn:")
        for rec in latest_diag.get("recommendations", []):
            st.info(f"💡 {rec}")

        if st.button("🔄 Làm lại bài test chẩn đoán (12 câu hỏi)", use_container_width=True):
            st.session_state[retake_key] = True
            st.rerun()

    else:
        st.info("📝 Hãy chọn phương án phản ánh **chính xác nhất phản xạ tự nhiên của bạn trong thực tế**, không chọn theo câu trả lời nghe có vẻ 'đẹp đẽ' nhất để có kết quả chẩn đoán trung thực nhất.")

        user_diag_answers = {}
        for idx, q in enumerate(DIAGNOSTIC_QUESTIONS, 1):
            dim_info = COGNITIVE_DIMENSIONS.get(q["dimension"], {})
            st.markdown(f"##### Câu {idx}: {dim_info.get('icon', '🔹')} {q['title']}")
            st.write(q["scenario"])
            
            options_text = [opt["text"] for opt in q["options"]]
            chosen_opt_text = st.radio(
                f"Lựa chọn của bạn cho câu {idx}:",
                options_text,
                key=f"diag_q_{q['id']}",
                index=None,
            )
            if chosen_opt_text:
                chosen_idx = options_text.index(chosen_opt_text)
                user_diag_answers[q["id"]] = chosen_idx

            st.markdown("---")

        if st.button("📊 Nộp Bài & Xuất Báo Cáo Chẩn Đoán Điểm Mù", type="primary", use_container_width=True):
            if len(user_diag_answers) < len(DIAGNOSTIC_QUESTIONS):
                st.warning(f"Bạn mới trả lời {len(user_diag_answers)}/{len(DIAGNOSTIC_QUESTIONS)} câu. Vui lòng hoàn thành toàn bộ câu hỏi để có kết quả chính xác.")
            else:
                eval_res = evaluate_diagnostic_submission(user_diag_answers)
                save_user_diagnostic_result(username, eval_res)
                st.session_state[retake_key] = False
                st.success("✅ Đã hoàn tất chẩn đoán điểm mù nhận thức! Đang tải báo cáo...")
                st.rerun()

# -------------------------------------------------------------------------
# Sub-tab 1: Trắc Nghiệm Lý Thuyết Cốt Lõi (Theory Foundation Quiz)
# -------------------------------------------------------------------------
with arena_tab_th:
    st.markdown("### 📖 Trắc Nghiệm Lý Thuyết Cốt Lõi & Ma Trận Phản Xạ Đa Chiều")
    st.caption("Muốn làm chủ tư duy đỉnh cao, bạn phải hiểu lý thuyết thật rành mạch: từ Chân lý gốc, Đòn bẩy tối thượng, Bẫy đảo ngược cho đến Ma trận phân biệt tương hỗ giữa các mô hình.")

    if "th_shuffle_seed" not in st.session_state:
        st.session_state["th_shuffle_seed"] = 42

    th_category = st.radio(
        "Chọn phân hệ trắc nghiệm lý thuyết",
        [
            "🧠 9 Chế độ Tư duy Tinh hoa (27 câu hỏi đa chiều)",
            "🕸️ 88 Mô hình Hạt nhân (Toàn bộ 88 mô hình · Ma trận 352 câu)",
            "🔬 100 Nguyên lý Khởi thủy (Toàn bộ 100 nguyên lý khoa học · Ma trận 352 câu)"
        ],
        horizontal=True,
        key="th_quiz_cat_radio"
    )

    th_selected_questions = []
    th_cat_key = ""

    if "9 Chế độ" in th_category:
        th_cat_key = "th_modes"
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            th_mode_angle = st.selectbox(
                "Góc độ khảo sát lý thuyết:",
                [
                    "🌟 Tất cả 3 góc độ (27 câu hỏi chuyên sâu)",
                    "🔬 Bản chất & Định nghĩa cốt lõi (9 câu)",
                    "⚡ Quy trình & Kích hoạt vận hành (9 câu)",
                    "⚠️ Bẫy tư duy đối nghịch & Lỗi ngụy biện (9 câu)"
                ],
                key="th_mode_angle_sel"
            )
        with col_m2:
            if st.button("🎲 Xáo trộn câu hỏi", key="btn_shuf_modes", use_container_width=True):
                st.session_state["th_shuffle_seed"] = random.randint(1, 999999)
                st.rerun()

        angle_map = {
            "🌟 Tất cả 3 góc độ (27 câu hỏi chuyên sâu)": "all",
            "🔬 Bản chất & Định nghĩa cốt lõi (9 câu)": "concept",
            "⚡ Quy trình & Kích hoạt vận hành (9 câu)": "operation",
            "⚠️ Bẫy tư duy đối nghịch & Lỗi ngụy biện (9 câu)": "trap"
        }
        th_selected_questions = get_theory_questions_for_modes(angle=angle_map.get(th_mode_angle, "all"))
        st.info(f"📋 Khoang thi **9 Chế độ Tư duy Tinh hoa** đang hiển thị **{len(th_selected_questions)} câu hỏi lý thuyết**. Khắc sâu bản chất lý thuyết, quy trình vận hành và bẫy tư duy đối nghịch.")

    elif "88 Mô hình" in th_category:
        th_cat_key = "th_models"
        col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
        with col_f1:
            th_scope = st.selectbox(
                "Phạm vi mô hình:",
                [
                    "🌐 Toàn bộ 88 Mô hình (100% đầy đủ)",
                    "⭐ 25 Siêu mô hình Tier 1 Pareto (80/20)",
                    "🎯 37 Mô hình Chiến lược Tier 2",
                    "🔬 26 Mô hình Chuyên sâu Tier 3"
                ],
                key="th_scope_sel"
            )
        with col_f2:
            th_filter_pillar = st.selectbox("Lọc theo Trụ cột", ["Tất cả"] + get_pillars(), key="th_filter_pillar")
        with col_f3:
            th_model_angle = st.selectbox(
                "Góc độ khảo sát:",
                [
                    "🌟 Tất cả các góc độ (Ma trận hỗn hợp)",
                    "🔬 Chân lý gốc (First Principle)",
                    "⚡ Đòn bẩy tối thượng (Elite Leverage)",
                    "⚠️ Bẫy đảo ngược (Inversion Trap)",
                    "🔀 Ma trận Phân biệt Tương hỗ (Discriminative Matrix)"
                ],
                key="th_model_angle_sel"
            )

        tier_map = {
            "🌐 Toàn bộ 88 Mô hình (100% đầy đủ)": None,
            "⭐ 25 Siêu mô hình Tier 1 Pareto (80/20)": 1,
            "🎯 37 Mô hình Chiến lược Tier 2": 2,
            "🔬 26 Mô hình Chuyên sâu Tier 3": 3
        }
        angle_map = {
            "🌟 Tất cả các góc độ (Ma trận hỗn hợp)": "all",
            "🔬 Chân lý gốc (First Principle)": "first_principle",
            "⚡ Đòn bẩy tối thượng (Elite Leverage)": "leverage",
            "⚠️ Bẫy đảo ngược (Inversion Trap)": "inversion",
            "🔀 Ma trận Phân biệt Tương hỗ (Discriminative Matrix)": "matrix"
        }
        p_arg = th_filter_pillar if th_filter_pillar != "Tất cả" else None
        t_arg = tier_map.get(th_scope)
        a_arg = angle_map.get(th_model_angle, "all")

        col_btn, _ = st.columns([2, 4])
        with col_btn:
            if st.button("🎲 Xáo trộn phương án & đề mới", key="btn_shuf_models", use_container_width=True):
                st.session_state["th_shuffle_seed"] = random.randint(1, 999999)
                st.rerun()

        th_selected_questions = get_theory_questions_for_models(
            pillar=p_arg,
            tier=t_arg,
            angle=a_arg,
            seed=st.session_state["th_shuffle_seed"]
        )
        st.info(f"📋 Khoang thi **88 Mô hình Hạt nhân** tìm thấy **{len(th_selected_questions)} câu hỏi lý thuyết**. Khắc sâu Chân lý gốc, Đòn bẩy tối thượng, Bẫy đảo ngược và Ma trận phân biệt mô hình.")

    else:
        th_cat_key = "th_principles"
        col_p1, col_p2, col_p3 = st.columns([2, 2, 2])
        with col_p1:
            th_domain = st.selectbox("Lọc Trụ cột khoa học", get_domains(), key="th_filter_domain")
        with col_p2:
            th_prin_angle = st.selectbox(
                "Góc độ khảo sát:",
                [
                    "🌟 Tất cả các góc độ (Ma trận hỗn hợp)",
                    "🔬 Định nghĩa hình thức & Trực giác",
                    "⚖️ Điều kiện biên nghiệm đúng",
                    "💥 Phép thử bác bỏ (Karl Popper Falsification)",
                    "🔀 Ma trận Phân biệt Nguyên lý"
                ],
                key="th_prin_angle_sel"
            )
        with col_p3:
            if st.button("🎲 Xáo trộn phương án & đề mới", key="btn_shuf_prin", use_container_width=True):
                st.session_state["th_shuffle_seed"] = random.randint(1, 999999)
                st.rerun()

        angle_p_map = {
            "🌟 Tất cả các góc độ (Ma trận hỗn hợp)": "all",
            "🔬 Định nghĩa hình thức & Trực giác": "definition",
            "⚖️ Điều kiện biên nghiệm đúng": "boundary",
            "💥 Phép thử bác bỏ (Karl Popper Falsification)": "falsification",
            "🔀 Ma trận Phân biệt Nguyên lý": "matrix"
        }
        d_arg = th_domain if th_domain != "Tất cả" else None
        a_p_arg = angle_p_map.get(th_prin_angle, "all")

        th_selected_questions = get_theory_questions_for_principles(
            domain=d_arg,
            angle=a_p_arg,
            seed=st.session_state["th_shuffle_seed"]
        )
        st.info(f"📋 Khoang thi **100 Nguyên lý Khởi thủy** tìm thấy **{len(th_selected_questions)} câu hỏi khoa học**. Khắc sâu định nghĩa hình thức, điều kiện biên, tính khả bác và ma trận nhận diện nguyên lý.")

    th_score = 0
    th_answered = 0

    # Slider to choose how many questions to display
    if len(th_selected_questions) > 10:
        default_lim = min(25, len(th_selected_questions))
        th_max_display = st.slider(
            "Số lượng câu hỏi kiểm tra đợt này:",
            min_value=5,
            max_value=len(th_selected_questions),
            value=default_lim,
            step=5 if len(th_selected_questions) <= 100 else 10,
            key=f"th_slider_limit_{th_cat_key}"
        )
        th_display_questions = th_selected_questions[:th_max_display]
    else:
        th_display_questions = th_selected_questions

    for i, q in enumerate(th_display_questions):
        q_title = q.get('concept') or q.get('model_name') or q.get('principle_name') or f"Câu {i+1}"
        q_angle_tag = q.get('angle_label', '')
        exp_header = f"Câu {i+1}: {q_title}"
        if q_angle_tag:
            exp_header += f" · [{q_angle_tag}]"

        with st.expander(exp_header, expanded=(i < 2)):
            st.markdown(f"**❓ Câu hỏi lý thuyết:** **{q.get('question')}**")

            th_state_key = f"th_ans_{th_cat_key}_{q.get('id')}_{st.session_state.get('th_shuffle_seed', 42)}"
            th_user_choice = st.radio(
                "Chọn đáp án chính xác:",
                q.get("options", []),
                key=th_state_key,
                index=None
            )

            if th_user_choice is not None:
                th_answered += 1
                th_chosen_idx = q["options"].index(th_user_choice)
                th_is_correct = (th_chosen_idx == q["correct_index"])

                if th_is_correct:
                    th_score += 1
                    st.success("🎉 **CHÍNH XÁC!** Bạn đã nắm rất rành mạch lý thuyết cốt lõi này.")
                else:
                    st.error(f"❌ **CHƯA CHÍNH XÁC!** Đáp án chuẩn là: **{q['options'][q['correct_index']]}**")

                st.markdown(f"💡 **Chân lý gốc / Định nghĩa cốt lõi:** {q.get('explanation')}")
                st.markdown(f"⚠️ **Bẫy ngụy biện & Ranh giới điều kiện biên:** {q.get('trap_analysis')}")

    st.divider()
    c_thr1, c_thr2 = st.columns([2, 1])
    with c_thr1:
        if th_answered > 0:
            th_pct = round(th_score / th_answered * 100, 1)
            st.markdown(f"#### 📊 Kết quả trắc nghiệm lý thuyết: **{th_score}/{th_answered} câu đúng ({th_pct}%)**")
        else:
            st.caption("Hãy chọn đáp án cho các câu hỏi lý thuyết phía trên để kiểm tra kết quả.")
    with c_thr2:
        if th_answered > 0 and st.button("💾 Ghi nhận lượt thi lý thuyết vào Lịch sử", type="primary", use_container_width=True, key="btn_save_th_quiz"):
            record_quiz_completion(username, f"Lý thuyết: {th_category}", th_score, th_answered)
            st.success("🎉 Đã lưu kết quả thi lý thuyết vào Lịch sử cá nhân! Tăng cường điểm số Mastery.")
            st.rerun()

# -------------------------------------------------------------------------
# Sub-tab 2: Trắc Nghiệm Tình Huống Thực Chiến
# -------------------------------------------------------------------------
with arena_tab1:
    st.markdown("### 🎯 Trắc Nghiệm Tình Huống Phản Xạ (Case-Based Reflex Quiz)")
    st.caption("Mỗi câu hỏi là một tình huống thực tế hóc búa. Đọc tình huống, chọn mô hình chi phối và giải mã bẫy ngụy biện.")

    quiz_category = st.radio(
        "Chọn khoang bài thi trắc nghiệm",
        [
            "🧠 9 Chế độ Tư duy Tinh hoa (9 tình huống kinh điển)",
            "🕸️ 88 Mô hình Hạt nhân (Munger Latticework)",
            "🔬 100 Nguyên lý Khởi thủy (Quy luật khoa học nền tảng)"
        ],
        horizontal=True
    )

    selected_questions = []
    cat_key = ""
    if "9 Chế độ" in quiz_category:
        selected_questions = MODES_QUIZ
        cat_key = "modes"
    elif "88 Mô hình" in quiz_category:
        cat_key = "models"
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            filter_pillar = st.selectbox("Lọc theo Trụ cột", ["Tất cả"] + get_pillars())
        with col_q2:
            only_tier1 = st.checkbox("Chỉ luyện 25 Mô hình Siêu hạt nhân (Tier 1 Pareto)", value=True)

        filtered_q = MODELS_QUIZ
        if filter_pillar != "Tất cả":
            filtered_q = [q for q in filtered_q if q.get("pillar") == filter_pillar]
        if only_tier1:
            filtered_q = [q for q in filtered_q if q.get("tier") == 1]
        selected_questions = filtered_q if filtered_q else MODELS_QUIZ
    else:
        cat_key = "principles"
        selected_questions = PRINCIPLES_QUIZ

    st.info(f"📋 Khoang thi hiện có **{len(selected_questions)} câu hỏi tình huống**. Hãy đọc kỹ tình huống để tìm ra bản chất:")

    quiz_score = 0
    answered_count = 0

    for i, q in enumerate(selected_questions):
        with st.expander(f"Câu {i+1}: {q.get('concept', q.get('model_name', q.get('principle_name', 'Tình huống')))}", expanded=(i < 2)):
            st.markdown(f"**📖 Bối cảnh tình huống:**\n> *{q.get('scenario')}*")
            st.markdown(f"**❓ Câu hỏi:** **{q.get('question')}**")

            state_key = f"quiz_ans_{cat_key}_{q.get('id')}"
            user_choice = st.radio(
                "Chọn phương án trả lời:",
                q.get("options", []),
                key=state_key,
                index=None
            )

            if user_choice is not None:
                answered_count += 1
                chosen_idx = q["options"].index(user_choice)
                is_correct = (chosen_idx == q["correct_index"])

                if is_correct:
                    quiz_score += 1
                    st.success("🎉 **CHÍNH XÁC TUYỆT ĐỐI!** Bạn đã nhìn xuyên qua bề mặt để chạm vào bản chất gốc.")
                else:
                    st.error(f"❌ **CHƯA CHÍNH XÁC!** Đáp án đúng là: **{q['options'][q['correct_index']]}**")

                st.markdown(f"💡 **Chân lý gốc (First Principles):** {q.get('explanation')}")
                st.markdown(f"⚠️ **Phân tích Bẫy ngụy biện:** {q.get('trap_analysis')}")

    st.divider()
    col_res1, col_res2 = st.columns([2, 1])
    with col_res1:
        if answered_count > 0:
            pct = round(quiz_score / answered_count * 100, 1)
            st.markdown(f"#### 📊 Kết quả tạm tính: **{quiz_score}/{answered_count} câu đúng ({pct}%)**")
        else:
            st.caption("Hãy chọn đáp án cho các câu hỏi phía trên để tính điểm.")
    with col_res2:
        if answered_count > 0 and st.button("💾 Ghi nhận lượt thi vào Lịch sử cá nhân", type="primary", use_container_width=True):
            record_quiz_completion(username, quiz_category, quiz_score, answered_count)
            st.success("🎉 Đã lưu thành tích vào Lịch sử của bạn! Cập nhật lại chỉ số Mastery.")
            st.rerun()

# -------------------------------------------------------------------------
# Sub-tab 2: Thẻ Flashcards Phản Xạ 5 Giây (Active Recall)
# -------------------------------------------------------------------------
with arena_tab2:
    st.markdown("### 🗂️ Thẻ Flashcards Phản Xạ 5 Giây (Active Recall & Spaced Repetition)")
    st.caption("Phương pháp ghi nhớ đỉnh cao: Đọc câu hỏi kích hoạt 5 giây ➔ Lật thẻ đối chiếu ➔ Tự đánh giá để hệ thống vẽ biểu đồ trí nhớ.")

    fc_col1, fc_col2, fc_col3 = st.columns([2, 2, 1])
    with fc_col1:
        fc_cat = st.selectbox("Bộ thẻ", ["88 Mô hình Hạt nhân", "9 Chế độ Tư duy", "100 Nguyên lý Khởi thủy", "Tất cả thẻ"])
    with fc_col2:
        fc_filter_pillar = "Tất cả"
        if "88 Mô hình" in fc_cat:
            fc_filter_pillar = st.selectbox("Lọc Trụ cột", ["Tất cả"] + get_pillars())
    with fc_col3:
        fc_tier = None
        if "88 Mô hình" in fc_cat:
            if st.checkbox("Tier 1 Pareto", value=False):
                fc_tier = 1

    filter_type_map = {
        "88 Mô hình Hạt nhân": "models",
        "9 Chế độ Tư duy": "modes",
        "100 Nguyên lý Khởi thủy": "principles",
        "Tất cả thẻ": "all"
    }
    raw_cards = get_all_flashcards(
        filter_type=filter_type_map.get(fc_cat, "models"),
        pillar=fc_filter_pillar if fc_filter_pillar != "Tất cả" else None,
        tier=fc_tier
    )

    if not raw_cards:
        st.warning("Không tìm thấy thẻ nào phù hợp với bộ lọc.")
    else:
        if "fc_card_idx" not in st.session_state:
            st.session_state["fc_card_idx"] = 0
        if "fc_is_flipped" not in st.session_state:
            st.session_state["fc_is_flipped"] = False

        total_c = len(raw_cards)
        curr_idx = st.session_state["fc_card_idx"] % total_c
        card = raw_cards[curr_idx]

        st.caption(f"Thẻ **{curr_idx + 1} / {total_c}** · {card.get('front_badge')}")

        # Giao diện Thẻ lật
        with st.container(border=True):
            if not st.session_state["fc_is_flipped"]:
                st.markdown(f"## ❓ {card.get('name_vi')} *({card.get('name_en', '')})*")
                st.markdown(f"### ⚡ Câu hỏi kích hoạt 5 giây:\n> **\"{card.get('front_trigger')}\"**")
                st.caption("💭 Hãy nhắm mắt lại 5 giây: Bạn có định nghĩa được chân lý gốc, đòn bẩy và bẫy đảo ngược của mô hình này không?")
                
                if st.button("🔄 Lật thẻ xem Chân lý gốc & Đòn bẩy Elite", type="primary", use_container_width=True):
                    st.session_state["fc_is_flipped"] = True
                    st.rerun()
            else:
                st.markdown(f"## 💡 {card.get('name_vi')} *({card.get('name_en', '')})*")
                st.info(f"🔬 **Chân lý gốc (First Principle):**\n\n{card.get('back_principle')}")
                st.success(f"⚡ **Đòn bẩy Elite:**\n\n{card.get('back_leverage')}")
                st.warning(f"⚠️ **Bẫy đảo ngược (Inversion Trap):**\n\n{card.get('back_trap')}")
                if card.get("back_lollapalooza"):
                    st.caption(f"🔗 **Cặp cộng hưởng Lollapalooza:** {card.get('back_lollapalooza')}")

                st.markdown("#### Tự đánh giá mức độ ghi nhớ:")
                btn_c1, btn_c2, btn_c3 = st.columns(3)
                with btn_c1:
                    if st.button("🔴 Chưa nhớ (Cần ôn lại)", use_container_width=True):
                        update_flashcard_mastery(username, card.get("id"), "review_needed")
                        st.session_state["fc_is_flipped"] = False
                        st.session_state["fc_card_idx"] = (curr_idx + 1) % total_c
                        st.rerun()
                with btn_c2:
                    if st.button("🟡 Nhớ mang máng", use_container_width=True):
                        update_flashcard_mastery(username, card.get("id"), "learning")
                        st.session_state["fc_is_flipped"] = False
                        st.session_state["fc_card_idx"] = (curr_idx + 1) % total_c
                        st.rerun()
                with btn_c3:
                    if st.button("🟢 Đã thuộc làu (Mastered)", type="primary", use_container_width=True):
                        update_flashcard_mastery(username, card.get("id"), "mastered")
                        st.session_state["fc_is_flipped"] = False
                        st.session_state["fc_card_idx"] = (curr_idx + 1) % total_c
                        st.rerun()

                if st.button("🔄 Úp thẻ lại mặt trước", use_container_width=True):
                    st.session_state["fc_is_flipped"] = False
                    st.rerun()

        # Điều hướng thẻ
        nav_c1, nav_c2, nav_c3 = st.columns([1, 1, 1])
        with nav_c1:
            if st.button("⬅️ Thẻ trước", use_container_width=True):
                st.session_state["fc_is_flipped"] = False
                st.session_state["fc_card_idx"] = (curr_idx - 1) % total_c
                st.rerun()
        with nav_c2:
            if st.button("🎲 Thẻ ngẫu nhiên", use_container_width=True):
                st.session_state["fc_is_flipped"] = False
                st.session_state["fc_card_idx"] = random.randint(0, total_c - 1)
                st.rerun()
        with nav_c3:
            if st.button("Thẻ tiếp theo ➡️", use_container_width=True):
                st.session_state["fc_is_flipped"] = False
                st.session_state["fc_card_idx"] = (curr_idx + 1) % total_c
                st.rerun()

# -------------------------------------------------------------------------
# Sub-tab 3: AI Đấu Trí & Thử Thách Feynman
# -------------------------------------------------------------------------
with arena_tab3:
    st.markdown("### ✨ AI Đấu Trí & Thử Thách Feynman")
    st.caption("Khắc sâu bản chất bằng cách giải thích cho đứa trẻ 10 tuổi hiểu hoặc yêu cầu AI tạo đề thi tình huống mới toanh.")

    ai_sec1, ai_sec2 = st.tabs(["✨ AI Tạo Đề Trắc Nghiệm Động", "🔬 Thử Thách Feynman (Socratic Arena)"])

    with ai_sec1:
        st.markdown("#### 🎲 AI Tự Động Sinh Đề Trắc Nghiệm Tình Huống Mới Toanh")
        st.caption("Không bị gò bó bởi các câu hỏi có sẵn; AI Gemini sẽ tạo câu hỏi theo tình huống đời thực bạn đưa vào.")

        ai_col1, ai_col2 = st.columns(2)
        with ai_col1:
            ai_quiz_cat = st.selectbox(
                "Loại mô hình cần kiểm tra",
                ["88 Mô hình Hạt nhân (Charlie Munger)", "9 Chế độ Tư duy Tinh hoa", "100 Nguyên lý Khởi thủy"]
            )
            ai_quiz_num = st.slider("Số lượng câu hỏi", 2, 5, 3)
        with ai_col2:
            ai_quiz_topic = st.text_input(
                "Chủ đề / Bối cảnh thực tế mong muốn",
                value="Thị trường chứng khoán Việt Nam, Bắt đáy cổ phiếu & FOMO đám đông",
                help="Gõ bất kỳ chủ đề nào: Khởi nghiệp SaaS, Học sinh Wellspring giải quyết bài tập, Quản trị sa thải..."
            )

        if st.button("🚀 AI Tạo Đề Thi Tình Huống Ngay", type="primary", use_container_width=True):
            if not active_keys:
                st.warning("Cần cấu hình Gemini API Key.")
            else:
                with st.spinner("AI đang thiết kế các tình huống thực tế hóc búa..."):
                    generated_quiz = generate_ai_quiz(
                        active_keys,
                        model_choice,
                        category=ai_quiz_cat,
                        topic=ai_quiz_topic.strip(),
                        num_questions=ai_quiz_num
                    )
                if generated_quiz:
                    st.session_state["current_ai_quiz"] = generated_quiz
                    st.success(f"🎉 Đã sinh thành công {len(generated_quiz)} câu hỏi tình huống mới toanh!")
                else:
                    st.error("Không thể sinh câu hỏi bằng AI lúc này. Vui lòng kiểm tra lại API Key.")

        if "current_ai_quiz" in st.session_state and st.session_state["current_ai_quiz"]:
            st.markdown("---")
            st.markdown("#### 📝 Đề Thi Tình Huống Do AI Thiết Kế:")
            for idx, q_ai in enumerate(st.session_state["current_ai_quiz"]):
                with st.expander(f"Tình huống {idx+1}: {q_ai.get('concept')}", expanded=True):
                    st.markdown(f"**📖 Bối cảnh:**\n> *{q_ai.get('scenario')}*")
                    st.markdown(f"**❓ Câu hỏi:** **{q_ai.get('question')}**")

                    choice = st.radio("Lựa chọn của bạn:", q_ai.get("options", []), key=f"ai_q_{idx}", index=None)
                    if choice is not None:
                        c_idx = q_ai["options"].index(choice)
                        if c_idx == q_ai.get("correct_index"):
                            st.success("🎉 **CHÍNH XÁC!** Bạn đã nhận diện chuẩn xác mô hình.")
                        else:
                            st.error(f"❌ **CHƯA ĐÚNG!** Đáp án chuẩn: {q_ai['options'][q_ai.get('correct_index')]}")
                        st.info(f"💡 **First Principles:** {q_ai.get('explanation')}")
                        st.warning(f"⚠️ **Bẫy ngụy biện:** {q_ai.get('trap_analysis')}")

    with ai_sec2:
        st.markdown("#### 🔬 Thử Thách Kỹ Thuật Feynman: 'Giải thích cho học sinh lớp 6 hiểu'")
        st.markdown("""
        > *"Bạn không thực sự hiểu điều gì cho đến khi bạn có thể giải thích nó bằng ngôn ngữ đơn giản nhất cho một đứa trẻ 10 tuổi mà không dùng bất kỳ từ ngữ cao siêu nào."* — **Richard Feynman**
        """)

        fey_col1, fey_col2 = st.columns([1, 2])
        with fey_col1:
            concept_source = st.radio("Khái niệm từ nguồn", ["88 Mô hình Hạt nhân", "9 Chế độ Tư duy"])
            if "88 Mô hình" in concept_source:
                all_m = get_all_models()
                m_names = [f"{m['name_vi']} ({m['name_en']})" for m in all_m]
                chosen_concept = st.selectbox("Chọn mô hình", m_names)
                c_type = "Mô hình Hạt nhân"
            else:
                mode_names = [q["concept"] for q in MODES_QUIZ]
                chosen_concept = st.selectbox("Chọn chế độ", mode_names)
                c_type = "Chế độ Tư duy Elite"

        with fey_col2:
            user_feynman_exp = st.text_area(
                f"Lời giải thích của bạn về '{chosen_concept}' cho một đứa trẻ:",
                height=130,
                placeholder="Hãy dùng một ví dụ trong đồ chơi, đời sống gia đình, trường học... Tuyệt đối không dùng các thuật ngữ chuyên môn."
            )

            if st.button("🎯 Nộp bài cho Giám khảo Feynman chấm điểm", type="primary", use_container_width=True):
                if not active_keys:
                    st.warning("Cần cấu hình Gemini API Key.")
                elif not user_feynman_exp.strip():
                    st.warning("Hãy nhập lời giải thích của bạn.")
                else:
                    with st.spinner("Richard Feynman AI đang lắng nghe và phản biện..."):
                        fey_res = evaluate_feynman_challenge(
                            active_keys,
                            model_choice,
                            concept_name=chosen_concept,
                            concept_type=c_type,
                            user_explanation=user_feynman_exp.strip()
                        )
                    if fey_res:
                        score = fey_res.get("feynman_score", 5)
                        verdict = fey_res.get("verdict", "")
                        st.metric("🏆 Điểm Thấu Suốt Feynman", f"{score} / 10", verdict)

                        st.success(f"✨ **Điểm sáng:** {fey_res.get('praise')}")
                        st.warning(f"🔍 **Điểm mù / Lỗ hổng:** {fey_res.get('blind_spots')}")
                        st.info(f"💡 **Phiên bản Richard Feynman giải thích:**\n\n> *\"{fey_res.get('feynman_refinement')}\"*")
                    else:
                        st.error("Không thể kết nối với AI. Vui lòng thử lại.")

