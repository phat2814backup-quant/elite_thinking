# -*- coding: utf-8 -*-
"""
Module Lộ Trình Bách Khoa 12 Tháng (Polymath Curriculum) & Dự Án Capstone Đa Ngành.
Hiện thực hóa lời khuyên của Elon Musk về 'Broad Education':
- Phối hợp tuần tự và cân bằng giữa 3 miền: Sciences -> Engineering -> Arts & Humanities.
- Cung cấp bản đồ học tập rõ ràng, kèm mốc thực hành và các dự án lớn đa ngành.
"""

from __future__ import annotations
from typing import Dict, List, Any

POLYMATH_12_MONTH_CURRICULUM = [
    {
        "quarter": "QUÝ 1 (THÁNG 1 - 3): KHOA HỌC KHỞI THỦY & CHÂN LÝ TỰ NHIÊN",
        "quarter_en": "Quarter 1: Sciences & Natural Laws (First Principles & Limits)",
        "icon": "⚛️",
        "theme": "Hiểu những gì vật lý, nhiệt động lực, toán học và sinh học KHÔNG THỂ BỊ BẺ CONG.",
        "months": [
            {
                "month": "Tháng 1",
                "title": "Chân Lý Khởi Thủy & Nhiệt Động Lực Học",
                "models": ["PHYS-11 (First Principles)", "PHYS-03 (Entropy & Clausius)", "PHYS-01 (Đòn bẩy Archimedes)"],
                "focus": "Đập vụn giả định thành hạt chân lý cơ bản. Nhận thức rằng mọi hệ thống không bơm năng lượng đều tự thoái hóa về entropy cực đại.",
                "farrow_topic": "physics_core_1"
            },
            {
                "month": "Tháng 2",
                "title": "Toán Xác Suất, Cập Nhật Bayes & Tiêu Chuẩn Kelly",
                "models": ["MATH-01 (Tư duy Xác suất)", "MATH-03 (Bayesian Updating)", "MATH-04 (Quy tắc Số 0 & Kelly)"],
                "focus": "Không tư duy đúng/sai nhị nguyên; nhìn mọi biến cố theo phân phối xác suất. Luôn cập nhật xác suất khi có dữ liệu mới và tuyệt đối không cược vào ván có xác suất nhân với 0.",
                "farrow_topic": "math_probability"
            },
            {
                "month": "Tháng 3",
                "title": "Sinh Học Tiến Hóa, Niche Sinh Thái & Tín Hiệu Đắt Giá",
                "models": ["BIO-01 (Chọn lọc tự nhiên)", "BIO-10 (Báo hiệu đắt giá / Zahavi)", "BIO-12 (Nữ hoàng Đỏ)"],
                "focus": "Trong tự nhiên, kẻ sống sót không phải là kẻ mạnh nhất mà là kẻ thích nghi nhanh nhất. Chỉ tin những tín hiệu đi kèm chi phí tổn thất thật (Costly Signaling).",
                "farrow_topic": "biology_evolution"
            }
        ]
    },
    {
        "quarter": "QUÝ 2 (THÁNG 4 - 6): KỸ THUẬT, HỆ THỐNG & KINH TẾ THỰC DỤNG",
        "quarter_en": "Quarter 2: Engineering, Complex Systems & Real Economics",
        "icon": "⚙️",
        "theme": "Hiểu cách thế giới thực vận hành: chi phí biên, độ trễ mạng lưới, cấu trúc quyền lực và động lực ngầm.",
        "months": [
            {
                "month": "Tháng 4",
                "title": "Kinh Tế Quy Mô, Chi Phí Giao Dịch & Con Hào Kinh Tế",
                "models": ["ECON-01 (Cung cầu & Chi phí biên)", "ECON-08 (Chi phí giao dịch Coase)", "ECON-10 (Con hào Moat & Network Effects)"],
                "focus": "Tại sao các tập đoàn phình to rồi sụp đổ? Khi nào chi phí giao dịch bị công nghệ kéo sụp? Xây dựng con hào kinh tế không thể bị sao chép bằng hiệu ứng mạng.",
                "farrow_topic": "economics_core_2"
            },
            {
                "month": "Tháng 5",
                "title": "Lý Thuyết Trò Chơi, Động Lực Ngầm & Tư Duy Bậc Hai",
                "models": ["SYS-10 (Tư duy Bậc hai)", "ECON-15 (Lý thuyết Trò chơi)", "PSY-03 (Bẫy động lực Incentives)"],
                "focus": "Đừng nhìn hành động bề nổi; nhìn vào cấu trúc trả thưởng và động lực ngầm của đối thủ. Luôn tự hỏi 'Và rồi sau đó chuyện gì sẽ xảy ra?'.",
                "farrow_topic": "trinity_thinking"
            },
            {
                "month": "Tháng 6",
                "title": "Tư Duy Hệ Thống Phức Hợp, Vòng Lặp Phản Hồi & Biên An Toàn",
                "models": ["SYS-01 (Hệ thống phức hợp)", "SYS-04 (Biên an toàn & Barbell)", "SYS-11 (Latticework)"],
                "focus": "Nhận diện các vòng lặp phản hồi dương (bong bóng) và âm (tự cân bằng). Thiết lập cấu trúc đòn tạ Barbell: bảo thủ 90% để bất hoại và mạo hiểm 10% đón tiềm năng vô hạn.",
                "farrow_topic": "systems_complex"
            }
        ]
    },
    {
        "quarter": "QUÝ 3 (THÁNG 7 - 9): NGHỆ THUẬT, GU THẨM MỸ & ĐIỆN ẢNH KỂ CHUYỆN",
        "quarter_en": "Quarter 3: Arts, Aesthetics, Taste & Cinematic Storytelling",
        "icon": "🎨",
        "theme": "Định hình 'Gu' (Taste) và Linh hồn: Tỷ lệ vàng, tối giản công năng, nghệ thuật ẩn ý và khoảng lặng.",
        "months": [
            {
                "month": "Tháng 7",
                "title": "Tỷ Lệ Vàng Phi, Bauhaus & Triết Lý Tối Giản Dieter Rams",
                "models": ["ART-01 (Tỷ lệ vàng Phi & Fibonacci)", "ART-03 (Công năng định hình Hình thức)", "PHYS-05 (Cân bằng động)"],
                "focus": "Loại bỏ mọi hoa văn giả tạo. Thiết kế tốt nhất là thiết kế càng ít can thiệp càng tốt (Less but better). Áp dụng tỷ số 1.618 vào trải nghiệm và bố cục trực quan.",
                "farrow_topic": "arts_design_aesthetics"
            },
            {
                "month": "Tháng 8",
                "title": "Cấu Trúc Kịch Nghệ 3 Hồi & Hành Trình Người Anh Hùng",
                "models": ["ART-02 (Hero's Journey & Campbell)", "ART-05 (Khẩu súng Chekhov & Subtext)", "PSY-01 (Bẫy thiên kiến tự sự)"],
                "focus": "Khách hàng là Anh hùng, bạn là Người dẫn đường. Mọi chi tiết ở hồi 1 phải kích nổ ở hồi kết. Chạm vào cảm xúc bằng những điều ẩn dưới lời thoại (Subtext).",
                "farrow_topic": "arts_cinematic_narrative"
            },
            {
                "month": "Tháng 9",
                "title": "Thẩm Mỹ Wabi-Sabi, Tương Phản Sáng Tối & Khoảng Lặng 'Ma'",
                "models": ["ART-04 (Wabi-Sabi & Chiaroscuro)", "ART-06 (Khoảng lặng thẩm mỹ Ma)", "BIO-10 (Sự vụng về chân thật)"],
                "focus": "Trong kỷ nguyên tràn ngập nội dung AI bóng bẩy rẻ tiền, chính sự bất toàn chân thật, vết nứt hàn vàng Kintsugi và những khoảng lặng tĩnh mịch trở thành thứ xa xỉ đắt giá nhất.",
                "farrow_topic": "arts_cinematic_narrative"
            }
        ]
    },
    {
        "quarter": "QUÝ 4 (THÁNG 10 - 12): VĂN MINH, ĐẠO ĐỨC & TRÁCH NHIỆM AGI",
        "quarter_en": "Quarter 4: Civilizational Cycles, Ethics & Existential Stewardship",
        "icon": "🏛️",
        "theme": "Nhìn thế cuộc bằng lăng kính nghìn năm: Quy luật hưng vong đế chế, pháo đài Khắc kỷ và đạo đức học AI.",
        "months": [
            {
                "month": "Tháng 10",
                "title": "Quy Luật Hưng Vong Đế Chế, Asabiya & Siêu Chu Kỳ Nợ",
                "models": ["CIV-01 (Chu kỳ văn minh Ibn Khaldun & Dalio)", "ECON-01 (Chu kỳ nợ dài hạn)", "SYS-10 (Bão hòa tinh hoa Turchin)"],
                "focus": "Định vị vị thế của nền kinh tế và tổ chức trên đồng hồ lịch sử. Nhận diện sớm dấu hiệu suy đồi khi tinh hoa bão hòa và chuẩn bị cho sự chuyển dịch trật tự thế giới.",
                "farrow_topic": "civilization_philosophy"
            },
            {
                "month": "Tháng 11",
                "title": "Thần Thoại Tập Thể Harari & Pháo Đài Tâm Trí Khắc Kỷ",
                "models": ["CIV-02 (Thực tại liên chủ thể Sapiens)", "CIV-03 (Nhị phân kiểm soát Stoicism)", "CIV-04 (Ý chí ý nghĩa Frankl)"],
                "focus": "Phân biệt thực tại khách quan vật lý và thỏa thuận tưởng tượng chung của số đông. Rèn luyện pháo đài tâm trí: tập trung 100% vào những gì ta kiểm soát được và yêu lấy định mệnh (Amor Fati).",
                "farrow_topic": "civilization_philosophy"
            },
            {
                "month": "Tháng 12",
                "title": "Bài Toán Căn Chỉnh AI, Đạo Đức Học Đức Hạnh & Ngọn Lửa Nhận Thức",
                "models": ["CIV-05 (AI Alignment & Midas Trap)", "CIV-06 (Đạo đức học đức hạnh Aristotle)", "PHYS-03 (Bảo tồn ngọn lửa nhận thức)"],
                "focus": "Khóa chặt các rào cản đạo đức tiêu cực cho siêu trí tuệ. Giữ vững phẩm giá con người và định vị sứ mệnh cá nhân như một người bảo vệ ngọn lửa ý thức nhân loại.",
                "farrow_topic": "humanities_ethics_ideas"
            }
        ]
    }
]

