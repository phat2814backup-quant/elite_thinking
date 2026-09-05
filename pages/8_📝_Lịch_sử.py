# -*- coding: utf-8 -*-
"""Lịch sử của tôi"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.knowledge import load_user_history
from utils.training import get_lesson
from utils.app_common import ensure_quiz_imports
from utils.daily_workout import get_user_streak_info
from utils.diagnostic import get_latest_diagnostic_result
from utils.decision_journal import get_decision_summary_stats

_quiz = ensure_quiz_imports()
get_user_mastery_summary = _quiz["get_user_mastery_summary"]

st.title("📝 Lịch sử của tôi")
hist = load_user_history(username)

# Thống kê Bộ 3 Động Lực Tinh Hoa (Elite Trinity)
st.markdown("#### 🔥 Chỉ Số Rèn Luyện & Hiệu Chuẩn Tinh Hoa")
trin_c1, trin_c2, trin_c3 = st.columns(3)

# 1. Streak
u_streak_tab8 = get_user_streak_info(username)
with trin_c1:
    s_val_t8 = u_streak_tab8["current_streak"]
    s_badge_t8 = "⚡ Khởi động" if s_val_t8 < 7 else ("🔥 Thói quen thép" if s_val_t8 < 30 else "🏆 Phản xạ vô thức")
    st.metric("🔥 Chuỗi Streak 15 Phút", f"{s_val_t8} ngày", f"Kỷ lục: {u_streak_tab8['longest_streak']} ngày ({s_badge_t8})")

# 2. Diagnostic
latest_diag_t8 = get_latest_diagnostic_result(username)
with trin_c2:
    if latest_diag_t8:
        st.metric("🧭 Chỉ Số Nhận Thức (Radar)", f"{latest_diag_t8['overall_index']}%", latest_diag_t8['rank_title'].split()[0] + " " + latest_diag_t8['rank_title'].split()[1])
    else:
        st.metric("🧭 Điểm Mù Nhận Thức", "Chưa làm test", "Vào Tab 5 để test")

# 3. Decision Calibration
d_stats_t8 = get_decision_summary_stats(username)
with trin_c3:
    if d_stats_t8["reviewed_count"] > 0:
        st.metric("📓 Điểm Hiệu Chuẩn Quyết Định", f"{d_stats_t8['calibration_accuracy']}%", f"{d_stats_t8['reviewed_count']} quyết định đã duyệt")
    else:
        st.metric("📓 Quyết Định Đang Lưu", f"{d_stats_t8['total_logged']} mục", f"{d_stats_t8['due_count']} đến hạn kiểm định")

st.divider()

# Thống kê thành tích Trắc nghiệm & Làm chủ
m_info = get_user_mastery_summary(username)
st.markdown("#### 🏆 Thành tích Trắc nghiệm & Làm chủ Mô hình")
mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.metric("Độ chính xác Trắc nghiệm", f"{m_info['accuracy']}%", f"{m_info['total_quizzes']} bài test")
with mc2:
    st.metric("Mô hình đã Mastered", f"{m_info['mastered_count']} / 88", f"{m_info['mastery_pct']}%")
with mc3:
    st.metric("Đang học / Cần ôn", f"{m_info['learning_count']} học · {m_info['review_count']} ôn")

recent_tests = m_info.get("recent_tests", [])
if recent_tests:
    with st.expander(f"📜 Xem {len(recent_tests)} lượt làm bài trắc nghiệm gần nhất"):
        for t in recent_tests[:10]:
            st.markdown(f"- `{t.get('time')}` · **{t.get('category')}**: **{t.get('score')}/{t.get('total')}** đúng ({t.get('percentage')}%)")

st.markdown("#### Phân rã đã làm")
analyses = hist.get("analyses", [])
if not analyses:
    st.info("Chưa có phân rã nào.")
else:
    for a in analyses[:30]:
        with st.expander(f"{a.get('time', '')} — {a.get('problem', '')[:80]}"):
            st.write(a.get("summary", ""))

st.markdown("#### Bài đào tạo đã làm")
training = hist.get("training", {})
if not training:
    st.info("Chưa hoàn thành bài nào.")
else:
    for lid, info in training.items():
        lesson = get_lesson(lid)
        title = lesson["title"] if lesson else lid
        with st.expander(f"{title} · {info.get('time', '')}"):
            st.markdown("**Câu trả lời:**")
            st.write(info.get("answer", ""))
            if info.get("feedback"):
                st.markdown("**Feedback:**")
                st.write(info["feedback"])

