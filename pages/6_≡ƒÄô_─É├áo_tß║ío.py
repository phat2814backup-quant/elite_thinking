# -*- coding: utf-8 -*-
"""Đào tạo tư duy"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.daily_workout import (
    DAILY_WORKOUT_BANK,
    get_today_workout,
    get_user_streak_info,
    record_daily_workout_answer,
    evaluate_daily_workout,
)
from utils.training import (
    load_lessons,
    get_lessons_by_grade,
    get_lesson,
    get_tracks_meta,
    get_lessons_by_track,
)
from utils.ai_engine import feedback_on_answer, generate_dynamic_lesson

st.title("🎓 Đào tạo tư duy theo lộ trình đa tầng")
st.caption("Hệ thống rèn luyện phản xạ 15 phút mỗi ngày kèm lộ trình 3 cấp độ cho K12 Wellspring & Người lớn.")

tab6_subtabs = st.tabs([
    "🔥 Elite Daily Workout (15 Phút Hàng Ngày & Streak)",
    "📚 Lộ Trình Đào Tạo Theo Cấp Độ (K12 & Người Lớn)",
])

# -------------------------------------------------------------------------
# Sub-tab 0: Elite Daily Workout
# -------------------------------------------------------------------------
with tab6_subtabs[0]:
    st.markdown("### 🔥 Elite Daily Workout — Rèn Luyện Phản Xạ 15 Phút Mỗi Ngày")
    st.caption("Nguyên lý Chuỗi Hạt (Seinfeld Streak): Mỗi ngày 1 tình huống thực chiến · 3 bước phân rã chuẩn Elite · Cài đặt tư duy vào tầng tiềm thức sau 90 ngày.")

    u_streak = get_user_streak_info(username)
    s_count = u_streak["current_streak"]
    s_status = "⚡ Đang khởi động" if s_count < 7 else ("🔥 Thói quen thép" if s_count < 30 else "🏆 Phản xạ vô thức")

    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    with w_col1:
        st.metric("🔥 Chuỗi Streak", f"{s_count} ngày", s_status)
    with w_col2:
        st.metric("🏆 Kỷ lục chuỗi", f"{u_streak['longest_streak']} ngày")
    with w_col3:
        st.metric("📝 Đã hoàn thành", f"{u_streak['total_completed']} bài")
    with w_col4:
        if u_streak["is_done_today"]:
            st.success("✅ Hôm nay: Đã xong!")
        else:
            st.warning("⏳ Hôm nay: Chưa làm")

    st.divider()

    w_track = st.radio(
        "Chọn chủ đề bài tập hôm nay:",
        ["all", "k12", "adult"],
        format_func=lambda x: "🌐 Đa Lĩnh Vực / Tổng Hợp" if x == "all" else ("🎒 Học Sinh Wellspring (K12)" if x == "k12" else "💼 Chuyên Sâu Người Lớn"),
        horizontal=True,
        key="dw_track_filter",
    )

    today_workout = get_today_workout(track=w_track)

    st.markdown(f"#### 🎯 Bài Tập Hôm Nay: {today_workout['title']}")
    st.info(f"**Tình huống thực tế:**\n\n{today_workout['scenario']}")
    st.caption("Các nguyên lý / mô hình định hướng: " + " · ".join([f"`{p}`" for p in today_workout.get('guiding_principles', [])]))

    with st.form(key=f"form_dw_{today_workout['id']}"):
        st.markdown(f"##### 1️⃣ {today_workout['step1_prompt']}")
        dw_ans_step1 = st.text_area(
            "Phân tích Sự thật vs Ý kiến:",
            height=90,
            placeholder="Chỉ ra rõ: Sự thật đo lường được là gì? Điều gì chỉ là ý kiến, phỏng đoán hoặc cảm xúc đám đông?",
            key="dw_step1_input",
        )

        st.markdown(f"##### 2️⃣ {today_workout['step2_prompt']}")
        dw_ans_step2 = st.text_area(
            "Chiếu lăng kính mô hình hạt nhân:",
            height=90,
            placeholder="Gọi tên chính xác mô hình hạt nhân (Tâm lý, Vật lý, Kinh tế) đang chi phối tình huống này và cơ chế của nó...",
            key="dw_step2_input",
        )

        st.markdown(f"##### 3️⃣ {today_workout['step3_prompt']}")
        dw_ans_step3 = st.text_area(
            "Đề xuất hành động bất đối xứng:",
            height=90,
            placeholder="Nếu ở vị thế người trong cuộc, nước cờ tối ưu nào giúp hạn chế tối đa rủi ro tổn thất và đón đầu thặng dư lớn nhất?",
            key="dw_step3_input",
        )

        submit_dw = st.form_submit_button("🔥 Hoàn Tất 15 Phút & Nhận Phản Hồi AI Mentor", type="primary", use_container_width=True)

    if submit_dw:
        if not dw_ans_step1.strip() or not dw_ans_step2.strip() or not dw_ans_step3.strip():
            st.warning("Vui lòng hoàn thành đủ cả 3 bước để bài tập đạt hiệu quả rèn luyện tối đa.")
        else:
            with st.spinner("AI Mentor đang đánh giá bài tập 15 phút của bạn..."):
                ai_dw_feedback = evaluate_daily_workout(
                    active_keys,
                    model_choice,
                    today_workout,
                    dw_ans_step1.strip(),
                    dw_ans_step2.strip(),
                    dw_ans_step3.strip(),
                )
            
            rec_res = record_daily_workout_answer(
                username=username,
                workout_id=today_workout["id"],
                workout_title=today_workout["title"],
                step1_ans=dw_ans_step1.strip(),
                step2_ans=dw_ans_step2.strip(),
                step3_ans=dw_ans_step3.strip(),
                ai_feedback=ai_dw_feedback,
            )

            st.balloons()
            st.success(f"🎉 Xuất sắc! Bạn đã duy trì chuỗi Streak lên **{rec_res['current_streak']} ngày liên tục**!")
            
            st.markdown("#### 🌟 Nhận Xét Phản Biện Từ AI Mentor:")
            st.info(ai_dw_feedback)

            with st.expander("💡 Xem Gợi Ý Tinh Hoa của Bậc Thầy (Elite Hint)", expanded=True):
                st.write(today_workout.get("elite_hint", ""))

    history_dw = u_streak.get("history", [])
    if history_dw:
        with st.expander(f"📜 Xem Lịch Sử {len(history_dw)} Bài Tập Daily Workout Đã Hoàn Thành"):
            for h_item in history_dw[:10]:
                st.markdown(f"**🗓️ {h_item.get('date')} — {h_item.get('title')}**")
                st.caption(f"Bước 1: {h_item.get('step1')[:100]}...")
                if h_item.get("ai_feedback"):
                    st.caption(f"AI Mentor: {h_item.get('ai_feedback')[:150]}...")
                st.markdown("---")

# -------------------------------------------------------------------------
# Sub-tab 1: Lộ Trình Đào Tạo Theo Cấp Độ
# -------------------------------------------------------------------------
with tab6_subtabs[1]:
    user_group = st.radio(
        "Chọn nhóm đối tượng đào tạo",
        ["🎒 Học sinh Wellspring (Lớp 6, 9, 10)", "💼 Chuyên sâu Người lớn (Trading, CKVN, Não bộ, Phật giáo, AI)"],
        horizontal=True,
    )

    tracks_meta = get_tracks_meta()

    if "Học sinh Wellspring" in user_group:
        track_options = {
            "grade_6": "Lớp 6 (Wellspring) — Khởi đầu tự chủ & AI cơ bản",
            "grade_9": "Lớp 9 (Wellspring) — Tư duy phản biện & Chọn hướng đi",
            "grade_10": "Lớp 10 (Wellspring) — Chiến lược dự án & Đòn bẩy AI",
        }
    else:
        track_options = {
            "trading": "Trading Vàng, FX, Crypto/BTC — Xác suất & Quản trị rủi ro",
            "ckvn": "Đầu tư Chứng khoán VN — Chu kỳ & Dòng tiền Smart Money",
            "neuroscience": "Khoa học Não bộ & Nhận thức — Dopamine & Khắc phục thiên kiến",
            "buddhism": "Phật giáo & Tâm thức — Vô thường & Chánh niệm ra quyết định",
            "ai_tech": "Công nghệ AI & Tương lai — Đòn bẩy không cần xin phép",
        }

    c_sel1, c_sel2 = st.columns([3, 2])
    with c_sel1:
        sel_track_id = st.selectbox(
            "Khóa học / Chủ đề đào tạo",
            options=list(track_options.keys()),
            format_func=lambda x: track_options.get(x, x),
        )
    with c_sel2:
        level_choice = st.selectbox(
            "Trình độ rèn luyện",
            ["🌱 Cấp 1: Nền tảng (Foundation)", "🔥 Cấp 2: Thực hành (Practice)", "👑 Cấp 3: Nhuần nhuyễn (Mastery)"],
            index=0,
        )

    track_info = tracks_meta.get(sel_track_id, {})
    if track_info.get("desc"):
        st.caption(f"💡 *Mục tiêu khóa:* {track_info['desc']}")

    level_map = {
        "🌱 Cấp 1: Nền tảng (Foundation)": ("level_1", "Cơ bản"),
        "🔥 Cấp 2: Thực hành (Practice)": ("level_2", "Thực hành"),
        "👑 Cấp 3: Nhuần nhuyễn (Mastery)": ("level_3", "Nâng cao"),
    }
    sel_level_code, sel_level_name = level_map[level_choice]

    # Lấy danh sách bài học thuộc track và level đã chọn
    lessons = get_lessons_by_track(sel_track_id, sel_level_code)

    hist = load_user_history(username)
    user_training = hist.get("training", {})
    done_count = sum(1 for l in lessons if l["id"] in user_training)
    total_count = len(lessons)

    # Thanh trạng thái tiến độ cấp độ
    c_p1, c_p2 = st.columns([3, 1])
    with c_p1:
        st.progress(done_count / max(total_count, 1))
    with c_p2:
        st.caption(f"Tiến độ cấp độ: **{done_count}/{total_count}** bài")

    # Sub-tabs tách bạch rõ ràng giữa Lộ trình bài tập và AI Mentor sinh bài tập
    sub_train_labels = [
        f"📖 Lộ trình Bài tập ({total_count} bài)",
        "✨ AI Mentor: Tự động tạo bài tập mở rộng",
    ]
    sub_train_tabs = st.tabs(sub_train_labels)

    with sub_train_tabs[0]:
        if not lessons:
            st.warning(f"Chưa có bài tập nào trong `{track_options[sel_track_id]}` ({sel_level_name}).")
            st.info("👉 Hãy bấm sang tab **'✨ AI Mentor: Tự động tạo bài tập mở rộng'** bên cạnh để AI tạo bài tập đầu tiên cho bạn!")
        else:
            def format_lesson_title(l: dict) -> str:
                done_icon = "✅" if l["id"] in user_training else "📖"
                is_ai = " [✨ AI]" if l.get("created_by") == "AI" or "_ai_" in l.get("id", "") else ""
                return f"{done_icon} {l.get('title', l['id'])} — ({l.get('mode', '')}){is_ai}"

            # Tự động chọn bài vừa tạo nếu có trong session
            target_id = st.session_state.get(f"target_lesson_{sel_track_id}_{sel_level_code}")
            default_index = 0
            if target_id:
                for idx, l in enumerate(lessons):
                    if l.get("id") == target_id:
                        default_index = idx
                        break

            choice = st.selectbox(
                f"📚 Danh sách bài tập khả dụng ({len(lessons)} bài)",
                options=lessons,
                index=default_index,
                format_func=format_lesson_title,
                key=f"sel_lesson_{sel_track_id}_{sel_level_code}",
            )
            lesson = choice

            st.subheader(lesson["title"])
            st.caption(f"Chế độ: **{lesson.get('mode')}** · Mức: **{lesson.get('level')}** · ID: `{lesson.get('id')}`")
            if lesson.get("related_principle"):
                st.caption(f"Nguyên lý cốt lõi: **{lesson['related_principle']}**")

            st.markdown(f"**Mục tiêu:** {lesson.get('objective')}")
            st.markdown("#### Tình huống thực tế")
            st.info(lesson.get("situation", ""))

            st.markdown("#### Các bước hướng dẫn tư duy")
            for i, step in enumerate(lesson.get("guide_steps", []), 1):
                st.markdown(f"{i}. {step}")

            with st.expander("💡 Gợi ý định hướng (mở khi cần)"):
                st.write(lesson.get("hint", ""))

            st.markdown("#### Thử thách của bạn")
            st.write(lesson.get("exercise_prompt", ""))

            # Load previous answer if any
            prev = user_training.get(lesson["id"], {})
            prev_answer = prev.get("answer", "")
            prev_feedback = prev.get("feedback", "")

            answer = st.text_area("Câu trả lời của bạn", value=prev_answer, height=150, key=f"ans_{lesson['id']}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("💾 Lưu câu trả lời", use_container_width=True, key=f"save_{lesson['id']}"):
                    save_training_answer(username, lesson["id"], answer.strip())
                    st.success("Đã lưu vào tiến độ cá nhân của bạn.")
                    st.rerun()
            with col_b:
                if st.button("🤖 Xin feedback AI", type="primary", use_container_width=True, key=f"fb_{lesson['id']}"):
                    if not answer.strip():
                        st.warning("Hãy viết câu trả lời trước khi xin feedback.")
                    elif not active_keys:
                        st.warning("Cần API Key để nhận feedback.")
                    else:
                        with st.spinner("AI Gia sư đang nhận xét và hiệu chỉnh tư duy (tự động xoay tua key)..."):
                            fb = feedback_on_answer(active_keys, model_choice, lesson, answer.strip())
                        save_training_answer(username, lesson["id"], answer.strip(), fb)
                        st.rerun()

            if prev_feedback:
                st.markdown("#### Feedback từ AI Mentor")
                st.success(prev_feedback)

            st.divider()
            st.info("💡 **Muốn rèn luyện thêm?** Bạn có thể bấm sang tab **'✨ AI Mentor: Tự động tạo bài tập mở rộng'** ở trên để yêu cầu thêm các tình huống thực tế khác không giới hạn!")

    with sub_train_tabs[1]:
        st.subheader(f"✨ AI Mentor: Tự Động Thiết Kế Bài Tập Thực Chiến")
        st.markdown(f"Tạo đề bài độc bản cho: **{track_options[sel_track_id]}** · Cấp độ: **{sel_level_name}**")

        quick_suggestions = {
            "grade_6": [
                "Lập kế hoạch tự học tại nhà không bị xao nhãng",
                "Xung đột ý kiến khi làm bài tập nhóm môn Khoa học",
                "Bị phân tâm vì xem video ngắn TikTok/Reels quá nhiều",
                "Phân biệt tin tức thật và tin giả trên mạng xã hội",
            ],
            "grade_9": [
                "Chọn trường cấp 3 công lập hay quốc tế dựa trên năng lực và tài chính",
                "Quản lý áp lực thi cử và kỳ vọng điểm số từ gia đình",
                "Tư duy xác suất và tỷ lệ cơ sở khi giải bài thi trắc nghiệm",
                "Từ chối lời rủ rê trốn học của bạn bè mà không làm mất lòng",
            ],
            "grade_10": [
                "Thiết kế dự án CLB trường học tạo tác động xã hội với ngân sách 0 đồng",
                "Xây dựng hồ sơ ngoại khóa săn học bổng du học bằng First Principles",
                "Ứng dụng AI vào học tập hiệu quả mà không bị thụ động tư duy",
                "Cân bằng giữa ôn luyện IELTS 8.0 và làm trưởng ban tổ chức sự kiện",
            ],
            "trading": [
                "Quản trị tâm lý và lệnh khi Vàng biến động 50 giá trong phiên Mỹ",
                "Chiến lược bất đối xứng (Asymmetry) khi giao dịch BTC/Crypto",
                "Cắt lỗ dứt khoát khi phân tích sai và tránh bẫy Revenge Trading",
                "Quản lý vốn theo tiêu chuẩn Kelly khi hệ thống có Winrate 45%",
            ],
            "ckvn": [
                "Nhận diện dấu chân dòng tiền Smart Money (VSA) ở vùng đáy gom hàng",
                "Phân tích chu kỳ nhóm ngành Chứng khoán - Thép - Bất động sản",
                "Quản trị rủi ro khi thị trường phân phối đỉnh với thanh khoản kỷ lục",
                "Định giá thực chất doanh nghiệp dựa trên dòng tiền tự do FCF",
            ],
            "neuroscience": [
                "Cơ chế Dopamine và cách cai nghiện dopamine rẻ tiền (Cheap Dopamine)",
                "Thực hành Deep Work 90 phút vượt qua quán tính trì hoãn của não bộ",
                "Tái cấu trúc nhận thức (Cognitive Reframing) khi gặp stress cực đại",
                "Khắc phục thiên kiến xác nhận khi đánh giá một cơ hội đầu tư",
            ],
            "buddhism": [
                "Ứng dụng tư duy Vô thường để không bị dính mắc vào thành công/thất bại",
                "Quan sát cảm xúc bằng Chánh niệm trước khi bấm nút Enter vào lệnh",
                "Bản chất Nhân - Quả trong các mối quan hệ gia đình và đối tác",
                "Tâm bất biến giữa dòng đời vạn biến: Quản trị sự bất định của thị trường",
            ],
            "ai_tech": [
                "Xây dựng Agentic Workflow tự động hóa quy trình phân tích dữ liệu",
                "Tư duy đòn bẩy không cần xin phép (Permissionless Leverage) thời AI",
                "Thiết kế Prompt First Principles để giải quyết bài toán kỹ thuật phức tạp",
                "Định vị năng lực cạnh tranh cốt lõi của con người khi AI làm chủ ngôn ngữ",
            ]
        }

        curr_suggestions = quick_suggestions.get(sel_track_id, ["Tình huống thực tế tùy biến theo chuyên môn"])
        sel_suggest = st.selectbox(
            "💡 Gợi ý chủ đề nhanh (chọn hoặc tự nhập bên dưới):",
            ["— Tự nhập tình huống riêng của bạn —"] + curr_suggestions,
            key=f"sel_sug_{sel_track_id}_{sel_level_code}",
        )
        initial_topic = "" if sel_suggest.startswith("—") else sel_suggest

        custom_topic = st.text_input(
            "Chủ đề hoặc tình huống bạn muốn AI ra đề thử thách:",
            value=initial_topic,
            placeholder="vd: Bài tập nhóm STEM lớp 10, quản lý lệnh Vàng phiên Mỹ, kiềm chế cơn giận khi bị chỉ trích...",
            key=f"topic_input_{sel_track_id}_{sel_level_code}",
        )

        if st.button("🚀 Yêu Cầu AI Sinh Bài Tập Mới Ngay", key=f"btn_gen_{sel_track_id}_{sel_level_code}", type="primary", use_container_width=True):
            if not active_keys:
                st.warning("Cần API Key để sinh bài tập.")
            else:
                with st.spinner("AI Mentor đang thiết kế bài tập tình huống thực chiến độc bản (tự động xoay tua API key)..."):
                    new_lesson = generate_dynamic_lesson(
                        api_keys=active_keys,
                        model_name=model_choice,
                        track_title=track_options[sel_track_id],
                        level_code=sel_level_code,
                        level_name=sel_level_name,
                        custom_topic=custom_topic.strip(),
                    )
                if new_lesson and not new_lesson.get("error"):
                    add_custom_lesson(sel_track_id, new_lesson, updated_by="AI")
                    st.session_state[f"target_lesson_{sel_track_id}_{sel_level_code}"] = new_lesson.get("id")
                    st.success(f"🎉 Đã tạo thành công bài tập mới: **{new_lesson.get('title')}**!")
                    st.rerun()
                else:
                    st.error(new_lesson.get("error", "Lỗi khi sinh bài tập."))

        # Danh sách các bài đã do AI tạo trong cấp độ này
        ai_lessons = [l for l in lessons if l.get("created_by") == "AI" or "_ai_" in l.get("id", "")]
        if ai_lessons:
            st.markdown(f"#### 📚 Các bài tập do AI mở rộng trong cấp độ này ({len(ai_lessons)} bài)")
            for al in ai_lessons:
                is_done = al["id"] in user_training
                icon = "✅" if is_done else "📖"
                st.markdown(f"- {icon} **{al.get('title')}** (Chế độ: `{al.get('mode')}`) — ID: `{al.get('id')}`")

