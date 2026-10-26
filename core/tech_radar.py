# -*- coding: utf-8 -*-
"""
HỆ THỐNG TECH RADAR TUẦN: TOP 10 MÃ NGUỒN MỞ ĐỊNH HÌNH TƯƠNG LAI (ELITE RADAR)
Lưu trữ theo tuần, phân tích đa chiều (Bottleneck, Paradigm Shift, Future Implication)
Hỗ trợ tự động cập nhật hàng tuần qua Gemini AI & GitHub Actions.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tech_radar.json")


def load_tech_radar_data() -> Dict[str, Any]:
    """Tải toàn bộ dữ liệu Tech Radar từ file JSON."""
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Lỗi đọc dữ liệu Tech Radar: {e}")
    return {"last_updated": "", "weeks": []}


def save_tech_radar_data(data: Dict[str, Any]) -> bool:
    """Lưu dữ liệu Tech Radar vào file JSON."""
    try:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu dữ liệu Tech Radar: {e}")
        return False


def get_current_iso_week_id() -> str:
    """Trả về mã tuần ISO hiện tại, ví dụ: 2026-W44."""
    now = datetime.datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def get_current_date_range_str() -> str:
    """Trả về chuỗi khoảng ngày của tuần hiện tại (Thứ 2 đến Chủ Nhật)."""
    now = datetime.datetime.now()
    start_of_week = now - datetime.timedelta(days=now.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return f"{start_of_week.strftime('%d/%m/%Y')} - {end_of_week.strftime('%d/%m/%Y')}"


TECH_SCOUT_PROMPT = """Bạn là Chuyên gia Trinh sát Công nghệ & Chiến lược gia Tương lai cấp cao của Hệ thống Elite.
Nhiệm vụ của bạn là: Tuyển chọn đúng TOP 10 DỰ ÁN MÃ NGUỒN MỞ ĐỘT PHÁ NHẤT ĐANG NỔI LÊN TRÊN GITHUB / HACKER NEWS / ARXAI trong tuần {week_id} ({date_range}).

TIÊU CHUẨN LỰA CHỌN KHẮC NGHIỆT:
1. TUYỆT ĐỐI BỎ QUA CÁC DỰ ÁN "WRAPPER" ĐỒ CHƠI: Không chọn các repo chỉ là giao diện UI bọc API thông thường.
2. CHỈ CHỌN CÁC DỰ ÁN TẠO CHUYỂN DỊCH KIẾN TRÚC (PARADIGM SHIFT): Giải quyết trực tiếp nút thắt vật lý, kinh tế, thông lượng hoặc chi phí.
3. PHÂN BỔ CÂN BẰNG 4 TRỤ CỘT TƯƠNG LAI:
   - 🤖 AI Agents & Autonomous Execution (3 dự án)
   - ⚡ High-Performance Infra & Systems (3 dự án)
   - 📈 Quant & FinTech (2 dự án)
   - 🛰️ Frontier & Physical AI (2 dự án)

MỖI DỰ ÁN BẮT BUỘC PHẢI PHÂN TÍCH THEO 3 CÂU HỎI MỔ XẺ SẮC BÉN:
- bottleneck_solved: Giải quyết nút thắt cổ chai gì mà công nghệ cũ làm quá dở/quá đắt/bế tắc?
- core_innovation: Đột phá kiến trúc / thuật toán cốt lõi là gì?
- future_implication: Ngụ ý tương lai: Ai hưởng lợi? Ai bị đào thải? Ứng dụng thực tế cho cá nhân/hệ thống Elite?

TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON HỢP LỆ (KHÔNG THÊM CHỮ NÀO BÊN NGOÀI):
{{
  "week_id": "{week_id}",
  "title": "Tuần ... ({date_range}): ...",
  "date_range": "{date_range}",
  "macro_theme": "Bản tổng kết 2-3 câu phân tích xu thế dòng chảy hạt nhân lớn nhất của mã nguồn mở tuần này",
  "items": [
    {{
      "rank": 1,
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "category": "🤖 AI Agents & Autonomous Execution",
      "stars": "... ⭐",
      "one_liner": "Tóm tắt 1 câu tinh hoa nhất",
      "bottleneck_solved": "...",
      "core_innovation": "...",
      "future_implication": "...",
      "maturity": "Sẵn sàng Production / Đang tăng tốc (Growth) / Thử nghiệm (Experimental)"
    }}
  ]
}}
"""


def generate_weekly_tech_radar_with_ai(active_api_key: Optional[str] = None, force_week_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Tự động sử dụng Gemini AI để quét và sinh báo cáo Top 10 của tuần."""
    from core.farrow_engine import get_all_gemini_api_keys
    try:
        import google.generativeai as genai
    except ImportError:
        st.error("Chưa cài đặt google-generativeai")
        return None

    api_keys = []
    if active_api_key:
        api_keys.append(active_api_key)
    api_keys.extend(get_all_gemini_api_keys())

    if not api_keys:
        st.error("Không tìm thấy Gemini API Key để thực hiện AI Scout.")
        return None

    week_id = force_week_id or get_current_iso_week_id()
    date_range = get_current_date_range_str()
    prompt = TECH_SCOUT_PROMPT.format(week_id=week_id, date_range=date_range)

    last_err = None
    for key in api_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                result_json = json.loads(resp.text)
                if "items" in result_json and len(result_json["items"]) > 0:
                    # Cập nhật vào kho lưu trữ
                    db = load_tech_radar_data()
                    weeks = db.get("weeks", [])
                    # Thay thế nếu tuần đã tồn tại, hoặc chèn mới lên đầu
                    existing_idx = next((i for i, w in enumerate(weeks) if w.get("week_id") == week_id), None)
                    if existing_idx is not None:
                        weeks[existing_idx] = result_json
                    else:
                        weeks.insert(0, result_json)
                    db["weeks"] = weeks
                    db["last_updated"] = datetime.datetime.now().isoformat()
                    save_tech_radar_data(db)
                    return result_json
        except Exception as e:
            last_err = e
            continue

    st.warning(f"Không thể tạo tự động bằng AI lúc này: {last_err}")
    return None


def export_week_to_markdown(week_data: Dict[str, Any]) -> str:
    """Xuất báo cáo tuần thành định dạng Markdown tinh hoa."""
    lines = [
        f"# 🛰️ ELITE TECH RADAR — {week_data.get('title', 'Báo Cáo Tuần')}",
        f"**Khoảng thời gian:** {week_data.get('date_range', '')} | **Mã tuần:** `{week_data.get('week_id', '')}`",
        "",
        "## 🌊 CHỦ ĐIỂM DÒNG CHẢY HẠT NHÂN (MACRO THEME)",
        f"> {week_data.get('macro_theme', '')}",
        "",
        "---",
        "## 🏆 TOP 10 DỰ ÁN MÃ NGUỒN MỞ ĐỊNH HÌNH TƯƠNG LAI",
        ""
    ]

    for item in week_data.get("items", []):
        lines.extend([
            f"### #{item.get('rank', '')}. [{item.get('name', '')}]({item.get('url', '')})",
            f"- **Phân loại:** `{item.get('category', '')}` | **Độ chín:** `{item.get('maturity', '')}` | **Sao:** `{item.get('stars', '')}`",
            f"- **Bản chất 1 câu:** {item.get('one_liner', '')}",
            f"- **⚡ Nút thắt giải quyết:** {item.get('bottleneck_solved', '')}",
            f"- **🔬 Đột phá kiến trúc:** {item.get('core_innovation', '')}",
            f"- **🔮 Ngụ ý tương lai:** {item.get('future_implication', '')}",
            ""
        ])

    lines.extend([
        "---",
        "*Bản quyền phân tích thuộc Hệ thống Tinh hoa Elite — fs28142401.streamlit.app*"
    ])
    return "\n".join(lines)


