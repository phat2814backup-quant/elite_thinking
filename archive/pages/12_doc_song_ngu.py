# -*- coding: utf-8 -*-
"""
Trang 12: Đọc Sách Song Ngữ Siêu Tốc (Ultralearning Reader)
- Đọc nguyên bản tiếng Anh đối sánh tiếng Việt song song (2 Cột)
- Chế độ Thử thách Siêu Học (Focus Challenge): Ẩn tiếng Việt để kích hoạt não bộ
- AI Feynman Explainer: Mổ xẻ cấu trúc ngữ pháp và bản chất từ nguyên không dùng thuật ngữ
- Bộ đếm từ vựng tần suất cao & Phát hiện điểm mù (Target Drill)
- Luyện tập phản xạ Active Recall (Cloze Test) & Tự động lưu vào Second Brain
"""

from __future__ import annotations

import streamlit as st
import json
import re
from datetime import datetime

from utils.app_common import bootstrap
from utils.bilingual_manager import (
    load_available_books,
    get_book_by_id,
    get_user_vocab_vault,
    record_word_lookup,
    toggle_word_mastery,
    delete_word_from_vault,
    explain_phrase_feynman,
    export_feynman_to_second_brain,
    load_chapter_jit_cache,
    save_chapter_jit_cache,
    translate_paragraphs_batch,
)

# -----------------------------------------------------------------------------
# Formatting & Alignment Helpers
# -----------------------------------------------------------------------------
def format_paragraphs_html(text: str) -> str:
    """Format multiline text into clean, tight HTML paragraphs without giant br gaps."""
    if not text:
        return ""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    if not paras:
        return ""
    html_parts = []
    for p in paras:
        clean_p = p.replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(f'<p class="bilingual-p">{clean_p}</p>')
    return "".join(html_parts)

def align_scene_paragraphs(en_text: str, vi_text: str) -> list[tuple[str, str]]:
    """
    Pairs English and Vietnamese paragraphs into synchronized rows.
    Guarantees every row has corresponding content and stays horizontally locked.
    """
    en_list = [p.strip() for p in en_text.split("\n\n") if p.strip()]
    vi_list = [p.strip() for p in vi_text.split("\n\n") if p.strip()]

    n_en = len(en_list)
    n_vi = len(vi_list)

    if n_en == 0 and n_vi == 0:
        return []
    if n_en == 0:
        return [("", "\n\n".join(vi_list))]
    if n_vi == 0:
        return [("\n\n".join(en_list), "")]
    if n_en == n_vi:
        return list(zip(en_list, vi_list))

    if n_en <= n_vi:
        pairs = []
        for i in range(n_en):
            vi_start = round(i * n_vi / n_en)
            vi_end = round((i + 1) * n_vi / n_en)
            sub_vi = "\n\n".join(vi_list[vi_start:vi_end])
            pairs.append((en_list[i], sub_vi))
        return pairs
    else:
        pairs = []
        for i in range(n_vi):
            en_start = round(i * n_en / n_vi)
            en_end = round((i + 1) * n_en / n_vi)
            sub_en = "\n\n".join(en_list[en_start:en_end])
            pairs.append((sub_en, vi_list[i]))
        return pairs

# -----------------------------------------------------------------------------
# Bootstrap & Auth Context
# -----------------------------------------------------------------------------
ctx = bootstrap()
username = ctx["username"]
display_name = ctx.get("display_name", username)
model_choice = ctx.get("model_choice", "gemini-2.5-flash")
active_keys = ctx.get("active_keys", [])

