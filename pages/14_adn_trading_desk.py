# -*- coding: utf-8 -*-
"""
H4 Institutional Air Sniper Desk & Replay Trainer
Trang Bàn Tác Chiến Định Chế & Huấn Luyện Tư Duy Big Boy cho 8 Tài Sản Cốt Lõi
"""
from __future__ import annotations

import os
import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx.get("username", "Trader")
display_name = ctx.get("display_name", username)

CURRENT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CURRENT_DIR / "data"
PAYLOAD_FILE = DATA_DIR / "adn_desk_payload.json"
STANDALONE_HTML_FILE = DATA_DIR / "adn_desk_app.html"

st.title("🎯 H4 Big Boy Institutional Desk & Replay Trainer")
st.caption("Ma trận 8 tài sản · Dải biến động ATR tuần neo chuẩn cực trị · Chấm 12h NY · Volume Profile 65 bins · Replay nến H4/H1/M15")

# Kiểm tra dữ liệu payload
payload = None
if PAYLOAD_FILE.exists():
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu payload: {e}")

if not payload:
    st.warning("⚠️ Chưa tìm thấy gói dữ liệu `adn_desk_payload.json`. Hãy chạy file `SYNC_TO_STREAMLIT.bat` từ máy local để đồng bộ dữ liệu MT5 lên đây!")
    st.stop()

updated_at_vn = payload.get("updated_at_vn", payload.get("updated_at", "Chưa rõ"))
symbols = payload.get("symbols", ["XAUUSD", "BTCUSD", "USOIL", "GBPUSD", "GBPJPY", "GBPAUD", "USTEC", "US500"])

# Overview Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Tài Sản Giám Sát", f"{len(symbols)} Mã", "XAU, BTC, WTI, FX, Tech")
with c2:
    st.metric("Phiên Đồng Bộ", updated_at_vn.split(" ")[0] if " " in updated_at_vn else updated_at_vn)
with c3:
    st.metric("Thời Gian MT5", updated_at_vn.split(" ")[1] if " " in updated_at_vn else "Live")
with c4:
    st.metric("Trạng Thái Desk", "SẴN SÀNG TÁC CHIẾN", "Cloud Ready")

# Main Tabs
main_tabs = st.tabs([
    "🖥️ Bàn Tác Chiến & Huấn Luyện (Air Sniper Desk)",
    "🧬 Hồ Sơ ADN 8 Tài Sản (Playbook Vault)",
    "📓 Nhật Ký Chiến Trường & Dự Phóng Tuần",
    "🔄 Hướng Dẫn Đồng Bộ Dữ Liệu"
])

# ==========================================
# SUB-TAB 1: INTERACTIVE DESK (AIR SNIPER & REPLAY TRAINER)
# ==========================================
with main_tabs[0]:
    st.markdown("""
    > [!TIP]
    > **Giao diện Bàn Tác Chiến Độc Lập:** Bạn có thể bấm chuyển qua lại giữa **Bàn Phân Tích (Live Desk)** và **Huấn Luyện (Replay Trainer)** ngay trên thanh công cụ phía trên biểu đồ. Hỗ trợ đầy đủ phóng to/thu nhỏ, vẽ dải ATR, Volume Profile 65 bins, tua nến H4 và đặt lệnh thực hành.
    """)
    
    # Đọc HTML tự chứa
    html_content = ""
    if STANDALONE_HTML_FILE.exists():
        try:
            html_content = STANDALONE_HTML_FILE.read_text(encoding="utf-8")
        except Exception as e:
            st.error(f"Lỗi đọc file HTML: {e}")
            
    if html_content:
        components.html(html_content, height=1050, scrolling=True)
    else:
        st.info("Đang tạo gói giao diện tự chứa, vui lòng tải lại trang sau giây lát...")

# ==========================================
# SUB-TAB 2: ADN PROFILES (PLAYBOOK VAULT)
# ==========================================
with main_tabs[1]:
    st.subheader("🧬 Cẩm Nang Cấu Trúc Gene (ADN) Định Lượng 8 Tài Sản")
    st.caption("Tổng hợp các tham số bất biến: Hạn ngạch ATR(7) W1, Vùng đệm Stop Loss, Giờ vàng thanh khoản, Phân bổ cực trị trong tuần.")
    
    selected_sym = st.selectbox("Chọn tài sản để xem chi tiết:", symbols, index=0, key="adn_sym_select")
    
    adn_info = payload.get("adn_profiles", {}).get(selected_sym, {})
    meta = adn_info.get("meta", {})
    
    if meta:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.info(f"**Weekly ATR(7)**\n\n### `{meta.get('atr_baseline', '--')}`")
        with m2:
            st.warning(f"**Vùng đệm Stop Loss**\n\n### `{meta.get('sl_buffer', '--')}`")
        with m3:
            st.success(f"**Giờ vàng bùng nổ**\n\n### `{meta.get('peak_hour', '--')}`")
        with m4:
            st.info(f"**Mở rộng Classic (100% ATR)**\n\n### `{meta.get('classic_exp', '--')}`")
            
        st.markdown(f"**📌 Đặc tính & Lưu ý tác chiến:** *{meta.get('notes', '')}*")
        st.markdown(f"**📊 Phân bổ cực trị:** *{meta.get('day_stats', '')}*")
        st.markdown("---")
        
    st.markdown("#### 📘 Nội Dung Cẩm Nang Chi Tiết:")
    raw_md = adn_info.get("raw_markdown", "")
    if raw_md:
        st.markdown(raw_md)
    else:
        st.caption("Chưa có cẩm nang chi tiết cho mã này.")

