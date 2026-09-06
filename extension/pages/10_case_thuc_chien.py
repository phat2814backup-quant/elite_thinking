# -*- coding: utf-8 -*-
"""Case Thực Chiến — Thư viện vấn đề áp dụng nguyên lý (nhóm A trước)"""
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
    # Cho phép chạy độc lập khi test trong thư mục extension
    st.set_page_config(page_title="Case Thực Chiến", page_icon="🎯", layout="wide")
    username = "guest"
    display_name = "Guest"
    active_keys = []
    model_choice = "gemini"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = CURRENT_DIR / "data" / "cases_toan_khoa_hoc.json"

@st.cache_data(show_spinner=False)
def load_cases() -> Dict[str, Any]:
    if not DATA_PATH.exists():
        return {"metadata": {}, "cases": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_cases()
meta = data.get("metadata", {})
cases: List[Dict[str, Any]] = data.get("cases", [])

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎯 Case Thực Chiến — Áp dụng Nguyên lý")
st.caption(
    f"Nhóm A: {meta.get('title', 'Toán & Khoa học')} · "
    f"{meta.get('total_cases', len(cases))} case · "
    f"Đối tượng: {meta.get('target_age', '11-15 tuổi')}"
)

st.markdown("""
Tab này cầu nối **lý thuyết → thực tế**.  
Mỗi case được phân rã về First Principles, gắn với nguyên lý cụ thể, có câu hỏi kích hoạt và biến thể để luyện interleaving.
""")

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 1.5])

with col_f1:
    difficulties = sorted({c.get("difficulty", "Cơ bản") for c in cases})
    sel_diff = st.multiselect(
        "Độ khó",
        options=difficulties,
        default=difficulties,
        key="case_filter_diff",
    )

with col_f2:
    all_principles = sorted(
        {p for c in cases for p in c.get("principles", [])}
    )
    sel_prin = st.multiselect(
        "Nguyên lý",
        options=all_principles,
        default=[],
        placeholder="Tất cả nguyên lý",
        key="case_filter_prin",
    )

with col_f3:
    search_q = st.text_input(
        "Tìm kiếm",
        placeholder="chu vi, entropy, đòn bẩy, xác suất...",
        key="case_search",
    )

# ---------------------------------------------------------------------------
# Filter logic
# ---------------------------------------------------------------------------
def match_case(c: Dict[str, Any]) -> bool:
    if c.get("difficulty") not in sel_diff:
        return False
    if sel_prin:
        if not any(p in c.get("principles", []) for p in sel_prin):
            return False
    if search_q.strip():
        q = search_q.strip().lower()
        blob = " ".join(
            [
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

st.caption(f"Hiển thị **{len(filtered)}** / {len(cases)} case")

# ---------------------------------------------------------------------------
# Display cases
# ---------------------------------------------------------------------------
if not filtered:
    st.info("Không có case nào khớp bộ lọc. Thử nới lỏng điều kiện.")
else:
    for c in filtered:
        with st.expander(
            f"**{c.get('id', '?')}** · {c.get('title', 'Không tiêu đề')}  "
            f"· `{c.get('difficulty', '')}` · ⏱ {c.get('time_minutes', '?')} phút",
            expanded=False,
        ):
            st.markdown(f"### Vấn đề")
            st.write(c.get("problem", ""))

            st.markdown(f"**Câu hỏi kích hoạt:** *{c.get('trigger_question', '')}*")

            st.markdown("#### Phân rã First Principles")
            for i, step in enumerate(c.get("first_principles_breakdown", []), 1):
                st.markdown(f"{i}. {step}")

            prin = c.get("principles", [])
            if prin:
                st.markdown("**Nguyên lý / Mô hình kích hoạt:** " + " · ".join(f"`{p}`" for p in prin))

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

            # Nút liên kết sang Phân Rã AI (nếu chạy trong app chính)
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
                        "Hãy chuyển sang tab **Phân Rã Thực Chiến** và dán (hoặc hệ thống sẽ tự điền nếu đã tích hợp)."
                    )
            with col_b:
                st.caption("Gợi ý: Làm case này trước, sau đó tự đặt biến thể mới và phân rã.")

# ---------------------------------------------------------------------------
# Sidebar info / next steps
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📌 Nhóm case hiện có")
    st.markdown(f"- **A. Toán & Khoa học**: {len(cases)} case")
    st.markdown("- B–E: sắp bổ sung")
    st.markdown("- **F. Elite hiện tại & 10–20 năm tới**: ~50 case (sắp có)")

    st.divider()
    st.markdown("### Hướng dẫn dùng")
    st.markdown("""
1. Chọn độ khó / nguyên lý hoặc tìm kiếm.
2. Mở case → đọc vấn đề → tự nghĩ trước.
3. Xem phân rã & nguyên lý.
4. Thử biến thể.
5. (Tuỳ chọn) Đưa sang tab Phân Rã AI để đào sâu hơn.
    """)

st.divider()
st.caption(
    "Extension page · Case Thực Chiến v1.0 · "
    "Dữ liệu: data/cases_toan_khoa_hoc.json · "
    "Có thể mở rộng thêm nhóm B–F bằng cách thêm file JSON và cập nhật loader."
)
