# -*- coding: utf-8 -*-
"""Lộ trình 12 tuần — xương curriculum + Systems/Uncertainty + AI Judgment."""
from __future__ import annotations

import streamlit as st

from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
is_admin_user = ctx.get("is_admin", False)

from utils.curriculum import (
    load_curriculum,
    get_weeks,
    get_week,
    get_week_progress,
    get_user_curriculum_progress,
    start_curriculum,
    save_week_exercise,
    save_week_quiz_score,
    complete_week,
    curriculum_summary,
    is_week_unlocked,
)

meta = load_curriculum()
weeks = get_weeks()
summary = curriculum_summary(username)

st.title("📅 Lộ trình 12 tuần — Tư duy Tinh hoa Gia đình")
st.caption(meta.get("subtitle") or "Curriculum · Systems/Uncertainty · AI Judgment")

if is_admin_user:
    st.info("👑 **Quyền Admin:** Bạn có đặc quyền mở khóa toàn bộ 12 tuần để duyệt nội dung và trải nghiệm tự do.")

# --- Overview metrics ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Đã hoàn thành", f"{summary['completed_weeks']}/{summary['total_weeks']}")
with c2:
    st.metric("Tiến độ", f"{summary['pct']}%")
with c3:
    st.metric("Tuần hiện tại", str(summary["current_week"]))
with c4:
    st.metric("Bắt đầu", summary["started_at"] or "—")

st.progress(min(1.0, summary["pct"] / 100.0))

with st.expander("4 nguyên tắc lộ trình", expanded=False):
    for p in meta.get("principles", []):
        st.markdown(f"- {p}")

with st.expander("⚡ 9 Nguyên Tắc Ultralearning (Scott H. Young) — Giao Thức Tăng Tốc Học Sâu", expanded=False):
    st.markdown("""
    1. **Bản đồ Siêu học (Metalearning):** Phân rã môn học thành 3 cột: *Khái niệm (cần hiểu)*, *Dữ kiện (cần nhớ)*, và *Quy trình (cần làm)*.
    2. **Tập trung cao độ (Focus):** Dành các khối thời gian 50-90 phút không xao nhãng để tư duy sâu.
    3. **Học trực diện (Directness):** Học kỹ năng nào thì lao thẳng vào tình huống thực chiến của kỹ năng đó, không học vòng vo qua lý thuyết thụ động.
    4. **Khoan sâu điểm yếu (Drill):** Tách nhỏ mắt xích bị tắc nghẽn nhất để luyện đi luyện lại cho đến khi thông suốt.
    5. **Truy hồi chủ động (Retrieval / Active Recall):** Đóng sách lại và tự giải thích / giải quyết vấn đề, không đọc thụ động.
    6. **Phản hồi tức thì (Feedback):** Tìm kiếm phản hồi khách quan từ thực tế, không trốn tránh sai sót.
    7. **Ghi nhớ bền vững (Retention):** Lặp lại ngắt quãng (Spaced Repetition) để cài đặt mô hình vào tiềm thức.
    8. **Trực giác từ nguyên lý sâu (Intuition):** Sử dụng Kỹ thuật Feynman để giải thích bản chất từ Chân lý gốc (First Principles).
    9. **Thực nghiệm liên tục (Experimentation):** Liên tục thử nghiệm các phương pháp mới ngoài vùng an toàn.
    """)

if st.button("🚀 Bắt đầu / tiếp tục lộ trình", type="primary"):
    start_curriculum(username)
    st.success("Đã ghi nhận bắt đầu. Chọn tuần bên dưới.")
    st.rerun()

st.divider()

# --- Week selector ---
labels = []
for w in weeks:
    wp = get_week_progress(username, w["week"])
    status = wp.get("status", "not_started")
    icon = {"completed": "✅", "in_progress": "🟡", "not_started": "⚪"}.get(status, "⚪")
    unlocked_w = is_week_unlocked(username, w["week"], is_admin=is_admin_user)
    lock = "" if unlocked_w else " 🔒"
    theme = w.get("theme", "")
    labels.append(f"{icon} Tuần {w['week']}: {w['title']} ({theme}){lock}")

idx_default = max(0, min(len(weeks) - 1, int(summary["current_week"]) - 1))
choice = st.selectbox("Chọn tuần", options=list(range(len(weeks))), format_func=lambda i: labels[i], index=idx_default)
week = weeks[choice]
wn = int(week["week"])
unlocked = is_week_unlocked(username, wn, is_admin=is_admin_user)
wp = get_week_progress(username, wn)