# ==========================================
# SUB-TAB 3: DIARIES & FORWARD PROJECTIONS
# ==========================================
with main_tabs[2]:
    st.subheader("📓 Nhật Ký Chiến Trường H4 & Dự Phóng Kịch Bản Tuần Tiếp Theo")
    st.caption("Xem dự phóng kế hoạch tác chiến đón đầu tuần mới và các bản ghi phân tích theo dòng thời gian.")
    
    diary_sym = st.selectbox("Chọn tài sản kiểm toán nhật ký:", symbols, index=0, key="diary_sym_select")
    diary_data = payload.get("diaries", {}).get(diary_sym, {})
    
    forward_proj = diary_data.get("forward_projection", {})
    if forward_proj and forward_proj.get("raw"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(8, 51, 68, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1.5px solid #06b6d4; border-radius: 14px; padding: 18px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(6, 182, 212, 0.15);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(6, 182, 212, 0.3); padding-bottom: 8px;">
                <span style="font-size: 16px; font-weight: 900; color: #38bdf8;">🔭 DỰ PHÓNG TUẦN TIẾP THEO (KỊCH BẢN TÁC CHIẾN H4)</span>
                <span style="background: rgba(6, 182, 212, 0.2); color: #38bdf8; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(6, 182, 212, 0.4);">TRỌNG TÂM CHIẾN DỊCH</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(forward_proj.get("raw"))
        st.markdown("---")
        
    weeks = diary_data.get("weeks", [])
    if weeks:
        st.markdown(f"#### 🗓️ Lịch Sử Các Tuần Chiến Trường ({len(weeks)} tuần)")
        for idx, w in enumerate(weeks):
            if "DỰ PHÓNG" in w.get("title", ""):
                continue
            is_latest = (idx == 0 or "MỚI NHẤT" in w.get("title", ""))
            expander_title = f"{'⭐ [MỚI NHẤT] ' if is_latest else '📁 '}{w.get('title', 'Tuần')}"
            with st.expander(expander_title, expanded=is_latest):
                st.markdown(w.get("raw", ""))
    else:
        st.info("Chưa có lịch sử các tuần trước đó.")

# ==========================================
# SUB-TAB 4: SYNC & AUTOMATION GUIDE
# ==========================================
with main_tabs[3]:
    st.subheader("🔄 Cơ Chế Đồng Bộ Dữ Liệu Tự Động Từ Máy Local MT5")
    st.markdown("""
    Ứng dụng được thiết kế theo kiến trúc **Local Data Engine + Cloud Serverless Visualizer**:
    - **Máy Local (Windows MT5)**: Chịu trách nhiệm kết nối trực tiếp với MetaTrader 5 để lấy dữ liệu nến H4, tính toán dải ATR tuần, Volume Profile 65 bins và xuất ra file gói nén.
    - **Cloud Web (`https://fs28142401.streamlit.app/`)**: Đọc gói dữ liệu offline và hiển thị biểu đồ Lightweight Charts siêu mượt mà cho phép bạn truy cập từ bất kỳ đâu (điện thoại, laptop ngoài quán cafe, máy tính bảng) mà không cần cài đặt MT5.
    
    ---
    ### ⚡ Cách Đồng Bộ 1-Click Từ Máy Local:
    Mỗi khi bạn muốn cập nhật dữ liệu nến mới nhất từ MT5 lên web Streamlit, chỉ cần làm một thao tác duy nhất trên máy tính của bạn:
    
    1. Nhấp đúp chuột vào file:
       `D:\\08_AI_MCP\\SYNC_TO_STREAMLIT.bat`
    2. File script sẽ tự động:
       - Kết nối MT5 lấy giá, ATR, Volume Profile của 8 tài sản.
       - Tự động xuất file gói `adn_desk_payload.json` và `adn_desk_app.html`.
       - Tự động chạy `git commit` & `git push` lên repository `phat2814backup-quant/elite_thinking`.
    3. Streamlit Cloud sẽ tự động nhận diện và cập nhật giao diện trong vòng 30 - 60 giây!
    """)
    
    st.success(f"Dữ liệu hiện tại trên Cloud được cập nhật lúc: **{updated_at_vn}**")
