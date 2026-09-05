# -*- coding: utf-8 -*-
"""9 Chế độ Tư duy"""
from __future__ import annotations

import streamlit as st
from utils.app_common import bootstrap

ctx = bootstrap()
username = ctx["username"]
display_name = ctx["display_name"]
active_keys = ctx["active_keys"]
model_choice = ctx["model_choice"]


st.title("📖 Cẩm Nang 9 Chế Độ Tư Duy Tinh Hoa (Elite Mental Modes)")
st.markdown("""
Giới tinh hoa hiếm khi chỉ dùng một góc nhìn đơn độc. Họ xây dựng một **mạng lưới các mô hình tư duy (Latticework of Mental Models)** 
và hoán chuyển linh hoạt tùy thuộc vào bài toán. Dưới đây là hướng dẫn thực hành 9 nguyên tắc cốt lõi theo từng bước cụ thể:
""")

st.markdown("""
| Chế độ tư duy | Bản chất cốt lõi | Khi nào nên dùng? | Mức độ phổ biến ở giới Elite |
| :--- | :--- | :--- | :--- |
| **1. First Principles** | Phân rã về chân lý bất biến, tránh bắt chước | Khi đổi mới sáng tạo, bế tắc giả định cũ | Rất cao (Musk, Feynman) |
| **2. Tư duy Xác suất & Bayes** | Nhìn thế giới theo phổ xác suất, cập nhật liên tục | Khi thông tin không chắc chắn, đầu tư, phán đoán | Cực cao (Buffett, Dalio, Quants) |
| **3. Tư duy Đảo ngược (Inversion)** | Tìm cách thất bại chắc chắn rồi né tránh | Khi lập kế hoạch, quản trị rủi ro dự án | Rất cao (Charlie Munger) |
| **4. Tư duy Bậc hai (Second-Order)** | Hỏi: "Và sau đó điều gì sẽ xảy ra tiếp theo?" | Khi ra quyết định có hệ quả lan truyền | Rất cao (Howard Marks) |
| **5. Tư duy Tùy chọn (Optionality)** | Rủi ro giới hạn, tiềm năng vô hạn (Barbell) | Khi môi trường biến động mạnh, chọn nghề, startup | Rất cao (Nassim Taleb) |
| **6. Latticework Đa ngành** | Kết hợp mô hình Vật lý, Sinh học, Tâm lý, Kinh tế | Khi giải quyết các hệ thống phức tạp | Cao (Munger, Polymaths) |
| **7. Thực nghiệm Nhanh (Iterative)** | Giả thuyết → Thử nghiệm vi mô → Đo lường → Tinh chỉnh | Khi khởi nghiệp, nghiên cứu khoa học, làm sản phẩm | Rất cao (Tech Founders, Lean) |
| **8. Lý thuyết Trò chơi (Game Theory)** | Đọc vị động lực (Incentives), cân bằng Nash | Khi đàm phán, làm việc nhóm, cạnh tranh | Rất cao (Chiến lược gia) |
| **9. Đa quy mô Thời gian** | Cân bằng Hôm nay (hành động) vs 10 năm (nguyên lý) | Khi định hướng sự nghiệp, xây dựng gia tộc | Cao (Bezos, Gia tộc bền vững) |
""")

st.divider()
st.markdown("### 🔍 Hướng Dẫn Thực Hành Chi Tiết Từng Nguyên Tắc")