if not unlocked:
    st.warning(f"Tuần {wn} chưa mở. Hãy hoàn thành tuần {wn - 1} trước (hoặc bấm bắt đầu lộ trình).")
    st.stop()

st.header(f"Tuần {wn} — {week['title']}")
st.markdown(f"**Chủ đề:** `{week.get('theme')}` · ⏱️ ~{week.get('estimated_minutes', 40)} phút")
st.info(f"**Mục tiêu tuần:** {week.get('goal')}")
st.markdown(f"**Ý trung tâm:** {week.get('core_idea')}")

# Reading pointers
if week.get("read"):
    st.subheader("📖 Đọc / ôn trong app")
    for r in week["read"]:
        st.markdown(f"- **{r.get('label')}** _(trang: `{r.get('page', '')}`)_")

# Concept deep dive
deep_dive = week.get("concept_deep_dive")
if deep_dive:
    st.subheader("🔬 Đào Sâu Khái Niệm & Liên Kết Mô Hình")
    for c in deep_dive:
        with st.expander(f"✨ {c.get('name')}", expanded=False):
            st.markdown(f"**Bản chất:** {c.get('summary', '')}")
            c_g, c_b = st.columns(2)
            with c_g:
                st.success(f"**✅ Áp dụng đúng:**\n\n{c.get('good_example', '')}")
            with c_b:
                st.error(f"**❌ Áp dụng sai / Bẫy:**\n\n{c.get('bad_example', '')}")
            if c.get("boundary"):
                st.caption(f"**⚖️ Điều kiện biên (Khi nào KHÔNG dùng):** {c.get('boundary')}")
            if c.get("lattice_link"):
                st.info(f"**🕸️ Liên kết Latticework:** {c.get('lattice_link')}")

# Case study
cs = week.get("case_study")
if cs:
    st.subheader(f"🎯 Tình Huống Thực Chiến: {cs.get('title', '')}")
    st.markdown(f"**Bối cảnh:** {cs.get('context', '')}")
    st.info(f"**❓ Câu hỏi quyết định:** {cs.get('decision_question', '')}")

    c_f, c_n = st.columns(2)
    with c_f:
        st.markdown("##### 📌 Dữ kiện cứng (Facts)")
        for f in cs.get("facts", []):
            st.markdown(f"- {f}")
    with c_n:
        st.markdown("##### 📢 Nhiễu / Cảm tính (Noise & Biases)")
        for n in cs.get("noise", []):
            st.markdown(f"- {n}")

    with st.expander("💡 Xem Hướng Dẫn Phân Tích & Đáp Án Mẫu Của Elite", expanded=False):
        st.markdown(f"**🔬 Ứng dụng mô hình:**\n\n{cs.get('framework_application', '')}")
        st.markdown(f"**📋 Phân tích mẫu từng bước:**\n\n{cs.get('exemplar_analysis', '')}")
        if cs.get("action_plan"):
            st.success(f"**🎯 Hành động đề xuất:** {cs.get('action_plan')}")
        if cs.get("common_traps"):
            st.warning("**⚠️ Các bẫy tư duy phổ biến:**\n\n" + "\n".join(f"- {t}" for t in cs.get("common_traps", [])))

# Systems concepts
if week.get("systems_concepts"):
    st.subheader("🕸️ Systems concepts")
    for c in week["systems_concepts"]:
        with st.expander(f"{c.get('name')} — {c.get('id')}", expanded=False):
            st.markdown(c.get("summary", ""))
            st.caption(f"Điều kiện biên: {c.get('boundary', '')}")
            st.caption(f"Bẫy: {c.get('trap', '')}")
            st.success(f"Hành động: {c.get('action', '')}")

# Uncertainty tools
if week.get("uncertainty_tools"):
    st.subheader("🎲 Uncertainty tools")
    for t in week["uncertainty_tools"]:
        with st.expander(f"{t.get('name')} — {t.get('id')}", expanded=False):
            st.markdown(t.get("summary", ""))
            st.caption(f"Điều kiện biên: {t.get('boundary', '')}")
            st.caption(f"Bẫy: {t.get('trap', '')}")
            st.success(f"Hành động: {t.get('action', '')}")

