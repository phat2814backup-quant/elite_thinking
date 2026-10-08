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



def _find_matching_scan(
    title: str,
    query: str,
    scans: Optional[list[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """Tìm bản quét First Principles tương ứng với một nhánh từ danh sách đã lưu."""
    if not scans:
        return None
    t_clean = title.strip().lower()
    q_clean = query.strip().lower()
    for s in scans:
        s_query = s.get("query", "").strip().lower()
        if not s_query:
            continue
        if t_clean in s_query or s_query in t_clean:
            return s.get("full_result", s)
        if len(q_clean) > 15 and (q_clean[:35] in s_query or s_query[:35] in q_clean):
            return s.get("full_result", s)
    return None


def _format_scan_details_markdown(res: Dict[str, Any], indent: str = "") -> str:
    """Format một khối bóc tách First Principles thành markdown chuẩn."""
    if not res or not isinstance(res, dict):
        return ""
    
    blocks = []
    if res.get("trend_summary"):
        blocks.append(f"{indent}> 🎯 **Bản chất cốt lõi (First Principles):** *{res.get('trend_summary')}*")
    
    if res.get("transaction_costs_impact"):
        blocks.append(f"{indent}- ⚡ **Tác động chi phí giao dịch (Coase):** {res.get('transaction_costs_impact')}")

    comm_list = res.get("commoditized_assets", [])
    if comm_list:
        blocks.append(f"{indent}- 📉 **Nguồn lực bị trượt giá về 0:**")
        for c in comm_list:
            if isinstance(c, dict):
                blocks.append(f"{indent}  * 📉 **{c.get('asset', '')}**: {c.get('why', '')}")
            else:
                blocks.append(f"{indent}  * 📉 {c}")

    scarcities = res.get("complementary_scarcities", [])
    if scarcities:
        blocks.append(f"{indent}- 💎 **Nút thắt khan hiếm mới lên ngôi:**")
        for sc in scarcities:
            if isinstance(sc, dict):
                blocks.append(f"{indent}  * 💎 **{sc.get('asset', '')}**: {sc.get('why', '')}")
            else:
                blocks.append(f"{indent}  * 💎 {sc}")

    moves = res.get("elite_strategic_moves", [])
    if moves:
        blocks.append(f"{indent}- ♟️ **Nước cờ chiến lược của giới Elite:**")
        for m in moves:
            blocks.append(f"{indent}  * ♟️ {m}")

    models = res.get("activated_mental_models", [])
    if models:
        blocks.append(f"{indent}- 🕸️ **Mô hình hạt nhân kích hoạt:**")
        for m in models:
            if isinstance(m, dict):
                blocks.append(f"{indent}  * `{m.get('model_name', '')}`: {m.get('mechanism', '')}")
            else:
                blocks.append(f"{indent}  * `{m}`")

    playbook = res.get("action_playbook_for_individual", [])
    if playbook:
        blocks.append(f"{indent}- 🧭 **Playbook hành động thực chiến:**")
        for p in playbook:
            blocks.append(f"{indent}  * 🚀 {p}")

    spears = res.get("socratic_spears", [])
    if spears:
        blocks.append(f"{indent}- 🗡️ **Mũi giáo Socrates khảo nghiệm thế cuộc:**")
        for sp in spears:
            s_q = sp.get("ruthless_question", "")
            s_title = sp.get("spear_title", "Mũi giáo")
            s_guide = sp.get("guidance", "")
            guide_str = f" *(Gợi ý: {s_guide})*" if s_guide else ""
            blocks.append(f"{indent}  * 👉 **{s_title}:** \"{s_q}\"{guide_str}")

    return "\n".join(blocks)


def export_macro_tree_to_markdown(
    tree_data: Dict[str, Any],
    all_scans: Optional[list[Dict[str, Any]]] = None
) -> str:
    """
    Xuất toàn bộ Bản Đồ Cây Thế Cuộc (F0 -> F1 -> F2) ra định dạng Markdown phân cấp như cây thư mục.
    Nhánh nào đã bóc tách First Principles sẽ tự động bung toàn bộ nội dung chi tiết.
    Càng bóc tách nhiều nhánh, cây càng đồ sộ và chi tiết.
    """
    domain = tree_data.get("domain", "Chưa đặt tên")
    scout_overview = tree_data.get("scout_overview", "Không có tóm tắt tổng quan.")
    time_created = tree_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time_updated = tree_data.get("updated_at", time_created)
    trends = tree_data.get("trends", [])

    # Tính toán thống kê và xây dựng sơ đồ ASCII
    scans_pool = all_scans or []
    total_f1 = len(trends)
    total_f2 = 0
    scanned_nodes_count = 0
    total_nodes = total_f1

    ascii_lines = [f"└── [F0] {domain.upper()}"]

    for i, t in enumerate(trends):
        t_rank = t.get("rank", i + 1)
        t_title = t.get("title", "")
        t_badge = t.get("badge", "🔥")
        sub_list = t.get("drill_down", {}).get("sub_trends", [])
        total_f2 += len(sub_list)
        total_nodes += len(sub_list)

        # Kiểm tra bóc tách F1
        f1_scan = t.get("scan_result") or _find_matching_scan(t_title, t.get("suggested_query", ""), scans_pool)
        if f1_scan:
            scanned_nodes_count += 1
            f1_tag = " (⚡ Đã bóc tách chi tiết)"
        else:
            f1_tag = ""

        prefix_f1 = "├──" if i < len(trends) - 1 else "└──"
        ascii_lines.append(f"    {prefix_f1} [#{t_rank}] {t_title} [{t_badge}]{f1_tag}")

        sub_connector = "│  " if i < len(trends) - 1 else "   "
        for j, sub in enumerate(sub_list):
            sub_rank = sub.get("sub_rank", j + 1)
            sub_title = sub.get("title", "")
            sub_scan = sub.get("scan_result") or _find_matching_scan(sub_title, sub.get("suggested_query", ""), scans_pool)
            if sub_scan:
                scanned_nodes_count += 1
                sub_tag = " (⚡ Đã bóc tách chi tiết)"
            else:
                sub_tag = ""
            prefix_f2 = "├──" if j < len(sub_list) - 1 else "└──"
            ascii_lines.append(f"    {sub_connector} {prefix_f2} [F2.{sub_rank}] {sub_title}{sub_tag}")

    ascii_tree_text = "\n".join(ascii_lines)
    coverage_pct = int((scanned_nodes_count / total_nodes * 100)) if total_nodes > 0 else 0

    # Xây dựng phần nội dung chi tiết từng nhánh
    branches_detail = []
    for i, t in enumerate(trends):
        t_rank = t.get("rank", i + 1)
        t_title = t.get("title", "")
        t_badge = t.get("badge", "🔥 Sóng Thần Tiên Phong")
        t_status = t.get("status", "Bùng nổ")
        t_one = t.get("one_liner", "")
        t_sug = t.get("suggested_query", t_title)

        f1_scan = t.get("scan_result") or _find_matching_scan(t_title, t_sug, scans_pool)
        
        branch_md = [
            f"## 🚀 NHÁNH #{t_rank}: {t_title}",
            f"- **Huy hiệu thế cuộc:** `{t_badge}`",
            f"- **Trạng thái:** `{t_status}`",
            f"- **Nhận định cốt lõi:** *{t_one}*",
            ""
        ]

        if f1_scan:
            branch_md.append("### 🔬 Bản Bóc Tách Chi Tiết First Principles (Đã Quét Sâu):")
            branch_md.append(_format_scan_details_markdown(f1_scan, indent=""))
            branch_md.append("")
        else:
            branch_md.append(f"> 💡 **Định hướng bóc tách đề xuất:** \"{t_sug}\"")
            branch_md.append("*(Nhánh này chưa quét sâu First Principles. Bấm nút [📡 Quét] trên app để bóc tách thêm vào cây)*\n")

        # Duyệt F2 nếu có
        sub_list = t.get("drill_down", {}).get("sub_trends", [])
        if sub_list:
            branch_md.append(f"### 🌿 CÁC NÚT THẮT & VI XU HƯỚNG F2 CỦA NHÁNH #{t_rank}:")
            insight_f2 = t.get("drill_down", {}).get("drill_down_insight", "")
            if insight_f2:
                branch_md.append(f"> 🎯 **Điểm nghẽn cốt lõi tầng F2:** *{insight_f2}*\n")

            for j, sub in enumerate(sub_list):
                sub_rank = sub.get("sub_rank", j + 1)
                sub_title = sub.get("title", "")
                sub_why = sub.get("why_crucial", "")
                sub_sug = sub.get("suggested_query", sub_title)
                sub_scan = sub.get("scan_result") or _find_matching_scan(sub_title, sub_sug, scans_pool)

                branch_md.append(f"#### └── [F2.{sub_rank}] {sub_title}")
                branch_md.append(f"- **Tại sao cốt tử (Why Crucial):** {sub_why}")

                if sub_scan:
                    branch_md.append("\n  **🔬 Bóc tách First Principles chi tiết của vi xu hướng này:**")
                    branch_md.append(_format_scan_details_markdown(sub_scan, indent="  "))
                    branch_md.append("")
                else:
                    branch_md.append(f"- 👉 **Câu truy vấn đề xuất:** \"{sub_sug}\"\n")

        branches_detail.append("\n".join(branch_md))

    branches_rendered = "\n\n---\n\n".join(branches_detail)

    md = f"""# 🌐 BẢN ĐỒ CÂY THẾ CUỘC TOÀN DIỆN: {domain.upper()}

- **Lĩnh vực trinh sát (F0):** `{domain}`
- **Thời gian khởi tạo cây:** `{time_created}`
- **Cập nhật gần nhất:** `{time_updated}`
- **Công cụ:** Elite First-Principles Macro Radar & Multi-Tier Trend Scout
- **Quy mô cây:** `{total_f1} Xu hướng F1` | `{total_f2} Vi xu hướng F2` | `{scanned_nodes_count} Nhánh đã bóc tách First Principles` ({coverage_pct}% Độ bao phủ)

---

## 🧭 1. TỔNG QUAN CỤC DIỆN THẾ CUỘC (F0)
> {scout_overview}

---

## 🌲 2. SƠ ĐỒ CÂY THƯ MỤC THẾ CUỘC (HIERARCHICAL TREE MAP)
```
{ascii_tree_text}
```

---

## 📚 3. GIẢI PHÃU TOÀN DIỆN TỪNG NHÁNH BẢN ĐỒ CÂY

{branches_rendered}

---
*Bản quyền phân tích thuộc về Elite Thinking Framework v2.5 — Hierarchical Frontier Knowledge Tree.*
"""
    return md.strip()


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

    spears = res.get("socratic_spears", [])
    spear_lines = []
    for s in spears:
        spear_lines.append(f"""### {s.get('spear_title', 'Mũi Giáo Socrates')}
- **Điểm mù truy sát:** *{s.get('targeted_vulnerability', '')}*
- **👉 Câu hỏi khảo nghiệm:** \"{s.get('ruthless_question', '')}\"
- **Gợi ý phản biện:** {s.get('guidance', '')}
""")
    spears_text = "\n".join(spear_lines) if spear_lines else ""
    spears_section = f"""
## 🗡️ 7. Mũi Giáo Socrates Khảo Nghiệm Thế Cuộc
{spears_text}
""" if spears_text else ""

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
{spears_section}
---
*Bản quyền phân tích thuộc về Elite Thinking Framework v2.5 — First Principles Macro Radar & Socratic Engine.*
"""
    return md.strip()


def export_problem_decomposition_to_markdown(
    prob: str,
    res: Dict[str, Any],
    created_at: str = ""
) -> str:
    """Xuất kết quả phân rã vấn đề qua 3 Trụ Cột, 9 Lăng kính và Võ Đài Socrates ra định dạng Markdown chuẩn mực."""
    time_str = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Kiểm tra xem có cấu trúc 3 Trụ Cột chuẩn mới không
    if "pillars" in res:
        pillars = res.get("pillars", {})
        pillar_blocks = []
        for p_key in ["root", "flow", "strike"]:
            p_data = pillars.get(p_key, {})
            p_title = p_data.get("pillar_title", p_key.upper())
            p_essence = p_data.get("essence", "")
            p_leverage = p_data.get("pillar_leverage", "")
            
            lenses_text = []
            for l_key, l_val in p_data.get("lenses", {}).items():
                m_str = ", ".join(l_val.get("activated_models", []))
                m_badge = f"\n  - *Mô hình hạt nhân:* `{m_str}`" if m_str else ""
                lenses_text.append(f"#### {l_val.get('lens_name', l_key)}\n{l_val.get('analysis', '')}{m_badge}")
            
            p_md = f"""### {p_title}
> *{p_essence}*

{chr(10).join(lenses_text)}

**🎯 Đòn bẩy của trụ:** {p_leverage}
"""
            pillar_blocks.append(p_md)

        pillars_rendered = "\n---\n\n".join(pillar_blocks)

        # Mũi giáo Socrates & Các Vòng Đấu Trí
        socratic_rounds = res.get("socratic_rounds", [])
        if socratic_rounds:
            round_blocks = []
            for r in socratic_rounds:
                r_num = r.get("round_number", 1)
                r_theme = r.get("round_theme", f"Vòng {r_num}")
                r_eval = r.get("evaluation") or {}
                r_ans = r.get("user_answers", {})
                r_spears = r.get("spears", [])
                
                sp_text = []
                for sp in r_spears:
                    sp_id = sp.get("spear_id", "")
                    sp_title = sp.get("spear_title", sp_id)
                    sp_q = sp.get("ruthless_question", "")
                    sp_u = r_ans.get(sp_id, "*(Chưa nhập câu trả lời)*")
                    sp_text.append(f"""#### {sp_title}
- **👉 Câu hỏi khảo nghiệm:** \"{sp_q}\"
- **🛡️ Luận cứ của bạn:** {sp_u}
""")
                eval_str = ""
                if r_eval:
                    eval_str = f"""
> **Kết Quả Thẩm Định Vòng {r_num}:** {r_eval.get('verdict_title', '')} ({r_eval.get('grit_score', 0)}/100 Điểm Grit - Thưởng +{r_eval.get('xp_awarded', 0)} XP)  
> *{r_eval.get('overall_comment', '')}*
"""
                round_blocks.append(f"""### 🥊 {r_theme}
{eval_str}
{chr(10).join(sp_text)}
""")
            spears_rendered = "\n---\n\n".join(round_blocks)
        else:
            spears = res.get("socratic_spears", [])
            spear_lines = []
            for s in spears:
                spear_lines.append(f"""### {s.get('spear_title', 'Mũi Giáo Socrates')}
- **Điểm mù truy sát:** *{s.get('targeted_vulnerability', '')}*
- **👉 Câu hỏi khảo nghiệm:** \"{s.get('ruthless_question', '')}\"
- **Gợi ý phản biện:** {s.get('guidance', '')}
""")
            spears_rendered = "\n".join(spear_lines) if spear_lines else "- *(Không có dữ liệu)*"

        actions = res.get("actionable_next_steps", res.get("actionable_insights", []))
        actions_text = "\n".join([f"- 💡 {a}" for a in actions]) if actions else "- *(Không có dữ liệu)*"

        md = f"""# 🎯 BẢN PHÂN RÃ THỰC CHIẾN & VÕ ĐÀI SOCRATES: {prob}

- **Thời gian phân rã:** `{time_str}`
- **Khung phân tích:** 3 Trụ Cột (Soi Gốc - Đọc Dòng - Ra Đòn), 9 Lăng Kính & 152 Mô Hình Tinh Hoa

---

## ⚡ 1. Chân Lý Nguyên Bản (Executive Summary)
> {res.get('executive_summary', res.get('first_principles_breakdown', 'Không có nội dung.'))}

---

## 🏛️ 2. Phân Rã Thực Chiến Qua 3 Trụ Cột & 9 Lăng Kính

{pillars_rendered}

---

## 🗡️ 3. Võ Đài Đối Kháng Socrates (3 Mũi Giáo Sát Thủ)
{spears_rendered}

---

## 🚀 4. Kế Hoạch Hành Động Đòn Bẩy Cao
{actions_text}

---
*Bản quyền phân tích thuộc về Elite Thinking Framework v2.5 — Socratic Problem Decomposition Engine.*
"""
        return md.strip()

    # Fallback cho bản phân rã cũ
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


def export_formulation_to_markdown(
    res: Dict[str, Any],
    user_intent: str = "",
    created_at: str = ""
) -> str:
    """Xuất bản điêu khắc đề bài Polymath thành văn bản Markdown chuẩn mực."""
    time_str = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = res.get("problem_title", "Bản Điêu Khắc Đề Bài Polymath")
    intent = user_intent or res.get("fuzzy_summary", "")

    layer_sci = res.get("layer_sciences", {})
    layer_eng = res.get("layer_engineering", {})
    layer_art = res.get("layer_arts_humanities", {})
    master_p = res.get("master_prompt", {})
    contrast = res.get("contrast_analysis", {})
    farrow = res.get("farrow_compression", {})

    hard_constraints_md = "\n".join([f"- {c}" for c in master_p.get("hard_constraints", [])])
    negative_rules_md = "\n".join([f"- ⛔ {r}" for r in master_p.get("negative_rules", [])])
    acceptance_md = "\n".join([f"- ✅ {a}" for a in master_p.get("acceptance_criteria", [])])

    md = f"""# 🔬 BẢN ĐIÊU KHẮC ĐỀ BÀI POLYMATH (MUSK & DA VINCI SPEC)
# {title}

- **Thời gian lập:** `{time_str}`
- **Ý định ban đầu của con người:** *"{intent}"*
- **Triết lý kiến tạo:** Arts + Sciences + Engineering ➔ Master AI/Robot Formulation

---

## 🏛️ 1. LĂNG KÍNH ĐA NGÀNH (POLYMATH LENSES)

### ⚛️ Tầng 1: Sciences & Natural Laws (Chân Lý Gốc & Giới Hạn Tự Nhiên)
- **Giới hạn vật lý / nhiệt động lực:** {layer_sci.get('physics_limits', '')}
- **Sinh học nhận thức & Ngưỡng chú ý:** {layer_sci.get('cognitive_biology', '')}
- **Chân lý xác suất & Quy tắc nhân số 0:** {layer_sci.get('probability_truth', '')}

### ⚙️ Tầng 2: Engineering & Systems (Kỹ Thuật & Kiến Trúc Thực Thi)
- **Kiến trúc hệ thống module:** {layer_eng.get('architecture', '')}
- **Chi phí biên & Điểm ma sát giao dịch:** {layer_eng.get('friction_and_costs', '')}
- **Biên an toàn & Cơ chế phòng vệ:** {layer_eng.get('fail_safes', '')}

### 🎨 Tầng 3: Arts, Taste & Humanities (Nghệ Thuật & Gu Thẩm Mỹ Nhân Văn)
- **Gu thẩm mỹ & Vị giác trải nghiệm (Taste):** {layer_art.get('aesthetic_taste', '')}
- **Linh hồn câu chuyện & Độ căng kịch nghệ:** {layer_art.get('narrative_soul', '')}
- **Ranh giới đạo đức & Phẩm giá con người:** {layer_art.get('human_ethics', '')}

---

## 🤖 2. BẢN ĐẶC TẢ TỐI THƯỢNG CHO AI / ROBOT (THE MASTER PROMPT)

> **🎯 Sứ mệnh & Nhân dạng:**  
> {master_p.get('role_and_mission', '')}

### 🔒 Ràng buộc cứng (Hard Constraints)
{hard_constraints_md}

### 🎨 Tiêu chuẩn Thẩm mỹ & Gu (Taste & Style)
> {master_p.get('taste_and_style', '')}

### ⛔ Kịch bản CẤM (Negative Directives)
{negative_rules_md}

### 🧪 Tiêu chí Nghiệm thu Hoàn thành (Acceptance Tests)
{acceptance_md}

---

## 🥊 3. ĐỐI SÁNH TRỰC QUAN: NGHIỆP DƯ VS. POLYMATH

| Yếu tố | Câu lệnh Nghiệp dư | Điêu khắc Polymath |
| :--- | :--- | :--- |
| **Câu lệnh mẫu** | `{contrast.get('amateur_prompt', '')}` | *(Bản Master Prompt bên trên)* |
| **Tại sao thất bại** | {contrast.get('why_amateur_fails', '')} | **Khắc phục triệt để:** Khóa chặt giới hạn vật lý, tối ưu chi phí kỹ thuật và định hình gu thẩm mỹ. |
| **Lợi thế xuất chúng** | 0% chiều sâu, AI trả lời chung chung | {contrast.get('polymath_advantage', '')} |

---

## ⚡ 4. MỎ NEO FARROW 10-PHÚT
- **🚪 Mỏ neo 1 (Khoa học):** {farrow.get('anchor_1', '')}
- **🖥️ Mỏ neo 2 (Kỹ thuật):** {farrow.get('anchor_2', '')}
- **🪑 Mỏ neo 3 (Nghệ thuật & Gu):** {farrow.get('anchor_3', '')}
- **⚡ Khẩu quyết phản xạ:** *"{farrow.get('reflex_mantra', '')}"*

---
*Xuất bản từ Elite Thinking: Farrow Edition — Problem Formulation Lab.*
"""
    return md.strip()
