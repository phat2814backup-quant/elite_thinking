# -*- coding: utf-8 -*-
"""
Trang 12: Từ Vựng Tiếng Anh Tư Duy Tinh Hoa (First-Principles English Vocab)
- Phương pháp sư phạm First Principles: Bóc tách Gốc từ Lego (Latin/Greek Roots)
- Mỏ neo Thị giác (Visual Mental Anchors) & Cặp đối kháng Nhị phân (Cognitive Contrast)
- 100% Zero-API: Tải tức thì, không tốn quota, không độ trễ, lưu bền vững Supabase/Local JSON.
"""

from __future__ import annotations

import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from utils.app_common import bootstrap
from utils.vocab_manager import (
    load_elite_vocab,
    get_all_vocab,
    get_categories,
    get_pillars,
    get_topics_by_pillar,
    get_vocab_by_pillar,
    get_vocab_by_topic,
    get_vocab_by_id,
    get_user_vocab_state,
    toggle_vocab_mastery,
    toggle_vocab_star,
    record_quiz_attempt,
    get_vocab_stats,
)


# -----------------------------------------------------------------------------
# Tiện ích Nghe Đọc Audio & Liên kết NaturalReaders Online (Zero-API)
# -----------------------------------------------------------------------------
def render_audio_and_tts_tools(text: str, key_suffix: str = "") -> None:
    """
    Tiện ích Nghe đọc Phát âm & Mở NaturalReaders:
    1. 🔊 Nghe đọc trực tiếp: Web Speech API giọng bản ngữ US, rate 0.88, 0 API tokens.
    2. 📋 Copy nhanh: Tự động sao chép câu vào clipboard kèm thông báo.
    3. 🎙️ Mở NaturalReader Online: Đường dẫn mở tab mới đến https://www.naturalreaders.com/online/
    """
    if not text:
        return

    enc_text = urllib.parse.quote(text)

    html_widget = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          margin: 0;
          padding: 2px 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          overflow: hidden;
          background: transparent;
        }}
        .tts-bar {{
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }}
        .btn {{
          border: none;
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          text-decoration: none;
          transition: all 0.15s ease-in-out;
        }}
        .btn:hover {{
          transform: translateY(-1px);
          filter: brightness(1.1);
        }}
        .btn-speak {{
          background: linear-gradient(135deg, #1E88E5, #1565C0);
          color: white;
          box-shadow: 0 1px 3px rgba(30,136,229,0.3);
        }}
        .btn-copy {{
          background: #2E7D32;
          color: white;
          box-shadow: 0 1px 3px rgba(46,125,50,0.3);
        }}
        .btn-natural {{
          background: #E65100;
          color: white;
          box-shadow: 0 1px 3px rgba(230,81,0,0.3);
        }}
        .toast {{
          color: #2E7D32;
          font-size: 12px;
          font-weight: bold;
          display: none;
        }}
      </style>
    </head>
    <body>
      <div class="tts-bar">
        <button class="btn btn-speak" onclick="playSpeech()">
          🔊 Nghe đọc trực tiếp
        </button>
        <button class="btn btn-copy" onclick="copyQuote()">
          📋 Copy câu
        </button>
        <a class="btn btn-natural" href="https://www.naturalreaders.com/online/" target="_blank" rel="noopener noreferrer">
          🎙️ Mở NaturalReaders ↗
        </a>
        <span id="toast-msg" class="toast">✓ Đã copy!</span>
      </div>
      <script>
        function playSpeech() {{
          if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var raw = decodeURIComponent("{enc_text}");
            var u = new SpeechSynthesisUtterance(raw);
            u.lang = 'en-US';
            u.rate = 0.88;
            window.speechSynthesis.speak(u);
          }} else {{
            alert('Trình duyệt chưa hỗ trợ Web Speech, bạn hãy bấm "Mở NaturalReaders"!');
          }}
        }}
        function copyQuote() {{
          var raw = decodeURIComponent("{enc_text}");
          if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(raw).then(showToast).catch(fallbackCopy);
          }} else {{
            fallbackCopy();
          }}
        }}
        function fallbackCopy() {{
          var raw = decodeURIComponent("{enc_text}");
          var ta = document.createElement('textarea');
          ta.value = raw;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          showToast();
        }}
        function showToast() {{
          var t = document.getElementById('toast-msg');
          if (t) {{
            t.style.display = 'inline';
            setTimeout(function() {{ t.style.display = 'none'; }}, 2500);
          }}
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_widget, height=38)


# -----------------------------------------------------------------------------
# Bootstrap & User Context
# -----------------------------------------------------------------------------
ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]


