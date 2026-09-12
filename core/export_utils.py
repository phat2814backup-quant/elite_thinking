# -*- coding: utf-8 -*-
"""
Module Xuất Bản Định Dạng Chuẩn (Markdown & Document Export).
Hỗ trợ xuất file .md chuẩn mực, có cấu trúc đầy đủ, sẵn sàng cho Obsidian, Notion, GitHub và in ấn PDF.
"""

from __future__ import annotations
import re
from datetime import datetime
from typing import Dict, Any


import unicodedata


def sanitize_filename(name: str, max_len: int = 40) -> str:
    """Tạo tên file an toàn từ tiêu đề bài viết."""
    # Chuẩn hóa bỏ dấu tiếng Việt để tạo tên file tương thích tối đa trên mọi HĐH/Trình duyệt
    nfkd = unicodedata.normalize("NFKD", name)
    no_accent = "".join([c for c in nfkd if not unicodedata.combining(c)])
    no_accent = no_accent.replace("đ", "d").replace("Đ", "D")
    clean = re.sub(r"[^a-zA-Z0-9_\- ]", "", no_accent)
    clean = re.sub(r"\s+", "_", clean).strip("_")
    return clean[:max_len] if clean else "ban_xuat"



def export_macro_radar_to_markdown(
    query: str,
    res: Dict[str, Any],
    created_at: str = ""
) -> str:
    """Xuất kết quả bóc tách thế cuộc ra định dạng Markdown chuẩn mực."""
    time_str = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    commoditized = res.get("commoditized_assets", [])
    comm_lines = []
    for c in commoditized:
        if isinstance(c, dict):
            comm_lines.append(f"- **📉 {c.get('asset', '')}**: {c.get('why', '')}")
        else:
            comm_lines.append(f"- 📉 {c}")
    comm_text = "\n".join(comm_lines) if comm_lines else "- *(Không có dữ liệu)*"

    scarcities = res.get("complementary_scarcities", [])
    scarcity_lines = []
    for s in scarcities:
        if isinstance(s, dict):
            scarcity_lines.append(f"- **💎 {s.get('asset', '')}**: {s.get('why', '')}")
        else:
            scarcity_lines.append(f"- 💎 {s}")
    scarcity_text = "\n".join(scarcity_lines) if scarcity_lines else "- *(Không có dữ liệu)*"

    elite_moves = res.get("elite_strategic_moves", [])
    moves_text = "\n".join([f"- ♟️ {m}" for m in elite_moves]) if elite_moves else "- *(Không có dữ liệu)*"

    models = res.get("activated_mental_models", [])
    model_lines = []
    for m in models:
        if isinstance(m, dict):
            model_lines.append(f"- `{m.get('model_name', '')}`: {m.get('mechanism', '')}")
        else:
            model_lines.append(f"- `{m}`")
    models_text = "\n".join(model_lines) if model_lines else "- *(Không có dữ liệu)*"

    playbook = res.get("action_playbook_for_individual", [])
    playbook_text = "\n".join([f"- 🚀 {p}" for p in playbook]) if playbook else "- *(Không có dữ liệu)*"

    md = f"""# 📡 BẢN BÓC TÁCH THẾ CUỘC: {query}

- **Thời gian phân tích:** `{time_str}`
- **Công cụ:** Elite First-Principles Macro Radar
- **Phương pháp:** Bóc tách chuyển dịch giá trị biên & Nút thắt khan hiếm mới

---

## 🎯 1. Bản Chất Cốt Lõi (First Principles)
> {res.get('trend_summary', 'Không có tóm tắt.')}

## ⚡ 2. Tác Động Lên Chi Phí Giao Dịch (Coase Theorem)
{res.get('transaction_costs_impact', 'Không có dữ liệu.')}

---

## ⚖️ 3. Ma Trận Dịch Chuyển Giá Trị Biên

### 📉 Nguồn Lực Bị Trượt Giá Về 0 (Bình Dân Hóa)
{comm_text}

### 💎 Nút Thắt Khan Hiếm Mới Lên Ngôi
{scarcity_text}

---

## 👁️ 4. Nước Cờ Chiến Lược Của Giới Elite
{moves_text}

## 🕸️ 5. Các Mô Hình Hạt Nhân Được Kích Hoạt
{models_text}

## 🧭 6. Playbook Hành Động Thực Chiến Cho Cá Nhân
{playbook_text}

---
*Bản quyền phân tích thuộc về Elite Thinking Framework v2.2 — First Principles Architecture.*
"""
    return md.strip()