POLYMATH_CAPSTONE_PROJECTS = [
    {
        "id": "capstone_1",
        "title": "🚀 Capstone 1: Thiết Kế Sản Phẩm Công Nghệ Có Gu & Linh Hồn (Tech Product with Soul)",
        "badge": "Sciences + Engineering + Arts",
        "duration": "4 - 6 Tuần",
        "mission": "Thiết kế một sản phẩm phần cứng hoặc phần mềm ứng dụng AI (ví dụ: Thiết bị trợ lý gia đình, Ứng dụng quản trị nhận thức cá nhân, Xe tự hành thông minh) thỏa mãn đồng thời 3 miền:",
        "requirements": [
            "⚛️ **Khoa học (Sciences):** Chứng minh tính khả thi vật lý, giới hạn năng lượng, và sự tương thích với sinh học thần kinh người dùng (không gây nghiện độc hại, không làm kiệt sức não).",
            "⚙️ **Kỹ thuật (Engineering):** Kiến trúc module phân lớp, chi phí biên tiến về 0, độ trễ < 500ms, cơ chế tự phục hồi khi mạng gián đoạn (Graceful Degradation).",
            "🎨 **Nghệ thuật & Gu (Arts & Taste):** Áp dụng tỷ lệ vàng Phi trong giao diện/kích thước, triết lý tối giản Dieter Rams, và kịch bản tương tác giàu sự thấu cảm nhân văn."
        ],
        "deliverable": "Bản Đặc Tả Sản Phẩm (Polymath PRD) + Master Formulated Prompt hoàn chỉnh để chỉ đạo AI Agents lập trình và thiết kế 3D.",
        "seed_intent": "Thiết kế một trợ lý AI đồng hành thông minh cho gia đình hoặc cá nhân: vừa tối ưu hóa năng lượng và chi phí biên dưới 1$/tháng, vừa sở hữu thiết kế tối giản tinh tế theo triết lý Dieter Rams và mang lại cảm xúc nhân văn ấm áp, tuyệt đối không tạo cảm giác bị giám sát."
    },
    {
        "id": "capstone_2",
        "title": "🎬 Capstone 2: Phim Tài Liệu / Kênh Truyền Thông Tri Thức Triệu View (Cinematic Intellectual Media)",
        "badge": "Sciences + Arts + Behavioral Psychology",
        "duration": "4 Tuần",
        "mission": "Xây dựng chuỗi nội dung truyền thông đỉnh cao giải mã một đề tài khoa học hoặc tài chính hóc búa (vd: Vi cấu trúc thị trường Vàng, Lỗ đen & Thuyết tương đối, hay Chu kỳ đế chế):",
        "requirements": [
            "⚛️ **Khoa học nhận thức (Sciences):** Tối ưu hóa chu kỳ chú ý 60-120 giây của não bộ, nhúng các mỏ neo hình ảnh Dave Farrow để người xem nhớ vĩnh viễn sau 1 lần xem.",
            "🎨 **Kịch nghệ điện ảnh (Arts):** Cấu trúc 3 hồi Aristotle, khẩu súng Chekhov kích nổ ở phút cuối, và sử dụng khoảng lặng thẩm mỹ 'Ma' để tạo cảm xúc lay động tâm can.",
            "⚙️ **Hệ thống phân phối (Engineering):** Quy trình tự động hóa sản xuất nội dung bằng AI Agents kết hợp kiểm duyệt chất lượng nghiêm ngặt chống rác slop."
        ],
        "deliverable": "Kịch bản phân cảnh chi tiết (Storyboard) + Bộ câu lệnh Prompt sinh video/âm thanh + Khung đánh giá chất lượng.",
        "seed_intent": "Sản xuất một chuỗi video ngắn 60 giây và phim tài liệu mini giải thích các chân lý khoa học - tài chính phức tạp: vừa giữ chân người xem 100% thời lượng bằng cấu trúc 3 hồi và khẩu súng Chekhov, vừa cài cắm các mỏ neo trí nhớ Farrow để người xem nhớ mãi mãi mà không bị sáo rỗng."
    },
    {
        "id": "capstone_3",
        "title": "⚖️ Capstone 3: Bản Hiến Chương & Hệ Thống AI Agent Tự Trị An Toàn (Autonomous AI Alignment System)",
        "badge": "Engineering + Humanities + Ethics",
        "duration": "6 Tuần",
        "mission": "Thiết kế một hệ thống đa AI Agents (Multi-Agent Swarm) tự động vận hành một doanh nghiệp hoặc quỹ đầu tư nhưng được khóa chặt bằng Hiến chương đạo đức:",
        "requirements": [
            "⚙️ **Kỹ thuật hệ thống (Engineering):** Thiết kế kiến trúc phân quyền đa tác nhân, cơ chế đồng thuận Byzantine, và trần rủi ro tài chính tự động ngắt mạch (Circuit Breakers).",
            "🏛️ **Lịch sử & Chu kỳ (Humanities):** Xây dựng kịch bản kiểm thử ứng phó với khủng hoảng địa chính trị, bão lạm phát và sự dịch chuyển trật tự tiền tệ toàn cầu.",
            "⚖️ **Đạo đức & Căn chỉnh (Ethics):** Khóa chặt rào cản tiêu cực chống lại bẫy Vua Midas / Kẹp giấy Bostrom; đảm bảo quyền can thiệp tối thượng của con người (Human-in-the-loop)."
        ],
        "deliverable": "Bộ quy tắc Guardrails & Architecture Spec + Bộ đề bài Formulate giao việc cho từng Agent trong bầy đàn.",
        "seed_intent": "Thiết kế kiến trúc hệ thống bầy đàn AI Agents (Multi-Agent Swarm) tự động vận hành doanh nghiệp hoặc phân tích đầu tư: có cơ chế ngắt mạch an toàn khi thị trường biến động, có hiến chương đạo đức chống bẫy Vua Midas và bảo đảm quyền can thiệp tuyệt đối của con người."
    }
]

