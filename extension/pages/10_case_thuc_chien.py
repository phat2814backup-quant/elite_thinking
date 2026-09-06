# -*- coding: utf-8 -*-
"""Case Thực Chiến — Thư viện vấn đề áp dụng nguyên lý (A–F)"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

# Bootstrap giống các page khác trong app chính
try:
    from utils.app_common import bootstrap
    ctx = bootstrap()
    username = ctx["username"]
    display_name = ctx["display_name"]
    active_keys = ctx["active_keys"]
    model_choice = ctx["model_choice"]
except Exception:
    st.set_page_config(page_title="Case Thực Chiến", page_icon="🎯", layout="wide")
    username = "guest"
    display_name = "Guest"
    active_keys = []
    model_choice = "gemini"

# ---------------------------------------------------------------------------
# Load all case files
# ---------------------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CURRENT_DIR / "data"

CASE_FILES = {
    "A": "cases_toan_khoa_hoc.json",
    "B": "cases_hoc_tap_tu_duy.json",
    "C": "cases_tai_chinh_ckvn.json",
    "D": "cases_su_nghiep_quyet_dinh.json",
    "E": "cases_tam_ly_he_thong.json",
    "F": "cases_elite_future.json",
}

GROUP_LABELS = {
    "A": "A · Toán & Khoa học (Trẻ em)",
    "B": "B · Học tập & Siêu học",
    "C": "C · Tài chính cá nhân & CKVN",
    "D": "D · Sự nghiệp & Quyết định",
    "E": "E · Tâm lý đám đông & Hệ thống",
    "F": "F · Elite hiện tại & 10–20 năm tới",
}


@st.cache_data(show_spinner=False)
def load_all_groups() -> Dict[str, Dict[str, Any]]:
    groups: Dict[str, Dict[str, Any]] = {}
    for g, fname in CASE_FILES.items():
        path = DATA_DIR / fname
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                groups[g] = json.load(f)
    return groups


all_data = load_all_groups()
total_cases = sum(len(d.get("cases", [])) for d in all_data.values())

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎯 Case Thực Chiến — Áp dụng Nguyên lý")
st.caption(
    f"Tổng **{total_cases}** case · 6 nhóm (A–F) · "
    "Cầu nối lý thuyết → thực tế · First Principles · Interleaving"
)

st.markdown("""
Mỗi case được phân rã về First Principles, gắn nguyên lý cụ thể, có câu hỏi kích hoạt và biến thể để luyện transfer.
""")

# ---------------------------------------------------------------------------
# Group selector + filters
# ---------------------------------------------------------------------------
available_groups = [g for g in "ABCDEF" if g in all_data]
default_groups = available_groups[:]

col_g, col_d, col_p, col_s = st.columns([1.4, 1.1, 1.3, 1.4])

with col_g:
    sel_groups = st.multiselect(
        "Nhóm",
        options=available_groups,
        default=default_groups,
        format_func=lambda g: GROUP_LABELS.get(g, g),
        key="case_filter_groups",
    )

# Collect cases from selected groups
cases: List[Dict[str, Any]] = []
for g in sel_groups:
    for c in all_data[g].get("cases", []):
        c = dict(c)
        c["_group"] = g
        cases.append(c)

with col_d:
    difficulties = sorted({c.get("difficulty", "Cơ bản") for c in cases}) or ["Cơ bản"]
    sel_diff = st.multiselect(
        "Độ khó",
        options=difficulties,
        default=difficulties,
        key="case_filter_diff",
    )

with col_p:
    all_principles = sorted({p for c in cases for p in c.get("principles", [])})
    sel_prin = st.multiselect(
        "Nguyên lý",
        options=all_principles,
        default=[],
        placeholder="Tất cả nguyên lý",
        key="case_filter_prin",
    )

with col_s:
    search_q = st.text_input(
        "Tìm kiếm",
        placeholder="AI, đòn bẩy, entropy, sự nghiệp...",
        key="case_search",
    )

# ---------------------------------------------------------------------------
# Filter logic
# ---------------------------------------------------------------------------
def match_case(c: Dict[str, Any]) -> bool:
    if c.get("difficulty") not in sel_diff:
        return False
    if sel_prin and not any(p in c.get("principles", []) for p in sel_prin):
        return False
    if search_q.strip():
        q = search_q.strip().lower()
        blob = " ".join(
            [
                c.get("id", ""),
                c.get("title", ""),
                c.get("problem", ""),
                c.get("trigger_question", ""),
                " ".join(c.get("principles", [])),
                " ".join(c.get("first_principles_breakdown", [])),
            ]
        ).lower()
        if q not in blob:
            return False
    return True


filtered = [c for c in cases if match_case(c)]
st.caption(f"Hiển thị **{len(filtered)}** / {len(cases)} case (đã chọn nhóm)")

# ---------------------------------------------------------------------------
# Display cases
# ---------------------------------------------------------------------------
if not filtered:
    st.info("Không có case nào khớp bộ lọc. Thử nới lỏng điều kiện hoặc chọn thêm nhóm.")
else:
    for c in filtered:
        gid = c.get("_group", "?")
        with st.expander(
            f"**{c.get('id', '?')}** · {c.get('title', 'Không tiêu đề')}  "
            f"· `{GROUP_LABELS.get(gid, gid)}` · `{c.get('difficulty', '')}` · ⏱ {c.get('time_minutes', '?')} phút",
            expanded=False,
        ):
            st.markdown("### Vấn đề")
            st.write(c.get("problem", ""))

            st.markdown(f"**Câu hỏi kích hoạt:** *{c.get('trigger_question', '')}*")

            st.markdown("#### Phân rã First Principles")
            for i, step in enumerate(c.get("first_principles_breakdown", []), 1):
                st.markdown(f"{i}. {step}")

            prin = c.get("principles", [])
            if prin:
                st.markdown(
                    "**Nguyên lý / Mô hình kích hoạt:** "
                    + " · ".join(f"`{p}`" for p in prin)
                )

            steps = c.get("solution_steps", [])
            if steps:
                st.markdown("#### Gợi ý bước giải")
                for i, s in enumerate(steps, 1):
                    st.markdown(f"{i}. {s}")

            variants = c.get("variants", [])
            if variants:
                st.markdown("#### Biến thể (Interleaving)")
                for v in variants:
                    st.markdown(f"- {v}")

            insight = c.get("elite_insight")
            if insight:
                st.success(f"**Elite Insight:** {insight}")

            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(
                    "🚀 Phân rã case này bằng AI 9 Lenses",
                    key=f"btn_ai_{c.get('id')}",
                    use_container_width=True,
                ):
                    st.session_state["prefill_problem"] = (
                        f"{c.get('title')}\n\n{c.get('problem')}\n\n"
                        f"Câu hỏi kích hoạt: {c.get('trigger_question')}"
                    )
                    st.info(
                        "Nội dung đã được chuẩn bị. "
                        "Chuyển sang tab **Phân Rã Thực Chiến** để chạy AI 9 Lenses."
                    )
            with col_b:
                st.caption("Gợi ý: Tự nghĩ trước → xem phân rã → làm biến thể → đưa sang AI nếu cần đào sâu.")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📌 Tổng quan nhóm case")
    for g in "ABCDEF":
        if g in all_data:
            n = len(all_data[g].get("cases", []))
            st.markdown(f"- **{GROUP_LABELS.get(g, g)}**: {n} case")
    st.markdown(f"**Tổng: {total_cases} case**")

    st.divider()
    st.markdown("### Hướng dẫn dùng")
    st.markdown("""
1. Chọn nhóm / độ khó / nguyên lý hoặc tìm kiếm.
2. Mở case → đọc vấn đề → tự nghĩ trước.
3. Xem phân rã & nguyên lý.
4. Thử biến thể (interleaving).
5. (Tuỳ chọn) Đưa sang tab Phân Rã AI.
    """)

st.divider()
st.caption(
    "Extension · Case Thực Chiến v1.1 · "
    "Data: extension/data/cases_*.json · "
    "Tự động load 6 nhóm A–F."
)
