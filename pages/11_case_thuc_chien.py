# -*- coding: utf-8 -*-
"""
Trang: 100+ Case Thực Chiến — Cầu Nối Lý Thuyết Vào Đời Sống Thực Tế
Phân rã bài toán đa chiều cho Học sinh Wellspring (2011-2015) và Giới Elite / Người lớn 8x.
Tự động quét và nạp dữ liệu từ data/cases_*.json và extension/data/cases_*.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Set

import streamlit as st

# Bootstrap đồng bộ toàn ứng dụng
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
# Data Loader (Đa nguồn: data/ và extension/data/)
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

@st.cache_data(show_spinner=False)
def load_all_cases() -> Dict[str, Any]:
    """Tự động phát hiện và gộp toàn bộ các file case trong data/ và extension/data/."""
    all_cases: List[Dict[str, Any]] = []
    groups_meta: Dict[str, Dict[str, Any]] = {}
    seen_ids: Set[str] = set()

    search_dirs = [ROOT_DIR / "data", ROOT_DIR / "extension" / "data"]
    json_files: List[Path] = []

    for d in search_dirs:
        if d.exists() and d.is_dir():
            for p in d.glob("cases_*.json"):
                if p.name not in [x.name for x in json_files]:
                    json_files.append(p)

    for f_path in json_files:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                meta = content.get("metadata", {})
                g_code = meta.get("group", f_path.stem.replace("cases_", "").upper())
                g_title = meta.get("title", f_path.stem)
                groups_meta[g_code] = {
                    "code": g_code,
                    "title": g_title,
                    "target_age": meta.get("target_age", "Đa lứa tuổi"),
                    "description": meta.get("description", ""),
                    "file": f_path.name,
                }
                for c in content.get("cases", []):
                    c_id = c.get("id")
                    if c_id and c_id not in seen_ids:
                        seen_ids.add(c_id)
                        c["group_code"] = g_code
                        c["group_title"] = g_title
                        all_cases.append(c)
        except Exception as e:
            st.sidebar.warning(f"Lỗi đọc {f_path.name}: {e}")

    return {"groups": groups_meta, "cases": all_cases}


loaded_data = load_all_cases()
groups_dict = loaded_data.get("groups", {})
all_cases = loaded_data.get("cases", [])

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎯 Thư Viện 150+ Case Thực Chiến — Cầu Nối Lý Thuyết ➔ Đời Sống")
st.caption(
    "Giải quyết bài toán thực tế bằng First Principles · Dành cho Học sinh Sài Gòn (2011–2015) "
    "& Giới Đầu tư / Tinh hoa Thế hệ 8x (Hiện tại & Tầm nhìn 10–20 năm)."
)

st.markdown("""
> *"Bạn không thực sự hiểu một nguyên lý cho đến khi bạn nhìn thấy nó vận hành trong một tình huống thực tế của chính mình."*  
Mỗi case dưới đây được mổ xẻ theo quy trình chuẩn: **Vấn đề cụ thể ➔ Câu hỏi kích hoạt ➔ Phân rã First Principles ➔ Nguyên lý kích hoạt ➔ Gợi ý giải ➔ Biến thể (Interleaving) ➔ Elite Insight**.
""")

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
c_g1, c_g2, c_g3, c_g4 = st.columns([1.5, 1.2, 1.5, 2.0])

with c_g1:
    group_options = ["Tất cả nhóm"] + [f"Nhóm {k}: {v['title']}" for k, v in groups_dict.items()]
    sel_group_label = st.selectbox("Phân hệ chuyên đề:", group_options, key="case_filter_group")

with c_g2:
    all_diffs = sorted({c.get("difficulty", "Cơ bản") for c in all_cases})
    sel_diffs = st.multiselect("Độ khó:", all_diffs, default=all_diffs, key="case_filter_diff")

with c_g3:
    all_principles = sorted({p for c in all_cases for p in c.get("principles", [])})
    sel_principles = st.multiselect(
        "Nguyên lý / Mô hình:",
        options=all_principles,
        default=[],
        placeholder="Tất cả nguyên lý",
        key="case_filter_prin",
    )

with c_g4:
    search_query = st.text_input(
        "🔍 Tìm kiếm tức thì:",
        placeholder="Chu vi, năng lượng, đòn bẩy, chuỗi cung ứng, AI...",
        key="case_search_box",
    )

# ---------------------------------------------------------------------------
# Filter Engine
# ---------------------------------------------------------------------------
def filter_single_case(c: Dict[str, Any]) -> bool:
    # 1. Filter theo Group
    if sel_group_label != "Tất cả nhóm":
        g_code_selected = sel_group_label.split(":")[0].replace("Nhóm ", "").strip()
        if c.get("group_code") != g_code_selected:
            return False

    # 2. Filter theo Difficulty (mặc định Cơ bản nếu thiếu)
    c_diff = c.get("difficulty") or "Cơ bản"
    if c_diff not in sel_diffs:
        return False

    # 3. Filter theo Principles
    c_prins = c.get("principles") or c.get("core_principles") or []
    if sel_principles:
        if not any(p in c_prins for p in sel_principles):
            return False

    # 4. Filter theo Search Query
    if search_query.strip():
        q = search_query.strip().lower()
        search_blob = " ".join([
            c.get("title", ""),
            c.get("problem", ""),
            c.get("trigger_question", ""),
            c.get("elite_insight", "") or c.get("key_takeaways", ""),
            " ".join(c_prins),
            " ".join(c.get("first_principles_breakdown", []) or [c.get("latticework_analysis", "")]),
        ]).lower()
        if q not in search_blob:
            return False

    return True


filtered_cases = [c for c in all_cases if filter_single_case(c)]

st.caption(f"Đang hiển thị **{len(filtered_cases)}** / **{len(all_cases)}** case thực chiến phù hợp")
st.divider()

# ---------------------------------------------------------------------------
# Render Cases List
# ---------------------------------------------------------------------------
if not filtered_cases:
    st.info("Không tìm thấy case nào phù hợp với bộ lọc. Bạn hãy thử nới lỏng các tiêu chí tìm kiếm.")
else:
    for idx, c in enumerate(filtered_cases):
        c_id = c.get("id", f"C{idx+1}")
        c_title = c.get("title", "Bài toán thực tế")
        c_diff = c.get("difficulty", "Cơ bản")
        c_time = c.get("time_minutes", 10)
        c_grp = c.get("group_code", "A")

        diff_badge = {"Cơ bản": "🟢 Cơ bản", "Trung bình": "🟡 Trung bình", "Nâng cao": "🔴 Nâng cao"}.get(c_diff, c_diff)

        with st.expander(f"**[{c_id}]** {c_title}  `[{diff_badge} · ⏱ {c_time} phút · Nhóm {c_grp}]`", expanded=(idx == 0)):
            st.markdown("### 📌 Bài Toán Thực Tế")
            st.info(c.get("problem", ""))

            trig_q = c.get("trigger_question") or c.get("problem", "")[:150]
            st.markdown(f"**❓ Câu hỏi kích hoạt tư duy (Trigger Prompt):**  \n👉 *\"{trig_q}\"*")

            raw_bd = c.get("first_principles_breakdown") or c.get("latticework_analysis") or []
            if isinstance(raw_bd, str):
                breakdown_steps = [s.strip() for s in raw_bd.split("\n") if s.strip()]
            elif isinstance(raw_bd, list):
                breakdown_steps = raw_bd
            else:
                breakdown_steps = []

            if breakdown_steps:
                st.markdown("#### 🔬 Phân Rã First Principles (Từng Bước Cốt Lõi):")
                for step_idx, step in enumerate(breakdown_steps, 1):
                    st.markdown(f"{step_idx}. {step}")

            prins = c.get("principles") or c.get("core_principles") or []
            if prins:
                st.markdown("**🔗 Nguyên lý & Mô hình tư duy kích hoạt:**  \n" + " · ".join([f"`{p}`" for p in prins]))

            raw_steps = c.get("solution_steps") or c.get("elite_solution") or []
            if isinstance(raw_steps, str):
                steps = [s.strip() for s in raw_steps.split("\n") if s.strip()]
            elif isinstance(raw_steps, list):
                steps = raw_steps
            else:
                steps = []

            if steps:
                st.markdown("#### 🛠️ Gợi Ý Khung Giải Quyết Thực Chiến:")
                for s_idx, s in enumerate(steps, 1):
                    st.markdown(f"- **Bước {s_idx}:** {s}")

            variants = c.get("variants", [])
            if variants:
                st.markdown("#### 🔄 Biến Thể Thực Hành Đan Xen (Interleaving Practice):")
                for v in variants:
                    st.markdown(f"- {v}")

            insight = c.get("elite_insight") or c.get("key_takeaways")
            if insight:
                st.success(f"💎 **Elite Insight (Bản Lĩnh Tinh Hoa):** {insight}")

            # Thanh tác vụ liên kết chéo
            st.markdown("---")
            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                if st.button(
                    "🚀 Chuyển sang Phân Rã AI 9 Lenses",
                    key=f"btn_ai_dispatch_{c_id}",
                    use_container_width=True,
                    help="Tự động nạp bối cảnh case này vào trang Phân Rã Thực Chiến để AI 9 Lăng kính soi chiếu sâu",
                ):
                    st.session_state["prefill_problem"] = (
                        f"[{c_id}] {c.get('title')}\n\n"
                        f"Bối cảnh: {c.get('problem')}\n\n"
                        f"Câu hỏi kích hoạt: {c.get('trigger_question')}"
                    )
                    st.success("✅ Đã chuẩn bị sẵn nội dung! Hãy bấm chọn mục **'🚀 Phân rã Vấn đề'** trên thanh Sidebar bên trái để chạy phân tích AI.")

            with col_act2:
                if st.button(
                    "💡 Dán vào Sổ Tay Tri Thức (Second Brain)",
                    key=f"btn_note_dispatch_{c_id}",
                    use_container_width=True,
                    help="Lưu case này vào Second Brain để ghi chép và tự giải",
                ):
                    st.session_state["note_custom_title_input"] = f"Case [{c_id}]: {c.get('title')}"
                    st.session_state["note_raw_text_area"] = (
                        f"### Case Thực Chiến: {c.get('title')}\n\n"
                        f"**Vấn đề:** {c.get('problem')}\n\n"
                        f"**Nguyên lý:** {', '.join(prins)}\n\n"
                        f"**Phân rã First Principles:**\n" +
                        "\n".join([f"- {s}" for s in c.get("first_principles_breakdown", [])]) +
                        f"\n\n**Elite Insight:** {insight}"
                    )
                    st.success("✅ Đã chuẩn bị sẵn nội dung! Hãy chuyển sang **'💡 Sổ tay Tri thức'** trên Sidebar để bấm phân rã và lưu trữ.")

# ---------------------------------------------------------------------------
# Sidebar Summary & Next Modules Roadmap
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Bản Đồ 150 Case Thực Chiến")
    st.markdown(f"Tổng cộng: **{len(all_cases)} case** đã chuẩn hóa sẵn sàng!")
    for g_code, g_info in sorted(groups_dict.items()):
        cnt = sum(1 for c in all_cases if c.get("group_code") == g_code)
        st.markdown(f"- **Nhóm {g_code} ({g_info['title']}):** {cnt} case")

    st.divider()
    st.markdown("### 💡 Khuyến Nghị Rèn Luyện")
    st.markdown("""
    1. **Tự giải trước:** Đọc *Vấn đề* và *Câu hỏi kích hoạt*, tự nghĩ ra lời giải bằng vốn hiểu biết của mình.
    2. **Đối chiếu First Principles:** Mở rộng để xem cách tư duy phân rã về nguyên tử gốc.
    3. **Luyện biến thể (Interleaving):** Đọc các biến thể mở rộng để xây dựng trực giác chuyển giao (transfer of learning).
    """)
