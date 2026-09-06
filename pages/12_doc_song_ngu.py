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
)

# -----------------------------------------------------------------------------
# Bootstrap & Auth Context
# -----------------------------------------------------------------------------
ctx = bootstrap()
username = ctx["username"]
display_name = ctx.get("display_name", username)
model_choice = ctx.get("model_choice", "gemini-2.5-flash")
active_keys = ctx.get("active_keys", [])

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
.en-column-text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #e2e8f0;
}
.vi-column-text {
    font-size: 1.02rem;
    line-height: 1.7;
    color: #cbd5e1;
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
    col_book, col_chap = st.columns([1, 1.5])
    with col_book:
        book_options = {b.get("title_vi", b.get("title_en")): b["book_id"] for b in books}
        selected_book_name = st.selectbox("Chọn sách:", list(book_options.keys()))
        current_book_id = book_options[selected_book_name]
        current_book = get_book_by_id(current_book_id)

    # Flatten chapters for easy selection
    all_chapters = []
    if current_book:
        for part in current_book.get("parts", []):
            for ch in part.get("chapters", []):
                all_chapters.append(ch)

    with col_chap:
        if all_chapters:
            chap_options = {f"Chương {ch['id']}: {ch['title_vi']} ({ch['title_en']})": ch for ch in all_chapters}
            selected_chap_label = st.selectbox("Chọn chương sách:", list(chap_options.keys()))
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
        st.write(f"**Tổng số đoạn trong chương:** {len(sections)} phần đọc đối xứng.")

        # Interactive Global Word Explainer Modal/Form in Sidebar or Top
        st.markdown("### 🔬 Trợ Lý Feynman: Mổ Xẻ Cụm Từ Bất Kỳ")
        with st.container():
            c_input, c_btn = st.columns([4, 1])
            with c_input:
                user_phrase_input = st.text_input(
                    "Gõ hoặc dán bất kỳ từ/cụm từ tiếng Anh khó hiểu trong bài:",
                    placeholder="Ví dụ: trickle charger, helluva racket, in series, fiddling...",
                    key="global_phrase_input",
                )
            with c_btn:
                st.write("")
                st.write("")
                explain_btn = st.button("🔬 Feynman Phân Tích", type="primary", use_container_width=True)

            if explain_btn and user_phrase_input.strip():
                with st.spinner("Richard Feynman đang mổ xẻ nguyên lý ngôn ngữ..."):
                    feynman_res = explain_phrase_feynman(
                        phrase=user_phrase_input.strip(),
                        context=f"Trích từ sách: {current_book.get('title_en')} - Chương {current_chapter.get('title_en')}",
                        model_choice=model_choice,
                        api_keys=active_keys,
                    )
                    st.session_state["last_feynman_result"] = feynman_res
                    # Record lookup
                    record_word_lookup(
                        username=username,
                        word=user_phrase_input.strip(),
                        context_sentence=current_chapter.get("title_en", ""),
                        feynman_breakdown=feynman_res.get("root_nuance", ""),
                        vi_meaning=feynman_res.get("vietnamese_meaning", ""),
                        source_chapter=current_chapter.get("title_vi", ""),
                    )

            if "last_feynman_result" in st.session_state and st.session_state["last_feynman_result"]:
                res = st.session_state["last_feynman_result"]
                with st.container():
                    st.markdown(f"""
                    <div class="feynman-box">
                        <h4>🔬 Kỹ Thuật Feynman: <code>{res.get('phrase', '')}</code> {res.get('phonetic', '')}</h4>
                        <p><strong>Nghĩa ngữ cảnh:</strong> <span style="color:#38bdf8; font-size:1.1rem; font-weight:bold;">{res.get('vietnamese_meaning', '')}</span> ({res.get('part_of_speech', '')})</p>
                        <p><strong>💡 Bản chất nguyên lý gốc (Why this word?):</strong><br>{res.get('root_nuance', '')}</p>
                        <p><strong>🧩 Giải phẫu cú pháp (Grammar Breakdown):</strong><br>{res.get('grammar_breakdown', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("**Ví dụ thực tế đời thường:**")
                    for ex in res.get("real_life_examples", []):
                        st.markdown(f"- 🇺🇸 **{ex.get('en', '')}**\n  ➔ 🇻🇳 *{ex.get('vi', '')}*")

                    if res.get("feynman_tip"):
                        st.success(f"**Mẹo siêu học nhớ lâu:** {res.get('feynman_tip')}")

                    # Export to Second Brain Button
                    col_sb, col_dummy = st.columns([1.5, 3])
                    with col_sb:
                        if st.button("⭐ Lưu vào Sổ tay Tri thức (Second Brain)", key=f"sb_save_{res.get('phrase')}"):
                            note = export_feynman_to_second_brain(
                                username=username,
                                phrase=res.get("phrase", ""),
                                explanation=res,
                                source_info=f"{current_book.get('title_en')} — {current_chapter.get('title_vi')}",
                            )
                            st.toast(f"Đã lưu '{res.get('phrase')}' vào Second Brain!", icon="✅")

        st.markdown("---")

        # RENDER BILINGUAL SECTIONS
        for sec in sections:
            sec_id = sec.get("section_id", 1)
            title = sec.get("title", f"Phần {sec_id}")

            st.markdown(f"#### 🏷️ Đoạn {sec_id}: {title}")

            col_en, col_vi = st.columns([1.1, 0.9])

            with col_en:
                st.markdown("**🇺🇸 Bản gốc Tiếng Anh:**")
                st.markdown(
                    f'<div class="en-column-text" style="font-size: {cur_font_size};">'
                    f'{sec.get("en", "").replace(chr(10), "<br><br>")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_vi:
                st.markdown("**🇻🇳 Bản dịch Tiếng Việt:**")
                is_blur = "focus-hidden" if "Thử thách Siêu Học" in reader_mode else ""
                blur_note = "<small style='color:#94a3b8;'><i>(Rê chuột hoặc chạm vào để mở bản dịch)</i></small><br>" if is_blur else ""
                st.markdown(
                    f'{blur_note}'
                    f'<div class="vi-column-text {is_blur}" style="font-size: {cur_font_size};">'
                    f'{sec.get("vi", "").replace(chr(10), "<br><br>")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Key Vocab Chips
            if show_vocab_chips and sec.get("vocab"):
                st.markdown("**🔑 Từ vựng & Điểm then chốt trong đoạn:**")
                chip_cols = st.columns(min(len(sec["vocab"]), 4))
                for v_idx, v in enumerate(sec["vocab"]):
                    with chip_cols[v_idx % 4]:
                        btn_label = f"📌 {v['word']} ({v['type']})"
                        if st.button(btn_label, key=f"vchip_{sec_id}_{v_idx}", help=f"{v.get('vi')} — {v.get('feynman_context', '')}"):
                            # Trigger Feynman analysis
                            with st.spinner(f"Feynman đang phân tích '{v['word']}'..."):
                                feynman_res = explain_phrase_feynman(
                                    phrase=v["word"],
                                    context=sec.get("en", ""),
                                    model_choice=model_choice,
                                    api_keys=active_keys,
                                )
                                st.session_state["last_feynman_result"] = feynman_res
                                record_word_lookup(
                                    username=username,
                                    word=v["word"],
                                    context_sentence=sec.get("en", "")[:150],
                                    feynman_breakdown=v.get("feynman_context", ""),
                                    vi_meaning=v.get("vi", ""),
                                    source_chapter=current_chapter.get("title_vi", ""),
                                )
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

