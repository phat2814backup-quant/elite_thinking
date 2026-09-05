# -*- coding: utf-8 -*-
"""Thư viện nguyên lý"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]

from utils.knowledge import get_principles, get_domains, search_principles

st.title("📚 Thư viện nguyên lý cốt lõi (dùng chung)")
st.caption("Kho 100 nguyên lý khởi thủy từ Vật lý, Sinh học, Toán học, Triết học & Khoa học máy tính")
domains = get_domains()
col_f1, col_f2 = st.columns([1, 2])
with col_f1:
    domain = st.selectbox("Lọc trụ cột", domains)
with col_f2:
    q = st.text_input("Tìm kiếm nguyên lý", placeholder="Bayes, đòn bẩy, bảo toàn, entropy...")

if q.strip():
    principles = search_principles(q)
else:
    principles = get_principles(domain if domain != "Tất cả" else None)

st.caption(f"Hiển thị {len(principles)} nguyên lý")

for p in principles:
    with st.expander(f"{p.get('principle_name', '?')} · {p.get('domain', '')}"):
        st.markdown(f"**Mô tả:** {p.get('description', '')}")
        if p.get("formal_definition"):
            st.info(p["formal_definition"])
        if p.get("intuitive_summary"):
            st.write(f"💡 {p['intuitive_summary']}")
        c1, c2 = st.columns(2)
        with c1:
            if p.get("boundary_conditions"):
                st.caption(f"Điều kiện biên: {p['boundary_conditions']}")
        with c2:
            if p.get("falsification_test"):
                st.caption(f"Falsify: {p['falsification_test']}")

st.divider()
st.info("🎯 **Muốn thử thách nhận diện 100 Nguyên lý khoa học?** Chuyển sang **Tab [⚡ Đấu trường Luyện nhớ]** để làm trắc nghiệm kiểm chứng điều kiện biên và tính khả bác!")

