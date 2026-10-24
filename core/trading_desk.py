# -*- coding: utf-8 -*-
"""
Module Bàn Tác Chiến & Huấn Luyện H4 Big Boy Institutional Desk
Tích hợp trực tiếp vào ứng dụng Elite Thinking
"""
from __future__ import annotations

import os
import sys
import json
import subprocess
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PAYLOAD_FILE = DATA_DIR / "adn_desk_payload.json"
STANDALONE_HTML_FILE = DATA_DIR / "adn_desk_app.html"

LOCAL_SYNC_BAT = Path("D:/08_AI_MCP/SYNC_TO_STREAMLIT.bat")
LOCAL_SYNC_SCRIPT = Path("D:/08_AI_MCP/sync_adn_to_streamlit.py")


def render_adn_trading_desk_room():
    st.markdown("## 🎯 Bàn Tác Chiến H4 & Huấn Luyện Big Boy (Air Sniper Desk)")
    st.caption("Giám sát 8 tài sản cốt lõi · Dải ATR tuần neo chuẩn cực trị · Volume Profile 65 bins · Huấn luyện Replay đa khung H4/H1/M15")

    # Kiểm tra xem có đang ở môi trường Local có MT5 không
    is_local_env = LOCAL_SYNC_BAT.exists() or LOCAL_SYNC_SCRIPT.exists()

    # Nút bấm cập nhật / Đồng bộ
    top_c1, top_c2 = st.columns([3, 2])
    with top_c1:
        if is_local_env:
            st.markdown("🟢 **Môi trường Local (Máy cá nhân MT5)**: Có thể cập nhật dữ liệu trực tiếp 1-click.")
        else:
            st.markdown("🌐 **Môi trường Cloud Web**: Đang hiển thị dữ liệu được đồng bộ từ MT5 máy local.")

    with top_c2:
        if is_local_env:
            if st.button("🚀 CẬP NHẬT TỪ MT5 & PUSH LÊN WEB (1-CLICK)", type="primary", use_container_width=True):
                with st.spinner("Đang kết nối MT5, trích xuất dữ liệu 8 tài sản và tự động push lên GitHub..."):
                    try:
                        # Thực thi script đồng bộ
                        sync_exec = sys.executable
                        res = subprocess.run(
                            [sync_exec, str(LOCAL_SYNC_SCRIPT)],
                            cwd="D:/08_AI_MCP",
                            capture_output=True,
                            text=True,
                            encoding="utf-8"
                        )
                        if res.returncode == 0:
                            st.success("🎉 ĐÃ ĐỒNG BỘ DỮ LIỆU MT5 & PUSH LÊN GITHUB THÀNH CÔNG! Web Cloud sẽ tự động cập nhật sau 30-60s.")
                            st.rerun()
                        else:
                            st.error(f"Lỗi khi chạy sync: {res.stderr}")
                    except Exception as ex:
                        st.error(f"Lỗi thực thi: {ex}")
        else:
            if st.button("🔄 Tải lại dữ liệu mới nhất", use_container_width=True):
                st.rerun()

    # Đọc Payload
    payload = None
    if PAYLOAD_FILE.exists():
        try:
            with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            st.error(f"Lỗi khi đọc file dữ liệu: {e}")

    if not payload:
        st.warning("⚠️ Chưa tìm thấy gói dữ liệu `adn_desk_payload.json`. Vui lòng chạy file `SYNC_TO_STREAMLIT.bat` tại `D:\\08_AI_MCP` để đồng bộ dữ liệu.")
        return

    updated_at_vn = payload.get("updated_at_vn", payload.get("updated_at", "Chưa rõ"))
    symbols = payload.get("symbols", ["XAUUSD", "BTCUSD", "USOIL", "GBPUSD", "GBPJPY", "GBPAUD", "USTEC", "US500"])

    # Metric Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Tài Sản Giám Sát", f"{len(symbols)} Mã", "XAU, BTC, WTI, FX, Tech")
    with m2:
        st.metric("Phiên Đồng Bộ MT5", updated_at_vn.split(" ")[0] if " " in updated_at_vn else updated_at_vn)
    with m3:
        st.metric("Giờ Cập Nhật", updated_at_vn.split(" ")[1] if " " in updated_at_vn else "Live")
    with m4:
        st.metric("Trạng Thái Desk", "SẴN SÀNG TÁC CHIẾN", "Cloud Ready")

    st.divider()

    # Sub-tabs
    desk_sub_tabs = st.tabs([
        "🖥️ Bàn Tác Chiến & Huấn Luyện (Interactive Desk)",
        "🧬 Hồ Sơ Gene ADN 8 Tài Sản (Playbook Vault)",
        "📓 Nhật Ký Chiến Trường & Dự Phóng Tuần",
        "🔄 Cơ Chế Đồng Bộ & Tự Động Hóa"
    ])

    # SUB-TAB 1: INTERACTIVE DESK
    with desk_sub_tabs[0]:
        st.markdown("""
        > [!TIP]
        > **Chuyển đổi chế độ:** Bạn có thể bấm chuyển qua lại giữa **Bàn Phân Tích (Live)** và **Huấn Luyện (Replay)** ngay trên thanh công cụ phía trên biểu đồ. Hỗ trợ đầy đủ phóng to/thu nhỏ, vẽ dải ATR, Volume Profile 65 bins mịn, tua nến H4 và đặt lệnh thực hành kèm lệnh chờ Limit/Stop.
        """)

        html_content = ""
        if STANDALONE_HTML_FILE.exists():
            try:
                html_content = STANDALONE_HTML_FILE.read_text(encoding="utf-8")
            except Exception as e:
                st.error(f"Lỗi đọc file HTML: {e}")

        if html_content:
            components.html(html_content, height=1050, scrolling=True)
        else:
            st.info("Đang nạp giao diện tự chứa, vui lòng tải lại trang...")

    # SUB-TAB 2: ADN PLAYBOOKS
    with desk_sub_tabs[1]:
        st.subheader("🧬 Cẩm Nang Cấu Trúc Gene (ADN) Định Lượng 8 Tài Sản")
        selected_sym = st.selectbox("Chọn tài sản để xem chi tiết:", symbols, index=0, key="desk_adn_sym_select")
        adn_info = payload.get("adn_profiles", {}).get(selected_sym, {})
        meta = adn_info.get("meta", {})

        if meta:
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            with col_a1:
                st.info(f"**Weekly ATR(7)**\n\n### `{meta.get('atr_baseline', '--')}`")
            with col_a2:
                st.warning(f"**Vùng đệm Stop Loss**\n\n### `{meta.get('sl_buffer', '--')}`")
            with col_a3:
                st.success(f"**Giờ vàng bùng nổ**\n\n### `{meta.get('peak_hour', '--')}`")
            with col_a4:
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

    # SUB-TAB 3: DIARIES & FORWARD PROJECTIONS
    with desk_sub_tabs[2]:
        st.subheader("📓 Nhật Ký Chiến Trường H4 & Dự Phóng Kịch Bản Tuần Tiếp Theo")
        diary_sym = st.selectbox("Chọn tài sản kiểm toán nhật ký:", symbols, index=0, key="desk_diary_sym_select")
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

    # SUB-TAB 4: SYNC GUIDE
    with desk_sub_tabs[3]:
        st.subheader("🔄 Cơ Chế Đồng Bộ Dữ Liệu Tự Động Từ Máy Local MT5")
        st.markdown(f"""
        - **Tại máy Local (có cài MT5)**: 
          Bạn chỉ cần bấm nút màu đỏ **`🚀 CẬP NHẬT TỪ MT5 & PUSH LÊN WEB (1-CLICK)`** ở góc trên bên phải, hoặc nhấp đúp file:
          `D:\\08_AI_MCP\\SYNC_TO_STREAMLIT.bat`
        - **Hệ thống tự động**:
          1. Kết nối MT5 local lấy giá nến H4, ATR, Volume Profile 65 bins của 8 tài sản.
          2. Đóng gói vào `adn_desk_payload.json` và `adn_desk_app.html`.
          3. Tự động `git commit` & `git push` lên GitHub repository `origin/main`.
          4. Streamlit Cloud (`https://fs28142401.streamlit.app/`) tự động cập nhật trong 30-60 giây.
        """)
        st.success(f"Dữ liệu hiện tại trên Cloud được cập nhật lúc: **{updated_at_vn}**")