# -----------------------------------------------------------------------------
# Sticky Sidebar: Trợ Lý Feynman Mổ Xẻ Cụm Từ
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔬 Trợ Lý Feynman (Sticky)")
    st.caption("Ghim cố định theo màn hình · Tra cứu mọi lúc mọi nơi")

    sidebar_word_input = st.text_input(
        "Gõ hoặc dán cụm từ cần mổ xẻ:",
        placeholder="Ví dụ: trickle charger, fiddling...",
        key="sidebar_word_input",
    )
    if st.button("🔬 Feynman Phân Tích", type="primary", use_container_width=True, key="sidebar_btn"):
        if sidebar_word_input.strip():
            with st.spinner("Feynman đang mổ xẻ..."):
                feynman_res = explain_phrase_feynman(
                    phrase=sidebar_word_input.strip(),
                    context="Sách tự truyện Feynman",
                    model_choice=model_choice,
                    api_keys=active_keys,
                )
                st.session_state["last_feynman_result"] = feynman_res
                record_word_lookup(
                    username=username,
                    word=sidebar_word_input.strip(),
                    context_sentence="Đọc trực tiếp từ sách Feynman",
                    feynman_breakdown=feynman_res.get("root_nuance", ""),
                    vi_meaning=feynman_res.get("vietnamese_meaning", ""),
                    source_chapter="",
                )

    if "last_feynman_result" in st.session_state and st.session_state["last_feynman_result"]:
        res = st.session_state["last_feynman_result"]
        st.markdown(f"""
        <div class="feynman-box" style="margin-bottom:12px;">
            <h4 style="margin-top:0;"><code>{res.get('phrase', '')}</code> {res.get('phonetic', '')}</h4>
            <p><strong>Nghĩa:</strong> <span style="color:#38bdf8; font-weight:bold;">{res.get('vietnamese_meaning', '')}</span> ({res.get('part_of_speech', '')})</p>
            <p><strong>💡 Nguyên lý gốc:</strong><br>{res.get('root_nuance', '')}</p>
            <p><strong>🧩 Cú pháp:</strong><br>{res.get('grammar_breakdown', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        if res.get("real_life_examples"):
            st.markdown("**Ví dụ thực tế:**")
            for ex in res.get("real_life_examples", [])[:2]:
                st.markdown(f"- 🇺🇸 **{ex.get('en', '')}**\n  ➔ 🇻🇳 *{ex.get('vi', '')}*")

        if res.get("feynman_tip"):
            st.info(f"💡 **Mẹo nhớ:** {res.get('feynman_tip')}")

        if st.button("⭐ Lưu vào Second Brain", use_container_width=True, key="sb_save_sidebar"):
            export_feynman_to_second_brain(
                username=username,
                phrase=res.get("phrase", ""),
                explanation=res,
                source_info="Surely You're Joking, Mr. Feynman!",
            )
            st.toast(f"Đã lưu '{res.get('phrase')}' vào Sổ tay Tri thức!", icon="✅")

    st.markdown("---")
    user_vocab = get_user_vocab_vault(username)
    if user_vocab:
        st.markdown("**🕒 Từ đã tra gần đây:**")
        recent = list(user_vocab.keys())[-5:]
        recent.reverse()
        for rw in recent:
            cnt = user_vocab[rw].get("count", 1)
            badge = "🔴" if cnt >= 2 else "🔵"
            st.caption(f"{badge} **{rw}** ({cnt} lần) — {user_vocab[rw].get('vi_meaning', '')}")


# Custom CSS for Dual Column Reader
st.markdown("""
<style>
.bilingual-card {
    background: #1e232a;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 20px;
}
.column-header-en {
    font-weight: 700;
    font-size: 0.95rem;
    color: #93c5fd;
    padding-bottom: 6px;
    border-bottom: 2px solid #3b82f6;
    margin-bottom: 12px;
}
.column-header-vi {
    font-weight: 700;
    font-size: 0.95rem;
    color: #86efac;
    padding-bottom: 6px;
    border-bottom: 2px solid #22c55e;
    margin-bottom: 12px;
}
.en-column-text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
    font-size: 1.05rem;
    line-height: 1.62;
    color: #e2e8f0;
}
.vi-column-text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 1.02rem;
    line-height: 1.62;
    color: #cbd5e1;
}
.bilingual-p {
    margin: 0 0 8px 0;
    line-height: 1.62;
}
.bilingual-p:last-child {
    margin-bottom: 0;
}
.bilingual-row-divider {
    border-bottom: 1px dashed #334155;
    margin: 14px 0 18px 0;
}
.bilingual-row-subdivider {
    border-bottom: 1px solid rgba(51, 65, 85, 0.45);
    margin: 10px 0 12px 0;
}
.focus-hidden {
    filter: blur(5px);
    transition: filter 0.3s ease;
    cursor: pointer;
}
.focus-hidden:hover {
    filter: blur(0px);
}
.vocab-chip {
    display: inline-block;
    background-color: #2b3945;
    color: #93c5fd;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    margin: 3px 4px;
    border: 1px solid #3b82f6;
}
.feynman-box {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 14px;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("📖 Đọc Sách Song Ngữ Siêu Tốc (Ultralearning Reader)")
st.caption(
    "Đọc sách nguyên bản · Căn chỉnh song ngữ trực diện · "
    "Mổ xẻ ngữ pháp & từ nguyên theo Kỹ thuật Feynman · Tự động phát hiện điểm mù từ vựng"
)

# Load books
books = load_available_books()
if not books:
    st.warning("Chưa tìm thấy sách song ngữ trong hệ thống. Vui lòng nạp sách hoặc chạy bộ trích xuất.")
    st.stop()

# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📚 Đọc Song Ngữ & Phân Tích Feynman",
    "🎯 Sổ Từ Vựng Tần Suất Cao & Luyện Phản Xạ",
    "🚀 Nạp Thêm Sách & Tài Liệu",
])