def export_problem_decomposition_to_markdown(
    prob: str,
    res: Dict[str, Any],
    created_at: str = ""
) -> str:
    """Xuất kết quả phân rã vấn đề qua 9 Lăng kính ra định dạng Markdown chuẩn mực."""
    time_str = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    core_principles = res.get("core_principles_found", [])
    core_lines = []
    for p in core_principles:
        if isinstance(p, dict):
            dom = f" *({p.get('domain', '')})*" if p.get("domain") else ""
            desc = f": {p.get('description', '')}" if p.get("description") else ""
            core_lines.append(f"- **📌 {p.get('name', '')}**{dom}{desc}")
        else:
            core_lines.append(f"- **📌 {p}**")
    core_text = "\n".join(core_lines) if core_lines else "- *(Không có dữ liệu)*"

    lenses = res.get("elite_lenses", {})
    insights = res.get("actionable_insights", [])
    insights_text = "\n".join([f"- 💡 {i}" for i in insights]) if insights else "- *(Không có dữ liệu)*"

    human_q = res.get("human_decision_needed", [])
    human_text = "\n".join([f"- 👉 *{q}*" for q in human_q]) if human_q else "- *(Không có dữ liệu)*"

    md = f"""# 🎯 BẢN PHÂN RÃ THỰC CHIẾN: {prob}

- **Thời gian phân rã:** `{time_str}`
- **Khung phân tích:** 9 Lăng Kính Tinh Hoa & First Principles Framework (Charlie Munger & Ray Dalio)

---

## ⚡ 1. Chân Lý Nguyên Bản (First Principles)
> {res.get('first_principles_breakdown', 'Không có nội dung.')}

## 🧬 2. Các Nguyên Lý Hạt Nhân Chi Phối
{core_text}

---

## 👁️ 3. Phân Tích Đa Chiều Qua 5 Lăng Kính Lớn

### 🔄 Lật Ngược Vấn Đề (Inversion - Munger)
{lenses.get('inversion', 'Không có dữ liệu.')}

### 🎯 Hệ Quả Bậc Hai & Bậc Cao (Second-Order Thinking)
{lenses.get('second_order', 'Không có dữ liệu.')}

### ⏳ Đa Khung Thời Gian (Multi-Timescale Dynamics)
{lenses.get('multi_timescale', 'Không có dữ liệu.')}

### 🎲 Xác Suất Bayes & Tỷ Lệ Nền (Bayesian Base Rate)
{lenses.get('bayesian', 'Không có dữ liệu.')}

### ⚖️ Đòn Bẩy & Điểm Nghẽn (Leverage & Bottlenecks)
{lenses.get('leverage', 'Không có dữ liệu.')}

---

## 🚀 4. Hành Động Đòn Bẩy Cao (Actionable Insights)
{insights_text}

## ❓ 5. Câu Hỏi Quyết Định Chỉ Bạn Mới Trả Lời Được
{human_text}

---
*Bản quyền phân tích thuộc về Elite Thinking Framework v2.2 — Problem Decomposition Engine.*
"""
    return md.strip()


def export_farrow_compression_to_markdown(
    title: str,
    raw_text: str,
    res: Dict[str, Any],
    created_at: str = ""
) -> str:
    """Xuất bản nén Dave Farrow ra định dạng Markdown chuẩn mực."""
    time_str = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t_name = title if title else res.get("title", "Bản Nén Farrow")
    tagline = res.get("tagline", "")

    chunks = res.get("chunks", [])
    chunk_blocks = []
    icons = ["🚪", "🖥️", "🪑"]
    for idx, c in enumerate(chunks[:3]):
        icon = icons[idx] if idx < len(icons) else "📌"
        label = c.get("label", f"TRỤ {idx+1}")
        anchor = c.get("anchor", f"Mỏ neo #{idx+1}")
        principle = c.get("principle", "")
        crazy = c.get("crazy_image", "")
        trigger = c.get("trigger_question", "")

        chunk_blocks.append(f"""### {icon} {label}
- **📍 Mỏ neo không gian:** `{anchor}`
- **⚙️ Nguyên lý gốc:**  
  {principle}
- **🧠 Hình ảnh dị biệt (Dave Farrow Anchor):**  
  > {crazy}
- **⚡ Phản xạ 5 giây:**  
  *"{trigger}"*
""")

    chunks_text = "\n".join(chunk_blocks)

    raw_preview = f"\n<details>\n<summary>📄 Xem lại văn bản thô ban đầu</summary>\n\n```text\n{raw_text}\n```\n</details>\n" if raw_text else ""

    md = f"""# ⚡ BẢN NÉN FARROW: {t_name}

- **Khẩu quyết cốt lõi:** *"{tagline}"*
- **Thời gian nén:** `{time_str}`
- **Quy chuẩn ghi nhớ:** Dave Farrow Memory Palace (Rule of 3 & Bizarre Association)

---

## 🏛️ Bộ 3 Trụ Cột Hạt Nhân

{chunks_text}

---

## 🎯 Đòn Bẩy Bất Đối Xứng (Actionable Strike)
> {res.get('asymmetric_action', 'Không có dữ liệu.')}
{raw_preview}
---
*Bản quyền thuộc về Dave Farrow Memory Palace & Elite Thinking Framework v2.2.*
"""
    return md.strip()