# -----------------------------------------------------------------------------
# Header & Triết lý Học Không Học Vẹt
# -----------------------------------------------------------------------------
st.title("🧬 Từ Vựng Tiếng Anh Tư Duy Tinh Hoa (Elite Vocab)")
st.caption("Phương pháp First Principles: Bẻ khóa qua Gốc từ Lego (Latinh/Hy Lạp) · Mỏ neo Thị giác · 100% Zero-API")

with st.expander("💡 Tại sao phương pháp này giúp bạn NHỚ VĨNH VIỄN mà KHÔNG CẦN HỌC VẸT?", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        #### 🧱 1. Gốc Từ Lego (Etymological Atoms)
        95% từ vựng tư duy và khoa học tiếng Anh được lắp ghép từ **gốc Latinh & Hy Lạp**. 
        Ví dụ: Khi bạn biết gốc `vert/vers` nghĩa là *xoay, lộn*, bạn tự động hiểu ngay:
        - `Inversion` (lộn ngược)
        - `Reverse` (quay lùi)
        - `Introvert` (xoay vào trong - hướng nội)
        - `Convert` (xoay đổi trạng thái)  
        **Học 1 gốc từ, làm chủ 5–10 từ học thuật!**
        """)
    with c2:
        st.markdown("""
        #### ⚓ 2. Mỏ Neo Thị Giác (Sensory Anchors)
        Bộ não người sinh ra để ghi nhớ hình ảnh chuyển động và cơ học, không phải các chuỗi ký tự trừu tượng.
        Mỗi từ vựng được gắn chặt với **một hình ảnh vật lý trực quan** (Chiếc bập bênh `Asymmetry`, Tảng đá nặng `Inertia`, Căn phòng bừa bộn `Entropy`).
        """)
    with c3:
        st.markdown("""
        #### ⚖️ 3. Cặp Đối Kháng Nhị Phân (Cognitive Contrast)
        Não bộ hiểu sâu sắc nhất qua **sự tương phản đối lập**:
        - *Symmetric* (Ăn 1 mất 1) vs *Asymmetric* (Mất 1 nhưng ăn 100).
        - *Fragile* (Sợ va đập) vs *Antifragile* (Càng va đập càng mạnh).
        - *Direct thinking* vs *Inversion*.
        """)

st.markdown("---")

# -----------------------------------------------------------------------------
# Thống Kê Tiến Độ Người Học (Progress Bar)
# -----------------------------------------------------------------------------
all_vocab = get_all_vocab()
if len(all_vocab) < 100:
    st.cache_data.clear()
    all_vocab = get_all_vocab()
    st.rerun()

stats = get_vocab_stats(username)
user_state = get_user_vocab_state(username)
categories = get_categories()
pillars = get_pillars()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("📚 Tổng số từ tinh hoa", f"{stats['total_words']} từ")
col_m2.metric("✅ Đã thông suốt", f"{stats['mastered_count']} từ", f"{stats['progress_percent']}%")
col_m3.metric("⭐ Đã gắn sao ưu tiên", f"{stats['starred_count']} từ")
col_m4.metric("⚡ Trạng thái Engine", "100% Offline (0 API)")

st.progress(stats["progress_percent"] / 100.0, text=f"Tiến độ làm chủ từ vựng tinh hoa: {stats['progress_percent']}% ({stats['mastered_count']}/{stats['total_words']} từ)")

# Phân bổ tiến độ theo 3 Cột Trụ
p_stats = stats.get("pillars_stats", {})
with st.expander("🏛️ Tiến độ theo 3 Cột Trụ Kiến Thức (Nhấp để mở rộng)", expanded=False):
    p_cols = st.columns(3)
    p_order = [
        ("modes_9", "🏛️ 9 Chế Độ Tư Duy (Tab 2)"),
        ("munger_88", "🧠 88 Mô Hình Munger (Tab 3)"),
        ("principles_100", "🎯 100 Nguyên Lý Đỉnh Cao (Tab 4)"),
    ]
    for idx, (p_id, p_title) in enumerate(p_order):
        ps = p_stats.get(p_id, {})
        with p_cols[idx]:
            st.markdown(f"**{p_title}**")
            st.caption(f"{ps.get('topics_count', 0)} chủ đề · {ps.get('total', 0)} từ vựng")
            st.progress(ps.get("progress_percent", 0) / 100.0, text=f"Đã thuộc: {ps.get('mastered', 0)}/{ps.get('total', 0)} từ ({ps.get('progress_percent', 0)}%)")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Tabs 4 Chế Độ Học Tập Tương Tác
# -----------------------------------------------------------------------------
tab_anatomy, tab_flashcard, tab_quiz, tab_vault = st.tabs([
    "🧱 1. Giải Phẫu Lego Từ Vựng",
    "⚡ 2. Flashcard Phản Xạ Nhận Diện",
    "🎯 3. Thử Thách Giải Mã & Cloze Test",
    "📊 4. Tủ Từ Vựng Của Tôi (Vault)",
])


# =============================================================================
# TAB 1: GIẢI PHẪU LEGO TỪ VỰNG (WORD ANATOMY EXPLORER)
# =============================================================================
with tab_anatomy:
    st.subheader("🧱 Bản Đồ Giải Phẫu Gốc Từ (Word Lego Anatomy)")
    st.markdown("Chọn Cột trụ và Mô hình tư duy bạn đang học ở các Tab trước để học ngay các từ vựng tiếng Anh nguyên bản cấu thành nên tư duy đó.")

    # Bộ lọc 2 tầng: Cột Trụ -> Mô hình / Chủ đề cụ thể
    f_c1, f_c2 = st.columns([1, 1.5])

    pillar_choices = [("all", "🌐 Tất cả 3 Cột Trụ Kiến Thức")] + [
        (p["id"], f"{p['name']} ({p.get('word_count', len([x for x in all_vocab if x.get('pillar_id') == p['id']]))} từ)")
        for p in pillars
    ]
    pillar_map = {choice[1]: choice[0] for choice in pillar_choices}
    pillar_labels = [c[1] for c in pillar_choices]

    with f_c1:
        if "tab1_pillar_sel" in st.session_state and st.session_state["tab1_pillar_sel"] not in pillar_labels:
            st.session_state["tab1_pillar_sel"] = pillar_labels[0]
        sel_p_label = st.selectbox("🏛️ Bước 1: Chọn Cột Trụ Kiến Thức:", pillar_labels, key="tab1_pillar_sel")
        sel_pillar_id = pillar_map[sel_p_label]

    # Danh sách chủ đề theo Cột trụ đã chọn
    available_topics = get_topics_by_pillar(sel_pillar_id)
    topic_choices = [("all", "📂 Tất cả chủ đề trong cột trụ này")] + [
        (t["code"], f"[{t['code']}] {t['name']} ({t.get('word_count', 0)} từ)")
        for t in available_topics
    ]
    topic_map = {choice[1]: choice[0] for choice in topic_choices}
    topic_labels = [c[1] for c in topic_choices]

    with f_c2:
        if "tab1_topic_sel" in st.session_state and st.session_state["tab1_topic_sel"] not in topic_labels:
            st.session_state["tab1_topic_sel"] = topic_labels[0]
        sel_t_label = st.selectbox("🎯 Bước 2: Chọn Chủ Đề / Mô Hình Cụ Thể:", topic_labels, key="tab1_topic_sel")
        sel_topic_code = topic_map.get(sel_t_label, "all")

    # Thanh tìm kiếm nhanh
    search_query = st.text_input("🔍 Tìm kiếm từ tiếng Anh hoặc nghĩa tiếng Việt:", "", key="tab1_search")

    # Lọc danh sách từ vựng theo 2 tầng + tìm kiếm
    filtered_vocab = all_vocab
    if sel_pillar_id != "all":
        filtered_vocab = [v for v in filtered_vocab if v.get("pillar_id") == sel_pillar_id]
    if sel_topic_code != "all":
        filtered_vocab = [v for v in filtered_vocab if v.get("topic_code") == sel_topic_code]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_vocab = [
            v for v in filtered_vocab
            if q in v.get("word", "").lower() or q in v.get("vietnamese", "").lower() or q in v.get("topic_code", "").lower()
        ]

    if not filtered_vocab:
        st.warning("Không tìm thấy từ vựng phù hợp với bộ lọc đã chọn.")
    else:
        st.caption(f"Tìm thấy **{len(filtered_vocab)}** từ vựng tinh hoa phù hợp:")
        word_labels = [
            f"{v['word']} — {v['vietnamese']}  [{v.get('topic_code', '')}: {v.get('topic_name', '')}]"
            for v in filtered_vocab
        ]
        if "selected_word_anatomy" in st.session_state and st.session_state["selected_word_anatomy"] not in word_labels:
            st.session_state["selected_word_anatomy"] = word_labels[0]
        selected_label = st.selectbox("🎯 Bước 3: Chọn từ vựng cần giải phẫu gốc từ:", word_labels, key="selected_word_anatomy")
        selected_idx = word_labels.index(selected_label) if selected_label in word_labels else 0
        v = filtered_vocab[selected_idx]
        v_id = v["id"]


        is_mastered = user_state.get(v_id, {}).get("mastered", False)
        is_starred = user_state.get(v_id, {}).get("starred", False)

        # Header từ vựng
        head_c1, head_c2 = st.columns([3, 1])
        with head_c1:
            st.markdown(f"## 🔤 **{v['word']}** `{v.get('ipa', '')}` *({v.get('part_of_speech', '')})*")
            st.markdown(f"### 🇻🇳 **{v['vietnamese']}**")
            render_audio_and_tts_tools(v['word'], key_suffix=f"word_pron_{v_id}")
            st.info(f"🏛️ **Cột trụ:** {v.get('pillar_name', '')}  |  🎯 **Mô hình / Chủ đề:** `[{v.get('topic_code', '')}]` **{v.get('topic_name', '')}**")
        with head_c2:
            st.write("")
            btn_star_label = "⭐ Đã gắn sao" if is_starred else "☆ Gắn sao ưu tiên"
            if st.button(btn_star_label, key=f"star_btn_{v_id}", use_container_width=True):
                toggle_vocab_star(username, v_id)
                st.rerun()

            btn_master_label = "✅ Đã thông suốt" if is_mastered else "⚪ Đánh dấu đã thuộc"
            if st.button(btn_master_label, key=f"master_btn_{v_id}", use_container_width=True):
                toggle_vocab_mastery(username, v_id)
                st.rerun()

        st.markdown("---")


        # Khối ghép Lego
        st.markdown("#### 🧩 1. Các Mảnh Ghép Lego (Prefix + Root + Suffix)")
        lego = v.get("lego_breakdown", {})
        l_c1, l_c2, l_c3 = st.columns(3)
        with l_c1:
            st.info(f"**🟦 Tiền tố (Prefix):**\n\n`{lego.get('prefix', 'Không có')}`")
        with l_c2:
            st.success(f"**🟧 Gốc từ (Root Core):**\n\n`{lego.get('root', 'Chưa rõ')}`")
        with l_c3:
            st.warning(f"**🟩 Hậu tố (Suffix):**\n\n`{lego.get('suffix', 'Không có')}`")

        if v.get("etymology_story"):
            st.caption(f"📜 **Nguồn gốc từ nguyên:** {v['etymology_story']}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Cây họ hàng từ vựng
        family = v.get("family_words", [])
        if family:
            st.markdown("#### 🌳 2. Cây Họ Hàng Từ Vựng (Học 1 Gốc Từ — Hiểu Cả Gia Đình Từ)")
            f_cols = st.columns(min(len(family), 4))
            for i, fw in enumerate(family):
                with f_cols[i % len(f_cols)]:
                    st.markdown(f"**`{fw.get('word')}`**\n\n*{fw.get('meaning')}*")

        st.markdown("<br>", unsafe_allow_html=True)

        # Mỏ neo thị giác & Cặp đối kháng
        col_vis, col_con = st.columns(2)
        with col_vis:
            st.markdown("#### ⚓ 3. Mỏ Neo Thị Giác Trực Quan")
            st.markdown(f"""
            > **{v.get('visual_anchor', 'Chưa có mỏ neo.')}**
            """)
            if v.get("elite_context"):
                st.markdown("##### 💡 Ngữ cảnh Tinh hoa:")
                st.info(f"*{v['elite_context']}*")
                render_audio_and_tts_tools(v["elite_context"], key_suffix=f"anatomy_quote_{v_id}")
                st.caption("📋 *Sao chép nhanh để nghe giọng đọc cao cấp trên NaturalReaders:*")
                st.code(v["elite_context"], language=None)

        with col_con:
            st.markdown("#### ⚖️ 4. Cặp Đối Kháng Nhị Phân")
            contrast = v.get("contrast_pair", {})
            st.markdown(f"""
            - **Khái niệm đối lập:** `{contrast.get('opposite', 'N/A')}`
            - **Bản chất khác biệt:** {contrast.get('distinction', 'N/A')}
            """)
            st.success("Tư duy tinh hoa luôn soi chiếu cả hai mặt đối lập để định vị đúng chân lý.")


# =============================================================================
# TAB 2: FLASHCARD PHẢN XẠ NHẬN DIỆN (ACTIVE RECALL)
# =============================================================================
with tab_flashcard:
    st.subheader("⚡ Flashcard Phản Xạ Nhận Diện (Active Recall)")
    st.markdown("Luyện phản xạ nhận diện từ vựng tinh hoa qua cấu trúc Lego và mỏ neo thị giác mà không cần học thuộc vẹt.")

    fc_c1, fc_c2 = st.columns([1, 1.5])
    with fc_c1:
        fc_p_options = [("all", "🌐 Tất cả Cột Trụ")] + [(p["id"], p["name"]) for p in pillars]
        fc_p_map = {c[1]: c[0] for c in fc_p_options}
        fc_p_labels = [c[1] for c in fc_p_options]
        if "fc_pillar_select" in st.session_state and st.session_state["fc_pillar_select"] not in fc_p_labels:
            st.session_state["fc_pillar_select"] = fc_p_labels[0]
        fc_sel_p_lbl = st.selectbox("Lọc Cột Trụ:", fc_p_labels, key="fc_pillar_select")
        fc_sel_pid = fc_p_map[fc_sel_p_lbl]

    with fc_c2:
        fc_t_list = get_topics_by_pillar(fc_sel_pid)
        fc_t_options = [("all", "📂 Tất cả Chủ Đề trong Cột Trụ")] + [(t["code"], f"[{t['code']}] {t['name']}") for t in fc_t_list]
        fc_t_map = {c[1]: c[0] for c in fc_t_options}
        fc_t_labels = [c[1] for c in fc_t_options]
        if "fc_topic_select" in st.session_state and st.session_state["fc_topic_select"] not in fc_t_labels:
            st.session_state["fc_topic_select"] = fc_t_labels[0]
        fc_sel_t_lbl = st.selectbox("Lọc Chủ Đề:", fc_t_labels, key="fc_topic_select")
        fc_sel_tcode = fc_t_map.get(fc_sel_t_lbl, "all")


    fc_list = all_vocab
    if fc_sel_pid != "all":
        fc_list = [v for v in fc_list if v.get("pillar_id") == fc_sel_pid]
    if fc_sel_tcode != "all":
        fc_list = [v for v in fc_list if v.get("topic_code") == fc_sel_tcode]

    if not fc_list:
        st.info("Không có từ vựng nào trong danh mục này.")
    else:
        if "fc_index" not in st.session_state:
            st.session_state["fc_index"] = 0
        if "fc_flipped" not in st.session_state:
            st.session_state["fc_flipped"] = False

        if st.session_state["fc_index"] >= len(fc_list):
            st.session_state["fc_index"] = 0

        curr_card = fc_list[st.session_state["fc_index"]]
        c_id = curr_card["id"]
        c_state = user_state.get(c_id, {})

        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        with col_nav1:
            if st.button("⬅️ Thẻ trước", key="fc_prev_btn", use_container_width=True):
                st.session_state["fc_index"] = (st.session_state["fc_index"] - 1) % len(fc_list)
                st.session_state["fc_flipped"] = False
                st.rerun()
        with col_nav2:
            st.markdown(
                f"<div style='text-align:center;font-weight:bold;padding-top:8px;'>Thẻ {st.session_state['fc_index'] + 1} / {len(fc_list)} · [{curr_card.get('topic_code', '')}: {curr_card.get('topic_name', '')}]</div>",
                unsafe_allow_html=True,
            )
        with col_nav3:
            if st.button("Thẻ sau ➡️", key="fc_next_btn", use_container_width=True):
                st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % len(fc_list)
                st.session_state["fc_flipped"] = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Thẻ Flashcard
        if not st.session_state["fc_flipped"]:
            # MẶT TRƯỚC: Thách thức nhận diện
            with st.container(border=True):
                st.markdown(f"<h1 style='text-align:center;color:#1E88E5;'>{curr_card['word']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;font-size:18px;color:#888;'>{curr_card.get('ipa', '')} · <i>{curr_card.get('part_of_speech', '')}</i></p>", unsafe_allow_html=True)
                st.markdown("---")

                lego = curr_card.get("lego_breakdown", {})
                st.markdown(f"**🧱 Gợi ý Lego:** Tiền tố `{lego.get('prefix')}` + Gốc `{lego.get('root')}` + Hậu tố `{lego.get('suffix')}`")

                if curr_card.get("recognition_quiz", {}).get("question"):
                    q_text = curr_card["recognition_quiz"]["question"].replace("______", f"**{curr_card['word']}**")
                    st.markdown(f"📖 **Ngữ cảnh sử dụng:** *\"{q_text}\"*")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Lật thẻ xem Giải mã & Mỏ neo thị giác", key="flip_btn_front", use_container_width=True):
                    st.session_state["fc_flipped"] = True
                    st.rerun()
        else:
            # MẶT SAU: Giải mã bản chất & Mỏ neo
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align:center;color:#2E7D32;'>🇻🇳 {curr_card['vietnamese']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;font-size:22px;color:#1E88E5;'><b>{curr_card['word']}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;color:#666;'><i>[{curr_card.get('pillar_name')}] · {curr_card.get('topic_name')}</i></p>", unsafe_allow_html=True)
                st.markdown("---")

                st.markdown(f"⚓ **Mỏ neo thị giác:** {curr_card.get('visual_anchor')}")
                if curr_card.get("elite_context"):
                    st.info(f"💡 **Tư duy tinh hoa:** {curr_card.get('elite_context')}")
                    render_audio_and_tts_tools(curr_card["elite_context"], key_suffix=f"fc_{c_id}")
                    st.code(curr_card["elite_context"], language=None)


                st.markdown(f"⚖️ **Đối kháng:** Tránh nhầm với *{con.get('opposite')}* — {con.get('distinction')}")

                st.markdown("---")
                col_btn_l, col_btn_r = st.columns(2)
                with col_btn_l:
                    if st.button("🔄 Quay lại mặt trước", key="flip_back_btn", use_container_width=True):
                        st.session_state["fc_flipped"] = False
                        st.rerun()
                with col_btn_r:
                    is_done = c_state.get("mastered", False)
                    btn_m_title = "✅ Đã thông suốt (Bấm để hủy)" if is_done else "✅ Đánh dấu Đã Nắm Bản Chất"
                    if st.button(btn_m_title, key="mark_mastered_btn", use_container_width=True):
                        toggle_vocab_mastery(username, c_id)
                        st.session_state["fc_index"] = (st.session_state["fc_index"] + 1) % len(fc_list)
                        st.session_state["fc_flipped"] = False
                        st.rerun()


# =============================================================================
# TAB 3: THỬ THÁCH GIẢI MÃ & CLOZE TEST (ROOT DECRYPTION QUIZ)
# =============================================================================
with tab_quiz:
    st.subheader("🎯 Thử Thách Giải Mã Gốc Từ & Cloze Test")
    st.markdown("Điền từ vựng tinh hoa đúng vào câu ngữ cảnh. Khi trả lời đúng, hệ thống tự động ghi nhận bạn đã thông suốt từ đó!")

    qz_c1, qz_c2 = st.columns([1, 1.5])
    with qz_c1:
        qz_p_options = [("all", "🌐 Tất cả Cột Trụ")] + [(p["id"], p["name"]) for p in pillars]
        qz_p_map = {c[1]: c[0] for c in qz_p_options}
        qz_p_labels = [c[1] for c in qz_p_options]
        if "quiz_pillar_select" in st.session_state and st.session_state["quiz_pillar_select"] not in qz_p_labels:
            st.session_state["quiz_pillar_select"] = qz_p_labels[0]
        qz_sel_p_lbl = st.selectbox("Lọc Cột Trụ Quiz:", qz_p_labels, key="quiz_pillar_select")
        qz_sel_pid = qz_p_map[qz_sel_p_lbl]

    with qz_c2:
        qz_t_list = get_topics_by_pillar(qz_sel_pid)
        qz_t_options = [("all", "📂 Tất cả Chủ Đề")] + [(t["code"], f"[{t['code']}] {t['name']}") for t in qz_t_list]
        qz_t_map = {c[1]: c[0] for c in qz_t_options}
        qz_t_labels = [c[1] for c in qz_t_options]
        if "quiz_topic_select" in st.session_state and st.session_state["quiz_topic_select"] not in qz_t_labels:
            st.session_state["quiz_topic_select"] = qz_t_labels[0]
        qz_sel_t_lbl = st.selectbox("Lọc Chủ Đề Quiz:", qz_t_labels, key="quiz_topic_select")
        qz_sel_tcode = qz_t_map.get(qz_sel_t_lbl, "all")


    quiz_vocab_pool = [v for v in all_vocab if v.get("recognition_quiz")]
    if qz_sel_pid != "all":
        quiz_vocab_pool = [v for v in quiz_vocab_pool if v.get("pillar_id") == qz_sel_pid]
    if qz_sel_tcode != "all":
        quiz_vocab_pool = [v for v in quiz_vocab_pool if v.get("topic_code") == qz_sel_tcode]

    if not quiz_vocab_pool:
        st.info("Chưa có câu hỏi trắc nghiệm nào trong bộ lọc này.")
    else:
        if "quiz_idx" not in st.session_state:
            st.session_state["quiz_idx"] = 0
        if "quiz_submitted" not in st.session_state:
            st.session_state["quiz_submitted"] = False

        if st.session_state["quiz_idx"] >= len(quiz_vocab_pool):
            st.session_state["quiz_idx"] = 0

        q_item = quiz_vocab_pool[st.session_state["quiz_idx"]]
        quiz_data = q_item["recognition_quiz"]

        with st.container(border=True):
            st.markdown(f"**Câu hỏi {st.session_state['quiz_idx'] + 1} / {len(quiz_vocab_pool)}** · *[{q_item.get('topic_code')}: {q_item.get('topic_name')}]*")
            st.markdown(f"### ❓ *\"{quiz_data['question']}\"*")

            user_choice = st.radio(
                "Chọn từ vựng chính xác để điền vào chỗ trống:",
                quiz_data["options"],
                key=f"quiz_radio_{q_item['id']}_{st.session_state['quiz_idx']}",
            )

            col_submit, col_next = st.columns([1, 1])
            with col_submit:
                if st.button("📝 Nộp bài kiểm tra", key=f"submit_q_{q_item['id']}", use_container_width=True):
                    st.session_state["quiz_submitted"] = True
                    is_correct = (user_choice.strip().lower() == quiz_data["answer"].strip().lower())
                    record_quiz_attempt(username, q_item["id"], is_correct)
                    st.session_state["last_is_correct"] = is_correct

            with col_next:
                if st.button("Câu tiếp theo ➡️", key=f"next_q_{q_item['id']}", use_container_width=True):
                    st.session_state["quiz_idx"] = (st.session_state["quiz_idx"] + 1) % len(quiz_vocab_pool)
                    st.session_state["quiz_submitted"] = False
                    st.rerun()

            if st.session_state.get("quiz_submitted"):
                if st.session_state.get("last_is_correct"):
                    st.success(f"🎉 **Chính xác tuyệt đối!** Đáp án là **{quiz_data['answer']}** ({q_item['vietnamese']}).")
                else:
                    st.error(f"❌ **Chưa chính xác!** Đáp án đúng là: **{quiz_data['answer']}** ({q_item['vietnamese']}).")
                st.info(f"💡 **Giải thích từ nguyên:** {quiz_data.get('explanation')}")


# =============================================================================
# TAB 4: TỦ TỪ VỰNG CỦA TÔI (MY VOCAB VAULT)
# =============================================================================
with tab_vault:
    st.subheader("📊 Tủ Từ Vựng Tinh Hoa Của Tôi (My Vocab Vault)")
    st.markdown("Theo dõi toàn bộ hành trình làm chủ từ vựng của bạn. Dữ liệu được đồng bộ bền vững với tài khoản của bạn.")

    col_v1, col_v2, col_v3 = st.columns([1, 1, 1.2])
    with col_v1:
        vault_status = st.selectbox(
            "Trạng thái học tập:",
            ["Tất cả từ vựng", "✅ Đã thông suốt", "⏳ Chưa thông suốt", "⭐ Đã gắn sao"],
            key="vault_status_filter",
        )
    with col_v2:
        vault_p_choices = [("all", "🌐 Tất cả Cột Trụ")] + [(p["id"], p["name"]) for p in pillars]
        vault_p_map = {c[1]: c[0] for c in vault_p_choices}
        vault_p_lbl = st.selectbox("Cột Trụ:", [c[1] for c in vault_p_choices], key="vault_p_filter")
        vault_pid = vault_p_map[vault_p_lbl]

    with col_v3:
        vault_search = st.text_input("🔍 Tìm kiếm nhanh:", "", key="vault_search_box")

    display_list = all_vocab
    if vault_status == "✅ Đã thông suốt":
        display_list = [v for v in display_list if user_state.get(v["id"], {}).get("mastered")]
    elif vault_status == "⏳ Chưa thông suốt":
        display_list = [v for v in display_list if not user_state.get(v["id"], {}).get("mastered")]
    elif vault_status == "⭐ Đã gắn sao":
        display_list = [v for v in display_list if user_state.get(v["id"], {}).get("starred")]

    if vault_pid != "all":
        display_list = [v for v in display_list if v.get("pillar_id") == vault_pid]

    if vault_search.strip():
        qs = vault_search.strip().lower()
        display_list = [
            v for v in display_list
            if qs in v.get("word", "").lower() or qs in v.get("vietnamese", "").lower() or qs in v.get("topic_name", "").lower()
        ]

    st.markdown(f"**Tìm thấy {len(display_list)} từ vựng phù hợp:**")

    for item in display_list:
        i_id = item["id"]
        i_state = user_state.get(i_id, {})
        is_m = i_state.get("mastered", False)
        is_s = i_state.get("starred", False)

        badge_m = "🟢 Đã thuộc" if is_m else "⚪ Chưa thuộc"
        badge_s = "⭐ " if is_s else ""

        with st.expander(f"{badge_s}**{item['word']}** — {item['vietnamese']}  [{item.get('topic_code', '')}: {item.get('topic_name', '')}] | {badge_m}"):
            c_left, c_right = st.columns([3, 1])
            with c_left:
                st.markdown(f"**Phiên âm:** `{item.get('ipa')}` | **Từ loại:** *{item.get('part_of_speech')}*")
                st.markdown(f"🏛️ **Cột trụ:** {item.get('pillar_name')}  |  🎯 **Mô hình:** {item.get('topic_name')}")
                lego = item.get("lego_breakdown", {})
                st.markdown(f"**🧱 Lego:** `{lego.get('prefix')}` + `{lego.get('root')}` + `{lego.get('suffix')}`")
                st.markdown(f"**⚓ Mỏ neo:** {item.get('visual_anchor')}")
                if item.get("family_words"):
                    f_str = ", ".join([f"`{f['word']}` ({f['meaning']})" for f in item["family_words"]])
                    st.caption(f"🌳 Từ liên quan: {f_str}")
            with c_right:
                if st.button("Đổi trạng thái thuộc" if is_m else "Đánh dấu đã thuộc", key=f"vault_m_{i_id}", use_container_width=True):
                    toggle_vocab_mastery(username, i_id)
                    st.rerun()
                if st.button("Bỏ sao" if is_s else "Gắn sao ⭐", key=f"vault_s_{i_id}", use_container_width=True):
                    toggle_vocab_star(username, i_id)
                    st.rerun()