# =============================================================================
# TAB 1: BILINGUAL READER
# =============================================================================
with tab1:
    col_book, col_part, col_chap = st.columns([1, 1.2, 1.5])
    with col_book:
        book_options = {b.get("title_vi", b.get("title_en")): b["book_id"] for b in books}
        selected_book_name = st.selectbox("Chọn sách:", list(book_options.keys()))
        current_book_id = book_options[selected_book_name]
        current_book = get_book_by_id(current_book_id)

    parts = current_book.get("parts", []) if current_book else []
    with col_part:
        if parts:
            part_options = {}
            for p in parts:
                p_title = p.get("title_vi") or f"Phần {p.get('part_id', 1)}"
                part_options[p_title] = p
            selected_part_label = st.selectbox("Chọn phần:", list(part_options.keys()))
            current_part = part_options[selected_part_label]
        else:
            current_part = None


    with col_chap:
        if current_part and current_part.get("chapters"):
            chap_options = {f"Chương {ch['id']}: {ch['title_vi']}": ch for ch in current_part["chapters"]}
            selected_chap_label = st.selectbox("Chọn chương:", list(chap_options.keys()))
            current_chapter = chap_options[selected_chap_label]
        else:
            current_chapter = None

    st.markdown("---")


    # Reader Controls Toolbar
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1, 1])
    with ctrl_col1:
        reader_mode = st.radio(
            "Chế độ hiển thị:",
            ["🟢 Song song 2 cột (Side-by-Side)", "🎯 Thử thách Siêu Học (Làm mờ tiếng Việt)"],
            horizontal=True,
        )
    with ctrl_col2:
        font_size_choice = st.select_slider(
            "Cỡ chữ:",
            options=["Vừa", "Lớn", "Rất lớn"],
            value="Lớn"
        )
        font_size_map = {"Vừa": "1.0rem", "Lớn": "1.12rem", "Rất lớn": "1.25rem"}
        cur_font_size = font_size_map[font_size_choice]
    with ctrl_col3:
        st.write("")
        st.write("")
        show_vocab_chips = st.checkbox("Hiện từ vựng then chốt", value=True)

    # Chapter Summary Banner
    if current_chapter:
        with st.expander(f"📌 Tóm lược Chương {current_chapter['id']}: {current_chapter['title_vi']}", expanded=False):
            st.info(current_chapter.get("summary_vi", "Không có tóm lược."))

        sections = current_chapter.get("sections", [])
        book_id = current_book.get("book_id", "default_book")
        chap_id = current_chapter.get("id", 1)

        # Granularity Selector: Fine-Grained JIT Paragraphs (Default) vs. Macro-Scenes
        view_mode = st.radio(
            "📐 Chế độ hiển thị song ngữ:",
            [
                "⚡ Song song từng đoạn (JIT Đối Xứng 100% - Khuyên dùng)",
                "🎬 Song song theo cảnh truyện (Macro-Scenes Khóa Hàng)",
            ],
            index=0,
            horizontal=True,
            key=f"view_mode_{chap_id}",
            help="Chế độ JIT dịch trực tiếp từ bản gốc tiếng Anh, đối xứng 100% từng dòng. Chế độ Macro-Scenes khóa hàng song song cho các cảnh truyện."
        )

        if "từng đoạn" in view_mode:
            # Flatten raw English text into individual paragraphs
            full_en_text = "\n\n".join([s.get("en", "") for s in sections])
            en_raw_paragraphs = [
                p.strip() for p in full_en_text.split("\n\n")
                if len(p.strip()) > 20 and not p.strip().startswith("He Fixes Radios by Thinking")
            ]

            total_paras = len(en_raw_paragraphs)
            batch_size = 4  # 3-5 paragraphs per page for optimal reading & API resilience
            total_pages = max(1, (total_paras + batch_size - 1) // batch_size)

            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col1:
                cur_page = st.number_input(
                    "Trang:",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    step=1,
                    key=f"jit_page_{chap_id}"
                )
            with p_col2:
                st.caption(f"Trang {cur_page} / {total_pages} (Tổng cộng {total_paras} đoạn văn trong chương)")
            with p_col3:
                force_retranslate = st.button("🔄 Dịch lại trang này", key=f"retrans_{chap_id}_{cur_page}")

            start_idx = (cur_page - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_paras)
            page_paragraphs = en_raw_paragraphs[start_idx:end_idx]

            # Load from JIT persistent cache
            jit_cache = load_chapter_jit_cache(book_id, chap_id)
            need_translate = []
            page_results = []

            for p_offset, p_text in enumerate(page_paragraphs):
                global_idx = start_idx + p_offset
                idx_key = str(global_idx)
                if force_retranslate or idx_key not in jit_cache:
                    need_translate.append((global_idx, p_text))
                else:
                    page_results.append((global_idx, p_text, jit_cache[idx_key]))

            if need_translate:
                with st.spinner(f"⚡ Đang dịch cuốn chiếu {len(need_translate)} đoạn tiếp theo bằng Gemini..."):
                    texts_to_trans = [item[1] for item in need_translate]
                    translated_batch = translate_paragraphs_batch(
                        paragraphs=texts_to_trans,
                        book_title=current_book.get("title_en", ""),
                        chapter_title=current_chapter.get("title_en", ""),
                        api_keys=active_keys,
                    )
                    has_error = False
                    for item, trans in zip(need_translate, translated_batch):
                        g_idx, p_text = item
                        page_results.append((g_idx, p_text, trans))
                        # Only persist if it's a real translation (not fallback message)
                        if trans.get("vi") and not trans["vi"].startswith("(Đang chờ kết nối API"):
                            jit_cache[str(g_idx)] = trans
                        else:
                            has_error = True
                    save_chapter_jit_cache(book_id, chap_id, jit_cache)
                    if has_error:
                        st.warning("⚠️ Chưa thể kết nối Gemini API để dịch các đoạn mới. Vui lòng bấm '🔄 Dịch lại trang này' hoặc kiểm tra API Key ở Sidebar!")

            # Sort page results by global index
            page_results.sort(key=lambda x: x[0])

            st.markdown(f"**Hiển thị đoạn {start_idx + 1} đến {end_idx} / {total_paras} (Khớp song song 100%):**")

            # Column headers once per page
            h_col1, h_col2 = st.columns([1.1, 0.9])
            with h_col1:
                st.markdown("<div class='column-header-en'>🇺🇸 Bản gốc Tiếng Anh</div>", unsafe_allow_html=True)
            with h_col2:
                st.markdown("<div class='column-header-vi'>🇻🇳 Bản dịch Tiếng Việt (Khớp 100%)</div>", unsafe_allow_html=True)

            for g_idx, p_en, trans_data in page_results:
                p_vi = trans_data.get("vi", "")
                p_vocab = trans_data.get("key_vocab", [])

                st.caption(f"📌 **Đoạn {g_idx + 1}**")
                col_en, col_vi = st.columns([1.1, 0.9])

                with col_en:
                    st.markdown(
                        f'<div class="en-column-text" style="font-size: {cur_font_size};">'
                        f'{format_paragraphs_html(p_en)}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                with col_vi:
                    is_blur = "focus-hidden" if "Thử thách Siêu Học" in reader_mode else ""
                    blur_note = "<small style='color:#94a3b8;'><i>(Rê chuột hoặc chạm vào để mở bản dịch)</i></small><br>" if is_blur else ""
                    st.markdown(
                        f'{blur_note}'
                        f'<div class="vi-column-text {is_blur}" style="font-size: {cur_font_size};">'
                        f'{format_paragraphs_html(p_vi)}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                if show_vocab_chips and p_vocab:
                    st.markdown("**🔑 Từ vựng & Sắc thái trong đoạn:**")
                    v_cols = st.columns(min(len(p_vocab), 4))
                    for v_idx, v in enumerate(p_vocab):
                        with v_cols[v_idx % 4]:
                            v_word = v.get("word", "")
                            if st.button(f"📌 {v_word}", key=f"jit_vchip_{g_idx}_{v_idx}", help=f"{v.get('vi')} — {v.get('nuance', '')}"):
                                with st.spinner(f"Feynman đang phân tích '{v_word}'..."):
                                    f_res = explain_phrase_feynman(
                                        phrase=v_word,
                                        context=p_en,
                                        model_choice=model_choice,
                                        api_keys=active_keys,
                                    )
                                    st.session_state["last_feynman_result"] = f_res
                                    st.session_state["sidebar_word_input"] = v_word
                                    record_word_lookup(
                                        username=username,
                                        word=v_word,
                                        context_sentence=p_en[:150],
                                        feynman_breakdown=v.get("nuance", ""),
                                        vi_meaning=v.get("vi", ""),
                                        source_chapter=current_chapter.get("title_vi", ""),
                                    )
                                    st.toast(f"Đã phân tích '{v_word}'! Xem chi tiết ở Sidebar.", icon="🔬")
                                    st.rerun()

                # Inline lookup popover
                with st.popover(f"🔍 Tra cứu cụm từ khác trong Đoạn {g_idx + 1}"):
                    inline_w = st.text_input("Gõ hoặc dán cụm từ trong đoạn này:", key=f"jit_inline_inp_{g_idx}")
                    if st.button("🔬 Mổ xẻ với Feynman", key=f"jit_inline_btn_{g_idx}") and inline_w.strip():
                        with st.spinner(f"Đang phân tích '{inline_w}'..."):
                            f_res = explain_phrase_feynman(
                                phrase=inline_w.strip(),
                                context=p_en[:200],
                                model_choice=model_choice,
                                api_keys=active_keys,
                            )
                            st.session_state["last_feynman_result"] = f_res
                            st.session_state["sidebar_word_input"] = inline_w.strip()
                            record_word_lookup(
                                username=username,
                                word=inline_w.strip(),
                                context_sentence=p_en[:150],
                                feynman_breakdown=f_res.get("root_nuance", ""),
                                vi_meaning=f_res.get("vietnamese_meaning", ""),
                                source_chapter=current_chapter.get("title_vi", ""),
                            )
                            st.toast(f"Đã phân tích '{inline_w}'! Xem chi tiết ở Sidebar.", icon="🔬")
                            st.rerun()

                st.markdown("<div class='bilingual-row-divider'></div>", unsafe_allow_html=True)

        else:
            # RENDER BILINGUAL MACRO-SECTIONS (ROW-LOCKED PARALLEL ALIGNMENT)
            st.write(f"**Tổng số cảnh truyện trong chương:** {len(sections)} cảnh (Đã căn chỉnh song song tương đối theo từng hàng).")
            for sec in sections:
                sec_id = sec.get("section_id", 1)
                title = sec.get("title", f"Cảnh {sec_id}")

                st.markdown(f"#### 🏷️ Cảnh {sec_id}: {title}")

                # Column headers once per scene
                h_col1, h_col2 = st.columns([1.1, 0.9])
                with h_col1:
                    st.markdown("<div class='column-header-en'>🇺🇸 Bản gốc Tiếng Anh</div>", unsafe_allow_html=True)
                with h_col2:
                    st.markdown("<div class='column-header-vi'>🇻🇳 Bản dịch Tiếng Việt</div>", unsafe_allow_html=True)

                aligned_rows = align_scene_paragraphs(sec.get("en", ""), sec.get("vi", ""))
                is_blur = "focus-hidden" if "Thử thách Siêu Học" in reader_mode else ""
                blur_note = "<small style='color:#94a3b8;'><i>(Rê chuột hoặc chạm vào để mở bản dịch)</i></small><br>" if is_blur else ""

                for r_idx, (r_en, r_vi) in enumerate(aligned_rows):
                    r_col1, r_col2 = st.columns([1.1, 0.9])
                    with r_col1:
                        st.markdown(
                            f'<div class="en-column-text" style="font-size: {cur_font_size};">'
                            f'{format_paragraphs_html(r_en)}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    with r_col2:
                        st.markdown(
                            f'{blur_note if r_idx == 0 else ""}'
                            f'<div class="vi-column-text {is_blur}" style="font-size: {cur_font_size};">'
                            f'{format_paragraphs_html(r_vi)}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    if r_idx < len(aligned_rows) - 1:
                        st.markdown("<div class='bilingual-row-subdivider'></div>", unsafe_allow_html=True)

                # Key Vocab Chips
                if show_vocab_chips and sec.get("vocab"):
                    st.markdown("**🔑 Từ vựng & Điểm then chốt trong đoạn:**")
                    chip_cols = st.columns(min(len(sec["vocab"]), 4))
                    for v_idx, v in enumerate(sec["vocab"]):
                        with chip_cols[v_idx % 4]:
                            btn_label = f"📌 {v['word']} ({v['type']})"
                            if st.button(btn_label, key=f"vchip_{sec_id}_{v_idx}", help=f"{v.get('vi')} — {v.get('feynman_context', '')}"):
                                with st.spinner(f"Feynman đang phân tích '{v['word']}'..."):
                                    feynman_res = explain_phrase_feynman(
                                        phrase=v["word"],
                                        context=sec.get("en", ""),
                                        model_choice=model_choice,
                                        api_keys=active_keys,
                                    )
                                    st.session_state["last_feynman_result"] = feynman_res
                                    st.session_state["sidebar_word_input"] = v["word"]
                                    record_word_lookup(
                                        username=username,
                                        word=v["word"],
                                        context_sentence=sec.get("en", "")[:150],
                                        feynman_breakdown=v.get("feynman_context", ""),
                                        vi_meaning=v.get("vi", ""),
                                        source_chapter=current_chapter.get("title_vi", ""),
                                    )
                                    st.toast(f"Đã phân tích '{v['word']}'! Xem chi tiết ở Sidebar bên trái.", icon="🔬")
                                    st.rerun()

                # Inline Quick Lookup Popover
                with st.popover(f"🔍 Tra cứu cụm từ khác trong Cảnh {sec_id}"):
                    inline_word = st.text_input("Gõ hoặc dán cụm từ trong đoạn này:", key=f"inline_inp_{sec_id}")
                    if st.button("🔬 Mổ xẻ với Feynman", key=f"inline_btn_{sec_id}") and inline_word.strip():
                        with st.spinner(f"Đang phân tích '{inline_word}'..."):
                            feynman_res = explain_phrase_feynman(
                                phrase=inline_word.strip(),
                                context=sec.get("en", "")[:200],
                                model_choice=model_choice,
                                api_keys=active_keys,
                            )
                            st.session_state["last_feynman_result"] = feynman_res
                            st.session_state["sidebar_word_input"] = inline_word.strip()
                            record_word_lookup(
                                username=username,
                                word=inline_word.strip(),
                                context_sentence=sec.get("en", "")[:150],
                                feynman_breakdown=feynman_res.get("root_nuance", ""),
                                vi_meaning=feynman_res.get("vietnamese_meaning", ""),
                                source_chapter=current_chapter.get("title_vi", ""),
                            )
                            st.toast(f"Đã phân tích '{inline_word}'! Xem chi tiết ở Sidebar bên trái.", icon="🔬")
                            st.rerun()

                st.markdown("<hr style='border: 1px dashed #334155;'>", unsafe_allow_html=True)


# =============================================================================
# TAB 2: VOCABULARY VAULT & ACTIVE RECALL DRILL
# =============================================================================
with tab2:
    st.subheader("🎯 Kho Từ Vựng Tần Suất Cao & Điểm Mù (Target Drill)")
    st.caption("Theo phương pháp Siêu Học (Ultralearning): Những từ được tra từ 2 lần trở lên là điểm mù cần luyện phản xạ lặp lại ngắt quãng.")

    vocab_vault = get_user_vocab_vault(username)

    if not vocab_vault:
        st.info("Bạn chưa tra cứu từ vựng nào. Khi đọc sách ở Tab 1, hãy bấm vào các từ hoặc tra cứu để hệ thống tự động ghi nhận và phân tích!")
    else:
        # Metrics
        total_words = len(vocab_vault)
        target_drills = [w for w, d in vocab_vault.items() if d.get("count", 1) >= 2]
        mastered_words = [w for w, d in vocab_vault.items() if d.get("mastered", False)]

        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số từ vựng đã tra", total_words)
        m2.metric("🔴 Điểm mù lặp lại (Tra >= 2 lần)", len(target_drills), help="Cần ưu tiên làm bài tập Active Recall")
        m3.metric("✅ Đã làm chủ thành thạo", len(mastered_words))

        st.markdown("---")

        # ACTIVE RECALL GAME (Cloze Test)
        st.markdown("### ⚡ Thử Thách Phản Xạ Active Recall (Điền từ vào chỗ trống)")
        st.write("Hệ thống sẽ lấy chính ngữ cảnh câu trong sách Feynman, giấu từ khóa đi để bạn tự gõ lại:")

        # Pick words that have contexts
        testable_words = [w for w, d in vocab_vault.items() if d.get("contexts")]
        if not testable_words:
            testable_words = list(vocab_vault.keys())

        if testable_words:
            # Word selector for drill
            drill_word = st.selectbox(
                "Chọn từ vựng muốn kiểm tra phản xạ:",
                testable_words,
                format_func=lambda w: f"{w.upper()} — (Đã tra {vocab_vault[w].get('count', 1)} lần) - {vocab_vault[w].get('vi_meaning', '')}"
            )
            entry = vocab_vault[drill_word]
            context_list = entry.get("contexts", [])
            sample_sentence = context_list[0] if context_list else f"I had to understand the {drill_word} to solve the problem."

            # Mask the target word in sentence
            pattern = re.compile(re.escape(drill_word), re.IGNORECASE)
            masked_sentence = pattern.sub("【 _____ 】", sample_sentence)

            st.markdown(f"**Câu đố:** *\"{masked_sentence}\"*")
            st.caption(f"Gợi ý nghĩa tiếng Việt: **{entry.get('vi_meaning', 'Từ ngữ Feynman sử dụng')}**")

            user_guess = st.text_input("Gõ từ tiếng Anh còn thiếu vào đây:", key="cloze_input")
            if st.button("Kiểm tra đáp án", type="primary"):
                if user_guess.strip().lower() == drill_word.strip().lower():
                    st.success(f"🎉 **Chính xác tuyệt đối!** Bạn đã làm chủ cụm từ: **{drill_word}**!")
                    st.balloons()
                    toggle_word_mastery(username, drill_word)
                else:
                    st.error(f"Chưa chính xác! Đáp án đúng là: **{drill_word}**. Đừng lo, hãy nhẩm lại câu văn và thử lại nhé!")

        st.markdown("---")

        # VOCABULARY TABLE
        st.markdown("### 📋 Danh Sách Từ Vựng Của Bạn")
        filter_target_only = st.checkbox("Chỉ hiển thị các từ điểm mù (Tra >= 2 lần)", value=False)

        sorted_vocab = sorted(
            vocab_vault.items(),
            key=lambda item: item[1].get("count", 1),
            reverse=True
        )

        for w, data in sorted_vocab:
            if filter_target_only and data.get("count", 1) < 2:
                continue

            count = data.get("count", 1)
            badge = "🔴 **[TARGET DRILL]**" if count >= 2 else "🔵 [Đã xem]"
            status = "✅ Đã thuộc" if data.get("mastered") else "⏳ Đang rèn luyện"

            with st.expander(f"{badge} **{w.upper()}** (Tra cứu: {count} lần) — {data.get('vi_meaning', '')} [{status}]"):
                st.write(f"**Từ loại & Ý nghĩa:** {data.get('vi_meaning', 'Chưa có chú thích')}")
                if data.get("feynman_breakdown"):
                    st.info(f"**Nguyên lý Feynman:** {data['feynman_breakdown']}")
                if data.get("source_chapter"):
                    st.caption(f"Nguồn: {data['source_chapter']} · Lần cuối xem: {data.get('updated_at', '')}")

                btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 2])
                with btn_c1:
                    if st.button("Đổi trạng thái thuộc", key=f"mst_{w}"):
                        toggle_word_mastery(username, w)
                        st.rerun()
                with btn_c2:
                    if st.button("Xóa từ này", key=f"del_{w}"):
                        delete_word_from_vault(username, w)
                        st.rerun()


# =============================================================================
# TAB 3: WEB INGESTION (NẠP THÊM TÀI LIỆU)
# =============================================================================
with tab3:
    st.subheader("🚀 Nạp Thêm Sách & Tài Liệu Song Ngữ Mới")

    st.markdown("""
    > [!TIP]
    > **Kiến trúc tối ưu cho Web (Cloud):** 
    > - Sách PDF dày hàng trăm trang (như Feynman) được bóc tách và căn chỉnh ở máy Local bằng `firecrawl-anydoc` thành file JSON siêu nhẹ (~50KB) trước khi đẩy lên Web. Nhờ đó, ứng dụng chạy trên Cloud không bao giờ bị tràn RAM hay lag giật!
    > - Để nạp bài báo, chương sách ngắn mới trực tiếp trên Web, bạn có thể sử dụng biểu mẫu dán văn bản đối xứng bên dưới:
    """)

    with st.form("custom_bilingual_ingest_form"):
        st.write("#### Nạp phiên đọc song ngữ tức thì:")
        c_title_en = st.text_input("Tiêu đề tiếng Anh:", "Richard Feynman on Thinking")
        c_title_vi = st.text_input("Tiêu đề tiếng Việt:", "Richard Feynman bàn về tư duy")

        c_en_col, c_vi_col = st.columns(2)
        with c_en_col:
            custom_en_text = st.text_area(
                "Đoạn văn tiếng Anh (Các đoạn cách nhau bằng dòng trống):",
                height=220,
                placeholder="Paste English paragraphs here..."
            )
        with c_vi_col:
            custom_vi_text = st.text_area(
                "Đoạn văn tiếng Việt đối ứng (Các đoạn cách nhau bằng dòng trống):",
                height=220,
                placeholder="Dán các đoạn tiếng Việt tương ứng vào đây..."
            )

        submit_ingest = st.form_submit_button("⚡ Tạo Phiên Đọc Song Ngữ Ngay", type="primary")

        if submit_ingest:
            if not custom_en_text.strip() or not custom_vi_text.strip():
                st.error("Vui lòng nhập cả văn bản tiếng Anh và tiếng Việt đối xứng.")
            else:
                en_chunks = [p.strip() for p in custom_en_text.split("\n\n") if p.strip()]
                vi_chunks = [p.strip() for p in custom_vi_text.split("\n\n") if p.strip()]

                sections_custom = []
                for idx in range(max(len(en_chunks), len(vi_chunks))):
                    sections_custom.append({
                        "section_id": idx + 1,
                        "title": f"Khối {idx + 1}",
                        "en": en_chunks[idx] if idx < len(en_chunks) else "",
                        "vi": vi_chunks[idx] if idx < len(vi_chunks) else "",
                        "vocab": []
                    })

                new_book_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                new_book = {
                    "book_id": new_book_id,
                    "title_en": c_title_en,
                    "title_vi": c_title_vi,
                    "author": username,
                    "parts": [{
                        "part_id": 1,
                        "title_en": "Custom Articles",
                        "title_vi": "Tài liệu nạp nhanh",
                        "chapters": [{
                            "id": 1,
                            "title_en": c_title_en,
                            "title_vi": c_title_vi,
                            "summary_vi": "Tài liệu tự nạp trực tiếp qua giao diện Web.",
                            "sections": sections_custom
                        }]
                    }]
                }

                # Save into session state or temp file
                out_path = Path(__file__).resolve().parent.parent / "data" / "bilingual_books" / f"{new_book_id}.json"
                with open(out_path, "w", encoding="utf-8") as fp:
                    json.dump(new_book, fp, ensure_ascii=False, indent=2)

                st.success("Đã tạo phiên đọc song ngữ thành công! Hãy chuyển sang Tab 1 và chọn tài liệu mới này.")
                st.cache_data.clear()
                st.rerun()