def render_tech_radar_room(active_api_key: Optional[str] = None):
    """Giao diện Streamlit của phòng chức năng Tech Radar Tuần."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
        <div style="display: inline-block; background: #2563eb; color: #ffffff; font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; margin-bottom: 6px;">
            🛰️ ELITE OPEN-SOURCE RADAR
        </div>
        <h2 style="color: #f8fafc; margin: 4px 0 8px 0; font-weight: 800; font-size: 1.6rem;">
            TOP 10 MÃ NGUỒN MỞ ĐỊNH HÌNH TƯƠNG LAI
        </h2>
        <p style="color: #94a3b8; margin: 0; font-size: 0.95rem; line-height: 1.5;">
            Lọc bỏ 95% repo wrapper và đồ chơi tạm bợ. Giới hạn cứng <b>đúng 10 dự án mỗi tuần</b> tạo đột phá kiến trúc thực chất.
            Lưu trữ lịch sử theo tuần để rèn luyện độ nhạy dự đoán thế cuộc công nghệ.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = load_tech_radar_data()
    weeks = db.get("weeks", [])

    if not weeks:
        st.warning("Chưa có dữ liệu tuần nào trong hệ thống.")
        if st.button("🚀 Khởi tạo Tuần Đầu Tiên", type="primary"):
            with st.spinner("Đang kích hoạt AI Scout phân tích..."):
                generate_weekly_tech_radar_with_ai(active_api_key=active_api_key)
                st.rerun()
        return

    # Top Toolbar
    col_week, col_btn_scout, col_btn_export = st.columns([3, 2, 2])

    week_options = {w["week_id"]: f"{w.get('week_id')} — {w.get('title', '')[:45]}..." for w in weeks}
    current_iso = get_current_iso_week_id()

    with col_week:
        selected_week_id = st.selectbox(
            "📅 Chọn tuần xem radar:",
            options=list(week_options.keys()),
            format_func=lambda x: week_options[x]
        )

    # Lấy tuần đang chọn
    selected_week = next((w for w in weeks if w.get("week_id") == selected_week_id), weeks[0])

    with col_btn_scout:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Cập Nhật Tuần Mới (AI Scout)", help="Chạy AI quét và cập nhật lại Top 10 dự án tuần hiện tại"):
            with st.spinner("Đang kích hoạt Elite AI Scout quét GitHub Trending & Arxiv..."):
                res = generate_weekly_tech_radar_with_ai(active_api_key=active_api_key, force_week_id=current_iso)
                if res:
                    st.success("Đã hoàn tất quét và cập nhật tuần mới thành công!")
                    st.rerun()

    with col_btn_export:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        md_content = export_week_to_markdown(selected_week)
        st.download_button(
            label="📥 Xuất Markdown (.md)",
            data=md_content,
            file_name=f"Elite_Tech_Radar_{selected_week_id}.md",
            mime="text/markdown"
        )

    # Macro Theme Banner
    st.markdown(f"""
    <div style="background: rgba(30, 58, 138, 0.25); border-left: 4px solid #3b82f6; padding: 12px 18px; border-radius: 6px; margin: 15px 0;">
        <span style="font-weight: 700; color: #60a5fa; font-size: 0.9rem;">🌊 CHỦ ĐIỂM DÒNG CHẢY TUẦN NÀY:</span><br>
        <span style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">{selected_week.get('macro_theme', '')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Metrics Strip
    items = selected_week.get("items", [])
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Tổng dự án tuyển chọn", f"{len(items)} / tuần")
    with m2:
        cat_count = len(set(it.get("category", "") for it in items))
        st.metric("Trụ cột công nghệ", f"{cat_count} Lĩnh vực")
    with m3:
        current_status = "Đang chạy Tuần này" if selected_week_id == current_iso else "Lưu trữ Lịch sử"
        st.metric("Trạng thái", current_status)
    with m4:
        st.metric("Tần suất đồng bộ", "Hàng tuần (Thứ 2)")

    st.divider()

    # Bộ lọc danh mục & Tìm kiếm
    f_col1, f_col2 = st.columns([2, 3])
    all_categories = ["Tất cả lĩnh vực"] + sorted(list(set(it.get("category", "") for it in items if it.get("category"))))

    with f_col1:
        selected_cat = st.selectbox("Lọc theo trụ cột:", all_categories)
    with f_col2:
        search_query = st.text_input("🔍 Tìm kiếm tên repo hoặc từ khóa công nghệ:", placeholder="Ví dụ: Rust, Agent, Vector, GPU, Quant...").strip().lower()

    filtered_items = items
    if selected_cat != "Tất cả lĩnh vực":
        filtered_items = [it for it in filtered_items if it.get("category") == selected_cat]
    if search_query:
        filtered_items = [
            it for it in filtered_items
            if search_query in it.get("name", "").lower()
            or search_query in it.get("one_liner", "").lower()
            or search_query in it.get("core_innovation", "").lower()
            or search_query in it.get("bottleneck_solved", "").lower()
        ]

    st.caption(f"Đang hiển thị **{len(filtered_items)}** dự án phù hợp tiêu chí:")

    # Hiển thị từng Card dự án
    for it in filtered_items:
        rank = it.get("rank", 0)
        name = it.get("name", "")
        url = it.get("url", "#")
        category = it.get("category", "General")
        stars = it.get("stars", "")
        maturity = it.get("maturity", "Chưa phân loại")
        one_liner = it.get("one_liner", "")
        bottleneck = it.get("bottleneck_solved", "")
        innovation = it.get("core_innovation", "")
        implication = it.get("future_implication", "")

        maturity_color = "#10b981" if "Production" in maturity else ("#f59e0b" if "Growth" in maturity or "tăng tốc" in maturity else "#a855f7")

        card_title = f"#{rank} · {name}  |  {stars}  [{category}]"
        with st.expander(card_title, expanded=(rank <= 3 and not search_query)):
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #f1f5f9;">{name}</span>
                &nbsp;·&nbsp;
                <a href="{url}" target="_blank" style="color: #60a5fa; text-decoration: none; font-size: 0.95rem;">🔗 Mở GitHub Repo ↗</a>
                &nbsp;·&nbsp;
                <span style="background: {maturity_color}22; color: {maturity_color}; border: 1px solid {maturity_color}55; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                    {maturity}
                </span>
            </div>
            <div style="font-size: 1rem; color: #cbd5e1; margin-bottom: 15px; font-style: italic;">
                💡 "{one_liner}"
            </div>
            """, unsafe_allow_html=True)

            c_bot, c_inno = st.columns(2)
            with c_bot:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 10px 14px; border-radius: 4px; height: 100%;">
                    <div style="color: #f87171; font-weight: 700; font-size: 0.85rem; margin-bottom: 4px;">⚡ NÚT THẮT CỔ CHAI GIẢI QUYẾT:</div>
                    <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">""" + bottleneck + """</div>
                </div>
                """, unsafe_allow_html=True)

            with c_inno:
                st.markdown("""
                <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; padding: 10px 14px; border-radius: 4px; height: 100%;">
                    <div style="color: #60a5fa; font-weight: 700; font-size: 0.85rem; margin-bottom: 4px;">🔬 ĐỘT PHÁ KIẾN TRÚC CỐT LÕI:</div>
                    <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">""" + innovation + """</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10b981; padding: 10px 14px; border-radius: 4px; margin-top: 12px;">
                <div style="color: #34d399; font-weight: 700; font-size: 0.85rem; margin-bottom: 4px;">🔮 NGỤ Ý TƯƠNG LAI & ĐÒN BẨY ELITE:</div>
                <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">""" + implication + """</div>
            </div>
            """, unsafe_allow_html=True)

            # Phím tắt chuyển nhanh sang máy nén Farrow
            f_col_act1, f_col_act2 = st.columns([3, 1])
            with f_col_act2:
                if st.button(f"⚡ Nén Farrow (#{rank})", key=f"btn_farrow_{selected_week_id}_{rank}"):
                    st.session_state["farrow_input_text"] = f"DỰ ÁN: {name}\nBẢN CHẤT: {one_liner}\nNÚT THẮT: {bottleneck}\nKIẾN TRÚC: {innovation}\nNGỤ Ý TƯƠNG LAI: {implication}"
                    st.session_state["app_mode_redirect"] = "⚡ Máy Ép Farrow 1-Click (AI Compressor)"
                    st.rerun()