with st.expander("🎯 1. First Principles — Tư duy Nguyên bản (Elon Musk, Aristotle, Feynman)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Không suy luận bằng phép loại suy/bắt chước (*Reasoning by Analogy* - "Người ta làm thế nào mình làm thế ấy"). 
        Thay vào đó, bóc tách vấn đề xuống tận những chân lý căn bản nhất không thể suy diễn thêm, rồi từ đó tái thiết kế giải pháp mới.

        **Quy trình 4 bước thực hành:**
        1. **Nhận diện & Thách thức giả định:** Liệt kê những điều mà mọi người đang mặc định là "đương nhiên đúng".
        2. **Bóc tách tầng sâu (Socratic Questioning):** Hỏi liên tục "Tại sao?", tách biệt triệt để Sự thật (Fact đo lường được) khỏi Ý kiến (Opinion/Emotion).
        3. **Tìm các quy luật vật lý / bất biến:** Xác định những giới hạn cứng (định luật tự nhiên, chi phí cận biên, nguyên liệu thô).
        4. **Tái thiết kế giải pháp từ số 0:** Lắp ghép các nguyên tử sự thật lại để tạo thành giải pháp tối ưu.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *SpaceX*: Mọi người bảo mua tên lửa tốn 65 triệu USD. Musk bóc tách chi phí nhôm, titan, sợi carbon chỉ chiếm 2% giá bán → Tự chế tạo tên lửa với giá rẻ hơn 90%.  
        - *Wellspring K12*: Thay vì học vẹt công thức Toán, hiểu rõ bản chất hình học từ tiên đề Euclid.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Điều gì tôi đang tin là đúng chỉ vì mọi người xung quanh bảo thế?*")
        st.caption("• *Nếu loại bỏ hết công cụ hiện tại, nhu cầu căn bản nhất ở đây là gì?*")

with st.expander("🎲 2. Tư duy Xác suất & Cập nhật Bayesian (Probabilistic & Bayesian Updating)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Từ bỏ tư duy nhị phân (Đúng/Sai, Được/Mất). Nhìn mọi sự vật hiện tượng dưới dạng **phổ xác suất (0% → 100%)**. 
        Liên tục hiệu chỉnh xác suất của niềm tin khi có dữ liệu thực nghiệm mới xuất hiện.

        **Quy trình 4 bước thực hành:**
        1. **Xác định tỷ lệ cơ sở (Base Rate / Prior Probability):** Trong thực tế, tỷ lệ thành công trung bình của việc này là bao nhiêu?
        2. **Thu thập dữ liệu mới khách quan (New Evidence):** Ghi nhận dữ liệu mới, tránh bẫy thiên kiến xác nhận (*Confirmation Bias*).
        3. **Hiệu chỉnh xác suất (Posterior Probability):** Tăng hoặc giảm niềm tin tương ứng với độ tin cậy của dữ liệu mới.
        4. **Ra quyết định theo Kỳ vọng toán (Expected Value):** $EV = (P_{thắng} \\times Lợi\\_nhuận) - (P_{thua} \\times Rủi\\_ro)$. Chỉ hành động khi $EV > 0$.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Trading Vàng/BTC*: Một lệnh bị lỗ không có nghĩa là phương pháp sai. Nếu hệ thống có tỷ lệ thắng 40% nhưng R:R = 1:2.5 thì $EV$ vẫn dương lớn.  
        - *Thi cử*: Một mẹo học thi đạt 9.0 IELTS chỉ có xác suất 1/10.000 đối với người mất gốc.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Xác suất khách quan điều này xảy ra là bao nhiêu %?*")
        st.caption("• *Dữ liệu mới này khiến tôi nên tăng hay giảm niềm tin bao nhiêu điểm?*")

with st.expander("🔄 3. Tư duy Đảo ngược (Inversion — Charlie Munger, Carl Jacobi)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        *"Invert, always invert"* (Nhà toán học Carl Jacobi). Nhiều bài toán phức tạp không thể giải quyết bằng cách tiến thẳng về phía trước. 
        Thay vì tìm kiếm sự thông thái vĩ đại, hãy kiên trì tránh xa những sai lầm ngu xuẩn đã được báo trước.

        **Quy trình 4 bước thực hành:**
        1. **Xác định mục tiêu mong muốn:** (Ví dụ: Muốn danh mục đầu tư tăng trưởng bền vững; Muốn đỗ cấp 3 điểm cao).
        2. **Đảo ngược thành kịch bản thảm họa:** "Làm sao để chắc chắn phá hủy tài khoản trong 1 tháng? / Làm sao để chắc chắn thi trượt?".
        3. **Lập danh sách hành vi tự sát (Not-to-do list):** Liệt kê 5-7 nguyên nhân cốt tử dẫn đến thảm họa đó.
        4. **Xây dựng rào chắn tuyệt đối:** Cắt bỏ hoàn toàn những hành vi trong danh sách cấm.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Đầu tư CKVN*: Muốn tránh mất tiền? Không dùng margin cao ở vùng đỉnh, không mua cổ phiếu rác không có thanh khoản, không nghe lời phím hàng ẩn danh.  
        - *Học tập*: Không thức khuya quá 11h trước ngày thi, không để điện thoại cạnh bàn học.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Nếu muốn dự án này thất bại thảm hại nhất có thể, tôi sẽ làm gì?*")
        st.caption("• *Tôi đang làm điều ngu ngốc nào mà nếu dừng lại sẽ tốt lên ngay lập tức?*")

with st.expander("🌊 4. Tư duy Bậc hai & Bậc cao (Second & Higher-Order Thinking — Howard Marks)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Tư duy bậc 1 đơn giản và nông cạn ("Tôi đói nên tôi ăn đồ ăn nhanh"). 
        Tư duy bậc 2 sâu sắc và hệ thống, luôn tự đặt câu hỏi thần thánh: **"Và sau đó thì điều gì sẽ xảy ra tiếp theo?"** (*And then what?*).

        **Quy trình 4 bước thực hành:**
        1. **Xác định hệ quả bậc 1 (Tức thì, dễ thấy):** Kết quả trực tiếp của hành động là gì?
        2. **Truy vấn hệ quả bậc 2 (Phản ứng dây chuyền):** Sau khi kết quả bậc 1 xảy ra, những người khác trong hệ thống sẽ phản ứng ra sao?
        3. **Truy vấn hệ quả bậc 3 (Trạng thái cân bằng mới):** Sau 6 tháng, 1 năm, 3 năm, thói quen hay cấu trúc mới nào được hình thành?
        4. **Đánh đổi chiến lược:** Chấp nhận chịu đau ở bậc 1 để gặt hái quả ngọt to lớn ở bậc 2 và bậc 3.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Kinh tế*: Chính phủ trợ cấp tiền mặt (Bậc 1: Dân có tiền tiêu -> Bậc 2: Nhu cầu vượt cung sinh lạm phát -> Bậc 3: Lãi suất tăng, doanh nghiệp phá sản).  
        - *Cộng tác AI*: Lạm dụng AI chép bài (Bậc 1: Được điểm 10 nhanh -> Bậc 2: Não teo khả năng suy luận -> Bậc 3: Trở thành người thừa trong xã hội).
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Và sau đó thì sao? Sau 1 tuần, 1 tháng, 1 năm nữa sẽ thế nào?*")
        st.caption("• *Hành động này mang lại lợi ích ngắn hạn nhưng rủi ro dài hạn ở đâu?*")

with st.expander("⚖️ 5. Tư duy Tùy chọn & Bất đối xứng (Optionality & Antifragility — Nassim Nicholas Taleb)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Thiết kế cuộc sống và đầu tư theo cấu trúc **Bất đối xứng lồi (Convex Asymmetry)**: Giới hạn tổn thất tối đa ở mức rất nhỏ (Capped Downside), 
        nhưng mở rộng tiềm năng lợi nhuận đến vô hạn (Unlimited Upside). Trở nên mạnh mẽ hơn từ biến động (*Antifragile*).

        **Quy trình 4 bước thực hành:**
        1. **Triệt tiêu nguy cơ diệt vong (Zero Ruin Risk):** Không bao giờ đặt cược toàn bộ vào một ván bài có xác suất tử vong dù chỉ là 0.1%.
        2. **Chiến lược Quả tạ (Barbell Strategy):** Phân bổ 80-90% nguồn lực vào nơi cực kỳ an toàn vững chắc + 10-20% vào các thể nghiệm có tiềm năng bùng nổ.
        3. **Tích lũy các Quyền chọn (Optionality):** Giữ tiền mặt, kỹ năng đa năng, quan hệ tốt để có quyền hành động khi cơ hội lớn xuất hiện.
        4. **Hưởng lợi từ sai lầm nhỏ:** Thử nghiệm nhiều sai lầm nhỏ có chi phí thấp để tìm ra đột phá lớn.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Sự nghiệp học sinh*: 80% học vững kiến thức phổ thông nền tảng (an toàn) + 20% tự học lập trình Agent AI và làm sản phẩm riêng (bùng nổ).  
        - *Trading*: Cắt lỗ 1% tài khoản khi sai, nhưng gồng lãi 4-6% khi thị trường chạy đúng sóng lớn.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Trường hợp xấu nhất xảy ra, tôi có bị phá sản/loại bỏ khỏi cuộc chơi không?*")
        st.caption("• *Nếu thành công, cơ hội này có thể nhân lên gấp bao nhiêu lần?*")

with st.expander("🕸️ 6. Mạng lưới Mô hình Tư duy Đa ngành (Latticework of Mental Models — Charlie Munger)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        *"Với người chỉ cầm cây búa, mọi thứ xung quanh đều trông giống cây đinh"*. 
        Thế giới thực không phân chia theo môn học (Toán, Lý, Sinh, Kinh tế, Tâm lý). Người tinh hoa xây dựng mạng lưới đan xen các mô hình cơ bản từ nhiều ngành để soi chiếu vấn đề.

        **Quy trình 4 bước thực hành:**
        1. **Làm chủ 80-90 mô hình hạt nhân:** (Vật lý: Đòn bẩy, Quán tính, Entropy; Sinh học: Tiến hóa, Hệ sinh thái; Tâm lý: Thiên kiến nhận thức; Kinh tế: Cung cầu, Chi phí cơ hội).
        2. **Soi chiếu đa góc nhìn:** Khi đứng trước quyết định lớn, bắt buộc phải xem xét qua ít nhất 3 lăng kính khoa học khác nhau.
        3. **Tìm kiếm hiệu ứng cộng hưởng (Lollapalooza Effect):** Khi 3-4 mô hình cùng chỉ về một hướng, kết quả tạo ra sẽ cực kỳ bùng nổ.
        4. **Tránh bẫy chuyên gia đơn ngành:** Không để một lăng kính duy nhất thao túng toàn bộ thế giới quan của bạn.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Đầu tư CKVN*: Kết hợp mô hình Chu kỳ (Kinh tế) + Dấu chân cung cầu VSA (Vật lý) + Tâm lý đám đông FOMO (Tâm lý học).  
        - *Dự án Wellspring*: Kết hợp kỹ năng thuyết trình (Ngôn ngữ) + số liệu khảo sát (Toán học) + mô hình sản phẩm (Công nghệ).
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Nhà sinh học / Nhà vật lý / Nhà kinh tế học sẽ nhìn bài toán này thế nào?*")
        st.caption("• *Có những lực vô hình nào từ các ngành khác đang chi phối hệ thống này?*")

with st.expander("⚡ 7. Tư duy Thực nghiệm Nhanh (Empirical / Iterative / Lean Thinking)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Kế hoạch nằm trên giấy luôn sai cho đến khi va chạm với thực tế. Giới tinh hoa công nghệ và khoa học không chờ đợi bản kế hoạch hoàn hảo. 
        Họ tạo ra vòng lặp phản hồi ngắn nhất: **Giả thuyết → Thử nghiệm vi mô → Đo lường → Tinh chỉnh (Build - Measure - Learn)**.

        **Quy trình 4 bước thực hành:**
        1. **Định hình Giả thuyết tối thiểu (Hypothesis):** Phát biểu rõ ràng: "Nếu tôi làm [A], chỉ số [B] sẽ thay đổi [C]%".
        2. **Tạo nguyên mẫu thử nghiệm nhỏ nhất (MVP):** Tạo phiên bản thử nghiệm có thể đưa vào thực tế trong vòng vài ngày với chi phí gần bằng 0.
        3. **Đo lường dữ liệu thật:** Thu thập phản hồi từ người dùng thực tế hoặc dữ liệu số học khách quan.
        4. **Lặp lại chu kỳ (Iterate) hoặc Chuyển hướng (Pivot):** Học nhanh từ dữ liệu để sửa đổi thay vì tranh cãi lý thuyết suông.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Khởi nghiệp công nghệ*: Thay vì bỏ 6 tháng viết app, tạo landing page trong 1 buổi để đo lường xem có bao nhiêu người đăng ký chờ.  
        - *Học tập*: Thử nghiệm phương pháp Pomodoro trong 3 ngày, ghi lại số trang sách đọc được để xem có phù hợp với mình không.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Cách nhanh nhất và rẻ nhất để tôi kiểm chứng giả thuyết này hôm nay là gì?*")
        st.caption("• *Dữ liệu thực tế đang nói điều gì trái ngược với niềm tin ban đầu của tôi?*")

with st.expander("♟️ 8. Tư duy Chiến lược & Lý thuyết Trò chơi (Strategic & Game Theory)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Kết quả của bạn không chỉ phụ thuộc vào bạn, mà còn phụ thuộc vào hành vi của những người tham gia khác. 
        Hiểu rõ cấu trúc **Động lực (Incentives)**: *"Hãy cho tôi thấy động lực của một người, tôi sẽ cho bạn thấy tương lai hành vi của họ"* (Charlie Munger).

        **Quy trình 4 bước thực hành:**
        1. **Xác định các người chơi (Players & Stakes):** Ai đang tham gia? Ai nắm quyền quyết định? Ai chịu rủi ro?
        2. **Phân tích ma trận động lực (Incentive Matrix):** Mỗi bên được gì nếu hợp tác? Họ mất gì nếu phản bội?
        3. **Tìm điểm cân bằng Nash (Nash Equilibrium):** Điểm mà tại đó không bên nào có động lực tự ý đổi chiến lược.
        4. **Thiết kế cơ chế cùng thắng (Mechanism Design):** Xây dựng luật chơi sao cho việc làm điều đúng đắn cũng chính là điều có lợi nhất cho tất cả các bên.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Làm việc nhóm Wellspring*: Tránh bẫy kẻ ăn bám (Free-rider problem) bằng cách chấm điểm minh bạch theo từng đầu việc gắn tên cá nhân.  
        - *Thị trường tài chính*: Hiểu động lực của nhà tạo lập thị trường (Market Makers) là kiếm phí và săn thanh khoản của đám đông thiếu kiên nhẫn.
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Người này được thưởng hay bị phạt dựa trên chỉ số nào?*")
        st.caption("• *Nếu tôi đi nước cờ này, đối phương có động lực phản ứng lại như thế nào?*")

with st.expander("⏳ 9. Tư duy Đa quy mô Thời gian (Multi-timescale Thinking — Jeff Bezos)", expanded=False):
    c_a, c_b = st.columns([3, 2])
    with c_a:
        st.markdown("""
        **Bản chất:**  
        Khả năng giữ vững đồng thời 3 khung thời gian trong tâm trí mà không để bên nào triệt tiêu bên nào: 
        **Bây giờ / Hôm nay** (kỷ luật thực thi, sinh tồn) — **1-3 Năm** (chiến lược thích ứng, tích lũy) — **10-20 Năm** (nguyên lý bất biến, tầm nhìn dài hạn).

        **Quy trình 4 bước thực hành:**
        1. **Xác định các hằng số 10 năm (Invariants):** Tìm những điều chắc chắn KHÔNG thay đổi trong 1-2 thập kỷ tới.
        2. **Xây dựng đòn bẩy trung hạn 1-3 năm:** Đặt ra các cột mốc năng lực và tài sản làm cầu nối giữa hiện tại và tương lai.
        3. **Chuyển hóa thành hành vi hàng ngày:** Biến mục tiêu dài hạn thành những thói quen vi mô kỷ luật mỗi ngày (Atomic Habits).
        4. **Kháng cự sự bốc đồng ngắn hạn:** Sẵn sàng bị người khác hiểu lầm trong ngắn hạn để kiên định với tầm nhìn dài hạn.
        """)
    with c_b:
        st.info("""
        💡 **Ví dụ thực tế:**  
        - *Amazon / Bezos*: "Khách hàng luôn muốn hàng rẻ hơn và giao nhanh hơn trong 10 năm tới" → Dồn toàn bộ nguồn lực xây kho vận và hạ tầng đám mây.  
        - *Gia đình & Con cái*: Dành 30 phút mỗi tối rèn tư duy phản biện (ngắn hạn) để tạo nên phẩm chất tự chủ suốt đời (dài hạn).
        """)
        st.markdown("**Bộ câu hỏi tự vấn (Prompts):**")
        st.caption("• *Điều gì sẽ KHÔNG thay đổi trong lĩnh vực của tôi 10 năm nữa?*")
        st.caption("• *Hành động hôm nay của tôi đang phục vụ cho tầm nhìn 1 tuần hay tầm nhìn 10 năm?*")

st.divider()
st.info("🎯 **Đã nắm vững 9 Lăng kính Tinh hoa?** Hãy chuyển sang **Tab [⚡ Đấu trường Luyện nhớ]** để kiểm tra phản xạ của bạn qua 9 tình huống thực chiến kinh điển hoặc lật thẻ Flashcard 5 giây!")