# AI drills
if week.get("ai_drills"):
    st.subheader("🤖 AI Judgment drills")
    for d in week["ai_drills"]:
        with st.expander(f"{d.get('name')} — {d.get('id')}", expanded=True):
            st.markdown(d.get("summary", ""))
            steps = d.get("steps") or []
            if steps:
                st.markdown("**Các bước:**")
                for i, s in enumerate(steps, 1):
                    st.markdown(f"{i}. {s}")
            st.caption(f"Bẫy: {d.get('trap', '')}")

# Exercise
st.subheader("✅ Bài tập áp dụng (bắt buộc để hoàn thành tuần)")
ex = week.get("exercise") or {}
st.markdown(ex.get("prompt", ""))
if ex.get("success_criteria"):
    st.caption(f"Tiêu chí đạt: {ex.get('success_criteria')}")

if ex.get("checklist"):
    with st.expander("📋 Checklist tiêu chí tự đánh giá", expanded=False):
        for item in ex.get("checklist", []):
            st.markdown(f"- [ ] {item}")

if ex.get("bad_example") or ex.get("good_example"):
    with st.expander("👀 Xem ví dụ bài làm Đạt vs Chưa đạt", expanded=False):
        if ex.get("bad_example"):
            st.markdown("**❌ Bài làm chưa đạt (hời hợt / bắt chước):**")
            st.info(ex.get("bad_example"))
        if ex.get("good_example"):
            st.markdown("**✅ Bài làm đạt chuẩn Elite (sâu sắc, có dữ kiện):**")
            st.success(ex.get("good_example"))

default_ans = wp.get("exercise_answer") or ""
answer = st.text_area("Câu trả lời của bạn", value=default_ans, height=180, key=f"ex_{wn}")
notes = st.text_input("Ghi chú thêm (optional)", value=wp.get("notes") or "", key=f"notes_{wn}")

if st.button("💾 Lưu bài tập", key=f"save_ex_{wn}"):
    if not answer.strip():
        st.error("Hãy viết bài tập trước khi lưu.")
    else:
        save_week_exercise(username, wn, answer.strip(), notes.strip())
        st.success("Đã lưu bài tập.")
        st.rerun()

# Quiz
quiz = week.get("quiz") or []
if quiz:
    st.subheader("📝 Quiz nhanh")
    responses = []
    for i, item in enumerate(quiz):
        st.markdown(f"**Câu {i+1}.** {item['q']}")
        opt = st.radio(
            f"Chọn đáp án ({wn}_{i})",
            options=list(range(len(item["options"]))),
            format_func=lambda j, item=item: item["options"][j],
            key=f"quiz_{wn}_{i}",
        )
        responses.append(opt)

    if st.button("Chấm quiz", key=f"grade_{wn}"):
        score = 0
        for i, item in enumerate(quiz):
            ok = responses[i] == item["answer"]
            if ok:
                score += 1
                st.success(f"Câu {i+1}: Đúng — {item.get('explain', '')}")
            else:
                st.error(
                    f"Câu {i+1}: Sai — Đáp án đúng: {item['options'][item['answer']]}. {item.get('explain', '')}"
                )
                if item.get("trap_analysis"):
                    st.caption(f"⚠️ **Phân tích bẫy:** {item.get('trap_analysis')}")
        save_week_quiz_score(username, wn, score, len(quiz))
        st.info(f"Điểm: {score}/{len(quiz)}")

# Complete
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.caption(f"Trạng thái: **{wp.get('status', 'not_started')}**")
    if wp.get("quiz_score") is not None:
        st.caption(f"Quiz: {wp.get('quiz_score')}/{wp.get('quiz_total')}")
with col_b:
    if st.button("🏁 Hoàn thành tuần này", type="primary", key=f"done_{wn}"):
        ok, msg = complete_week(username, wn, is_admin=is_admin_user)
        if ok:
            st.success(msg)
            st.balloons()
            st.rerun()
        else:
            st.error(msg)

st.divider()
st.markdown("### Toàn cảnh 12 tuần")
for w in weeks:
    p = get_week_progress(username, w["week"])
    status_val = p.get("status", "not_started")
    icon = {"completed": "✅", "in_progress": "🟡"}.get(status_val, "⚪")
    st.markdown(f"{icon} **Tuần {w['week']}** · {w['title']} · _{w.get('theme')}_")
