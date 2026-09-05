# -*- coding: utf-8 -*-
"""
Elite Thinking Family v2 — Dynamic Multipage + Supabase persistence
Entrypoint with role-based navigation & pre-login sidebar protection.
"""
from __future__ import annotations

from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

st.set_page_config(
    page_title="Elite Thinking Family",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.auth import init_auth_state, require_login, is_admin
from utils.app_common import bootstrap


def render_home():
    """Trang chủ: Bản đồ tư duy & Lộ trình 7 bước."""
    ctx = bootstrap()
    username = ctx["username"]
    display_name = ctx["display_name"]

    st.title("🧭 Bản Đồ Huấn Luyện Tư Duy Tinh Hoa (Elite Thinking Roadmap)")
    st.markdown("""
    Chào mừng bạn đến với **Hệ thống Huấn luyện Tư duy Tinh hoa & Nguyên lý Khởi thủy**. 
    Hệ thống này được xây dựng dựa trên phương pháp tư duy của các bậc thầy kiệt xuất: **Charlie Munger, Richard Feynman, Elon Musk và John von Neumann** — 
    nhằm giúp bạn giải phóng khỏi lối mòn suy nghĩ bắt chước (analogy), làm chủ các quy luật bất biến của tự nhiên và ra quyết định chính xác trong môi trường phức tạp.
    """)

    # 3 Triết lý cốt lõi
    c_q1, c_q2, c_q3 = st.columns(3)
    with c_q1:
        st.info("""
        **🕸️ Charlie Munger**
        > *"Bạn phải xây dựng một mạng lưới các mô hình trong đầu, và bạn phải treo kinh nghiệm của mình lên mạng lưới đó. Nếu chỉ có một mô hình, bạn sẽ bóp méo thực tế để vừa vặn với nó."*
        """)
    with c_q2:
        st.success("""
        **🔬 Richard Feynman**
        > *"Bạn không thực sự hiểu điều gì cho đến khi bạn có thể giải thích nó bằng ngôn ngữ giản dị nhất từ nguyên lý gốc, không dùng thuật ngữ hoa mỹ."*
        """)
    with c_q3:
        st.warning("""
        **⚡ Elon Musk**
        > *"Đừng suy luận bằng cách bắt chước. Hãy đập vụn sự vật về những chân lý cơ bản nhất không thể phủ nhận, rồi suy luận ngược lên từ đó."*
        """)

    st.markdown("---")
    st.subheader("🗺️ Quy Trình 7 Bước Chuyển Hóa Năng Lực Tư Duy Tinh Hoa")
    st.markdown("Để biến tri thức thành phản xạ tự nhiên và giải quyết được mọi bài toán hóc búa, hãy đi theo lộ trình 7 bước sư phạm:")

    step_cols = st.columns(7)
    with step_cols[0]:
        st.markdown("""
        #### 1️⃣ Định Vị Thế Cuộc
        **Tab 1: Thế cuộc & Elite**
        *Hiểu chiến trường thực tại:*
        - 5 kỷ nguyên tiến hóa
        - 8 mật mã vận hành ngầm
        - Nút thắt khan hiếm mới
        - AI Macro Radar
        """)
    with step_cols[1]:
        st.markdown("""
        #### 2️⃣ Nạp Lăng Kính
        **Tab 2: 9 Chế độ**
        *Làm chủ hệ điều hành não:*
        - First Principles
        - Đảo ngược Inversion
        - Hệ quả bậc hai
        - Xác suất Bayes
        - Đa quy mô thời gian
        """)
    with step_cols[2]:
        st.markdown("""
        #### 3️⃣ Cài Mô Hình
        **Tab 3: 88 Mô hình**
        *Nắm 6 trụ cột Munger:*
        - Vật lý (Đòn bẩy, Entropy)
        - Sinh học (Tiến hóa)
        - Tâm lý (Thiên kiến)
        - Kinh tế (Chi phí cơ hội)
        - Toán/Xác suất & Hệ thống
        """)
    with step_cols[3]:
        st.markdown("""
        #### 4️⃣ Tra Cứu Sâu
        **Tab 4: Thư viện**
        *100 định luật khoa học:*
        - Định nghĩa toán học
        - Điều kiện biên
        - Tiêu chuẩn khả bác Karl Popper
        """)
    with step_cols[4]:
        st.markdown("""
        #### 5️⃣ Luyện Phản Xạ
        **Tab 5: Đấu trường**
        *Khắc sâu vào phản xạ:*
        - Thẻ Flashcards 5 giây
        - Ma trận 731 câu trắc nghiệm
        - Dynamic AI Quiz
        - Thử thách Richard Feynman
        """)
    with step_cols[5]:
        st.markdown("""
        #### 6️⃣ Rèn Chủ Đích
        **Tab 6: Đào tạo**
        *Bài tập tự luận đa tầng:*
        - K12 Wellspring & Người lớn
        - 3 Cấp độ thực hành
        - AI Mentor phản biện
        - Tự động sinh đề mở rộng
        """)
    with step_cols[6]:
        st.markdown("""
        #### 7️⃣ Thực Chiến
        **Tab 7: Phân rã**
        *Vũ khí giải quyết vấn đề:*
        - Đưa vấn đề thực tế vào
        - AI kích hoạt đa lăng kính
        - Tìm đòn bẩy bất đối xứng
        - Ra quyết định thượng thừa
        """)

    st.markdown("---")

    st.subheader("🎯 Chọn Lộ Trình Huấn Luyện Phù Hợp Với Bạn")
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("""
        ### 🎒 Track 1: Học sinh Phổ thông (Wellspring Lớp 6, 9, 10)
        - **Mục tiêu:** Thoát khỏi thói quen học vẹt và tin đồn, xây dựng tư duy phản biện độc lập, định hình tư duy logic trước tuổi trưởng thành.
        - **Các bài toán trọng tâm:**
          - *Lớp 6:* Xây dựng thói quen hỏi "Tại sao?", nhận diện giả định ngầm, đối chiếu sự thật khách quan.
          - *Lớp 9:* Quản lý năng lượng & thời gian thi cử, phân biệt hệ quả trước mắt vs hệ quả lâu dài, cân bằng sở thích và trách nhiệm.
          - *Lớp 10:* Ra quyết định chọn ngành nghề / môn học, quản trị mối quan hệ bạn bè, tư duy chi phí cơ hội.
        - **Bắt đầu ngay:** Chuyển sang **Tab [🎓 Đào tạo tư duy]** ➔ Chọn nhóm **Học sinh Wellspring**.
        """)
    with t_c2:
        st.markdown("""
        ### 💼 Track 2: Người lớn & Chuyên gia (Trading CKVN, Quản trị, Não bộ, AI)
        - **Mục tiêu:** Ra quyết định đầu tư/kinh doanh thượng thừa, làm chủ tâm lý đám đông, quản trị rủi ro bất đối xứng và thiết kế hệ thống.
        - **Các bài toán trọng tâm:**
          - *Tài chính & CKVN:* Tư duy xác suất Bayes, quản trị rủi ro bất đối xứng (Asymmetry), chu kỳ Mr. Market, đòn bẩy tài chính.
          - *Não bộ & Tâm lý:* Kiểm soát thiên kiến xác nhận, bẫy chi phí chìm, hiệu ứng sợ mất mát (Loss Aversion).
          - *Phật giáo & Quy luật:* Vô thường (Entropy), Duyên khởi (Tư duy hệ thống phức hợp), Nhân quả (Hệ quả bậc 2).
        - **Bắt đầu ngay:** Xem **Tab [🕸️ 88 Mô hình Hạt nhân]** để nạp 25 mô hình Tier 1 ➔ Sau đó vào **Tab [🎓 Đào tạo tư duy]**.
        """)

    st.markdown("---")

    st.subheader("⭐ 4 Nguyên Tắc Vàng Khi Rèn Luyện")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("""
        **1. Chống bẫy "Người cầm búa" (Man with a Hammer Syndrome)**
        - *"Nếu công cụ duy nhất bạn có là một cây búa, bạn sẽ đối xử với mọi thứ như thể nó là một chiếc đinh."* — Abraham Maslow / Charlie Munger.
        - Giới tinh hoa không bao giờ giải quyết bài toán phức tạp bằng một góc nhìn đơn lẻ. Hãy kết hợp ít nhất 2–3 mô hình từ các ngành khác nhau để tạo hiệu ứng cộng hưởng (**Lollapalooza**).

        **2. Kiểm chứng tính khả bác (Falsification Principle)**
        - Đừng chỉ tìm bằng chứng ủng hộ ý kiến có sẵn của mình (bẫy Confirmation Bias). 
        - Hãy luôn tự hỏi: *"Tình huống nào hoặc bằng chứng nào sẽ chứng minh là tôi đang sai?"* Nếu không tìm được điều kiện biên làm cho nó sai, bạn chưa thực sự thấu suốt vấn đề.
        """)
    with r2:
        st.markdown("""
        **3. Rèn luyện có chủ đích & Nhận phản hồi (Deliberate Practice & Feedback Loop)**
        - Chỉ đọc lý thuyết chỉ tạo ra ảo tưởng về sự hiểu biết.
        - Bạn phải tự tay gõ câu trả lời, nhấn nộp bài để nhận phản biện sắc bén từ **AI Mentor**, và theo dõi sự tiến bộ của mình tại **Tab [📝 Lịch sử của tôi]**.

        **4. Chuyển hóa kiến thức thành Đòn bẩy Thực chiến**
        - Mọi mô hình và nguyên lý đều vô giá trị nếu không tạo ra kết quả trong thế giới thực.
        - Khi gặp bất kỳ khúc mắc nào trong công việc, đầu tư hay cuộc sống, hãy đưa ngay vào **Tab [🚀 Phân rã thực chiến]** để bóc tách tận gốc rễ.
        """)


def render_login():
    """Trang đăng nhập: hiển thị form và chặn truy cập trái phép."""
    require_login()


# -----------------------------------------------------------------------------
# Dynamic Navigation Router
# -----------------------------------------------------------------------------
init_auth_state()

if not st.session_state.get("authenticated") or not st.session_state.get("user"):
    # CHƯA ĐĂNG NHẬP: Ẩn hoàn toàn thanh điều hướng sidebar, không lộ bất kỳ trang nào
    login_page = st.Page(render_login, title="Đăng nhập", icon="🔐")
    router = st.navigation([login_page], position="hidden")
    router.run()
else:
    # ĐÃ ĐĂNG NHẬP: Hiển thị các trang theo phân quyền
    home_page = st.Page(render_home, title="Bản đồ Tư duy", icon="🧭", default=True)
    p1 = st.Page("pages/1_the_cuoc_elite.py", title="Thế cuộc & Elite", icon="🌐")
    p2 = st.Page("pages/2_9_che_do_tu_duy.py", title="9 Chế độ Tư duy", icon="📖")
    p3 = st.Page("pages/3_88_mo_hinh.py", title="88 Mô hình", icon="🕸️")
    p4 = st.Page("pages/4_thu_vien_nguyen_ly.py", title="Thư viện Nguyên lý", icon="📚")
    p5 = st.Page("pages/5_dau_truong.py", title="Đấu trường & Bài tập", icon="⚡")
    p6 = st.Page("pages/6_dao_tao.py", title="Đào tạo Gia đình", icon="🎓")
    p7 = st.Page("pages/7_phan_ra.py", title="Phân rã Vấn đề", icon="🚀")
    p8 = st.Page("pages/8_lich_su.py", title="Lịch sử Học tập", icon="📝")

    nav_map = {
        "🧭 Định hướng": [home_page],
        "🧠 Lăng kính & Mô hình": [p1, p2, p3, p4],
        "⚔️ Rèn luyện & Thực chiến": [p5, p6, p7, p8],
    }

    # Phân quyền Admin: Chỉ tài khoản Admin mới nhìn thấy mục Quản trị trong Menu
    if is_admin():
        p9 = st.Page("pages/9_admin.py", title="Quản trị Hệ thống", icon="👑")
        nav_map["👑 Quản trị"] = [p9]

    router = st.navigation(nav_map, position="sidebar")
    router.run()
