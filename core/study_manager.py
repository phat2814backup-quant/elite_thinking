# -*- coding: utf-8 -*-
"""
Module Quản Lý Chuyên Khảo Sâu Đa Ngành (Polymath Deep Study Dossier Manager).
Tự động đồng bộ, liên kết và trực quan hóa các tài liệu nghiên cứu chuyên sâu
trong thư mục study/ với các Mô Hình Tinh Hoa (Mental Models / Principles).
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Any, Optional
import streamlit as st

# Các thư mục chứa tài liệu nghiên cứu chuyên khảo
STUDY_SEARCH_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "study"),
    "D:/02_HocTap/elite/study",
    "D:/02_HocTap/elite_thinking/study",
    os.path.join("study"),
]


def normalize_model_id(raw_id: str) -> str:
    """Chuẩn hóa ID mô hình về dạng chuẩn (e.g., MM_ART-01, ART_01 -> ART-01)."""
    clean = raw_id.upper().strip()
    if clean.startswith("MM_"):
        clean = clean[3:]
    clean = clean.replace("_", "-")
    return clean


def get_all_study_dossiers() -> List[Dict[str, Any]]:
    """Quét và nạp toàn bộ danh sách các tài liệu chuyên khảo trong các thư mục study."""
    dossiers: Dict[str, Dict[str, Any]] = {}

    for s_dir in STUDY_SEARCH_DIRS:
        if not os.path.exists(s_dir) or not os.path.isdir(s_dir):
            continue

        for fname in os.listdir(s_dir):
            if not fname.endswith(".md"):
                continue

            full_path = os.path.join(s_dir, fname)
            file_id = os.path.splitext(fname)[0]

            # Nhận diện Model ID liên kết từ tên file (ví dụ: ART_01_fibonaci -> ART-01)
            model_match = re.match(r"^([A-Z]{3,4}[_-]\d{1,3})", file_id, re.IGNORECASE)
            linked_model_id = normalize_model_id(model_match.group(1)) if model_match else file_id

            if linked_model_id in dossiers and os.path.exists(dossiers[linked_model_id]["file_path"]):
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Trích xuất tiêu đề từ dòng H1 đầu tiên
                title_match = re.search(r"^#\s+\**([^\n\*]+)\**", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else fname

                # Trích xuất tóm tắt cốt lõi
                core_match = re.search(r"Tóm tắt cốt lõi[^\n:]*:\s*([^\n]+)", content, re.IGNORECASE)
                core_summary = core_match.group(1).strip() if core_match else ""

                dossiers[linked_model_id] = {
                    "file_id": file_id,
                    "filename": fname,
                    "file_path": full_path,
                    "linked_model_id": linked_model_id,
                    "title": title,
                    "core_summary": core_summary,
                    "content": content,
                    "size_bytes": os.path.getsize(full_path),
                    "size_kb": round(os.path.getsize(full_path) / 1024, 1),
                }
            except Exception:
                pass

    return list(dossiers.values())


def get_study_dossier_by_model_id(model_id: str) -> Optional[Dict[str, Any]]:
    """Tìm tài liệu chuyên khảo sâu liên kết với Model ID cụ thể."""
    norm_id = normalize_model_id(model_id)
    all_d = get_all_study_dossiers()
    for d in all_d:
        if normalize_model_id(d.get("linked_model_id", "")) == norm_id:
            return d
    return None


def render_study_dossier_box(model_id: str, is_expanded: bool = False):
    """Render khối hiển thị Chuyên khảo sâu tích hợp trực tiếp vào thẻ mô hình GMM."""
    dossier = get_study_dossier_by_model_id(model_id)
    if not dossier:
        return

    st.markdown("---")
    badge_title = f"📖 BẢN CHUYÊN KHẢO NGHIÊN CỨU SÂU: {dossier['title']} ({dossier['size_kb']} KB)"
    
    with st.expander(badge_title, expanded=is_expanded):
        st.markdown(f"📍 **Đường dẫn file gốc trên máy:** `{dossier['file_path']}`")
        if dossier.get("core_summary"):
            st.info(f"⚡ **Tóm tắt cốt lõi:** {dossier['core_summary']}")

        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            st.download_button(
                label=f"📥 Tải Về File Gốc Markdown ({dossier['filename']})",
                data=dossier["content"],
                file_name=dossier["filename"],
                mime="text/markdown",
                key=f"dl_study_{dossier['file_id']}"
            )
        with col_act2:
            show_raw = st.checkbox("Hiển thị mã nguồn Markdown thô", key=f"raw_toggle_{dossier['file_id']}")

        if show_raw:
            st.code(dossier["content"], language="markdown")
        else:
            st.markdown(dossier["content"])


def render_study_library_view():
    """Hiển thị giao diện Thư viện Chuyên khảo sâu độc lập."""
    st.markdown("### 📚 Thư Viện Chuyên Khảo Nghiên Cứu Sâu (Polymath Deep Dossiers)")
    st.caption("Các công trình nghiên cứu bản chất vật lý, thần kinh học, toán học và động lực học hành vi giúp làm giàu chiều sâu cho hệ tư duy.")

    dossiers = get_all_study_dossiers()
    if not dossiers:
        st.warning("Hiện chưa có tài liệu chuyên khảo nào trong thư mục `study/`.")
        return

    st.markdown(f"**Hiện có `{len(dossiers)}` công trình chuyên khảo đã được lập chỉ mục.**")
    
    search_kw = st.text_input("🔍 Tìm kiếm chuyên khảo (tên, từ khóa, mô hình liên kết):", "", placeholder="Ví dụ: Fibonacci, Saccade, Shopee, Cân bằng động...")

    for d in dossiers:
        if search_kw.strip():
            kw = search_kw.lower()
            match = (
                kw in d["title"].lower()
                or kw in d["content"].lower()
                or kw in d["linked_model_id"].lower()
            )
            if not match:
                continue

        with st.expander(f"📑 [{d['linked_model_id']}] {d['title']} ({d['size_kb']} KB)", expanded=True):
            st.markdown(f"📍 **File nguồn:** `{d['file_path']}`")
            if d.get("core_summary"):
                st.info(f"⚡ **Cốt lõi:** {d['core_summary']}")

            c1, c2 = st.columns([1, 1])
            with c1:
                st.download_button(
                    label=f"📥 Tải File Gốc ({d['filename']})",
                    data=d["content"],
                    file_name=d["filename"],
                    mime="text/markdown",
                    key=f"lib_dl_{d['file_id']}"
                )
            with c2:
                show_raw_lib = st.checkbox("Xem Markdown thô", key=f"lib_raw_{d['file_id']}")

            if show_raw_lib:
                st.code(d["content"], language="markdown")
            else:
                st.markdown(d["content"])
